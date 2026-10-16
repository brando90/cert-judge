from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("e50_margin", ROOT / "experiments/archive/50_semantic_effect_margin_cached_judge_selection_train_val_test/scripts/analyze_semantic_margin.py")
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(M)

class SemanticMarginTest(unittest.TestCase):
    def test_hand_computed_margin_and_equal_task_weights(self):
        declaration = {"a": {"strict": [{"kind":"w", "level":1}], "formatting":[{"kind":"f", "level":1}]}, "b": {"strict":[{"kind":"w", "level":1}], "formatting":[{"kind":"f", "level":1}]}}
        cells = {("ident","a",1): {1:.9,2:.9}, ("w","a",1): {1:.4,2:.4}, ("f","a",1): {1:.8,2:.8}, ("ident","b",1): {1:.5,2:.5}, ("w","b",1): {1:.4,2:.4}, ("f","b",1): {1:.1,2:.1}}
        result, rows = M.margin_for_split(cells, declaration, {"a","b"})
        self.assertAlmostEqual(rows[0]["semantic_margin"], .4); self.assertAlmostEqual(rows[1]["semantic_margin"], -.3); self.assertAlmostEqual(result["value"], .05)
    def test_constant_reverse_and_bidirectional_formatting(self):
        declaration = {"a": {"strict": [{"kind":"w", "level":1}], "formatting":[{"kind":"f", "level":1}]}}
        cells = {("ident","a",1): {1:.5,2:.5}, ("w","a",1): {1:.5,2:.5}, ("f","a",1): {1:.8,2:.8}}
        result, _ = M.margin_for_split(cells, declaration, {"a"}); self.assertAlmostEqual(result["value"], -.3)
        constant = {("ident","a",1): {1:.5,2:.5}, ("w","a",1): {1:.5,2:.5}, ("f","a",1): {1:.5,2:.5}}
        result, _ = M.margin_for_split(constant, declaration, {"a"}); self.assertEqual(result["value"], 0.0)
        reverse = {("ident","a",1): {1:.1,2:.1}, ("w","a",1): {1:.9,2:.9}, ("f","a",1): {1:.1,2:.1}}
        result, _ = M.margin_for_split(reverse, declaration, {"a"}); self.assertAlmostEqual(result["value"], -.8)
        both = {"a": {"strict": [{"kind":"w", "level":1}], "formatting":[{"kind":"up", "level":1}, {"kind":"down", "level":1}]}}
        bidirectional = {("ident","a",1): {1:.5,2:.5}, ("w","a",1): {1:.2,2:.2}, ("up","a",1): {1:.7,2:.7}, ("down","a",1): {1:.3,2:.3}}
        result, _ = M.margin_for_split(bidirectional, both, {"a"}); self.assertAlmostEqual(result["value"], .1)

    def test_exact_probe_and_split_coverage_boundaries(self):
        strict = [{"kind":"w", "level":i} for i in range(5)]
        declaration = {f"t{i}": {"strict": strict, "formatting":[{"kind":"f", "level":1}]} for i in range(5)}
        cells = {}
        for task in declaration:
            cells[("ident",task,1)] = {1:.8,2:.8}; cells[("f",task,1)] = {1:.8,2:.8}
            for i in range(5): cells[("w",task,i)] = {1:.4,2:.4}
        result, rows = M.margin_for_split(cells, declaration, set(declaration)); self.assertEqual(result["observed_tasks"], 5); self.assertEqual(result["value"], .4)
        for i in (3, 4): cells.pop(("w","t4",i))
        result, rows = M.margin_for_split(cells, declaration, set(declaration)); self.assertEqual(result["observed_tasks"], 4); self.assertEqual(result["status"], "COMPUTED")
        for i in (3, 4): cells.pop(("w","t3",i))
        result, _ = M.margin_for_split(cells, declaration, set(declaration)); self.assertEqual(result["observed_tasks"], 3); self.assertEqual(result["status"], "NOT_COMPUTABLE_COVERAGE")
        empty, _ = M.margin_for_split({}, {}, set()); self.assertEqual(empty["status"], "NOT_COMPUTABLE_COVERAGE")

    def test_unequal_strict_counts_equal_task_weights_and_fail_closed_parsing(self):
        declaration = {"a": {"strict": [{"kind":"wa", "level":1}], "formatting":[{"kind":"f", "level":1}]}, "b": {"strict":[{"kind":"wb", "level":i} for i in range(4)], "formatting":[{"kind":"f", "level":1}]}}
        cells = {("ident","a",1): {1:.9,2:.9}, ("wa","a",1): {1:.4,2:.4}, ("f","a",1): {1:.9,2:.9}, ("ident","b",1): {1:.9,2:.9}, ("f","b",1): {1:.9,2:.9}}
        for i in range(4): cells[("wb","b",i)] = {1:.8,2:.8}
        result, _ = M.margin_for_split(cells, declaration, {"a","b"}); self.assertAlmostEqual(result["value"], .3)
        duplicate = {"config":"fixture", "cells":[{"cell":"x","kind":"crit","key":"x","level":0,"repeat":1,"status":"measured","score":.2},{"cell":"y","kind":"crit","key":"x","level":0,"repeat":1,"status":"measured","score":.3}]}
        invalid = {"config":"fixture", "cells":[{"cell":"x","kind":"crit","key":"x","level":0,"repeat":1,"status":"measured","score":1.1}]}
        with self.assertRaises(ValueError): M.E46A.accepted_cells(duplicate)
        with self.assertRaises(ValueError): M.E46A.accepted_cells(invalid)
    def test_ties_and_restricted_tie_selector(self):
        self.assertEqual(M.maximum_weights(["a","b"], {"a": .2, "b": .2 + 5e-13, "outside": 1.}), {"a": .5, "b": .5})

    def test_archived_manifest_path_resolution(self):
        old = "experiments/50_semantic_effect_margin_cached_judge_selection_train_val_test/PROTOCOL.md"
        self.assertEqual(M.resolve_manifest_path(old), ROOT / "experiments/archive/50_semantic_effect_margin_cached_judge_selection_train_val_test/PROTOCOL.md")
    def test_exaggerated_margin_is_wrong_against_humans(self):
        declaration = {"a": {"strict": [{"kind":"w", "level":1}], "formatting":[{"kind":"f", "level":1}]}}
        cells = {("ident","a",1): {1:1.,2:1.}, ("w","a",1): {1:0.,2:0.}, ("f","a",1): {1:1.,2:1.}}
        result, _ = M.margin_for_split(cells, declaration, {"a"}); self.assertEqual(result["value"], 1.0)
        # A high effect margin can coexist with perfectly reversed human ranking.
        self.assertLess(M.E46A.safe_corr(np.array([1., .9, .1, 0.]), np.array([0., .1, .9, 1.]))["spearman"], 0)

    def test_evaluate_split_adapter_end_to_end(self):
        configs = ["good", "bad", "constant"]
        items = [{"item": f"i{i}", "task": f"t{i//2}", "split":"test"} for i in range(4)]
        human = [.0, .3, .7, 1.]
        medians = {"good": dict(zip([x["item"] for x in items], human)), "bad": dict(zip([x["item"] for x in items], [1-x for x in human])), "constant": dict.fromkeys([x["item"] for x in items], .5)}
        repeats = {c: {x["item"]: [medians[c][x["item"]], medians[c][x["item"]]] for x in items} for c in configs}
        ratings = {x["item"]: {"current5_mean_0_to_1": human[i], "current3_mean_0_to_1": human[i]} for i, x in enumerate(items)}
        selectors = {"max_train_semantic_margin":{"good":.5,"bad":.5}, "fixed_H2":{"constant":1.0}}
        out = M.evaluate_split(configs, items, medians, repeats, ratings, selectors, draws=16, declared_files=4)
        primary = out["targets"]["current5_mean_0_to_1"]
        self.assertEqual(set(out["per_judge"]["current5_mean_0_to_1"]), set(configs))
        self.assertAlmostEqual(primary["selectors"]["max_train_semantic_margin"]["metrics"]["spearman"]["value"], 0.0)
        self.assertTrue(np.isnan(primary["selectors"]["fixed_H2"]["metrics"]["spearman"]["value"]))
        self.assertIsNotNone(primary["selectors"]["fixed_H2"]["metrics"]["mae"]["value"])
        self.assertIsNone(primary["margin_minus_every_comparator"]["fixed_H2"]["spearman"]["value"])
        self.assertIsNotNone(primary["margin_minus_every_comparator"]["fixed_H2"]["mae"]["value"])
        ensemble = np.mean([np.array(human), 1-np.array(human)], axis=0)
        self.assertIsNone(M.E46A.safe_corr(ensemble, np.array(human))["spearman"])

if __name__ == "__main__": unittest.main()
