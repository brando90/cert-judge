#!/usr/bin/env python3
"""TLDR: Offline tests for experiment 48 — parity of the cluster bootstrap and the stratified permutation with
experiment 39's analysis_lib, the task-level criterion recomputation and its coverage rule, rater targets with a
missing rater, the reference-quality filters, the split-half Spearman–Brown step, and (when the receipts and the
pinned VeriBench items are present) the real G0 reproduction gate. No model calls."""
from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_e48 as X  # noqa: E402

A = X.A
pytestmark = pytest.mark.skipif(A is None, reason="experiment 39 receipts (analysis_lib) not found")


def _xy(n: int = 12, seed: int = 1):
    rng = random.Random(seed)
    x = [rng.random() for _ in range(n)]
    y = [v + 0.3 * rng.random() for v in x]
    return x, y


def test_cluster_bootstrap_matches_analysis_lib_interval():
    x, y = _xy(12)
    clusters = ["a"] * 4 + ["b"] * 4 + ["c"] * 2 + ["d"] * 2
    mine = X.cluster_bootstrap(x, y, clusters, draws=400, seed=7)
    ref = A.bootstrap_ci(x, y, A.spearman, draws=400, seed=7, clusters=clusters)
    assert mine["all_defined_draws"]["lo"] == ref["lo"]
    assert mine["all_defined_draws"]["hi"] == ref["hi"]
    assert mine["all_defined_draws"]["valid_draws"] == ref["valid_draws"]
    assert mine["n_clusters"] == 4 and mine["distinct_cluster_multisets"] == 35


def test_cluster_bootstrap_counts_small_draws():
    x, y = _xy(6)
    clusters = ["a"] * 3 + ["b"] * 3
    out = X.cluster_bootstrap(x, y, clusters, draws=50, seed=3)
    assert out["draws_fewer_than_8_units"] == 50
    assert out["draws_with_at_least_8_units"]["valid_draws"] == 0


def test_stratified_permutation_single_stratum_matches_analysis_lib():
    x, y = _xy(14, seed=2)
    p_mine, obs = X.stratified_permutation_p(x, y, ["s"] * 14, draws=300, seed=5)
    p_ref = A.permutation_p(x, y, A.spearman, draws=300, seed=5)
    assert obs == A.spearman(x, y)
    assert p_mine == p_ref


def test_stratified_permutation_constant_within_strata_gives_p_one():
    x = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    y = [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]
    strata = ["a"] * 4 + ["b"] * 4
    p, obs = X.stratified_permutation_p(x, y, strata, draws=100, seed=1)
    assert obs is not None and p == 1.0


def _synthetic_scores(medians: dict, split: str = "test"):
    cells = []
    for item, vals in medians.items():
        for r, v in enumerate(vals):
            cells.append({"kind": "crit", "key": item, "level": 0, "status": "measured", "score": v, "repeat": r})
    return A.Scores({"config": "m|P", "split": split, "family": "m", "kind": "llm", "cells": cells})


def test_criterion_over_matches_analysis_lib_criterion_and_coverage_rule():
    rng = random.Random(4)
    items = []
    for t in range(6):
        for k in range(3):
            items.append({"item": f"t{t}_a{k}", "task": f"t{t}", "split": "test" if t % 2 else "val", "target_expert": rng.random()})
    raw = {it["item"]: [rng.random(), rng.random(), rng.random()] for it in items}
    sc = _synthetic_scores(raw)
    ref = A.criterion(sc, items, ("val", "test"), draws=10, seed=1)
    med = {it["item"]: sc.median("crit", it["item"], 0) for it in items}
    target = {it["item"]: float(it["target_expert"]) for it in items}
    got, n_scored, declared = X.criterion_over(med, items, target)
    assert got == ref["spearman"] and n_scored == 18 and declared == 18
    # a task bootstrap with duplicates still computes
    dup = items + items[:3]
    got2, n2, d2 = X.criterion_over(med, dup, target)
    assert got2 is not None and n2 == 21 and d2 == 21
    # coverage below 90% -> NOT_COMPUTABLE
    med2 = dict(med)
    for it in items[:2]:
        med2[it["item"]] = None
    got3, n3, d3 = X.criterion_over(med2, items, target)
    assert got3 is None and n3 == 16 and d3 == 18
    # an item without a target under the view is not declared
    target2 = dict(target)
    target2[items[0]["item"]] = None
    got4, n4, d4 = X.criterion_over(med, items, target2)
    assert got4 is not None and d4 == 17 and n4 == 17


def test_rater_targets_with_missing_rater():
    items = [{"item": "i1", "p1": 4.0, "p2": 3.0, "p3": None, "p4": 5.0, "p5": 2.0, "target_expert": 0.7},
             {"item": "i2", "p1": 1.0, "p2": 2.0, "p3": 3.0, "p4": 4.0, "p5": 5.0, "target_expert": 0.4}]
    v = X.rater_targets(items)
    assert v["single_p3"]["i1"] is None and v["single_p3"]["i2"] == 0.6
    assert abs(v["all_available_raters_mean"]["i1"] - (14.0 / 4) / 5) < 1e-12
    assert abs(v["all_available_raters_mean"]["i2"] - 0.6) < 1e-12
    assert abs(v["leave_out_p3"]["i1"] - v["all_available_raters_mean"]["i1"]) < 1e-12
    assert abs(v["leave_out_p1"]["i1"] - (10.0 / 3) / 5) < 1e-12
    assert v["registered_target_expert"]["i1"] == 0.7


def test_reference_views_filters():
    held = []
    for t, (ph, am) in enumerate([(True, False), (False, True), (False, False), (True, True)]):
        for k in range(3):
            held.append({"item": f"t{t}_{k}", "task": f"t{t}", "split": "test" if t < 2 else "val",
                         X.PLACEHOLDER_FLAG: ph, X.AMBIGUOUS_FLAG: am})
    views, ph_tasks, am_tasks = X.reference_views(held)
    assert ph_tasks == ["t0", "t3"] and am_tasks == ["t1", "t3"]
    assert len(views["original45"]) == 12
    assert {it["task"] for it in views["no_placeholder_reference_tasks"]} == {"t1", "t2"}
    assert {it["task"] for it in views["no_ambiguous_reference_tasks"]} == {"t0", "t2"}
    assert {it["task"] for it in views["neither_placeholder_nor_ambiguous"]} == {"t2"}
    assert {it["task"] for it in views["test_tasks_only30"]} == {"t0", "t1"}


def test_split_half_spearman_brown_and_ms_gold_halves():
    assert abs(X.spearman_brown(0.5) - 2 / 3) < 1e-12
    assert X.spearman_brown(None) is None
    cells = []
    ladders = {"k1": [0.9, 0.8, 0.7], "k2": [0.9, 0.9, 0.9]}   # k1 decreasing (quality 1), k2 constant (quality 0)
    for key, meds in ladders.items():
        cells.append({"kind": "ident", "key": key, "level": 0, "status": "measured", "score": meds[0]})
        for lv, v in enumerate(meds[1:], start=1):
            cells.append({"kind": "ms_gold", "key": key, "level": lv, "status": "measured", "score": v})
    sc = A.Scores({"config": "m|P", "split": "train", "family": "m", "kind": "llm", "cells": cells})
    probes = {"ms_gold": [{"key": k, "level": lv} for k in ladders for lv in (1, 2)]}
    full = A.components(sc, probes)["ms_gold"]["value"]
    h1, h2 = X.ms_gold_over_keys(sc, probes, {"k1"}), X.ms_gold_over_keys(sc, probes, {"k2"})
    assert h1 == 1.0 and h2 == 0.0 and abs(full - (h1 + h2) / 2) < 1e-12


def test_readings():
    assert X.reading(0.6, 0.01) == "ROBUST"
    assert X.reading(0.6, 0.2) == "WEAKENED"
    assert X.reading(0.3, 0.01) == "WEAKENED"
    assert X.reading(-0.1, 0.9) == "REVERSED"
    assert X.reading(None, None) == "unavailable"
    assert X.reading(0.5, None) == "ROBUST"


def test_real_g0_gate_passes():
    try:
        items_path, digest, items = X.load_items()
    except (FileNotFoundError, SystemExit):
        pytest.skip("pinned VeriBench items.jsonl not available")
    root = X.E39
    units_test = X.read_json(root / "results/units_test.json")
    units_tv = X.read_json(root / "results/units_train_val.json")
    receipt = X.read_json(root / "results/TEST_RECEIPT.json")
    probes = A.valid_probes(X.read_json(root / "results/probe_manifest.json"))
    test_units = [u for u in units_test["units"] if u["kind"] == "llm"]
    llm_units = [u for u in units_tv["units"] if u["kind"] == "llm"] + test_units
    scores = {u["config"]: A.Scores(X.read_json(X.harvest_path(root, u["config"]))) for u in test_units}
    g0 = X.run_g0(root, items, test_units, llm_units, scores, probes, receipt, units_tv, ci_draws=50)
    assert g0["registered_association"]["pass"]
    assert g0["criterion_reproduction"]["pass"]
    assert g0["c_ms_gold_reproduction"]["pass"]
    assert g0["criterion_ranking_reproducibility"]["pass"]
    assert g0["pass"]
