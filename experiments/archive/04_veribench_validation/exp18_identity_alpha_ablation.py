#!/usr/bin/env python3
"""
EXP18B: Alpha-sensitivity ablation on EXP16 results.

Recomputes identity component from EXP16 detail rows with and without ALPHA variants
and evaluates how cert->human trend changes.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import kendalltau, pearsonr, spearmanr


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXP16_SUMMARY = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust" / "summary.json"
DEFAULT_EXP16_DETAIL = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust" / "detail_rows.csv"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp18_identity_alpha_ablation"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP18B alpha-sensitivity ablation")
    p.add_argument("--exp16-summary", type=Path, default=DEFAULT_EXP16_SUMMARY)
    p.add_argument("--exp16-detail-rows", type=Path, default=DEFAULT_EXP16_DETAIL)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--bootstrap-iters", type=int, default=10000)
    p.add_argument("--perm-iters", type=int, default=20000)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def _bootstrap_ci_stat(x: np.ndarray, y: np.ndarray, fn, n_boot: int, seed: int) -> Tuple[float, float]:
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
        return (float("nan"), float("nan"))
    vals = np.sort(np.asarray(vals))
    lo = float(vals[int(0.025 * (len(vals) - 1))])
    hi = float(vals[int(0.975 * (len(vals) - 1))])
    return (lo, hi)


def _perm_pvalue_corr(x: np.ndarray, y: np.ndarray, fn, n_perm: int, seed: int) -> float:
    rng = np.random.default_rng(seed)
    obs = abs(float(fn(x, y)))
    ge = 0
    for _ in range(n_perm):
        yp = np.array(y, copy=True)
        rng.shuffle(yp)
        if abs(float(fn(x, yp))) >= obs:
            ge += 1
    return float((ge + 1) / (n_perm + 1))


def _compute_cert_index(identity_mean: float, bug_spearman_r: float, bug_weak_mono_pct: float, flip_rate: float) -> float:
    mono_rank = max(0.0, min(1.0, (-bug_spearman_r + 1.0) / 2.0))
    weak = max(0.0, min(1.0, bug_weak_mono_pct / 100.0))
    flip_stability = max(0.0, min(1.0, 1.0 - flip_rate))
    ident = max(0.0, min(1.0, identity_mean))
    return float(0.30 * ident + 0.30 * mono_rank + 0.25 * weak + 0.15 * flip_stability)


def _compute_trend(x: np.ndarray, y: np.ndarray, n_boot: int, n_perm: int, seed: int) -> dict:
    sp = float(spearmanr(x, y).statistic)
    pe = float(pearsonr(x, y).statistic)
    ke = float(kendalltau(x, y).statistic)
    sp_ci = _bootstrap_ci_stat(x, y, lambda a, b: spearmanr(a, b).statistic, n_boot, seed + 11)
    pe_ci = _bootstrap_ci_stat(x, y, lambda a, b: pearsonr(a, b).statistic, n_boot, seed + 13)
    ke_ci = _bootstrap_ci_stat(x, y, lambda a, b: kendalltau(a, b).statistic, n_boot, seed + 17)
    sp_p = _perm_pvalue_corr(x, y, lambda a, b: spearmanr(a, b).statistic, n_perm, seed + 101)
    pe_p = _perm_pvalue_corr(x, y, lambda a, b: pearsonr(a, b).statistic, n_perm, seed + 103)
    ke_p = _perm_pvalue_corr(x, y, lambda a, b: kendalltau(a, b).statistic, n_perm, seed + 107)
    return {
        "spearman_r": sp,
        "spearman_ci_lo": float(sp_ci[0]),
        "spearman_ci_hi": float(sp_ci[1]),
        "spearman_perm_p": float(sp_p),
        "pearson_r": pe,
        "pearson_ci_lo": float(pe_ci[0]),
        "pearson_ci_hi": float(pe_ci[1]),
        "pearson_perm_p": float(pe_p),
        "kendall_tau": ke,
        "kendall_ci_lo": float(ke_ci[0]),
        "kendall_ci_hi": float(ke_ci[1]),
        "kendall_perm_p": float(ke_p),
    }


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    summary = json.loads(args.exp16_summary.read_text(encoding="utf-8"))
    judge_rows: List[dict] = summary["judge_rows"]

    # Gather identity probe means by judge and variant type from detail rows.
    by_judge_variant: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    with args.exp16_detail_rows.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("row_type") != "property_identity":
                continue
            jid = row["judge_id"]
            item_key = row["item_key"]
            # item_key format: "<problem>::<VARIANT>"
            parts = item_key.split("::")
            if len(parts) < 2:
                continue
            variant = parts[-1].strip().upper()
            s = float(row["score_mean"])
            by_judge_variant[jid][variant].append(s)

    updated_rows = []
    for r in judge_rows:
        jid = r["judge_id"]
        vmap = by_judge_variant.get(jid, {})
        all_scores: List[float] = []
        no_alpha: List[float] = []
        for vname, vals in vmap.items():
            all_scores.extend(vals)
            if vname != "ALPHA":
                no_alpha.extend(vals)
        identity_all = float(np.mean(all_scores)) if all_scores else float(r["identity_mean"])
        identity_no_alpha = float(np.mean(no_alpha)) if no_alpha else identity_all

        cert_all = _compute_cert_index(identity_all, float(r["bug_spearman_r"]), float(r["bug_weak_mono_pct"]), float(r["flip_rate"]))
        cert_no_alpha = _compute_cert_index(identity_no_alpha, float(r["bug_spearman_r"]), float(r["bug_weak_mono_pct"]), float(r["flip_rate"]))

        out = dict(r)
        out["identity_mean_from_detail_all"] = identity_all
        out["identity_mean_no_alpha"] = identity_no_alpha
        out["cert_index_v1_recomputed_all"] = cert_all
        out["cert_index_v1_no_alpha"] = cert_no_alpha
        out["identity_delta_no_alpha_minus_all"] = identity_no_alpha - identity_all
        out["cert_delta_no_alpha_minus_all"] = cert_no_alpha - cert_all
        updated_rows.append(out)

    trend = {}
    x_all = np.asarray([r["cert_index_v1_recomputed_all"] for r in updated_rows], dtype=float)
    x_no_alpha = np.asarray([r["cert_index_v1_no_alpha"] for r in updated_rows], dtype=float)
    for label in ["pass1", "pass2", "avg"]:
        y = np.asarray([r[f"human_spearman_r_{label}"] for r in updated_rows], dtype=float)
        trend[label] = {
            "all_variants": _compute_trend(x_all, y, args.bootstrap_iters, args.perm_iters, args.seed + 200),
            "exclude_alpha": _compute_trend(x_no_alpha, y, args.bootstrap_iters, args.perm_iters, args.seed + 300),
        }

    # write rows
    out_csv = args.out_dir / "judge_rows_alpha_ablation.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(updated_rows[0].keys()))
        w.writeheader()
        w.writerows(updated_rows)

    # figure
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [r["judge_id"] for r in updated_rows]
    deltas = [r["identity_delta_no_alpha_minus_all"] for r in updated_rows]
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    ax.bar(range(len(labels)), deltas)
    ax.axhline(0.0, color="k", linewidth=0.8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("Identity delta (exclude ALPHA - all variants)")
    ax.set_title("EXP18B: Alpha-sensitivity ablation on identity")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(args.out_dir / "fig_identity_alpha_ablation.png", dpi=180)
    plt.close(fig)

    final = {
        "experiment": "exp18_identity_alpha_ablation",
        "exp16_summary": str(args.exp16_summary),
        "exp16_detail_rows": str(args.exp16_detail_rows),
        "n_judges": len(updated_rows),
        "trend_by_label_set": trend,
        "notes": {
            "all_variants": "identity computed over all identity variants including ALPHA",
            "exclude_alpha": "identity computed excluding ALPHA rows; proxy for alpha-normalization mitigation",
        },
    }
    (args.out_dir / "summary.json").write_text(json.dumps(final, indent=2), encoding="utf-8")

    print("=" * 72)
    print("EXP18B: identity alpha ablation")
    print(f"n_judges={len(updated_rows)}")
    for label in ["pass1", "pass2", "avg"]:
        a = trend[label]["all_variants"]
        b = trend[label]["exclude_alpha"]
        print(
            f"{label}: all Spearman={a['spearman_r']:.3f} (p={a['spearman_perm_p']:.4g}) | "
            f"no-alpha Spearman={b['spearman_r']:.3f} (p={b['spearman_perm_p']:.4g})"
        )
    print(f"Wrote: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

