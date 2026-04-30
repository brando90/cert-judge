#!/usr/bin/env python3
"""
EXP19: Low-variance replot package for EXP16 detail rows.

Purpose:
- Produce cleaner monotonicity curves for main judges using robust repeat aggregation.
- Separate failure modes (alpha sensitivity, local bug reversals) into dedicated plots.
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


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DETAIL_ROWS = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust" / "detail_rows.csv"
DEFAULT_JUDGE_ROWS = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp16_final_robust" / "judge_rows.csv"
DEFAULT_OUT_DIR = REPO_ROOT / "experiments" / "04_veribench_validation" / "results_exp19_low_variance_replot"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EXP19 low-variance replot for EXP16 detail rows")
    p.add_argument("--detail-rows", type=Path, default=DEFAULT_DETAIL_ROWS)
    p.add_argument("--judge-rows", type=Path, default=DEFAULT_JUDGE_ROWS)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument(
        "--repeat-agg",
        choices=["mean", "median"],
        default="median",
        help="How to aggregate repeat_scores within each item before curve stats.",
    )
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--bootstrap-iters", type=int, default=4000)
    return p.parse_args()


def _agg_repeat_scores(repeat_scores_text: str, agg: str) -> float:
    vals = json.loads(repeat_scores_text)
    arr = np.asarray(vals, dtype=float)
    if agg == "mean":
        return float(np.mean(arr))
    return float(np.median(arr))


def _bootstrap_ci(vals: np.ndarray, n_boot: int, seed: int) -> Tuple[float, float]:
    if len(vals) == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    out: List[float] = []
    n = len(vals)
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        out.append(float(np.mean(vals[idx])))
    out = np.sort(np.asarray(out))
    lo = float(out[int(0.025 * (len(out) - 1))])
    hi = float(out[int(0.975 * (len(out) - 1))])
    return (lo, hi)


def _is_main_gpt53(jid: str) -> bool:
    main_prefixes = (
        "gpt-5.3-codex|",
        "claude-3-7-sonnet-20250219|",
    )
    return jid.startswith(main_prefixes) and ("BAD_STRINGY" not in jid)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    # Load judge rows for ordering and labels.
    judge_rows: List[dict] = []
    with args.judge_rows.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            judge_rows.append(row)
    judge_ids = [r["judge_id"] for r in judge_rows]

    # Parse detail rows into robust per-item scores.
    # bug_by_judge_problem[jid][problem][level] = robust score
    bug_by_judge_problem: Dict[str, Dict[str, Dict[int, float]]] = defaultdict(lambda: defaultdict(dict))
    # id_by_judge_variant[jid][variant] -> list[robust score]
    id_by_judge_variant: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    with args.detail_rows.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            jid = row["judge_id"]
            item_key = row["item_key"]
            row_type = row["row_type"]
            rep = row["repeat_scores"]
            score = _agg_repeat_scores(rep, args.repeat_agg)
            parts = item_key.split("::")
            if len(parts) < 2:
                continue
            if row_type == "property_bug":
                problem = parts[0]
                lvl_txt = parts[1].upper().strip()
                if not lvl_txt.startswith("L"):
                    continue
                try:
                    lvl = int(lvl_txt[1:])
                except Exception:
                    continue
                bug_by_judge_problem[jid][problem][lvl] = score
            elif row_type == "property_identity":
                variant = parts[-1].upper().strip()
                id_by_judge_variant[jid][variant].append(score)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # ---------------------------
    # Plot 1: main monotonicity curves (lower-variance view)
    # ---------------------------
    main_jids = [j for j in judge_ids if _is_main_gpt53(j)]
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    color_cycle = plt.rcParams["axes.prop_cycle"].by_key().get("color", ["C0", "C1", "C2"])
    trend_rows: List[dict] = []
    for i, jid in enumerate(main_jids):
        by_problem = bug_by_judge_problem.get(jid, {})
        xs: List[int] = []
        ys: List[float] = []
        lo: List[float] = []
        hi: List[float] = []
        for lvl in [0, 1, 2, 3, 4]:
            v = []
            for _, ladder in by_problem.items():
                if lvl in ladder:
                    v.append(ladder[lvl])
            arr = np.asarray(v, dtype=float)
            if len(arr) == 0:
                continue
            m = float(np.mean(arr))
            cil, cih = _bootstrap_ci(arr, args.bootstrap_iters, args.seed + i * 100 + lvl)
            xs.append(lvl)
            ys.append(m)
            lo.append(cil)
            hi.append(cih)
            trend_rows.append(
                {
                    "judge_id": jid,
                    "bug_level": lvl,
                    "mean_score": m,
                    "ci_lo": cil,
                    "ci_hi": cih,
                    "n_problems": int(len(arr)),
                }
            )
        c = color_cycle[i % len(color_cycle)]
        ax.plot(xs, ys, marker="o", linewidth=2.0, label=jid.split("|", 1)[1], color=c)
        ax.fill_between(xs, lo, hi, alpha=0.16, color=c)
    ax.set_xlabel("Bug level (L0 clean \u2192 L4 most degraded)")
    ax.set_ylabel("Judge score (robust aggregate)")
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_xticklabels(["0", "1", "2", "3", "4"])
    ax.set_title(f"EXP19 Main Monotonicity Curves ({args.repeat_agg} over repeats)")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(args.out_dir / "fig_main_monotonicity_lowvar.png", dpi=180)
    plt.close(fig)

    # ---------------------------
    # Plot 2: alpha sensitivity as separate failure-mode plot
    # ---------------------------
    variants = ["RENAME", "REORDER", "STYLE", "ALPHA"]
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    x = np.arange(len(judge_ids))
    width = 0.18
    for k, vname in enumerate(variants):
        vals = []
        for jid in judge_ids:
            arr = np.asarray(id_by_judge_variant.get(jid, {}).get(vname, []), dtype=float)
            vals.append(float(np.mean(arr)) if len(arr) else float("nan"))
        ax.bar(x + (k - 1.5) * width, vals, width=width, label=vname)
    ax.set_xticks(x)
    ax.set_xticklabels(judge_ids, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("Identity probe score")
    ax.set_title("EXP19 Failure Mode: Identity Variant Breakdown (ALPHA isolated)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, ncol=4, fontsize=8)
    fig.tight_layout()
    fig.savefig(args.out_dir / "fig_failure_alpha_variant_breakdown.png", dpi=180)
    plt.close(fig)

    # ---------------------------
    # Plot 3: local bug reversal rates
    # ---------------------------
    reversal_rows: List[dict] = []
    for jid in judge_ids:
        by_problem = bug_by_judge_problem.get(jid, {})
        rev_ct = 0
        total = 0
        for _, ladder in by_problem.items():
            seq = [ladder.get(l, float("nan")) for l in [0, 1, 2, 3, 4]]
            if any(not math.isfinite(v) for v in seq):
                continue
            total += 1
            has_rev = False
            for a, b in zip(seq[:-1], seq[1:]):
                # expected non-increasing; b > a indicates local reversal
                if b > a + 1e-12:
                    has_rev = True
                    break
            if has_rev:
                rev_ct += 1
        rate = float(rev_ct / total) if total else float("nan")
        reversal_rows.append({"judge_id": jid, "n_ladders": total, "n_reversal": rev_ct, "reversal_rate": rate})

    fig, ax = plt.subplots(figsize=(10.2, 4.8))
    vals = [r["reversal_rate"] for r in reversal_rows]
    ax.bar(range(len(judge_ids)), vals, color="#d95f02")
    ax.set_xticks(range(len(judge_ids)))
    ax.set_xticklabels(judge_ids, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("Rate of ladders with >=1 local reversal")
    ax.set_title("EXP19 Failure Mode: Bug-Ladder Local Reversal Rate")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(args.out_dir / "fig_failure_bug_reversal_rates.png", dpi=180)
    plt.close(fig)

    # Write tabular outputs.
    with (args.out_dir / "bug_curve_main_points.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["judge_id", "bug_level", "mean_score", "ci_lo", "ci_hi", "n_problems"])
        w.writeheader()
        w.writerows(trend_rows)

    with (args.out_dir / "bug_reversal_rates.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["judge_id", "n_ladders", "n_reversal", "reversal_rate"])
        w.writeheader()
        w.writerows(reversal_rows)

    summary = {
        "experiment": "exp19_replot_low_variance",
        "detail_rows": str(args.detail_rows),
        "judge_rows": str(args.judge_rows),
        "repeat_agg": args.repeat_agg,
        "main_judges": main_jids,
        "outputs": {
            "main_monotonicity": str(args.out_dir / "fig_main_monotonicity_lowvar.png"),
            "alpha_failure_plot": str(args.out_dir / "fig_failure_alpha_variant_breakdown.png"),
            "reversal_failure_plot": str(args.out_dir / "fig_failure_bug_reversal_rates.png"),
            "main_points_csv": str(args.out_dir / "bug_curve_main_points.csv"),
            "reversal_csv": str(args.out_dir / "bug_reversal_rates.csv"),
        },
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=" * 72)
    print("EXP19: low-variance replot package")
    print(f"repeat_agg={args.repeat_agg} | main_judges={len(main_jids)}")
    print(f"Wrote: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
