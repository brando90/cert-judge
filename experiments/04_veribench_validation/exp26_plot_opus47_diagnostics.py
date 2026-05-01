#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plot OPUS47 per-judge monotonicity + flip diagnostics.")
    p.add_argument("--judge-rows", type=Path, required=True)
    p.add_argument("--reversal-csv", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    return p.parse_args()


def _label(jid: str) -> str:
    if "|" in jid:
        m, p = jid.split("|", 1)
        return f"{m}\n{p}"
    return jid


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    with args.judge_rows.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)

    rev = {}
    with args.reversal_csv.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rev[r["judge_id"]] = r

    judge_ids = [r["judge_id"] for r in rows]
    x = np.arange(len(judge_ids))
    labels = [_label(j) for j in judge_ids]

    # Figure A: per-judge monotonicity metrics.
    bug_rank = np.asarray([max(0.0, min(1.0, (-float(r["bug_spearman_r"]) + 1.0) / 2.0)) for r in rows], dtype=float)
    weak_mono = np.asarray([float(r["bug_weak_mono_pct"]) / 100.0 for r in rows], dtype=float)
    rev_inv = np.asarray([1.0 - float(rev.get(j, {}).get("reversal_rate", 0.0)) for j in judge_ids], dtype=float)

    width = 0.25
    fig, ax = plt.subplots(figsize=(12.8, 5.2))
    ax.bar(x - width, bug_rank, width=width, label="P2 rank monotonicity", color="#4e79a7")
    ax.bar(x, weak_mono, width=width, label="P3 weak monotonicity", color="#59a14f")
    ax.bar(x + width, rev_inv, width=width, label="1 - local reversal rate", color="#f28e2b")
    ax.set_ylim(0.0, 1.05)
    ax.set_ylabel("Score (higher is better)")
    ax.set_title("Opus47: per-judge monotonicity diagnostics")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper left")
    fig.tight_layout()
    fig.savefig(args.out_dir / "fig_opus47_per_judge_monotonicity.png", dpi=200)
    plt.close(fig)

    # Figure B: flip rates with small/error-bar method: binomial SE.
    flip = np.asarray([float(r["flip_rate"]) for r in rows], dtype=float)
    # 72 pairs in exp16 for opus47.
    n = 72.0
    se = np.sqrt(np.clip(flip * (1.0 - flip) / n, 0.0, None))

    fig, ax = plt.subplots(figsize=(12.8, 4.8))
    ax.bar(x, flip, yerr=se, color="#e15759", capsize=3)
    ax.set_ylim(0.0, max(0.20, float(np.max(flip) * 1.2 + 0.01)))
    ax.set_ylabel("Flip rate at threshold t=0.85")
    ax.set_title("Opus47: repeat-call decision flip rate (mean ± SE)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(args.out_dir / "fig_opus47_flip_rate_se.png", dpi=200)
    plt.close(fig)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

