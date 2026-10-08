from __future__ import annotations

import math
import importlib.util
from itertools import product
from pathlib import Path
import unittest

from cert_judge.information_properties import (
    deletion_tvd_task,
    complete_repeat_candidates,
    gold_deletion_monotonicity,
    repeat_tvd_task,
    score_bin,
    semantic_auc_task,
    semantic_acceptance_gaps,
    total_variation,
)


ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "e46_analysis_test", ROOT / "experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation/scripts/analyze_information_properties.py"
)
assert _SPEC and _SPEC.loader
ANALYSIS = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ANALYSIS)


class InformationPropertiesTest(unittest.TestCase):
    def test_total_variation_hand_computed_and_bin_coarsening(self):
        self.assertAlmostEqual(total_variation({0: 0.75, 1: 0.25}, {0: 0.25, 1: 0.75}), 0.5)
        fine = total_variation({0: .25, 1: .25, 2: .25, 3: .25}, {0: .5, 1: 0, 2: .5, 3: 0})
        coarse = total_variation({0: .5, 1: .5}, {0: .5, 1: .5})
        self.assertGreaterEqual(fine, coarse)
        self.assertEqual(score_bin(1.0), 4)

    def test_semantic_ties_and_bidirectional_formatting(self):
        self.assertEqual(semantic_auc_task([.1], [.1]), 0.0)
        self.assertEqual(semantic_auc_task([.2], [.1, .3]), 0.0)
        gaps = semantic_acceptance_gaps([.2, .01], [.2, .05], [0, .01, .05])
        self.assertAlmostEqual(gaps[0.0], 0.0)
        self.assertAlmostEqual(gaps[0.01], -0.5)

    def test_repeat_independent_task_and_invertible_bin_relabeling(self):
        # A task-level repeat pattern shared by every candidate has no candidate
        # dependence, so the per-repeat joint equals its product distribution.
        independent = {"a": {1: .1, 2: .9, 3: .1}, "b": {1: .1, 2: .9, 3: .1}}
        self.assertAlmostEqual(repeat_tvd_task(independent), 0.0)
        dependent = {"a": {1: .1, 2: .1, 3: .1}, "b": {1: .9, 2: .9, 3: .9}}
        original = repeat_tvd_task(dependent)
        inverted = repeat_tvd_task({c: {r: 1 - v for r, v in reps.items()} for c, reps in dependent.items()})
        self.assertEqual(original, 0.5)
        self.assertEqual(inverted, 0.5)

    def test_repeat_candidate_id_counterexample_and_failures(self):
        candidate_id = {"a": {1: .1, 2: .1, 3: .1}, "b": {1: .9, 2: .9, 3: .9}}
        self.assertEqual(repeat_tvd_task(candidate_id), 0.5)
        reversed_candidate_id = {candidate: {repeat: 1 - score for repeat, score in repeats.items()} for candidate, repeats in candidate_id.items()}
        self.assertEqual(repeat_tvd_task(reversed_candidate_id), 0.5)
        constant = {"a": {1: .1, 2: .1, 3: .1}, "b": {1: .1, 2: .1, 3: .1}}
        self.assertEqual(repeat_tvd_task(constant), 0.0)
        cube = {str(bits): {repeat: value for repeat, value in enumerate(bits, start=1)} for bits in product((.1, .9), repeat=3)}
        self.assertEqual(repeat_tvd_task(cube), 0.0)
        with self.assertRaises(ValueError):
            repeat_tvd_task({"a": {1: .1, 2: .1}, "b": {1: .9, 2: .9}})
        with self.assertRaises(ValueError):
            repeat_tvd_task({"a": {1: .1, 2: .1, 3: .1}})

    def test_repeat_split_uses_two_complete_candidates_and_reports_excluded(self):
        cells = {
            ("crit", "a", 0): {1: .1, 2: .1, 3: .1},
            ("crit", "b", 0): {1: .9, 2: .9, 3: .9},
            ("crit", "c", 0): {1: .5, 2: .5},
        }
        items = [{"item": item, "task": "task", "split": "train"} for item in ("a", "b", "c")]
        result, detail = ANALYSIS.repeat_for_split(cells, items, "train")
        self.assertEqual(result["declared_tasks"], 1)
        self.assertEqual(result["observed_tasks"], 1)
        self.assertEqual(result["value"], 0.5)
        self.assertEqual(detail[0]["complete_candidate_count"], 2)
        self.assertEqual(detail[0]["excluded_candidates"], ["c"])
        complete, excluded = complete_repeat_candidates({"a": cells[("crit", "a", 0)], "c": cells[("crit", "c", 0)]})
        self.assertEqual(set(complete), {"a"})
        self.assertEqual(excluded, ["c"])

    def test_analysis_rejects_duplicate_cells_and_enforces_coverage_rules(self):
        duplicate = {"config": "fixture", "cells": [
            {"cell": "one", "kind": "crit", "key": "a", "level": 0, "repeat": 1, "status": "measured", "score": .2},
            {"cell": "two", "kind": "crit", "key": "a", "level": 0, "repeat": 1, "status": "measured", "score": .3},
        ]}
        with self.assertRaises(ValueError):
            ANALYSIS.accepted_cells(duplicate)
        declarations = {"task": {"strict": [{"kind": "weakening", "level": 1}], "formatting": [{"kind": "formatting", "level": 1}]}}
        semantic, _ = ANALYSIS.semantic_for_split({("ident", "task", 1): {1: .8, 2: .8}, ("weakening", "task", 1): {1: .4, 2: .4}}, declarations, {"task"})
        self.assertEqual(semantic["status"], "NOT_COMPUTABLE_COVERAGE")
        repeat, _ = ANALYSIS.repeat_for_split({("crit", "a", 0): {1: .1, 2: .1, 3: .1}, ("crit", "b", 0): {1: .2, 2: .2}}, [{"item": "a", "task": "task", "split": "train"}, {"item": "b", "task": "task", "split": "train"}], "train")
        self.assertEqual(repeat["status"], "NOT_COMPUTABLE_COVERAGE")
        deletion, _ = ANALYSIS.deletion_for_split({("ident", "task", 0): {1: .8, 2: .8}, ("ms_gold", "task", 1): {1: .4}}, {"ms_gold": [{"task": "task", "level": 1}]}, {"task"})
        self.assertEqual(deletion["status"], "NOT_COMPUTABLE_COVERAGE")

    def test_task_cluster_bootstrap_handles_unequal_task_file_counts(self):
        matrix = ANALYSIS.np.array([[.1, .4, .8], [.2, .5, .7]])
        human = ANALYSIS.np.array([.2, .4, .9])
        groups = [ANALYSIS.np.array([0]), ANALYSIS.np.array([1, 2])]
        draws = ANALYSIS.np.array([[0, 0], [0, 1], [1, 1]])
        actual = ANALYSIS.task_cluster_bootstrap_metrics(matrix, human, draws, groups)
        expected = []
        for draw in draws:
            indices = ANALYSIS.np.concatenate([groups[group] for group in draw])
            expected.append(ANALYSIS.per_config_bootstrap_metrics(matrix, human, indices[None, :])[0])
        self.assertTrue(ANALYSIS.np.allclose(actual, ANALYSIS.np.stack(expected), equal_nan=True))

    def test_deletion_correct_reversed_constant_and_identity_control(self):
        correct = deletion_tvd_task({0: [.9, .9], 1: [.5, .5], 2: [.1, .1]})
        reversed_ladder = deletion_tvd_task({0: [.1, .1], 1: [.5, .5], 2: [.9, .9]})
        constant = deletion_tvd_task({0: [.5, .5], 1: [.5, .5], 2: [.5, .5]})
        self.assertAlmostEqual(correct["orientation"], 1.0)
        self.assertGreater(correct["value"], 0.0)
        self.assertAlmostEqual(reversed_ladder["information"], correct["information"])
        self.assertLess(reversed_ladder["orientation"], 0.0)
        self.assertEqual(reversed_ladder["value"], 0.0)
        self.assertEqual(constant["value"], 0.0)
        self.assertAlmostEqual(gold_deletion_monotonicity({0: .9, 1: .5, 2: .1}), 1.0)
        self.assertAlmostEqual(gold_deletion_monotonicity({0: .1, 1: .5, 2: .9}), 0.0)
        self.assertEqual(gold_deletion_monotonicity({0: .5, 1: .5}), 0.0)


if __name__ == "__main__":
    unittest.main()
