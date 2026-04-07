"""Tests for P8 (Evaluator Replicability) and P9 (Rubric Specification Robustness)."""

import numpy as np
import pytest

from cert_judge.mutual_evaluation import (
    P8Report,
    P9Report,
    compute_p8_evaluator_replicability,
    compute_p9_rubric_robustness,
    compute_me_factor,
    compute_jti_with_mutual_evaluation,
)
from cert_judge.hsj_scoring import compute_jti


# =====================================================================
# P8 tests
# =====================================================================

class TestP8EvaluatorReplicability:
    def test_perfect_agreement(self):
        """All judges give identical scores -> P8 = 1.0."""
        scores = [[0.1, 0.5, 0.9, 0.3]] * 3  # 3 judges, 4 items, identical
        report = compute_p8_evaluator_replicability(scores)
        assert report.p8 == pytest.approx(1.0, abs=1e-6)
        assert report.mean_pairwise_rho == pytest.approx(1.0, abs=1e-6)
        assert report.conclusion_stability == 1.0
        assert report.k_judges == 3
        assert report.n_items == 4

    def test_perfectly_anticorrelated(self):
        """Two judges with reversed rankings -> rho = -1, P8 = 0.0."""
        scores = [
            [0.1, 0.3, 0.5, 0.7, 0.9],
            [0.9, 0.7, 0.5, 0.3, 0.1],
        ]
        report = compute_p8_evaluator_replicability(scores)
        assert report.mean_pairwise_rho == pytest.approx(-1.0, abs=1e-6)
        assert report.p8 == pytest.approx(0.0, abs=1e-6)

    def test_partial_agreement(self):
        """Two judges with moderate agreement -> P8 in (0, 1)."""
        rng = np.random.default_rng(123)
        base = rng.uniform(0, 1, size=20)
        noisy = base + rng.normal(0, 0.2, size=20)
        noisy = np.clip(noisy, 0, 1)
        scores = [base.tolist(), noisy.tolist()]
        report = compute_p8_evaluator_replicability(scores)
        assert 0.0 < report.p8 < 1.0
        assert report.k_judges == 2
        assert report.n_items == 20
        assert len(report.pairwise_rhos) == 1  # C(2,2) = 1 pair

    def test_three_judges_pairwise_count(self):
        """3 judges -> C(3,2) = 3 pairwise correlations."""
        scores = [
            [0.1, 0.5, 0.9],
            [0.2, 0.6, 0.8],
            [0.15, 0.55, 0.85],
        ]
        report = compute_p8_evaluator_replicability(scores)
        assert len(report.pairwise_rhos) == 3

    def test_conclusion_stability_partial(self):
        """Some items agree, some don't."""
        # 3 buckets on [0,1]: [0, 0.33), [0.33, 0.67), [0.67, 1.0]
        scores = [
            [0.1, 0.5, 0.9],  # buckets: 0, 1, 2
            [0.2, 0.8, 0.95], # buckets: 0, 2, 2
        ]
        report = compute_p8_evaluator_replicability(scores, n_buckets=3)
        # Item 0: both bucket 0 (agree), Item 1: 1 vs 2 (disagree), Item 2: both 2 (agree)
        assert report.conclusion_stability == pytest.approx(2 / 3, abs=1e-6)

    def test_constant_identical_scores_are_perfect_agreement(self):
        """Identical constant scores should still count as perfect agreement."""
        scores = [
            [0.5, 0.5, 0.5],
            [0.5, 0.5, 0.5],
        ]
        report = compute_p8_evaluator_replicability(scores)
        assert report.mean_pairwise_rho == pytest.approx(1.0, abs=1e-6)
        assert report.p8 == pytest.approx(1.0, abs=1e-6)
        assert report.conclusion_stability == pytest.approx(1.0, abs=1e-6)

    def test_too_few_judges_raises(self):
        with pytest.raises(ValueError, match="at least 2 judges"):
            compute_p8_evaluator_replicability([[0.1, 0.5]])

    def test_too_few_items_raises(self):
        with pytest.raises(ValueError, match="at least 2 items"):
            compute_p8_evaluator_replicability([[0.5], [0.6]])


# =====================================================================
# P9 tests
# =====================================================================

class TestP9RubricRobustness:
    def test_structured_signal_high_p9(self):
        """Response matrix with clear item-specific structure -> high P9."""
        # Two distinct item types: items 0-9 answer [1,1,0,0], items 10-19 answer [0,0,1,1]
        mat = np.zeros((20, 4), dtype=int)
        mat[:10, :2] = 1
        mat[10:, 2:] = 1
        report = compute_p9_rubric_robustness(mat, n_permutations=50, seed=42)
        assert report.p9 > 0.5  # structured signal should score well
        assert report.welfare_raw > 0.0
        assert report.null_95th < report.welfare_raw
        assert report.n_items == 20
        assert report.n_questions == 4

    def test_random_noise_low_p9(self):
        """Purely random response matrix -> P9 near or below 1.0 (welfare ~ null)."""
        rng = np.random.default_rng(99)
        mat = rng.integers(0, 2, size=(20, 4))
        report = compute_p9_rubric_robustness(mat, n_permutations=50, seed=99)
        # Random data should not score much above the null
        assert report.p9 <= 1.0
        assert report.welfare_raw >= 0.0

    def test_too_few_items_raises(self):
        with pytest.raises(ValueError, match="at least 3 items"):
            compute_p9_rubric_robustness([[1, 0], [0, 1]])

    def test_too_few_questions_raises(self):
        with pytest.raises(ValueError, match="at least 1 coding question"):
            compute_p9_rubric_robustness([[], [], []])

    def test_report_fields(self):
        mat = np.eye(5, dtype=int)
        report = compute_p9_rubric_robustness(mat, n_permutations=20, seed=7)
        assert isinstance(report, P9Report)
        assert report.n_permutations == 20
        assert report.tau > 0


# =====================================================================
# ME factor and JTI integration tests
# =====================================================================

class TestMEFactor:
    def test_balanced(self):
        """Equal P8 and P9 with default alpha=0.5."""
        assert compute_me_factor(0.8, 0.6) == pytest.approx(0.7, abs=1e-6)

    def test_all_p8(self):
        """alpha=1.0 -> ME = P8."""
        assert compute_me_factor(0.8, 0.2, alpha=1.0) == pytest.approx(0.8, abs=1e-6)

    def test_all_p9(self):
        """alpha=0.0 -> ME = P9."""
        assert compute_me_factor(0.8, 0.2, alpha=0.0) == pytest.approx(0.2, abs=1e-6)

    def test_clipping(self):
        assert compute_me_factor(1.5, -0.1) == pytest.approx(0.5, abs=1e-6)


class TestJTIWithMutualEvaluation:
    def test_perfect_me_preserves_jti(self):
        """ME factor = 1.0 -> JTI' = JTI_base."""
        jti_base = 0.85
        jti_prime = compute_jti_with_mutual_evaluation(jti_base, p8=1.0, p9=1.0)
        assert jti_prime == pytest.approx(jti_base, abs=1e-6)

    def test_zero_me_kills_jti(self):
        """ME factor = 0.0 -> JTI' = 0.0."""
        jti_prime = compute_jti_with_mutual_evaluation(0.9, p8=0.0, p9=0.0)
        assert jti_prime == pytest.approx(0.0, abs=1e-6)

    def test_partial_discount(self):
        """ME factor = 0.5 -> JTI' = 0.5 * JTI_base."""
        jti_prime = compute_jti_with_mutual_evaluation(0.8, p8=0.5, p9=0.5)
        assert jti_prime == pytest.approx(0.4, abs=1e-6)

    def test_hierarchical_vs_additive(self):
        """JTI with P8/P9 additive vs. hierarchical multiplicative should differ."""
        p1, p2, p3, p4, p8, p9 = 0.9, 0.85, 0.8, 0.95, 0.6, 0.7
        jti_additive = compute_jti(p1, p2, p3, p4, p8=p8, p9=p9)
        jti_base = compute_jti(p1, p2, p3, p4)
        jti_hierarchical = compute_jti_with_mutual_evaluation(jti_base, p8, p9)
        # They should not be equal in general
        assert jti_additive != pytest.approx(jti_hierarchical, abs=1e-3)


class TestComputeJTIWithP8P9:
    def test_p8_p9_additive_in_jti(self):
        """compute_jti with p8/p9 produces equal-weighted average of 6 properties."""
        jti = compute_jti(0.9, 0.8, 0.7, 0.95, p8=0.6, p9=0.5)
        expected = (0.9 + 0.8 + 0.7 + 0.95 + 0.6 + 0.5) / 6
        assert jti == pytest.approx(expected, abs=1e-6)

    def test_backward_compatible_without_p8_p9(self):
        """compute_jti without p8/p9 still works as before."""
        jti = compute_jti(0.9, 0.8, 0.7, 0.6)
        expected = (0.9 + 0.8 + 0.7 + 0.6) / 4
        assert jti == pytest.approx(expected, abs=1e-6)
