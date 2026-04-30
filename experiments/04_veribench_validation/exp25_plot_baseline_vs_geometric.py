#!/usr/bin/env python3
"""
EXP25: Baseline cert_index vs geometric trust-index (mono, stab) re-aggregation.

Reads an EXP16 summary.json (no model calls), computes a 2-component geometric
trust index over per-judge mono and stab signals, and compares its Spearman
correlation with the human label set against the baseline cert_index_v1
already recorded in the summary.

Index definition:
  mono     = (1 - bug_spearman_r) / 2    # in [0, 1], higher is better
  stab     = 1 - flip_rate                # in [0, 1], higher is better
  TI_geom  = mono^0.4 * stab^0.6
           = exp(0.4*log(mono) + 0.6*log(stab))

Outputs (per --label-set):
  - summary.json with rho_baseline and rho_geometric
  - fig7_trend_update_baseline_vs_geom.png
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import List, Tuple

import numpy as np
from scipy.stats import spearmanr


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Baseline vs geometric (mono, stab) trust-index plot")
    p.add_argument("--summary-json", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--label-set", choices=["pass1", "pass2", "avg"], required=True)
    p.add_argument("--w-mono", type=float, default=0.4)
    p.add_argument("--w-stab", type=float, default=0.6)
    p.add_argument("--eps", type=float, default=1e-6)
    p.add_argument("--bootstrap-iters", type=int, default=10000)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def _bootstrap_ci_spearman(x: np.ndarray, y: np.ndarray, n_boot: int, seed: int) -> Tuple[float, float]:
    if len(x) < 3:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    n = len(x)
    vals: List[float] = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        v = float(spearmanr(x[idx], y[idx]).statistic)
        if math.isfinite(v):
            vals.append(v)
    if not vals:
        return (float("nan"), float("nan"))
    arr = np.sort(np.asarray(vals, dtype=float))
    lo = float(arr[int(0.025 * (len(arr) - 1))])
    hi = float(arr[int(0.975 * (len(arr) - 1))])
    return (lo, hi)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    summary = json.loads(args.summary_json.read_text(encoding="utf-8"))
    rows = summary["judge_rows"]

    judge_ids = [r["judge_id"] for r in rows]
    bug_r = np.asarray([float(r["bug_spearman_r"]) for r in rows], dtype=float)
    flip = np.asarray([float(r["flip_rate"]) for r in rows], dtype=float)
    human_r = np.asarray(
        [float(r[f"human_spearman_r_{args.label_set}"]) for r in rows], dtype=float
    )
    cert_index = np.asarray(
        [float(r.get("cert_index", float("nan"))) for r in rows], dtype=float
    )

    mono = np.clip((1.0 - bug_r) / 2.0, 0.0, 1.0)
    stab = np.clip(1.0 - flip, 0.0, 1.0)
    eps = float(args.eps)
    log_geom = args.w_mono * np.log(np.clip(mono, eps, 1.0)) + args.w_stab * np.log(
        np.clip(stab, eps, 1.0)
    )
    geo = np.exp(log_geom)

    # rho_baseline: existing cert_index_v1 vs human Spearman, recomputed to
    # match the geometric pipeline exactly (same n, same y).
    mask = np.isfinite(cert_index) & np.isfinite(human_r)
    if mask.sum() >= 3:
        rho_base = float(spearmanr(cert_index[mask], human_r[mask]).statistic)
        base_lo, base_hi = _bootstrap_ci_spearman(
            cert_index[mask], human_r[mask], args.bootstrap_iters, args.seed
        )
    else:
        rho_base, base_lo, base_hi = float("nan"), float("nan"), float("nan")

    rho_geom = float(spearmanr(geo, human_r).statistic)
    geom_lo, geom_hi = _bootstrap_ci_spearman(
        geo, human_r, args.bootstrap_iters, args.seed
    )

    # Also surface the baseline rho already cached in the summary for sanity.
    cached_baseline = (
        summary.get("trend_by_set", {})
        .get(args.label_set, {})
        .get("trend_v1", {})
        .get("spearman_r", float("nan"))
    )

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6), sharey=True)
    titles = [
        f"Baseline cert_index  (rho={rho_base:.3f})",
        f"Geometric mono^{args.w_mono:g} * stab^{args.w_stab:g}  (rho={rho_geom:.3f})",
    ]
    xs_pair = [cert_index, geo]
    for ax, x, title in zip(axes, xs_pair, titles):
        finite = np.isfinite(x) & np.isfinite(human_r)
        ax.scatter(x[finite], human_r[finite], s=42, color="#1f77b4", edgecolor="black", linewidth=0.5)
        for i, jid in enumerate(judge_ids):
            if not finite[i]:
                continue
            short = jid.replace("claude-3-7-sonnet-20250219|", "C37|").replace("BAD_STRINGY", "BAD")
            ax.annotate(short, (x[i], human_r[i]), fontsize=7, alpha=0.75, xytext=(3, 3), textcoords="offset points")
        if finite.sum() >= 2:
            xa = x[finite]
            ya = human_r[finite]
            try:
                m, b = np.polyfit(xa, ya, 1)
                xl = np.linspace(float(np.min(xa)), float(np.max(xa)), 50)
                ax.plot(xl, m * xl + b, "--", color="#d62728", linewidth=1.2, alpha=0.7)
            except Exception:
                pass
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("trust index (per judge)")
        ax.grid(alpha=0.25)
    axes[0].set_ylabel(f"human Spearman r ({args.label_set})")
    fig.suptitle(
        f"EXP25 Trend update: baseline vs geometric (label_set={args.label_set}, n_judges={len(judge_ids)})",
        fontsize=11,
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.96))
    fig_path = args.out_dir / "fig7_trend_update_baseline_vs_geom.png"
    fig.savefig(fig_path, dpi=180)
    plt.close(fig)

    out_rows = []
    for i, jid in enumerate(judge_ids):
        out_rows.append(
            {
                "judge_id": jid,
                "bug_spearman_r": float(bug_r[i]),
                "flip_rate": float(flip[i]),
                "mono": float(mono[i]),
                "stab": float(stab[i]),
                "cert_index_baseline": float(cert_index[i]) if math.isfinite(cert_index[i]) else None,
                "geo_trust_index": float(geo[i]),
                "human_spearman_r": float(human_r[i]) if math.isfinite(human_r[i]) else None,
            }
        )

    summary_out = {
        "experiment": "exp25_plot_baseline_vs_geometric",
        "source_summary": str(args.summary_json),
        "label_set": args.label_set,
        "n_judges": len(judge_ids),
        "formula": "TI_geom = mono^w_mono * stab^w_stab = exp(w_mono*log(mono) + w_stab*log(stab))",
        "weights": {"mono": float(args.w_mono), "stab": float(args.w_stab)},
        "eps": eps,
        "rho_baseline": rho_base,
        "rho_baseline_ci_lo": base_lo,
        "rho_baseline_ci_hi": base_hi,
        "rho_baseline_cached_from_summary": cached_baseline,
        "rho_geometric": rho_geom,
        "rho_geometric_ci_lo": geom_lo,
        "rho_geometric_ci_hi": geom_hi,
        "improvement": rho_geom - rho_base if math.isfinite(rho_geom) and math.isfinite(rho_base) else float("nan"),
        "geometric_better_than_baseline": bool(rho_geom > rho_base) if math.isfinite(rho_geom) and math.isfinite(rho_base) else None,
        "fig_path": str(fig_path),
        "rows": out_rows,
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary_out, indent=2), encoding="utf-8")

    print("=" * 72)
    print(f"EXP25 baseline-vs-geometric  label_set={args.label_set}")
    print(f"  rho_baseline  = {rho_base:.4f}  CI=[{base_lo:.3f},{base_hi:.3f}]")
    print(f"  rho_geometric = {rho_geom:.4f}  CI=[{geom_lo:.3f},{geom_hi:.3f}]")
    print(f"  improvement   = {summary_out['improvement']:+.4f}  geom_better={summary_out['geometric_better_than_baseline']}")
    print(f"  fig: {fig_path}")
    print(f"  out: {args.out_dir}/summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
