#!/usr/bin/env python3
"""
Experiment 11 (List #3): Self-consistency aggregation sweep.

For each file pair, collect max(K) repeated judge samples once, then evaluate
aggregation policies at k in K:
- mean
- median
- trimmed_mean_20

Goal: identify aggregation that lowers variance while preserving monotonicity.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path
from typing import Dict, List

EXP_DIR = Path(__file__).parent
REPO_ROOT = EXP_DIR.parents[2]
sys.path.insert(0, str(EXP_DIR))

from utils.metrics import pearson_r, spearman_r, weak_monotonicity_pct
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
    parser = argparse.ArgumentParser(description="Self-consistency sweep for judge variance reduction.")
    parser.add_argument("--model", type=str, default="gpt-5.3-codex")
    parser.add_argument("--judge-mode", type=str, default="api", choices=["api", "local"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-files", type=int, default=0)
    parser.add_argument("--prompt-name", type=str, default="P1_BASELINE", choices=sorted(PROMPT_VARIANTS.keys()))
    parser.add_argument("--k-values", type=str, default="1,3,5,7")
    parser.add_argument(
        "--veribench-root",
        type=Path,
        default=REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=EXP_DIR / "results" / "self_consistency_sweep",
    )
    parser.add_argument("--pass-threshold", type=float, default=0.8)
    return parser.parse_args()


def _parse_k_values(raw: str) -> List[int]:
    vals = sorted({int(x.strip()) for x in raw.split(",") if x.strip()})
    vals = [v for v in vals if v > 0]
    if not vals:
        raise ValueError("k-values must contain positive integers")
    return vals


def _aggregate(scores: List[float], method: str) -> float:
    if not scores:
        return 0.0
    if method == "mean":
        return float(statistics.mean(scores))
    if method == "median":
        return float(statistics.median(scores))
    if method == "trimmed_mean_20":
        if len(scores) < 5:
            return float(statistics.mean(scores))
        sorted_scores = sorted(scores)
        trim = int(0.2 * len(sorted_scores))
        if trim <= 0 or (2 * trim) >= len(sorted_scores):
            return float(statistics.mean(sorted_scores))
        core = sorted_scores[trim:-trim]
        return float(statistics.mean(core))
    raise ValueError(f"Unknown aggregation method: {method}")


def main() -> int:
    args = parse_args()
    random.seed(args.seed)

    k_values = _parse_k_values(args.k_values)
    max_k = max(k_values)
    agg_methods = ["mean", "median", "trimmed_mean_20"]

    files = collect_veribench_files(args.veribench_root, args.max_files, args.seed)
    if not files:
        print(f"ERROR: no .lean files found under {args.veribench_root}")
        return 1

    prompt_template = PROMPT_VARIANTS[args.prompt_name]

    args.results_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("EXP 11: Self-Consistency Sweep")
    print(f"model={args.model} mode={args.judge_mode} prompt={args.prompt_name} files={len(files)}")
    print(f"k_values={k_values} agg_methods={agg_methods}")
    print("=" * 72)

    base_rows: List[dict] = []
    # store raw repeated scores once per pair, then re-aggregate for each config
    pair_records: List[dict] = []

    for i, fpath in enumerate(files, start=1):
        code = fpath.read_text(encoding="utf-8", errors="ignore")
        rel = str(fpath.relative_to(args.veribench_root))
        split = infer_split(fpath)
        print(f"[{i}/{len(files)}] {rel}")

        variants = generate_variants(code)
        bug_codes = build_bug_ladder(code)

        for v in variants:
            result = score_pair(
                generated_theorem=v["code"],
                reference_impl=code,
                model=args.model,
                n_repeats=max_k,
                prompt_template=prompt_template,
                cache_namespace=f"exp11:{args.prompt_name}:maxk{max_k}",
                judge_mode=args.judge_mode,
            )
            scores = [float(x) for x in result.get("scores", [])]
            pair_records.append(
                {
                    "split": split,
                    "file": rel,
                    "task": "identity",
                    "item": v["variant_type"],
                    "level": -1,
                    "scores": scores,
                    "cached": bool(result.get("cached", False)),
                }
            )

        for level, cand in enumerate(bug_codes):
            result = score_pair(
                generated_theorem=cand,
                reference_impl=code,
                model=args.model,
                n_repeats=max_k,
                prompt_template=prompt_template,
                cache_namespace=f"exp11:{args.prompt_name}:maxk{max_k}",
                judge_mode=args.judge_mode,
            )
            scores = [float(x) for x in result.get("scores", [])]
            pair_records.append(
                {
                    "split": split,
                    "file": rel,
                    "task": "bug_ladder",
                    "item": f"L{level}",
                    "level": level,
                    "scores": scores,
                    "cached": bool(result.get("cached", False)),
                }
            )

    summary_rows: List[dict] = []

    for k in k_values:
        for agg in agg_methods:
            identity_scores: List[float] = []
            repeat_stds: List[float] = []
            bug_ladders_by_file: Dict[str, Dict[int, float]] = {}
            bug_flat_levels: List[int] = []
            bug_flat_scores: List[float] = []
            threshold_flip_map: Dict[str, List[bool]] = {}

            for r in pair_records:
                sraw = r["scores"][:k]
                s = _aggregate(sraw, agg)
                s_std = statistics.stdev(sraw) if len(sraw) > 1 else 0.0
                repeat_stds.append(s_std)

                key = f"{r['split']}::{r['file']}"
                threshold_flip_map.setdefault(key, []).append(s >= args.pass_threshold)

                base_rows.append(
                    {
                        "split": r["split"],
                        "file": r["file"],
                        "task": r["task"],
                        "item": r["item"],
                        "level": r["level"],
                        "k": k,
                        "agg": agg,
                        "score": round(s, 6),
                        "within_k_std": round(s_std, 6),
                        "cached": r["cached"],
                    }
                )

                if r["task"] == "identity":
                    identity_scores.append(s)
                else:
                    level = int(r["level"])
                    bug_flat_levels.append(level)
                    bug_flat_scores.append(s)
                    bug_ladders_by_file.setdefault(key, {})[level] = s

            bug_ladders = []
            for _, lv_map in bug_ladders_by_file.items():
                ladder = [lv_map[idx] for idx in sorted(lv_map.keys())]
                bug_ladders.append(ladder)

            flip_rate = sum(1 for flags in threshold_flip_map.values() if len(set(flags)) > 1) / max(1, len(threshold_flip_map))

            id_mean = statistics.mean(identity_scores) if identity_scores else 0.0
            id_std = statistics.stdev(identity_scores) if len(identity_scores) > 1 else 0.0
            mean_repeat_std = statistics.mean(repeat_stds) if repeat_stds else 0.0

            b_spear, b_spear_p = spearman_r(bug_flat_levels, bug_flat_scores)
            b_pear, b_pear_p = pearson_r(bug_flat_levels, bug_flat_scores)
            b_weak = weak_monotonicity_pct(bug_ladders)

            summary_rows.append(
                {
                    "k": k,
                    "agg": agg,
                    "identity_mean": round(id_mean, 6),
                    "identity_std_across_items": round(id_std, 6),
                    "bug_spearman_r": round(float(b_spear), 6),
                    "bug_spearman_p": round(float(b_spear_p), 6),
                    "bug_pearson_r": round(float(b_pear), 6),
                    "bug_pearson_p": round(float(b_pear_p), 6),
                    "bug_weak_mono_pct": round(float(b_weak), 6),
                    "mean_within_k_std": round(float(mean_repeat_std), 6),
                    "threshold_flip_rate": round(float(flip_rate), 6),
                }
            )

    summary_rows = sorted(
        summary_rows,
        key=lambda row: (
            row["mean_within_k_std"],
            row["threshold_flip_rate"],
            -row["identity_mean"],
            row["bug_spearman_r"],
            -row["bug_weak_mono_pct"],
        ),
    )

    best = summary_rows[0] if summary_rows else None
    summary = {
        "experiment": "exp11_self_consistency_sweep",
        "model": args.model,
        "judge_mode": args.judge_mode,
        "prompt_name": args.prompt_name,
        "k_values": k_values,
        "aggregation_methods": agg_methods,
        "n_files": len(files),
        "pass_threshold": args.pass_threshold,
        "best_config_by_variance_objective": best,
        "leaderboard": summary_rows,
    }

    write_csv(args.results_dir / "detail_rows.csv", base_rows)
    write_csv(args.results_dir / "leaderboard.csv", summary_rows)
    (args.results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\nTop self-consistency configs (best first):")
    for row in summary_rows[: min(7, len(summary_rows))]:
        print(
            f"  k={row['k']} agg={row['agg']}: std={row['mean_within_k_std']:.4f}, "
            f"flip={row['threshold_flip_rate']:.3f}, id={row['identity_mean']:.3f}, "
            f"bug_r={row['bug_spearman_r']:.3f}, weak={row['bug_weak_mono_pct']:.1f}%"
        )
    print(f"\nWrote: {args.results_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
