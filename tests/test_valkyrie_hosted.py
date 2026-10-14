"""TLDR: Offline tests for cert_judge.valkyrie_hosted and the experiment 39/42 hosted-Valkyrie port. A fake `valkyrie`
executable records each call's arguments, stdin and whether VALKYRIE_API_KEY reached it; no Tracker or model call."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from cert_judge import valkyrie_hosted as VH

REPO = Path(__file__).resolve().parents[1]
FAKE = r'''#!{python}
import json, os, sys
args = sys.argv[1:]
data = sys.stdin.read() if args[:2] == ["secret", "set"] else ""
with open(os.environ["FAKE_VALK_LOG"], "a") as fh:
    fh.write(json.dumps({{"args": args, "stdin": data, "api_key": "VALKYRIE_API_KEY" in os.environ,
                         "legacy": [k for k in ("VALKYRIE_ENV", "VALKYRIE_CONFIG_PATH") if k in os.environ]}}) + "\n")
if args == ["whoami"]:
    cred = "an access key" if "VALKYRIE_API_KEY" in os.environ else os.environ.get("FAKE_LOGIN", "a login")
    print(f"user@example.org in brando-org on https://tracker.example (using {{cred}})")
elif args == ["provider", "list"]:
    print(os.environ.get("FAKE_PROVIDERS", "* daytona → daytona\n  modal → modal-key"))
elif args[:2] == ["secret", "set"]:
    print(args[2])
elif args[:3] == ["benchmark", "service", "set"]:
    print(f"Runs of {{args[3]}} now use {{args[4]}}, sending the secret {{args[6]}} as {{args[8]}}.")
else:
    print("ok")
'''


@pytest.fixture
def fake_valk(tmp_path, monkeypatch):
    exe = tmp_path / "valkyrie"
    exe.write_text(FAKE.format(python=sys.executable))
    exe.chmod(0o755)
    log = tmp_path / "calls.jsonl"
    monkeypatch.setenv("FAKE_VALK_LOG", str(log))
    monkeypatch.setenv("VALKYRIE_ENV", "bench")
    monkeypatch.setenv("VALKYRIE_CONFIG_PATH", "/nowhere/valkyrie.yaml")
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-pass")

    def calls():
        return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    return exe, calls


def test_env_drops_pre_hosted_settings_and_keeps_the_access_key(monkeypatch):
    monkeypatch.setenv("VALKYRIE_ENV", "bench")
    monkeypatch.setenv("VALKYRIE_CONFIG_PATH", "/x/valkyrie.yaml")
    monkeypatch.setenv("VALKYRIE_API_KEY", "k")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a")
    out = VH.env()
    assert "VALKYRIE_ENV" not in out and "VALKYRIE_CONFIG_PATH" not in out and "ANTHROPIC_API_KEY" not in out
    assert out["VALKYRIE_API_KEY"] == "k"
    assert "VALKYRIE_API_KEY" not in VH.env(login_only=True)


def test_parsers():
    who = VH.parse_whoami("a@b.c in my-org on https://t.example (using an access key)\n")
    assert who == {"organization": "my-org", "tracker": "https://t.example", "credential": "access_key"}
    assert VH.parse_whoami("Usage: valk [OPTIONS]") == {}
    prov = VH.parse_providers("* daytona → daytona\n  modal → modal-key\n")
    assert prov == {"default": "daytona", "providers": {"daytona": "daytona", "modal": "modal-key"}}
    unset = VH.parse_providers("* daytona (default; no secret set — run `valkyrie provider set daytona SECRET`)")
    assert unset["default"] == "daytona" and unset["providers"]["daytona"] is None


def test_preflight_pass_and_log(fake_valk, tmp_path):
    exe, calls = fake_valk
    receipt = VH.preflight(exe, tmp_path / "private/preflight.log")
    assert receipt["verdict"] == "PASS", receipt["problems"]
    assert receipt["organization"] == "brando-org" and receipt["credential"] == "login" and receipt["default_provider"] == "daytona"
    assert sorted(receipt["legacy_settings_ignored"]) == ["VALKYRIE_CONFIG_PATH", "VALKYRIE_ENV"]
    assert [c["args"] for c in calls()] == [["whoami"], ["provider", "list"]]
    assert all(not c["legacy"] for c in calls())             # pre-hosted settings never reach the CLI
    assert "user@example.org" not in json.dumps(receipt)   # the account stays in the private log
    assert "user@example.org" in (tmp_path / "private/preflight.log").read_text()


def test_preflight_fails_without_login_or_provider(fake_valk, monkeypatch):
    exe, _ = fake_valk
    monkeypatch.setenv("VALKYRIE_API_KEY", "k")
    assert VH.preflight(exe)["verdict"] == "PASS"            # an access key is enough to admit runs
    monkeypatch.setenv("FAKE_LOGIN", "no credential")
    bad = VH.preflight(exe, need_login=True)                 # registration ignores the key and needs the login
    assert bad["verdict"] == "FAIL" and "valkyrie login" in bad["problems"][0]
    monkeypatch.delenv("FAKE_LOGIN")
    monkeypatch.setenv("FAKE_PROVIDERS", "No provider has a secret yet. Map one with `valkyrie provider set NAME SECRET`.")
    assert VH.preflight(exe)["verdict"] == "FAIL"
    with pytest.raises(SystemExit):
        VH.require(VH.preflight(exe))


def test_preflight_rejects_a_pre_hosted_cli(tmp_path):
    old = tmp_path / "valk"
    old.write_text(f"#!{sys.executable}\nimport sys\nprint(\"Error: No such command 'whoami'.\", file=sys.stderr)\nsys.exit(2)\n")
    old.chmod(0o755)
    receipt = VH.preflight(old)
    assert receipt["verdict"] == "FAIL" and "uv tool install" in receipt["problems"][0]


def test_register_service_sends_the_bearer_on_stdin_only(fake_valk, tmp_path, monkeypatch):
    exe, calls = fake_valk
    monkeypatch.setenv("VALKYRIE_API_KEY", "k")
    receipt = VH.register_service(exe, "certjudge39-sol6h", "https://abc.trycloudflare.com", "tok123", tmp_path / "reg.log")
    secret_call, service_call = calls()
    assert secret_call["args"] == ["secret", "set", "certjudge39-sol6h-bearer"] and secret_call["stdin"] == "Bearer tok123"
    assert service_call["args"] == ["benchmark", "service", "set", "certjudge39-sol6h", "https://abc.trycloudflare.com",
                                    "--auth-secret", "certjudge39-sol6h-bearer", "--auth-header", "Authorization"]
    assert not secret_call["api_key"] and not service_call["api_key"]   # both use the login
    assert all("tok123" not in " ".join(c["args"]) for c in calls())
    assert receipt == {"benchmark": "certjudge39-sol6h", "registered_by": VH.REGISTERED_BY,
                       "auth_secret": "certjudge39-sol6h-bearer", "auth_header": "Authorization"}
    assert "tok123" not in (tmp_path / "reg.log").read_text()


def test_secret_names_are_tenant_valid():
    assert VH.SECRET_NAME_RE.fullmatch(VH.GATEWAY_SECRET) and "/" not in VH.GATEWAY_SECRET
    assert VH.bearer_secret_name("certjudge43-gaming") == "certjudge43-gaming-bearer"
    with pytest.raises(ValueError):
        VH.bearer_secret_name("fellows/x")


def test_resolve_cli_prefers_override(monkeypatch, tmp_path):
    monkeypatch.setenv("E39_VALK", str(tmp_path / "custom"))
    assert VH.resolve_cli(Path("/frozen/valk"), "E39_VALK") == tmp_path / "custom"


@pytest.mark.parametrize("exp", ["39_*", "42_*"])
def test_experiment_transports_are_ported(exp):
    scripts = next((REPO / "experiments").glob(exp)) / "scripts"
    for name in ("judge_controller.py", "verify_bundle.py", "verify_agent_harness.py", "deploy_service.py"):
        code = (scripts / name).read_text()
        assert "VALKYRIE_CONFIG_PATH=" not in code and "VALKYRIE_ENV=\"bench\"" not in code, name
        assert "custom_benchmark_services\", {})" not in code and "benchmark_auth\", {})" not in code, name
        assert "VH.cli(VALK" in code or "VH.register_service" in code, name
    assert "VH.register_service(VALK, benchmark, url, bearer" in (scripts / "deploy_service.py").read_text()
    assert "VH.GATEWAY_SECRET" in (scripts / "judge_controller.py").read_text()


def test_cloud_setup_uses_the_access_key():
    sh = (next((REPO / "experiments").glob("39_*")) / "scripts/cloud_valkyrie_setup.sh").read_text()
    assert "base64 -d" not in sh and "valkyrie.yaml\"" not in sh
    assert "VALKYRIE_API_KEY" in sh and "valkyrie whoami" in sh and "valkyrie provider list" in sh


def test_bundle_check_accepts_only_the_gateway_secret_rename():
    import hashlib

    def sha(b):
        return hashlib.sha256(b).hexdigest()
    old = b"name: vb103_judge\nsecrets:\n  MODEL_GATEWAY_API_KEY: fellows/brandoModelGatewayApiKey\n"
    new = old.replace(b"fellows/brandoModelGatewayApiKey", b"brandoModelGatewayApiKey")
    validated = {"contract.yaml": sha(old), "judge_call.py": "aa"}
    assert VH.matches_validated_except_secret_rename(dict(validated), validated, old)
    assert VH.matches_validated_except_secret_rename({"contract.yaml": sha(new), "judge_call.py": "aa"}, validated, new)
    tampered = new + b"run_cmd: other\n"
    assert not VH.matches_validated_except_secret_rename({"contract.yaml": sha(tampered), "judge_call.py": "aa"}, validated, tampered)
    assert not VH.matches_validated_except_secret_rename({"contract.yaml": sha(new), "judge_call.py": "bb"}, validated, new)
