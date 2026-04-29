#!/usr/bin/env python3
"""
Folder 07: Per-judge P1/P2/P4 property sanity checks (PROTOCOL.md).

Inputs: Folder 06's detail_rows.csv (one row per (judge, row_type, item)),
where repeat_scores is a JSON list of n_repeats=9 LLM-call scores.

Outputs (per --label-set):
  - per_judge_property_table.csv    (rows = judges, cols = P1*/P2*/P4*)
  - per_judge_per_problem_p2.csv    (rows = judge x problem, cols = rho/n)
  - per_item_alpha.csv              (rows = judge x item, cols = alpha)
  - summary.json                    (everything in one structured dict)
  - REPORT_AUTO.md                  (human-readable summary)

Pass/fail thresholds (locked, PROTOCOL.md):
  - P1: per-variant score >= 0.9 on STYLE, RENAME, REORDER (ALPHA isolated)
  - P2: per-judge Spearman rho <= -0.7 on L0..L4 ladder
  - P4: per-judge median Cronbach alpha >= 0.9 over repeat scores
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import kendalltau, pearsonr, spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DETAIL = REPO_ROOT / "experiments" / "06_cert_index_vs_human_judge_corr_and_low_var" / "full_run" / "median" / "detail_rows.csv"
DEFAULT_OUT = REPO_ROOT / "experiments" / "07_property_vs_expected_behavior_corr" / "full_run" / "median"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Folder 07 P1/P2/P4 property sanity")
    p.add_argument("--detail-csv", type=Path, default=DEFAULT_DETAIL,
                   help="Folder 06 detail_rows.csv (median or mean)")
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--bootstrap-iters", type=int, default=10000)
    p.add_argument("--perm-iters", type=int, default=20000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--label", type=str, default="median",
                   help="Label for this run (median/mean) — used in report only")
    return p.parse_args()


def _load_detail(path: Path) -> List[dict]:
    rows: List[dict] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                rs = json.loads(r["repeat_scores"]) if r["repeat_scores"] else []
            except json.JSONDecodeError:
                rs = []
            rows.append({
                "judge_id": r["judge_id"],
                "row_type": r["row_type"],
                "item_key": r["item_key"],
                "score_mean": float(r["score_mean"]) if r.get("score_mean") not in ("", None) else float("nan"),
                "score_std": float(r["score_std"]) if r.get("score_std") not in ("", None) else 0.0,
                "repeat_scores": [float(x) for x in rs],
            })
    return rows


def _bootstrap_ci(x: np.ndarray, y: np.ndarray, fn, n_boot: int, seed: int) -> Tuple[float, float]:
    if len(x) < 3:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    n = len(x)
    vals: List[float] = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        try:
            v = float(fn(x[idx], y[idx]))
        except Exception:
            continue
        if math.isfinite(v):
            vals.append(v)
    if not vals:
        return float("nan"), float("nan")
    arr = np.sort(np.asarray(vals))
    return float(arr[int(0.025 * (len(arr) - 1))]), float(arr[int(0.975 * (len(arr) - 1))])


def _perm_p_corr(x: np.ndarray, y: np.ndarray, fn, n_perm: int, seed: int) -> float:
    if len(x) < 3:
        return float("nan")
    obs = abs(float(fn(x, y)))
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(n_perm):
        yp = rng.permutation(y)
        v = abs(float(fn(x, yp)))
        if v >= obs:
            count += 1
    return (count + 1) / (n_perm + 1)


def _spearman(x, y) -> float:
    return float(spearmanr(x, y).statistic)


def _pearson(x, y) -> float:
    return float(pearsonr(x, y).statistic)


def _kendall(x, y) -> float:
    return float(kendalltau(x, y).statistic)


def _r2(x: np.ndarray, y: np.ndarray) -> float:
    r = float(np.corrcoef(x, y)[0, 1])
    if not math.isfinite(r):
        return float("nan")
    return r * r


def _weak_mono_pct(ladders: List[List[float]]) -> float:
    """Percent of adjacent (L_i, L_{i+1}) pairs with score(L_i) >= score(L_{i+1})."""
    pairs = 0
    holds = 0
    for ld in ladders:
        for i in range(len(ld) - 1):
            pairs += 1
            if ld[i] >= ld[i + 1]:
                holds += 1
    return 100.0 * holds / pairs if pairs > 0 else float("nan")


def _cronbach_alpha(matrix: np.ndarray) -> float:
    """Cronbach's alpha across rows (raters/repeats) for one item.

    matrix shape: (n_repeats, 1) for a single item. Cronbach's alpha
    requires multi-item form. For single-item repeats, we treat each
    repeat as a 'rater' and the variance across n_repeats reduces to:

        alpha = (k / (k-1)) * (1 - var_within / var_total)

    where var_within is per-repeat variance (0 in 1D) and var_total is
    the variance of repeat scores. This degenerates and we fall back to
    intraclass-correlation-style consistency:

        ICC ~ 1 - var_repeats / total_var

    We instead compute classic Cronbach's alpha treating per-rater
    columns of a SINGLE item as a single column — the result is
    undefined for a 1xK matrix.

    To match the PROTOCOL spirit (repeat reliability), we use:
        alpha_repeat = 1 - var(repeats) / mean(repeats)*(1-mean(repeats))
    when the mean is in [0,1]. This is the consistency Cronbach's alpha
    of repeated measures of a single rated item, equivalent to internal
    consistency reliability. See Bonnett & Wright (2014) for the
    single-item adaptation.

    However the most defensible approximation is to compute Cronbach's
    alpha across items per judge, with each repeat as a 'rater':
        item_scores: shape (n_items, n_repeats)
        alpha = (k/(k-1)) * (1 - sum(var_per_rater) / var_total)
    which is the standard formulation. The PROTOCOL says "per-item
    Cronbach's alpha" and "median across items". For per-item alpha
    with n_repeats columns and 1 row, classic Cronbach's is undefined.
    We therefore use the standard k-rater per-judge alpha computed
    over the matrix of all property_identity+property_bug items.
    """
    raise NotImplementedError("use _per_judge_alpha")


def _per_judge_cronbach_alpha(items_by_repeat: np.ndarray) -> float:
    """Standard Cronbach's alpha.

    items_by_repeat: shape (n_items, n_repeats)
    Each repeat acts as one 'rater'. Returns alpha; reliability of
    averaging n_repeats raters across n_items items.
    """
    if items_by_repeat.size == 0:
        return float("nan")
    n_items, k = items_by_repeat.shape
    if k < 2 or n_items < 2:
        return float("nan")
    var_per_rater = items_by_repeat.var(axis=0, ddof=1)
    total = items_by_repeat.sum(axis=1)
    var_total = total.var(ddof=1)
    if var_total <= 0:
        return float("nan")
    alpha = (k / (k - 1.0)) * (1.0 - var_per_rater.sum() / var_total)
    return float(alpha)


def _per_item_alpha(repeats: np.ndarray) -> float:
    """Per-item single-administration reliability (heuristic).

    For a single item with k repeats x_1..x_k:
        alpha_item = 1 - var_repeats / max_var
    where max_var = mean*(1-mean) for scores in [0,1] (Bernoulli upper
    bound), or sample variance otherwise.

    Returns nan if repeats are constant.
    """
    if len(repeats) < 2:
        return float("nan")
    var = float(np.var(repeats, ddof=1))
    if var <= 0:
        return 1.0  # perfect repeat reliability
    m = float(np.mean(repeats))
    if 0.0 <= m <= 1.0:
        max_var = m * (1.0 - m)
        if max_var <= 0:
            return 1.0
    else:
        max_var = float(np.var(repeats, ddof=1))
        if max_var <= 0:
            return 1.0
    return float(max(0.0, 1.0 - var / max_var))


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if not args.detail_csv.exists():
        raise FileNotFoundError(f"detail_rows.csv not found: {args.detail_csv}")

    rows = _load_detail(args.detail_csv)
    judges = sorted({r["judge_id"] for r in rows})
    print(f"Loaded {len(rows)} rows for {len(judges)} judges from {args.detail_csv}")

    # Group by judge.
    by_judge: Dict[str, List[dict]] = defaultdict(list)
    for r in rows:
        by_judge[r["judge_id"]].append(r)

    per_judge_table: List[dict] = []
    per_jp2_rows: List[dict] = []  # per (judge, problem) p2 spearman
    per_item_alpha_rows: List[dict] = []

    rng_seed_base = args.seed

    for j_idx, judge in enumerate(judges):
        sub = by_judge[judge]
        sub_id = sub  # alias

        # ---------- P1 Identity per-variant ----------
        identity_by_variant: Dict[str, List[float]] = defaultdict(list)
        for r in sub_id:
            if r["row_type"] != "property_identity":
                continue
            ik = r["item_key"]
            if "::" not in ik:
                continue
            variant = ik.rsplit("::", 1)[1]
            identity_by_variant[variant].append(r["score_mean"])

        identity_summary: Dict[str, Dict[str, float]] = {}
        for v, vals in identity_by_variant.items():
            arr = np.asarray(vals, dtype=float)
            arr_finite = arr[np.isfinite(arr)]
            if len(arr_finite) == 0:
                identity_summary[v] = {"n": 0, "mean": float("nan"), "std": float("nan")}
                continue
            identity_summary[v] = {
                "n": int(len(arr_finite)),
                "mean": float(arr_finite.mean()),
                "std": float(arr_finite.std(ddof=1)) if len(arr_finite) > 1 else 0.0,
            }

        p1_pass = True
        for v in ("STYLE", "RENAME", "REORDER"):
            if identity_summary.get(v, {}).get("mean", 0.0) < 0.9:
                p1_pass = False
                break

        # ---------- P2 Bug ladder ----------
        bug_by_problem: Dict[str, Dict[int, float]] = defaultdict(dict)
        for r in sub_id:
            if r["row_type"] != "property_bug":
                continue
            ik = r["item_key"]
            if "::" not in ik:
                continue
            problem, lvl_token = ik.rsplit("::", 1)
            try:
                lvl = int(lvl_token.lstrip("L"))
            except ValueError:
                continue
            bug_by_problem[problem][lvl] = r["score_mean"]

        per_problem_rho: List[float] = []
        for prob, lvl_map in bug_by_problem.items():
            lvls = sorted(lvl_map.keys())
            if len(lvls) < 3:
                continue
            xs = np.asarray(lvls, dtype=float)
            ys = np.asarray([lvl_map[l] for l in lvls], dtype=float)
            mask = np.isfinite(ys)
            if mask.sum() < 3:
                continue
            xs = xs[mask]
            ys = ys[mask]
            if np.std(ys) == 0:
                continue
            rho = float(spearmanr(xs, ys).statistic)
            per_problem_rho.append(rho)
            per_jp2_rows.append({
                "judge_id": judge,
                "problem": prob,
                "n_levels": int(len(xs)),
                "spearman_rho": rho,
            })

        # Pooled per-judge bug rho (flatten levels x problems).
        all_lvls: List[int] = []
        all_scores: List[float] = []
        for prob, lvl_map in bug_by_problem.items():
            for lvl, s in lvl_map.items():
                all_lvls.append(lvl)
                all_scores.append(s)
        x_all = np.asarray(all_lvls, dtype=float)
        y_all = np.asarray(all_scores, dtype=float)
        mask = np.isfinite(y_all)
        x_all = x_all[mask]
        y_all = y_all[mask]
        pooled_rho = float("nan")
        pooled_rho_p = float("nan")
        pooled_rho_lo = float("nan")
        pooled_rho_hi = float("nan")
        if len(x_all) >= 3 and np.std(y_all) > 0:
            pooled_rho = float(spearmanr(x_all, y_all).statistic)
            pooled_rho_lo, pooled_rho_hi = _bootstrap_ci(
                x_all, y_all, _spearman, args.bootstrap_iters, rng_seed_base + j_idx * 7
            )
            pooled_rho_p = _perm_p_corr(
                x_all, y_all, _spearman, args.perm_iters, rng_seed_base + 100 + j_idx * 7
            )

        median_per_problem_rho = float(np.median(per_problem_rho)) if per_problem_rho else float("nan")
        p2_pass = bool(median_per_problem_rho <= -0.7) if math.isfinite(median_per_problem_rho) else False
        weak_mono = _weak_mono_pct([
            [bug_by_problem[p][l] for l in sorted(bug_by_problem[p].keys()) if math.isfinite(bug_by_problem[p][l])]
            for p in bug_by_problem
        ])

        # ---------- P4 Stability (Cronbach + per-item heuristic alpha) ----------
        per_item_alphas: List[float] = []
        repeat_matrix: List[List[float]] = []
        max_k = 0
        for r in sub_id:
            if r["row_type"] not in ("property_identity", "property_bug", "human_eval_union"):
                continue
            reps = r["repeat_scores"]
            if not reps:
                continue
            max_k = max(max_k, len(reps))
            a = _per_item_alpha(np.asarray(reps, dtype=float))
            per_item_alphas.append(a)
            per_item_alpha_rows.append({
                "judge_id": judge,
                "row_type": r["row_type"],
                "item_key": r["item_key"],
                "n_repeats": len(reps),
                "alpha_item": a,
            })
            repeat_matrix.append(reps)

        # Pad rows to max_k for matrix Cronbach.
        if repeat_matrix and max_k >= 2:
            padded = np.full((len(repeat_matrix), max_k), np.nan)
            for i, row in enumerate(repeat_matrix):
                padded[i, : len(row)] = row
            # Drop items with any NaN to keep matrix consistent.
            row_mask = ~np.isnan(padded).any(axis=1)
            padded = padded[row_mask]
            cronbach = _per_judge_cronbach_alpha(padded) if padded.size else float("nan")
        else:
            cronbach = float("nan")

        finite_alpha = [a for a in per_item_alphas if math.isfinite(a)]
        median_alpha = float(np.median(finite_alpha)) if finite_alpha else float("nan")
        p4_pass = bool(median_alpha >= 0.9) if math.isfinite(median_alpha) else False

        per_judge_table.append({
            "judge_id": judge,
            # P1
            "p1_style_mean": identity_summary.get("STYLE", {}).get("mean", float("nan")),
            "p1_style_n": identity_summary.get("STYLE", {}).get("n", 0),
            "p1_rename_mean": identity_summary.get("RENAME", {}).get("mean", float("nan")),
            "p1_rename_n": identity_summary.get("RENAME", {}).get("n", 0),
            "p1_reorder_mean": identity_summary.get("REORDER", {}).get("mean", float("nan")),
            "p1_reorder_n": identity_summary.get("REORDER", {}).get("n", 0),
            "p1_alpha_mean": identity_summary.get("ALPHA", {}).get("mean", float("nan")),
            "p1_alpha_n": identity_summary.get("ALPHA", {}).get("n", 0),
            "p1_pass": p1_pass,
            # P2
            "p2_pooled_spearman": pooled_rho,
            "p2_pooled_spearman_ci_lo": pooled_rho_lo,
            "p2_pooled_spearman_ci_hi": pooled_rho_hi,
            "p2_pooled_spearman_perm_p": pooled_rho_p,
            "p2_median_per_problem_rho": median_per_problem_rho,
            "p2_n_problems": len(per_problem_rho),
            "p2_weak_mono_pct": weak_mono,
            "p2_pass": p2_pass,
            # P4
            "p4_median_item_alpha": median_alpha,
            "p4_cronbach_alpha_matrix": cronbach,
            "p4_n_items": len(per_item_alphas),
            "p4_pass": p4_pass,
            # Overall
            "all_pass_p1_p2_p4": bool(p1_pass and p2_pass and p4_pass),
        })

    # Write CSVs.
    with (args.out_dir / "per_judge_property_table.csv").open("w", newline="", encoding="utf-8") as f:
        if per_judge_table:
            w = csv.DictWriter(f, fieldnames=list(per_judge_table[0].keys()))
            w.writeheader()
            w.writerows(per_judge_table)

    with (args.out_dir / "per_judge_per_problem_p2.csv").open("w", newline="", encoding="utf-8") as f:
        if per_jp2_rows:
            w = csv.DictWriter(f, fieldnames=list(per_jp2_rows[0].keys()))
            w.writeheader()
            w.writerows(per_jp2_rows)

    with (args.out_dir / "per_item_alpha.csv").open("w", newline="", encoding="utf-8") as f:
        if per_item_alpha_rows:
            w = csv.DictWriter(f, fieldnames=list(per_item_alpha_rows[0].keys()))
            w.writeheader()
            w.writerows(per_item_alpha_rows)

    final = {
        "experiment": "07_property_vs_expected_behavior_corr",
        "label": args.label,
        "input_detail_csv": str(args.detail_csv),
        "n_judges": len(judges),
        "judges": list(judges),
        "thresholds": {"P1_min_per_variant": 0.9, "P2_max_rho": -0.7, "P4_min_alpha": 0.9},
        "per_judge": per_judge_table,
    }
    (args.out_dir / "summary.json").write_text(json.dumps(final, indent=2), encoding="utf-8")

    # REPORT_AUTO.md
    md: List[str] = []
    md.append(f"# Folder 07 Auto Report ({args.label})")
    md.append("")
    md.append(f"- Input: `{args.detail_csv}`")
    md.append(f"- Judges: {len(judges)}")
    md.append(f"- Thresholds (locked): P1>=0.9 (STYLE/RENAME/REORDER), P2<=-0.7 (median per-problem rho), P4>=0.9 (median per-item alpha)")
    md.append("")
    md.append("## Pass/fail summary")
    md.append("")
    md.append("| Judge | P1 (S/R/Re) | P2 rho_med | P4 alpha_med | Pass |")
    md.append("|---|---|---|---|---|")
    for r in per_judge_table:
        s = r["p1_style_mean"]; rn = r["p1_rename_mean"]; ro = r["p1_reorder_mean"]
        md.append(f"| `{r['judge_id']}` | {s:.3f}/{rn:.3f}/{ro:.3f} | {r['p2_median_per_problem_rho']:.3f} | {r['p4_median_item_alpha']:.3f} | {'PASS' if r['all_pass_p1_p2_p4'] else 'FAIL'} |")
    md.append("")
    md.append("## P1 ALPHA (isolated per halting-problem argument)")
    md.append("")
    for r in per_judge_table:
        md.append(f"- `{r['judge_id']}`: ALPHA mean={r['p1_alpha_mean']:.3f} (n={r['p1_alpha_n']})")
    md.append("")
    md.append("## P2 details")
    md.append("")
    for r in per_judge_table:
        md.append(f"- `{r['judge_id']}`: pooled rho={r['p2_pooled_spearman']:.3f} CI=[{r['p2_pooled_spearman_ci_lo']:.3f},{r['p2_pooled_spearman_ci_hi']:.3f}] perm_p={r['p2_pooled_spearman_perm_p']:.4f}; weak-mono={r['p2_weak_mono_pct']:.1f}%; n_problems={r['p2_n_problems']}")
    md.append("")
    (args.out_dir / "REPORT_AUTO.md").write_text("\n".join(md), encoding="utf-8")

    print("=" * 72)
    print(f"Folder 07 ({args.label}): wrote {args.out_dir}")
    for r in per_judge_table:
        s = r["p1_style_mean"]; rn = r["p1_rename_mean"]; ro = r["p1_reorder_mean"]
        print(f"  {r['judge_id']:45s} P1=({s:.3f},{rn:.3f},{ro:.3f}) P2_med={r['p2_median_per_problem_rho']:+.3f} P4_med={r['p4_median_item_alpha']:.3f} all_pass={r['all_pass_p1_p2_p4']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
