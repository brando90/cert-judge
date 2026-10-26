#!/usr/bin/env python3
"""TLDR: Check that every shipped rebuilt prompt (private/prompts/<exp>/<prompt>.jsonl.gz) hashes to its frozen
prompt_sha256 and to the committed results/cells hash of experiment 39 or 42, and that the file sha256s equal the ones
recorded by rebuild_prompts.py (results/REBUILD_REPORT.json). Zero model calls; exits 1 on any difference.

Usage: verify_prompts.py"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e58                                                    # noqa: E402


def main() -> int:
    report = e58.read_json(e58.RESULTS / "REBUILD_REPORT.json")
    bad, n = 0, 0
    for exp, folder, cfg in (("e39", e58.E39_DIR, "gem31h"), ("e42", e58.E42_DIR, "qwen36")):
        for p in e58.PROMPT_ORDER:
            path = e58.prompts_path(exp, p)
            if e58.sha_file(path) != report["exps"][exp]["prompts"][p]["prompts_file_sha256"]:
                print(f"DIFF file sha256: {exp} {p}")
                bad += 1
            committed = {c["cell"]: c for c in e58.read_json(folder / f"results/cells/{cfg}__{p}.json")["cells"]}
            for r in e58.read_jsonl(path):
                n += 1
                if r["status"] != "render":
                    continue
                if e58.prompt_sha(r["system"], r["user"]) != r["prompt_sha256"] or committed[r["cell"]].get("prompt_sha256") != r["prompt_sha256"]:
                    print(f"DIFF prompt hash: {exp} {p} {r['cell']}")
                    bad += 1
    print(f"verified {n} prompt rows, {bad} differences")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
