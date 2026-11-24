#!/usr/bin/env python3
"""Unit tests for canonical proper scoring rules, agreement diagnostics, LORO ceiling, and leakage guards."""
import math
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import metrics as M  # noqa: E402


class TestProperScoringMetrics(unittest.TestCase):
    def test_rps_decomposition_matches_individual_definition(self):
        rng = np.random.default_rng(7)
        for _ in range(25):
            q = rng.dirichlet(np.ones(6))
            ratings = rng.integers(0, 6, size=int(rng.integers(1, 8))).tolist()
            rps_direct = M.rps_item(q, ratings)
            rps_d, dist_err, disag = M.rps_decomp(q, ratings)
            self.assertAlmostEqual(rps_direct, rps_d, places=12)
            self.assertAlmostEqual(rps_direct, dist_err + disag, places=12)
            self.assertGreaterEqual(rps_direct, 0.0)
            self.assertLessEqual(rps_direct, 1.0)

    def test_perfect_forecast_on_mixed_ratings(self):
        # Empirical ratings [2, 4] -> p_hat = [0, 0, 0.5, 0, 0.5, 0]
        q = np.array([0.0, 0.0, 0.5, 0.0, 0.5, 0.0])
        ratings = [2, 4]
        self.assertAlmostEqual(M.tvd_item(q, ratings), 0.0, places=12)
        rps_val, dist_err, disag = M.rps_decomp(q, ratings)
        self.assertAlmostEqual(dist_err, 0.0, places=12)
        # F = [0, 0, 0.5, 0.5, 1, 1] -> F*(1-F) nonzero at k=2,3 (two of 5 bins -> 2 * 0.25 / 5 = 0.1)
        self.assertAlmostEqual(disag, 0.1, places=12)
        self.assertAlmostEqual(rps_val, 0.1, places=12)

    def test_tvd_uses_empirical_distribution_not_one_hot_average(self):
        q = np.array([0.0, 0.0, 0.5, 0.0, 0.5, 0.0])
        ratings = [2, 4]
        # Against empirical distribution TVD is 0.0; averaging one-hot TVDs would erroneously give 0.5.
        self.assertAlmostEqual(M.tvd_item(q, ratings), 0.0, places=12)

    def test_shifted_bias_judge_breaks_icc_a1_and_proper_losses_despite_spearman_one(self):
        # Human ratings: 0, 1, 2, 3, 4; Judge A = exact; Judge B = lenient +1 (clipped at 5 -> use 0..4 humans, +1 judge)
        humans = [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]]
        q_exact = np.eye(6)[[0, 1, 2, 3, 4]]
        q_lenient = np.eye(6)[[1, 2, 3, 4, 5]]
        ev_a = M.evaluate_forecast_panel(q_exact, humans)
        ev_b = M.evaluate_forecast_panel(q_lenient, humans)
        self.assertAlmostEqual(ev_a["spearman"], 1.0, places=12)
        self.assertAlmostEqual(ev_b["spearman"], 1.0, places=12)
        self.assertAlmostEqual(ev_a["icc_c1"], 1.0, places=12)
        self.assertAlmostEqual(ev_b["icc_c1"], 1.0, places=12)
        self.assertAlmostEqual(ev_a["bias_05"], 0.0, places=12)
        # Unsmoothed exact vs +1 scalar bias check
        sum_a = M.scalar_agreement_summary(np.array([0, 1, 2, 3, 4], float), np.array([0, 1, 2, 3, 4], float))
        sum_b = M.scalar_agreement_summary(np.array([1, 2, 3, 4, 5], float), np.array([0, 1, 2, 3, 4], float))
        self.assertAlmostEqual(sum_a["icc_a1"], 1.0, places=12)
        self.assertAlmostEqual(sum_b["icc_c1"], 1.0, places=12)
        self.assertLess(sum_b["icc_a1"], 0.90)
        self.assertAlmostEqual(sum_b["bias_05"], 1.0, places=12)
        self.assertGreater(ev_b["rps"], ev_a["rps"])
        self.assertGreater(ev_b["tvd"], ev_a["tvd"])
        self.assertGreater(ev_b["ce"], ev_a["ce"])

    def test_equal_artifact_weighting_ignores_rater_count_differences(self):
        # Artifact 0 has 1 rating (error = 0), Artifact 1 has 9 identical ratings (error > 0)
        q = np.array([
            [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ])
        ratings = [[0], [5] * 9]
        res = M.evaluate_forecast_panel(q, ratings)
        # RPS([1,0,0,0,0,0], [0]) = 0; RPS([1,0,0,0,0,0], [5]) = 1 -> mean must be 0.5, NOT 0.9
        self.assertAlmostEqual(res["rps"], 0.5, places=12)
        self.assertAlmostEqual(res["tvd"], 0.5, places=12)

    def test_icc_matches_shrout_fleiss_reference(self):
        # Classic 6x2 numerical check
        x = np.array([9.0, 2.0, 5.0, 8.0, 4.0, 6.0])
        y = np.array([6.0, 1.0, 3.0, 7.0, 4.0, 7.0])
        d = np.column_stack([x, y])
        n, k = d.shape
        gm = d.mean()
        msr = k * np.sum((d.mean(1) - gm) ** 2) / (n - 1)
        msc = n * np.sum((d.mean(0) - gm) ** 2) / (k - 1)
        mse = np.sum((d - d.mean(1, keepdims=True) - d.mean(0, keepdims=True) + gm) ** 2) / ((n - 1) * (k - 1))
        expected_c = (msr - mse) / (msr + mse)
        expected_a = (msr - mse) / (msr + mse + 2.0 * (msc - mse) / n)
        self.assertAlmostEqual(M.icc_two_way(x, y, "C"), expected_c, places=12)
        self.assertAlmostEqual(M.icc_two_way(x, y, "A"), expected_a, places=12)
        both_a, both_c = M.icc_two_way_both(x, y)
        self.assertAlmostEqual(both_a, expected_a, places=12)
        self.assertAlmostEqual(both_c, expected_c, places=12)
        both_shift_a, both_shift_c = M.icc_two_way_both(x, x + 2.5)
        self.assertAlmostEqual(both_shift_c, 1.0, places=12)
        self.assertLess(both_shift_a, 0.90)

    def test_loro_ceiling_returns_expected_perfect_agreement_values(self):
        # If 3 raters all agree perfectly on every item, empirical LORO RPS/TVD/Brier/MAE must all be 0
        ratings = [[0, 0, 0], [3, 3, 3], [5, 5, 5], [2, 2, 2]]
        loro = M.leave_one_rater_out_ceiling(ratings, task_ids=["t0", "t1", "t2", "t3"], alpha=0.5, draws=200)
        self.assertEqual(loro["n_items"], 4)
        self.assertAlmostEqual(loro["empirical"]["rps"], 0.0, places=12)
        self.assertAlmostEqual(loro["empirical"]["tvd"], 0.0, places=12)
        self.assertAlmostEqual(loro["empirical"]["brier"], 0.0, places=12)
        self.assertAlmostEqual(loro["empirical"]["mae_05"], 0.0, places=12)
        self.assertAlmostEqual(loro["loro_single_draw_spearman_mean"], 1.0, places=12)

    def test_calibration_fitters_are_valid_distributions_and_respect_monotonicity(self):
        scores = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ratings = [[0, 1], [1, 1], [2, 2], [3, 3], [4, 4], [5, 5]]
        for fitter in (lambda s, r: M.fit_const(r), M.fit_ce_ordinal, M.fit_pearson_gauss):
            pred = fitter(scores, ratings)
            probs = pred(scores)
            self.assertEqual(probs.shape, (6, 6))
            self.assertTrue(np.allclose(probs.sum(axis=1), 1.0, atol=1e-9))
            self.assertTrue(np.all(probs > 0.0))
        ce_pred = M.fit_ce_ordinal(scores, ratings)
        evs = ce_pred(scores) @ M.CATEGORIES
        self.assertGreater(evs[-1], evs[0] + 2.0)

    def test_signflip_permutation_p_exact_for_small_g(self):
        tasks = [f"t{i}" for i in range(6)]
        # All 6 differences positive -> 1 of 64 assignments has |mean| >= |obs| on positive side + 1 on negative = 2/64
        res = M.paired_task_signflip_p(tasks, [0.1] * 6, [0.5] * 6)
        self.assertEqual(res["method"], "exact_task_signflip_2^6")
        self.assertAlmostEqual(res["p_val"], 2.0 / 64.0, places=12)

    def test_vectorized_meta_association_exact_and_within_family(self):
        # Monotone increasing of length 8 -> exact 1/8! positive, 2/8! two-sided
        x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
        y = [10.0, 12.0, 12.0, 15.0, 20.0, 21.0, 25.0, 30.0]
        m8 = M.meta_association(x, y, draws=500, seed=1)
        self.assertEqual(m8["perm_method"], "exact_8!")
        self.assertAlmostEqual(m8["perm_p_one_sided_pos"], 2.0 / 40320.0, places=12)  # 2 tied values at index 1,2
        # Verify MC vectorized rank dot-product agrees with direct spearman_corr for n=10
        x10 = [float(i) for i in range(10)]
        y10 = [0.0, 0.0, 1.0, 2.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        fams = ["A"] * 5 + ["B"] * 5
        m10 = M.meta_association(x10, y10, families=fams, draws=1000, seed=42, boot_draws=250)
        self.assertEqual(m10["perm_method"], "mc_perm")
        self.assertEqual(m10["boot_draws"], 250)
        self.assertEqual(m10["perm_draws"], 1000)
        self.assertLess(m10["perm_p_two_sided"], 0.01)
        # Constant x within strata -> within-family permutation cannot alter correlation within strata when y is constant within strata
        y_const_strata = [1.0] * 5 + [9.0] * 5
        m_strat = M.meta_association(x10, y_const_strata, families=fams, draws=100, seed=42)
        self.assertAlmostEqual(m_strat["within_family_perm_p_two_sided"], 1.0, places=12)

    def test_fast_spearman_matches_scipy_with_ties(self):
        from scipy import stats
        rng = np.random.default_rng(123)
        for _ in range(20):
            x = rng.integers(0, 6, size=35).astype(float)
            y = rng.integers(0, 6, size=35).astype(float)
            if np.ptp(x) > 0 and np.ptp(y) > 0:
                self.assertAlmostEqual(M.spearman_corr(x, y), float(stats.spearmanr(x, y).statistic), places=12)
                self.assertAlmostEqual(M.pearson_corr(x, y), float(stats.pearsonr(x, y).statistic), places=12)


if __name__ == "__main__":
    unittest.main()
