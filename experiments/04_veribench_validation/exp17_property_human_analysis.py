#!/usr/bin/env python3
"""
EXP17: Property-level analysis against human correlation across judges.

Inputs:
  - summary.json from EXP16

Outputs:
  - per_property_correlations.csv
  - partial_correlations.csv
  - regression_summary.json
  - summary.json
  - results_summary.md
  - fig_property_vs_human_bars.png
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import pearsonr, spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXP16_SUMMARY = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_multi_judge_human_sets" / "summary.json"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp17_property_human_analysis"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP17 property-level and regression analysis")
    p.add_argument("--exp16-summary", type=Path, default=DEFAULT_EXP16_SUMMARY)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--label-set", type=str, default="avg", choices=["pass1", "pass2", "avg"])
    p.add_argument("--perm-iters", type=int, default=20000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--bad-judge-pattern", type=str, default="BAD_STRINGY")
    return p.parse_args()


def _perm_pvalue_corr(x: np.ndarray, y: np.ndarray, fn, n_perm: int, seed: int) -> float:
    rng = np.random.default_rng(seed)
    obs = abs(float(fn(x, y)))
    vals = []
    for _ in range(n_perm):
        yp = rng.permutation(y)
        vals.append(abs(float(fn(x, yp))))
    vals = np.asarray(vals, dtype=float)
    return float((1 + np.sum(vals >= obs)) / (1 + len(vals)))


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    return float(spearmanr(x, y).statistic)


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    return float(pearsonr(x, y).statistic)


def _zscore(v: np.ndarray) -> np.ndarray:
    s = np.std(v)
    if s <= 0:
        return np.zeros_like(v)
    return (v - np.mean(v)) / s


def _residualize(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    # y ~ [1, X]
    Xd = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    return y - Xd @ beta


def _partial_corr(xj: np.ndarray, y: np.ndarray, Xother: np.ndarray) -> Tuple[float, float]:
    rx = _residualize(xj, Xother)
    ry = _residualize(y, Xother)
    return float(pearsonr(rx, ry).statistic), float(spearmanr(rx, ry).statistic)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    summary = json.loads(args.exp16_summary.read_text(encoding="utf-8"))
    rows: List[dict] = summary["judge_rows"]
    n = len(rows)
    if n < 5:
        raise ValueError(f"Need >=5 judges, got {n}")

    # P1-P4 aligned feature mapping.
    # Higher-is-better for all.
    feature_specs = [
        ("P1_identity", lambda r: float(r["identity_mean"])),
        ("P2_bug_rank", lambda r: float(max(0.0, min(1.0, (-float(r["bug_spearman_r"]) + 1.0) / 2.0)))),
        ("P3_weak_mono", lambda r: float(max(0.0, min(1.0, float(r["bug_weak_mono_pct"]) / 100.0)))),
        ("P4_stability", lambda r: float(max(0.0, min(1.0, 1.0 - float(r["flip_rate"]))))),
    ]

    y = np.asarray([float(r[f"human_spearman_r_{args.label_set}"]) for r in rows], dtype=float)
    X_cols: Dict[str, np.ndarray] = {}
    for name, fn in feature_specs:
        X_cols[name] = np.asarray([fn(r) for r in rows], dtype=float)

    # 1) Per-property correlations with human outcome.
    per_prop: List[dict] = []
    for i, (name, _) in enumerate(feature_specs):
        x = X_cols[name]
        sp = _spearman(x, y)
        pe = _pearson(x, y)
        sp_p = _perm_pvalue_corr(x, y, _spearman, args.perm_iters, args.seed + 10 + i)
        pe_p = _perm_pvalue_corr(x, y, _pearson, args.perm_iters, args.seed + 20 + i)
        per_prop.append(
            {
                "property": name,
                "spearman_r": float(sp),
                "spearman_perm_p": float(sp_p),
                "pearson_r": float(pe),
                "pearson_perm_p": float(pe_p),
            }
        )

    # 2) Multivariate regression (standardized).
    prop_names = [p[0] for p in feature_specs]
    X = np.column_stack([X_cols[p] for p in prop_names])
    Xz = np.column_stack([_zscore(X[:, j]) for j in range(X.shape[1])])
    yz = _zscore(y)
    Xd = np.column_stack([np.ones(len(Xz)), Xz])
    beta, *_ = np.linalg.lstsq(Xd, yz, rcond=None)
    yhat = Xd @ beta
    resid = yz - yhat
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((yz - np.mean(yz)) ** 2))
    r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan")

    rng = np.random.default_rng(args.seed + 77)
    r2_perm_vals = []
    beta_perm_vals = [[] for _ in range(X.shape[1])]
    for _ in range(args.perm_iters):
        yp = rng.permutation(yz)
        b, *_ = np.linalg.lstsq(Xd, yp, rcond=None)
        yp_hat = Xd @ b
        sse = float(np.sum((yp - yp_hat) ** 2))
        sst = float(np.sum((yp - np.mean(yp)) ** 2))
        r2p = float(1.0 - sse / sst) if sst > 0 else float("nan")
        if math.isfinite(r2p):
            r2_perm_vals.append(r2p)
        for j in range(X.shape[1]):
            beta_perm_vals[j].append(abs(float(b[j + 1])))

    r2_perm_vals = np.asarray(r2_perm_vals, dtype=float)
    r2_p = float((1 + np.sum(r2_perm_vals >= r2)) / (1 + len(r2_perm_vals))) if len(r2_perm_vals) else float("nan")
    beta_rows: List[dict] = []
    for j, name in enumerate(prop_names):
        obs = abs(float(beta[j + 1]))
        vals = np.asarray(beta_perm_vals[j], dtype=float)
        p = float((1 + np.sum(vals >= obs)) / (1 + len(vals))) if len(vals) else float("nan")
        beta_rows.append({"property": name, "beta_std": float(beta[j + 1]), "beta_perm_p": p})

    # 3) Partial correlations.
    partial_rows: List[dict] = []
    for j, name in enumerate(prop_names):
        xj = Xz[:, j]
        xother = np.delete(Xz, j, axis=1)
        ppear, pspear = _partial_corr(xj, yz, xother)
        # Perm p for partial pearson (residualized).
        rx = _residualize(xj, xother)
        ry = _residualize(yz, xother)
        p_p = _perm_pvalue_corr(rx, ry, _pearson, args.perm_iters, args.seed + 300 + j)
        s_p = _perm_pvalue_corr(rx, ry, _spearman, args.perm_iters, args.seed + 400 + j)
        partial_rows.append(
            {
                "property": name,
                "partial_pearson_r": float(ppear),
                "partial_pearson_perm_p": float(p_p),
                "partial_spearman_r": float(pspear),
                "partial_spearman_perm_p": float(s_p),
            }
        )

    # 4) Bad-judge gap analysis (if present).
    bad_rows = [r for r in rows if args.bad_judge_pattern in str(r["judge_id"])]
    bad_gap = None
    if bad_rows:
        bad = bad_rows[0]
        prop_scores = {
            "P1_identity": float(bad["identity_mean"]),
            "P2_bug_rank": float(max(0.0, min(1.0, (-float(bad["bug_spearman_r"]) + 1.0) / 2.0))),
            "P3_weak_mono": float(max(0.0, min(1.0, float(bad["bug_weak_mono_pct"]) / 100.0))),
            "P4_stability": float(max(0.0, min(1.0, 1.0 - float(bad["flip_rate"])))),
        }
        all_scores = {
            "P1_identity": np.asarray([float(r["identity_mean"]) for r in rows], dtype=float),
            "P2_bug_rank": np.asarray([max(0.0, min(1.0, (-float(r["bug_spearman_r"]) + 1.0) / 2.0)) for r in rows], dtype=float),
            "P3_weak_mono": np.asarray([max(0.0, min(1.0, float(r["bug_weak_mono_pct"]) / 100.0)) for r in rows], dtype=float),
            "P4_stability": np.asarray([max(0.0, min(1.0, 1.0 - float(r["flip_rate"]))) for r in rows], dtype=float),
        }
        gaps = []
        for k in ["P1_identity", "P2_bug_rank", "P3_weak_mono", "P4_stability"]:
            arr = all_scores[k]
            v = prop_scores[k]
            pct = float(np.mean(arr <= v))
            z = float((v - np.mean(arr)) / np.std(arr)) if np.std(arr) > 0 else 0.0
            gaps.append({"property": k, "value": v, "percentile_lower_is_worse": pct, "zscore": z})

        bad_composite = float(np.mean(list(prop_scores.values())))
        all_composite = np.mean(
            np.column_stack([all_scores["P1_identity"], all_scores["P2_bug_rank"], all_scores["P3_weak_mono"], all_scores["P4_stability"]]),
            axis=1,
        )
        bad_gap = {
            "bad_judge_id": bad["judge_id"],
            "bad_human_corr": float(bad[f"human_spearman_r_{args.label_set}"]),
            "bad_composite_p1p4": bad_composite,
            "bad_composite_percentile": float(np.mean(all_composite <= bad_composite)),
            "per_property": gaps,
        }

    # Write outputs
    with (args.out_dir / "per_property_correlations.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(per_prop[0].keys()))
        w.writeheader()
        w.writerows(per_prop)
    with (args.out_dir / "partial_correlations.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(partial_rows[0].keys()))
        w.writeheader()
        w.writerows(partial_rows)
    (args.out_dir / "regression_summary.json").write_text(
        json.dumps({"r2": r2, "r2_perm_p": r2_p, "betas": beta_rows}, indent=2), encoding="utf-8"
    )

    # Plot simple bar chart (Spearman per property)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labels = [r["property"] for r in per_prop]
    vals = [r["spearman_r"] for r in per_prop]
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.bar(labels, vals)
    ax.set_ylim(-1, 1)
    ax.set_ylabel(f"Corr with human_spearman_{args.label_set}")
    ax.set_title("EXP17: Per-property correlation across judges")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(args.out_dir / "fig_property_vs_human_bars.png", dpi=180)
    plt.close(fig)

    final = {
        "experiment": "exp17_property_human_analysis",
        "input_summary": str(args.exp16_summary),
        "label_set": args.label_set,
        "n_judges": n,
        "per_property_correlations": per_prop,
        "partial_correlations": partial_rows,
        "regression": {"r2": r2, "r2_perm_p": r2_p, "betas": beta_rows},
        "bad_judge_gap": bad_gap,
    }
    (args.out_dir / "summary.json").write_text(json.dumps(final, indent=2), encoding="utf-8")

    md = []
    md.append("# EXP17 Property vs Human Analysis")
    md.append("")
    md.append(f"- Label set: `{args.label_set}`")
    md.append(f"- Judges: `{n}`")
    md.append(f"- Regression R2: `{r2:.3f}` (perm p=`{r2_p:.4f}`)")
    md.append("")
    md.append("## Per-property correlation (Spearman)")
    for r in per_prop:
        md.append(f"- {r['property']}: r={r['spearman_r']:.3f}, perm p={r['spearman_perm_p']:.4f}")
    md.append("")
    md.append("## Regression betas (standardized)")
    for b in beta_rows:
        md.append(f"- {b['property']}: beta={b['beta_std']:.3f}, perm p={b['beta_perm_p']:.4f}")
    if bad_gap is not None:
        md.append("")
        md.append(f"## Bad-judge gap: `{bad_gap['bad_judge_id']}`")
        md.append(f"- P1-P4 composite percentile: {bad_gap['bad_composite_percentile']:.3f}")
        md.append(f"- Human corr ({args.label_set}): {bad_gap['bad_human_corr']:.3f}")
    (args.out_dir / "results_summary.md").write_text("\n".join(md), encoding="utf-8")

    print("=" * 72)
    print("EXP17: Property-level analysis vs human correlation")
    print(f"label_set={args.label_set} n_judges={n}")
    print(f"Regression R2={r2:.3f} perm_p={r2_p:.4f}")
    for r in per_prop:
        print(f"  {r['property']}: spearman={r['spearman_r']:.3f} perm_p={r['spearman_perm_p']:.4f}")
    print(f"Wrote: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

