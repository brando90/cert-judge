#!/usr/bin/env python3
"""
Experiment 1: Hard Identity Test
Show judge is semantic, not edit-distance based.

30 pairs x 4 variants x 3 judge calls = 360 calls.
"""
import json
import os
import random
import statistics
import sys
from pathlib import Path

EXP_DIR = Path(__file__).parent
sys.path.insert(0, str(EXP_DIR))

VERIBENCH_DIR = Path.home() / "veribench/veribench_dataset/lean_src/veribench"
RESULTS_DIR = EXP_DIR / "results" / "hard_identity"
FIGURES_DIR = EXP_DIR / "figures"
MODEL = "gpt-4o-mini"  # using OpenAI since Anthropic credits unavailable
N_FILES = 30

random.seed(42)


def collect_lean_files() -> list:
    """Collect .lean files from all VeriBench sets."""
    subdirs = ["easy_set", "cs_set", "humaneval_set", "realcode_set", "security_set"]
    all_files = []
    for subdir in subdirs:
        path = VERIBENCH_DIR / subdir
        if path.exists():
            all_files.extend(sorted(path.glob("*.lean")))
    print(f"Found {len(all_files)} total .lean files across all sets")
    random.shuffle(all_files)
    return all_files[:N_FILES]


def main():
    from utils.variant_generator import generate_variants
    from utils.metrics import levenshtein_normalized, pearson_r, spearman_r
    from utils.judge_caller import judge

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("EXP 1: Hard Identity Test")
    print(f"Model: {MODEL}, Files: {N_FILES}")
    print("=" * 60)

    files = collect_lean_files()
    if not files:
        print("ERROR: No files found.")
        sys.exit(1)

    all_results = []
    per_variant = {vt: {"lev": [], "judge": [], "std": []} for vt in ["RENAME", "REORDER", "STYLE", "ALPHA"]}

    for i, fpath in enumerate(files):
        content = fpath.read_text()
        print(f"\n[{i+1}/{len(files)}] {fpath.name}")

        variants = generate_variants(content)

        for variant in variants:
            vtype = variant["variant_type"]
            variant_code = variant["code"]

            lev = levenshtein_normalized(content, variant_code)

            print(f"  [{vtype}] lev={lev:.3f} | calling judge ...")
            result = judge(
                generated_theorem=variant_code,
                reference_impl=content,
                model=MODEL,
                n_repeats=3,
            )
            j_mean = result["mean"]
            j_std = result["std"]
            print(f"  [{vtype}] judge={j_mean:.3f} +/- {j_std:.3f} (cached={result['cached']})")

            per_variant[vtype]["lev"].append(lev)
            per_variant[vtype]["judge"].append(j_mean)
            per_variant[vtype]["std"].append(j_std)

            all_results.append({
                "file": fpath.name,
                "variant_type": vtype,
                "levenshtein": lev,
                "judge_mean": j_mean,
                "judge_std": j_std,
                "judge_scores": result["scores"],
                "cached": result["cached"],
            })

    # Compute overall statistics
    all_lev = [r["levenshtein"] for r in all_results]
    all_judge = [r["judge_mean"] for r in all_results]

    r_pearson, p_pearson = pearson_r(all_lev, all_judge)
    r_spearman, p_spearman = spearman_r(all_lev, all_judge)

    identity_mean = statistics.mean(all_judge) if all_judge else 0.0
    identity_std = statistics.stdev(all_judge) if len(all_judge) > 1 else 0.0

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print(f"  identity_mean = {identity_mean:.4f} +/- {identity_std:.4f}")
    print(f"  Pearson r(lev, judge) = {r_pearson:.4f} (p={p_pearson:.4f})")
    print(f"  Spearman r(lev, judge) = {r_spearman:.4f} (p={p_spearman:.4f})")
    print(f"  n_pairs = {len(all_results)}")

    # Pass criteria: identity_mean > 0.85 AND Pearson(edit, score) < 0.30
    passed = (identity_mean > 0.85) and (r_pearson < 0.30)
    print(f"  Pass criteria: identity_mean > 0.85 AND Pearson < 0.30")
    print(f"  Result: {'PASS' if passed else 'FAIL'}")

    print("\nPer-variant stats:")
    for vt, stats in per_variant.items():
        if stats["lev"]:
            ml = statistics.mean(stats["lev"])
            mj = statistics.mean(stats["judge"])
            ms = statistics.mean(stats["std"])
            print(f"  {vt}: mean_lev={ml:.3f}, mean_judge={mj:.3f} +/- {ms:.3f}")

    summary = {
        "identity_mean_score": round(identity_mean, 4),
        "identity_std": round(identity_std, 4),
        "monotonicity_spearman_r": 0.0,
        "weak_monotonicity_pct": 0.0,
        "pearson_edit_vs_judge": round(r_pearson, 4),
        "pearson_edit_pvalue": round(p_pearson, 4),
        "spearman_lev_judge": round(r_spearman, 4),
        "n_theorems": len(files),
        "n_pairs": len(all_results),
        "certified": 0,
        "lean_available": False,
        "model": MODEL,
        "passed": passed,
        "per_variant": {
            vt: {
                "mean_lev": round(statistics.mean(v["lev"]), 4) if v["lev"] else 0.0,
                "mean_judge": round(statistics.mean(v["judge"]), 4) if v["judge"] else 0.0,
                "mean_std": round(statistics.mean(v["std"]), 4) if v["std"] else 0.0,
            }
            for vt, v in per_variant.items()
        },
        "notes": (
            f"Hard identity: {len(files)} files x 4 variants. "
            f"identity_mean={identity_mean:.3f}, pearson_r={r_pearson:.3f}"
        ),
        "all_results": all_results,
    }

    summary_path = RESULTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nResults written to {summary_path}")

    # Create figure: 4-panel scatter (one per variant type)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        import seaborn as sns
        from scipy.stats import pearsonr

        sns.set_palette("colorblind")
        plt.rcParams.update({"font.size": 12})

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        variant_types = ["RENAME", "REORDER", "STYLE", "ALPHA"]
        colors = sns.color_palette("colorblind", 4)

        for idx, (vt, ax, color) in enumerate(zip(variant_types, axes.flatten(), colors)):
            lev_vals = per_variant[vt]["lev"]
            judge_vals = per_variant[vt]["judge"]

            if lev_vals and judge_vals:
                ax.scatter(lev_vals, judge_vals, alpha=0.6, color=color, s=40, label=vt)

                # Regression line
                if len(lev_vals) > 1:
                    z = np.polyfit(lev_vals, judge_vals, 1)
                    p_line = np.poly1d(z)
                    x_range = np.linspace(min(lev_vals), max(lev_vals), 50)
                    ax.plot(x_range, p_line(x_range), "r--", alpha=0.7, linewidth=2)
                    r_val, p_val = pearsonr(lev_vals, judge_vals)
                    ax.set_title(
                        f"{vt}\nr={r_val:.3f}, p={p_val:.3f}",
                        fontsize=12
                    )

            ax.set_xlabel("Levenshtein Distance", fontsize=12)
            ax.set_ylabel("Judge Score", fontsize=12)
            ax.set_xlim(-0.05, 1.05)
            ax.set_ylim(-0.05, 1.15)
            ax.axhline(0.85, color="green", linestyle=":", alpha=0.5)

        plt.suptitle(
            f"Hard Identity: Levenshtein vs Judge Score by Variant Type\n"
            f"Overall Pearson r={r_pearson:.3f} (p={p_pearson:.3f}), "
            f"identity_mean={identity_mean:.3f}",
            fontsize=13
        )
        plt.tight_layout()
        fig_pdf = FIGURES_DIR / "fig_hard_identity.pdf"
        fig_png = FIGURES_DIR / "fig_hard_identity.png"
        plt.savefig(fig_pdf, dpi=150, bbox_inches="tight")
        plt.savefig(fig_png, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Figure saved: {fig_pdf}")
    except Exception as e:
        print(f"WARNING: Figure creation failed: {e}")

    # Push to W&B
    print("\nPushing to W&B ...")
    try:
        from utils.push_per_run import push
        push(
            run_name="hard_identity",
            model=MODEL,
            results_path=str(summary_path),
            experiment="exp1_hard_identity",
            notes=f"identity_mean={identity_mean:.3f}, pearson_r={r_pearson:.3f}",
        )
    except Exception as e:
        print(f"WARNING: W&B push failed: {e}")

    return summary


if __name__ == "__main__":
    main()
