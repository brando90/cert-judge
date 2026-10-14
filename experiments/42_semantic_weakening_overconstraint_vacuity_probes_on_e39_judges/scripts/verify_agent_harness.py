#!/usr/bin/env python3
"""TLDR: (Vendored from experiment 39's scripts/verify_agent_harness.py at origin/e39-proxy-index-search 9823689, adapted to experiment 42.) PROTOCOL.md's agent-harness check — download the first Terminus2 bundle of the pre-registered candidate
list that exists in the account, record its contract (kwargs it accepts, secrets it maps, run command) and file
hashes, and write results/agent_harness.json for the controller; the smoke gate then proves it can judge. Download
only: experiment 42 never pushes an agent. Zero model calls."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e42                                                    # noqa: E402

sys.path[:0] = [str(Path(__file__).resolve().parents[3] / "py_src")]
from cert_judge import valkyrie_hosted as VH                   # noqa: E402

import yaml                                                   # noqa: E402

# Kwargs we would like to set if the bundle's contract exposes them (values fixed here, before any call).
WANTED_KWARGS = {"max_turns": "20", "reasoning_effort": "high"}


# Hosted Valkyrie (10-14-2026): the CLI reads only `valkyrie login` / VALKYRIE_API_KEY / VALKYRIE_URL; the former
# private valkyrie.yaml, VALKYRIE_CONFIG_PATH and VALKYRIE_ENV=bench are ignored and no longer set.
VALK = VH.resolve_cli(e42.VALK, "E42_VALK")


def cli(args: list[str], timeout: int = 900) -> subprocess.CompletedProcess:
    return VH.cli(VALK, args, timeout=timeout)


def tree(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): e42.sha_file(p) for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default=",".join(e42.AGENT_HARNESS_CANDIDATES))
    ap.add_argument("--out", type=Path, default=e42.RESULTS / "agent_harness.json")
    args = ap.parse_args()
    os.umask(0o077)
    preflight = VH.require(VH.preflight(VALK, e42.PRIVATE / "valkyrie_preflight.log"))
    attempts = []
    chosen = None
    for name in [c for c in args.candidates.split(",") if c]:
        into = e42.PRIVATE / "agent_download_harness" / name
        if into.exists():
            shutil.rmtree(into)
        into.mkdir(parents=True)
        result = cli(["agent", "download", name, "-o", str(into)])
        (e42.PRIVATE / f"agent_download_{name}.log").write_text(result.stdout + result.stderr)
        contract_path = next(iter((into / name).glob("contract.y*ml")), None) or next(iter(into.rglob("contract.y*ml")), None)
        attempt = {"agent": name, "download_rc": result.returncode, "contract_found": contract_path is not None}
        attempts.append(attempt)
        if result.returncode or contract_path is None:
            continue
        contract = yaml.safe_load(contract_path.read_text()) or {}
        supported = sorted((contract.get("kwargs") or {}).keys())
        secrets = contract.get("secrets") or {}
        legacy = sorted(str(v) for v in secrets.values() if "/" in str(v))
        if legacy:
            # A slash-containing name was an AWS Secrets Manager path; hosted tenant secrets cannot contain a
            # slash, so this bundle cannot resolve its secrets until it is re-pushed with the new name.
            attempt.update(rejected=f"contract maps pre-hosted secret names {legacy}; re-push it mapping {VH.GATEWAY_SECRET}")
            continue
        chosen = {"agent": name, "contract_name": contract.get("name"), "run_cmd": contract.get("run_cmd"),
                  "supported_kwargs": supported, "kwargs": {k: v for k, v in WANTED_KWARGS.items() if k in supported},
                  "contract_secrets": {k: str(v) for k, v in secrets.items()},
                  # If the contract already maps the gateway secret, the CLI must not map it again; otherwise the
                  # run passes `-s MODEL_GATEWAY_API_KEY <secret name>` (the only funded route).
                  "secret_env": None if any(str(v) == VH.GATEWAY_SECRET for v in secrets.values()) else "MODEL_GATEWAY_API_KEY",
                  "gateway_secret": VH.GATEWAY_SECRET,
                  "egress_allowlist": contract.get("egress_allowlist"),
                  "bundle_sha256": tree(contract_path.parent), "contract_sha256": e42.sha_file(contract_path)}
        attempt.update(chosen=True)
        break
    receipt = {"written_utc": e42.stamp(), "condition": "expt42-agent-harness-check", "candidates": args.candidates.split(","),
               "attempts": attempts, "route": VH.ROUTE,
               "valkyrie_preflight": {k: preflight[k] for k in ("organization", "credential", "default_provider")},
               "pushed_by": "not experiment 42 (download only)",
               "inference_calls": 0, "verdict": "PASS" if chosen else "FAIL", **(chosen or {})}
    e42.write_json(args.out, receipt)
    print(json.dumps({k: receipt.get(k) for k in ("verdict", "agent", "supported_kwargs", "kwargs", "secret_env", "attempts")}, indent=1))
    return 0 if chosen else 1


if __name__ == "__main__":
    raise SystemExit(main())
