#!/usr/bin/env python3
"""TLDR: Experiment 43's transport on hosted Valkyrie (10-14-2026). `transport.py`, `attack.py` and `e43.py` stay
byte-identical to what ran the 09-30-2026 campaign (Amendment 1 bytes; `results/protocol_hashes.json` is the earlier
pre-pilot lock). Importing this module rebinds six functions of the `transport` module that every other script
imports: CLI calls no longer set `VALKYRIE_ENV` / `VALKYRIE_CONFIG_PATH` and keep the login or `VALKYRIE_API_KEY`;
`start_tunnel` registers each new tunnel URL on the Tracker (`valkyrie secret set certjudge43-gaming-bearer`, then
`valkyrie benchmark service set ... --auth-secret`) instead of writing a private `valkyrie.yaml`, so the tunnel
restart in `ensure_live` re-registers automatically; `deploy` and `admit` run a `valkyrie whoami` +
`valkyrie provider list` preflight; `verify_bundle` records the hosted route. Task files, prompt bytes, grouping,
admission bookkeeping, polling, harvest and parsing remain the frozen code.

Usage:  transport_hosted.py preflight | deploy | status | verify-bundle | charges     (zero model calls)
        transport_hosted.py attack run|post|gates|all [--stage S] [--fake]          (attack.py on this transport)
"""
from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parents[3] / "py_src")]
import e43                                                    # noqa: E402
import transport as TR                                        # noqa: E402
from cert_judge import valkyrie_hosted as VH                   # noqa: E402

VALK = VH.resolve_cli(e43.VALK, "E43_VALK")
FROZEN = {name: getattr(TR, name) for name in ("env", "cli", "start_tunnel", "deploy", "verify_bundle", "admit")}
_PREFLIGHT: dict = {}


def preflight(need_login: bool = False) -> dict:
    """Zero-call identity and sandbox check (once per process; again when a login is newly required)."""
    if not _PREFLIGHT.get("receipt") or (need_login and not _PREFLIGHT.get("login")):
        _PREFLIGHT["receipt"] = VH.require(VH.preflight(VALK, e43.PRIVATE / "valkyrie_preflight.log", need_login=need_login))
        _PREFLIGHT["login"] = need_login
    return _PREFLIGHT["receipt"]


def _preflight_summary() -> dict:
    return {k: preflight()[k] for k in ("organization", "credential", "default_provider")}


def env() -> dict[str, str]:
    return VH.env()


def cli(args: list[str], timeout: int = 1800) -> subprocess.CompletedProcess:
    return VH.cli(VALK, args, timeout=timeout)


def start_tunnel() -> str:
    """The frozen tunnel start, with server-side registration of the new URL in place of the valkyrie.yaml write."""
    preflight(need_login=True)                                 # fail before the old tunnel is stopped
    token = TR.bearer()
    dep = TR.deployment()
    if dep.get("tunnel_pid") and TR.alive(dep["tunnel_pid"]):
        os.kill(int(dep["tunnel_pid"]), signal.SIGTERM)
    tlog = e43.PRIVATE / "tunnel.log"
    tlog.write_bytes(b"")
    fh = open(tlog, "ab", buffering=0)
    proc = subprocess.Popen([str(TR.CLOUDFLARED), "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{e43.PORT}"],
                            stdin=subprocess.DEVNULL, stdout=fh, stderr=fh, start_new_session=True)
    url = None
    for _ in range(90):
        found = re.findall(r"https://[a-z0-9-]+\.trycloudflare\.com", tlog.read_text())
        if found:
            url = found[-1]
            break
        time.sleep(2)
    if not url:
        raise SystemExit("tunnel hostname timed out")
    for _ in range(60):
        if TR.probe(url + "/health", token) == 200:
            break
        time.sleep(2)
    else:
        raise SystemExit("tunnel health timed out")
    if TR.probe(url + "/health", None) != 401:
        raise SystemExit("tunnel answered an unauthenticated probe; refusing")
    registration = VH.register_service(VALK, e43.BENCHMARK, url, token, e43.PRIVATE / "registration.log")
    dep = TR.deployment()
    dep.update(registration)
    dep.update(tunnel_pid=proc.pid, tunnel_url=url, tunnel_started_utc=e43.stamp(), benchmark=e43.BENCHMARK, port=e43.PORT,
               registered_utc=e43.stamp(), route=VH.ROUTE)
    e43.write_json(e43.PRIVATE / "deployment.json", dep)
    TR.log(f"tunnel up and {e43.BENCHMARK} registered on the Tracker (URL in private/deployment.json)")
    return url


def deploy() -> dict:
    """First deployment: the frozen steps, with the login and sandbox-provider preflight in place of valkyrie.yaml."""
    for path in (TR.SERVICE_DIR, TR.KERNEL_AXIOMS, TR.VENV / "bin/uvicorn", TR.CLOUDFLARED):
        if not Path(path).exists():
            raise SystemExit(f"missing: {path}")
    preflight(need_login=True)
    if not TR.PACK.is_dir() or not any(TR.PACK.iterdir()):
        TR.write_task(TR.Request("health_probe", "Answer with the single word OK.", "Reply OK.", "none", role="health"))
    TR.start_service()
    TR.start_tunnel()
    dep = TR.deployment()
    public = {k: v for k, v in dep.items() if k != "tunnel_url"}
    public.update(tunnel_url="recorded in private/deployment.json (not published)", service_dir=str(TR.SERVICE_DIR),
                  service_code="experiment 103 vb_service_single_call, run read-only with experiment 43's environment",
                  service_files_sha256={p.name: e43.sha_file(p) for p in sorted(TR.SERVICE_DIR.glob("*.py"))},
                  control_pack=True, grade_mode="collect_only", sandbox_lean="none", local_unauthenticated_health=401,
                  tunnel_unauthenticated_health=401, valkyrie_preflight=_preflight_summary(), inference_calls=0,
                  written_utc=e43.stamp())
    e43.write_json(e43.RESULTS / "deployment.json", public)
    return public


def verify_bundle() -> int:
    preflight()
    rc = FROZEN["verify_bundle"]()                             # downloads through the rebound cli
    path = e43.RESULTS / "agent_bundle_check.json"
    receipt = e43.read_json(path)
    receipt.update(route=VH.ROUTE, valkyrie_preflight=_preflight_summary())
    e43.write_json(path, receipt)
    return rc


def admit(run_key: str, reqs: list, concurrency: int) -> dict:
    preflight()
    if TR.deployment().get("registered_by") != VH.REGISTERED_BY:
        raise SystemExit(f"{e43.BENCHMARK} has no server-side registration (deployment predates hosted Valkyrie); "
                         "run `transport_hosted.py deploy` first")
    return FROZEN["admit"](run_key, reqs, concurrency)


def install() -> None:
    """Rebind the transport module's functions; frozen callers (run_batch, ensure_live, main, attack.py) pick them up."""
    TR.env, TR.cli, TR.start_tunnel, TR.deploy, TR.verify_bundle, TR.admit = env, cli, start_tunnel, deploy, verify_bundle, admit


install()


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "attack":
        import attack                                          # noqa: E402  (imports the rebound transport module)
        sys.argv = [str(Path(attack.__file__))] + sys.argv[2:]
        return attack.main()
    if len(sys.argv) > 1 and sys.argv[1] == "preflight":
        receipt = VH.preflight(VALK, e43.PRIVATE / "valkyrie_preflight.log", need_login="--login" in sys.argv[2:])
        print(json.dumps({k: receipt[k] for k in ("verdict", "credential", "default_provider", "providers", "problems",
                                                   "legacy_settings_ignored")}, indent=1))
        return 0 if receipt["verdict"] == "PASS" else 1
    return TR.main()


if __name__ == "__main__":
    raise SystemExit(main())
