#!/usr/bin/env python3
"""TLDR: (Vendored from experiment 39's scripts/deploy_service.py at origin/e39-proxy-index-search 9823689, adapted to
experiment 42's paths, benchmark names certjudge42-<key> and ports 9460-9468.) Serve one judge-model pack of experiment 42 through experiment 103's collect-only, Lean-less benchmark
service (run read-only) on its own port behind a cloudflared tunnel, verify health 200 / unauthenticated 401,
and register it as benchmark `certjudge42-<model>` in experiment 42's own private Valkyrie config. Adapted from
experiment 105's deploy_service.py. Zero model calls; nothing of experiments 103/105 is written."""
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e42                                                    # noqa: E402

import yaml                                                   # noqa: E402

SERVICE_DIR = e42.X103 / "scripts/vb_service_single_call"
VENV = Path(os.environ.get("E42_VENV", "/lfs/skampere1/0/brando9/vb103_venv"))
CLOUDFLARED = Path(os.environ.get("E42_CLOUDFLARED", "/lfs/skampere1/0/brando9/vb-e2-service-20260916/bin/cloudflared"))
KERNEL_AXIOMS = e42.VB_REPO / "scripts/scsc/kernel_axioms.py"
VALKYRIE_SOURCE = Path(os.environ.get("E42_VALKYRIE_SOURCE", str(Path.home() / ".config/valkyrie/valkyrie.yaml")))
# Sandbox base image for the AGENT-judge services only. The service's default (a bare Ubuntu 24.04 digest) has no system
# python3; its Lean-less `verify` phase requires one, which the vb103_judge bundle's setup happens to install (apt) before
# that phase runs, while the Terminus2 bundle's setup installs uv + a private CPython venv only, so every agent-judge
# sandbox failed provisioning with `python3 missing` (09-30-2026 smoke). A digest-pinned public image that ships python3
# (and no Lean) satisfies the same phase; the single-call services keep the service default. Recorded in the receipt.
# Experiment 39's recorded image (results/deployment_t2_*.json), reused unchanged.
AGENT_BASE_IMAGE = os.environ.get("E42_AGENT_BASE_IMAGE", "python@sha256:1aaa65a85fda306ffb8b910824d4e93bdce61e212c7e87168123ea3073b41a1a")
# Ports: e42.BASE_PORT (9460-9468); experiment 39 uses 8990-8998, 43 uses 9431, 103 uses 8923-8962.
MODEL_KEYS = list(e42.MODELS)


def port_of(model_key: str) -> int:
    return e42.port_of(model_key)


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


def report_status(model_key: str) -> int:
    receipt = e42.PRIVATE / f"deployment_{model_key}.json"
    if not receipt.exists():
        print(json.dumps({"deployed": False, "model_key": model_key}))
        return 1
    state = e42.read_json(receipt)
    bearer = (e42.PRIVATE / "service_bearer").read_text().strip()
    state.update(checked_utc=e42.stamp(), service_alive=alive(state.get("service_pid")), tunnel_alive=alive(state.get("tunnel_pid")),
                 local_health_now=probe(f"http://127.0.0.1:{state['port']}/health", bearer),
                 tunnel_health_now=probe(state["tunnel_url"] + "/health", bearer))
    print(json.dumps({k: v for k, v in state.items() if k != "tunnel_url"}, indent=2))
    return 0 if state["service_alive"] and state["tunnel_alive"] else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=MODEL_KEYS)
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()
    if args.status:
        return report_status(args.model)
    # Valkyrie accepts hyphen-only benchmark names (experiment 103: "every deployed benchmark uses hyphens only");
    # the agent-judge keys carry an underscore, so it is folded to a hyphen here and nowhere else.
    benchmark = e42.benchmark_of(args.model)
    port = port_of(args.model)
    pack = e42.PRIVATE / "packs" / args.model

    os.umask(0o077)
    e42.PRIVATE.mkdir(mode=0o700, exist_ok=True)
    os.chmod(e42.PRIVATE, 0o700)
    receipt_path = e42.PRIVATE / f"deployment_{args.model}.json"
    if receipt_path.exists():
        old = e42.read_json(receipt_path)
        if alive(old.get("service_pid")) and alive(old.get("tunnel_pid")):
            raise SystemExit(f"a live deployment for {args.model} is already recorded; use --status. A redeploy changes the "
                             "tunnel URL and would orphan a running Valkyrie run.")
    if not pack.is_dir():
        raise SystemExit(f"pack missing: {pack} (run scripts/pack.py)")
    if not SERVICE_DIR.is_dir():
        raise SystemExit(f"experiment 103 service code missing: {SERVICE_DIR}")
    if not KERNEL_AXIOMS.is_file():
        raise SystemExit(f"kernel axiom checker missing: {KERNEL_AXIOMS}")

    bearer_path = e42.PRIVATE / "service_bearer"
    if not bearer_path.exists():
        bearer_path.write_text(secrets.token_urlsafe(36))
    os.chmod(bearer_path, 0o600)
    bearer = bearer_path.read_text().strip()

    env = dict(os.environ)
    for key in ("AUTH_DISABLED", "PYTHONPATH", "PYTHONHOME", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
                "GOOGLE_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN"):
        env.pop(key, None)
    agent_flavor = e42.MODELS[args.model]["harness"] != "vb103_judge"
    if agent_flavor:
        if not AGENT_BASE_IMAGE:
            raise SystemExit("E42_AGENT_BASE_IMAGE (digest-pinned public image with python3) is required for an agent-judge service")
        env["VB_BASE_IMAGE"] = AGENT_BASE_IMAGE
    env.update(VB_SERVICE_KEY_FILE=str(bearer_path), VB_TASK_PACK=str(pack), VB_CONTROL_PACK="1", VB_NO_COMPILER="1",
               VB_COLLECT_ONLY="1", VB_LAKE_DIR=str(e42.LAKE_DIR), VB_KERNEL_AXIOMS=str(KERNEL_AXIOMS),
               VB_GRADE_SCRATCH=str(e42.PRIVATE / "grade_scratch"), VB_GRADE_NETNS="off", VB_IC_PP="offline",
               VB_AGENT_TIMEOUT_S="3600", VB_SETUP_TIMEOUT_S="900", VB_RESOURCES_VCPU="2", VB_RESOURCES_MEMORY="4",
               VB_RESOURCES_DISK="20")

    log = open(e42.PRIVATE / f"service_{args.model}.log", "ab", buffering=0)
    service = subprocess.Popen([str(VENV / "bin/uvicorn"), "main:app", "--host", "127.0.0.1", "--port", str(port)],
                               cwd=str(SERVICE_DIR), env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    (e42.PRIVATE / f"service_{args.model}.pid").write_text(str(service.pid))
    for _ in range(90):
        if probe(f"http://127.0.0.1:{port}/health", bearer) == 200:
            break
        if service.poll() is not None:
            raise SystemExit(f"service exited during startup; see private/service_{args.model}.log")
        time.sleep(2)
    else:
        raise SystemExit("local service health timed out")
    if probe(f"http://127.0.0.1:{port}/health", None) != 401:
        raise SystemExit("local service answered an unauthenticated probe; refusing to expose it")

    tunnel_log = e42.PRIVATE / f"tunnel_{args.model}.log"
    tunnel_log.write_bytes(b"")
    cloud = open(tunnel_log, "ab", buffering=0)
    tunnel = subprocess.Popen([str(CLOUDFLARED), "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{port}"],
                              stdin=subprocess.DEVNULL, stdout=cloud, stderr=cloud, start_new_session=True)
    (e42.PRIVATE / f"tunnel_{args.model}.pid").write_text(str(tunnel.pid))
    for _ in range(90):
        found = re.findall(r"https://[a-z0-9-]+\.trycloudflare\.com", tunnel_log.read_text())
        if found:
            url = found[-1]
            break
        time.sleep(2)
    else:
        raise SystemExit("tunnel hostname timed out")
    for _ in range(45):
        if probe(url + "/health", bearer) == 200:
            break
        time.sleep(2)
    else:
        raise SystemExit("tunnel health timed out")
    unauth = probe(url + "/health", None)
    if unauth != 401:
        raise SystemExit(f"tunnel answered an unauthenticated probe with {unauth}; refusing")

    target = e42.PRIVATE / "valkyrie.yaml"
    cfg = yaml.safe_load((target if target.exists() else VALKYRIE_SOURCE).read_text())
    cfg.setdefault("custom_benchmark_services", {})[benchmark] = url
    cfg.setdefault("benchmark_auth", {})[benchmark] = "Bearer " + bearer
    target.write_text(yaml.safe_dump(cfg))
    os.chmod(target, 0o600)

    receipt = {"deployed_utc": e42.stamp(), "model_key": args.model, "benchmark": benchmark, "service_pid": service.pid,
               "tunnel_pid": tunnel.pid, "port": port, "tunnel_url": url, "local_health": 200, "local_unauthenticated_health": 401,
               "tunnel_health": 200, "tunnel_unauthenticated_health": unauth, "service_dir": str(SERVICE_DIR),
               "service_code": "experiment 103 vb_service_single_call, run read-only with experiment 42's env",
               "service_files_sha256": {p.name: e42.sha_file(p) for p in sorted(SERVICE_DIR.glob("*.py"))},
               "pack_dir": str(pack), "pack_task_count": len([p for p in pack.iterdir() if p.is_dir()]),
               "control_pack": True, "grade_mode": "collect_only", "sandbox_lean": "none", "valkyrie_config": str(target),
               "base_image": env.get("VB_BASE_IMAGE", "service default (ubuntu 24.04 digest)"), "harness": e42.MODELS[args.model]["harness"],
               "inference_calls": 0}
    tmp = receipt_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(receipt, indent=2) + "\n")
    tmp.replace(receipt_path)
    public = {k: v for k, v in receipt.items() if k != "tunnel_url"}
    public["tunnel_url"] = "recorded in private/deployment_<model>.json (not published)"
    e42.write_json(e42.RESULTS / f"deployment_{args.model}.json", public)
    print(json.dumps(public, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
