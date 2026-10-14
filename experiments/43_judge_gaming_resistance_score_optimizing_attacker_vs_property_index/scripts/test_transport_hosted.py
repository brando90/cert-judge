"""TLDR: Offline tests for experiment 43's hosted-Valkyrie wrapper (transport_hosted.py): the scripts that ran the
09-30-2026 campaign are byte-identical, the wrapper rebinds the frozen transport's CLI and tunnel functions,
and every tunnel start, including the restart inside `ensure_live`, registers the new URL on the Tracker with the
bearer on stdin only. A fake `valkyrie` and a fake cloudflared stand in; no Tracker or model call."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e43                                                    # noqa: E402
import transport as TR                                        # noqa: E402

HERE = Path(__file__).resolve().parent
FAKE_VALK = r'''#!{python}
import json, os, sys
args = sys.argv[1:]
data = sys.stdin.read() if args[:2] == ["secret", "set"] else ""
with open(os.environ["FAKE_VALK_LOG"], "a") as fh:
    fh.write(json.dumps({{"args": args, "stdin": data, "api_key": "VALKYRIE_API_KEY" in os.environ,
                         "legacy": [k for k in ("VALKYRIE_ENV", "VALKYRIE_CONFIG_PATH") if k in os.environ]}}) + "\n")
if args == ["whoami"]:
    print("user@example.org in brando-org on https://tracker.example (using a login)")
elif args == ["provider", "list"]:
    print("* daytona → daytona")
elif args[:2] == ["secret", "set"]:
    print(args[2])
elif args[:3] == ["benchmark", "service", "set"]:
    print(f"Runs of {{args[3]}} now use {{args[4]}}, sending the secret {{args[6]}} as {{args[8]}}.")
else:
    print("ok")
'''
# Each start prints a fresh quick-tunnel hostname (a restart changes the URL), then idles like cloudflared.
FAKE_CLOUDFLARED = r'''#!{python}
import os, time, uuid
print(f"INF |  https://t-{{uuid.uuid4().hex[:10]}}.trycloudflare.com  |", flush=True)
time.sleep(60)
'''


@pytest.fixture
def hosted(tmp_path, monkeypatch):
    valk = tmp_path / "valkyrie"
    valk.write_text(FAKE_VALK.format(python=sys.executable))
    cloudflared = tmp_path / "cloudflared"
    cloudflared.write_text(FAKE_CLOUDFLARED.format(python=sys.executable))
    for exe in (valk, cloudflared):
        exe.chmod(0o755)
    log = tmp_path / "calls.jsonl"
    monkeypatch.setenv("FAKE_VALK_LOG", str(log))
    monkeypatch.setenv("E43_VALK", str(valk))
    monkeypatch.setenv("VALKYRIE_ENV", "bench")
    monkeypatch.setenv("VALKYRIE_CONFIG_PATH", str(tmp_path / "valkyrie.yaml"))
    monkeypatch.setenv("VALKYRIE_API_KEY", "access-key")
    monkeypatch.setattr(e43, "PRIVATE", tmp_path / "private")
    (tmp_path / "private").mkdir()
    import transport_hosted as TH
    monkeypatch.setattr(TH, "VALK", valk)
    monkeypatch.setattr(TR, "CLOUDFLARED", cloudflared)
    monkeypatch.setattr(TR, "probe", lambda url, bearer: 200 if bearer else 401)
    TH._PREFLIGHT.clear()
    TH.install()
    yield TH, (lambda: [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else [])
    for pid in (TR.deployment().get("tunnel_pid"),):
        if pid and TR.alive(pid):
            os.kill(int(pid), 15)
    for name, fn in TH.FROZEN.items():                       # leave the frozen module as other tests expect it
        setattr(TR, name, fn)


# The bytes that ran the 09-30-2026 campaign (Amendment 1 included; last changed in commit ba6e9f2). The hosted port
# never edits them; results/protocol_hashes.json is the earlier pre-pilot lock.
AS_RUN = {"transport.py": "a7573809f818e031753a903d75e6efbc9ce7fff21973dc53f3cbd806588111ea",
          "attack.py": "976eb292195da753e9bc22d2388fd582d425fb50ded9d4bf42711190f16ab727",
          "e43.py": "0aed514c23d7629c33977ccac7e0d0fc5a6c0c9da0a083bb735256710a7ec44c",
          "worker_loop.sh": "c75e75bf8e7ea984257c691011f5dace9e2c911fb20c3c11a08993d09c679c5b"}


def test_as_run_scripts_are_untouched():
    assert {name: e43.sha_file(HERE / name) for name in AS_RUN} == AS_RUN


def test_install_rebinds_the_frozen_transport(hosted):
    TH, _ = hosted
    assert TR.cli is TH.cli and TR.start_tunnel is TH.start_tunnel and TR.admit is TH.admit and TR.deploy is TH.deploy
    assert TH.FROZEN["cli"] is not TH.cli
    env = TR.env()
    assert "VALKYRIE_ENV" not in env and "VALKYRIE_CONFIG_PATH" not in env and env["VALKYRIE_API_KEY"] == "access-key"


def test_tunnel_restart_re_registers_the_new_url(hosted):
    TH, calls = hosted
    first = TR.start_tunnel()
    dep = TR.deployment()
    assert dep["registered_by"] == TH.VH.REGISTERED_BY and dep["auth_secret"] == "certjudge43-gaming-bearer"
    # ensure_live with the service up and the tunnel gone: the frozen code restarts the tunnel, which re-registers
    os.kill(int(dep["tunnel_pid"]), 15)
    os.waitpid(int(dep["tunnel_pid"]), 0)
    e43.write_json(e43.PRIVATE / "deployment.json", {**TR.deployment(), "service_pid": os.getpid()})
    TR.ensure_live()
    second = TR.deployment()["tunnel_url"]
    assert second != first
    service_sets = [c for c in calls() if c["args"][:3] == ["benchmark", "service", "set"]]
    assert [c["args"][4] for c in service_sets] == [first, second]
    assert all(c["args"][5:] == ["--auth-secret", "certjudge43-gaming-bearer", "--auth-header", "Authorization"] for c in service_sets)
    secret_sets = [c for c in calls() if c["args"][:2] == ["secret", "set"]]
    token = TR.bearer()
    assert len(secret_sets) == 2 and all(c["stdin"] == "Bearer " + token for c in secret_sets)
    assert all(token not in " ".join(c["args"]) for c in calls())
    assert not any(c["api_key"] for c in service_sets + secret_sets)     # registration uses the login
    assert not any(c["legacy"] for c in calls())
    assert not (e43.PRIVATE / "valkyrie.yaml").exists()


def test_admit_refuses_an_unregistered_deployment(hosted):
    TH, calls = hosted
    e43.write_json(e43.PRIVATE / "deployment.json", {"benchmark": e43.BENCHMARK})
    with pytest.raises(SystemExit, match="no server-side registration"):
        TR.admit("k", [TR.Request("r1", "s", "u", "openai/x")], 1)
    assert [c["args"] for c in calls()] == [["whoami"], ["provider", "list"]]
