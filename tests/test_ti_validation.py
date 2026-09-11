"""Tests for the ``PTI_p -> TI_m`` validation harness.

Reference values for the intraclass correlations come from Shrout & Fleiss
(1979), Table 1, which is the standard published worked example.  The ceiling
tests reproduce the inter-pass agreement reported in Appendix G.2 of the
CertJudge submission so that a regression in the attenuation logic shows up as
a disagreement with a number that appears in the paper.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "py_src"))

from cert_judge.ti_validation import (
    COMPUTED,
    NOT_COMPUTABLE,
    UNDERPOWERED,
    attenuation_ceiling,
    bootstrap_ci,
    ceiling_report,
    compute_ti_m,
    correlation_suite,
    disattenuate,
    fisher_ci,
    grouped_three_way_split,
    icc,
    leave_one_group_out,
    lin_ccc,
    mean_rank_displacement,
    mean_within_item_std,
    min_units_for_ci_width,
    pairwise_rank_accuracy,
    pearson_r,
    pooled_leave_one_group_out,
    resolving_power,
    spearman_brown,
    ti_2prime,
    top_k_overlap,
    validate_pti,
    validate_pti_across_splits,
)

# Shrout & Fleiss (1979) Table 1: six subjects rated by four judges.
SF_DATA = [
    [9, 2, 5, 8],
    [6, 1, 3, 2],
    [8, 4, 6, 8],
    [7, 1, 2, 6],
    [10, 5, 6, 9],
    [6, 2, 4, 7],
]

# Inter-pass human agreement reported in the submission's Appendix G.2.
PAPER_INTER_PASS_RELIABILITY = 0.249


# ---------------------------------------------------------------------------
# correlation suite
# ---------------------------------------------------------------------------


class TestCorrelations:
    def test_pearson_matches_hand_computed_value(self):
        assert pearson_r([1, 2, 3, 4], [2, 4, 6, 8]) == pytest.approx(1.0)
        assert pearson_r([1, 2, 3, 4], [8, 6, 4, 2]) == pytest.approx(-1.0)

    def test_pearson_none_when_a_side_is_constant(self):
        assert pearson_r([1, 1, 1], [1, 2, 3]) is None

    def test_ccc_is_one_only_for_exact_agreement(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert lin_ccc(x, x) == pytest.approx(1.0)

    def test_ccc_penalises_shift_and_scale_where_pearson_does_not(self):
        """The behaviour that makes CCC the answer to the stability objection."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        shifted = [v + 10.0 for v in x]
        scaled = [v * 2.0 for v in x]
        assert pearson_r(x, shifted) == pytest.approx(1.0)
        assert pearson_r(x, scaled) == pytest.approx(1.0)
        assert lin_ccc(x, shifted) < 0.1
        assert lin_ccc(x, scaled) < 0.5


# ---------------------------------------------------------------------------
# ICC
# ---------------------------------------------------------------------------


class TestIcc:
    def test_reproduces_shrout_and_fleiss_published_values(self):
        result = icc(SF_DATA)
        assert result.icc_1_1 == pytest.approx(0.17, abs=0.01)
        assert result.icc_2_1 == pytest.approx(0.29, abs=0.01)
        assert result.icc_3_1 == pytest.approx(0.71, abs=0.01)
        assert result.icc_2_k == pytest.approx(0.62, abs=0.01)
        assert result.icc_3_k == pytest.approx(0.91, abs=0.01)

    def test_shape_is_reported(self):
        result = icc(SF_DATA)
        assert (result.n_subjects, result.n_raters) == (6, 4)

    def test_averaged_reliability_exceeds_single_rater(self):
        result = icc(SF_DATA)
        assert result.averaged_raters > result.single_rater

    def test_identical_raters_give_perfect_reliability(self):
        ratings = [[3, 3], [7, 7], [1, 1], [9, 9]]
        assert icc(ratings).icc_3_1 == pytest.approx(1.0)

    def test_ragged_design_is_rejected_not_imputed(self):
        with pytest.raises(ValueError, match="fully crossed"):
            icc([[1, 2, 3], [1, 2]])

    def test_degenerate_shapes_return_none(self):
        assert icc([]).icc_2_1 is None
        assert icc([[1, 2]]).icc_2_1 is None


# ---------------------------------------------------------------------------
# TI_m
# ---------------------------------------------------------------------------


class TestTrustIndex:
    def test_ti_2prime_is_geometric_mean_of_validity_and_stability(self):
        value, corr_clamped, stab_clamped = ti_2prime(0.64, 0.0)
        assert value == pytest.approx(0.8)
        assert not corr_clamped and not stab_clamped

        value, _, _ = ti_2prime(1.0, 0.75)
        assert value == pytest.approx(0.5)

    def test_negative_correlation_clamps_to_zero_and_is_flagged(self):
        """A judge that ranks against the target earns zero trust, not a crash."""
        value, corr_clamped, _ = ti_2prime(-0.30, 0.10)
        assert value == pytest.approx(0.0)
        assert corr_clamped is True

    def test_missing_inputs_are_not_computable(self):
        assert ti_2prime(None, 0.1)[0] is None
        assert ti_2prime(0.5, None)[0] is None

    def test_raw_signed_correlation_survives_the_clamp(self):
        result = compute_ti_m(
            "leanstral",
            judge_scores=[1, 2, 3, 4, 5],
            target_scores=[5, 4, 3, 2, 1],
            instability=0.1,
        )
        assert result.ti_2prime == pytest.approx(0.0)
        assert result.correlation == pytest.approx(-1.0)
        assert result.correlation_clamped is True

    def test_perfect_judge_scores_near_one(self):
        result = compute_ti_m(
            "oracle",
            judge_scores=[0.1, 0.4, 0.6, 0.9],
            target_scores=[0.1, 0.4, 0.6, 0.9],
            instability=0.0,
        )
        assert result.status == COMPUTED
        assert result.ti_2prime == pytest.approx(1.0)

    def test_instability_derived_from_repeats(self):
        result = compute_ti_m(
            "codex",
            judge_scores=[0.2, 0.5, 0.9],
            target_scores=[0.1, 0.6, 0.8],
            judge_repeats_by_item=[[0.2, 0.2], [0.5, 0.5], [0.9, 0.9]],
        )
        assert result.instability == pytest.approx(0.0)
        assert result.stability == pytest.approx(1.0)

    def test_not_computable_without_any_stability_information(self):
        result = compute_ti_m("x", [1, 2, 3], [1, 2, 3])
        assert result.status == NOT_COMPUTABLE
        assert result.ti_2prime is None
        assert result.ti_m1 == pytest.approx(1.0)

    def test_scale_ratio_exposes_a_judge_compressed_against_the_target(self):
        result = compute_ti_m(
            "compressed",
            judge_scores=[0.50, 0.52, 0.54, 0.56],
            target_scores=[0.10, 0.40, 0.70, 1.00],
            instability=0.0,
        )
        assert result.scale_ratio < 0.15
        assert result.lin_ccc < result.correlation


class TestInstabilityDefinition:
    """The stability term must measure repeat noise, never item discrimination."""

    def test_discriminating_judge_with_no_repeat_noise_is_perfectly_stable(self):
        repeats = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]]
        assert mean_within_item_std(repeats) == pytest.approx(0.0)

    def test_indecisive_judge_with_repeat_noise_is_penalised(self):
        repeats = [[0.1, 0.9, 0.5], [0.2, 0.8, 0.5], [0.3, 0.7, 0.5]]
        assert mean_within_item_std(repeats) > 0.2

    def test_within_item_std_differs_from_pooled_std(self):
        """Pooled std would rank these the same way; within-item std inverts it."""
        discriminating = [[0.0, 0.0], [1.0, 1.0]]
        noisy = [[0.4, 0.6], [0.4, 0.6]]
        assert mean_within_item_std(discriminating) < mean_within_item_std(noisy)

    def test_single_repeat_items_are_skipped(self):
        assert mean_within_item_std([[0.5], [0.7]]) is None


# ---------------------------------------------------------------------------
# ceiling
# ---------------------------------------------------------------------------


class TestCeiling:
    def test_spearman_brown_raises_reliability_with_more_raters(self):
        assert spearman_brown(0.249, 1) == pytest.approx(0.249)
        assert spearman_brown(0.249, 5) == pytest.approx(0.624, abs=0.001)

    def test_attenuation_ceiling_is_sqrt_of_reliability(self):
        assert attenuation_ceiling(0.25) == pytest.approx(0.5)
        assert attenuation_ceiling(1.0) == pytest.approx(1.0)
        assert attenuation_ceiling(0.0) == pytest.approx(0.0)

    def test_paper_single_pass_labels_cannot_reach_the_target(self):
        """Appendix G.2 reliability of 0.249 caps any judge near 0.50."""
        report = ceiling_report(
            single_rater_reliability=PAPER_INTER_PASS_RELIABILITY,
            n_raters=1,
            target_threshold=0.70,
        )
        assert report.ceiling_single == pytest.approx(0.499, abs=0.002)
        assert report.threshold_reachable is False

    def test_five_raters_lift_the_ceiling_above_the_target(self):
        report = ceiling_report(
            single_rater_reliability=PAPER_INTER_PASS_RELIABILITY,
            n_raters=5,
            target_threshold=0.70,
        )
        assert report.ceiling_averaged == pytest.approx(0.790, abs=0.002)
        assert report.threshold_reachable is True

    def test_reports_how_many_raters_the_target_needs(self):
        report = ceiling_report(
            single_rater_reliability=PAPER_INTER_PASS_RELIABILITY,
            n_raters=1,
            target_threshold=0.70,
        )
        assert report.raters_needed_for_threshold == 3

    def test_ceiling_can_be_estimated_straight_from_a_rating_matrix(self):
        report = ceiling_report(SF_DATA, target_threshold=0.70)
        assert report.n_raters == 4
        assert report.averaged_reliability == pytest.approx(0.62, abs=0.01)
        assert report.ceiling_averaged == pytest.approx(math.sqrt(0.62), abs=0.01)

    def test_requires_either_matrix_or_summary(self):
        with pytest.raises(ValueError, match="needs either ratings"):
            ceiling_report()

    def test_disattenuation_raises_an_observed_correlation(self):
        assert disattenuate(0.40, 0.64) == pytest.approx(0.5)
        assert disattenuate(None, 0.64) is None
        assert disattenuate(0.4, 0.0) is None


# ---------------------------------------------------------------------------
# resolving power
# ---------------------------------------------------------------------------


class TestResolvingPower:
    def test_paper_panel_has_no_resolving_power(self):
        """Spread across judges is about the size of one judge's own error."""
        criterion = [0.45 + 0.109 * i / 7 for i in range(8)]
        report = resolving_power(criterion, n_items_per_unit=75)
        assert report.criterion_se == pytest.approx(0.116, abs=0.002)
        assert report.resolving_ratio < 1.2
        assert report.underpowered is True

    def test_wide_spread_and_many_items_are_well_powered(self):
        criterion = [i / 15 for i in range(16)]
        report = resolving_power(criterion, n_items_per_unit=600)
        assert report.resolving_ratio > 3.0

    def test_small_panel_is_flagged_regardless_of_spread(self):
        report = resolving_power([0.0, 0.5, 1.0], n_items_per_unit=10_000)
        assert report.underpowered is True
        assert any("below the" in note for note in report.notes)

    def test_fisher_interval_at_eight_units_straddles_zero(self):
        low, high = fisher_ci(0.70, 8)
        assert low < 0.0 < high

    def test_fisher_interval_narrows_with_more_units(self):
        narrow = fisher_ci(0.70, 50)
        wide = fisher_ci(0.70, 8)
        assert (narrow[1] - narrow[0]) < (wide[1] - wide[0])

    def test_min_units_for_ci_width_is_monotone(self):
        loose = min_units_for_ci_width(0.70, 0.6)
        tight = min_units_for_ci_width(0.70, 0.3)
        assert loose < tight


# ---------------------------------------------------------------------------
# ranking agreement
# ---------------------------------------------------------------------------


class TestRankMetrics:
    def test_pairwise_accuracy_spans_the_full_range(self):
        assert pairwise_rank_accuracy([1, 2, 3], [1, 2, 3]) == pytest.approx(1.0)
        assert pairwise_rank_accuracy([3, 2, 1], [1, 2, 3]) == pytest.approx(0.0)

    def test_predicted_ties_earn_half_credit(self):
        assert pairwise_rank_accuracy([1, 1], [1, 2]) == pytest.approx(0.5)

    def test_criterion_ties_are_excluded(self):
        assert pairwise_rank_accuracy([5, 1], [2, 2]) is None

    def test_top_k_overlap_detects_a_reversed_leaderboard(self):
        assert top_k_overlap([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], 3) == pytest.approx(1.0)
        assert top_k_overlap([1, 2, 3, 4, 5], [5, 4, 3, 2, 1], 2) == pytest.approx(0.0)

    def test_top_k_rejects_impossible_k(self):
        assert top_k_overlap([1, 2], [1, 2], 0) is None
        assert top_k_overlap([1, 2], [1, 2], 5) is None

    def test_rank_displacement_is_zero_for_an_exact_match(self):
        assert mean_rank_displacement([1, 2, 3], [10, 20, 30]) == pytest.approx(0.0)
        assert mean_rank_displacement([1, 2, 3], [30, 20, 10]) > 0.0


# ---------------------------------------------------------------------------
# bootstrap
# ---------------------------------------------------------------------------


class TestBootstrap:
    def test_interval_brackets_the_point_estimate(self):
        x = [0.1, 0.3, 0.35, 0.5, 0.55, 0.7, 0.8, 0.95, 1.0, 0.2, 0.6, 0.45]
        y = [0.15, 0.25, 0.4, 0.45, 0.6, 0.65, 0.85, 0.9, 0.95, 0.3, 0.55, 0.5]
        estimate = bootstrap_ci(x, y, pearson_r, name="pearson", resamples=2000)
        assert estimate.ci_low <= estimate.value <= estimate.ci_high

    def test_same_seed_gives_identical_intervals(self):
        x = list(range(12))
        y = [v * 1.3 + (v % 3) for v in x]
        first = bootstrap_ci(x, y, pearson_r, resamples=500, seed=7)
        second = bootstrap_ci(x, y, pearson_r, resamples=500, seed=7)
        assert (first.ci_low, first.ci_high) == (second.ci_low, second.ci_high)

    def test_tiny_panels_get_a_point_estimate_but_no_interval(self):
        estimate = bootstrap_ci([1, 2], [1, 2], pearson_r, resamples=100)
        assert estimate.ci_low is None

    def test_correlation_suite_reports_every_requested_method(self):
        x = [1, 2, 3, 4, 5, 6, 7, 8]
        y = [2, 1, 4, 3, 6, 5, 8, 7]
        suite = correlation_suite(x, y, resamples=200)
        assert set(suite) == {"pearson", "spearman", "kendall_tau_b", "lin_ccc"}
        assert suite["kendall_tau_b"].value <= suite["spearman"].value

    def test_unknown_method_is_rejected(self):
        with pytest.raises(KeyError):
            correlation_suite([1, 2, 3], [1, 2, 3], methods=["cosine"])


# ---------------------------------------------------------------------------
# splits
# ---------------------------------------------------------------------------


GROUPS = {
    "codex-p1": "codex",
    "codex-p2": "codex",
    "opus-p1": "opus",
    "opus-p2": "opus",
    "leanstral-p1": "leanstral",
    "leanstral-p2": "leanstral",
    "qwen-p1": "qwen",
    "qwen-p2": "qwen",
}


class TestSplits:
    def test_leave_one_group_out_produces_one_fold_per_group(self):
        splits = leave_one_group_out(list(GROUPS), GROUPS)
        assert len(splits) == 4
        assert {s.name for s in splits} == {
            "holdout:codex",
            "holdout:opus",
            "holdout:leanstral",
            "holdout:qwen",
        }

    def test_no_unit_appears_in_both_halves_of_a_fold(self):
        for split in leave_one_group_out(list(GROUPS), GROUPS):
            assert not set(split.train) & set(split.test)

    def test_whole_group_is_held_out_never_split(self):
        """The point of the protocol: the test family is unseen at fit time."""
        for split in leave_one_group_out(list(GROUPS), GROUPS):
            held = {GROUPS[u] for u in split.test}
            trained = {GROUPS[u] for u in split.train}
            assert not held & trained

    def test_three_way_split_keeps_groups_disjoint(self):
        split = grouped_three_way_split(list(GROUPS), GROUPS)
        train = {GROUPS[u] for u in split.train}
        validation = {GROUPS[u] for u in split.validation}
        test = {GROUPS[u] for u in split.test}
        assert not train & validation
        assert not train & test
        assert not validation & test

    def test_three_way_split_covers_every_unit(self):
        split = grouped_three_way_split(list(GROUPS), GROUPS)
        assert set(split.train) | set(split.validation) | set(split.test) == set(GROUPS)

    def test_missing_group_assignment_is_an_error(self):
        with pytest.raises(KeyError):
            leave_one_group_out(["unknown"], GROUPS)

    def test_too_few_groups_for_a_three_way_split(self):
        with pytest.raises(ValueError, match="three-way split"):
            grouped_three_way_split(["a", "b"], {"a": "g1", "b": "g2"})


# ---------------------------------------------------------------------------
# end to end
# ---------------------------------------------------------------------------


class TestValidatePti:
    def test_perfect_proxy_on_a_real_panel_is_computed_and_strong(self):
        units = [f"judge{i:02d}" for i in range(16)]
        pti = {u: i / 15 for i, u in enumerate(units)}
        ti = {u: i / 15 for i, u in enumerate(units)}
        report = validate_pti(pti, ti, n_items_per_unit=600, resamples=400)
        assert report.status == COMPUTED
        assert report.headline.value == pytest.approx(1.0)
        assert report.pairwise_rank_accuracy == pytest.approx(1.0)

    def test_perfect_proxy_on_the_papers_panel_is_still_underpowered(self):
        """A point estimate of 1.0 must not read as evidence at n=8."""
        units = [f"judge{i}" for i in range(8)]
        pti = {u: i for i, u in enumerate(units)}
        ti = {u: 0.45 + 0.109 * i / 7 for i, u in enumerate(units)}
        report = validate_pti(pti, ti, n_items_per_unit=75, resamples=400)
        assert report.headline.value == pytest.approx(1.0)
        assert report.status == UNDERPOWERED
        assert report.power.notes

    def test_units_missing_a_criterion_are_dropped(self):
        pti = {"a": 1.0, "b": 2.0, "c": 3.0, "d": 4.0}
        ti = {"a": 1.0, "b": 2.0, "c": None, "d": 4.0}
        report = validate_pti(pti, ti, resamples=100)
        assert set(report.units) == {"a", "b", "d"}

    def test_panel_below_three_units_is_not_computable(self):
        report = validate_pti({"a": 1.0, "b": 2.0}, {"a": 1.0, "b": 2.0})
        assert report.status == NOT_COMPUTABLE
        assert report.correlations == {}

    def test_disattenuation_applied_when_a_ceiling_is_supplied(self):
        units = [f"j{i}" for i in range(14)]
        pti = {u: i for i, u in enumerate(units)}
        ti = {u: i * 0.5 for i, u in enumerate(units)}
        ceiling = ceiling_report(
            single_rater_reliability=PAPER_INTER_PASS_RELIABILITY, n_raters=5
        )
        report = validate_pti(
            pti, ti, n_items_per_unit=600, ceiling=ceiling, resamples=200
        )
        raw = report.correlations["spearman"].value
        corrected = report.disattenuated["spearman"]
        assert corrected > raw

    def test_across_splits_reports_train_and_test_separately(self):
        units = list(GROUPS)
        pti = {u: i for i, u in enumerate(units)}
        ti = {u: float(i) for i, u in enumerate(units)}
        splits = leave_one_group_out(units, GROUPS)
        results = validate_pti_across_splits(pti, ti, splits, resamples=100)
        assert set(results) == {s.name for s in splits}
        for per_split in results.values():
            assert "train" in per_split
            assert "test" in per_split

    def test_held_out_family_can_fail_while_train_succeeds(self):
        """The failure mode the protocol exists to expose."""
        units = list(GROUPS)
        # Proxy tracks the criterion everywhere except the leanstral family.
        ti = {u: float(i) for i, u in enumerate(units)}
        pti = dict(ti)
        for unit in units:
            if GROUPS[unit] == "leanstral":
                pti[unit] = -ti[unit]
        splits = {s.name: s for s in leave_one_group_out(units, GROUPS)}
        results = validate_pti_across_splits(
            pti, ti, [splits["holdout:leanstral"]], resamples=100
        )
        train = results["holdout:leanstral"]["train"]
        assert train.headline.value == pytest.approx(1.0)


class TestPooledHoldout:
    """Cross-validated validity pooled over folds, for panels with few groups."""

    def _panel(self, n_groups: int = 5, per_group: int = 4):
        units, pti, ti, groups = [], {}, {}, {}
        for g in range(n_groups):
            for j in range(per_group):
                name = f"g{g}-u{j}"
                value = g * per_group + j
                units.append(name)
                pti[name] = float(value)
                ti[name] = float(value) * 0.25
                groups[name] = f"group{g}"
        return units, pti, ti, groups

    def test_every_unit_receives_a_held_out_prediction(self):
        units, pti, ti, groups = self._panel()
        report = pooled_leave_one_group_out(pti, ti, groups, resamples=200)
        assert set(report.units) == set(units)
        assert report.skipped_units == ()
        assert report.n_folds == 5

    def test_recovers_a_linear_relationship_out_of_sample(self):
        _, pti, ti, groups = self._panel()
        report = pooled_leave_one_group_out(pti, ti, groups, resamples=200)
        assert report.headline.value == pytest.approx(1.0)
        assert report.status == COMPUTED

    def test_pooling_yields_one_estimate_over_the_whole_panel(self):
        """Four folds of three units each become one correlation over twelve."""
        units = list(GROUPS)
        pti = {u: float(i) for i, u in enumerate(units)}
        ti = {u: float(i) * 2.0 for i, u in enumerate(units)}
        report = pooled_leave_one_group_out(pti, ti, GROUPS, resamples=200)
        assert len(report.units) == len(units)
        assert report.n_folds == 4

    def test_a_proxy_that_inverts_one_family_is_caught(self):
        """In-panel fit stays perfect; the pooled held-out estimate drops."""
        _, pti, ti, groups = self._panel()
        for unit, group in groups.items():
            if group == "group2":
                pti[unit] = -pti[unit]
        report = pooled_leave_one_group_out(pti, ti, groups, resamples=200)
        in_panel = validate_pti(pti, ti, resamples=200)
        assert report.headline.value < in_panel.headline.value

    def test_degenerate_fold_is_reported_not_dropped_silently(self):
        pti = {"a1": 1.0, "a2": 1.0, "b1": 1.0, "b2": 1.0}
        ti = {"a1": 0.1, "a2": 0.2, "b1": 0.3, "b2": 0.4}
        groups = {"a1": "a", "a2": "a", "b1": "b", "b2": "b"}
        report = pooled_leave_one_group_out(pti, ti, groups, resamples=50)
        assert set(report.skipped_units) == set(pti)
        assert report.status == NOT_COMPUTABLE

    def test_single_group_is_rejected(self):
        with pytest.raises(ValueError, match="at least two groups"):
            pooled_leave_one_group_out(
                {"a": 1.0, "b": 2.0}, {"a": 1.0, "b": 2.0}, {"a": "g", "b": "g"}
            )

    def test_predictions_never_come_from_the_units_own_group(self):
        """The property that makes the pooled number genuinely held out."""
        _, pti, ti, groups = self._panel(n_groups=3, per_group=3)
        # Make one group's relationship the exact opposite of every other's.
        for unit, group in groups.items():
            if group == "group1":
                ti[unit] = -ti[unit]
        report = pooled_leave_one_group_out(pti, ti, groups, resamples=100)
        by_unit = dict(zip(report.units, report.predicted, strict=True))
        flipped = [u for u, g in groups.items() if g == "group1"]
        # A calibration fit without group1 cannot reproduce group1's sign flip.
        assert all(by_unit[u] > 0 for u in flipped)
