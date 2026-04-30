#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
DROP_CSV = REPO_ROOT / "experiments/04_veribench_validation/results_exp24_alpha_canonicalized_identity_drop/identity_alpha_canonicalized_summary.csv"
CLIP_CSV = REPO_ROOT / "experiments/04_veribench_validation/results_exp24_alpha_canonicalized_identity_clip/identity_alpha_canonicalized_summary.csv"
OUT_PLOT = REPO_ROOT / "paper_latex/NeurIPS_2025/figures/exp24_alpha_canonicalized_identity/fig_identity_variance_fig9_style.png"
OUT_SUMMARY = REPO_ROOT / "experiments/04_veribench_validation/results_exp24_alpha_canonicalized_identity_compare/summary.json"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plot alpha-canonicalized identity variance (Fig9 style)")
    p.add_argument("--drop-csv", type=Path, default=DROP_CSV)
    p.add_argument("--clip-csv", type=Path, default=CLIP_CSV)
    p.add_argument("--out-plot", type=Path, default=OUT_PLOT)
    p.add_argument("--out-summary", type=Path, default=OUT_SUMMARY)
    p.add_argument("--dpi", type=int, default=180)
    return p.parse_args()


def read_csv(path: Path):
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def main() -> int:
    args = parse_args()
    drop_rows = read_csv(args.drop_csv)
    clip_rows = read_csv(args.clip_csv)

    by_j_drop = {r["judge_id"]: r for r in drop_rows}
    by_j_clip = {r["judge_id"]: r for r in clip_rows}
    judges = sorted(set(by_j_drop).intersection(by_j_clip))

    original = np.asarray([float(by_j_drop[j]["identity_std_original"]) for j in judges], dtype=float)
    drop = np.asarray([float(by_j_drop[j]["identity_std_alpha_canon"]) for j in judges], dtype=float)
    clip = np.asarray([float(by_j_clip[j]["identity_std_alpha_canon"]) for j in judges], dtype=float)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x = np.arange(len(judges))
    width = 0.26

    fig, ax = plt.subplots(figsize=(max(10.5, 0.9 * len(judges)), 4.8))
    ax.bar(x - width, original, width=width, label="Original identity std", color="#4C78A8")
    ax.bar(x, drop, width=width, label="Alpha-canonicalized (drop)", color="#F58518")
    ax.bar(x + width, clip, width=width, label="Alpha-canonicalized (clip)", color="#54A24B")

    ax.set_xticks(x)
    ax.set_xticklabels(judges, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("Std dev of identity scores")
    ax.set_title("Identity Variance: Original vs Alpha-Canonicalized (Fig9-style bars)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()

    args.out_plot.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out_plot, dpi=args.dpi)
    plt.close(fig)

    args.out_summary.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "n_judges": len(judges),
        "mean_original_std": float(np.mean(original)),
        "mean_drop_std": float(np.mean(drop)),
        "mean_clip_std": float(np.mean(clip)),
        "mean_pct_reduction_drop": float(np.mean((original - drop) / np.maximum(original, 1e-12) * 100.0)),
        "mean_pct_reduction_clip": float(np.mean((original - clip) / np.maximum(original, 1e-12) * 100.0)),
        "inputs": {"drop_csv": str(args.drop_csv), "clip_csv": str(args.clip_csv)},
        "output_plot": str(args.out_plot),
    }
    args.out_summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
