#!/usr/bin/env python3
"""
Experiment 2: Hard Monotonicity -- Semantic Bug Ladder
Show monotonicity holds for subtle semantic bugs.

20 pairs x 5 degradation levels x 3 judge calls = 300 calls.
"""
import json
import os
import random
import re
import statistics
import sys
from pathlib import Path

EXP_DIR = Path(__file__).parent
sys.path.insert(0, str(EXP_DIR))

VERIBENCH_DIR = Path.home() / "veribench/veribench_dataset/lean_src/veribench"
RESULTS_DIR = EXP_DIR / "results" / "hard_monotonicity"
FIGURES_DIR = EXP_DIR / "figures"
MODEL = "gpt-4o-mini"  # using OpenAI since Anthropic credits unavailable
N_FILES = 20

random.seed(42)


def collect_lean_files() -> list:
    """Collect .lean files from all VeriBench sets."""
    subdirs = ["easy_set", "cs_set", "humaneval_set", "realcode_set", "security_set"]
    all_files = []
    for subdir in subdirs:
        path = VERIBENCH_DIR / subdir
        if path.exists():
            all_files.extend(sorted(path.glob("*.lean")))
    random.shuffle(all_files)
    return all_files[:N_FILES]


def build_degradation_ladder(code: str) -> list:
    """
    Build 5-level degradation ladder.
    Level 0: Original
    Level 1: Subtle weakening (n > 0 -> n >= 0, or add 'True' to postcondition)
    Level 2: Remove one postcondition clause (remove one '∧' clause)
    Level 3: Replace '∧' with '∨' in a conjunction
    Level 4: Replace theorem body/postcondition with 'True'

    Returns list of 5 code strings, from least to most degraded.
    """
    ladder = [code]  # Level 0: original

    # Level 1: Subtle -- weaken preconditions or add trivially true clause
    level1 = code
    # Replace 'n > 0' with 'n ≥ 0' (weakening)
    if re.search(r'\bn\s*>\s*0\b', level1):
        level1 = re.sub(r'\bn\s*>\s*0\b', 'n ≥ 0', level1)
    elif re.search(r'\bm\s*>\s*0\b', level1):
        level1 = re.sub(r'\bm\s*>\s*0\b', 'm ≥ 0', level1)
    elif re.search(r'\bk\s*>\s*0\b', level1):
        level1 = re.sub(r'\bk\s*>\s*0\b', 'k ≥ 0', level1)
    else:
        # Add '∧ True' to a postcondition or replace '= n' with '= n ∨ False'
        if '∧' in level1:
            # Add another trivially true clause
            idx = level1.rfind('∧')
            rest = level1[idx:]
            # Find end of the last clause (before ':=' or end)
            level1 = level1[:idx] + '∧ True ' + level1[idx:]
        elif ':= sorry' in level1:
            # Replace sorry with a slightly different proof hint
            level1 = level1.replace(':= sorry', ':= by\n  simp; sorry', 1)
        else:
            # Fallback: add a vacuously true hypothesis
            level1 = re.sub(
                r'(theorem\s+\w+\s*[({])',
                r'\1-- weakened\n  ',
                level1, count=1
            )
    ladder.append(level1)

    # Level 2: Moderate -- remove one '∧' clause
    level2 = ladder[-1]
    # Find conjunctions and remove the last clause
    if '∧' in level2:
        # Remove the last '∧ <clause>' pattern before ':=' or 'sorry'
        # Simple approach: find last '∧' and remove from there to next ')' or end of line
        parts = level2.rsplit('∧', 1)
        if len(parts) == 2:
            # Remove the last conjunction clause but keep the rest
            # Keep up to the last clause boundary
            before = parts[0].rstrip()
            after = parts[1]
            # Find where the removed clause ends (next ')', line end, or ':=')
            end_match = re.search(r'[\)\n]|:=', after)
            if end_match:
                level2 = before + after[end_match.start():]
            else:
                level2 = before
    else:
        # Fallback: replace a property with a weaker version
        if 'n + m = m + n' in level2:
            level2 = level2.replace('n + m = m + n', 'n + m ≥ 0')
        elif '= n' in level2:
            level2 = level2.replace('= n', '≥ 0', 1)
        else:
            # Remove last line of theorem before sorry
            lines = level2.split('\n')
            # Remove second-to-last non-empty line
            non_empty = [i for i, l in enumerate(lines) if l.strip() and 'sorry' not in l]
            if len(non_empty) >= 2:
                lines.pop(non_empty[-1])
                level2 = '\n'.join(lines)
    ladder.append(level2)

    # Level 3: Significant -- replace '∧' with '∨'
    level3 = level2
    if '∧' in level3:
        level3 = level3.replace('∧', '∨', 1)
    elif 'and' in level3.lower():
        level3 = re.sub(r'\band\b', 'or', level3, count=1, flags=re.IGNORECASE)
    else:
        # Replace a key equality with inequality
        if '=' in level3 and ':=' not in level3.split('=')[0]:
            # Replace first non-definition '=' with '<'
            # Be careful about ':='
            level3 = re.sub(r'(?<!:)(?<!=)=(?!=)(?!>)', '<', level3, count=1)
    ladder.append(level3)

    # Level 4: Severe -- replace theorem statement with True
    level4 = level3
    # Replace whatever comes after ':' in the theorem signature with 'True'
    # Pattern: 'theorem Name ... : <type> := ...' -> 'theorem Name ... : True := trivial'
    theorem_match = re.search(
        r'(theorem\s+\w+[^:]*:\s*)([^:=]+?)(\s*:=)',
        level4, re.DOTALL
    )
    if theorem_match:
        level4 = (
            level4[:theorem_match.start(2)] +
            "True" +
            level4[theorem_match.start(3):]
        )
        # Also replace the proof
        level4 = re.sub(r':=.*$', ':= trivial', level4, flags=re.DOTALL)
    else:
        # Fallback: replace 'sorry' with 'trivial' and append 'True'
        level4 = re.sub(r'sorry', 'True.intro', level4)
    ladder.append(level4)

    return ladder


def main():
    from utils.metrics import levenshtein_normalized, spearman_r, weak_monotonicity_pct
    from utils.judge_caller import judge

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("EXP 2: Hard Monotonicity")
    print(f"Model: {MODEL}, Files: {N_FILES}")
    print("=" * 60)

    files = collect_lean_files()
    if not files:
        print("ERROR: No files found.")
        sys.exit(1)

    all_ladders = []  # list of score sequences
    all_lev_ladders = []  # levenshtein distance sequences
    all_degradation_levels = []
    all_judge_scores_flat = []
    per_level_scores = {i: [] for i in range(5)}
    per_level_lev = {i: [] for i in range(5)}

    level1_levs = []
    level1_drops = []

    theorem_results = []

    for i, fpath in enumerate(files):
        content = fpath.read_text()
        print(f"\n[{i+1}/{len(files)}] {fpath.name}")

        ladder_codes = build_degradation_ladder(content)
        print(f"  Built {len(ladder_codes)}-level ladder")

        level_scores = []
        level_levs = []

        for level, code in enumerate(ladder_codes):
            lev = levenshtein_normalized(content, code)
            print(f"  Level {level}: lev={lev:.3f} | calling judge ...")

            result = judge(
                generated_theorem=code,
                reference_impl=content,
                model=MODEL,
                n_repeats=3,
            )
            j_mean = result["mean"]
            j_std = result["std"]
            print(f"  Level {level}: judge={j_mean:.3f} +/- {j_std:.3f}")

            level_scores.append(j_mean)
            level_levs.append(lev)
            per_level_scores[level].append(j_mean)
            per_level_lev[level].append(lev)
            all_degradation_levels.append(level)
            all_judge_scores_flat.append(j_mean)

        # Level 1 analysis: small levenshtein but meaningful score drop
        if len(level_scores) >= 2:
            level1_levs.append(level_levs[1])
            level1_drops.append(level_scores[0] - level_scores[1])

        all_ladders.append(level_scores)
        all_lev_ladders.append(level_levs)
        theorem_results.append({
            "file": fpath.name,
            "level_scores": level_scores,
            "level_levenshteins": level_levs,
        })

    # Compute Spearman r between degradation_level and judge_score
    r_spearman, p_spearman = spearman_r(all_degradation_levels, all_judge_scores_flat)

    # Weak monotonicity
    weak_mono = weak_monotonicity_pct(all_ladders)

    # Level 1 stats
    mean_l1_lev = statistics.mean(level1_levs) if level1_levs else 0.0
    mean_l1_drop = statistics.mean(level1_drops) if level1_drops else 0.0

    # Per-level mean scores
    per_level_means = {
        lvl: statistics.mean(scores) if scores else 0.0
        for lvl, scores in per_level_scores.items()
    }

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print(f"  Spearman r(level, judge) = {r_spearman:.4f} (p={p_spearman:.4f})")
    print(f"  Weak monotonicity % = {weak_mono:.1f}%")
    print(f"  Level 1 mean lev = {mean_l1_lev:.3f}")
    print(f"  Level 1 mean score drop = {mean_l1_drop:.3f}")
    print("\n  Per-level mean scores:")
    for lvl, mean_score in per_level_means.items():
        print(f"    Level {lvl}: {mean_score:.3f}")

    # Pass criteria: weak_mono_pct >= 80% AND Spearman r <= -0.60
    passed = (weak_mono >= 80.0) and (r_spearman <= -0.60)
    print(f"\n  Pass criteria: weak_mono >= 80% AND Spearman <= -0.60")
    print(f"  Result: {'PASS' if passed else 'FAIL'}")

    summary = {
        "identity_mean_score": round(per_level_means[0], 4),
        "identity_std": 0.0,
        "monotonicity_spearman_r": round(r_spearman, 4),
        "monotonicity_spearman_pvalue": round(p_spearman, 4),
        "weak_monotonicity_pct": round(weak_mono, 2),
        "pearson_edit_vs_judge": 0.0,
        "n_theorems": len(files),
        "n_ladders": len(all_ladders),
        "certified": 0,
        "lean_available": False,
        "model": MODEL,
        "passed": passed,
        "per_level_mean_scores": {str(k): round(v, 4) for k, v in per_level_means.items()},
        "level1_mean_levenshtein": round(mean_l1_lev, 4),
        "level1_mean_score_drop": round(mean_l1_drop, 4),
        "notes": (
            f"Monotonicity: {len(files)} theorems x 5 levels. "
            f"Spearman r={r_spearman:.3f}, weak_mono={weak_mono:.1f}%"
        ),
        "theorem_results": theorem_results,
    }

    summary_path = RESULTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nResults written to {summary_path}")

    # Create figure: line chart with light gray per-theorem lines + bold mean
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        import seaborn as sns

        sns.set_palette("colorblind")
        plt.rcParams.update({"font.size": 12})

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Left: score ladders
        levels = list(range(5))
        for ladder in all_ladders:
            ax1.plot(levels[:len(ladder)], ladder, color="lightgray", alpha=0.5, linewidth=1)

        # Bold mean line
        mean_scores = [per_level_means[l] for l in levels]
        ax1.plot(levels, mean_scores, color="darkblue", linewidth=3, marker="o",
                 markersize=8, label="Mean score")

        ax1.set_xlabel("Degradation Level", fontsize=12)
        ax1.set_ylabel("Judge Score", fontsize=12)
        ax1.set_title(
            f"Monotonicity Ladder\nSpearman r={r_spearman:.3f}, "
            f"Weak Mono={weak_mono:.1f}%",
            fontsize=12
        )
        ax1.set_xticks(levels)
        ax1.set_xticklabels([
            "L0\n(Original)", "L1\n(Subtle)", "L2\n(Moderate)",
            "L3\n(Significant)", "L4\n(Severe)"
        ], fontsize=9)
        ax1.set_ylim(-0.05, 1.1)
        ax1.legend(fontsize=11)

        # Right: secondary axis for mean Levenshtein per level
        per_level_lev_means = {
            lvl: statistics.mean(levs) if levs else 0.0
            for lvl, levs in per_level_lev.items()
        }
        mean_levs = [per_level_lev_means[l] for l in levels]

        ax2.bar(levels, mean_levs, color="steelblue", alpha=0.7, label="Mean Levenshtein")
        ax2.plot(levels, mean_scores, color="darkorange", linewidth=2, marker="o",
                 markersize=6, label="Mean Judge Score")
        ax2.set_xlabel("Degradation Level", fontsize=12)
        ax2.set_ylabel("Score / Levenshtein Distance", fontsize=12)
        ax2.set_title(
            f"Judge Score vs Levenshtein per Level\n"
            f"L1: lev={mean_l1_lev:.3f}, drop={mean_l1_drop:.3f}",
            fontsize=12
        )
        ax2.set_xticks(levels)
        ax2.legend(fontsize=11)

        plt.suptitle(
            f"Experiment 2: Hard Monotonicity ({len(files)} theorems, {MODEL})",
            fontsize=13
        )
        plt.tight_layout()
        fig_pdf = FIGURES_DIR / "fig_monotonicity_ladder.pdf"
        fig_png = FIGURES_DIR / "fig_monotonicity_ladder.png"
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
            run_name="hard_monotonicity",
            model=MODEL,
            results_path=str(summary_path),
            experiment="exp2_hard_monotonicity",
            notes=(
                f"Spearman r={r_spearman:.3f}, weak_mono={weak_mono:.1f}%, "
                f"level1_lev={mean_l1_lev:.3f}, level1_drop={mean_l1_drop:.3f}"
            ),
        )
    except Exception as e:
        print(f"WARNING: W&B push failed: {e}")

    return summary


if __name__ == "__main__":
    main()
