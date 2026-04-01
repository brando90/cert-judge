#!/usr/bin/env python3
"""
Experiment 7: Scale Sensitivity Sweep

Vary grading scale expression while keeping rubric semantics fixed.
"""
import argparse
import statistics
import sys
from pathlib import Path

EXP_DIR = Path(__file__).parent
sys.path.insert(0, str(EXP_DIR))

from utils.judge_caller import judge
from utils.sensitivity_sweep import (
    SCALE_VARIANTS,
    ensure_dir,
    load_items,
    pairwise_stats,
    score_to_label,
    summarize_score_distributions,
    write_json,
    write_rows_csv,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run scale sensitivity sweep for LLM judge.")
    parser.add_argument("--model", type=str, default="gpt-4o-mini")
    parser.add_argument("--n-repeats", type=int, default=1)
    parser.add_argument("--items-source", type=str, default="file_equiv", choices=["auto", "file_equiv", "veribench_variants"])
    parser.add_argument("--max-items", type=int, default=0, help="0 means use all available items.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--pass-threshold", type=float, default=0.8)
    parser.add_argument("--out-dir", type=str, default=str(EXP_DIR / "results" / "scale_sensitivity_sweep"))
    return parser.parse_args()


def _make_figures(
    out_dir: Path,
    scale_names: list,
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

    idx = {name: i for i, name in enumerate(scale_names)}
    n = len(scale_names)
    spearman = np.zeros((n, n), dtype=float)
    kappa = np.zeros((n, n), dtype=float)
    np.fill_diagonal(spearman, 1.0)
    np.fill_diagonal(kappa, 1.0)
    for row in pairwise:
        i = idx[row["a"]]
        j = idx[row["b"]]
        spearman[i, j] = spearman[j, i] = float(row["spearman_r"])
        kappa[i, j] = kappa[j, i] = float(row["cohen_kappa"])

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(spearman, vmin=-1.0, vmax=1.0, cmap="coolwarm")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(scale_names, rotation=45, ha="right")
    ax.set_yticklabels(scale_names)
    ax.set_title("Scale Pairwise Spearman Correlation")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(figures_dir / "scale_pairwise_spearman_heatmap.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(kappa, vmin=-1.0, vmax=1.0, cmap="coolwarm")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(scale_names, rotation=45, ha="right")
    ax.set_yticklabels(scale_names)
    ax.set_title("Scale Pairwise Cohen's Kappa")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(figures_dir / "scale_pairwise_kappa_heatmap.png", dpi=180)
    plt.close(fig)

    item_ids = sorted(score_by_item.keys())
    by_scale = [[score_by_item[item_id][s] for item_id in item_ids] for s in scale_names]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.boxplot(by_scale, labels=scale_names, showfliers=False)
    ax.set_ylim(-0.02, 1.02)
    ax.set_ylabel("Normalized Score")
    ax.set_title("Normalized Score Distribution by Scale Variant")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(figures_dir / "scale_score_distribution_boxplot.png", dpi=180)
    plt.close(fig)

    stds = [float(r["score_std_across_scales"]) for r in per_item_rows]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(stds, bins=10)
    ax.set_xlabel("Per-item score std across scales")
    ax.set_ylabel("Count")
    ax.set_title("Scale Sensitivity Histogram")
    fig.tight_layout()
    fig.savefig(figures_dir / "scale_item_std_histogram.png", dpi=180)
    plt.close(fig)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    ensure_dir(out_dir)

    items = load_items(items_source=args.items_source, max_items=args.max_items, seed=args.seed)
    if not items:
        print("ERROR: No items found for selected items source.")
        return 1

    scale_names = list(SCALE_VARIANTS.keys())
    print("=" * 70)
    print("EXP 7: Scale Sensitivity Sweep")
    print(f"model={args.model} | items={len(items)} | scales={len(scale_names)} | repeats={args.n_repeats}")
    print(f"items_source={args.items_source} | pass_threshold={args.pass_threshold}")
    print("=" * 70)

    score_by_item = {}
    label_by_item = {}
    detail_rows = []

    for ix, item in enumerate(items):
        item_id = item["item_id"]
        score_by_item[item_id] = {}
        label_by_item[item_id] = {}
        print(f"[{ix+1}/{len(items)}] {item_id}")

        for scale_name in scale_names:
            prompt_template = SCALE_VARIANTS[scale_name]
            result = judge(
                generated_theorem=item["generated_theorem"],
                reference_impl=item["reference_impl"],
                model=args.model,
                n_repeats=args.n_repeats,
                prompt_template=prompt_template,
                cache_namespace=f"scale_sensitivity:{scale_name}",
            )
            score = float(result["mean"])
            label = score_to_label(score)
            score_by_item[item_id][scale_name] = score
            label_by_item[item_id][scale_name] = label
            detail_rows.append(
                {
                    "item_id": item_id,
                    "source": item["source"],
                    "group": item["group"],
                    "bug_level": item["bug_level"],
                    "scale_name": scale_name,
                    "score_mean": round(score, 6),
                    "score_std": round(float(result["std"]), 6),
                    "label": label,
                    "decision_pass": score >= args.pass_threshold,
                    "cached": bool(result.get("cached", False)),
                    "reasoning": result.get("reasoning", ""),
                }
            )

    per_item_rows = []
    pass_flip_flags = []
    score_stds = []
    for item in items:
        item_id = item["item_id"]
        vals = [score_by_item[item_id][s] for s in scale_names]
        item_std = statistics.stdev(vals) if len(vals) > 1 else 0.0
        score_stds.append(item_std)
        decisions = [v >= args.pass_threshold for v in vals]
        pass_flip = len(set(decisions)) > 1
        pass_flip_flags.append(1 if pass_flip else 0)
        per_item_rows.append(
            {
                "item_id": item_id,
                "source": item["source"],
                "group": item["group"],
                "bug_level": item["bug_level"],
                "score_std_across_scales": round(float(item_std), 6),
                "n_unique_scores_4dp": len(set(round(v, 4) for v in vals)),
                "pass_flip": pass_flip,
            }
        )

    pairwise = pairwise_stats(score_by_item, label_by_item, scale_names)
    score_dists = summarize_score_distributions(score_by_item, scale_names)
    baseline_std = score_dists.get("S1_UNIT_0_1", {}).get("std", 0.0)
    variance_ratio_vs_baseline = {}
    for scale_name in scale_names:
        scale_std = score_dists.get(scale_name, {}).get("std", 0.0)
        ratio = (scale_std / baseline_std) if baseline_std > 1e-9 else 0.0
        variance_ratio_vs_baseline[scale_name] = round(float(ratio), 6)

    pass_flip_rate = sum(pass_flip_flags) / max(1, len(pass_flip_flags))
    mean_item_std = sum(score_stds) / max(1, len(score_stds))
    min_spearman = min((p["spearman_r"] for p in pairwise), default=0.0)
    max_mad = max((p["mean_abs_diff"] for p in pairwise), default=0.0)

    summary = {
        "experiment": "exp7_scale_sensitivity_sweep",
        "model": args.model,
        "n_repeats": args.n_repeats,
        "items_source": args.items_source,
        "n_items": len(items),
        "n_scale_variants": len(scale_names),
        "scale_names": scale_names,
        "pass_threshold": args.pass_threshold,
        "pass_flip_rate": round(float(pass_flip_rate), 6),
        "mean_score_std_across_scales": round(float(mean_item_std), 6),
        "min_pairwise_spearman": round(float(min_spearman), 6),
        "max_pairwise_mean_abs_diff": round(float(max_mad), 6),
        "variance_ratio_vs_baseline": variance_ratio_vs_baseline,
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
        scale_names=scale_names,
        score_by_item=score_by_item,
        per_item_rows=per_item_rows,
        pairwise=pairwise,
    )

    print("\nSummary:")
    print(f"  pass_flip_rate={pass_flip_rate:.4f}")
    print(f"  mean_item_std={mean_item_std:.4f}")
    print(f"  min_pairwise_spearman={min_spearman:.4f}")
    print(f"  max_pairwise_MAD={max_mad:.4f}")
    print(f"  wrote: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
