#!/usr/bin/env python3
"""Canonical proper scoring rules, agreement statistics, calibration fitters, and cluster uncertainty.

Follows the prospective evaluation definitions in:
~/judges-dont-need-psychometrics-or-corr/experiments/02_exp06_ce_vs_pearson_matched_budget_start_09Nov2026/EVALUATION_CRITERION_11-09-2026.md
All proper scoring rules operate over the six integer rating categories {0, 1, 2, 3, 4, 5},
averaged within each artifact over its observed ratings and then weighted equally across eligible artifacts.
"""
from __future__ import annotations

import itertools
import math
from typing import Callable, Iterable, Sequence

import numpy as np
from scipy import optimize, stats

CATEGORIES = np.arange(6, dtype=float)
DEFAULT_CE_FLOOR = 1e-12


def validate_probs(probs_q: Sequence[float]) -> np.ndarray:
    """Validate and return a 6-category probability forecast summing to 1."""
    q = np.asarray(probs_q, dtype=float)
    if q.shape != (6,) or not np.all(np.isfinite(q)) or np.any(q < -1e-12):
        raise ValueError(f"Expected 6 finite non-negative probabilities, got {probs_q!r}")
    q = np.clip(q, 0.0, None)
    s = float(q.sum())
    if s <= 0.0:
        raise ValueError("Probability vector must have positive total mass")
    return q / s


def rating_counts(ratings: Sequence[int | float]) -> np.ndarray:
    """Count integer ratings in {0..5}, validating integrality within 1e-9."""
    if len(ratings) == 0:
        raise ValueError("Artifact must have at least one rating")
    c = np.zeros(6, dtype=float)
    for y in ratings:
        yf = float(y)
        yi = int(round(yf))
        if abs(yf - yi) > 1e-9 or yi < 0 or yi > 5:
            raise ValueError(f"Rating must be an integer in 0..5, got {y!r}")
        c[yi] += 1.0
    return c


def empirical_dist(ratings: Sequence[int | float]) -> np.ndarray:
    """Empirical distribution p_hat over {0..5} for one artifact."""
    c = rating_counts(ratings)
    return c / float(c.sum())


def binned_repeats_to_probs(repeats_01: Sequence[float], alpha: float = 0.5) -> np.ndarray:
    """Bin [0,1] scalar repeats to {0..5} via floor(5s + 0.5) and apply symmetric Laplace smoothing."""
    if len(repeats_01) == 0:
        raise ValueError("Need at least one repeat score")
    c = np.zeros(6, dtype=float)
    for s in repeats_01:
        idx = min(5, max(0, math.floor(5.0 * float(s) + 0.5 + 1e-12)))
        c[idx] += 1.0
    q = c + float(alpha)
    return q / float(q.sum())


def expected_score_05(probs_q: Sequence[float]) -> float:
    """Expected 0-5 score under forecast distribution q."""
    q = validate_probs(probs_q)
    return float(np.dot(CATEGORIES, q))


def rps_item(probs_q: Sequence[float], ratings: Sequence[int | float]) -> float:
    """Normalized individual-rating Ranked Probability Score (RPS) in [0, 1], lower is better."""
    q = validate_probs(probs_q)
    Q = np.cumsum(q)[:5]
    total = 0.0
    for y in ratings:
        yi = int(round(float(y)))
        if abs(float(y) - yi) > 1e-9 or yi < 0 or yi > 5:
            raise ValueError(f"Invalid rating {y!r}")
        ind = (np.arange(5) >= yi).astype(float)
        total += float(np.mean((Q - ind) ** 2))
    return total / float(len(ratings))


def rps_decomp(probs_q: Sequence[float], ratings: Sequence[int | float]) -> tuple[float, float, float]:
    """Return (individual_rps, cum_dist_error_D, empirical_disagreement) for one artifact."""
    q = validate_probs(probs_q)
    p = empirical_dist(ratings)
    Q = np.cumsum(q)[:5]
    F = np.cumsum(p)[:5]
    dist_err = float(np.mean((Q - F) ** 2))
    disag = float(np.mean(F * (1.0 - F)))
    return dist_err + disag, dist_err, disag


def ce_item(probs_q: Sequence[float], ratings: Sequence[int | float], floor: float = DEFAULT_CE_FLOOR) -> float:
    """Mean individual-rating cross-entropy -ln(max(q(y), floor)) in nats, lower is better."""
    q = validate_probs(probs_q)
    c = rating_counts(ratings)
    mask = c > 0
    return float(-np.sum(c[mask] * np.log(np.maximum(q[mask], floor))) / float(c.sum()))


def tvd_item(probs_q: Sequence[float], ratings: Sequence[int | float]) -> float:
    """Total variation distance 0.5 * sum_r |q(r) - p_hat(r)| computed once against p_hat."""
    q = validate_probs(probs_q)
    p = empirical_dist(ratings)
    return float(0.5 * np.sum(np.abs(q - p)))


def brier_item(probs_q: Sequence[float], ratings: Sequence[int | float]) -> float:
    """Mean 6-category individual-rating Brier score in [0, 2], lower is better."""
    q = validate_probs(probs_q)
    p = empirical_dist(ratings)
    # E[sum_r (q_r - 1{Y=r})^2] = sum_r q_r^2 - 2 sum_r p_r q_r + 1
    return float(np.sum(q * q) - 2.0 * np.sum(p * q) + 1.0)


def per_item_losses(
    probs_matrix: np.ndarray,
    rating_lists: Sequence[Sequence[int | float]],
    ce_floor: float = DEFAULT_CE_FLOOR,
) -> dict[str, np.ndarray]:
    """Compute per-artifact proper loss arrays (equal artifact weight on aggregation)."""
    n = len(rating_lists)
    if probs_matrix.shape != (n, 6):
        raise ValueError(f"Expected ({n}, 6), got {probs_matrix.shape}")
    out = {k: np.empty(n, dtype=float) for k in ("rps", "rps_dist_err", "ce", "tvd", "brier", "ev_05", "hum_mean_05")}
    for i, ratings in enumerate(rating_lists):
        q = validate_probs(probs_matrix[i])
        rps_val, dist_err, _ = rps_decomp(q, ratings)
        out["rps"][i] = rps_val
        out["rps_dist_err"][i] = dist_err
        out["ce"][i] = ce_item(q, ratings, floor=ce_floor)
        out["tvd"][i] = tvd_item(q, ratings)
        out["brier"][i] = brier_item(q, ratings)
        out["ev_05"][i] = float(np.dot(CATEGORIES, q))
        out["hum_mean_05"][i] = float(np.mean(np.asarray(ratings, dtype=float)))
    return out


def _rank_array(x: np.ndarray) -> np.ndarray:
    """Fast tie-aware average-rank helper matching scipy.stats.rankdata(method='average')."""
    n = len(x)
    order = np.argsort(x, kind="mergesort")
    xs = x[order]
    r = np.empty(n, dtype=float)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and xs[j + 1] == xs[i]:
            j += 1
        r[order[i : j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return r


def pearson_corr(x: Sequence[float], y: Sequence[float]) -> float:
    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(xa) < 3 or np.ptp(xa) == 0.0 or np.ptp(ya) == 0.0:
        return float("nan")
    xd = xa - xa.mean()
    yd = ya - ya.mean()
    denom = math.sqrt(float(np.dot(xd, xd) * np.dot(yd, yd)))
    return float(np.dot(xd, yd) / denom) if denom > 0.0 else float("nan")


def spearman_corr(x: Sequence[float], y: Sequence[float]) -> float:
    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(xa) < 3 or np.ptp(xa) == 0.0 or np.ptp(ya) == 0.0:
        return float("nan")
    return pearson_corr(_rank_array(xa), _rank_array(ya))


def kendall_corr(x: Sequence[float], y: Sequence[float]) -> float:
    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(xa) < 3 or np.ptp(xa) == 0 or np.ptp(ya) == 0:
        return float("nan")
    return float(stats.kendalltau(xa, ya).statistic)


def icc_two_way_both(x: Sequence[float], y: Sequence[float]) -> tuple[float, float]:
    """Fast single-pass two-way random single-measure (ICC(A,1), ICC(C,1)) for k=2 raters."""
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    n = len(xa)
    if n < 3:
        return (float("nan"), float("nan"))
    s = xa + ya
    d = xa - ya
    ms = float(s.mean())
    md = float(d.mean())
    msr = 0.5 * float(np.sum((s - ms) ** 2)) / float(n - 1)
    msc = 0.5 * float(n) * (md * md)
    mse = 0.5 * float(np.sum((d - md) ** 2)) / float(n - 1)
    den_c = msr + mse
    den_a = den_c + 2.0 * (msc - mse) / float(n)
    icc_a = float((msr - mse) / den_a) if den_a > 0.0 else float("nan")
    icc_c = float((msr - mse) / den_c) if den_c > 0.0 else float("nan")
    return (icc_a, icc_c)


def icc_two_way(x: Sequence[float], y: Sequence[float], kind: str) -> float:
    """Two-way random single-measure ICC(C,1) or ICC(A,1) for k=2 raters."""
    if kind not in ("A", "C"):
        return float("nan")
    icc_a, icc_c = icc_two_way_both(x, y)
    return icc_a if kind == "A" else icc_c


def quadratic_weighted_kappa(a: Sequence[int | float], b: Sequence[int | float], n_cat: int = 6) -> float:
    """Quadratic weighted Cohen's kappa over integer categories 0..n_cat-1."""
    xa = np.asarray([int(round(float(v))) for v in a], dtype=int)
    xb = np.asarray([int(round(float(v))) for v in b], dtype=int)
    if len(xa) < 2:
        return float("nan")
    O = np.zeros((n_cat, n_cat), dtype=float)
    for i, j in zip(xa, xb):
        O[i, j] += 1.0
    n = float(len(xa))
    h1 = O.sum(axis=1)
    h2 = O.sum(axis=0)
    E = np.outer(h1, h2) / n
    idx = np.arange(n_cat, dtype=float)
    W = ((idx[:, None] - idx[None, :]) ** 2) / float((n_cat - 1) ** 2)
    denom = float(np.sum(W * E))
    if denom == 0.0:
        return float("nan")
    return float(1.0 - np.sum(W * O) / denom)


def scalar_agreement_summary(judge_05: np.ndarray, human_05: np.ndarray) -> dict[str, float]:
    """Compute MAE, signed bias (judge - human), both means, ICC(A,1), ICC(C,1), and rank/linear correlations."""
    j = np.asarray(judge_05, dtype=float)
    h = np.asarray(human_05, dtype=float)
    diff = j - h
    return {
        "mae_05": float(np.mean(np.abs(diff))),
        "bias_05": float(np.mean(diff)),
        "judge_mean_05": float(np.mean(j)),
        "human_mean_05": float(np.mean(h)),
        "icc_a1": icc_two_way(j, h, "A"),
        "icc_c1": icc_two_way(j, h, "C"),
        "spearman": spearman_corr(j, h),
        "kendall": kendall_corr(j, h),
        "pearson": pearson_corr(j, h),
    }


def evaluate_forecast_panel(
    probs_matrix: np.ndarray,
    rating_lists: Sequence[Sequence[int | float]],
    judge_05: np.ndarray | None = None,
    ce_floor: float = DEFAULT_CE_FLOOR,
) -> dict[str, float]:
    """Evaluate a forecast panel against individual ratings with equal weight per artifact."""
    losses = per_item_losses(probs_matrix, rating_lists, ce_floor=ce_floor)
    j05 = losses["ev_05"] if judge_05 is None else np.asarray(judge_05, dtype=float)
    h05 = losses["hum_mean_05"]
    out = {
        "rps": float(np.mean(losses["rps"])),
        "rps_dist_err": float(np.mean(losses["rps_dist_err"])),
        "ce": float(np.mean(losses["ce"])),
        "tvd": float(np.mean(losses["tvd"])),
        "brier": float(np.mean(losses["brier"])),
    }
    out.update(scalar_agreement_summary(j05, h05))
    return out


def task_cluster_bootstrap(
    task_ids: Sequence[str],
    stat_fn: Callable[[np.ndarray], np.ndarray | float],
    draws: int = 10000,
    seed: int = 68,
) -> dict[str, object]:
    """Resample task clusters with replacement and compute 95% percentile intervals."""
    uniq = sorted(set(task_ids))
    idx_map = {t: np.array([i for i, x in enumerate(task_ids) if x == t], dtype=int) for t in uniq}
    all_idx = np.arange(len(task_ids), dtype=int)
    pt = np.asarray(stat_fn(all_idx), dtype=float)
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(draws):
        picks = rng.integers(0, len(uniq), size=len(uniq))
        ii = np.concatenate([idx_map[uniq[k]] for k in picks])
        with np.errstate(all="ignore"):
            samples.append(np.asarray(stat_fn(ii), dtype=float))
    arr = np.asarray(samples, dtype=float)
    if arr.ndim == 1:
        finite = arr[np.isfinite(arr)]
        n_finite = int(len(finite))
        lo = float(np.percentile(finite, 2.5)) if n_finite > 0 else float("nan")
        hi = float(np.percentile(finite, 97.5)) if n_finite > 0 else float("nan")
    else:
        n_finite = int(np.sum(np.isfinite(arr), axis=0).min())
        lo = np.full(arr.shape[1], float("nan"), dtype=float)
        hi = np.full(arr.shape[1], float("nan"), dtype=float)
        for col in range(arr.shape[1]):
            finite = arr[:, col][np.isfinite(arr[:, col])]
            if len(finite) > 0:
                lo[col] = float(np.percentile(finite, 2.5))
                hi[col] = float(np.percentile(finite, 97.5))
    return {
        "point": pt.tolist() if pt.ndim > 0 else float(pt),
        "ci_lo": lo.tolist() if pt.ndim > 0 else float(lo),
        "ci_hi": hi.tolist() if pt.ndim > 0 else float(hi),
        "n_tasks": len(uniq),
        "draws": draws,
        "finite_draws": n_finite,
        "seed": seed,
    }


def paired_task_signflip_p(
    task_ids: Sequence[str],
    vals_a: Sequence[float],
    vals_b: Sequence[float],
    draws: int = 10000,
    seed: int = 68,
) -> dict[str, object]:
    """Two-sided sign-flip permutation p-value over task-cluster mean differences (vals_a - vals_b).

    Uses exact enumeration over all 2^G sign assignments when G <= 12, else Monte Carlo draws.
    """
    a = np.asarray(vals_a, dtype=float)
    b = np.asarray(vals_b, dtype=float)
    tasks = sorted(set(task_ids))
    cluster_diffs = np.array([float(np.mean(a[np.asarray(task_ids) == t] - b[np.asarray(task_ids) == t])) for t in tasks])
    obs = float(np.mean(cluster_diffs))
    g = len(tasks)
    if g <= 12:
        signs = np.array(list(itertools.product([-1.0, 1.0], repeat=g)), dtype=float)
        perm_means = (signs @ cluster_diffs) / float(g)
        p_val = float(np.mean(np.abs(perm_means) >= abs(obs) - 1e-12))
        method = f"exact_task_signflip_2^{g}"
        n_perm = 2 ** g
    else:
        rng = np.random.default_rng(seed)
        signs = rng.choice([-1.0, 1.0], size=(draws, g))
        perm_means = (signs @ cluster_diffs) / float(g)
        p_val = float((1 + np.sum(np.abs(perm_means) >= abs(obs) - 1e-12)) / (draws + 1))
        method = "mc_task_signflip"
        n_perm = draws
    return {"obs_diff": obs, "p_val": p_val, "method": method, "n_clusters": g, "n_perm": n_perm}


def leave_one_rater_out_ceiling(
    rating_lists: Sequence[Sequence[int | float]],
    task_ids: Sequence[str] | None = None,
    alpha: float = 0.5,
    draws: int = 10000,
    seed: int = 68,
) -> dict[str, object]:
    """Compute item-equal leave-one-rater-out (LORO) human ceiling on RPS, CE, TVD, Brier, MAE, and Spearman.

    Only items with >= 2 ratings enter LORO; each held-out rating y_j is predicted from the remaining m-1 ratings.
    """
    eligible_idx = [i for i, r in enumerate(rating_lists) if len(r) >= 2]
    if not eligible_idx:
        return {"n_items": 0}

    per_item_smooth = {k: [] for k in ("rps", "ce", "tvd", "brier", "mae_05")}
    per_item_emp = {k: [] for k in ("rps", "tvd", "brier", "mae_05")}
    pred_means, target_means = [], []
    for i in eligible_idx:
        rats = [int(round(float(v))) for v in rating_lists[i]]
        m = len(rats)
        s_acc = {k: 0.0 for k in per_item_smooth}
        e_acc = {k: 0.0 for k in per_item_emp}
        item_pred_means = []
        for j in range(m):
            others = rats[:j] + rats[j + 1 :]
            c_other = rating_counts(others)
            q_smooth = (c_other + alpha) / float(c_other.sum() + 6.0 * alpha)
            q_emp = c_other / float(c_other.sum())
            y = rats[j]
            s_acc["rps"] += rps_item(q_smooth, [y])
            s_acc["ce"] += ce_item(q_smooth, [y])
            s_acc["tvd"] += tvd_item(q_smooth, [y])
            s_acc["brier"] += brier_item(q_smooth, [y])
            s_acc["mae_05"] += abs(float(np.dot(CATEGORIES, q_smooth)) - y)

            e_acc["rps"] += rps_item(q_emp, [y])
            e_acc["tvd"] += tvd_item(q_emp, [y])
            e_acc["brier"] += brier_item(q_emp, [y])
            e_acc["mae_05"] += abs(float(np.dot(CATEGORIES, q_emp)) - y)
            item_pred_means.append(float(np.dot(CATEGORIES, q_emp)))
        for k in per_item_smooth:
            per_item_smooth[k].append(s_acc[k] / float(m))
        for k in per_item_emp:
            per_item_emp[k].append(e_acc[k] / float(m))
        pred_means.append(float(np.mean(item_pred_means)))
        target_means.append(float(np.mean(rats)))

    # Pooled item-level LORO scalar correlation (pairs of (other_mean, heldout_rating) weighted 1/m per item)
    # Also compute exact item-level correlation between LOO expectation and item mean, plus split-half reliability if task_ids given.
    res: dict[str, object] = {
        "n_items": len(eligible_idx),
        "alpha": alpha,
        "smoothed": {k: float(np.mean(v)) for k, v in per_item_smooth.items()},
        "empirical": {k: float(np.mean(v)) for k, v in per_item_emp.items()},
    }
    # Pairwise random rater-pair expectation per item (all ordered pairs j != l within each item)
    # Using deterministic enumeration of random single-heldout draws averaged over item-weighted pairs gives exact LORO Spearman.
    rng = np.random.default_rng(seed)
    pair_x, pair_y = [], []
    # Pick 500 stratified single-rater draws per eligible item (one held-out rating vs mean of remaining)
    loro_rhos = []
    for _ in range(500):
        xs, ys = [], []
        for i in eligible_idx:
            rats = rating_lists[i]
            j = int(rng.integers(0, len(rats)))
            others = [float(rats[idx]) for idx in range(len(rats)) if idx != j]
            xs.append(float(np.mean(others)))
            ys.append(float(rats[j]))
        r = spearman_corr(xs, ys)
        if math.isfinite(r):
            loro_rhos.append(r)
    res["loro_single_draw_spearman_mean"] = float(np.mean(loro_rhos)) if loro_rhos else float("nan")
    res["loro_single_draw_spearman_p025_p975"] = (
        [float(np.percentile(loro_rhos, 2.5)), float(np.percentile(loro_rhos, 97.5))] if loro_rhos else None
    )

    if task_ids is not None:
        sub_tasks = [task_ids[i] for i in eligible_idx]
        s_arr = np.column_stack([per_item_smooth[k] for k in ("rps", "ce", "tvd", "brier", "mae_05")])
        e_arr = np.column_stack([per_item_emp[k] for k in ("rps", "tvd", "brier", "mae_05")])
        res["smoothed_ci"] = task_cluster_bootstrap(sub_tasks, lambda ii: np.mean(s_arr[ii], axis=0), draws=draws, seed=seed)
        res["empirical_ci"] = task_cluster_bootstrap(sub_tasks, lambda ii: np.mean(e_arr[ii], axis=0), draws=draws, seed=seed)
    return res


def _smooth_rows(p: np.ndarray, eps: float = 1e-3) -> np.ndarray:
    p = np.clip(p, eps, None)
    return p / p.sum(axis=1, keepdims=True)


def fit_const(train_rating_lists: Sequence[Sequence[int | float]], alpha: float = 0.5) -> Callable[[Sequence[float]], np.ndarray]:
    """Constant marginal forecast over {0..5} fitted on training ratings with Laplace smoothing."""
    c = np.sum([rating_counts(r) for r in train_rating_lists], axis=0)
    q = (c + float(alpha)) / float(c.sum() + 6.0 * float(alpha))
    return lambda scores: np.tile(q, (len(scores), 1))


def fit_ce_ordinal(
    train_scores: Sequence[float],
    train_rating_lists: Sequence[Sequence[int | float]],
    l2: float = 1e-3,
    eps: float = 1e-3,
) -> Callable[[Sequence[float]], np.ndarray]:
    """Cumulative-logit ordinal model P(H<=k|s) = sigmoid(theta_k - beta*s), MLE over individual training ratings."""
    s = np.asarray(train_scores, dtype=float)
    C = np.array([rating_counts(r) for r in train_rating_lists], dtype=float)

    def unpack(w: np.ndarray) -> tuple[np.ndarray, float]:
        th = np.cumsum(np.concatenate([[w[0]], np.exp(np.clip(w[1:5], -20.0, 20.0))]))
        return th, float(w[5])

    def nll(w: np.ndarray) -> float:
        th, b = unpack(w)
        z = np.clip(th[None, :] - b * s[:, None], -40.0, 40.0)
        cum = 1.0 / (1.0 + np.exp(-z))
        cum_full = np.concatenate([np.zeros((len(s), 1)), cum, np.ones((len(s), 1))], axis=1)
        p = np.clip(np.diff(cum_full, axis=1), 1e-9, 1.0)
        return float(-(C * np.log(p)).sum() / float(C.sum()) + l2 * b * b)

    marg = C.sum(axis=0) / float(C.sum())
    cm = np.clip(np.cumsum(marg)[:5], 1e-3, 1.0 - 1e-3)
    th0 = np.log(cm / (1.0 - cm))
    w0 = np.concatenate([[th0[0]], np.log(np.maximum(np.diff(th0), 1e-3)), [0.0]])
    opt = optimize.minimize(nll, w0, method="L-BFGS-B")
    th, b = unpack(opt.x)

    def predict(x: Sequence[float]) -> np.ndarray:
        xa = np.asarray(x, dtype=float)
        z = np.clip(th[None, :] - b * xa[:, None], -40.0, 40.0)
        cum = 1.0 / (1.0 + np.exp(-z))
        cum_full = np.concatenate([np.zeros((len(xa), 1)), cum, np.ones((len(xa), 1))], axis=1)
        return _smooth_rows(np.diff(cum_full, axis=1), eps=eps)

    return predict


def fit_pearson_gauss(
    train_scores: Sequence[float],
    train_rating_lists: Sequence[Sequence[int | float]],
    eps: float = 1e-3,
) -> Callable[[Sequence[float]], np.ndarray]:
    """OLS line for mean rating + discretized Gaussian using individual-rating training residual SD."""
    s = np.asarray(train_scores, dtype=float)
    xs = np.repeat(s, [len(r) for r in train_rating_lists])
    ys = np.concatenate([np.asarray(r, dtype=float) for r in train_rating_lists])
    if np.ptp(xs) == 0:
        a, b = float(np.mean(ys)), 0.0
    else:
        b, a = np.polyfit(xs, ys, 1)
    sd = max(float(np.std(ys - (a + b * xs))), 0.3)

    def predict(x: Sequence[float]) -> np.ndarray:
        mu = float(a) + float(b) * np.asarray(x, dtype=float)
        edges = np.arange(-0.5, 6.0, 1.0)
        cdf = stats.norm.cdf((edges[None, :] - mu[:, None]) / sd)
        p = np.diff(cdf, axis=1)
        p[:, 0] += cdf[:, 0]
        p[:, -1] += 1.0 - cdf[:, -1]
        return _smooth_rows(p, eps=eps)

    return predict


def meta_association(
    x_vals: Sequence[float],
    y_vals: Sequence[float],
    families: Sequence[str] | None = None,
    draws: int = 10000,
    seed: int = 68,
    boot_draws: int | None = None,
) -> dict[str, object]:
    """Compute judge-level Spearman/Kendall/Pearson, bootstrap 95% CI, permutation p, and family-clustered checks."""
    b_draws = draws if boot_draws is None else int(boot_draws)
    x = np.asarray(x_vals, dtype=float)
    y = np.asarray(y_vals, dtype=float)
    n = len(x)
    if n < 3:
        return {"n_units": n}
    obs_sp = spearman_corr(x, y)
    obs_kd = kendall_corr(x, y)
    obs_pe = pearson_corr(x, y)
    rng = np.random.default_rng(seed)

    # Pre-centered unit-norm rank vectors make exact & within-stratum permutations algebraically exact.
    rx = stats.rankdata(x)
    ry = stats.rankdata(y)
    rx_d = rx - rx.mean()
    ry_d = ry - ry.mean()
    nx, ny = float(np.linalg.norm(rx_d)), float(np.linalg.norm(ry_d))
    if nx == 0.0 or ny == 0.0:
        return {"n_units": n, "spearman": float("nan"), "boot_draws": b_draws, "perm_draws": draws}
    rx_c = rx_d / nx
    ry_c = ry_d / ny

    # Config bootstrap 95% CI (uses spearman_corr because bootstrap ties alter ranks)
    b_sp = []
    for _ in range(b_draws):
        idx = rng.integers(0, n, size=n)
        v = spearman_corr(x[idx], y[idx])
        if math.isfinite(v):
            b_sp.append(v)
    ci_sp = [float(np.percentile(b_sp, 2.5)), float(np.percentile(b_sp, 97.5))] if b_sp else None

    # Exact two-sided & one-sided permutation p for n <= 8, else vectorized MC draws
    if n <= 8:
        perms = np.array(list(itertools.permutations(range(n))), dtype=int)
        rs = ry_c[perms] @ rx_c
        p_two = float(np.mean(np.abs(rs) >= abs(obs_sp) - 1e-12))
        p_one = float(np.mean(rs >= obs_sp - 1e-12))
        perm_method = f"exact_{n}!"
        actual_perm_draws = int(len(perms))
    else:
        base_mat = np.broadcast_to(ry_c, (draws, n))
        perm_mat = rng.permuted(base_mat, axis=1)
        rs = perm_mat @ rx_c
        p_two = float((1 + np.sum(np.abs(rs) >= abs(obs_sp) - 1e-12)) / (draws + 1))
        p_one = float((1 + np.sum(rs >= obs_sp - 1e-12)) / (draws + 1))
        perm_method = "mc_perm"
        actual_perm_draws = int(draws)

    out: dict[str, object] = {
        "n_units": n,
        "boot_draws": b_draws,
        "perm_draws": actual_perm_draws,
        "spearman": obs_sp,
        "spearman_ci": ci_sp,
        "kendall": obs_kd,
        "pearson": obs_pe,
        "perm_p_two_sided": p_two,
        "perm_p_one_sided_pos": p_one,
        "perm_method": perm_method,
    }

    if families is not None:
        fam_arr = np.asarray(families)
        uniq_f = sorted(set(fam_arr))
        fam_idx = {f: np.where(fam_arr == f)[0] for f in uniq_f}
        out["n_families"] = len(uniq_f)
        if len(uniq_f) >= 3:
            c_sp = []
            for _ in range(b_draws):
                picks = rng.integers(0, len(uniq_f), size=len(uniq_f))
                ii = np.concatenate([fam_idx[uniq_f[k]] for k in picks])
                v = spearman_corr(x[ii], y[ii])
                if math.isfinite(v):
                    c_sp.append(v)
            out["family_cluster_ci"] = [float(np.percentile(c_sp, 2.5)), float(np.percentile(c_sp, 97.5))] if c_sp else None

        # Within-family stratified permutation p using pre-centered global ranks
        perm_strat = np.broadcast_to(ry_c, (draws, n)).copy()
        for idxs in fam_idx.values():
            if len(idxs) > 1:
                perm_strat[:, idxs] = rng.permuted(perm_strat[:, idxs], axis=1)
        rs_strat = perm_strat @ rx_c
        out["within_family_perm_p_two_sided"] = float((1 + np.sum(np.abs(rs_strat) >= abs(obs_sp) - 1e-12)) / (draws + 1))
        out["within_family_perm_p_one_sided_pos"] = float((1 + np.sum(rs_strat >= obs_sp - 1e-12)) / (draws + 1))

    return out
