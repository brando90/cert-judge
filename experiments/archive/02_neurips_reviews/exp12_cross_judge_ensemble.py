#!/usr/bin/env python3
"""
Experiment 12 (List #9): Cross-judge ensemble for lower variance.

Compares base judges and ensembles across:
- identity robustness
- bug-ladder monotonicity
- per-item judge disagreement (cross-judge std)
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
    parser = argparse.ArgumentParser(description="Cross-judge ensemble variance experiment.")
    parser.add_argument("--judge-mode", type=str, default="api", choices=["api", "local"])
    parser.add_argument("--n-repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-files", type=int, default=0)
    parser.add_argument(
        "--judges",
        type=str,
        default="gpt-5.3-codex:P1_BASELINE,gpt-5.3-codex:P4_CHECKLIST,claude-sonnet-4-20250514:P8_STRICT_B",
        help="Comma-separated model:prompt_name entries",
    )
    parser.add_argument(
        "--veribench-root",
        type=Path,
        default=REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=EXP_DIR / "results" / "cross_judge_ensemble",
    )
    parser.add_argument("--pass-threshold", type=float, default=0.8)
    return parser.parse_args()


def _parse_judges(raw: str) -> List[dict]:
    out: List[dict] = []
    for spec in [x.strip() for x in raw.split(",") if x.strip()]:
        if ":" not in spec:
            raise ValueError(f"Invalid judge spec '{spec}', expected model:prompt_name")
        model, prompt_name = spec.split(":", 1)
        model = model.strip()
        prompt_name = prompt_name.strip()
        if prompt_name not in PROMPT_VARIANTS:
            raise ValueError(f"Unknown prompt name in judges: {prompt_name}")
        out.append({"judge_id": f"{model}|{prompt_name}", "model": model, "prompt_name": prompt_name})
    if len(out) < 2:
        raise ValueError("Need at least two judges for cross-judge ensemble")
    return out


def _ensemble_score(values: List[float], method: str) -> float:
    if not values:
        return 0.0
    if method == "mean":
        return float(statistics.mean(values))
    if method == "median":
        return float(statistics.median(values))
    raise ValueError(f"Unknown ensemble method: {method}")


def _eval_variant(config_name: str, scores_by_pair: Dict[str, List[float]], pass_threshold: float) -> dict:
    identity_scores = []
    bug_flat_levels = []
    bug_flat_scores = []
    bug_ladder_map: Dict[str, Dict[int, float]] = {}
    threshold_flip_map: Dict[str, List[bool]] = {}
    disagreement_stds: List[float] = []

    for pair_key, arr in scores_by_pair.items():
        split, file_rel, task, level_str = pair_key.split("||")
        level = int(level_str)

        score = float(arr[0])
        threshold_flip_map.setdefault(f"{split}::{file_rel}", []).append(score >= pass_threshold)

        if len(arr) > 1:
            disagreement_stds.append(statistics.stdev(arr))

        if task == "identity":
            identity_scores.append(score)
        else:
            bug_flat_levels.append(level)
            bug_flat_scores.append(score)
            bug_ladder_map.setdefault(f"{split}::{file_rel}", {})[level] = score

    bug_ladders = [[lv[idx] for idx in sorted(lv.keys())] for lv in bug_ladder_map.values()]

    id_mean = statistics.mean(identity_scores) if identity_scores else 0.0
    id_std = statistics.stdev(identity_scores) if len(identity_scores) > 1 else 0.0

    b_spear, b_spear_p = spearman_r(bug_flat_levels, bug_flat_scores)
    b_pear, b_pear_p = pearson_r(bug_flat_levels, bug_flat_scores)
    b_weak = weak_monotonicity_pct(bug_ladders)

    flip_rate = sum(1 for flags in threshold_flip_map.values() if len(set(flags)) > 1) / max(1, len(threshold_flip_map))
    mean_disagreement_std = statistics.mean(disagreement_stds) if disagreement_stds else 0.0

    return {
        "config_name": config_name,
        "identity_mean": round(id_mean, 6),
        "identity_std_across_items": round(id_std, 6),
        "bug_spearman_r": round(float(b_spear), 6),
        "bug_spearman_p": round(float(b_spear_p), 6),
        "bug_pearson_r": round(float(b_pear), 6),
        "bug_pearson_p": round(float(b_pear_p), 6),
        "bug_weak_mono_pct": round(float(b_weak), 6),
        "mean_cross_judge_std": round(float(mean_disagreement_std), 6),
        "threshold_flip_rate": round(float(flip_rate), 6),
    }


def main() -> int:
    args = parse_args()
    random.seed(args.seed)

    judges = _parse_judges(args.judges)
    files = collect_veribench_files(args.veribench_root, args.max_files, args.seed)
    if not files:
        print(f"ERROR: no .lean files found under {args.veribench_root}")
        return 1

    args.results_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("EXP 12: Cross-Judge Ensemble")
    print(f"judge_mode={args.judge_mode} repeats={args.n_repeats} files={len(files)}")
    print(f"judges={[j['judge_id'] for j in judges]}")
    print("=" * 72)

    # pair_key -> judge_id -> score
    pair_scores: Dict[str, Dict[str, float]] = {}
    detail_rows: List[dict] = []

    for i, fpath in enumerate(files, start=1):
        code = fpath.read_text(encoding="utf-8", errors="ignore")
        rel = str(fpath.relative_to(args.veribench_root))
        split = infer_split(fpath)
        print(f"[{i}/{len(files)}] {rel}")

        pairs: List[dict] = []
        for v in generate_variants(code):
            pairs.append({"task": "identity", "item": v["variant_type"], "level": -1, "cand": v["code"]})
        for level, cand in enumerate(build_bug_ladder(code)):
            pairs.append({"task": "bug_ladder", "item": f"L{level}", "level": level, "cand": cand})

        for pair in pairs:
            pkey = f"{split}||{rel}||{pair['task']}||{pair['level']}"
            pair_scores.setdefault(pkey, {})

            for j in judges:
                prompt_template = PROMPT_VARIANTS[j["prompt_name"]]
                result = score_pair(
                    generated_theorem=pair["cand"],
                    reference_impl=code,
                    model=j["model"],
                    n_repeats=args.n_repeats,
                    prompt_template=prompt_template,
                    cache_namespace=f"exp12:{j['judge_id']}",
                    judge_mode=args.judge_mode,
                )
                s = float(result["mean"])
                pair_scores[pkey][j["judge_id"]] = s
                detail_rows.append(
                    {
                        "split": split,
                        "file": rel,
                        "task": pair["task"],
                        "item": pair["item"],
                        "level": pair["level"],
                        "judge_id": j["judge_id"],
                        "model": j["model"],
                        "prompt_name": j["prompt_name"],
                        "score_mean": round(s, 6),
                        "score_std": round(float(result["std"]), 6),
                        "cached": bool(result.get("cached", False)),
                    }
                )

    # Build evaluation views: each base judge + ensembles.
    eval_rows: List[dict] = []

    for j in judges:
        jid = j["judge_id"]
        scores_by_pair = {pk: [vals[jid]] for pk, vals in pair_scores.items() if jid in vals}
        eval_rows.append(_eval_variant(config_name=f"base::{jid}", scores_by_pair=scores_by_pair, pass_threshold=args.pass_threshold))

    for method in ["mean", "median"]:
        scores_by_pair = {}
        for pk, vals in pair_scores.items():
            ordered = [float(vals[j["judge_id"]]) for j in judges if j["judge_id"] in vals]
            ens = _ensemble_score(ordered, method)
            # keep original judge values after first position so disagreement std is measurable
            scores_by_pair[pk] = [ens] + ordered
        eval_rows.append(_eval_variant(config_name=f"ensemble::{method}", scores_by_pair=scores_by_pair, pass_threshold=args.pass_threshold))

    eval_rows = sorted(
        eval_rows,
        key=lambda row: (
            row["mean_cross_judge_std"],
            row["threshold_flip_rate"],
            -row["identity_mean"],
            row["bug_spearman_r"],
            -row["bug_weak_mono_pct"],
        ),
    )

    best = eval_rows[0] if eval_rows else None
    summary = {
        "experiment": "exp12_cross_judge_ensemble",
        "judge_mode": args.judge_mode,
        "n_repeats": args.n_repeats,
        "n_files": len(files),
        "judges": judges,
        "pass_threshold": args.pass_threshold,
        "best_config_by_variance_objective": best,
        "leaderboard": eval_rows,
    }

    write_csv(args.results_dir / "detail_rows.csv", detail_rows)
    write_csv(args.results_dir / "leaderboard.csv", eval_rows)
    (args.results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\nConfigs (best first):")
    for row in eval_rows:
        print(
            f"  {row['config_name']}: cross_std={row['mean_cross_judge_std']:.4f}, "
            f"flip={row['threshold_flip_rate']:.3f}, id={row['identity_mean']:.3f}, "
            f"bug_r={row['bug_spearman_r']:.3f}, weak={row['bug_weak_mono_pct']:.1f}%"
        )
    print(f"\nWrote: {args.results_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
