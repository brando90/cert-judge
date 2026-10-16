#!/usr/bin/env python3
"""Regression-check every comparable experiment-46 selector/result cell."""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
E50 = Path(__file__).resolve().parents[1] / "results"
E46 = ROOT / "experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation/results"
TOL = 1e-12

def read(p): return json.loads(p.read_text())
def same(a, b):
    if a is None or b is None: return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)): return math.isclose(a, b, abs_tol=TOL, rel_tol=0)
    return a == b

def main():
    failures, checked = [], 0
    old_select, new_select = read(E46 / "selectors.json"), read(E50 / "selectors.json")
    for name, weights in old_select["weights"].items():
        checked += 1
        if new_select["weights"].get(name) != weights: failures.append(f"selector weights {name}")
    old_eval, new_eval = read(E46 / "selector_utility.json"), read(E50 / "evaluation.json")
    for split in ("val", "test"):
        old_split, new_split = old_eval["splits"][split], new_eval["splits"][split]
        for key in ("status", "declared_files", "common_files", "required_common_files"):
            checked += 1
            if old_split.get(key) != new_split.get(key): failures.append(f"{split} {key}")
        if old_split["status"] != "COMPUTED": continue
        for target, old_target in old_split["targets"].items():
            for selector, old_row in old_target["selectors"].items():
                for metric, old_cell in old_row["metrics"].items():
                    new_cell = new_split["targets"][target]["selectors"][selector]["metrics"][metric]
                    for key in ("value", "lo", "hi", "valid_draws", "undefined_draws"):
                        checked += 1
                        if not same(old_cell[key], new_cell[key]): failures.append(f"{split}/{target}/{selector}/{metric}/{key}")
    old_assoc, new_assoc = read(E46 / "association.json"), read(E50 / "association.json")
    for prop, old_row in old_assoc.items():
        for metric, old_cell in old_row["metrics"].items():
            new_cell = new_assoc[prop]["metrics"][metric]
            for key in ("value", "lo", "hi", "valid_draws", "undefined_draws"):
                checked += 1
                if not same(old_cell[key], new_cell[key]): failures.append(f"association/{prop}/{metric}/{key}")
    payload = {"status": "PASS" if not failures else "FAIL", "tolerance": TOL, "checked_cells": checked, "failures": failures,
               "scope": "Experiment-46 selectors, val/test selector metrics and intervals, and three archived associations; experiment-50 adds semantic_margin only."}
    (E50 / "baseline_reproduction.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload))
    if failures: raise SystemExit(1)

if __name__ == "__main__": main()
