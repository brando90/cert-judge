#!/usr/bin/env python3
"""
Experiment 13: Threshold calibration sweep for judge decision stability.

Goal:
- Sweep decision thresholds and measure decision stability (flip rate)
- Keep score-quality diagnostics visible (identity mean/std, bug Spearman)
- Add bootstrap confidence intervals for all reported metrics

Outputs:
- results/threshold_calibration_sweep/summary.json
- results/threshold_calibration_sweep/threshold_metrics.csv
- results/threshold_calibration_sweep/detail_rows.csv
- figures/threshold_calibration_sweep/threshold_stability_curve.png
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Sequence

EXP_DIR = Path(__file__).parent
REPO_ROOT = EXP_DIR.parents[1]
sys.path.insert(0, str(EXP_DIR))

from utils.metrics import spearman_r, weak_monotonicity_pct
from utils.sensitivity_sweep import PROMPT_VARIANTS
from utils.variant_generator import generate_variants
from utils.veribench_variance_utils import (
    build_bug_ladder,
    collect_veribench_files,
    infer_split,
    score_pair,
    write_csv,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Threshold calibration sweep with bootstrap CIs.")
    parser.add_argument("--model", type=str, default="gpt-5.3-codex")
    parser.add_argument("--judge-mode", type=str, default="api", choices=["api", "local"])
    parser.add_argument("--prompt-name", type=str, default="P8_STRICT_B", choices=sorted(PROMPT_VARIANTS.keys()))
    parser.add_argument("--n-repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-files", type=int, default=30, help="0 means all files")
    parser.add_argument(
        "--thresholds",
        type=str,
        default="0.6,0.65,0.7,0.75,0.8,0.85",
        help="Comma-separated threshold list.",
    )
    parser.add_argument("--bootstrap-iters", type=int, default=1000)
    parser.add_argument(
        "--veribench-root",
        type=Path,
        default=REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=EXP_DIR / "results" / "threshold_calibration_sweep",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=EXP_DIR / "figures" / "threshold_calibration_sweep",
    )
    return parser.parse_args()


def _parse_thresholds(raw: str) -> List[float]:
    vals = sorted({round(float(x.strip()), 6) for x in raw.split(",") if x.strip()})
    vals = [v for v in vals if 0.0 <= v <= 1.0]
    if not vals:
        raise ValueError("No valid thresholds found in [0,1].")
    return vals


def _percentile(sorted_vals: Sequence[float], q: float) -> float:
    if not sorted_vals:
        return float("nan")
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    idx = q * (len(sorted_vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return float(sorted_vals[lo])
    frac = idx - lo
    return float(sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac)


def _ci(vals: Sequence[float]) -> tuple[float, float]:
    clean = sorted(float(v) for v in vals if v is not None and not math.isnan(float(v)))
    if not clean:
        return (float("nan"), float("nan"))
    return (_percentile(clean, 0.025), _percentile(clean, 0.975))


def _compute_metrics_for_threshold(items: List[dict], threshold: float) -> dict:
    identity_means = [float(it["score_mean"]) for it in items if it["task"] == "identity"]
    bug_points = [(int(it["level"]), float(it["score_mean"])) for it in items if it["task"] == "bug_ladder"]

    flip_flags = []
    pass_flags = []

    ladders_by_file: Dict[str, Dict[int, float]] = defaultdict(dict)
    for it in items:
        reps = [float(x) for x in it["repeat_scores"]]
        decs = [x >= threshold for x in reps]
        flip_flags.append(len(set(decs)) > 1)

        pass_flags.append(float(it["score_mean"]) >= threshold)

        if it["task"] == "bug_ladder":
            ladders_by_file[it["file_key"]][int(it["level"])] = float(it["score_mean"])

    bug_ladders = []
    for _, lv_map in ladders_by_file.items():
        ladder = [lv_map[k] for k in sorted(lv_map.keys())]
        bug_ladders.append(ladder)

    if bug_points:
        levels = [x[0] for x in bug_points]
        scores = [x[1] for x in bug_points]
        bug_spearman_r, bug_spearman_p = spearman_r(levels, scores)
    else:
        bug_spearman_r, bug_spearman_p = (0.0, 1.0)

    identity_mean = statistics.mean(identity_means) if identity_means else 0.0
    identity_std = statistics.stdev(identity_means) if len(identity_means) > 1 else 0.0
    flip_rate = sum(1 for x in flip_flags if x) / max(1, len(flip_flags))
    pass_rate = sum(1 for x in pass_flags if x) / max(1, len(pass_flags))
    weak_mono = weak_monotonicity_pct(bug_ladders)

    return {
        "threshold": threshold,
        "threshold_flip_rate": float(flip_rate),
        "identity_mean": float(identity_mean),
        "identity_std": float(identity_std),
        "bug_spearman_r": float(bug_spearman_r),
        "bug_spearman_p": float(bug_spearman_p),
        "bug_weak_mono_pct": float(weak_mono),
        "pass_rate": float(pass_rate),
    }


def _bootstrap_by_file(items: List[dict], thresholds: List[float], n_iters: int, seed: int) -> Dict[float, dict]:
    by_file: Dict[str, List[dict]] = defaultdict(list)
    for it in items:
        by_file[it["file_key"]].append(it)

    file_keys = sorted(by_file.keys())
    rng = random.Random(seed + 7919)

    dist: Dict[float, Dict[str, List[float]]] = {
        t: {
            "threshold_flip_rate": [],
            "identity_mean": [],
            "identity_std": [],
            "bug_spearman_r": [],
            "pass_rate": [],
        }
        for t in thresholds
    }

    if not file_keys:
        return {t: {k: (float("nan"), float("nan")) for k in v.keys()} for t, v in dist.items()}

    n_files = len(file_keys)
    for _ in range(n_iters):
        sampled = [rng.choice(file_keys) for _ in range(n_files)]
        sampled_items: List[dict] = []
        for fk in sampled:
            sampled_items.extend(by_file[fk])

        for t in thresholds:
            m = _compute_metrics_for_threshold(sampled_items, t)
            dist[t]["threshold_flip_rate"].append(m["threshold_flip_rate"])
            dist[t]["identity_mean"].append(m["identity_mean"])
            dist[t]["identity_std"].append(m["identity_std"])
            dist[t]["bug_spearman_r"].append(m["bug_spearman_r"])
            dist[t]["pass_rate"].append(m["pass_rate"])

    cis: Dict[float, dict] = {}
    for t in thresholds:
        cis[t] = {
            "threshold_flip_rate_ci": _ci(dist[t]["threshold_flip_rate"]),
            "identity_mean_ci": _ci(dist[t]["identity_mean"]),
            "identity_std_ci": _ci(dist[t]["identity_std"]),
            "bug_spearman_r_ci": _ci(dist[t]["bug_spearman_r"]),
            "pass_rate_ci": _ci(dist[t]["pass_rate"]),
        }
    return cis


def _make_plot(rows: List[dict], out_png: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:
        print(f"WARNING: plot generation skipped (matplotlib unavailable): {e}")
        return

    thresholds = [float(r["threshold"]) for r in rows]

    flip = [float(r["threshold_flip_rate"]) for r in rows]
    flip_lo = [float(r["threshold_flip_rate_ci_lo"]) for r in rows]
    flip_hi = [float(r["threshold_flip_rate_ci_hi"]) for r in rows]

    pr = [float(r["pass_rate"]) for r in rows]
    pr_lo = [float(r["pass_rate_ci_lo"]) for r in rows]
    pr_hi = [float(r["pass_rate_ci_hi"]) for r in rows]

    fig, ax = plt.subplots(figsize=(8.2, 4.8))

    ax.plot(thresholds, flip, marker="o", linewidth=2.0, label="Flip Rate", color="#d62728")
    ax.fill_between(thresholds, flip_lo, flip_hi, color="#d62728", alpha=0.15)

    ax.plot(thresholds, pr, marker="s", linewidth=2.0, label="Pass Rate", color="#1f77b4")
    ax.fill_between(thresholds, pr_lo, pr_hi, color="#1f77b4", alpha=0.15)

    ax.set_xlabel("Decision Threshold")
    ax.set_ylabel("Rate")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title("Threshold Calibration Sweep (with 95% bootstrap CI)")
    ax.grid(alpha=0.25)
    ax.legend()

    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=180)
    plt.close(fig)


def main() -> int:
    args = parse_args()
    random.seed(args.seed)
    thresholds = _parse_thresholds(args.thresholds)

    files = collect_veribench_files(args.veribench_root, args.max_files, args.seed)
    if not files:
        print(f"ERROR: no .lean files found under {args.veribench_root}")
        return 1

    prompt_template = PROMPT_VARIANTS[args.prompt_name]
    args.results_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("EXP 13: Threshold Calibration Sweep")
    print(
        f"model={args.model} mode={args.judge_mode} prompt={args.prompt_name} "
        f"repeats={args.n_repeats} files={len(files)}"
    )
    print(f"thresholds={thresholds} bootstrap_iters={args.bootstrap_iters}")
    print("=" * 72)

    detail_rows: List[dict] = []
    items: List[dict] = []

    for i, fpath in enumerate(files, start=1):
        code = fpath.read_text(encoding="utf-8", errors="ignore")
        rel = str(fpath.relative_to(args.veribench_root))
        split = infer_split(fpath)
        file_key = f"{split}::{rel}"

        print(f"[{i}/{len(files)}] {rel}")

        for v in generate_variants(code):
            result = score_pair(
                generated_theorem=v["code"],
                reference_impl=code,
                model=args.model,
                n_repeats=args.n_repeats,
                prompt_template=prompt_template,
                cache_namespace=f"exp13:{args.prompt_name}:identity",
                judge_mode=args.judge_mode,
            )
            reps = [float(x) for x in result.get("scores", [])]
            mean_score = float(result["mean"])

            item = {
                "file_key": file_key,
                "split": split,
                "file": rel,
                "task": "identity",
                "item": v["variant_type"],
                "level": -1,
                "score_mean": mean_score,
                "score_std": float(result["std"]),
                "repeat_scores": reps,
            }
            items.append(item)
            detail_rows.append(
                {
                    "split": split,
                    "file": rel,
                    "task": "identity",
                    "item": v["variant_type"],
                    "level": -1,
                    "score_mean": round(mean_score, 6),
                    "score_std": round(float(result["std"]), 6),
                    "repeat_scores": json.dumps([round(x, 6) for x in reps]),
                    "cached": bool(result.get("cached", False)),
                }
            )

        for level, cand in enumerate(build_bug_ladder(code)):
            result = score_pair(
                generated_theorem=cand,
                reference_impl=code,
                model=args.model,
                n_repeats=args.n_repeats,
                prompt_template=prompt_template,
                cache_namespace=f"exp13:{args.prompt_name}:bug_ladder",
                judge_mode=args.judge_mode,
            )
            reps = [float(x) for x in result.get("scores", [])]
            mean_score = float(result["mean"])

            item = {
                "file_key": file_key,
                "split": split,
                "file": rel,
                "task": "bug_ladder",
                "item": f"L{level}",
                "level": level,
                "score_mean": mean_score,
                "score_std": float(result["std"]),
                "repeat_scores": reps,
            }
            items.append(item)
            detail_rows.append(
                {
                    "split": split,
                    "file": rel,
                    "task": "bug_ladder",
                    "item": f"L{level}",
                    "level": level,
                    "score_mean": round(mean_score, 6),
                    "score_std": round(float(result["std"]), 6),
                    "repeat_scores": json.dumps([round(x, 6) for x in reps]),
                    "cached": bool(result.get("cached", False)),
                }
            )

    ci_by_threshold = _bootstrap_by_file(items, thresholds, args.bootstrap_iters, args.seed)

    threshold_rows: List[dict] = []
    for t in thresholds:
        m = _compute_metrics_for_threshold(items, t)
        ci = ci_by_threshold[t]
        threshold_rows.append(
            {
                "threshold": round(float(t), 6),
                "threshold_flip_rate": round(m["threshold_flip_rate"], 6),
                "threshold_flip_rate_ci_lo": round(float(ci["threshold_flip_rate_ci"][0]), 6),
                "threshold_flip_rate_ci_hi": round(float(ci["threshold_flip_rate_ci"][1]), 6),
                "identity_mean": round(m["identity_mean"], 6),
                "identity_mean_ci_lo": round(float(ci["identity_mean_ci"][0]), 6),
                "identity_mean_ci_hi": round(float(ci["identity_mean_ci"][1]), 6),
                "identity_std": round(m["identity_std"], 6),
                "identity_std_ci_lo": round(float(ci["identity_std_ci"][0]), 6),
                "identity_std_ci_hi": round(float(ci["identity_std_ci"][1]), 6),
                "bug_spearman_r": round(m["bug_spearman_r"], 6),
                "bug_spearman_r_ci_lo": round(float(ci["bug_spearman_r_ci"][0]), 6),
                "bug_spearman_r_ci_hi": round(float(ci["bug_spearman_r_ci"][1]), 6),
                "bug_weak_mono_pct": round(m["bug_weak_mono_pct"], 6),
                "pass_rate": round(m["pass_rate"], 6),
                "pass_rate_ci_lo": round(float(ci["pass_rate_ci"][0]), 6),
                "pass_rate_ci_hi": round(float(ci["pass_rate_ci"][1]), 6),
            }
        )

    best_row = min(threshold_rows, key=lambda r: (r["threshold_flip_rate"], abs(r["pass_rate"] - 0.5)))

    summary = {
        "experiment": "exp13_threshold_calibration_sweep",
        "model": args.model,
        "judge_mode": args.judge_mode,
        "prompt_name": args.prompt_name,
        "n_repeats": args.n_repeats,
        "n_files": len(files),
        "thresholds": thresholds,
        "bootstrap_iters": args.bootstrap_iters,
        "selection_rule": "min threshold_flip_rate, tie-break by pass_rate closest to 0.5",
        "recommended_threshold": best_row["threshold"],
        "recommended_metrics": best_row,
        "notes": {
            "flip_definition": "an item flips at threshold t if repeat-level decisions are not all equal",
            "pass_definition": "item passes at threshold t if mean score across repeats >= t",
            "ci_method": "bootstrap over files with replacement, percentile 95% CI",
        },
    }

    write_csv(args.results_dir / "detail_rows.csv", detail_rows)
    write_csv(args.results_dir / "threshold_metrics.csv", threshold_rows)
    (args.results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    fig_path = args.figures_dir / "threshold_stability_curve.png"
    _make_plot(threshold_rows, fig_path)

    print("\nThreshold metrics:")
    for r in threshold_rows:
        print(
            f"  t={r['threshold']:.2f}: flip={r['threshold_flip_rate']:.3f} "
            f"[{r['threshold_flip_rate_ci_lo']:.3f},{r['threshold_flip_rate_ci_hi']:.3f}] | "
            f"pass={r['pass_rate']:.3f} | bug_r={r['bug_spearman_r']:.3f}"
        )

    print(f"\nRecommended threshold: {best_row['threshold']:.2f}")
    print(f"Wrote results: {args.results_dir}")
    print(f"Wrote figure: {fig_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
