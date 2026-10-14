#!/usr/bin/env python3
"""TLDR: (Vendored from experiment 39's scripts/verify_bundle.py at origin/e39-proxy-index-search 9823689, adapted to experiment 42.) PROTOCOL.md section 5's bundle check — download the published `vb103_judge` agent Valkyrie will run and
prove byte for byte that it is the bundle experiment 103 validated (its local files and its deployment receipt).
Download only: experiment 42 never pushes this agent. Zero model calls."""
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

LOCAL_BUNDLE = e42.X103 / "scripts/valkyrie_judge_agent"
BUNDLE_RECEIPT = e42.X103 / "results/agent_bundle_judge.json"


# Hosted Valkyrie (10-14-2026): the CLI reads only `valkyrie login` / VALKYRIE_API_KEY / VALKYRIE_URL; the former
# private valkyrie.yaml, VALKYRIE_CONFIG_PATH and VALKYRIE_ENV=bench are ignored and no longer set.
VALK = VH.resolve_cli(e42.VALK, "E42_VALK")


def cli(args: list[str], timeout: int = 900) -> subprocess.CompletedProcess:
    return VH.cli(VALK, args, timeout=timeout)


def tree(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): e42.sha_file(p) for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=e42.RESULTS / "agent_bundle_check.json")
    args = ap.parse_args()
    os.umask(0o077)
    into = e42.PRIVATE / "agent_download_judge"
    if into.exists():
        shutil.rmtree(into)
    into.mkdir(parents=True)
    preflight = VH.require(VH.preflight(VALK, e42.PRIVATE / "valkyrie_preflight.log"))
    result = cli(["agent", "download", e42.AGENT, "-o", str(into)])
    (e42.PRIVATE / "agent_download.log").write_text(result.stdout + result.stderr)
    if result.returncode:
        raise SystemExit(f"download of {e42.AGENT} failed: {(result.stderr or '')[-600:]}")
    downloaded = tree(into / e42.AGENT)
    local = tree(LOCAL_BUNDLE)
    validated = e42.read_json(BUNDLE_RECEIPT)
    receipt = {"written_utc": e42.stamp(), "condition": "expt42-judge-bundle-check", "agent": e42.AGENT,
               "route": VH.ROUTE,
               "valkyrie_preflight": {k: preflight[k] for k in ("organization", "credential", "default_provider")}, "pushed_by": "experiment 103; experiment 42 downloads only",
               "experiment_103_receipt": str(BUNDLE_RECEIPT), "experiment_103_receipt_sha256": e42.sha_file(BUNDLE_RECEIPT),
               "experiment_103_validated_sha256": validated["downloaded_files_sha256"], "experiment_103_local_files_sha256": local,
               "downloaded_now_sha256": downloaded,
               "identical_to_experiment_103_validated_bundle": downloaded == validated["downloaded_files_sha256"],
               "identical_to_experiment_103_local_files": downloaded == local, "inference_calls": 0}
    # The hosted move renames the gateway secret in the bundle's contract.yaml (no slash allowed in tenant secret names);
    # that one edit is accepted only if restoring the old name reproduces experiment 103's validated contract hash.
    contract = into / e42.AGENT / "contract.yaml"
    receipt["identical_except_gateway_secret_rename"] = VH.matches_validated_except_secret_rename(
        downloaded, validated["downloaded_files_sha256"], contract.read_bytes() if contract.is_file() else b"")
    receipt["verdict"] = "PASS" if ((receipt["identical_to_experiment_103_validated_bundle"] or receipt["identical_except_gateway_secret_rename"])
                                    and receipt["identical_to_experiment_103_local_files"]) else "FAIL"
    e42.write_json(args.out, receipt)
    print(json.dumps({k: receipt[k] for k in ("verdict", "agent", "identical_to_experiment_103_validated_bundle",
                                              "identical_to_experiment_103_local_files")}, indent=1))
    return 0 if receipt["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
