#!/usr/bin/env python3
"""
Experiment 10 (List #1): Prompt template ablation for lower-variance judging.

Evaluates prompt templates on:
- Identity robustness (syntactic variants)
- Monotonicity (bug ladder)
- Variance proxies (mean repeat std, threshold flip rate)
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
    parser = argparse.ArgumentParser(description="Prompt template ablation over VeriBench.")
    parser.add_argument("--model", type=str, default="gpt-5.3-codex")
    parser.add_argument("--judge-mode", type=str, default="api", choices=["api", "local"])
    parser.add_argument("--n-repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-files", type=int, default=0, help="0 means all files")
    parser.add_argument(
        "--prompt-names",
        type=str,
        default="P1_BASELINE,P2_FORMAL,P4_CHECKLIST,P8_STRICT_B",
        help="Comma-separated prompt names from utils.sensitivity_sweep.PROMPT_VARIANTS",
    )
    parser.add_argument(
        "--veribench-root",
        type=Path,
        default=REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=EXP_DIR / "results" / "prompt_template_ablation",
    )
    parser.add_argument("--pass-threshold", type=float, default=0.8)
    return parser.parse_args()


def _resolve_prompt_names(raw: str) -> List[str]:
    if not raw.strip():
        return sorted(PROMPT_VARIANTS.keys())
    names = [x.strip() for x in raw.split(",") if x.strip()]
    unknown = [n for n in names if n not in PROMPT_VARIANTS]
    if unknown:
        raise ValueError(f"Unknown prompt names: {unknown}")
    return names


def main() -> int:
    args = parse_args()
    random.seed(args.seed)

    prompt_names = _resolve_prompt_names(args.prompt_names)
    files = collect_veribench_files(args.veribench_root, args.max_files, args.seed)
    if not files:
        print(f"ERROR: no .lean files found under {args.veribench_root}")
        return 1

    args.results_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("EXP 10: Prompt Template Ablation")
    print(f"model={args.model} mode={args.judge_mode} repeats={args.n_repeats} files={len(files)}")
    print(f"prompts={prompt_names}")
    print("=" * 72)

    detail_rows: List[dict] = []
    per_prompt: Dict[str, dict] = {
        p: {
            "identity_scores": [],
            "identity_stds": [],
            "bug_ladders": [],
            "bug_flat_levels": [],
            "bug_flat_scores": [],
            "bug_flat_stds": [],
            "threshold_flip_flags": [],
        }
        for p in prompt_names
    }

    for i, fpath in enumerate(files, start=1):
        code = fpath.read_text(encoding="utf-8", errors="ignore")
        rel = str(fpath.relative_to(args.veribench_root))
        split = infer_split(fpath)
        print(f"[{i}/{len(files)}] {rel}")

        variants = generate_variants(code)
        bug_codes = build_bug_ladder(code)

        for prompt_name in prompt_names:
            prompt_template = PROMPT_VARIANTS[prompt_name]
            cache_ns = f"exp10:{prompt_name}"

            variant_passes = []
            for v in variants:
                result = score_pair(
                    generated_theorem=v["code"],
                    reference_impl=code,
                    model=args.model,
                    n_repeats=args.n_repeats,
                    prompt_template=prompt_template,
                    cache_namespace=cache_ns,
                    judge_mode=args.judge_mode,
                )
                s = float(result["mean"])
                st = float(result["std"])
                variant_passes.append(s >= args.pass_threshold)
                per_prompt[prompt_name]["identity_scores"].append(s)
                per_prompt[prompt_name]["identity_stds"].append(st)
                detail_rows.append(
                    {
                        "split": split,
                        "file": rel,
                        "prompt_name": prompt_name,
                        "task": "identity",
                        "item": v["variant_type"],
                        "level": -1,
                        "score_mean": round(s, 6),
                        "score_std": round(st, 6),
                        "cached": bool(result.get("cached", False)),
                    }
                )

            ladder_scores = []
            ladder_passes = []
            for level, cand in enumerate(bug_codes):
                result = score_pair(
                    generated_theorem=cand,
                    reference_impl=code,
                    model=args.model,
                    n_repeats=args.n_repeats,
                    prompt_template=prompt_template,
                    cache_namespace=cache_ns,
                    judge_mode=args.judge_mode,
                )
                s = float(result["mean"])
                st = float(result["std"])
                ladder_scores.append(s)
                ladder_passes.append(s >= args.pass_threshold)
                per_prompt[prompt_name]["bug_flat_levels"].append(level)
                per_prompt[prompt_name]["bug_flat_scores"].append(s)
                per_prompt[prompt_name]["bug_flat_stds"].append(st)
                detail_rows.append(
                    {
                        "split": split,
                        "file": rel,
                        "prompt_name": prompt_name,
                        "task": "bug_ladder",
                        "item": f"L{level}",
                        "level": level,
                        "score_mean": round(s, 6),
                        "score_std": round(st, 6),
                        "cached": bool(result.get("cached", False)),
                    }
                )
            per_prompt[prompt_name]["bug_ladders"].append(ladder_scores)

            # whether prompt changes binary pass/fail decisions within the file+task group
            pass_flags = variant_passes + ladder_passes
            per_prompt[prompt_name]["threshold_flip_flags"].append(len(set(pass_flags)) > 1)

    leaderboard_rows: List[dict] = []
    for prompt_name in prompt_names:
        stats = per_prompt[prompt_name]

        id_mean = statistics.mean(stats["identity_scores"]) if stats["identity_scores"] else 0.0
        id_std_across_items = statistics.stdev(stats["identity_scores"]) if len(stats["identity_scores"]) > 1 else 0.0

        b_spear, b_spear_p = spearman_r(stats["bug_flat_levels"], stats["bug_flat_scores"])
        b_pear, b_pear_p = pearson_r(stats["bug_flat_levels"], stats["bug_flat_scores"])
        b_weak = weak_monotonicity_pct(stats["bug_ladders"])

        mean_repeat_std = statistics.mean(stats["identity_stds"] + stats["bug_flat_stds"]) if (stats["identity_stds"] or stats["bug_flat_stds"]) else 0.0
        flip_rate = sum(1 for x in stats["threshold_flip_flags"] if x) / max(1, len(stats["threshold_flip_flags"]))

        leaderboard_rows.append(
            {
                "prompt_name": prompt_name,
                "identity_mean": round(id_mean, 6),
                "identity_std_across_items": round(id_std_across_items, 6),
                "bug_spearman_r": round(float(b_spear), 6),
                "bug_spearman_p": round(float(b_spear_p), 6),
                "bug_pearson_r": round(float(b_pear), 6),
                "bug_pearson_p": round(float(b_pear_p), 6),
                "bug_weak_mono_pct": round(float(b_weak), 6),
                "mean_repeat_std": round(float(mean_repeat_std), 6),
                "threshold_flip_rate": round(float(flip_rate), 6),
            }
        )

    # Lower is better for variance; higher is better for identity/monotonicity.
    def _rank_key(row: dict):
        return (
            row["mean_repeat_std"],
            row["threshold_flip_rate"],
            -row["identity_mean"],
            row["bug_spearman_r"],  # more negative is better
            -row["bug_weak_mono_pct"],
        )

    leaderboard_rows = sorted(leaderboard_rows, key=_rank_key)
    best = leaderboard_rows[0] if leaderboard_rows else None

    summary = {
        "experiment": "exp10_prompt_template_ablation",
        "model": args.model,
        "judge_mode": args.judge_mode,
        "n_repeats": args.n_repeats,
        "n_files": len(files),
        "prompt_names": prompt_names,
        "pass_threshold": args.pass_threshold,
        "best_prompt_by_variance_objective": best,
        "leaderboard": leaderboard_rows,
    }

    write_csv(args.results_dir / "detail_rows.csv", detail_rows)
    write_csv(args.results_dir / "leaderboard.csv", leaderboard_rows)
    (args.results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\nTop prompts (best first):")
    for row in leaderboard_rows[: min(5, len(leaderboard_rows))]:
        print(
            f"  {row['prompt_name']}: repeat_std={row['mean_repeat_std']:.4f}, "
            f"flip={row['threshold_flip_rate']:.3f}, id={row['identity_mean']:.3f}, "
            f"bug_r={row['bug_spearman_r']:.3f}, weak={row['bug_weak_mono_pct']:.1f}%"
        )
    print(f"\nWrote: {args.results_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
