#!/usr/bin/env python3
"""TLDR: Offline tests for experiment 49's analysis (zero inference): rating targets with missing raters and the 90%
coverage rule, task-level subsampling, NumPy tie-aware Spearman and permutation p-value parity with experiment 39's
analysis_lib, the power gate, the equal-budget selection, variance components on a matrix with known components, the
pre-declared readings, and (when the frozen inputs are present) the real gate G0."""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze_e49 as E  # noqa: E402


def inputs_present() -> bool:
    try:
        E.e39_root()
    except FileNotFoundError:
        return False
    return E.veribench_items_path().exists()


def test_rating_target_with_missing_raters():
    ratings = np.array([[4, 5, np.nan], [2, np.nan, np.nan], [np.nan, np.nan, np.nan], [1, 1, 1]], dtype=float)
    t = E.rating_target(ratings, [0, 1, 2])
    assert t[0] == pytest.approx(4.5 / 5) and t[1] == pytest.approx(0.4) and math.isnan(t[2]) and t[3] == pytest.approx(0.2)
    t3 = E.rating_target(ratings, [2])
    assert math.isnan(t3[0]) and math.isnan(t3[1]) and math.isnan(t3[2]) and t3[3] == pytest.approx(0.2)


def test_criterion_coverage_rule_and_target_dropping():
    rng = np.random.default_rng(0)
    n = 10
    target = rng.random(n)
    S = np.vstack([target + 0.01 * rng.random(n), target.copy(), target.copy()])
    S[1, :2] = np.nan          # 80% coverage -> NOT_COMPUTABLE
    S[2, 0] = np.nan           # 90% coverage -> computable
    c = E.criterion_vector(S, target)
    assert np.isfinite(c[0]) and math.isnan(c[1]) and np.isfinite(c[2])
    assert c[0] > 0.9 and c[2] == pytest.approx(1.0)
    target_drop = target.copy()
    target_drop[:2] = np.nan   # items without a target are dropped before the coverage rule
    c2 = E.criterion_vector(S, target_drop)
    assert np.isfinite(c2[1]) and c2[1] == pytest.approx(1.0)
    const = np.full(n, 0.5)
    assert all(math.isnan(v) for v in E.criterion_vector(S, const))


def fake_data(n_tasks=6, n_configs=4, seed=3):
    rng = np.random.default_rng(seed)
    tasks = [f"t{i}" for i in range(n_tasks)]
    task_items = {t: [3 * i, 3 * i + 1, 3 * i + 2] for i, t in enumerate(tasks)}
    n_items = 3 * n_tasks
    ratings = rng.integers(0, 6, size=(n_items, 5)).astype(float)
    ratings[::2, 2] = np.nan
    S = rng.random((n_configs, n_items))
    d = SimpleNamespace(tasks=tasks, task_items=task_items, ratings=ratings, S=S, n_configs=n_configs)
    d.items_of_tasks = lambda ts: np.array([i for t in ts for i in task_items[t]], dtype=int)
    return d


def test_task_level_subsampling_keeps_outputs_together():
    d = fake_data()
    rng = np.random.default_rng(1)
    for _ in range(20):
        tasks, raters, items = E.draw_design(d, rng, 4, 2)
        assert len(tasks) == 4 and len(set(tasks)) == 4 and len(raters) == 2 and len(set(raters)) == 2
        assert items.tolist() == [i for t in tasks for i in d.task_items[t]]
        assert len(items) == 12
    tasks, raters, items = E.draw_design(d, rng, 6, 5)
    assert tasks == d.tasks and raters == [0, 1, 2, 3, 4] and len(items) == 18
    c, used, n_items, r = E.draw_cell(d, rng, 3, 1)
    assert c.shape == (d.n_configs,) and n_items <= 9 and used <= 9


@pytest.mark.skipif(not inputs_present(), reason="experiment 39 receipts or VeriBench items not present")
def test_numpy_spearman_and_permutation_parity_with_analysis_lib():
    A = E.load_analysis_lib()
    r = random.Random(1)
    x = [r.choice([0.2, 0.4, 0.6, 0.8, 1.0]) for _ in range(20)]
    y = [r.random() for _ in range(20)]
    y[3] = y[4] = y[5]
    assert abs(float(E.spearman_rows(np.array(x), np.array(y))[0]) - A.spearman(x, y)) < 1e-12
    assert abs(float(E.spearman_pairs(np.array([x, x]), np.array([y, y]))[1]) - A.spearman(x, y)) < 1e-12
    draws, seed = 400, 7
    rr = random.Random(seed)
    ys = list(y)
    perms = []
    for _ in range(draws):
        rr.shuffle(ys)
        perms.append(list(ys))
    assert E.perm_p_given(x, y, perms) == pytest.approx(A.permutation_p(x, y, A.spearman, draws, seed))
    assert math.isnan(E.spearman_rows(np.full(5, 1.0), np.arange(5.0))[0])


def test_perm_p_rows_behaves():
    rng = np.random.default_rng(5)
    X = rng.standard_normal((500, 10))
    Y = rng.standard_normal((500, 10))
    rho, p = E.perm_p_rows(X, Y, rng, 200)
    assert 0.4 < float(np.mean(p)) < 0.6 and abs(float(np.mean(rho))) < 0.05
    Z = rng.standard_normal((200, 30))
    rho2, p2 = E.perm_p_rows(Z, 0.95 * Z + 0.3 * rng.standard_normal((200, 30)), rng, 200)
    assert float(np.mean(p2 < 0.05)) > 0.95 and float(np.mean(rho2)) > 0.8
    rho3, p3 = E.perm_p_rows(np.ones((3, 8)), rng.standard_normal((3, 8)), rng, 50)
    assert all(math.isnan(v) for v in rho3) and all(math.isnan(v) for v in p3)


def test_power_gate_logic():
    rng = np.random.default_rng(2)
    base = rng.standard_normal((50, 12))
    perfect = E.power_table(base, base, rng, 100)
    assert perfect["power"] == pytest.approx(1.0) and perfect["undefined_draws"] == 0
    anti = E.power_table(base, -base, rng, 100)
    assert anti["power"] == 0.0 and anti["frac_rho_ge_gate"] == 0.0
    const = E.power_table(np.ones((5, 12)), base[:5], rng, 100)
    assert const["undefined_draws"] == 5 and const["power"] == 0.0


def test_equal_budget_selection_and_readings():
    cells = []
    for T, R, rel, agree in ((5, 2, 0.80, 0.85), (10, 1, 0.85, 0.90), (5, 3, 0.70, 0.80), (15, 1, 0.95, 0.95), (10, 3, 0.95, 0.95), (15, 2, 0.95, 0.90), (25, 5, 1.0, 1.0)):
        cells.append({"T": T, "R": R, "ratings_nominal": 3 * T * R, "ratings_used_mean": 3.0 * T * R, "ranking_reliability_mean": rel, "gate_agreement_mean": agree, "precision_sd_mean_all": 0.1})
    q3 = E.q3_allocation({"cells": cells})
    assert q3["n_budgets"] == 3
    best = {r["ratings_nominal"]: (r["best"]["T"], r["best"]["R"]) for r in q3["budgets"]}
    assert best[30] == (10, 1) and best[45] == (15, 1) and best[90] == (15, 2)     # tie at 90 (0.95 vs 0.95): more tasks wins
    q2 = {"empirical": {name: {"by_K": {str(K): {"power": pw} for K, pw in zip(E.K_GRID, powers)}} for name, powers in
                        (("all_configurations", (0.3, 0.6, 0.85, 0.9, 0.95, 0.99)), ("fuller_context", (0.1, 0.2, 0.3, 0.4, 0.5, 0.6)), ("test_16", (0.2,) * 6), ("legacy", (0.0,) * 6))},
          "clustered": {str(M): {"power": pw} for M, pw in zip(E.M_GRID, (0.2, 0.5, 0.85, 0.9, 0.95))}}
    rd = E.readings({"cells": cells}, q2)
    assert rd["smallest_adequate_TR"]["T"] == 15 and rd["smallest_adequate_TR"]["R"] == 1
    assert rd["smallest_adequate_K_all_configurations"] == {"K": 16, "power": 0.85, "met": True}
    assert rd["smallest_adequate_K_fuller_context"] == {"K": None, "power": 0.6, "met": False}
    assert rd["smallest_adequate_M_clustered"]["M"] == 4 and rd["power_at_K16"]["fuller_context"] == 0.3


def test_two_way_components_recover_known_values():
    rng = np.random.default_rng(11)
    I, J = 1500, 40
    s_item, s_rater, s_e = 1.0, 0.3, 0.5
    a = rng.standard_normal(I) * s_item
    b = rng.standard_normal(J) * s_rater
    M = 3.0 + a[:, None] + b[None, :] + rng.standard_normal((I, J)) * s_e
    full = E.two_way_components(M)
    assert full["sigma2_item"] == pytest.approx(s_item ** 2, rel=0.08)
    assert full["sigma2_error"] == pytest.approx(s_e ** 2, rel=0.05)
    assert full["sigma2_rater"] == pytest.approx(s_rater ** 2, rel=0.5)
    assert full["icc_c1"] == pytest.approx(s_item ** 2 / (s_item ** 2 + s_e ** 2), abs=0.03)
    M2 = M.copy()
    M2[rng.random((I, J)) < 0.2] = np.nan
    miss = E.two_way_components(M2)
    assert miss["n_observations"] < I * J
    assert miss["sigma2_item"] == pytest.approx(s_item ** 2, rel=0.10) and miss["sigma2_error"] == pytest.approx(s_e ** 2, rel=0.06)
    assert miss["icc_c_by_R"]["5"] == pytest.approx(5 * miss["icc_c1"] / (1 + 4 * miss["icc_c1"]))
    # five-rater complete block: the alternating-least-squares fit agrees with the classic balanced ANOVA ICCs
    M5 = 3.0 + a[:300, None] + b[None, :5] + rng.standard_normal((300, 5)) * s_e
    bal = E.balanced_anova_icc(M5)
    als = E.two_way_components(M5)
    assert bal["icc_c1"] == pytest.approx(als["icc_c1"], abs=0.02) and bal["icc_a1"] == pytest.approx(als["icc_a1"], abs=0.03)


@pytest.mark.skipif(not inputs_present(), reason="experiment 39 receipts or VeriBench items not present")
def test_real_gate_g0_passes():
    A = E.load_analysis_lib()
    d = E.Data(A)
    assert d.n_configs == 56 and d.n_items == 75 and len(d.tasks) == 25
    assert int(d.test_mask.sum()) == 18 and int(d.test_computable.sum()) == 16
    g0 = E.gate_g0(d)
    assert g0["pass"], {k: v["pass"] for k, v in g0["checks"].items()}
    assert g0["checks"]["registered_association"]["recomputed"]["n_units"] == 16
