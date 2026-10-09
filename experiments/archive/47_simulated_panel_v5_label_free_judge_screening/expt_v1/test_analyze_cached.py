#!/usr/bin/env python3
"""Deterministic provenance tests for the zero-call v5 target reconstruction."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE = Path(__file__).with_name("analyze_cached.py")
SPEC = importlib.util.spec_from_file_location("e47_analyze_cached", MODULE)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class RecoveryPrecedenceTest(unittest.TestCase):
    def setUp(self):
        self.cell = "s2__qwen38max__P1__item__r1"
        self.declared = {self.cell: {"cell": self.cell, "item": "item", "frame": "P1", "repeat": 1,
                                     "prompt_sha256": "p", "model": "qwen38max"}}

    def row(self, category, source="S2_qwen38max", score=None):
        r = {"cell": self.cell, "item": "item", "frame": "P1", "repeat": 1, "prompt_sha256": "p",
             "prompt_sha256_delivered": "p", "category": category, "run_key": source}
        if score is not None:
            r["score_0_5_parser_v2"] = score
        return r

    def test_recovery_replaces_only_unmeasured_original(self):
        rows = [("S2_qwen38max", self.row("MISSING")),
                ("S2_qwen38max_rec1a", self.row("COMPLETE", "S2_qwen38max_rec1a", 4))]
        got, audit = M.resolve_receipts(rows, self.declared)
        self.assertEqual(got[self.cell]["category"], "COMPLETE")
        self.assertEqual(got[self.cell]["_declared_model"], "qwen38max")
        self.assertEqual(len(audit["accepted_recoveries"]), 1)

    def test_recovery_never_replaces_original_parse_error(self):
        rows = [("S2_qwen38max", self.row("PARSE_ERROR")),
                ("S2_qwen38max_rec1a", self.row("COMPLETE", "S2_qwen38max_rec1a", 4))]
        got, audit = M.resolve_receipts(rows, self.declared)
        self.assertEqual(got[self.cell]["category"], "PARSE_ERROR")
        self.assertEqual(len(audit["ignored_recoveries"]), 1)

    def test_recovery_model_is_declared_not_run_key_derived(self):
        rows = [("S2_qwen38max", self.row("MISSING")),
                ("S2_qwen38max_rec1a", self.row("COMPLETE", "S2_qwen38max_rec1a", 4))]
        got, _ = M.resolve_receipts(rows, self.declared)
        slots = M.complete_first(got)
        self.assertIn(("item", "P1", "qwen38max"), slots)
        self.assertNotIn(("item", "P1", "qwen38max_rec1a"), slots)


if __name__ == "__main__":
    unittest.main()
