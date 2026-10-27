#!/usr/bin/env python3
"""TLDR: Experiment 61: render the open-weight judge prompts for experiment 43's saved start and final candidates (77 unique texts x D0, H2, P1); zero model calls.
Use on a host that has the VeriBench clone (skampere1: /lfs/skampere1/0/brando9/veribench_e43). Writes <out>/prompts61.jsonl.
Usage: render61.py --out DIR"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

E61 = Path(__file__).resolve().parents[1]
E43_SCRIPTS = E61.parent / "43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/scripts"
sys.path[:0] = [str(E43_SCRIPTS)]
import e43  # noqa: E402

CAND = E43_SCRIPTS.parent / "results/full/candidates"
PROMPTS = ("D0", "H2", "P1")
MODEL_KEY = "sonnet5m"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def unique_texts() -> dict[tuple[str, str], str]:
    out = {}
    for f in sorted((CAND / "starts").glob("*.lean")):
        t = f.read_text(encoding="utf-8")
        out[(f.stem, sha(t.encode()))] = t
    for f in sorted((CAND / "finals").glob("*.lean")):
        judge, prompt, item = f.stem.split("__", 2)
        t = f.read_text(encoding="utf-8")
        out.setdefault((item, sha(t.encode())), t)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    items = e43.items_by_id()
    rows, texts = [], unique_texts()
    for (item, tsha), text in sorted(texts.items()):
        for p in PROMPTS:
            cfg = f"{MODEL_KEY}|{p}"
            r = e43.render_judge(cfg, items[item], text)
            cell = f"{item}|{tsha[:16]}|{p}"
            if r[0] is None:
                rows.append({"cell": cell, "item": item, "text_sha256": tsha, "prompt": p,
                             "status": "deterministic" if r[1] is not None else "unmeasured", "score": r[1]})
            else:
                rows.append({"cell": cell, "item": item, "text_sha256": tsha, "prompt": p, "status": "render",
                             "system": r[0], "user": r[1], "prompt_sha256": sha((r[0] + "\n\x00\n" + r[1]).encode())})
    a.out.mkdir(parents=True, exist_ok=True)
    with open(a.out / "prompts61.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    from collections import Counter
    print(json.dumps({"texts": len(texts), "rows": len(rows), "status": Counter(r["status"] for r in rows),
                      "by_prompt": Counter((r["prompt"], r["status"]) for r in rows if r["status"] != "render").most_common()}, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
