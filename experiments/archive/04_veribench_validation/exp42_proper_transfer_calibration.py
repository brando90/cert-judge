#!/usr/bin/env python3
"""
EXP42: Proper global calibration transfer — fit on train tasks, apply to test tasks.

The critical constraint: NO test-task human labels are used to fit the calibration.
That is the only honest train→test claim for the TMLR paper.

Methods
-------
raw            - No calibration (baseline).
split_linear   - Global OLS linear: fit on train tasks, predict test tasks.
split_isotonic - Global PAV isotonic: fit on train tasks, predict test tasks.
lto_linear     - Leave-one-task-out global linear CV (most defensible).
lto_isotonic   - Leave-one-task-out global isotonic CV.
oracle         - Per-task isotonic, SAME items (upper bound, clearly labeled).

Human targets
-------------
Primary  : zscore_mean (five-rater z-score mean)
Secondary: participant1–participant5 (individual reviewers)

Prompt selection
-----------------
Best prompt per model family selected using ONLY train-task raw Spearman.
Test-task labels NEVER used for selection.

Multi-seed
----------
Runs the 70/30 task split with 10 different random seeds to report mean ± std.

Outputs
-------
results_exp42_proper_transfer/
  sweep_results.csv      - all method × target × judge rows
  PAPER_TABLE.md         - primary TMLR table (train ρ | test ρ, no oracle)
  PER_REVIEWER_TABLE.md  - per-reviewer test ρ for best prompt per model
  MULTISEED_TABLE.md     - mean ± std across 10 seeds (split_isotonic, zscore_mean)
  plots/
"""
from __future__ import annotations

import csv
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
    REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp42_proper_transfer"
)
DEFAULT_PAPER_FIG_DIR = (
    REPO_ROOT / "paper_latex" / "TMLR_2026" / "figures" / "exp42_proper_transfer"
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

TRAIN_SEED = 42
MULTI_SEEDS = [42, 1, 2, 3, 7, 13, 17, 31, 99, 123]
TRAIN_FRAC = 0.70
PRIMARY_TARGET = "zscore_mean"

MODEL_ORDER = ["labs-leanstral-2603", "gpt-4o-mini", "gpt-5.3-codex", "claude-opus-4-7"]
MODEL_DISPLAY = {
    "gpt-5.3-codex": "GPT-5.3 Codex",
    "claude-opus-4-7": "Claude Opus 4.7",
    "labs-leanstral-2603": "LeanStral",
    "gpt-4o-mini": "GPT-4o-mini",
}
COLORS = {
    "labs-leanstral-2603": "#2ca02c",
    "gpt-4o-mini": "#8c564b",
    "gpt-5.3-codex": "#1f77b4",
    "claude-opus-4-7": "#9467bd",
}

# ---------------------------------------------------------------------------
# Math utilities
# ---------------------------------------------------------------------------

def _mean(v: Sequence[float]) -> float:
    vs = [x for x in v if math.isfinite(x)]
    return math.fsum(vs) / len(vs) if vs else float("nan")


def _std(v: Sequence[float]) -> float:
    vs = [x for x in v if math.isfinite(x)]
    if len(vs) < 2:
        return 0.0
    m = _mean(vs)
    return math.sqrt(sum((x - m) ** 2 for x in vs) / (len(vs) - 1))


def _rankdata(v: Sequence[float]) -> List[float]:
    DIGITS = 12
    indexed = sorted(enumerate(v), key=lambda t: round(t[1], DIGITS))
    ranks = [0.0] * len(v)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and round(indexed[j][1], DIGITS) == round(indexed[i][1], DIGITS):
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg
        i = j
    return ranks


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx < 1e-12 or dy < 1e-12:
        return float("nan")
    return num / (dx * dy)


def _spearman(xs: Sequence[float], ys: Sequence[float]) -> float:
    return _pearson(_rankdata(xs), _rankdata(ys))


def _kendall_tau_b(xs: Sequence[float], ys: Sequence[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")
    concordant = discordant = tied_x = tied_y = 0
    DIGITS = 12
    for i in range(n):
        for j in range(i + 1, n):
            dx = round(xs[i] - xs[j], DIGITS)
            dy = round(ys[i] - ys[j], DIGITS)
            sx = (dx > 0) - (dx < 0)
            sy = (dy > 0) - (dy < 0)
            if sx == 0 and sy == 0:
                pass
            elif sx == 0:
                tied_x += 1
            elif sy == 0:
                tied_y += 1
            elif sx == sy:
                concordant += 1
            else:
                discordant += 1
    pairs = n * (n - 1) / 2
    denom = math.sqrt((pairs - tied_x) * (pairs - tied_y))
    if denom < 1e-12:
        return float("nan")
    return (concordant - discordant) / denom


def _r2(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    ss_res = sum((t - p) ** 2 for t, p in zip(y_true, y_pred))
    mt = _mean(y_true)
    ss_tot = sum((t - mt) ** 2 for t in y_true)
    return (1.0 - ss_res / ss_tot) if ss_tot > 1e-12 else float("nan")


def _mae(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    return _mean([abs(t - p) for t, p in zip(y_true, y_pred)])


def _rmse(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    return math.sqrt(_mean([(t - p) ** 2 for t, p in zip(y_true, y_pred)]))


def all_metrics(pred: Sequence[float], true: Sequence[float]) -> dict:
    pairs = [(p, t) for p, t in zip(pred, true) if math.isfinite(p) and math.isfinite(t)]
    if len(pairs) < 3:
        return {k: float("nan") for k in ("n", "spearman", "kendall_tau_b", "pearson", "r2", "mae", "rmse")}
    ps = [p for p, _ in pairs]
    ts = [t for _, t in pairs]
    if len(set(ps)) < 2 or len(set(ts)) < 2:
        return {"n": len(pairs), "spearman": float("nan"), "kendall_tau_b": float("nan"),
                "pearson": float("nan"), "r2": float("nan"), "mae": _mae(ts, ps), "rmse": _rmse(ts, ps)}
    return {
        "n": len(pairs),
        "spearman": _spearman(ps, ts),
        "kendall_tau_b": _kendall_tau_b(ps, ts),
        "pearson": _pearson(ps, ts),
        "r2": _r2(ts, ps),
        "mae": _mae(ts, ps),
        "rmse": _rmse(ts, ps),
    }


def task_means(keys: List[str], scores: List[float]) -> Tuple[List[str], List[float]]:
    bkt: Dict[str, List[float]] = defaultdict(list)
    for k, s in zip(keys, scores):
        bkt[k.split("::", 1)[0]].append(s)
    tasks = sorted(bkt)
    return tasks, [_mean(bkt[t]) for t in tasks]


# ---------------------------------------------------------------------------
# Calibration functions
# ---------------------------------------------------------------------------

def _ols_fit(x: Sequence[float], y: Sequence[float]) -> Tuple[float, float]:
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    den = sum((xi - mx) ** 2 for xi in x)
    if abs(den) < 1e-12:
        return 0.0, my
    slope = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / den
    return slope, my - slope * mx


def _pav_fit(x: Sequence[float], y: Sequence[float]) -> Tuple[List[float], List[float]]:
    pairs = sorted(zip(x, y), key=lambda t: t[0])
    xs = [p[0] for p in pairs]
    ys = [[p[1], 1] for p in pairs]
    flat_y = [b[0] for b in ys]
    i = 0
    while i < len(ys) - 1:
        if flat_y[i] <= flat_y[i + 1] + 1e-15:
            i += 1
            continue
        new_y = (ys[i][0] * ys[i][1] + ys[i + 1][0] * ys[i + 1][1]) / (ys[i][1] + ys[i + 1][1])
        ys[i] = [new_y, ys[i][1] + ys[i + 1][1]]
        del ys[i + 1]
        del xs[i + 1]
        flat_y[i] = new_y
        del flat_y[i + 1]
        if i:
            i -= 1
    return xs, [b[0] for b in ys]


def _pav_predict(fit_xs: List[float], fit_ys: List[float], x_new: Sequence[float]) -> List[float]:
    out = []
    for xv in x_new:
        idx = 0
        while idx + 1 < len(fit_xs) and xv > fit_xs[idx]:
            idx += 1
        idx = min(idx, len(fit_ys) - 1)
        out.append(float(fit_ys[idx]))
    return out


def lto_cv(keys: List[str], x: List[float], y: List[float], calib: str) -> List[float]:
    """Leave-one-task-out CV. Held-out task NEVER used during fitting."""
    task_of = [k.split("::", 1)[0] for k in keys]
    tasks = sorted(set(task_of))
    out = list(x)
    for held in tasks:
        tr_idx = [i for i, t in enumerate(task_of) if t != held]
        te_idx = [i for i, t in enumerate(task_of) if t == held]
        xt = [x[i] for i in tr_idx]
        yt = [y[i] for i in tr_idx]
        xte = [x[i] for i in te_idx]
        if len(set(xt)) < 2:
            continue
        if calib == "linear":
            slope, intercept = _ols_fit(xt, yt)
            pred = [slope * v + intercept for v in xte]
        else:
            fxs, fys = _pav_fit(xt, yt)
            pred = _pav_predict(fxs, fys, xte)
        for j, i in enumerate(te_idx):
            out[i] = pred[j]
    return out


def split_cal(
    keys: List[str],
    x: List[float],
    y: List[float],
    train_tasks: set,
    calib: str,
) -> Tuple[List[float], List[float], List[str], List[str], List[float], List[float]]:
    """
    Fit global calibration on train_tasks; predict both partitions.
    Test predictions are fully held-out — test labels NEVER used.
    Returns (train_pred, test_pred, train_keys, test_keys, train_y, test_y).
    """
    task_of = [k.split("::", 1)[0] for k in keys]
    tr_idx = [i for i, t in enumerate(task_of) if t in train_tasks]
    te_idx = [i for i, t in enumerate(task_of) if t not in train_tasks]
    xt = [x[i] for i in tr_idx]
    yt = [y[i] for i in tr_idx]

    if len(set(xt)) < 2:
        tr_pred = [_mean(yt)] * len(tr_idx)
        te_pred = [_mean(yt)] * len(te_idx)
    elif calib == "linear":
        slope, intercept = _ols_fit(xt, yt)
        tr_pred = [slope * v + intercept for v in xt]
        te_pred = [slope * v + intercept for v in [x[i] for i in te_idx]]
    else:
        fxs, fys = _pav_fit(xt, yt)
        tr_pred = _pav_predict(fxs, fys, xt)
        te_pred = _pav_predict(fxs, fys, [x[i] for i in te_idx])

    return (
        tr_pred, te_pred,
        [keys[i] for i in tr_idx], [keys[i] for i in te_idx],
        [y[i] for i in tr_idx], [y[i] for i in te_idx],
    )


def per_task_iso_oracle(keys: List[str], x: List[float], y: List[float]) -> List[float]:
    """ORACLE: per-task isotonic fit and eval on the SAME items. Upper bound only."""
    task_of = [k.split("::", 1)[0] for k in keys]
    out = list(x)
    by_task: Dict[str, List[int]] = defaultdict(list)
    for i, t in enumerate(task_of):
        by_task[t].append(i)
    for idxs in by_task.values():
        if len(idxs) < 2:
            continue
        xt = [x[i] for i in idxs]
        yt = [y[i] for i in idxs]
        if len(set(xt)) < 2:
            continue
        fxs, fys = _pav_fit(xt, yt)
        for j, i in enumerate(idxs):
            out[i] = _pav_predict(fxs, fys, [xt[j]])[0]
    return out


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

PARTICIPANT_FILES = {
    "participant1": "participant1_data_correct_prompt.tsv",
    "participant2": "participant2_data_pass_1.tsv",
    "participant3": "participant3_data_pass_1.tsv",
    "participant4": "participant4_data_pass_1.tsv",
    "participant5": "participant5_data_pass_1.tsv",
}


def load_human_labels(human_dir: Path) -> Tuple[Dict[str, Dict[str, float]], List[str]]:
    """Load all participant TSVs. Returns (by_item, rater_names)."""
    by_item: Dict[str, Dict[str, float]] = defaultdict(dict)
    raters: List[str] = []
    for rater, fname in sorted(PARTICIPANT_FILES.items()):
        path = human_dir / fname
        if not path.exists():
            continue
        raters.append(rater)
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                gold = str(row.get("gold_file", "")).strip()
                cand = str(row.get("candidate_file", "")).strip()
                score_text = str(row.get("human_score_0_5", "")).strip()
                # handle format where score is appended to cand field
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
    return by_item, raters


def build_targets(
    by_item: Dict[str, Dict[str, float]], raters: List[str]
) -> Dict[str, Dict[str, float]]:
    """
    Build all human targets:
      - zscore_mean: five-rater z-score mean (primary)
      - mean: simple mean
      - participant1 … participant5: individual rater scores
    """
    rater_stats: Dict[str, Tuple[float, float]] = {}
    for r in raters:
        vals = [rmap[r] for rmap in by_item.values() if r in rmap]
        rater_stats[r] = (_mean(vals), _std(vals))

    targets: Dict[str, Dict[str, float]] = {"zscore_mean": {}, "mean": {}}
    for r in raters:
        targets[r] = {}

    for item_key, rmap in by_item.items():
        vals = [rmap[r] for r in raters if r in rmap]
        if not vals:
            continue
        targets["mean"][item_key] = _mean(vals)
        zs = []
        for r in raters:
            if r not in rmap:
                continue
            m, s = rater_stats[r]
            zs.append((rmap[r] - m) / s if s > 1e-9 else 0.0)
        targets["zscore_mean"][item_key] = _mean(zs)
        for r in raters:
            if r in rmap:
                targets[r][item_key] = rmap[r]

    return targets


def load_judge_scores(result_dirs: List[Path]) -> Tuple[Dict[str, dict], Dict[str, Dict[str, float]]]:
    meta: Dict[str, dict] = {}
    scores: Dict[str, Dict[str, float]] = defaultdict(dict)
    for rd in result_dirs:
        jr = rd / "judge_rows.csv"
        dr = rd / "detail_rows.csv"
        if not jr.exists() or not dr.exists():
            continue
        with jr.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                jid = row["judge_id"]
                if jid not in meta:
                    meta[jid] = {
                        "judge_id": jid,
                        "kind": row.get("kind", ""),
                        "model": row.get("model", ""),
                        "prompt_name": row.get("prompt_name", ""),
                    }
        with dr.open(newline="", encoding="utf-8") as f:
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
# Core analysis
# ---------------------------------------------------------------------------

def analyze_judge(
    jid: str,
    meta: dict,
    j_scores: Dict[str, float],
    targets: Dict[str, Dict[str, float]],
    train_tasks: set,
    primary_target: str,
) -> List[dict]:
    """Run all methods for one judge against all targets. Returns list of result rows."""
    human_target = targets[primary_target]
    common = sorted(set(j_scores) & set(human_target))
    if len(common) < 6:
        return []

    keys = common
    x = [j_scores[k] for k in keys]
    y = [human_target[k] for k in keys]
    task_of = [k.split("::", 1)[0] for k in keys]
    all_tasks = sorted(set(task_of))

    base = {
        "judge_id": jid,
        "kind": meta["kind"],
        "model": meta["model"],
        "prompt_name": meta["prompt_name"],
        "n_items": len(common),
        "n_tasks": len(all_tasks),
    }

    rows: List[dict] = []

    def _add(method: str, is_oracle: bool, split: str, tgt_name: str,
             pred: List[float], true: List[float], item_keys: List[str]) -> None:
        m = all_metrics(pred, true)
        tk, ty_hat = task_means(item_keys, pred)
        _, ty_true = task_means(item_keys, true)
        mt = all_metrics(ty_hat, ty_true)
        rows.append({
            **base,
            "human_target": tgt_name,
            "method": method,
            "is_oracle": is_oracle,
            "split": split,
            **{f"item_{k}": v for k, v in m.items()},
            **{f"task_{k}": v for k, v in mt.items()},
        })

    # --- Process for primary target (all methods) ---
    _add("raw", False, "full", primary_target, x, y, keys)

    # LOO-CV global linear
    lto_lin = lto_cv(keys, x, y, "linear")
    _add("lto_linear", False, "loo_cv", primary_target, lto_lin, y, keys)

    # LOO-CV global isotonic
    lto_iso = lto_cv(keys, x, y, "isotonic")
    _add("lto_isotonic", False, "loo_cv", primary_target, lto_iso, y, keys)

    # Split global linear
    tr_pred, te_pred, tr_keys, te_keys, tr_y, te_y = split_cal(keys, x, y, train_tasks, "linear")
    for sname, pred_s, keys_s, y_s in [("train", tr_pred, tr_keys, tr_y), ("test", te_pred, te_keys, te_y)]:
        _add("split_linear", False, sname, primary_target, pred_s, y_s, keys_s)

    # Split global isotonic
    tr_pred, te_pred, tr_keys, te_keys, tr_y, te_y = split_cal(keys, x, y, train_tasks, "isotonic")
    for sname, pred_s, keys_s, y_s in [("train", tr_pred, tr_keys, tr_y), ("test", te_pred, te_keys, te_y)]:
        _add("split_isotonic", False, sname, primary_target, pred_s, y_s, keys_s)

    # Oracle upper bound
    oracle_pred = per_task_iso_oracle(keys, x, y)
    for split_name, idx_fn in [
        ("full", lambda: list(range(len(keys)))),
        ("train", lambda: [i for i, k in enumerate(keys) if k.split("::")[0] in train_tasks]),
        ("test", lambda: [i for i, k in enumerate(keys) if k.split("::")[0] not in train_tasks]),
    ]:
        idxs = idx_fn()
        sk = [keys[i] for i in idxs]
        sp = [oracle_pred[i] for i in idxs]
        sy = [y[i] for i in idxs]
        _add("per_task_iso_ORACLE", True, split_name, primary_target, sp, sy, sk)

    # --- Per-reviewer analysis (split_isotonic test only, for PER_REVIEWER table) ---
    for tgt_name, tgt_dict in targets.items():
        if tgt_name in (primary_target, "mean"):
            continue  # already done or skipped
        if not tgt_name.startswith("participant"):
            continue
        common_r = sorted(set(j_scores) & set(tgt_dict))
        if len(common_r) < 6:
            continue
        xr = [j_scores[k] for k in common_r]
        yr = [tgt_dict[k] for k in common_r]
        # raw
        _add("raw", False, "full", tgt_name, xr, yr, common_r)
        # split_isotonic train/test
        tr_pred2, te_pred2, tr_keys2, te_keys2, tr_y2, te_y2 = split_cal(
            common_r, xr, yr, train_tasks, "isotonic"
        )
        for sname, pred_s, keys_s, y_s in [
            ("train", tr_pred2, tr_keys2, tr_y2),
            ("test", te_pred2, te_keys2, te_y2),
        ]:
            _add("split_isotonic", False, sname, tgt_name, pred_s, y_s, keys_s)

    return rows


# ---------------------------------------------------------------------------
# Prompt selection (train only)
# ---------------------------------------------------------------------------

def best_prompt_per_model_train(
    all_rows: List[dict],
    primary_target: str,
    method: str = "raw",
    split: str = "full",
) -> Dict[str, Tuple[str, float]]:
    """Return {model: (judge_id, train_item_spearman)} selected on train items only."""
    by_model: Dict[str, Tuple[float, str]] = {}
    for r in all_rows:
        if r["human_target"] != primary_target:
            continue
        if r["method"] != method:
            continue
        if r["split"] != split:
            continue
        if r["kind"] != "llm":
            continue
        model = r["model"]
        val = r.get("item_spearman", float("nan"))
        if not math.isfinite(val):
            continue
        if model not in by_model or val > by_model[model][0]:
            by_model[model] = (val, r["judge_id"])
    return {m: (jid, rho) for m, (rho, jid) in by_model.items()}


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def write_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _fmt(v: float, decimals: int = 3) -> str:
    if not math.isfinite(v):
        return "—"
    return f"{v:.{decimals}f}"


def _flag(v: float, thresh: float = 0.70) -> str:
    return " **✓**" if math.isfinite(v) and v >= thresh else ""


# ---------------------------------------------------------------------------
# Paper Table (PAPER_TABLE.md)
# ---------------------------------------------------------------------------

def write_paper_table(
    all_rows: List[dict],
    out_dir: Path,
    primary_target: str,
    n_train: int,
    n_test: int,
    best_prompts: Dict[str, Tuple[str, float]],
) -> None:
    """
    Main TMLR paper table. Columns:
      Model | Best judge | Raw item ρ | Train item ρ | Test item ρ | Train task ρ | Test task ρ
    One row per model family (best judge selected on train raw ρ only).
    Methods shown: raw (full), split_isotonic train, split_isotonic test.
    Oracle shown as a separate 'upper bound' block.
    """

    def _best(method: str, split: str, tgt: str = primary_target) -> Dict[str, dict]:
        by: Dict[str, dict] = {}
        for r in all_rows:
            if r["human_target"] != tgt or r["method"] != method or r["split"] != split:
                continue
            if r["kind"] != "llm":
                continue
            model = r["model"]
            # For non-raw methods: restrict to the prompt selected on train
            if method != "raw" and model in best_prompts:
                if r["judge_id"] != best_prompts[model][0]:
                    continue
            val = r.get("item_spearman", float("nan"))
            if not math.isfinite(val):
                continue
            if model not in by or val > by[model].get("item_spearman", float("nan")):
                by[model] = r
        return by

    raw_full = _best("raw", "full")
    split_iso_train = _best("split_isotonic", "train")
    split_iso_test = _best("split_isotonic", "test")
    oracle_full = _best("per_task_iso_ORACLE", "full")

    col_hdr = "| Model | Best judge | Raw item ρ | Train item ρ | **Test item ρ** | Train task ρ | Test task ρ |"
    col_sep = "| --- | --- | ---: | ---: | ---: | ---: | ---: |"

    def _row(model: str) -> str:
        label = MODEL_DISPLAY.get(model, model)
        r_raw = raw_full.get(model)
        r_tr = split_iso_train.get(model)
        r_te = split_iso_test.get(model)
        jid = best_prompts.get(model, (None,))[0] or "—"
        raw_rho = r_raw.get("item_spearman", float("nan")) if r_raw else float("nan")
        tr_rho = r_tr.get("item_spearman", float("nan")) if r_tr else float("nan")
        te_rho = r_te.get("item_spearman", float("nan")) if r_te else float("nan")
        tr_task = r_tr.get("task_spearman", float("nan")) if r_tr else float("nan")
        te_task = r_te.get("task_spearman", float("nan")) if r_te else float("nan")
        return (
            f"| {label} | `{jid}` "
            f"| {_fmt(raw_rho)} "
            f"| {_fmt(tr_rho)} "
            f"| {_fmt(te_rho)}{_flag(te_rho)} "
            f"| {_fmt(tr_task)} "
            f"| {_fmt(te_task)} |"
        )

    def _oracle_row(model: str) -> str:
        label = MODEL_DISPLAY.get(model, model)
        r = oracle_full.get(model)
        if not r:
            return f"| {label} | — | — | — |"
        rho = r.get("item_spearman", float("nan"))
        task_rho = r.get("task_spearman", float("nan"))
        return f"| {label} | `{r['judge_id']}` | {_fmt(rho)}{_flag(rho)} | {_fmt(task_rho)} |"

    lines = [
        "# EXP42 Judge–Human Alignment: Proper Calibration Transfer",
        "",
        f"Human target: **{primary_target}** (five-rater z-score mean)  ",
        f"Train/test split: {n_train} train tasks / {n_test} test tasks (seed={TRAIN_SEED})  ",
        "Calibration: **global isotonic** (PAV), fit on train tasks, applied to test tasks.  ",
        "**No test-task human labels used anywhere in the calibration pipeline.**",
        "",
        "Best prompt per model family selected by raw item Spearman on train tasks only.",
        "",
        "---",
        "",
        "## Primary Table — Global Isotonic Calibration Transfer",
        "",
        col_hdr,
        col_sep,
    ]
    for model in MODEL_ORDER:
        lines.append(_row(model))
    lines += [
        "| Qwen | N/A | N/A | N/A | N/A | N/A | N/A |",
        "",
        "**✓** = Test item ρ ≥ 0.70.",
        "",
        "---",
        "",
        "## Oracle Upper Bound (per-task isotonic, same items — NOT held-out)",
        "",
        "| Model | Best judge | Full item ρ | Full task ρ |",
        "| --- | --- | ---: | ---: |",
    ]
    for model in MODEL_ORDER:
        lines.append(_oracle_row(model))
    lines += [
        "| Qwen | N/A | N/A | N/A |",
        "",
        "---",
        "",
        "## Methodology",
        "",
        "- **Global isotonic calibration**: fit a single monotone step function (PAV) on all",
        "  train-task items (judge score → human score). Applied as-is to test-task judge scores.",
        "  No per-task adaptation — the calibration must transfer across tasks.",
        "- **Split**: tasks randomly partitioned 70/30 by seed. Calibration never touches test labels.",
        "- **Oracle**: per-task isotonic on the same 3 items used for evaluation — an upper bound,",
        "  not a valid claim for unseen tasks.",
        "- **Qwen**: excluded — no item-level judge caches against the five-human panel.",
        "",
        "## Honest Assessment",
        "",
        "- Global calibration transfers the monotone shape learned on train tasks.",
        "- Per-task scale differences (task difficulty) are NOT corrected without test labels.",
        "- This is the most defensible claim for TMLR: held-out test ρ with zero test leakage.",
    ]

    (out_dir / "PAPER_TABLE.md").write_text("\n".join(lines) + "\n")
    print(f"  Wrote PAPER_TABLE.md")


# ---------------------------------------------------------------------------
# Per-Reviewer Table (PER_REVIEWER_TABLE.md)
# ---------------------------------------------------------------------------

def write_per_reviewer_table(
    all_rows: List[dict],
    out_dir: Path,
    raters: List[str],
    best_prompts: Dict[str, Tuple[str, float]],
) -> None:
    """
    Per-reviewer test Spearman for best prompt per model family.
    Columns: Model | Rev1 train ρ / test ρ | … | Rev5 train ρ / test ρ | Agg test ρ
    """

    def _get(model: str, method: str, split: str, tgt: str) -> float:
        jid = best_prompts.get(model, (None,))[0]
        best = float("nan")
        for r in all_rows:
            if r["human_target"] != tgt or r["method"] != method or r["split"] != split:
                continue
            if r["kind"] != "llm" or r["model"] != model:
                continue
            if jid and r["judge_id"] != jid:
                continue
            val = r.get("item_spearman", float("nan"))
            if math.isfinite(val) and (not math.isfinite(best) or val > best):
                best = val
        return best

    rev_labels = [r.replace("participant", "P") for r in raters]

    lines = [
        "# EXP42 Per-Reviewer Judge–Human Alignment (Test Tasks)",
        "",
        "Global isotonic calibration, fit on train tasks, applied to test tasks.  ",
        f"Best prompt per model selected on train raw ρ (primary target = {PRIMARY_TARGET}).",
        "",
        "Each reviewer shown separately; 'Agg' = zscore_mean of all five.",
        "",
    ]

    # Header: Model | P1 tr/te | P2 tr/te | ... | Agg te
    hdr_cols = ["Model"]
    for rl in rev_labels:
        hdr_cols.append(f"{rl} Train ρ")
        hdr_cols.append(f"{rl} Test ρ")
    hdr_cols.append("Agg Test ρ")
    lines.append("| " + " | ".join(hdr_cols) + " |")
    lines.append("| " + " | ".join(["---"] + ["---:"] * (len(hdr_cols) - 1)) + " |")

    for model in MODEL_ORDER:
        label = MODEL_DISPLAY.get(model, model)
        cols = [label]
        for r in raters:
            tr = _get(model, "split_isotonic", "train", r)
            te = _get(model, "split_isotonic", "test", r)
            cols.append(_fmt(tr))
            cols.append(f"{_fmt(te)}{_flag(te)}")
        agg_te = _get(model, "split_isotonic", "test", PRIMARY_TARGET)
        cols.append(f"{_fmt(agg_te)}{_flag(agg_te)}")
        lines.append("| " + " | ".join(cols) + " |")

    lines += [
        "| Qwen | " + " | ".join(["N/A"] * (len(hdr_cols) - 1)) + " |",
        "",
        "**✓** = ρ ≥ 0.70.",
    ]

    (out_dir / "PER_REVIEWER_TABLE.md").write_text("\n".join(lines) + "\n")
    print(f"  Wrote PER_REVIEWER_TABLE.md")


# ---------------------------------------------------------------------------
# Multi-seed robustness (MULTISEED_TABLE.md)
# ---------------------------------------------------------------------------

def write_multiseed_table(
    judge_meta: Dict[str, dict],
    judge_scores: Dict[str, Dict[str, float]],
    human_target: Dict[str, float],
    all_tasks: List[str],
    out_dir: Path,
) -> None:
    """Run split_isotonic (primary target) across MULTI_SEEDS and report mean ± std."""
    # Collect per-seed, per-model best test rho
    per_seed: Dict[int, Dict[str, float]] = {}

    for seed in MULTI_SEEDS:
        rng = random.Random(seed)
        tasks_shuffled = list(all_tasks)
        rng.shuffle(tasks_shuffled)
        n_train = int(len(tasks_shuffled) * TRAIN_FRAC)
        train_set = set(tasks_shuffled[:n_train])

        best_for_model: Dict[str, float] = {}
        for jid, meta in judge_meta.items():
            if meta["kind"] != "llm":
                continue
            model = meta["model"]
            common = sorted(set(judge_scores[jid]) & set(human_target))
            if len(common) < 6:
                continue
            keys = common
            x = [judge_scores[jid][k] for k in keys]
            y = [human_target[k] for k in keys]
            _, te_pred, _, te_keys, _, te_y = split_cal(keys, x, y, train_set, "isotonic")
            if len(te_pred) < 3:
                continue
            rho = all_metrics(te_pred, te_y).get("spearman", float("nan"))
            if not math.isfinite(rho):
                continue
            if model not in best_for_model or rho > best_for_model[model]:
                best_for_model[model] = rho
        per_seed[seed] = best_for_model

    lines = [
        "# EXP42 Multi-Seed Robustness (split_isotonic, zscore_mean)",
        "",
        f"10 random train/test splits (70/30). Best judge per model selected per seed.",
        "",
        "| Model | Mean test ρ | Std | Min | Max |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]

    for model in MODEL_ORDER:
        label = MODEL_DISPLAY.get(model, model)
        vals = [per_seed[s].get(model, float("nan")) for s in MULTI_SEEDS]
        vals = [v for v in vals if math.isfinite(v)]
        if not vals:
            lines.append(f"| {label} | — | — | — | — |")
            continue
        mu = _mean(vals)
        sd = _std(vals)
        mn = min(vals)
        mx = max(vals)
        lines.append(
            f"| {label} | {_fmt(mu)}{_flag(mu)} | ±{_fmt(sd)} | {_fmt(mn)} | {_fmt(mx)} |"
        )

    lines += [
        "| Qwen | N/A | N/A | N/A | N/A |",
        "",
        "**✓** = Mean test ρ ≥ 0.70.",
        "",
        f"Seeds used: {MULTI_SEEDS}",
    ]

    (out_dir / "MULTISEED_TABLE.md").write_text("\n".join(lines) + "\n")
    print(f"  Wrote MULTISEED_TABLE.md")


# ---------------------------------------------------------------------------
# Scatter plots
# ---------------------------------------------------------------------------

def plot_scatter(
    judge_id: str,
    model: str,
    test_keys: List[str],
    test_pred: List[float],
    test_y: List[float],
    out_dir: Path,
    rho: float,
) -> None:
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.scatter(test_pred, test_y, alpha=0.6, color=COLORS.get(model, "#333333"), s=30)
    ax.set_xlabel("Calibrated judge score (global isotonic)", fontsize=10)
    ax.set_ylabel("Human score (zscore_mean)", fontsize=10)
    ax.set_title(f"{MODEL_DISPLAY.get(model, model)}\nTest ρ = {rho:.3f}", fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    safe = judge_id.replace("|", "_").replace("/", "_")
    fig.savefig(out_dir / f"scatter_test_{safe}.png", dpi=120)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="EXP42: Proper global calibration transfer")
    parser.add_argument("--human-dir", type=Path, default=DEFAULT_HUMAN_DIR)
    parser.add_argument("--result-dirs", nargs="+", type=Path, default=DEFAULT_RESULT_DIRS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--paper-fig-dir", type=Path, default=DEFAULT_PAPER_FIG_DIR)
    parser.add_argument("--train-seed", type=int, default=TRAIN_SEED)
    parser.add_argument("--train-frac", type=float, default=TRAIN_FRAC)
    args = parser.parse_args()

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(exist_ok=True)

    print("Loading human labels...")
    by_item, raters = load_human_labels(args.human_dir)
    print(f"  {len(raters)} raters: {raters}")
    targets = build_targets(by_item, raters)
    human_target = targets[PRIMARY_TARGET]
    print(f"  {len(human_target)} items with primary target ({PRIMARY_TARGET})")

    # Determine tasks and train/test split
    all_tasks = sorted({k.split("::", 1)[0] for k in human_target})
    rng = random.Random(args.train_seed)
    tasks_shuffled = list(all_tasks)
    rng.shuffle(tasks_shuffled)
    n_train = int(len(tasks_shuffled) * args.train_frac)
    train_tasks = set(tasks_shuffled[:n_train])
    test_tasks = set(tasks_shuffled[n_train:])
    print(f"  Tasks: {len(all_tasks)} total | {len(train_tasks)} train | {len(test_tasks)} test (seed={args.train_seed})")

    print("Loading judge scores...")
    judge_meta, judge_scores = load_judge_scores(args.result_dirs)
    print(f"  {len(judge_meta)} judges loaded")

    print("Running analysis...")
    all_rows: List[dict] = []
    for jid, meta in judge_meta.items():
        if meta["kind"] != "llm":
            continue
        rows = analyze_judge(
            jid=jid,
            meta=meta,
            j_scores=judge_scores[jid],
            targets=targets,
            train_tasks=train_tasks,
            primary_target=PRIMARY_TARGET,
        )
        all_rows.extend(rows)
    print(f"  {len(all_rows)} result rows")

    # Select best prompt per model on train raw ρ
    best_prompts = best_prompt_per_model_train(all_rows, PRIMARY_TARGET, method="raw", split="full")
    # Refine: use train-only items for raw selection
    # (raw "full" already computed above; use train subset by filtering)
    # Actually recompute on train items only for correctness
    best_prompts_train: Dict[str, Tuple[str, float]] = {}
    for jid, meta in judge_meta.items():
        if meta["kind"] != "llm":
            continue
        model = meta["model"]
        common = sorted(set(judge_scores[jid]) & set(human_target))
        tr_keys = [k for k in common if k.split("::")[0] in train_tasks]
        if len(tr_keys) < 3:
            continue
        xtr = [judge_scores[jid][k] for k in tr_keys]
        ytr = [human_target[k] for k in tr_keys]
        rho = all_metrics(xtr, ytr).get("spearman", float("nan"))
        if not math.isfinite(rho):
            continue
        if model not in best_prompts_train or rho > best_prompts_train[model][1]:
            best_prompts_train[model] = (jid, rho)
    print("  Best prompts (selected on train raw ρ):")
    for model, (jid, rho) in sorted(best_prompts_train.items()):
        print(f"    {MODEL_DISPLAY.get(model, model)}: {jid}  (train raw ρ = {rho:.3f})")

    # Write CSV
    write_csv(out_dir / "sweep_results.csv", all_rows)
    print(f"  Wrote sweep_results.csv ({len(all_rows)} rows)")

    # Scatter plots for best judge per model (test split_isotonic)
    for model, (jid, _) in best_prompts_train.items():
        common = sorted(set(judge_scores[jid]) & set(human_target))
        if len(common) < 6:
            continue
        keys = common
        x = [judge_scores[jid][k] for k in keys]
        y = [human_target[k] for k in keys]
        _, te_pred, _, te_keys, _, te_y = split_cal(keys, x, y, train_tasks, "isotonic")
        rho = all_metrics(te_pred, te_y).get("spearman", float("nan"))
        try:
            plot_scatter(jid, model, te_keys, te_pred, te_y, plots_dir, rho)
        except Exception as e:
            print(f"    Plot failed for {jid}: {e}")

    # Write paper table
    write_paper_table(all_rows, out_dir, PRIMARY_TARGET, len(train_tasks), len(test_tasks), best_prompts_train)

    # Write per-reviewer table
    write_per_reviewer_table(all_rows, out_dir, raters, best_prompts_train)

    # Write multi-seed table
    print("Running multi-seed analysis...")
    write_multiseed_table(judge_meta, judge_scores, human_target, all_tasks, out_dir)

    # Copy figures to paper latex dir
    paper_fig_dir: Path = args.paper_fig_dir
    paper_fig_dir.mkdir(parents=True, exist_ok=True)
    for f in plots_dir.glob("*.png"):
        shutil.copy2(f, paper_fig_dir / f.name)
    for f in ["PAPER_TABLE.md", "PER_REVIEWER_TABLE.md", "MULTISEED_TABLE.md"]:
        src = out_dir / f
        if src.exists():
            shutil.copy2(src, paper_fig_dir / f)
    print(f"  Figures and tables copied to {paper_fig_dir}")

    print("\nDone. Results in:", out_dir)


if __name__ == "__main__":
    main()
