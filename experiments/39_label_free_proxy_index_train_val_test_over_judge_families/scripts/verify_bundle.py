#!/usr/bin/env python3
"""TLDR: PROTOCOL.md section 5's bundle check — download the published `vb103_judge` agent Valkyrie will run and
prove byte for byte that it is the bundle experiment 103 validated (its local files and its deployment receipt).
Download only: experiment 39 never pushes this agent. Zero model calls."""
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

sys.path[:0] = [str(Path(__file__).resolve().parents[3] / "py_src")]
from cert_judge import valkyrie_hosted as VH                   # noqa: E402

LOCAL_BUNDLE = e39.X103 / "scripts/valkyrie_judge_agent"
BUNDLE_RECEIPT = e39.X103 / "results/agent_bundle_judge.json"


# Hosted Valkyrie (10-14-2026): the CLI reads only `valkyrie login` / VALKYRIE_API_KEY / VALKYRIE_URL; the former
# private valkyrie.yaml, VALKYRIE_CONFIG_PATH and VALKYRIE_ENV=bench are ignored and no longer set.
VALK = VH.resolve_cli(e39.VALK, "E39_VALK")


def cli(args: list[str], timeout: int = 900) -> subprocess.CompletedProcess:
    return VH.cli(VALK, args, timeout=timeout)


def tree(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): e39.sha_file(p) for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=e39.RESULTS / "agent_bundle_check.json")
    args = ap.parse_args()
    os.umask(0o077)
    into = e39.PRIVATE / "agent_download_judge"
    if into.exists():
        shutil.rmtree(into)
    into.mkdir(parents=True)
    preflight = VH.require(VH.preflight(VALK, e39.PRIVATE / "valkyrie_preflight.log"))
    result = cli(["agent", "download", e39.AGENT, "-o", str(into)])
    (e39.PRIVATE / "agent_download.log").write_text(result.stdout + result.stderr)
    if result.returncode:
        raise SystemExit(f"download of {e39.AGENT} failed: {(result.stderr or '')[-600:]}")
    downloaded = tree(into / e39.AGENT)
    local = tree(LOCAL_BUNDLE)
    validated = e39.read_json(BUNDLE_RECEIPT)
    receipt = {"written_utc": e39.stamp(), "condition": "expt39-judge-bundle-check", "agent": e39.AGENT,
               "route": VH.ROUTE,
               "valkyrie_preflight": {k: preflight[k] for k in ("organization", "credential", "default_provider")}, "pushed_by": "experiment 103; experiment 39 downloads only",
               "experiment_103_receipt": str(BUNDLE_RECEIPT), "experiment_103_receipt_sha256": e39.sha_file(BUNDLE_RECEIPT),
               "experiment_103_validated_sha256": validated["downloaded_files_sha256"], "experiment_103_local_files_sha256": local,
               "downloaded_now_sha256": downloaded,
               "identical_to_experiment_103_validated_bundle": downloaded == validated["downloaded_files_sha256"],
               "identical_to_experiment_103_local_files": downloaded == local, "inference_calls": 0}
    receipt["verdict"] = "PASS" if (receipt["identical_to_experiment_103_validated_bundle"] and receipt["identical_to_experiment_103_local_files"]) else "FAIL"
    e39.write_json(args.out, receipt)
    print(json.dumps({k: receipt[k] for k in ("verdict", "agent", "identical_to_experiment_103_validated_bundle",
                                              "identical_to_experiment_103_local_files")}, indent=1))
    return 0 if receipt["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
