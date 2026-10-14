"""TLDR: The hosted-Valkyrie side of cert-judge's judge transports (experiments 39, 42 and 43). Since 10-13-2026
Valkyrie runs in Vals' cloud: the CLI reads only the saved login (`valkyrie login`), `VALKYRIE_API_KEY` and
`VALKYRIE_URL`; a private `valkyrie.yaml`, `VALKYRIE_CONFIG_PATH`, `VALKYRIE_ENV`, `custom_benchmark_services` and
`benchmark_auth` do nothing. A tunnelled benchmark service is registered on the Tracker instead:
`valkyrie secret set <benchmark>-bearer` (value `Bearer <token>`, piped on stdin) and
`valkyrie benchmark service set <benchmark> <url> --auth-secret <benchmark>-bearer --auth-header Authorization`,
which needs a login (an access key cannot change it) and is repeated after every tunnel restart because the URL
changes. Every call here is a CLI subprocess with zero model calls; no secret value is printed, logged or returned.
Checked against `vals-ai/Valkyrie@prod` 865135f (10-14-2026)."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

# Organization secret holding the model-gateway key. The former name `fellows/brandoModelGatewayApiKey` lived in the
# per-user AWS Secrets Manager; tenant secret names cannot contain a slash.
GATEWAY_SECRET = os.environ.get("CJ_GATEWAY_SECRET", "brandoModelGatewayApiKey")
SECRET_NAME_RE = re.compile(r"^[A-Za-z0-9_+=.@-]{1,128}$")
ROUTE = "Valkyrie hosted (Vals cloud; valkyrie login or VALKYRIE_API_KEY)"
REGISTERED_BY = "valkyrie benchmark service set --auth-secret"
# Keys a judge-transport CLI call must never inherit: provider keys (every call goes through Valkyrie), the Python
# path of the caller, and the pre-hosted settings that the new CLI ignores (kept out so receipts never suggest them).
DROPPED_ENV = ("TRACKER_SERVICE_URL", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY",
               "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_AUTH_TOKEN", "PYTHONPATH", "PYTHONHOME", "VALKYRIE_ENV",
               "VALKYRIE_CONFIG_PATH")
_WHOAMI_RE = re.compile(r" in (?P<org>.+) on (?P<url>\S+) \(using (?P<credential>a login|an access key|no credential)\)\s*$")


def resolve_cli(frozen_default: Path, override_var: str) -> Path:
    """The hosted CLI: `<override_var>` if set, else the `uv tool install` location, else `valkyrie` on PATH, else the
    experiment's frozen default (whose pre-hosted bootstrap build fails the preflight)."""
    if os.environ.get(override_var):
        return Path(os.environ[override_var])
    for candidate in (Path.home() / ".local/bin/valkyrie", shutil.which("valkyrie"), shutil.which("valk")):
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    return Path(frozen_default)


def env(login_only: bool = False) -> dict[str, str]:
    """Environment for a CLI call. `login_only` drops VALKYRIE_API_KEY, which otherwise takes precedence over the
    saved login, so the calls that need a login (benchmark service set) use it."""
    out = dict(os.environ)
    for key in DROPPED_ENV + (("VALKYRIE_API_KEY",) if login_only else ()):
        out.pop(key, None)
    return out


def cli(valk: Path, args: list[str], timeout: int = 1800, login_only: bool = False,
        stdin_text: str | None = None) -> subprocess.CompletedProcess:
    """One CLI call. A secret value only ever travels on stdin (`stdin_text`), never on the command line."""
    return subprocess.run([str(valk)] + args, env=env(login_only), capture_output=True, text=True, timeout=timeout,
                          **({"input": stdin_text} if stdin_text is not None else {"stdin": subprocess.DEVNULL}))


def legacy_settings() -> list[str]:
    """Pre-hosted settings still exported in the caller's shell (ignored by the CLI; reported so nobody relies on them)."""
    return [k for k in ("VALKYRIE_ENV", "VALKYRIE_CONFIG_PATH") if os.environ.get(k)]


def parse_whoami(text: str) -> dict:
    """`<who> in <org> on <tracker url> (using a login|an access key)` -> organization, tracker and credential."""
    for line in reversed(text.strip().splitlines()):
        found = _WHOAMI_RE.search(line)
        if found:
            return {"organization": found["org"], "tracker": found["url"],
                    "credential": {"a login": "login", "an access key": "access_key"}.get(found["credential"], "none")}
    return {}


def parse_providers(text: str) -> dict:
    """`valkyrie provider list` -> {"default": name or None, "providers": {name: secret name or None}}."""
    providers: dict[str, str | None] = {}
    default = None
    for line in text.splitlines():
        found = re.match(r"^([* ]) (\S+)(?: → (\S+))?", line)
        if not found:
            continue
        providers[found[2]] = found[3]
        if found[1] == "*":
            default = found[2]
    return {"default": default, "providers": providers}


def preflight(valk: Path, log_path: Path | None = None, need_login: bool = False) -> dict:
    """Zero-call identity and sandbox check before anything is admitted or registered: `valkyrie whoami` must name an
    organization and credential (a login when `need_login`), and `valkyrie provider list` must show a default sandbox
    provider with a secret behind it. Raw output (it names the account) goes to `log_path` only; the returned receipt
    holds the organization, the credential kind and the provider names."""
    who = cli(valk, ["whoami"], timeout=120, login_only=need_login)
    prov = cli(valk, ["provider", "list"], timeout=120, login_only=need_login)
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(f"$ valkyrie whoami (rc={who.returncode})\n{who.stdout}{who.stderr}\n"
                            f"$ valkyrie provider list (rc={prov.returncode})\n{prov.stdout}{prov.stderr}\n")
    identity = parse_whoami(who.stdout) if who.returncode == 0 else {}
    providers = parse_providers(prov.stdout) if prov.returncode == 0 else {"default": None, "providers": {}}
    problems = []
    if not identity:
        problems.append(f"`{valk} whoami` failed or is not the hosted CLI (rc={who.returncode}): run "
                        "`uv tool install --force git+https://github.com/vals-ai/Valkyrie@prod`, then `valkyrie login`")
    elif identity["credential"] == "none":
        problems.append("no Valkyrie credential: run `valkyrie login` (or export VALKYRIE_API_KEY on a headless host)")
    elif need_login and identity["credential"] != "login":
        problems.append("benchmark service registration needs `valkyrie login`; an access key cannot change it")
    default = providers["default"]
    if not default or not providers["providers"].get(default):
        problems.append("no default sandbox provider with a secret: `valkyrie secret set daytona < daytona.json`, "
                        "`valkyrie provider set daytona daytona`, `valkyrie provider default daytona`")
    receipt = {"route": ROUTE, "cli": str(valk), "organization": identity.get("organization"),
               "tracker": identity.get("tracker"), "credential": identity.get("credential"),
               "default_provider": default, "providers": sorted(providers["providers"]),
               "legacy_settings_ignored": legacy_settings(), "problems": problems,
               "verdict": "FAIL" if problems else "PASS"}
    return receipt


def require(receipt: dict) -> dict:
    if receipt["verdict"] != "PASS":
        raise SystemExit("Valkyrie preflight failed:\n- " + "\n- ".join(receipt["problems"]))
    return receipt


def bearer_secret_name(benchmark: str) -> str:
    name = f"{benchmark}-bearer"
    if not SECRET_NAME_RE.fullmatch(name):
        raise ValueError(f"{name!r} is not a valid Valkyrie secret name")
    return name


def register_service(valk: Path, benchmark: str, url: str, bearer: str, log_path: Path | None = None) -> dict:
    """Store `Bearer <token>` as the organization secret `<benchmark>-bearer` (stdin only) and point the benchmark at
    the tunnel URL. Needs a login. Returns a receipt without the URL or the token."""
    secret = bearer_secret_name(benchmark)
    stored = cli(valk, ["secret", "set", secret], timeout=120, login_only=True, stdin_text="Bearer " + bearer)
    saved = cli(valk, ["benchmark", "service", "set", benchmark, url, "--auth-secret", secret, "--auth-header",
                       "Authorization"], timeout=120, login_only=True) if stored.returncode == 0 else None
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as fh:
            fh.write(f"$ valkyrie secret set {secret} (rc={stored.returncode})\n{stored.stdout}{stored.stderr}\n")
            if saved is not None:
                fh.write(f"$ valkyrie benchmark service set {benchmark} <tunnel url> --auth-secret {secret} "
                         f"--auth-header Authorization (rc={saved.returncode})\n{saved.stdout}{saved.stderr}\n")
    if stored.returncode:
        raise SystemExit(f"`valkyrie secret set {secret}` failed (rc={stored.returncode}): {(stored.stderr or stored.stdout)[-400:]}")
    if saved is None or saved.returncode or f"Runs of {benchmark} now use" not in saved.stdout:
        tail = "" if saved is None else (saved.stderr or saved.stdout)[-400:]
        raise SystemExit(f"`valkyrie benchmark service set {benchmark}` failed: {tail}")
    return {"benchmark": benchmark, "registered_by": REGISTERED_BY, "auth_secret": secret, "auth_header": "Authorization"}
