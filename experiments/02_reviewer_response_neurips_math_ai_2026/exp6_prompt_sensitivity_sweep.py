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


def _make_figures(
    out_dir: Path,
    prompt_names: list,
    score_by_item: dict,
    per_item_rows: list,
    pairwise: list,
) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except Exception as e:
        print(f"WARNING: figure generation skipped (matplotlib unavailable): {e}")
        return

    figures_dir = out_dir / "figures"
    ensure_dir(figures_dir)

    idx = {name: i for i, name in enumerate(prompt_names)}
    n = len(prompt_names)
    spearman = np.zeros((n, n), dtype=float)
    kappa = np.zeros((n, n), dtype=float)
    np.fill_diagonal(spearman, 1.0)
    np.fill_diagonal(kappa, 1.0)
    for row in pairwise:
        i = idx[row["a"]]
        j = idx[row["b"]]
        spearman[i, j] = spearman[j, i] = float(row["spearman_r"])
        kappa[i, j] = kappa[j, i] = float(row["cohen_kappa"])

    # Spearman heatmap
    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(spearman, vmin=-1.0, vmax=1.0, cmap="coolwarm")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(prompt_names, rotation=90, fontsize=8)
    ax.set_yticklabels(prompt_names, fontsize=8)
    ax.set_title("Prompt Pairwise Spearman Correlation")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(figures_dir / "prompt_pairwise_spearman_heatmap.png", dpi=180)
    plt.close(fig)

    # Kappa heatmap
    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(kappa, vmin=-1.0, vmax=1.0, cmap="coolwarm")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(prompt_names, rotation=90, fontsize=8)
    ax.set_yticklabels(prompt_names, fontsize=8)
    ax.set_title("Prompt Pairwise Cohen's Kappa")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(figures_dir / "prompt_pairwise_kappa_heatmap.png", dpi=180)
    plt.close(fig)

    # Per-prompt score distribution boxplot
    item_ids = sorted(score_by_item.keys())
    by_prompt = [[score_by_item[item_id][p] for item_id in item_ids] for p in prompt_names]
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.boxplot(by_prompt, labels=prompt_names, showfliers=False)
    ax.set_ylim(-0.02, 1.02)
    ax.set_ylabel("Score")
    ax.set_title("Score Distribution by Prompt Variant")
    ax.tick_params(axis="x", rotation=90, labelsize=8)
    fig.tight_layout()
    fig.savefig(figures_dir / "prompt_score_distribution_boxplot.png", dpi=180)
    plt.close(fig)

    # Per-item std histogram
    stds = [float(r["score_std_across_prompts"]) for r in per_item_rows]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(stds, bins=10)
    ax.set_xlabel("Per-item score std across prompts")
    ax.set_ylabel("Count")
    ax.set_title("Prompt Sensitivity Histogram")
    fig.tight_layout()
    fig.savefig(figures_dir / "prompt_item_std_histogram.png", dpi=180)
    plt.close(fig)


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
    _make_figures(
        out_dir=out_dir,
        prompt_names=prompt_names,
        score_by_item=score_by_item,
        per_item_rows=per_item_rows,
        pairwise=pairwise,
    )

    print("\nSummary:")
    print(f"  flip_rate={flip_rate:.4f}")
    print(f"  mean_item_std={mean_item_std:.4f}")
    print(f"  min_pairwise_kappa={min_kappa:.4f}")
    print(f"  min_pairwise_spearman={min_spearman:.4f}")
    print(f"  wrote: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
