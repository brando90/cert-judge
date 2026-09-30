#!/usr/bin/env python3
"""TLDR: PROTOCOL.md's agent-harness check — download the first Terminus2 bundle of the pre-registered candidate
list that exists in the account, record its contract (kwargs it accepts, secrets it maps, run command) and file
hashes, and write results/agent_harness.json for the controller; the smoke gate then proves it can judge. Download
only: experiment 39 never pushes an agent. Zero model calls."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e39                                                    # noqa: E402

import yaml                                                   # noqa: E402

# Kwargs we would like to set if the bundle's contract exposes them (values fixed here, before any call).
WANTED_KWARGS = {"max_turns": "20", "reasoning_effort": "high"}


def env() -> dict[str, str]:
    out = dict(os.environ)
    for key in ("VALKYRIE_API_KEY", "TRACKER_SERVICE_URL", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
                "GOOGLE_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_AUTH_TOKEN", "PYTHONPATH", "PYTHONHOME"):
        out.pop(key, None)
    out.update(VALKYRIE_ENV="bench", VALKYRIE_CONFIG_PATH=str(e39.PRIVATE / "valkyrie.yaml"))
    return out


def cli(args: list[str], timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run([str(e39.VALK)] + args, env=env(), stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)


def tree(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): e39.sha_file(p) for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default=",".join(e39.AGENT_HARNESS_CANDIDATES))
    ap.add_argument("--out", type=Path, default=e39.RESULTS / "agent_harness.json")
    args = ap.parse_args()
    os.umask(0o077)
    attempts = []
    chosen = None
    for name in [c for c in args.candidates.split(",") if c]:
        into = e39.PRIVATE / "agent_download_harness" / name
        if into.exists():
            shutil.rmtree(into)
        into.mkdir(parents=True)
        result = cli(["agent", "download", name, "-o", str(into)])
        (e39.PRIVATE / f"agent_download_{name}.log").write_text(result.stdout + result.stderr)
        contract_path = next(iter((into / name).glob("contract.y*ml")), None) or next(iter(into.rglob("contract.y*ml")), None)
        attempt = {"agent": name, "download_rc": result.returncode, "contract_found": contract_path is not None}
        attempts.append(attempt)
        if result.returncode or contract_path is None:
            continue
        contract = yaml.safe_load(contract_path.read_text()) or {}
        supported = sorted((contract.get("kwargs") or {}).keys())
        secrets = contract.get("secrets") or {}
        chosen = {"agent": name, "contract_name": contract.get("name"), "run_cmd": contract.get("run_cmd"),
                  "supported_kwargs": supported, "kwargs": {k: v for k, v in WANTED_KWARGS.items() if k in supported},
                  "contract_secrets": {k: str(v) for k, v in secrets.items()},
                  # If the contract already maps the gateway secret, the CLI must not map it again; otherwise the
                  # run passes `-s MODEL_GATEWAY_API_KEY <secret name>` (the only funded route).
                  "secret_env": None if any(e39.GATEWAY_SECRET in str(v) for v in secrets.values()) else "MODEL_GATEWAY_API_KEY",
                  "egress_allowlist": contract.get("egress_allowlist"),
                  "bundle_sha256": tree(contract_path.parent), "contract_sha256": e39.sha_file(contract_path)}
        attempt.update(chosen=True)
        break
    receipt = {"written_utc": e39.stamp(), "condition": "expt39-agent-harness-check", "candidates": args.candidates.split(","),
               "attempts": attempts, "route": "Valkyrie (VALKYRIE_ENV=bench)", "pushed_by": "not experiment 39 (download only)",
               "inference_calls": 0, "verdict": "PASS" if chosen else "FAIL", **(chosen or {})}
    e39.write_json(args.out, receipt)
    print(json.dumps({k: receipt.get(k) for k in ("verdict", "agent", "supported_kwargs", "kwargs", "secret_env", "attempts")}, indent=1))
    return 0 if chosen else 1


if __name__ == "__main__":
    raise SystemExit(main())
