#!/usr/bin/env python3
"""
EXP13B: Statistical significance for threshold deltas (paired by item).

Given exp13 detail_rows.csv and threshold list:
- computes per-item flip/pass indicators at each threshold
- compares each threshold against a reference threshold (default 0.85)
- reports paired delta estimates with bootstrap CI and paired-permutation p-values
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, List

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
EXP_DIR = REPO_ROOT / "experiments" / "02_reviewer_response_neurips_math_ai_2026"
DEFAULT_IN = EXP_DIR / "results" / "threshold_calibration_sweep" / "detail_rows.csv"
DEFAULT_OUT = EXP_DIR / "results" / "threshold_calibration_sweep_significance"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP13B threshold significance tests")
    p.add_argument("--detail-rows-csv", type=Path, default=DEFAULT_IN)
    p.add_argument("--thresholds", type=str, default="0.6,0.65,0.7,0.75,0.8,0.85")
    p.add_argument("--reference-threshold", type=float, default=0.85)
    p.add_argument("--bootstrap-iters", type=int, default=10000)
    p.add_argument("--perm-iters", type=int, default=20000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    return p.parse_args()


def _parse_thresholds(raw: str) -> List[float]:
    vals = sorted({float(x.strip()) for x in raw.split(",") if x.strip()})
    vals = [v for v in vals if 0.0 <= v <= 1.0]
    if not vals:
        raise ValueError("No valid thresholds in [0,1]")
    return vals


def _load_items(path: Path) -> Dict[str, dict]:
    items: Dict[str, dict] = {}
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            key = f"{row['split']}::{row['file']}::{row['task']}::{row['item']}::{row['level']}"
            reps = json.loads(row["repeat_scores"])
            reps = [float(x) for x in reps]
            if not reps:
                continue
            items[key] = {
                "split": row["split"],
                "task": row["task"],
                "mean": float(row["score_mean"]),
                "reps": reps,
            }
    return items


def _flip_indicator(reps: List[float], t: float) -> int:
    decs = [x >= t for x in reps]
    return int(len(set(decs)) > 1)


def _pass_indicator(mean_score: float, t: float) -> int:
    return int(mean_score >= t)


def _bootstrap_ci(d: np.ndarray, n_boot: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(d)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        vals.append(float(np.mean(d[idx])))
    vals = np.sort(np.asarray(vals, dtype=float))
    lo = float(vals[int(0.025 * (len(vals) - 1))])
    hi = float(vals[int(0.975 * (len(vals) - 1))])
    return (lo, hi)


def _perm_paired_signed(d: np.ndarray, n_perm: int, seed: int) -> float:
    # Paired sign-flip permutation on per-item differences.
    rng = np.random.default_rng(seed)
    obs = abs(float(np.mean(d)))
    n = len(d)
    ge = 0
    for _ in range(n_perm):
        signs = rng.choice([-1.0, 1.0], size=n)
        val = abs(float(np.mean(d * signs)))
        if val >= obs:
            ge += 1
    return float((ge + 1) / (n_perm + 1))


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    thresholds = _parse_thresholds(args.thresholds)
    if args.reference_threshold not in thresholds:
        thresholds = sorted(set(thresholds + [args.reference_threshold]))

    items = _load_items(args.detail_rows_csv)
    if not items:
        raise ValueError("No rows loaded from detail_rows_csv")

    keys = sorted(items.keys())
    ref_t = float(args.reference_threshold)

    rows = []
    for t in thresholds:
        t = float(t)
        flip_ref = np.asarray([_flip_indicator(items[k]["reps"], ref_t) for k in keys], dtype=float)
        flip_t = np.asarray([_flip_indicator(items[k]["reps"], t) for k in keys], dtype=float)
        pass_ref = np.asarray([_pass_indicator(items[k]["mean"], ref_t) for k in keys], dtype=float)
        pass_t = np.asarray([_pass_indicator(items[k]["mean"], t) for k in keys], dtype=float)

        # positive delta_flip means t has higher flip rate than reference
        d_flip = flip_t - flip_ref
        d_pass = pass_t - pass_ref

        d_flip_mean = float(np.mean(d_flip))
        d_pass_mean = float(np.mean(d_pass))
        d_flip_ci = _bootstrap_ci(d_flip, args.bootstrap_iters, args.seed + int(round(t * 1000)) + 11)
        d_pass_ci = _bootstrap_ci(d_pass, args.bootstrap_iters, args.seed + int(round(t * 1000)) + 13)
        p_flip = _perm_paired_signed(d_flip, args.perm_iters, args.seed + int(round(t * 1000)) + 101)
        p_pass = _perm_paired_signed(d_pass, args.perm_iters, args.seed + int(round(t * 1000)) + 103)

        rows.append(
            {
                "threshold": t,
                "reference_threshold": ref_t,
                "delta_flip_rate_vs_ref": d_flip_mean,
                "delta_flip_ci_lo": float(d_flip_ci[0]),
                "delta_flip_ci_hi": float(d_flip_ci[1]),
                "delta_flip_perm_p": p_flip,
                "delta_pass_rate_vs_ref": d_pass_mean,
                "delta_pass_ci_lo": float(d_pass_ci[0]),
                "delta_pass_ci_hi": float(d_pass_ci[1]),
                "delta_pass_perm_p": p_pass,
            }
        )

    rows = sorted(rows, key=lambda r: r["threshold"])

    out_csv = args.out_dir / "threshold_delta_significance.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    summary = {
        "experiment": "exp13_threshold_significance",
        "detail_rows_csv": str(args.detail_rows_csv),
        "n_items": len(keys),
        "thresholds": thresholds,
        "reference_threshold": ref_t,
        "bootstrap_iters": args.bootstrap_iters,
        "perm_iters": args.perm_iters,
        "rows": rows,
        "notes": {
            "delta_flip_rate_vs_ref": "mean(flip_t - flip_ref); positive means threshold t flips more than reference",
            "delta_pass_rate_vs_ref": "mean(pass_t - pass_ref); positive means threshold t passes more than reference",
            "test": "paired sign-flip permutation on per-item deltas",
        },
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # quick plot
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    xs = [r["threshold"] for r in rows]
    dflip = [r["delta_flip_rate_vs_ref"] for r in rows]
    dflip_lo = [r["delta_flip_ci_lo"] for r in rows]
    dflip_hi = [r["delta_flip_ci_hi"] for r in rows]
    dpass = [r["delta_pass_rate_vs_ref"] for r in rows]
    dpass_lo = [r["delta_pass_ci_lo"] for r in rows]
    dpass_hi = [r["delta_pass_ci_hi"] for r in rows]

    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.axhline(0.0, color="k", linewidth=0.8)
    ax.plot(xs, dflip, marker="o", color="#d62728", label="Δ flip vs ref")
    ax.fill_between(xs, dflip_lo, dflip_hi, color="#d62728", alpha=0.15)
    ax.plot(xs, dpass, marker="s", color="#1f77b4", label="Δ pass vs ref")
    ax.fill_between(xs, dpass_lo, dpass_hi, color="#1f77b4", alpha=0.15)
    ax.set_xlabel("Threshold")
    ax.set_ylabel("Delta rate vs reference")
    ax.set_title(f"Threshold deltas vs reference t={ref_t:.2f}")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.out_dir / "fig_threshold_delta_significance.png", dpi=180)
    plt.close(fig)

    print("=" * 72)
    print("EXP13B: threshold significance")
    print(f"n_items={len(keys)} reference_t={ref_t}")
    for r in rows:
        print(
            f"t={r['threshold']:.2f}: Δflip={r['delta_flip_rate_vs_ref']:.4f} "
            f"[{r['delta_flip_ci_lo']:.4f},{r['delta_flip_ci_hi']:.4f}] p={r['delta_flip_perm_p']:.4g} | "
            f"Δpass={r['delta_pass_rate_vs_ref']:.4f} [{r['delta_pass_ci_lo']:.4f},{r['delta_pass_ci_hi']:.4f}] "
            f"p={r['delta_pass_perm_p']:.4g}"
        )
    print(f"Wrote: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

