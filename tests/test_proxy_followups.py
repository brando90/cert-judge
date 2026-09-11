"""Counterexamples for the exploratory analysis and validation repairs."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest
from cert_judge.ti_validation import compute_ti_m, fisher_ci, top_k_overlap

PATH = Path(__file__).resolve().parents[1] / "experiments/30_proxy_trust_index_held_out_validity/expt_v2/run_diagnostics.py"
spec = importlib.util.spec_from_file_location("proxy_followups", PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_fisher_uses_requested_confidence_and_rejects_invalid_alpha():
    low, high = fisher_ci(.5, 20, alpha=.5)
    lower, higher = fisher_ci(.5, 20, alpha=.01)
    assert lower < low < high < higher
    with pytest.raises(ValueError):
        fisher_ci(.5, 20, alpha=0)


def test_constant_predictor_receives_chance_top_k_overlap():
    assert top_k_overlap([0, 0, 0, 0], [1, 2, 3, 4], 1) == pytest.approx(.25)
    assert top_k_overlap([0, 0, 0, 0], [1, 2, 3, 4], 2) == pytest.approx(.5)
    assert top_k_overlap([0, 0, 1, 1], [0, 0, 1, 1], 1) == pytest.approx(.5)


@pytest.mark.parametrize("repeats", [[[0., 0.]], [[0., 0.], [.5]], [[0., 0.], [2., 2.]]])
def test_combined_criterion_rejects_misaligned_missing_or_unscaled_repeats(repeats):
    with pytest.raises(ValueError):
        compute_ti_m("judge", [0., .5], [0., .5], judge_repeats_by_item=repeats)


def test_score_join_requires_judge_identity_and_complete_distinct_repeats():
    rows = [{"judge_id": j, "score_cell_id": "same", "repeat_id": r,
             "normalized_score": v} for j, v in [("a", .2), ("b", .8)] for r in range(3)]
    result = m.score_index(rows)
    assert result[("a", "same")] == [.2] * 3
    assert result[("b", "same")] == [.8] * 3
    with pytest.raises(ValueError):
        m.score_index(rows + [rows[0]])
    with pytest.raises(ValueError):
        m.score_index(rows[:-1])


def test_floor_is_at_artifact_level_and_shared_weights_apply_to_every_judge():
    factors = {p: {"a|g0": [0., 1.], "b|g0": [1., 1.]} for p in m.PROPERTIES}
    result = m.aggregate(factors)
    assert result["frozen"][0].tolist() == [0., 1.]
    assert result["floor_0.001"][0, 0] == pytest.approx(np.sqrt(.001))
    assert result["mean_then_gm"][0, 0] == pytest.approx(.5)
    omitted = m.aggregate(factors, {"a": np.array([0]), "b": np.array([2])})
    assert omitted["frozen"][0].tolist() == [1., 1.]


def test_negative_slope_does_not_masquerade_as_positive_proxy():
    x = np.array([.1, .2, .8, .9])
    y = 1 - x
    groups = ["a", "a", "b", "b"]
    unrestricted, uf = m.family_predictions(x, y, groups, "unrestricted")
    constrained, cf = m.family_predictions(x, y, groups, "nonnegative")
    baseline, _ = m.family_predictions(x, y, groups, "training_mean")
    np.testing.assert_allclose(unrestricted, y)
    np.testing.assert_allclose(constrained, baseline)
    assert all(f["used_slope"] < 0 for f in uf)
    assert all(f["used_slope"] == 0 for f in cf)


def test_constant_training_fold_keeps_every_test_prediction():
    predicted, folds = m.family_predictions(np.array([0., 0., .5, .8]),
        np.array([.1, .2, .3, .4]), ["a", "a", "b", "b"], "nonnegative")
    assert len(predicted) == 4 and np.isfinite(predicted).all()
    assert folds[1]["constant_training_fallback"]
    np.testing.assert_allclose(predicted[2:], [.15, .15])


def test_identical_judges_stay_identical_under_shared_problem_bootstrap():
    rows = [{"gold_file": f"p{i}.lean", "artifact_id": f"p{i}|g0"} for i in range(4)]
    rr = np.array([[[v, v, v] for v in [0., .2, .8, 1.]]] * 2)
    labels = {"average": np.array([0., .3, .6, 1.])}
    factors = {p: {f"p{i}|g0": [.2 + .1*i, .2 + .1*i] for i in range(4)} for p in m.PROPERTIES}
    targets, proxies = m.bootstrap(rows, rr, labels, factors, 20, 7)
    np.testing.assert_allclose(targets[:, 0], targets[:, 1], equal_nan=True)
    for values in proxies.values():
        np.testing.assert_allclose(values[:, 0], values[:, 1], equal_nan=True)


def test_full_frozen_inputs_reconstruct_without_changing_score_identity():
    _, judges, _, rows, repeats, _, _, variants = m.load_inputs()
    assert len(judges) == 8 and len(rows) == 72 and repeats.shape == (8, 72, 3)
    assert np.count_nonzero(variants["frozen"] == 0) == 7
    assert np.count_nonzero(variants["P_bm"] == 0) == 6
