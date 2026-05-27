from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
RUNNER_PATH = EXPERIMENT_DIR / "run_mathlib_style_bench.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("mathlib_style_bench_runner", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load runner from {RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class MathlibStyleBenchRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner()

    def test_heuristic_smoke_scores_good_above_bad(self):
        pairs = self.runner.load_pairs(EXPERIMENT_DIR / "data" / "sample_pairs.jsonl")
        records = self.runner.score_pairs_with_heuristic(
            pairs=pairs,
            repeats=1,
            judge_id="test_heuristic",
        )
        pair_rows, summary = self.runner.aggregate_metrics(
            pairs=pairs,
            records=records,
            min_margin=0.05,
            margin_target=0.25,
            stability_tau=0.05,
        )

        self.assertEqual(summary["n_scored_pairs"], 3)
        self.assertEqual(summary["style_order_score_mean"], 1.0)
        self.assertGreater(summary["mathlib_style_bench_mvp_score"], 0.9)
        for row in pair_rows:
            self.assertGreaterEqual(row["score_margin_good_minus_bad"], 0.05)
            self.assertTrue(row["pass_at_min_margin"])

    def test_report_sorts_pair_margins_worst_to_best(self):
        pairs = self.runner.load_pairs(EXPERIMENT_DIR / "data" / "sample_pairs.jsonl")
        records = self.runner.score_pairs_with_heuristic(
            pairs=pairs,
            repeats=1,
            judge_id="test_heuristic",
        )
        pair_rows, summary = self.runner.aggregate_metrics(
            pairs=pairs,
            records=records,
            min_margin=0.05,
            margin_target=0.25,
            stability_tau=0.05,
        )

        with tempfile.TemporaryDirectory() as td:
            report_path = Path(td) / "REPORT.md"
            self.runner.write_report(report_path, pair_rows, summary)
            report = report_path.read_text(encoding="utf-8")

        self.assertLess(report.index("`list_length_map`"), report.index("`nat_add_comm`"))
        self.assertLess(report.index("`nat_add_comm`"), report.index("`nat_zero_add`"))

    def test_load_external_raw_scores_csv(self):
        pairs = self.runner.load_pairs(EXPERIMENT_DIR / "data" / "sample_pairs.jsonl")[:1]
        with tempfile.TemporaryDirectory() as td:
            scores_path = Path(td) / "scores.csv"
            with scores_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "pair_id",
                        "variant",
                        "raw_score",
                        "max_score",
                        "judge_id",
                        "repeat_idx",
                        "source",
                    ],
                )
                writer.writeheader()
                writer.writerow({
                    "pair_id": pairs[0].pair_id,
                    "variant": "bad",
                    "raw_score": "8",
                    "max_score": "30",
                    "judge_id": "external",
                    "repeat_idx": "0",
                    "source": "unit_test",
                })
                writer.writerow({
                    "pair_id": pairs[0].pair_id,
                    "variant": "good",
                    "raw_score": "27",
                    "max_score": "30",
                    "judge_id": "external",
                    "repeat_idx": "0",
                    "source": "unit_test",
                })

            records = self.runner.load_scores_csv(scores_path, "fallback", 1.0)
            pair_rows, summary = self.runner.aggregate_metrics(
                pairs=pairs,
                records=records,
                min_margin=0.05,
                margin_target=0.25,
                stability_tau=0.05,
            )

        self.assertEqual(len(records), 2)
        self.assertEqual(pair_rows[0]["style_order_score"], 1.0)
        self.assertAlmostEqual(summary["mean_margin_good_minus_bad"], 19 / 30)

    def test_unknown_external_pair_id_is_rejected(self):
        pairs = self.runner.load_pairs(EXPERIMENT_DIR / "data" / "sample_pairs.jsonl")[:1]
        records = [
            self.runner.ScoreRecord(
                pair_id=pairs[0].pair_id,
                variant="bad",
                score=0.2,
                judge_id="external",
                repeat_idx=0,
                source="unit_test",
            ),
            self.runner.ScoreRecord(
                pair_id="not_in_manifest",
                variant="good",
                score=0.9,
                judge_id="external",
                repeat_idx=0,
                source="unit_test",
            ),
        ]

        with self.assertRaisesRegex(ValueError, "unknown pair_id"):
            self.runner.aggregate_metrics(
                pairs=pairs,
                records=records,
                min_margin=0.05,
                margin_target=0.25,
                stability_tau=0.05,
            )

    def test_nonpositive_margin_target_is_rejected(self):
        pairs = self.runner.load_pairs(EXPERIMENT_DIR / "data" / "sample_pairs.jsonl")[:1]
        records = self.runner.score_pairs_with_heuristic(
            pairs=pairs,
            repeats=1,
            judge_id="test_heuristic",
        )

        with self.assertRaisesRegex(ValueError, "margin_target"):
            self.runner.aggregate_metrics(
                pairs=pairs,
                records=records,
                min_margin=0.05,
                margin_target=0.0,
                stability_tau=0.05,
            )


if __name__ == "__main__":
    unittest.main()
