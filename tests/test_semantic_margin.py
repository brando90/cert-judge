from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("e50_margin", ROOT / "experiments/50_semantic_effect_margin_cached_judge_selection_train_val_test/scripts/analyze_semantic_margin.py")
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(M)

class SemanticMarginTest(unittest.TestCase):
    def test_hand_computed_margin_and_equal_task_weights(self):
        declaration = {"a": {"strict": [{"kind":"w", "level":1}], "formatting":[{"kind":"f", "level":1}]}, "b": {"strict":[{"kind":"w", "level":1}], "formatting":[{"kind":"f", "level":1}]}}
        cells = {("ident","a",1): {1:.9,2:.9}, ("w","a",1): {1:.4,2:.4}, ("f","a",1): {1:.8,2:.8}, ("ident","b",1): {1:.5,2:.5}, ("w","b",1): {1:.4,2:.4}, ("f","b",1): {1:.1,2:.1}}
        result, rows = M.margin_for_split(cells, declaration, {"a","b"})
        self.assertAlmostEqual(rows[0]["semantic_margin"], .4); self.assertAlmostEqual(rows[1]["semantic_margin"], -.3); self.assertAlmostEqual(result["value"], .05)
    def test_constant_reverse_format_and_fail_closed_coverage(self):
        declaration = {"a": {"strict": [{"kind":"w", "level":1}], "formatting":[{"kind":"f", "level":1}]}}
        cells = {("ident","a",1): {1:.5,2:.5}, ("w","a",1): {1:.5,2:.5}, ("f","a",1): {1:.8,2:.8}}
        result, rows = M.margin_for_split(cells, declaration, {"a"}); self.assertAlmostEqual(result["value"], -.3)
        bad = dict(cells); bad[("f","a",1)] = {1:.8}
        result, rows = M.margin_for_split(bad, declaration, {"a"}); self.assertEqual(result["status"], "NOT_COMPUTABLE_COVERAGE")
    def test_ties_and_restricted_tie_selector(self):
        self.assertEqual(M.maximum_weights(["a","b"], {"a": .2, "b": .2 + 5e-13, "outside": 1.}), {"a": .5, "b": .5})
    def test_exaggerated_margin_is_not_correctness(self):
        declaration = {"a": {"strict": [{"kind":"w", "level":1}], "formatting":[{"kind":"f", "level":1}]}}
        cells = {("ident","a",1): {1:1.,2:1.}, ("w","a",1): {1:0.,2:0.}, ("f","a",1): {1:1.,2:1.}}
        result, _ = M.margin_for_split(cells, declaration, {"a"}); self.assertEqual(result["value"], 1.0)
        # A large response difference is an effect-size property, not a human-correctness label.
        self.assertNotIn("correct", result)

if __name__ == "__main__": unittest.main()
