#!/usr/bin/env python3
"""Synthetic self-test of the rating-pool gate. No files with human ratings are read."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LIB = ROOT / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families/scripts/analysis_lib.py"
FREEZE = ROOT / "experiments/ideas/cj_human_rating_pool_prospective_screen/freeze/FREEZE_10-18-2026.json"
SPEC = importlib.util.spec_from_file_location("e39_analysis", LIB)
assert SPEC and SPEC.loader
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)

DRAWS = 10_000
SEED = 48


def gate(row: dict) -> str:
    """Proposal O1, 10-14-2026: three conditions, otherwise FAIL. Missing Spearman is not a pass."""
    spearman, p_value, interval = row.get("spearman"), row.get("permutation_p"), row.get("ci") or {}
    if spearman is None:
        return "NOT_COMPUTABLE"
    lower = interval.get("lo")
    if spearman >= 0.45 and p_value is not None and p_value < 0.05 and lower is not None and lower > 0.20:
        return "PASS"
    return "FAIL"


def unit(name: str, index: float, criterion: float) -> dict:
    return {
        "config": name,
        "indices": {"C_ms_gold": index},
        "criteria": {"pool": {"spearman": criterion}},
    }


class SyntheticGateTest(unittest.TestCase):
    def test_pinned_analysis_library_is_unchanged(self):
        pinned = json.loads(FREEZE.read_text())["analysis_lib_sha256"]
        digest = hashlib.sha256(LIB.read_bytes()).hexdigest()
        self.assertEqual(digest, pinned)

    def test_monotone_deletion_ladder_scores_high_and_constant_scores_zero(self):
        falling = A.ladder_quality([0, 1, 2, 3, 4], [1.0, 0.8, 0.6, 0.4, 0.2])
        rising = A.ladder_quality([0, 1, 2, 3, 4], [0.2, 0.4, 0.6, 0.8, 1.0])
        constant = A.ladder_quality([0, 1, 2, 3, 4], [0.5, 0.5, 0.5, 0.5, 0.5])
        self.assertGreater(falling, 0.9)
        self.assertLess(rising, 0.1)
        self.assertEqual(constant, 0.0)

    def test_eight_aligned_units_pass_and_reversed_units_fail(self):
        aligned = [unit(f"j{i}", 0.2 + 0.1 * i, 0.2 + 0.1 * i) for i in range(8)]
        passed = A.association(aligned, "C_ms_gold", "pool", draws=DRAWS, seed=SEED)
        self.assertEqual(gate(passed), "PASS")
        self.assertEqual(passed["n_units"], 8)
        self.assertAlmostEqual(passed["spearman"], 1.0)
        reversed_units = [unit(f"j{i}", 0.2 + 0.1 * i, 0.9 - 0.1 * i) for i in range(8)]
        failed = A.association(reversed_units, "C_ms_gold", "pool", draws=DRAWS, seed=SEED)
        self.assertEqual(gate(failed), "FAIL")
        self.assertAlmostEqual(failed["spearman"], -1.0)

    def test_seven_units_are_not_computable(self):
        short = [unit(f"j{i}", 0.2 + 0.1 * i, 0.2 + 0.1 * i) for i in range(7)]
        row = A.association(short, "C_ms_gold", "pool", draws=DRAWS, seed=SEED)
        self.assertEqual(row["n_units"], 7)
        self.assertEqual(gate(row), "NOT_COMPUTABLE")

    def test_components_read_a_synthetic_monotone_ladder(self):
        cells = []
        for task in ("t1", "t2"):
            cells.append({"kind": "ident", "key": task, "level": 0, "score": 1.0, "status": "measured"})
            for level in (1, 2, 3, 4):
                cells.append({"kind": "ms_gold", "key": task, "level": level, "score": 1.0 - 0.2 * level, "status": "measured"})
        harvest = {"config": "synthetic|H2", "split": "synthetic", "family": "synthetic", "kind": "llm", "cells": cells}
        probes = {
            "ident": [{"key": "t1", "kind": "ident", "level": 0}, {"key": "t2", "kind": "ident", "level": 0}],
            "ms_gold": [{"key": task, "kind": "ms_gold", "level": level} for task in ("t1", "t2") for level in (1, 2, 3, 4)],
        }
        value = A.components(A.Scores(harvest), probes)["ms_gold"]["value"]
        self.assertGreater(value, 0.9)


if __name__ == "__main__":
    unittest.main()
