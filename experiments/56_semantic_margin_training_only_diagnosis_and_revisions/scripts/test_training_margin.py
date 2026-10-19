from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("analyze_training_margin.py")
SPEC = importlib.util.spec_from_file_location("e56", SCRIPT)
M = importlib.util.module_from_spec(SPEC); assert SPEC and SPEC.loader; SPEC.loader.exec_module(M)
PROJ_SPEC = importlib.util.spec_from_file_location("e56_proj", Path(__file__).with_name("train_only_projection.py"))
P = importlib.util.module_from_spec(PROJ_SPEC); assert PROJ_SPEC and PROJ_SPEC.loader; PROJ_SPEC.loader.exec_module(P)


def cell(kind, key, level, repeat, score, *, task="t", status="measured"):
    return {"cell": f"{kind}-{key}-{level}-{repeat}", "kind": kind, "key": key, "task": task, "level": level, "repeat": repeat, "score": score, "status": status}


class TrainingMarginTest(unittest.TestCase):
    def test_duplicate_repeat_fails_closed(self):
        harvest = {"cells": [cell("ident", "t", 1, 1, .8), cell("ident", "t", 1, 1, .7)]}
        with self.assertRaises(ValueError): M.index_cells(harvest)

    def test_original_headroom_and_specificity_controls(self):
        cells = M.index_cells({"cells": [cell("ident", "t", 1, 1, .8), cell("ident", "t", 1, 2, .8), cell("weak", "t", 1, 1, .4), cell("weak", "t", 1, 2, .4), cell("fmt", "t", 1, 1, .7), cell("fmt", "t", 1, 2, .7), cell("weak", "t", 2, 1, .75), cell("weak", "t", 2, 2, .75)]})
        declarations = [{"task":"t","kind":"weak","level":1,"family":"weakening","valid":True,"audit_label":"strict"},{"task":"t","kind":"fmt","level":1,"family":"formatting","valid":True,"audit_label":None}]
        controls = [{"task":"t","kind":"weak","level":2}]
        detail = M.task_components(cells, declarations, controls, {"t"})[0]
        self.assertAlmostEqual(detail["original_S_minus_F"], .3); self.assertAlmostEqual(detail["headroom_normalized"], .375); self.assertAlmostEqual(detail["semantic_specificity"], .35)

    def test_zero_baseline_and_missing_support(self):
        cells = M.index_cells({"cells": [cell("ident", "t", 1, 1, 0), cell("ident", "t", 1, 2, 0), cell("weak", "t", 1, 1, 0), cell("weak", "t", 1, 2, 0), cell("fmt", "t", 1, 1, 0), cell("fmt", "t", 1, 2, 0)]})
        declarations = [{"task":"t","kind":"weak","level":1,"family":"weakening","valid":True,"audit_label":"strict"},{"task":"t","kind":"fmt","level":1,"family":"formatting","valid":True,"audit_label":None}]
        detail = M.task_components(cells, declarations, [], {"t"})[0]
        self.assertIsNone(detail["headroom_normalized"]); self.assertFalse(detail["specificity_observed"])

    def test_affine_scaling_changes_raw_margin_not_rank(self):
        raw = [.2, .7]; scaled = [2*x + 1 for x in raw]
        self.assertEqual(M.correlations(raw, [0, 1])["spearman"], M.correlations(scaled, [0, 1])["spearman"])
        self.assertNotEqual(raw, scaled)
        def raw_margin(identity, weakening, formatting):
            return (identity - weakening) - abs(identity - formatting)
        self.assertAlmostEqual(2 * raw_margin(.8, .4, .7), raw_margin(1.6, .8, 1.4))

    def test_split_sentinel_is_excluded(self):
        item_task, train_tasks = {"train-item": "train-task"}, {"train-task"}
        self.assertTrue(P.semantic_cell_allowed({"kind": "weak", "task": "train-task", "key": "train-task"}, item_task, train_tasks))
        self.assertFalse(P.semantic_cell_allowed({"kind": "weak", "task": "heldout-task", "key": "heldout-task"}, item_task, train_tasks))
        self.assertFalse(P.semantic_cell_allowed({"kind": "crit", "task": "heldout-task", "key": "SECRET"}, item_task, train_tasks))
        self.assertFalse(P.criterion_cell_allowed({"kind": "crit", "task": "train-task", "key": "SECRET", "level": 0}, item_task, train_tasks))
        self.assertFalse(P.criterion_cell_allowed({"kind": "ms_gold", "task": "heldout-task", "key": "heldout-task", "level": 1}, item_task, train_tasks))

    def test_constant_configuration_association_is_unavailable(self):
        row = M._assoc([.2, .2, .2], [.1, .4, .9])
        self.assertIsNone(row["spearman"])
        self.assertEqual(row["p_val"], "n/a")
        self.assertEqual(row["interval"], "unavailable")


if __name__ == "__main__": unittest.main()
