#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr, spearmanr


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Figure-3-style monotonicity plots for Claude Opus runs.")
    p.add_argument("--detail-rows", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--repeat-agg", choices=["mean", "median"], default="median")
    p.add_argument(
        "--judge-ids",
        type=str,
        default="claude-opus-4-7|P8_STRICT_B,claude-opus-4-7|P4_CHECKLIST,claude-opus-4-7|P1_BASELINE",
        help="Comma-separated judge IDs to render as 3 Figure-3 style panels.",
    )
    p.add_argument("--title", type=str, default="Claude Opus 4.7 Monotonicity (Figure-3 style)")
    p.add_argument("--stem", type=str, default="fig3_style_claude_opus_monotonicity")
    return p.parse_args()


def _agg(scores_text: str, mode: str) -> float:
    vals = np.asarray(json.loads(scores_text), dtype=float)
    return float(np.mean(vals) if mode == "mean" else np.median(vals))


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    judges = [x.strip() for x in args.judge_ids.split(",") if x.strip()]
    judge_set = set(judges)

    # judge -> level -> list of robust scores across problems
    by_judge_level = defaultdict(lambda: defaultdict(list))
    # judge -> x(level per problem) and y(score) for raw corr
    raw_xy = defaultdict(lambda: {"x": [], "y": []})

    with args.detail_rows.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            jid = r["judge_id"]
            if jid not in judge_set:
                continue
            if r["row_type"] != "property_bug":
                continue
            parts = r["item_key"].split("::")
            if len(parts) < 2 or not parts[1].startswith("L"):
                continue
            lvl = int(parts[1][1:])
            s = _agg(r["repeat_scores"], args.repeat_agg)
            by_judge_level[jid][lvl].append(s)
            raw_xy[jid]["x"].append(lvl)
            raw_xy[jid]["y"].append(s)

    fig, axes = plt.subplots(1, 3, figsize=(14.8, 4.6), sharey=True)
    for ax, jid in zip(axes, judges):
        levels = sorted(by_judge_level[jid].keys())
        means, ses = [], []
        for lv in levels:
            arr = np.asarray(by_judge_level[jid][lv], dtype=float)
            means.append(float(np.mean(arr)))
            ses.append(float(np.std(arr, ddof=1) / np.sqrt(len(arr))) if len(arr) > 1 else 0.0)

        x = np.asarray(raw_xy[jid]["x"], dtype=float)
        y = np.asarray(raw_xy[jid]["y"], dtype=float)
        sp = float(spearmanr(x, y).statistic)
        pr = float(pearsonr(x, y).statistic)

        ax.errorbar(levels, means, yerr=ses, marker="o", linewidth=2.0, capsize=3)
        if len(levels) >= 2:
            m, b = np.polyfit(np.asarray(levels, dtype=float), np.asarray(means, dtype=float), 1)
            xs = np.linspace(min(levels), max(levels), 100)
            ax.plot(xs, m * xs + b, "r--", alpha=0.8)

        ax.set_title(f"{jid.split('|')[1]}\nSpearman={sp:.3f}, Pearson={pr:.3f}")
        ax.set_xlabel("Bug level (L0 clean → L4)")
        ax.set_xticks([0, 1, 2, 3, 4])
        ax.grid(alpha=0.25)

    axes[0].set_ylabel("Judge score (robust aggregate, mean ± SE)")
    fig.suptitle(args.title)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    out = args.out_dir / f"{args.stem}.png"
    fig.savefig(out, dpi=220)
    plt.close(fig)

    # pooled panel
    x_all, y_all = [], []
    for jid in judges:
        x_all.extend(raw_xy[jid]["x"])
        y_all.extend(raw_xy[jid]["y"])
    x_all = np.asarray(x_all, dtype=float)
    y_all = np.asarray(y_all, dtype=float)
    sp_all = float(spearmanr(x_all, y_all).statistic)
    pr_all = float(pearsonr(x_all, y_all).statistic)

    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    ax.scatter(x_all + np.random.default_rng(42).uniform(-0.05, 0.05, size=len(x_all)), y_all, s=15, alpha=0.45)
    m, b = np.polyfit(x_all, y_all, 1)
    xs = np.linspace(0, 4, 100)
    ax.plot(xs, m * xs + b, "r--", linewidth=2)
    ax.set_title(f"Pooled Opus monotonicity: Spearman={sp_all:.3f}, Pearson={pr_all:.3f}")
    ax.set_xlabel("Bug level")
    ax.set_ylabel("Judge score")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    out2 = args.out_dir / f"{args.stem}_pooled.png"
    fig.savefig(out2, dpi=220)
    plt.close(fig)

    summary = {
        "judges": judges,
        "repeat_agg": args.repeat_agg,
        "per_judge": {
            jid: {
                "spearman_bug_level_vs_score": float(spearmanr(np.asarray(raw_xy[jid]["x"], dtype=float), np.asarray(raw_xy[jid]["y"], dtype=float)).statistic),
                "pearson_bug_level_vs_score": float(pearsonr(np.asarray(raw_xy[jid]["x"], dtype=float), np.asarray(raw_xy[jid]["y"], dtype=float))[0]),
                "n_points": int(len(raw_xy[jid]["x"])),
            }
            for jid in judges
        },
        "pooled": {
            "spearman_bug_level_vs_score": sp_all,
            "pearson_bug_level_vs_score": pr_all,
            "n_points": int(len(x_all)),
        },
        "outputs": {
            "fig3_style": str(out),
            "fig3_style_pooled": str(out2),
        },
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
