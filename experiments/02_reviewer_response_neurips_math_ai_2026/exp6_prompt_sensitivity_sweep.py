#!/usr/bin/env python3
"""
Experiment 6: Prompt Sensitivity Sweep

Vary evaluator prompt wording and measure verdict stability.
"""
import argparse
import statistics
import sys
from pathlib import Path

EXP_DIR = Path(__file__).parent
sys.path.insert(0, str(EXP_DIR))

from utils.judge_caller import judge
from utils.sensitivity_sweep import (
    PROMPT_VARIANTS,
    ensure_dir,
    load_items,
    pairwise_stats,
    score_to_label,
    summarize_score_distributions,
    write_json,
    write_rows_csv,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run prompt sensitivity sweep for LLM judge.")
    parser.add_argument("--model", type=str, default="gpt-4o-mini")
    parser.add_argument("--n-repeats", type=int, default=1)
    parser.add_argument("--items-source", type=str, default="auto", choices=["auto", "file_equiv", "veribench_variants"])
    parser.add_argument("--max-items", type=int, default=0, help="0 means use all available items.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out-dir", type=str, default=str(EXP_DIR / "results" / "prompt_sensitivity_sweep"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    ensure_dir(out_dir)

    items = load_items(items_source=args.items_source, max_items=args.max_items, seed=args.seed)
    if not items:
        print("ERROR: No items found for selected items source.")
        return 1

    prompt_names = list(PROMPT_VARIANTS.keys())
    print("=" * 70)
    print("EXP 6: Prompt Sensitivity Sweep")
    print(f"model={args.model} | items={len(items)} | prompts={len(prompt_names)} | repeats={args.n_repeats}")
    print(f"items_source={args.items_source}")
    print("=" * 70)

    score_by_item = {}
    label_by_item = {}
    detail_rows = []

    for ix, item in enumerate(items):
        item_id = item["item_id"]
        score_by_item[item_id] = {}
        label_by_item[item_id] = {}
        print(f"[{ix+1}/{len(items)}] {item_id}")

        for prompt_name in prompt_names:
            prompt_template = PROMPT_VARIANTS[prompt_name]
            result = judge(
                generated_theorem=item["generated_theorem"],
                reference_impl=item["reference_impl"],
                model=args.model,
                n_repeats=args.n_repeats,
                prompt_template=prompt_template,
                cache_namespace=f"prompt_sensitivity:{prompt_name}",
            )
            score = float(result["mean"])
            label = score_to_label(score)
            score_by_item[item_id][prompt_name] = score
            label_by_item[item_id][prompt_name] = label
            detail_rows.append(
                {
                    "item_id": item_id,
                    "source": item["source"],
                    "group": item["group"],
                    "bug_level": item["bug_level"],
                    "prompt_name": prompt_name,
                    "score_mean": round(score, 6),
                    "score_std": round(float(result["std"]), 6),
                    "label": label,
                    "cached": bool(result.get("cached", False)),
                    "reasoning": result.get("reasoning", ""),
                }
            )

    per_item_rows = []
    flip_flags = []
    stds = []
    for item in items:
        item_id = item["item_id"]
        vals = [score_by_item[item_id][p] for p in prompt_names]
        labs = [label_by_item[item_id][p] for p in prompt_names]
        item_std = statistics.stdev(vals) if len(vals) > 1 else 0.0
        unique_labels = len(set(labs))
        flip = unique_labels > 1
        stds.append(item_std)
        flip_flags.append(1 if flip else 0)
        per_item_rows.append(
            {
                "item_id": item_id,
                "source": item["source"],
                "group": item["group"],
                "bug_level": item["bug_level"],
                "score_std_across_prompts": round(float(item_std), 6),
                "n_unique_labels": unique_labels,
                "label_flip": flip,
            }
        )

    pairwise = pairwise_stats(score_by_item, label_by_item, prompt_names)
    score_dists = summarize_score_distributions(score_by_item, prompt_names)

    flip_rate = sum(flip_flags) / max(1, len(flip_flags))
    mean_item_std = sum(stds) / max(1, len(stds))
    min_kappa = min((p["cohen_kappa"] for p in pairwise), default=0.0)
    min_spearman = min((p["spearman_r"] for p in pairwise), default=0.0)

    summary = {
        "experiment": "exp6_prompt_sensitivity_sweep",
        "model": args.model,
        "n_repeats": args.n_repeats,
        "items_source": args.items_source,
        "n_items": len(items),
        "n_prompt_variants": len(prompt_names),
        "prompt_names": prompt_names,
        "flip_rate": round(float(flip_rate), 6),
        "mean_score_std_across_prompts": round(float(mean_item_std), 6),
        "min_pairwise_kappa": round(float(min_kappa), 6),
        "min_pairwise_spearman": round(float(min_spearman), 6),
        "score_distributions": score_dists,
        "pairwise_metrics": pairwise,
    }

    write_json(out_dir / "summary.json", summary)
    write_json(out_dir / "per_item.json", {"rows": per_item_rows})
    write_json(out_dir / "details.json", {"rows": detail_rows})
    write_rows_csv(out_dir / "per_item.csv", per_item_rows)
    write_rows_csv(out_dir / "pairwise.csv", pairwise)
    write_rows_csv(out_dir / "details.csv", detail_rows)

    print("\nSummary:")
    print(f"  flip_rate={flip_rate:.4f}")
    print(f"  mean_item_std={mean_item_std:.4f}")
    print(f"  min_pairwise_kappa={min_kappa:.4f}")
    print(f"  min_pairwise_spearman={min_spearman:.4f}")
    print(f"  wrote: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
