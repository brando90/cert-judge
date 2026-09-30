#!/usr/bin/env python3
"""TLDR: (Vendored from experiment 39's scripts/local_controls.py, adapted to experiment 42's manifest.) Score every probe cell with the four deterministic non-LLM controls of experiment 39 (edit-distance
similarity, seeded random, theorem-count ratio, theorem-name Jaccard) and write them in the same harvest
format as the LLM configurations (results/harvest/ctl__<name>.json). Zero model calls."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parents[2] / "39_label_free_proxy_index_train_val_test_over_judge_families/scripts")]
import e42                                                    # noqa: E402
import probes as P                                            # noqa: E402  (experiment 39's widened theorem finder, read-only import)
import render_cells as RC                                     # noqa: E402

try:                                                          # cert-judge's pyproject pins python-Levenshtein
    import Levenshtein                                        # type: ignore
    _METHOD = "Levenshtein.ratio (normalized character edit similarity)"

    def similarity(a: str, b: str) -> float:
        return float(Levenshtein.ratio(a, b))
except Exception:                                             # noqa: BLE001
    _METHOD = "difflib.SequenceMatcher.ratio (fallback; not Levenshtein)"

    def similarity(a: str, b: str) -> float:
        return float(difflib.SequenceMatcher(None, a, b).ratio())


def random_score(config: str, gold: str, cand: str, seed: int = 42) -> float:
    """Experiment 16's `_det_random_score`: SHA-256 of judge id, seed and the first 200 chars of each side."""
    h = hashlib.sha256((config + str(seed) + gold[:200] + cand[:200]).encode("utf-8")).hexdigest()
    return int(h[:12], 16) / float(16 ** 12 - 1)


def score(control: str, gold: str, cand: str) -> float:
    if control == "ctl|editdist":
        return similarity(cand, gold) if cand else 0.0
    if control == "ctl|random":
        return random_score(control, gold, cand)
    if control == "ctl|count_ratio":
        n_ref, n_cand = len(P.statement_texts(gold)), len(P.statement_texts(cand))
        return 1.0 if n_ref == 0 else min(1.0, n_cand / n_ref)
    if control == "ctl|name_jaccard":
        a, b = set(P.theorem_names(cand)), set(P.theorem_names(gold))
        return 1.0 if not (a | b) else len(a & b) / len(a | b)
    raise KeyError(control)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=e42.RESULTS / "semantic_probe_manifest.json")
    ap.add_argument("--allow-unvalidated", action="store_true")
    args = ap.parse_args()
    items = e42.load_items()
    probe_rows = RC.load_probe_rows(e42.read_json(args.manifest), items, args.allow_unvalidated)
    golds = {it["task"]: Path(it["ref_ann_path_abs"]).read_text(encoding="utf-8", errors="replace") for it in items}
    for control, doc in e42.CONTROLS.items():
        cells = []
        for r in probe_rows:
            text = RC.probe_text(r)
            value = score(control, golds[r["task"]], text)
            for repeat in range(1, e42.REPEATS + 1):
                cells.append({"cell": RC.cell_id(r["kind"], r["key"], r["level"], repeat), "kind": r["kind"], "key": r["key"],
                              "task": r["task"], "item": r["item"], "level": r["level"], "repeat": repeat, "config": control,
                              "status": "deterministic", "score": value, "score_raw": value})
        out = {"written_utc": e42.stamp(), "config": control, "family": "control", "split": "train", "kind": "control",
               "rubric": control, "scale": 1, "selector": None, "kwargs": {}, "doc": doc,
               "method": _METHOD if control == "ctl|editdist" else doc, "n_cells": len(cells),
               "status_counts": {"deterministic": len(cells)}, "charges_usd": 0.0, "cells": cells}
        e42.write_json(e42.RESULTS / "harvest" / (control.replace("|", "__") + ".json"), out)
        print(json.dumps({control: len(cells)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
