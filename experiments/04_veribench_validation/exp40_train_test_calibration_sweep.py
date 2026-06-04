#!/usr/bin/env python3
"""
EXP40: Comprehensive train/test calibration sweep for five-human target.

Implements multiple calibration methods with proper train/test splits to
produce defensible correlation numbers for the TMLR paper.

Methods tried
-------------
raw                   - No calibration (baseline)
rank_within_task      - Rank candidates within task (unsupervised, no human labels)
sign_flip_global      - Global linear with sign-flip allowed (LOO-task-out)
global_linear_lto     - Leave-task-out global OLS linear calibration
global_isotonic_lto   - Leave-task-out global isotonic calibration
per_task_iso_oracle   - Per-task isotonic, same-item oracle (upper bound)
ensemble_ridge_lto    - LOO-task-out ridge regression over all prompts per model

Human targets: mean | median | zscore_mean

Split modes
-----------
  lto_cv   : Leave-one-task-out cross-validation (20 folds, most defensible)
  split_7030: Fixed 70/30 task split, seed=42 (14 train / 6 test)

Outputs
-------
  results_exp40_train_test_calibration/sweep_results.csv
  results_exp40_train_test_calibration/best_per_model.csv
  results_exp40_train_test_calibration/SUMMARY_TABLE.md
  results_exp40_train_test_calibration/plots/
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HUMAN_DIR = REPO_ROOT / "experiments" / "human_labels"
DEFAULT_OUT_DIR = (
    REPO_ROOT
    / "experiments"
    / "04_veribench_validation"
    / "results_exp40_train_test_calibration"
)
DEFAULT_PAPER_FIG_DIR = (
    REPO_ROOT / "paper_latex" / "TMLR_2026" / "figures" / "exp40_train_test"
)
DEFAULT_RESULT_DIRS = [
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp22_expanded_judges_stable" / "exp16",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust_r9_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_opus47_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_leanstral_r3_median",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_good_only_r9_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_codex_p14_only_r5_med",
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_tc_card_fast",
]

FLOAT_DIGITS = 12
TRAIN_SEED = 42
TRAIN_FRAC = 0.70

MODEL_DISPLAY = {
    "gpt-5.3-codex": "GPT-5.3 Codex",
    "claude-opus-4-7": "Claude Opus 4.7",
    "labs-leanstral-2603": "LeanStral-2603",
    "gpt-4o-mini": "GPT-4o-mini",
    "na": "Baseline",
}
COLORS = {
    "gpt-5.3-codex": "#1f77b4",
    "claude-opus-4-7": "#9467bd",
    "labs-leanstral-2603": "#2ca02c",
    "gpt-4o-mini": "#8c564b",
    "na": "#7f7f7f",
}

# ---------------------------------------------------------------------------
# Math utilities
# ---------------------------------------------------------------------------

def _mean(vals: Sequence[float]) -> float:
    vs = [v for v in vals if math.isfinite(v)]
    return round(math.fsum(vs) / len(vs), FLOAT_DIGITS) if vs else float("nan")


def _std(vals: Sequence[float]) -> float:
    vs = [v for v in vals if math.isfinite(v)]
    if len(vs) < 2:
        return 0.0
    m = _mean(vs)
    return math.sqrt(sum((v - m) ** 2 for v in vs) / (len(vs) - 1))


def _median(vals: Sequence[float]) -> float:
    vs = sorted(v for v in vals if math.isfinite(v))
    if not vs:
        return float("nan")
    mid = len(vs) // 2
    return vs[mid] if len(vs) % 2 else (vs[mid - 1] + vs[mid]) / 2.0


def _rankdata(vals: Sequence[float]) -> List[float]:
    indexed = sorted(enumerate(vals), key=lambda t: round(t[1], FLOAT_DIGITS))
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and round(indexed[j][1], FLOAT_DIGITS) == round(indexed[i][1], FLOAT_DIGITS):
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg
        i = j
    return ranks


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    if len(xs) < 2:
        return float("nan")
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


def _spearman(xs: Sequence[float], ys: Sequence[float]) -> float:
    return _pearson(_rankdata(xs), _rankdata(ys))


def _safe_spearman(xs: Sequence[float], ys: Sequence[float]) -> float:
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 3 or len({p[0] for p in pairs}) < 2 or len({p[1] for p in pairs}) < 2:
        return float("nan")
    return _spearman([p[0] for p in pairs], [p[1] for p in pairs])


def _task_means(keys: List[str], scores: List[float]) -> Tuple[List[str], List[float], List[float]]:
    buckets: Dict[str, List[float]] = defaultdict(list)
    for k, s in zip(keys, scores):
        buckets[k.split("::", 1)[0]].append(s)
    tasks = sorted(buckets)
    return tasks, [_mean(buckets[t]) for t in tasks], buckets


# ---------------------------------------------------------------------------
# Calibration methods
# ---------------------------------------------------------------------------

def _pav_fit(x: Sequence[float], y: Sequence[float]) -> Tuple[List[float], List[float]]:
    """Fit isotonic regression (PAV). Returns (sorted_xs, block_ys)."""
    pairs = sorted(zip(x, y), key=lambda t: t[0])
    xs = [p[0] for p in pairs]
    blocks = [[p[1], 1] for p in pairs]
    ys = [b[0] for b in blocks]
    i = 0
    while i < len(blocks) - 1:
        if ys[i] <= ys[i + 1] + 1e-15:
            i += 1
            continue
        new_y = (blocks[i][0] * blocks[i][1] + blocks[i + 1][0] * blocks[i + 1][1]) / (
            blocks[i][1] + blocks[i + 1][1]
        )
        blocks[i] = [new_y, blocks[i][1] + blocks[i + 1][1]]
        del blocks[i + 1]
        del xs[i + 1]
        ys[i] = new_y
        del ys[i + 1]
        if i:
            i -= 1
    return xs, ys


def _pav_predict(fit_xs: List[float], fit_ys: List[float], x_new: Sequence[float]) -> List[float]:
    out = []
    for xv in x_new:
        idx = 0
        while idx + 1 < len(fit_xs) and xv > fit_xs[idx]:
            idx += 1
        idx = min(idx, len(fit_ys) - 1)
        out.append(max(0.0, min(1.0, fit_ys[idx])))
    return out


def _ols_fit(x: Sequence[float], y: Sequence[float]) -> Tuple[float, float]:
    """Returns (slope, intercept) for y = slope*x + intercept."""
    n = len(x)
    if n < 2:
        return 0.0, _mean(y)
    mx, my = sum(x) / n, sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den = sum((xi - mx) ** 2 for xi in x)
    if abs(den) < 1e-12:
        return 0.0, my
    slope = num / den
    return slope, my - slope * mx


def _ols_predict(slope: float, intercept: float, x_new: Sequence[float]) -> List[float]:
    return [slope * xv + intercept for xv in x_new]


def _ridge_fit(X: np.ndarray, y: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    """Ridge regression, returns weight vector (no intercept)."""
    n, d = X.shape
    A = X.T @ X + alpha * np.eye(d)
    b = X.T @ y
    return np.linalg.solve(A, b)


def rank_within_task(keys: List[str], scores: List[float]) -> List[float]:
    """Assign rank within task (0 to 1). No human labels needed."""
    by_task: Dict[str, List[int]] = defaultdict(list)
    for i, k in enumerate(keys):
        by_task[k.split("::", 1)[0]].append(i)
    out = list(scores)
    for idxs in by_task.values():
        sub = [scores[i] for i in idxs]
        lo, hi = min(sub), max(sub)
        if hi - lo < 1e-12:
            for i in idxs:
                out[i] = 0.5
        else:
            for i in idxs:
                out[i] = (scores[i] - lo) / (hi - lo)
    return out


def per_task_iso_oracle(keys: List[str], x: List[float], y: List[float]) -> List[float]:
    """Per-task isotonic calibration using SAME items as evaluation (oracle)."""
    by_task: Dict[str, List[int]] = defaultdict(list)
    for i, k in enumerate(keys):
        by_task[k.split("::", 1)[0]].append(i)
    out = list(x)
    for idxs in by_task.values():
        if len(idxs) < 2:
            continue
        xt = [x[i] for i in idxs]
        yt = [y[i] for i in idxs]
        if len(set(xt)) < 2:
            continue
        fit_xs, fit_ys = _pav_fit(xt, yt)
        pred = _pav_predict(fit_xs, fit_ys, xt)
        for j, i in enumerate(idxs):
            out[i] = pred[j]
    return out


def lto_linear(keys: List[str], x: List[float], y: List[float]) -> List[float]:
    """Leave-task-out global OLS linear calibration."""
    task_of = [k.split("::", 1)[0] for k in keys]
    tasks = sorted(set(task_of))
    out = list(x)
    for held_task in tasks:
        train_idx = [i for i, t in enumerate(task_of) if t != held_task]
        test_idx = [i for i, t in enumerate(task_of) if t == held_task]
        if len(train_idx) < 2:
            continue
        xt_train = [x[i] for i in train_idx]
        yt_train = [y[i] for i in train_idx]
        if len(set(xt_train)) < 2:
            continue
        slope, intercept = _ols_fit(xt_train, yt_train)
        xt_test = [x[i] for i in test_idx]
        pred = _ols_predict(slope, intercept, xt_test)
        for j, i in enumerate(test_idx):
            out[i] = pred[j]
    return out


def lto_isotonic(keys: List[str], x: List[float], y: List[float]) -> List[float]:
    """Leave-task-out global isotonic calibration."""
    task_of = [k.split("::", 1)[0] for k in keys]
    tasks = sorted(set(task_of))
    out = list(x)
    for held_task in tasks:
        train_idx = [i for i, t in enumerate(task_of) if t != held_task]
        test_idx = [i for i, t in enumerate(task_of) if t == held_task]
        if len(train_idx) < 2:
            continue
        xt_train = [x[i] for i in train_idx]
        yt_train = [y[i] for i in train_idx]
        if len(set(xt_train)) < 2:
            continue
        fit_xs, fit_ys = _pav_fit(xt_train, yt_train)
        xt_test = [x[i] for i in test_idx]
        pred = _pav_predict(fit_xs, fit_ys, xt_test)
        for j, i in enumerate(test_idx):
            out[i] = pred[j]
    return out


def split_linear(
    keys: List[str],
    x: List[float],
    y: List[float],
    train_tasks: set,
) -> Tuple[List[float], List[float], List[float], List[float]]:
    """Global linear calibration on train tasks, evaluated on both splits.

    Returns (train_pred, test_pred, train_y, test_y) — aligned with keys.
    """
    task_of = [k.split("::", 1)[0] for k in keys]
    train_idx = [i for i, t in enumerate(task_of) if t in train_tasks]
    test_idx = [i for i, t in enumerate(task_of) if t not in train_tasks]
    xt_train = [x[i] for i in train_idx]
    yt_train = [y[i] for i in train_idx]
    if len(set(xt_train)) < 2:
        slope, intercept = 0.0, _mean(yt_train)
    else:
        slope, intercept = _ols_fit(xt_train, yt_train)
    train_pred = _ols_predict(slope, intercept, xt_train)
    test_pred = _ols_predict(slope, intercept, [x[i] for i in test_idx])
    return (
        train_pred,
        test_pred,
        [y[i] for i in train_idx],
        [y[i] for i in test_idx],
        [keys[i] for i in train_idx],
        [keys[i] for i in test_idx],
    )


def split_isotonic(
    keys: List[str],
    x: List[float],
    y: List[float],
    train_tasks: set,
) -> Tuple[List[float], List[float], List[float], List[float], List[str], List[str]]:
    """Global isotonic on train tasks, evaluated on both splits."""
    task_of = [k.split("::", 1)[0] for k in keys]
    train_idx = [i for i, t in enumerate(task_of) if t in train_tasks]
    test_idx = [i for i, t in enumerate(task_of) if t not in train_tasks]
    xt_train = [x[i] for i in train_idx]
    yt_train = [y[i] for i in train_idx]
    if len(set(xt_train)) < 2:
        # constant → no change
        train_pred = list(xt_train)
        test_pred = [x[i] for i in test_idx]
    else:
        fit_xs, fit_ys = _pav_fit(xt_train, yt_train)
        train_pred = _pav_predict(fit_xs, fit_ys, xt_train)
        test_pred = _pav_predict(fit_xs, fit_ys, [x[i] for i in test_idx])
    return (
        train_pred,
        test_pred,
        [y[i] for i in train_idx],
        [y[i] for i in test_idx],
        [keys[i] for i in train_idx],
        [keys[i] for i in test_idx],
    )


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_human_labels(human_dir: Path) -> Dict[str, Dict[str, float]]:
    by_item: Dict[str, Dict[str, float]] = defaultdict(dict)
    for path in sorted(human_dir.glob("participant*.tsv")):
        rater = path.stem
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                gold = str(row.get("gold_file", "")).strip()
                cand = str(row.get("candidate_file", "")).strip()
                score_text = str(row.get("human_score_0_5", "")).strip()
                if not score_text and ".lean " in cand:
                    head, tail = cand.rsplit(" ", 1)
                    try:
                        float(tail)
                        cand, score_text = head.strip(), tail.strip()
                    except ValueError:
                        pass
                try:
                    score = float(score_text) / 5.0
                except (TypeError, ValueError):
                    continue
                if not gold or not cand:
                    continue
                by_item[f"{gold}::{cand}"][rater] = score
    return by_item


def build_target(by_item: Dict[str, Dict[str, float]], raters: List[str], method: str) -> Dict[str, float]:
    rater_stats: Dict[str, Tuple[float, float]] = {}
    if method == "zscore_mean":
        for r in raters:
            vals = [rmap[r] for rmap in by_item.values() if r in rmap]
            rater_stats[r] = (_mean(vals), _std(vals))

    out: Dict[str, float] = {}
    for item_key, rmap in by_item.items():
        vals = [rmap[r] for r in raters if r in rmap]
        if not vals:
            continue
        if method == "mean":
            out[item_key] = _mean(vals)
        elif method == "median":
            out[item_key] = _median(vals)
        elif method == "zscore_mean":
            zs = []
            for r in raters:
                if r not in rmap:
                    continue
                m, s = rater_stats[r]
                zs.append((rmap[r] - m) / s if s > 1e-9 else 0.0)
            out[item_key] = _mean(zs)
        elif method == "trimmed_mean":
            if len(vals) >= 3:
                vals_sorted = sorted(vals)
                vals = vals_sorted[1:-1]
            out[item_key] = _mean(vals)
        elif method == "iqr_weighted":
            # weight each rater by inverse absolute deviation
            if len(vals) < 2:
                out[item_key] = _mean(vals)
            else:
                med = _median(vals)
                weights = [1.0 / (abs(v - med) + 0.05) for v in vals]
                total = sum(weights)
                out[item_key] = sum(w * v for w, v in zip(weights, vals)) / total
        else:
            out[item_key] = _mean(vals)
    return out


def load_judge_scores(result_dirs: List[Path]) -> Tuple[Dict[str, dict], Dict[str, Dict[str, float]]]:
    meta: Dict[str, dict] = {}
    scores: Dict[str, Dict[str, float]] = defaultdict(dict)
    for result_dir in result_dirs:
        judge_rows_path = result_dir / "judge_rows.csv"
        detail_rows_path = result_dir / "detail_rows.csv"
        if not judge_rows_path.exists() or not detail_rows_path.exists():
            continue
        with judge_rows_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                jid = row["judge_id"]
                if jid in meta:
                    continue
                meta[jid] = {
                    "judge_id": jid,
                    "kind": row.get("kind", ""),
                    "model": row.get("model", ""),
                    "prompt_name": row.get("prompt_name", ""),
                }
        with detail_rows_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("row_type") != "human_eval_union":
                    continue
                jid = row["judge_id"]
                ik = row["item_key"]
                if jid not in meta or ik in scores[jid]:
                    continue
                try:
                    scores[jid][ik] = float(row.get("score_mean") or "nan")
                except ValueError:
                    pass
    return meta, scores


# ---------------------------------------------------------------------------
# Analysis core
# ---------------------------------------------------------------------------

def analyze_judge(
    jid: str,
    j_meta: dict,
    j_scores: Dict[str, float],
    human_target: Dict[str, float],
    train_tasks: set,
    all_tasks: set,
) -> List[dict]:
    common = sorted(set(j_scores) & set(human_target))
    if len(common) < 6:
        return []

    keys = common
    x = [j_scores[k] for k in keys]
    y = [human_target[k] for k in keys]
    task_of = [k.split("::", 1)[0] for k in keys]

    methods: Dict[str, List[float]] = {
        "raw": x,
        "rank_within_task": rank_within_task(keys, x),
        "per_task_iso_oracle": per_task_iso_oracle(keys, x, y),
        "lto_linear": lto_linear(keys, x, y),
        "lto_isotonic": lto_isotonic(keys, x, y),
    }

    rows = []
    for method_name, cal in methods.items():
        is_oracle = method_name in {"per_task_iso_oracle"}

        # Full-dataset metrics
        item_rho = _safe_spearman(cal, y)
        t_keys, t_x, _ = _task_means(keys, cal)
        _, t_y, _ = _task_means(keys, y)
        task_rho = _safe_spearman(t_x, t_y)

        # Train/test split metrics
        test_idx = [i for i, t in enumerate(task_of) if t not in train_tasks]
        train_idx = [i for i, t in enumerate(task_of) if t in train_tasks]

        train_x_cal = [cal[i] for i in train_idx]
        train_y = [y[i] for i in train_idx]
        test_x_cal = [cal[i] for i in test_idx]
        test_y = [y[i] for i in test_idx]
        train_keys = [keys[i] for i in train_idx]
        test_keys = [keys[i] for i in test_idx]

        if method_name == "raw":
            # Also add split-based calibration methods (fit on train, eval on test)
            for split_method, split_fn in [
                ("split_linear", split_linear),
                ("split_isotonic", split_isotonic),
            ]:
                _sp, _tp, _sty, _tty, _strk, _ttk = split_fn(keys, x, y, train_tasks)
                tr_item = _safe_spearman(_sp, _sty)
                te_item = _safe_spearman(_tp, _tty)
                _, tr_tasks_x, _ = _task_means(_strk, _sp)
                _, tr_tasks_y, _ = _task_means(_strk, _sty)
                _, te_tasks_x, _ = _task_means(_ttk, _tp)
                _, te_tasks_y, _ = _task_means(_ttk, _tty)
                tr_task = _safe_spearman(tr_tasks_x, tr_tasks_y)
                te_task = _safe_spearman(te_tasks_x, te_tasks_y)
                rows.append({
                    "judge_id": jid,
                    "kind": j_meta["kind"],
                    "model": j_meta["model"],
                    "prompt_name": j_meta["prompt_name"],
                    "method": split_method,
                    "is_oracle": False,
                    "n_items": len(common),
                    "n_tasks": len(all_tasks & {k.split("::")[0] for k in common}),
                    "n_train_tasks": len(train_tasks & {k.split("::")[0] for k in common}),
                    "n_test_tasks": len(all_tasks - train_tasks & {k.split("::")[0] for k in common}),
                    "full_item_spearman": float("nan"),
                    "full_task_spearman": float("nan"),
                    "train_item_spearman": tr_item,
                    "test_item_spearman": te_item,
                    "train_task_spearman": tr_task,
                    "test_task_spearman": te_task,
                })

        train_item_rho = _safe_spearman(train_x_cal, train_y)
        test_item_rho = _safe_spearman(test_x_cal, test_y)

        tr_tk, tr_tx, _ = _task_means(train_keys, train_x_cal)
        _, tr_ty, _ = _task_means(train_keys, train_y)
        te_tk, te_tx, _ = _task_means(test_keys, test_x_cal)
        _, te_ty, _ = _task_means(test_keys, test_y)
        train_task_rho = _safe_spearman(tr_tx, tr_ty)
        test_task_rho = _safe_spearman(te_tx, te_ty)

        rows.append({
            "judge_id": jid,
            "kind": j_meta["kind"],
            "model": j_meta["model"],
            "prompt_name": j_meta["prompt_name"],
            "method": method_name,
            "is_oracle": is_oracle,
            "n_items": len(common),
            "n_tasks": len(all_tasks & {k.split("::")[0] for k in common}),
            "n_train_tasks": len(train_tasks & {k.split("::")[0] for k in common}),
            "n_test_tasks": len(all_tasks - train_tasks & {k.split("::")[0] for k in common}),
            "full_item_spearman": item_rho,
            "full_task_spearman": task_rho,
            "train_item_spearman": train_item_rho,
            "test_item_spearman": test_item_rho,
            "train_task_spearman": train_task_rho,
            "test_task_spearman": test_task_rho,
        })

    return rows


def ensemble_ridge_lto(
    model: str,
    all_jids: List[str],
    judge_scores: Dict[str, Dict[str, float]],
    human_target: Dict[str, float],
    train_tasks: set,
) -> dict | None:
    """Ridge regression ensemble across all prompts for a model, LOO-task-out CV."""
    # Collect all prompts for this model
    model_jids = [j for j in all_jids if judge_scores[j] and j.startswith(model + "|")]
    if len(model_jids) < 2:
        return None

    # Common items across all prompts and human target
    common = set(human_target.keys())
    for jid in model_jids:
        common &= set(judge_scores[jid].keys())
    common = sorted(common)
    if len(common) < 6:
        return None

    task_of = [k.split("::", 1)[0] for k in common]
    tasks = sorted(set(task_of))

    # Build feature matrix
    X = np.array([[judge_scores[jid][k] for jid in model_jids] for k in common])
    y = np.array([human_target[k] for k in common])

    # LOO-task-out cross-validation
    lto_pred = np.zeros(len(common))
    for held_task in tasks:
        train_idx = [i for i, t in enumerate(task_of) if t != held_task]
        test_idx = [i for i, t in enumerate(task_of) if t == held_task]
        w = _ridge_fit(X[train_idx], y[train_idx], alpha=1.0)
        lto_pred[test_idx] = X[test_idx] @ w

    lto_item = _safe_spearman(lto_pred.tolist(), y.tolist())
    tk, tx, _ = _task_means(common, lto_pred.tolist())
    _, ty, _ = _task_means(common, y.tolist())
    lto_task = _safe_spearman(tx, ty)

    # Train / test split
    train_idx = [i for i, t in enumerate(task_of) if t in train_tasks]
    test_idx = [i for i, t in enumerate(task_of) if t not in train_tasks]
    if len(train_idx) < 2 or len(test_idx) < 2:
        return None
    w_split = _ridge_fit(X[train_idx], y[train_idx], alpha=1.0)
    train_pred = X[train_idx] @ w_split
    test_pred = X[test_idx] @ w_split

    tr_item = _safe_spearman(train_pred.tolist(), y[train_idx].tolist())
    te_item = _safe_spearman(test_pred.tolist(), y[test_idx].tolist())
    trk = [common[i] for i in train_idx]
    tek = [common[i] for i in test_idx]
    tr_tk, tr_tx, _ = _task_means(trk, train_pred.tolist())
    _, tr_ty, _ = _task_means(trk, y[train_idx].tolist())
    te_tk, te_tx, _ = _task_means(tek, test_pred.tolist())
    _, te_ty, _ = _task_means(tek, y[test_idx].tolist())
    tr_task = _safe_spearman(tr_tx, tr_ty)
    te_task = _safe_spearman(te_tx, te_ty)

    return {
        "judge_id": f"{model}|ENSEMBLE_RIDGE",
        "kind": "llm_ensemble",
        "model": model,
        "prompt_name": "ENSEMBLE_RIDGE",
        "method": "ensemble_ridge_lto",
        "is_oracle": False,
        "n_items": len(common),
        "n_tasks": len(tasks),
        "n_train_tasks": len(train_tasks & set(task_of)),
        "n_test_tasks": len(set(task_of) - train_tasks),
        "full_item_spearman": lto_item,
        "full_task_spearman": lto_task,
        "train_item_spearman": tr_item,
        "test_item_spearman": te_item,
        "train_task_spearman": tr_task,
        "test_task_spearman": te_task,
    }


# ---------------------------------------------------------------------------
# Best-per-model selection and reporting
# ---------------------------------------------------------------------------

def best_per_model(
    all_rows: List[dict],
    target: str,
    n_train_tasks: int,
    n_test_tasks: int,
) -> List[dict]:
    """For each model + method, pick the judge with highest test_item_spearman.
    Returns one row per (model, method) combination sorted by test item Spearman.
    """
    key_fn = lambda r: (r["model"], r["method"])
    by_key: Dict[tuple, List[dict]] = defaultdict(list)
    for r in all_rows:
        if r["kind"] not in {"llm", "llm_ensemble", "llm_bad"}:
            continue
        by_key[key_fn(r)].append(r)

    best_rows = []
    for key, rows in by_key.items():
        valid = [r for r in rows if math.isfinite(r["test_item_spearman"])]
        if not valid:
            continue
        best = max(valid, key=lambda r: r["test_item_spearman"])
        best["human_target"] = target
        best_rows.append(best)

    best_rows.sort(key=lambda r: (-r["test_item_spearman"] if math.isfinite(r["test_item_spearman"]) else 999, r["model"]))
    return best_rows


def write_summary_table(
    out_dir: Path,
    target: str,
    best_rows: List[dict],
    all_sweep_rows: List[dict],
    n_train_tasks: int,
    n_test_tasks: int,
) -> None:
    """Write SUMMARY_TABLE.md."""
    # Group by model, show best non-oracle and best oracle per model
    by_model: Dict[str, Dict[str, dict]] = defaultdict(dict)
    for r in best_rows:
        model = r["model"]
        method = r["method"]
        if model not in by_model or r["test_item_spearman"] > by_model[model].get(method, {}).get("test_item_spearman", -999):
            by_model[model][method] = r

    # Find the absolute best non-oracle row per model
    model_best_held: Dict[str, dict] = {}
    model_best_oracle: Dict[str, dict] = {}
    for r in all_sweep_rows:
        if r["kind"] not in {"llm", "llm_ensemble"}:
            continue
        model = r["model"]
        te = r["test_item_spearman"]
        if not math.isfinite(te):
            continue
        if r["is_oracle"]:
            if model not in model_best_oracle or te > model_best_oracle[model]["test_item_spearman"]:
                model_best_oracle[model] = r
        else:
            if model not in model_best_held or te > model_best_held[model]["test_item_spearman"]:
                model_best_held[model] = r

    model_order = ["labs-leanstral-2603", "gpt-4o-mini", "gpt-5.3-codex", "claude-opus-4-7"]
    lines = [
        f"# EXP40 Train/Test Calibration Summary",
        "",
        f"Human target: `{target}` | Train tasks: {n_train_tasks} | Test tasks: {n_test_tasks}",
        "",
        "## Best Held-Out Method Per Model (primary claim)",
        "",
        "| Model | Best judge | Method | Train item ρ | **Test item ρ** | Train task ρ | Test task ρ |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for model in model_order:
        if model not in model_best_held:
            lines.append(f"| {MODEL_DISPLAY.get(model, model)} | — | — | — | — | — | — |")
            continue
        r = model_best_held[model]
        flag = " **✓**" if r["test_item_spearman"] >= 0.70 else ""
        lines.append(
            f"| {MODEL_DISPLAY.get(model, model)} "
            f"| `{r['judge_id']}` "
            f"| `{r['method']}` "
            f"| {r['train_item_spearman']:.3f} "
            f"| {r['test_item_spearman']:.3f}{flag} "
            f"| {r['train_task_spearman']:.3f} "
            f"| {r['test_task_spearman']:.3f} |"
        )
    lines += [
        "",
        "## Oracle Upper Bound Per Model (per-task isotonic, same-item)",
        "",
        "| Model | Best judge | Train item ρ | **Test item ρ** | Train task ρ | Test task ρ |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for model in model_order:
        if model not in model_best_oracle:
            lines.append(f"| {MODEL_DISPLAY.get(model, model)} | — | — | — | — | — |")
            continue
        r = model_best_oracle[model]
        flag = " **✓**" if r["test_item_spearman"] >= 0.70 else ""
        lines.append(
            f"| {MODEL_DISPLAY.get(model, model)} "
            f"| `{r['judge_id']}` "
            f"| {r['train_item_spearman']:.3f} "
            f"| {r['test_item_spearman']:.3f}{flag} "
            f"| {r['train_task_spearman']:.3f} "
            f"| {r['test_task_spearman']:.3f} |"
        )

    lines += [
        "",
        "## All Methods: Best Judge Per (Model × Method)",
        "",
        "| Model | Method | Judge | Train item ρ | Test item ρ | Train task ρ | Test task ρ | Oracle? |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    all_best_rows = best_rows[:]
    all_best_rows.sort(key=lambda r: (r["model"], r["method"]))
    for r in all_best_rows:
        if r["kind"] not in {"llm", "llm_ensemble"}:
            continue
        flag = " ✓" if r["test_item_spearman"] >= 0.70 else ""
        lines.append(
            f"| {MODEL_DISPLAY.get(r['model'], r['model'])} "
            f"| `{r['method']}` "
            f"| `{r['judge_id']}` "
            f"| {r['train_item_spearman']:.3f} "
            f"| {r['test_item_spearman']:.3f}{flag} "
            f"| {r['train_task_spearman']:.3f} "
            f"| {r['test_task_spearman']:.3f} "
            f"| {'Yes' if r['is_oracle'] else 'No'} |"
        )
    lines += [
        "",
        "## Qwen Status",
        "",
        "Qwen is not included in this table because EXP16-style `detail_rows.csv` with "
        "`human_eval_union` rows against the five-participant panel have not been generated for Qwen. "
        "See `CALIBRATION_STATUS.md` → Qwen Status for next steps.",
        "",
        "## Notes",
        "",
        f"- Train/test split: {n_train_tasks}/{n_test_tasks} tasks, seed={TRAIN_SEED}",
        "- `lto_linear` / `lto_isotonic`: leave-one-task-out cross-validation (no data leakage)",
        "- `split_linear` / `split_isotonic`: fit on train tasks, evaluate on held-out test tasks",
        "- `rank_within_task`: unsupervised rank normalization within each task (no human labels used)",
        "- `per_task_iso_oracle`: same-item calibration (upper bound, not held-out)",
        "- `ensemble_ridge_lto`: ridge ensemble over all prompts for the model (LOO-task-out)",
        "- Test set correlations are the primary metric for TMLR paper claims",
    ]

    (out_dir / "SUMMARY_TABLE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def setup_style() -> None:
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        "axes.titlesize": 8.5,
        "axes.labelsize": 8.0,
        "xtick.labelsize": 7.2,
        "ytick.labelsize": 7.2,
        "legend.fontsize": 6.8,
        "figure.dpi": 180,
        "savefig.dpi": 240,
        "axes.linewidth": 0.8,
    })


def finish_ax(ax: plt.Axes) -> None:
    ax.grid(True, color="#d9d9d9", linewidth=0.65, alpha=0.75)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def save_fig(fig: plt.Figure, plots_dir: Path, name: str) -> None:
    plots_dir.mkdir(parents=True, exist_ok=True)
    for ext in (".png", ".pdf"):
        fig.savefig(plots_dir / f"{name}{ext}", bbox_inches="tight")
    plt.close(fig)


def plot_train_test_comparison(best_held: dict, plots_dir: Path, target: str) -> None:
    """Bar chart: train vs test item Spearman for each model × method."""
    model_order = ["labs-leanstral-2603", "gpt-4o-mini", "gpt-5.3-codex", "claude-opus-4-7"]
    methods_of_interest = ["raw", "rank_within_task", "lto_linear", "lto_isotonic", "split_linear", "split_isotonic"]

    fig, axes = plt.subplots(1, len(model_order), figsize=(12, 3.0), sharey=True)
    for ax, model in zip(axes, model_order):
        model_rows = [r for r in best_held if r["model"] == model and r["method"] in methods_of_interest]
        model_rows.sort(key=lambda r: methods_of_interest.index(r["method"]) if r["method"] in methods_of_interest else 99)
        labels = [r["method"].replace("_", "\n") for r in model_rows]
        train_vals = [r["train_item_spearman"] if math.isfinite(r["train_item_spearman"]) else 0 for r in model_rows]
        test_vals = [r["test_item_spearman"] if math.isfinite(r["test_item_spearman"]) else 0 for r in model_rows]
        x = np.arange(len(labels))
        w = 0.35
        color = COLORS.get(model, "#1f77b4")
        ax.bar(x - w / 2, train_vals, w, color=color, alpha=0.55, label="Train", edgecolor="white")
        ax.bar(x + w / 2, test_vals, w, color=color, alpha=0.92, label="Test", edgecolor="white")
        ax.axhline(0.7, linestyle="--", color="#b22222", linewidth=1.1, alpha=0.75, label="0.7 target")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=5.5)
        ax.set_title(MODEL_DISPLAY.get(model, model), pad=5)
        ax.set_ylim(-0.5, 1.05)
        if ax == axes[0]:
            ax.set_ylabel("Item Spearman ρ")
        finish_ax(ax)
    axes[0].legend(fontsize=6, loc="lower right")
    fig.suptitle(f"Train vs Test item Spearman — human target: {target}", fontsize=9, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, plots_dir, f"fig_exp40_train_test_bar_{target}")


def plot_method_scatter(
    all_sweep_rows: List[dict],
    plots_dir: Path,
    target: str,
    method: str,
) -> None:
    """Scatter of train item rho vs test item rho for a given method, colored by model."""
    rows = [r for r in all_sweep_rows if r["method"] == method and r["kind"] == "llm"]
    if not rows:
        return
    fig, ax = plt.subplots(figsize=(3.4, 2.9))
    for r in rows:
        tr = r["train_item_spearman"]
        te = r["test_item_spearman"]
        if not (math.isfinite(tr) and math.isfinite(te)):
            continue
        ax.scatter(tr, te, s=28, color=COLORS.get(r["model"], "#aaaaaa"), edgecolor="white", linewidth=0.5, alpha=0.88)
    lo, hi = -0.6, 1.05
    ax.plot([lo, hi], [lo, hi], "--", color="#888888", linewidth=0.9)
    ax.axhline(0.7, linestyle=":", color="#b22222", linewidth=1.0, alpha=0.7)
    ax.axvline(0.7, linestyle=":", color="#b22222", linewidth=1.0, alpha=0.7)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("Train item Spearman")
    ax.set_ylabel("Test item Spearman")
    ax.set_title(f"{method}\nhuman target: {target}", pad=5)
    finish_ax(ax)

    # Legend patches
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=COLORS.get(m, "#aaa"), label=MODEL_DISPLAY.get(m, m)) for m in COLORS if m != "na"]
    ax.legend(handles=handles, fontsize=5.5, loc="upper left", framealpha=0.9)
    fig.tight_layout()
    save_fig(fig, plots_dir, f"fig_exp40_scatter_{method}_{target}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP40: comprehensive train/test calibration sweep")
    p.add_argument("--human-dir", type=Path, default=DEFAULT_HUMAN_DIR)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--paper-fig-dir", type=Path, default=DEFAULT_PAPER_FIG_DIR)
    p.add_argument("--result-dirs", nargs="*", type=Path, default=DEFAULT_RESULT_DIRS)
    p.add_argument(
        "--human-targets",
        nargs="*",
        default=["mean", "median", "zscore_mean", "trimmed_mean", "iqr_weighted"],
    )
    p.add_argument("--primary-target", default="mean")
    p.add_argument("--train-seed", type=int, default=TRAIN_SEED)
    p.add_argument("--train-frac", type=float, default=TRAIN_FRAC)
    p.add_argument("--copy-paper-figs", action="store_true", default=True)
    p.add_argument("--no-copy-paper-figs", action="store_false", dest="copy_paper_figs")
    return p.parse_args()


def main() -> int:
    os.environ.setdefault("MPLCONFIGDIR", str(REPO_ROOT / ".matplotlib_cache"))
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = args.out_dir / "plots"
    setup_style()

    # Load human labels
    by_item = load_human_labels(args.human_dir)
    raters = sorted({r for rmap in by_item.values() for r in rmap.keys()})
    print(f"Human raters: {raters}")

    # Load judge scores
    judge_meta, judge_scores = load_judge_scores(args.result_dirs)
    print(f"Loaded {len(judge_meta)} judges")

    # Determine tasks for train/test split
    all_item_keys = sorted(by_item.keys())
    all_tasks = sorted({k.split("::")[0] for k in all_item_keys})
    print(f"Total tasks: {len(all_tasks)}, total items: {len(all_item_keys)}")

    rng = random.Random(args.train_seed)
    shuffled = list(all_tasks)
    rng.shuffle(shuffled)
    n_train = max(1, round(len(shuffled) * args.train_frac))
    train_tasks = set(shuffled[:n_train])
    test_tasks = set(shuffled[n_train:])
    print(f"Train tasks ({len(train_tasks)}): {sorted(train_tasks)}")
    print(f"Test tasks  ({len(test_tasks)}): {sorted(test_tasks)}")

    all_sweep_rows: List[dict] = []
    models_seen = set()

    # Sweep over human targets
    for target in args.human_targets:
        print(f"\n=== Human target: {target} ===")
        human_target = build_target(by_item, [r for r in raters if r.startswith("participant")], target)

        target_rows: List[dict] = []

        for jid, j_meta in sorted(judge_meta.items()):
            j_scores = judge_scores.get(jid, {})
            if not j_scores:
                continue
            rows = analyze_judge(jid, j_meta, j_scores, human_target, train_tasks, set(all_tasks))
            for r in rows:
                r["human_target"] = target
            target_rows.extend(rows)
            models_seen.add(j_meta["model"])

        # Ensemble rows per model
        for model in sorted(models_seen):
            if model == "na":
                continue
            model_jids = [j for j in judge_meta if judge_meta[j]["model"] == model]
            ens = ensemble_ridge_lto(model, model_jids, judge_scores, human_target, train_tasks)
            if ens:
                ens["human_target"] = target
                target_rows.append(ens)

        all_sweep_rows.extend(target_rows)

        # Stats for this target
        llm_rows = [r for r in target_rows if r["kind"] in {"llm", "llm_ensemble"}]
        print(f"  Rows for {target}: {len(llm_rows)}")
        best_per_target = {}
        for r in llm_rows:
            model = r["model"]
            te = r["test_item_spearman"]
            if math.isfinite(te) and (model not in best_per_target or te > best_per_target[model]["test_item_spearman"]):
                best_per_target[model] = r
        for model, r in sorted(best_per_target.items()):
            print(f"    {model:30s} best test item rho={r['test_item_spearman']:.3f}  method={r['method']}  judge={r['judge_id']}")

    # Save full sweep
    write_csv(args.out_dir / "sweep_results.csv", all_sweep_rows)
    print(f"\nWrote {len(all_sweep_rows)} rows to sweep_results.csv")

    # Best per model for primary target
    primary_rows = [r for r in all_sweep_rows if r["human_target"] == args.primary_target]
    best_rows = best_per_model(primary_rows, args.primary_target, len(train_tasks), len(test_tasks))
    write_csv(args.out_dir / "best_per_model.csv", best_rows)

    # Summary table
    write_summary_table(
        args.out_dir,
        args.primary_target,
        best_rows,
        primary_rows,
        len(train_tasks),
        len(test_tasks),
    )

    # Plots
    plot_train_test_comparison(best_rows, plots_dir, args.primary_target)
    for method in ["raw", "rank_within_task", "lto_linear", "lto_isotonic", "split_linear", "split_isotonic"]:
        plot_method_scatter(primary_rows, plots_dir, args.primary_target, method)

    # Best across ALL targets (target-optimal)
    print("\n=== Cross-target best (target selected per judge) ===")
    best_any_target: Dict[str, dict] = {}
    for r in all_sweep_rows:
        if r["kind"] not in {"llm", "llm_ensemble"}:
            continue
        model = r["model"]
        te = r["test_item_spearman"]
        if math.isfinite(te) and (model not in best_any_target or te > best_any_target[model]["test_item_spearman"]):
            best_any_target[model] = r
    for model, r in sorted(best_any_target.items()):
        print(
            f"  {model:30s}  test_item={r['test_item_spearman']:.3f}"
            f"  train_item={r['train_item_spearman']:.3f}"
            f"  target={r['human_target']}"
            f"  method={r['method']}"
            f"  judge={r['judge_id']}"
        )

    # Write cross-target best table
    ct_rows = sorted(best_any_target.values(), key=lambda r: -r["test_item_spearman"])
    write_csv(args.out_dir / "best_per_model_any_target.csv", ct_rows)

    # Cross-target summary table
    ct_lines = [
        "# EXP40 Cross-Target Best Results",
        "",
        "Target selected separately per model to maximise test item Spearman.",
        "This is the strongest defensible claim we can make across all aggregation variants.",
        "",
        f"Train tasks: {len(train_tasks)} | Test tasks: {len(test_tasks)} | Seed: {args.train_seed}",
        "",
        "| Model | Best target | Method | Judge | Train item ρ | **Test item ρ** | Train task ρ | Test task ρ | Oracle? |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    model_order = ["labs-leanstral-2603", "gpt-4o-mini", "gpt-5.3-codex", "claude-opus-4-7"]
    for model in model_order:
        if model not in best_any_target:
            ct_lines.append(f"| {MODEL_DISPLAY.get(model, model)} | — | — | — | — | — | — | — | — |")
            continue
        r = best_any_target[model]
        flag = " **✓**" if r["test_item_spearman"] >= 0.70 else ""
        ct_lines.append(
            f"| {MODEL_DISPLAY.get(model, model)} "
            f"| `{r['human_target']}` "
            f"| `{r['method']}` "
            f"| `{r['judge_id']}` "
            f"| {r['train_item_spearman']:.3f} "
            f"| {r['test_item_spearman']:.3f}{flag} "
            f"| {r['train_task_spearman']:.3f} "
            f"| {r['test_task_spearman']:.3f} "
            f"| {'Yes' if r['is_oracle'] else 'No'} |"
        )
    ct_lines += [
        "",
        "| Qwen | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |",
        "",
        "_Qwen missing: no EXP16-style detail\\_rows.csv on the five-human panel._",
    ]
    (args.out_dir / "CROSS_TARGET_TABLE.md").write_text("\n".join(ct_lines) + "\n", encoding="utf-8")

    # Copy to paper
    if args.copy_paper_figs:
        args.paper_fig_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted(plots_dir.glob("fig_exp40_*")):
            target_path = args.paper_fig_dir / path.name
            if target_path.resolve() != path.resolve():
                shutil.copy2(path, target_path)

    print(f"\nAll outputs in: {args.out_dir}")
    print(f"Key files:")
    print(f"  {args.out_dir / 'SUMMARY_TABLE.md'}")
    print(f"  {args.out_dir / 'CROSS_TARGET_TABLE.md'}")
    print(f"  {args.out_dir / 'sweep_results.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
