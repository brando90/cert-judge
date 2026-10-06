"""Offline tests for experiment 44's cached-score selection utility script."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

MODULE = Path(__file__).with_name("analyze_selection_utility.py")
spec = importlib.util.spec_from_file_location("e44", MODULE)
E = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(E)


def items(n_tasks=4):
    return [{"item": f"t{t}_a{a}", "task": f"t{t}", "split": "val", "target_expert": (a + t) / (n_tasks + 1),
             "ref_placeholder_at_annotation": False, "ref_ambiguous_in_window": False} for t in range(n_tasks) for a in range(2)]


def test_final_status_filtering_median_and_zero():
    harvest = {"config": "x", "cells": [
        {"cell": "a", "repeat": 1, "kind": "crit", "level": 0, "key": "i", "status": "measured", "score": 0.0},
        {"cell": "b", "repeat": 2, "kind": "crit", "level": 0, "key": "i", "status": "deterministic", "score": 1.0},
        {"cell": "c", "repeat": 3, "kind": "crit", "level": 0, "key": "i", "status": "invalid", "score": 0.9},
    ]}
    assert E.median_scores(harvest) == {"i": 0.5}


def test_ties_and_missing_proxy_retain_oracle_candidates():
    configs = ["a", "b", "c"]
    weights = E.weights_max(configs, {"a": .9, "b": .9, "c": None})
    assert weights == {"a": .5, "b": .5}
    assert E.selector_weights(configs, {x: {"prompt_key": "H2" if x == "c" else "D0"} for x in configs},
                              {"a": .9, "b": .9, "c": None}, {x: 1.0 for x in configs}, "D0")["random"] == {"a": 1/3, "b": 1/3, "c": 1/3}


def test_positive_weight_undefined_member_is_not_dropped_or_renormalized():
    utilities = {"a": {"spearman": .5, "pearson": .5, "kendall": .4}, "b": {"spearman": None, "pearson": .2, "kendall": .1}}
    out = E.expected({"a": .5, "b": .5}, utilities)
    assert out["status"] == "UNDEFINED" and out["value"] is None and out["metrics"]["pearson"] == .35


def test_shared_support_threshold_and_undefined_correlations():
    assert E.corr([1, 1, 1], [.2, .5, .8])["spearman"] is None
    data = items(2)
    assert len(data) == 4 and 3 < np.ceil(.9 * 4)


def test_task_bootstrap_retains_multiplicity_and_pairwise_finite_draws():
    data = items(4)
    keys = [x["item"] for x in data]
    scores = {"a": {k: i / 8 for i, k in enumerate(keys)}, "b": {k: 1 - i / 8 for i, k in enumerate(keys)}}
    weights = {"proxy_C_ms_gold": {"a": 1.0}, "human_mirror_H2": {"b": 1.0}, "random": {"a": .5, "b": .5},
               "identity_C_ident": {"a": 1.0}, "transferred_prompt": None}
    out = E.bootstrap(scores, ["a", "b"], data, keys, weights, 100)
    assert out["draws"] == 100
    assert out["intervals"]["difference:proxy_C_ms_gold-human_mirror_H2"]["valid_draws"] == 100
    assert out["resampling_unit"].startswith("task")


def test_transferred_prompt_cannot_read_test_rows():
    meta = {"tr_a": {"prompt_key": "A"}, "tr_b": {"prompt_key": "B"}, "va_a": {"prompt_key": "A"}, "va_b": {"prompt_key": "B"},
            "te_a": {"prompt_key": "A"}}
    units = [
        {"config": "tr_a", "kind": "llm", "split": "train", "criteria": {"heldout": {"spearman": .6}}},
        {"config": "tr_b", "kind": "llm", "split": "train", "criteria": {"heldout": {"spearman": .5}}},
        {"config": "va_a", "kind": "llm", "split": "val", "criteria": {"heldout": {"spearman": .2}}},
        {"config": "va_b", "kind": "llm", "split": "val", "criteria": {"heldout": {"spearman": .9}}},
        {"config": "te_a", "kind": "llm", "split": "test", "criteria": {"heldout": {"spearman": 1.0}}},
    ]
    out = E.choose_prompt(units, meta)
    assert out["chosen_prompt"] == "B", "test row must not affect selection"


def test_fixed_mask_avoids_support_change():
    data = items(3)
    keys = [x["item"] for x in data]
    score = {"a": {k: float(i) for i, k in enumerate(keys)}, "b": {k: float(i) for i, k in enumerate(keys)}}
    mask = keys[:-1]
    got = E.config_correlations(score, ["a", "b"], data, mask)
    assert got["a"]["spearman"] == got["b"]["spearman"], "both candidates must use the same supplied mask"


def test_diagnostics_use_supplied_mask_and_repeat_sample_sd():
    im = {"x": {"target_expert": .2}, "y": {"target_expert": .8}}
    scores = {"a": {"x": .2, "y": .8, "offmask": 0.0}}
    raw = {"a": {"x": [.1, .3], "y": [.8], "offmask": [0.0, 1.0]}}
    got = E.score_diagnostics(scores, im, ["x", "y"], {"a": 1.0}, raw)
    sd = got["within_item_raw_repeat_sample_sd"]["a"]
    assert got["mean_absolute_error"] == 0.0 and sd["n_defined"] == 1 and sd["n_unavailable"] == 1 and sd["mean"] > 0
    assert got["available_repeat_counts"]["a"] == 3 and got["missing_repeat_counts"]["a"] == 3
    assert got["per_item_repeat_count_histogram"]["a"] == {"1": 1, "2": 1}


def test_vectorized_draw_statistics_match_scipy_on_ties_and_constants():
    matrix = np.array([[1., 1., 2., 3., 3.], [4., 4., 4., 4., 4.], [3., 2., 1., 1., 0.]])
    y = np.array([0., 1., 1., 2., 2.])
    idx = np.array([0, 1, 1, 2, 4])
    got = E.draw_correlations(matrix, y, idx)
    for row in (0, 2):
        want = E.corr(matrix[row, idx], y[idx])
        for stat in want:
            assert np.isclose(got[stat][row], want[stat])
    assert np.isnan(got["spearman"][1]) and np.isnan(got["pearson"][1]) and np.isnan(got["kendall"][1])
    constant = E.draw_correlations(np.array([np.full(42, .1)]), np.arange(42, dtype=float), np.arange(42))
    assert np.isnan(constant["spearman"][0]) and np.isnan(constant["pearson"][0]) and np.isnan(constant["kendall"][0])


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"{len(tests)} offline tests passed")
