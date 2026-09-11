#!/usr/bin/env python3
"""
Experiment 5: Edit Distance Control
Proves judge != string matching.

Smoke test: 10 theorem pairs, 4 variants each, compute:
- levenshtein_normalized
- judge_score (3x, mean)
- Pearson r between levenshtein and judge_score
"""
import json
import os
import random
import sys
from pathlib import Path

# Setup paths
EXP_DIR = Path(__file__).parent
sys.path.insert(0, str(EXP_DIR))

VERIBENCH_DIR = Path.home() / "veribench/veribench_dataset/lean_src/veribench"
RESULTS_DIR = EXP_DIR / "results" / "edit_distance_control"
FIGURES_DIR = EXP_DIR / "figures"
MODEL = "gpt-4o-mini"  # using OpenAI since Anthropic credits unavailable

random.seed(42)


def load_lean_files(n: int = 10) -> list:
    """Load n .lean files from VeriBench easy_set."""
    easy_set = VERIBENCH_DIR / "easy_set"
    files = sorted(easy_set.glob("*.lean"))
    if not files:
        print(f"WARNING: No files found in {easy_set}")
        return []
    random.shuffle(files)
    return files[:n]


def main():
    from utils.variant_generator import generate_variants
    from utils.metrics import levenshtein_normalized, pearson_r, jaccard_tokens
    from utils.judge_caller import judge

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("EXP 5: Edit Distance Control (Smoke Test)")
    print("=" * 60)

    files = load_lean_files(10)
    if not files:
        print("ERROR: No files found. Check VeriBench path.")
        sys.exit(1)

    print(f"Loaded {len(files)} theorem files")

    all_results = []
    levenshtein_scores = []
    judge_scores = []
    variant_stats = {vt: {"lev": [], "judge": []} for vt in ["RENAME", "REORDER", "STYLE", "ALPHA"]}

    for i, fpath in enumerate(files):
        content = fpath.read_text()
        print(f"\n[{i+1}/{len(files)}] Processing {fpath.name} ...")

        # Use file content as both generated_theorem and reference_impl
        # (identity test: same code should get high judge score)
        variants = generate_variants(content)

        for variant in variants:
            vtype = variant["variant_type"]
            variant_code = variant["code"]

            # String similarity: levenshtein between original and variant
            lev = levenshtein_normalized(content, variant_code)

            # Judge score: judge(variant, original_as_reference)
            # This tests if judge gives HIGH score for syntactic variants
            print(f"  Calling judge for {vtype} variant ...")
            result = judge(
                generated_theorem=variant_code,
                reference_impl=content,
                model=MODEL,
                n_repeats=3,
            )
            j_score = result["mean"]
            j_std = result["std"]

            print(f"  {vtype}: lev={lev:.3f}, judge={j_score:.3f} +/- {j_std:.3f}")

            levenshtein_scores.append(lev)
            judge_scores.append(j_score)
            variant_stats[vtype]["lev"].append(lev)
            variant_stats[vtype]["judge"].append(j_score)

            all_results.append({
                "file": fpath.name,
                "variant_type": vtype,
                "levenshtein": lev,
                "judge_mean": j_score,
                "judge_std": j_std,
                "judge_scores": result["scores"],
                "cached": result["cached"],
            })

    # Compute Pearson r
    r, p = pearson_r(levenshtein_scores, judge_scores)
    print(f"\nPearson r(levenshtein, judge_score) = {r:.4f} (p={p:.4f})")

    mean_judge = sum(judge_scores) / len(judge_scores) if judge_scores else 0.0
    mean_lev = sum(levenshtein_scores) / len(levenshtein_scores) if levenshtein_scores else 0.0

    print(f"Mean judge score: {mean_judge:.4f}")
    print(f"Mean levenshtein: {mean_lev:.4f}")

    # Pass criteria: mean judge_score on variants > 0.80 AND Pearson(lev, judge) < 0.30
    passed = (mean_judge > 0.80) and (r < 0.30)
    print(f"\nPass criteria: mean_judge > 0.80 AND Pearson < 0.30")
    print(f"Result: {'PASS' if passed else 'FAIL'}")

    # Per-variant stats
    print("\nPer-variant type stats:")
    for vtype, stats in variant_stats.items():
        if stats["lev"]:
            ml = sum(stats["lev"]) / len(stats["lev"])
            mj = sum(stats["judge"]) / len(stats["judge"])
            print(f"  {vtype}: mean_lev={ml:.3f}, mean_judge={mj:.3f}")

    # Write summary.json
    import statistics
    std_judge = statistics.stdev(judge_scores) if len(judge_scores) > 1 else 0.0

    summary = {
        "identity_mean_score": round(mean_judge, 4),
        "identity_std": round(std_judge, 4),
        "monotonicity_spearman_r": 0.0,
        "weak_monotonicity_pct": 0.0,
        "pearson_edit_vs_judge": round(r, 4),
        "pearson_edit_pvalue": round(p, 4),
        "n_theorems": len(files),
        "n_pairs": len(all_results),
        "mean_levenshtein": round(mean_lev, 4),
        "mean_judge_score": round(mean_judge, 4),
        "certified": 0,
        "lean_available": False,
        "model": MODEL,
        "passed_smoke_test": passed,
        "variant_stats": {
            vt: {
                "mean_lev": round(sum(v["lev"]) / len(v["lev"]), 4) if v["lev"] else 0.0,
                "mean_judge": round(sum(v["judge"]) / len(v["judge"]), 4) if v["judge"] else 0.0,
            }
            for vt, v in variant_stats.items()
        },
        "notes": f"Smoke test: {len(files)} files x 4 variants. Pearson(lev,judge)={r:.4f}",
        "all_results": all_results,
    }

    summary_path = RESULTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nResults written to {summary_path}")

    # Create figure
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns

        sns.set_palette("colorblind")
        plt.rcParams.update({"font.size": 12})

        variant_types = list(variant_stats.keys())
        mean_lev_vals = [
            sum(variant_stats[vt]["lev"]) / max(1, len(variant_stats[vt]["lev"]))
            for vt in variant_types
        ]
        mean_judge_vals = [
            sum(variant_stats[vt]["judge"]) / max(1, len(variant_stats[vt]["judge"]))
            for vt in variant_types
        ]

        x = range(len(variant_types))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))
        bars1 = ax.bar([xi - width/2 for xi in x], mean_lev_vals, width,
                       label="Mean Levenshtein Distance", color="steelblue", alpha=0.8)
        bars2 = ax.bar([xi + width/2 for xi in x], mean_judge_vals, width,
                       label="Mean Judge Score", color="darkorange", alpha=0.8)

        ax.set_xlabel("Variant Type", fontsize=12)
        ax.set_ylabel("Score", fontsize=12)
        ax.set_title(
            f"String Similarity vs Semantic Judge Score by Variant Type\n"
            f"Pearson r(lev, judge) = {r:.3f} (p={p:.3f})",
            fontsize=12
        )
        ax.set_xticks(list(x))
        ax.set_xticklabels(variant_types, fontsize=12)
        ax.set_ylim(0, 1.1)
        ax.legend(fontsize=12)
        ax.axhline(0.80, color="green", linestyle="--", alpha=0.5, label="Judge threshold (0.80)")

        for bar in bars1:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                    f"{bar.get_height():.2f}", ha='center', va='bottom', fontsize=9)
        for bar in bars2:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                    f"{bar.get_height():.2f}", ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        fig_pdf = FIGURES_DIR / "fig_string_vs_semantic.pdf"
        fig_png = FIGURES_DIR / "fig_string_vs_semantic.png"
        plt.savefig(fig_pdf, dpi=150, bbox_inches="tight")
        plt.savefig(fig_png, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Figure saved: {fig_pdf}")
        print(f"Figure saved: {fig_png}")
    except Exception as e:
        print(f"WARNING: Figure creation failed: {e}")

    # Push to W&B
    print("\nPushing to W&B ...")
    try:
        from utils.push_per_run import push
        push(
            run_name="edit_distance_control",
            model=MODEL,
            results_path=str(summary_path),
            experiment="exp5_edit_distance_control",
            notes=f"Smoke test. mean_judge={mean_judge:.3f}, pearson_r={r:.3f}",
        )
    except Exception as e:
        print(f"WARNING: W&B push failed: {e}")

    return summary


if __name__ == "__main__":
    main()
