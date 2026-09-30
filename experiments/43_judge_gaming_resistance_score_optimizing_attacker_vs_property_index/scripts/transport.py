#!/usr/bin/env python3
"""TLDR: Experiment 43's Valkyrie transport — every model call (attacker, attacked judge, reference) is one task of
the benchmark `certjudge43-gaming`, served read-only by experiment 103's collect-only single-call service from an
append-only task pack and answered by experiment 103's validated `vb103_judge` agent (prompt bytes in, one gateway
call, raw completion out). A batch writes its tasks, reloads the service (same port, same tunnel), records every
admission BEFORE the CLI call, admits one run per (selector, effort, max_tokens) group, polls, harvests, and gives
unanswered requests exactly one labelled recovery admission. A request that has a verdict is never re-admitted.

Usage:  transport.py deploy | status | verify-bundle      (zero model calls)
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import secrets
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e43                                                    # noqa: E402

T = e43.PRIVATE / "transport"
PACK = T / "pack"
STATE = T / "state.json"
REQ_DIR = T / "requests"          # one JSON per request: admission history and final result (raw text kept here)
RAW = T / "raw"
SERVICE_DIR = e43.X103 / "scripts/vb_service_single_call"
VENV = Path(os.environ.get("E43_VENV", "/lfs/skampere1/0/brando9/vb103_venv"))
CLOUDFLARED = Path(os.environ.get("E43_CLOUDFLARED", "/lfs/skampere1/0/brando9/vb-e2-service-20260916/bin/cloudflared"))
KERNEL_AXIOMS = e43.VB_REPO / "scripts/scsc/kernel_axioms.py"
VALKYRIE_SOURCE = Path(os.environ.get("E43_VALKYRIE_SOURCE", str(Path.home() / ".config/valkyrie/valkyrie.yaml")))
LOCAL_BUNDLE = e43.X103 / "scripts/valkyrie_judge_agent"
BUNDLE_RECEIPT = e43.X103 / "results/agent_bundle_judge.json"

STAMP_LINE = "<!-- VeriBench agent-spec v6: experiment 43 transport task (attacker, judge or reference call), not a solver task -->"
SYS_BEGIN, SYS_END = "=== VB103_JUDGE_SYSTEM_BEGIN ===", "=== VB103_JUDGE_SYSTEM_END ==="
USER_BEGIN, USER_END = "=== VB103_JUDGE_USER_BEGIN ===", "=== VB103_JUDGE_USER_END ==="
OUTPUT_PATH = "/home/user/lean_project/Veribench/JudgeVerdict.lean"
MARKERS = (SYS_BEGIN, SYS_END, USER_BEGIN, USER_END, "vb103-judge-cell")
TEST_SH = ('#!/usr/bin/env bash\n'
           '# TLDR: Path declaration for an experiment 43 transport task; the service reads only the SOLUTION_FILE\n'
           '# line and never executes this file (the completion is parsed on the host).\n'
           f'SOLUTION_FILE="{OUTPUT_PATH}"\n'
           'exit 0\n')
UUID_RE = re.compile(r"[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}")
TERMINAL_RUN = {"finished", "completed", "error", "failed", "stopped", "cancelled", "canceled", "success", "succeeded"}
NO_VERDICT = ("unmeasured_infra", "model_error", "incomplete")
POLL_S = int(os.environ.get("E43_POLL_S", "45"))
RUN_TIMEOUT_S = int(os.environ.get("E43_RUN_TIMEOUT_S", str(4 * 3600)))


@dataclass
class Request:
    req_id: str                 # [A-Za-z0-9_]+, unique for the whole experiment
    system: str
    user: str
    selector: str
    kwargs: dict = field(default_factory=dict)
    max_tokens: int = 32000
    role: str = ""              # attacker | judge | rescore | reference
    config: str = ""            # judge configuration or reference member (receipt only)


def env() -> dict[str, str]:
    out = dict(os.environ)
    for key in ("VALKYRIE_API_KEY", "TRACKER_SERVICE_URL", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
                "GOOGLE_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_AUTH_TOKEN", "PYTHONPATH", "PYTHONHOME"):
        out.pop(key, None)
    out.update(VALKYRIE_ENV="bench", VALKYRIE_CONFIG_PATH=str(e43.PRIVATE / "valkyrie.yaml"))
    return out


def cli(args: list[str], timeout: int = 1800) -> subprocess.CompletedProcess:
    return subprocess.run([str(e43.VALK)] + args, env=env(), stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)


def log(msg: str) -> None:
    line = f"{e43.stamp()} {msg}"
    print(line, flush=True)
    (e43.PRIVATE / "logs").mkdir(parents=True, exist_ok=True)
    with (e43.PRIVATE / "logs" / "transport.log").open("a") as fh:
        fh.write(line + "\n")


# ---------------------------------------------------------------------------------------------------------
# state
# ---------------------------------------------------------------------------------------------------------
def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {"runs": {}, "created": e43.stamp()}


def save_state(state: dict) -> None:
    state["updated"] = e43.stamp()
    e43.write_json(STATE, state)


def req_path(req_id: str) -> Path:
    return REQ_DIR / f"{req_id}.json"


def load_req(req_id: str) -> dict | None:
    p = req_path(req_id)
    return json.loads(p.read_text()) if p.exists() else None


def save_req(rec: dict) -> None:
    e43.write_json(req_path(rec["req_id"]), rec)


# ---------------------------------------------------------------------------------------------------------
# pack
# ---------------------------------------------------------------------------------------------------------
def task_id_of(req_id: str) -> str:
    assert re.fullmatch(r"[A-Za-z0-9_]+", req_id), req_id
    return f"e43__{req_id}"


def task_file(req: Request) -> str:
    for text, what in ((req.system, "system"), (req.user, "user")):
        for marker in MARKERS:
            assert marker not in text, f"{req.req_id}: the {what} prompt contains the marker {marker!r}"
    header = {"cell": req.req_id, "item": None, "repeat": 1, "kind": req.role, "rubric": req.config, "output_path": OUTPUT_PATH,
              "system_sha256": e43.sha(req.system.encode()), "user_sha256": e43.sha(req.user.encode()),
              "prompt_sha256": e43.sha((req.system + "\n\n" + req.user).encode())}
    return (STAMP_LINE + "\n" + "<!-- vb103-judge-cell: " + json.dumps(header, sort_keys=True) + " -->\n"
            + SYS_BEGIN + "\n" + req.system + "\n" + SYS_END + "\n" + USER_BEGIN + "\n" + req.user + "\n" + USER_END + "\n")


def write_task(req: Request) -> str:
    tid = task_id_of(req.req_id)
    body = task_file(req)
    d = PACK / tid
    if (d / "instruction.md").exists():
        assert (d / "instruction.md").read_text() == body, f"{tid}: task exists with different bytes"
        return tid
    (d / "tests").mkdir(parents=True, exist_ok=True)
    (d / "tests/test.sh").write_text(TEST_SH)
    tmp = d / "instruction.md.tmp"
    tmp.write_text(body)
    tmp.replace(d / "instruction.md")
    return tid


def round_trip(req: Request) -> bool:
    """The task file parses back to the same prompt bytes with the agent's own parser."""
    sys.path[:0] = [str(e43.X103 / "scripts/valkyrie_judge_agent")]
    import judge_call                                        # noqa: E402
    header, system, user = judge_call.parse_task_file((PACK / task_id_of(req.req_id) / "instruction.md").read_text())
    return system == req.system and user == req.user and header["prompt_sha256"] == e43.sha((system + "\n\n" + user).encode())


# ---------------------------------------------------------------------------------------------------------
# service and tunnel
# ---------------------------------------------------------------------------------------------------------
def alive(pid) -> bool:
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, TypeError, ValueError):
        return False


def probe(url: str, bearer: str | None) -> int:
    headers = {"Authorization": "Bearer " + bearer} if bearer else {}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        return 0


def bearer() -> str:
    path = e43.PRIVATE / "service_bearer"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(secrets.token_urlsafe(36))
    os.chmod(path, 0o600)
    return path.read_text().strip()


def deployment() -> dict:
    p = e43.PRIVATE / "deployment.json"
    return json.loads(p.read_text()) if p.exists() else {}


def _service_env() -> dict:
    out = dict(os.environ)
    for key in ("AUTH_DISABLED", "PYTHONPATH", "PYTHONHOME", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
                "GOOGLE_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN"):
        out.pop(key, None)
    out.update(VB_SERVICE_KEY_FILE=str(e43.PRIVATE / "service_bearer"), VB_TASK_PACK=str(PACK), VB_CONTROL_PACK="1",
               VB_NO_COMPILER="1", VB_COLLECT_ONLY="1", VB_LAKE_DIR=str(e43.LAKE_DIR), VB_KERNEL_AXIOMS=str(KERNEL_AXIOMS),
               VB_GRADE_SCRATCH=str(e43.PRIVATE / "grade_scratch"), VB_GRADE_NETNS="off", VB_IC_PP="offline",
               VB_AGENT_TIMEOUT_S="3600", VB_SETUP_TIMEOUT_S="900", VB_RESOURCES_VCPU="2", VB_RESOURCES_MEMORY="4",
               VB_RESOURCES_DISK="20")
    return out


def start_service() -> int:
    """(Re)start the collect-only service on PORT with the current pack; the tunnel keeps pointing at the port."""
    os.umask(0o077)
    dep = deployment()
    old = dep.get("service_pid")
    if old and alive(old):
        os.killpg(int(old), signal.SIGTERM) if _is_group_leader(old) else os.kill(int(old), signal.SIGTERM)
        for _ in range(30):
            if not alive(old):
                break
            time.sleep(1)
    token = bearer()
    for _ in range(30):                                        # the port must be free before rebinding
        if probe(f"http://127.0.0.1:{e43.PORT}/health", token) == 0:
            break
        time.sleep(1)
    logf = open(e43.PRIVATE / "service.log", "ab", buffering=0)
    proc = subprocess.Popen([str(VENV / "bin/uvicorn"), "main:app", "--host", "127.0.0.1", "--port", str(e43.PORT)],
                            cwd=str(SERVICE_DIR), env=_service_env(), stdin=subprocess.DEVNULL, stdout=logf, stderr=logf,
                            start_new_session=True)
    for _ in range(120):
        if probe(f"http://127.0.0.1:{e43.PORT}/health", token) == 200:
            break
        if proc.poll() is not None:
            raise SystemExit("service exited during startup; see private/service.log")
        time.sleep(2)
    else:
        raise SystemExit("local service health timed out")
    if probe(f"http://127.0.0.1:{e43.PORT}/health", None) != 401:
        proc.terminate()
        raise SystemExit("local service answered an unauthenticated probe; refusing to expose it")
    dep.update(service_pid=proc.pid, service_started_utc=e43.stamp(), pack_task_count=sum(1 for p in PACK.iterdir() if p.is_dir()))
    e43.write_json(e43.PRIVATE / "deployment.json", dep)
    return proc.pid


def _is_group_leader(pid) -> bool:
    try:
        return os.getpgid(int(pid)) == int(pid)
    except OSError:
        return False


def start_tunnel() -> str:
    token = bearer()
    dep = deployment()
    if dep.get("tunnel_pid") and alive(dep["tunnel_pid"]):
        os.kill(int(dep["tunnel_pid"]), signal.SIGTERM)
    tlog = e43.PRIVATE / "tunnel.log"
    tlog.write_bytes(b"")
    fh = open(tlog, "ab", buffering=0)
    proc = subprocess.Popen([str(CLOUDFLARED), "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{e43.PORT}"],
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
        if probe(url + "/health", token) == 200:
            break
        time.sleep(2)
    else:
        raise SystemExit("tunnel health timed out")
    if probe(url + "/health", None) != 401:
        raise SystemExit("tunnel answered an unauthenticated probe; refusing")
    import yaml                                                # noqa: E402  (vb103 venv or system PyYAML)
    target = e43.PRIVATE / "valkyrie.yaml"
    cfg = yaml.safe_load((target if target.exists() else VALKYRIE_SOURCE).read_text())
    cfg.setdefault("custom_benchmark_services", {})[e43.BENCHMARK] = url
    cfg.setdefault("benchmark_auth", {})[e43.BENCHMARK] = "Bearer " + token
    target.write_text(yaml.safe_dump(cfg))
    os.chmod(target, 0o600)
    dep = deployment()
    dep.update(tunnel_pid=proc.pid, tunnel_url=url, tunnel_started_utc=e43.stamp(), benchmark=e43.BENCHMARK, port=e43.PORT)
    e43.write_json(e43.PRIVATE / "deployment.json", dep)
    return url


def deploy() -> dict:
    """First deployment: the pack must hold at least one task (the service refuses an empty pack)."""
    for path in (SERVICE_DIR, KERNEL_AXIOMS, VENV / "bin/uvicorn", CLOUDFLARED, VALKYRIE_SOURCE):
        if not Path(path).exists():
            raise SystemExit(f"missing: {path}")
    if not PACK.is_dir() or not any(PACK.iterdir()):
        write_task(Request("health_probe", "Answer with the single word OK.", "Reply OK.", "none", role="health"))
    start_service()
    start_tunnel()
    dep = deployment()
    public = {k: v for k, v in dep.items() if k != "tunnel_url"}
    public.update(tunnel_url="recorded in private/deployment.json (not published)", service_dir=str(SERVICE_DIR),
                  service_code="experiment 103 vb_service_single_call, run read-only with experiment 43's environment",
                  service_files_sha256={p.name: e43.sha_file(p) for p in sorted(SERVICE_DIR.glob("*.py"))},
                  control_pack=True, grade_mode="collect_only", sandbox_lean="none", local_unauthenticated_health=401,
                  tunnel_unauthenticated_health=401, inference_calls=0, written_utc=e43.stamp())
    e43.write_json(e43.RESULTS / "deployment.json", public)
    return public


def ensure_live() -> None:
    """Between batches only: service and tunnel alive and healthy through the tunnel; otherwise restart them."""
    dep = deployment()
    token = bearer()
    if not dep.get("tunnel_pid") or not alive(dep["tunnel_pid"]) or probe(dep.get("tunnel_url", "") + "/health", token) != 200:
        if dep.get("service_pid") and alive(dep["service_pid"]) and probe(f"http://127.0.0.1:{e43.PORT}/health", token) == 200:
            log("tunnel down; restarting the tunnel (new URL recorded in private/valkyrie.yaml)")
            start_tunnel()
        else:
            log("service and tunnel down; redeploying")
            start_service()
            start_tunnel()


def status() -> int:
    dep = deployment()
    token = bearer()
    out = {"service_alive": alive(dep.get("service_pid")), "tunnel_alive": alive(dep.get("tunnel_pid")),
           "local_health": probe(f"http://127.0.0.1:{e43.PORT}/health", token),
           "tunnel_health": probe(dep.get("tunnel_url", "") + "/health", token) if dep.get("tunnel_url") else None,
           "pack_task_count": sum(1 for p in PACK.iterdir() if p.is_dir()) if PACK.is_dir() else 0}
    print(json.dumps(out, indent=1))
    return 0 if out["service_alive"] and out["tunnel_alive"] else 1


def verify_bundle() -> int:
    """Download the published vb103_judge bundle and prove it is experiment 103's validated bytes (download only)."""
    into = e43.PRIVATE / "agent_download_judge"
    if into.exists():
        shutil.rmtree(into)
    into.mkdir(parents=True)
    result = cli(["agent", "download", e43.AGENT, "-o", str(into)], timeout=900)
    (e43.PRIVATE / "agent_download.log").write_text(result.stdout + result.stderr)
    if result.returncode:
        raise SystemExit(f"download of {e43.AGENT} failed: {(result.stderr or '')[-600:]}")

    def tree(root: Path) -> dict[str, str]:
        return {p.relative_to(root).as_posix(): e43.sha_file(p) for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
    downloaded, local = tree(into / e43.AGENT), tree(LOCAL_BUNDLE)
    validated = e43.read_json(BUNDLE_RECEIPT)["downloaded_files_sha256"]
    receipt = {"written_utc": e43.stamp(), "agent": e43.AGENT, "route": "Valkyrie (VALKYRIE_ENV=bench)",
               "pushed_by": "experiment 103; experiment 43 downloads only", "experiment_103_validated_sha256": validated,
               "experiment_103_local_files_sha256": local, "downloaded_now_sha256": downloaded,
               "identical_to_experiment_103_validated_bundle": downloaded == validated,
               "identical_to_experiment_103_local_files": downloaded == local, "inference_calls": 0}
    receipt["verdict"] = "PASS" if receipt["identical_to_experiment_103_validated_bundle"] and receipt["identical_to_experiment_103_local_files"] else "FAIL"
    e43.write_json(e43.RESULTS / "agent_bundle_check.json", receipt)
    print(json.dumps({k: receipt[k] for k in ("verdict", "identical_to_experiment_103_validated_bundle", "identical_to_experiment_103_local_files")}))
    return 0 if receipt["verdict"] == "PASS" else 1


# ---------------------------------------------------------------------------------------------------------
# runs
# ---------------------------------------------------------------------------------------------------------
def _group_key(req: Request) -> str:
    return json.dumps([req.selector, sorted(req.kwargs.items()), req.max_tokens, req.role], sort_keys=True)


def admit(run_key: str, reqs: list[Request], concurrency: int) -> dict:
    hold = e43.PRIVATE / "HOLD_ADMISSIONS"
    if hold.exists():
        raise SystemExit(f"admissions on hold ({hold}): {hold.read_text().strip()}")
    bundle = e43.read_json(e43.RESULTS / "agent_bundle_check.json")
    assert bundle["verdict"] == "PASS", "the transport bundle on the server is not the validated bytes"
    state = load_state()
    if run_key in state["runs"]:
        log(f"{run_key}: already admitted as {state['runs'][run_key].get('run_id')}; refusing a second admission")
        return state["runs"][run_key]
    ids = [task_id_of(r.req_id) for r in reqs]
    ids_file = T / "task_ids" / f"{run_key}.txt"
    ids_file.parent.mkdir(parents=True, exist_ok=True)
    ids_file.write_text("".join(i + "\n" for i in ids))
    head = reqs[0]
    kwargs = {"judge_config": head.config or head.role, "max_tokens": str(head.max_tokens), "benchmark": e43.BENCHMARK}
    kwargs.update({k: str(v) for k, v in head.kwargs.items()})
    args = ["run", "start", "--agent", e43.AGENT, "--benchmark", e43.BENCHMARK, "--dataset", "default", "--model", head.selector,
            "--concurrency", str(min(concurrency, len(ids))), "--task-ids-file", str(ids_file), "--label", f"cj43-{run_key}"[:96]]
    for k, v in kwargs.items():
        args += ["-k", k, v]
    entry = {"run_key": run_key, "selector": head.selector, "kwargs": kwargs, "role": head.role, "req_ids": [r.req_id for r in reqs],
             "expected": len(ids), "admitted_at": e43.stamp(), "phase": "admitting", "command": args}
    state["runs"][run_key] = entry
    save_state(state)                                          # recorded BEFORE the call: an admission is never replayed
    for r in reqs:
        rec = load_req(r.req_id) or {"req_id": r.req_id, "role": r.role, "config": r.config, "selector": r.selector, "admissions": []}
        rec["admissions"].append({"run_key": run_key, "at": e43.stamp()})
        save_req(rec)
    result = cli(args)
    (T / "admissions").mkdir(parents=True, exist_ok=True)
    (T / "admissions" / f"{run_key}.log").write_text(result.stdout + result.stderr)
    found = UUID_RE.findall(result.stdout)
    if result.returncode or not found:
        entry.update(phase="admission_failed", returncode=result.returncode, stderr_tail=(result.stderr or result.stdout or "")[-800:])
        log(f"{run_key}: ADMISSION FAILED rc={result.returncode}: {(result.stderr or result.stdout or '')[-300:]}")
    else:
        entry.update(phase="running", run_id=found[0])
        log(f"{run_key}: run_id={found[0]} over {len(ids)} tasks ({head.selector}, {head.role})")
    state = load_state()
    state["runs"][run_key] = entry
    save_state(state)
    return entry


def poll_run(entry: dict) -> dict:
    result = cli(["run", "status", "--ids", entry["run_id"], "--format", "json"], timeout=600)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        entry["poll_error"] = (result.stderr or result.stdout or "")[-300:]
        return entry
    runs = payload.get("runs") if isinstance(payload, dict) else payload
    row = runs[0] if isinstance(runs, list) and runs else (runs if isinstance(runs, dict) else (payload if isinstance(payload, dict) else {}))
    counts = row.get("task_state_counts") or row.get("task_states") or {}
    status_ = str(row.get("status") or row.get("state") or "").lower()
    terminal = sum(int(counts.get(k, 0)) for k in ("FINISHED", "ERROR", "STOPPED"))
    entry.update(run_status=status_, task_state_counts=counts, cells_terminal=terminal, polled_at=e43.stamp())
    if status_ in TERMINAL_RUN and terminal >= entry["expected"]:
        entry["phase"] = "terminal"
    return entry


def wait_runs(run_keys: list[str]) -> None:
    t0 = time.time()
    while True:
        state = load_state()
        pending = [k for k in run_keys if state["runs"].get(k, {}).get("phase") == "running"]
        if not pending:
            return
        for k in pending:
            state["runs"][k] = poll_run(state["runs"][k])
        save_state(state)
        summary = {k: f"{state['runs'][k].get('cells_terminal')}/{state['runs'][k]['expected']} {state['runs'][k].get('run_status')}" for k in pending}
        log(f"poll: {summary}")
        if time.time() - t0 > RUN_TIMEOUT_S:
            for k in pending:
                if state["runs"][k].get("phase") == "running":
                    state["runs"][k]["phase"] = "timed_out_unterminal"
                    log(f"{k}: not terminal after {RUN_TIMEOUT_S}s; harvesting what exists (unanswered tasks are labelled)")
            save_state(state)
            return
        time.sleep(POLL_S)


def _rows_of(results_path: Path) -> dict[str, dict]:
    payload = json.loads(results_path.read_text())
    blob = payload[0] if isinstance(payload, list) and payload else payload
    raw = (blob.get("evaluation_results") or blob.get("results") or blob.get("task_results") or {})
    out = {}
    for task_id, value in raw.items():
        row = value.get("result", value) if isinstance(value, dict) else value
        out[task_id] = row if isinstance(row, dict) else {}
    return out


def harvest(run_key: str) -> dict[str, dict]:
    state = load_state()
    entry = state["runs"][run_key]
    out: dict[str, dict] = {}
    if not entry.get("run_id"):
        for rid in entry["req_ids"]:
            out[rid] = {"status": "unmeasured_infra", "reason": "admission failed", "run_key": run_key}
        return out
    RAW.mkdir(parents=True, exist_ok=True)
    results_path, artifacts = RAW / f"{run_key}_results.json", RAW / f"{run_key}_artifacts"
    if artifacts.exists():
        shutil.rmtree(artifacts)
    with (RAW / f"{run_key}_download.log").open("w") as fh:
        for args in (["run", "results", entry["run_id"], "--path", str(results_path)], ["run", "output", entry["run_id"], "-o", str(artifacts)]):
            done = cli(args, timeout=5400)
            fh.write(f"{e43.stamp()} {' '.join(args[:3])} rc={done.returncode}\n")
            if done.returncode:
                fh.write((done.stdout or "")[-2000:] + (done.stderr or "")[-2000:] + "\n")
    served = _rows_of(results_path) if results_path.exists() else {}
    receipts = {}
    if artifacts.exists():
        for path in sorted(artifacts.rglob("receipt.json")):
            try:
                receipt = json.loads(path.read_text())
            except json.JSONDecodeError:
                continue
            receipts[receipt.get("task_id") or path.parent.name] = receipt
    charges = 0.0
    for rid in entry["req_ids"]:
        tid = task_id_of(rid)
        row, receipt = served.get(tid, {}), receipts.get(tid, {})
        res = {"run_key": run_key, "run_id": entry["run_id"], "agent_status": receipt.get("status"), "cost_usd": receipt.get("cost_usd"),
               "finish_reason": receipt.get("finish_reason"), "usage": receipt.get("usage"), "http_status": receipt.get("http_status"),
               "submission_status": row.get("submission_status"), "prompt_sha256_delivered": receipt.get("prompt_sha256"),
               "selector": entry["selector"]}
        charges += res["cost_usd"] or 0.0
        blob = row.get("solution_b64")
        if blob and receipt.get("status") in ("measured", None):
            text = base64.b64decode(blob).decode("utf-8", errors="replace")
            res.update(status="measured", text=text, text_sha256=e43.sha(text.encode()))
        elif receipt.get("status") == "model_error":
            res.update(status="model_error", error_type=receipt.get("error_type"))
        elif receipt.get("status") == "incomplete":
            res.update(status="incomplete", reason=receipt.get("reason"))
        else:
            res.update(status="unmeasured_infra", reason=receipt.get("error_kind") or receipt.get("reason")
                       or f"no collected completion (submission_status={row.get('submission_status')})")
        out[rid] = res
    entry.update(harvested_at=e43.stamp(), charges_usd=round(charges, 6),
                 status_counts={s: sum(1 for r in out.values() if r["status"] == s) for s in {r["status"] for r in out.values()}})
    state = load_state()
    state["runs"][run_key] = entry
    save_state(state)
    log(f"{run_key}: harvested {entry['status_counts']} charges ${charges:.4f}")
    return out


class ValkyrieTransport:
    """run_batch(requests) -> {req_id: result}; result['status'] in measured | model_error | incomplete | unmeasured_infra."""

    def __init__(self, concurrency: int = 30):
        self.concurrency = concurrency

    def run_batch(self, batch: str, reqs: list[Request]) -> dict[str, dict]:
        results: dict[str, dict] = {}
        todo = []
        for r in reqs:
            rec = load_req(r.req_id)
            if rec and rec.get("final"):
                results[r.req_id] = rec["final"]                # already has a verdict or a labelled failure: never re-admitted
            else:
                todo.append(r)
        if not todo:
            return results
        for attempt in ("main", "recovery_1"):
            if not todo:
                break
            for r in todo:
                write_task(r)
                assert round_trip(r), f"{r.req_id}: task file does not round-trip"
            ensure_live()
            start_service()                                    # reload the pack; no run is in flight between batches
            groups: dict[str, list[Request]] = {}
            for r in todo:
                groups.setdefault(_group_key(r), []).append(r)
            keys = []
            for gi, (_, grp) in enumerate(sorted(groups.items())):
                key = f"{batch}__g{gi}__{attempt}"
                state = load_state()
                if key not in state["runs"]:
                    admit(key, grp, self.concurrency)
                keys.append(key)
            wait_runs(keys)
            got: dict[str, dict] = {}
            for key in keys:
                got.update(harvest(key))
            retry = []
            for r in todo:
                res = got.get(r.req_id, {"status": "unmeasured_infra", "reason": "not in any harvested run"})
                res["attempt"] = attempt
                if res["status"] in NO_VERDICT and attempt == "main":
                    retry.append(r)
                    rec = load_req(r.req_id)
                    rec.setdefault("attempts", []).append({k: v for k, v in res.items() if k != "text"})
                    save_req(rec)
                    continue
                rec = load_req(r.req_id)
                rec["final"] = res
                save_req(rec)
                results[r.req_id] = res
            todo = retry
        return results


class FakeTransport:
    """Offline stand-in: `responder(req) -> text or None` (None = an infrastructure failure)."""

    def __init__(self, responder):
        self.responder = responder
        self.calls: list[Request] = []

    def run_batch(self, batch: str, reqs: list[Request]) -> dict[str, dict]:
        out = {}
        for r in reqs:
            self.calls.append(r)
            text = self.responder(r)
            out[r.req_id] = ({"status": "measured", "text": text, "cost_usd": 0.0, "attempt": "main"} if text is not None
                             else {"status": "unmeasured_infra", "reason": "fake failure", "cost_usd": 0.0, "attempt": "main"})
        return out


def charges_total() -> dict:
    state = load_state()
    by_role: dict[str, float] = {}
    for entry in state["runs"].values():
        by_role[entry.get("role", "?")] = by_role.get(entry.get("role", "?"), 0.0) + (entry.get("charges_usd") or 0.0)
    return {"total_usd": round(sum(by_role.values()), 4), "by_role_usd": {k: round(v, 4) for k, v in by_role.items()},
            "n_runs": len(state["runs"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["deploy", "status", "verify-bundle", "charges"])
    args = ap.parse_args()
    if args.cmd == "deploy":
        print(json.dumps(deploy(), indent=1))
        return 0
    if args.cmd == "status":
        return status()
    if args.cmd == "verify-bundle":
        return verify_bundle()
    print(json.dumps(charges_total(), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
