#!/usr/bin/env python3
"""
Experiment 05: Scaled Bug Ladder — P2 Monotonicity at Scale

Generates semantic bug ladders for ALL VeriBench files using Claude,
then scores each level with Claude as judge.

Usage:
    python run_bug_ladder.py --model claude-sonnet-4-20250514 --n_repeats 3
    python run_bug_ladder.py --model claude-sonnet-4-20250514 --n_files 10  # quick test
"""
import json
import os
import statistics
import sys
import time
from pathlib import Path

import fire

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
EXP_DIR = Path(__file__).parent
REPO_ROOT = EXP_DIR.parent.parent
VERIBENCH_DIR = REPO_ROOT / "data" / "veribench_dataset" / "lean_src" / "veribench"
RESULTS_DIR = EXP_DIR / "results"
LADDERS_DIR = RESULTS_DIR / "bug_ladders"
FIGURES_DIR = EXP_DIR / "figures"

# Also allow the judge_caller from exp02 (reuse caching + API logic)
sys.path.insert(0, str(EXP_DIR.parent / "02_reviewer_response_neurips_math_ai_2026"))

N_BUG_LEVELS = 5  # Level 0 (gold) through Level 4 (4 bugs)
DEFAULT_MODEL = "claude-sonnet-4-20250514"

# ---------------------------------------------------------------------------
# VeriBench splits
# ---------------------------------------------------------------------------
SPLITS = ["easy_set", "cs_set", "humaneval_set", "real_code", "security_6858", "security_python"]


# ---------------------------------------------------------------------------
# Bug insertion prompt
# ---------------------------------------------------------------------------
BUG_INSERTION_PROMPT = """You are an expert in Lean 4 formal verification. Your task is to \
insert exactly ONE new semantic bug into the following Lean 4 file.

RULES:
1. The bug must be SEMANTIC — it changes the mathematical meaning, not just formatting.
2. The file must remain syntactically valid Lean 4 (it should parse, proofs can use `sorry`).
3. Choose from these bug categories:
   - Property definition error: change a mathematical property (e.g., `n + 0 = n` -> `n + 1 = n`)
   - Postcondition weakening: remove a conjunct, or replace `∧` with `∨`
   - Implementation logic error: break the imperative impl (off-by-one, no-op, wrong op)
   - Equivalence error: break an equivalence theorem (e.g., `f a b = g a b` -> `f a b = f a b`)
   - Precondition error: make precondition trivially true or overly restrictive
4. Do NOT repeat a bug that was already inserted (see ALREADY INSERTED BUGS below).
5. Make the bug subtle — a careless reader might miss it.

ALREADY INSERTED BUGS:
{already_inserted_bugs}

CURRENT FILE (with {n_existing_bugs} bug(s) already):
```lean
{current_code}
```

Respond ONLY with valid JSON, no markdown fences:
{{"modified_code": "<the full modified lean file with the new bug>", "bug_description": "<1-2 sentence description of what you changed and why it's a bug>", "bug_category": "<one of: property_definition, postcondition_weakening, implementation_logic, equivalence_error, precondition_error>"}}"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def collect_lean_files(n_files: int = 0) -> list[tuple[str, Path]]:
    """Collect .lean files from all VeriBench splits, return (split_name, path) tuples."""
    all_files = []
    for split in SPLITS:
        split_dir = VERIBENCH_DIR / split
        if not split_dir.exists():
            print(f"  WARNING: {split_dir} not found, skipping")
            continue
        for f in sorted(split_dir.glob("*.lean")):
            # Skip tiny "safe" stub files (< 10 lines)
            if f.stat().st_size < 200:
                continue
            all_files.append((split, f))
    if n_files > 0:
        all_files = all_files[:n_files]
    print(f"Collected {len(all_files)} files across {len(SPLITS)} splits")
    return all_files


def call_claude_for_bug_insertion(
    current_code: str,
    already_inserted_bugs: list[str],
    n_existing_bugs: int,
    model: str,
) -> dict:
    """Call Claude to insert one semantic bug. Returns {modified_code, bug_description, bug_category}."""
    import anthropic

    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        key_path = Path.home() / "keys" / "anthropic_bm_key_koyejolab.txt"
        if key_path.exists():
            key = key_path.read_text().strip()
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set and key file not found")

    client = anthropic.Anthropic(api_key=key)

    bugs_str = "\n".join(f"  - Bug {i+1}: {b}" for i, b in enumerate(already_inserted_bugs))
    if not bugs_str:
        bugs_str = "  (none — this is the first bug)"

    prompt = BUG_INSERTION_PROMPT.format(
        already_inserted_bugs=bugs_str,
        n_existing_bugs=n_existing_bugs,
        current_code=current_code,
    )

    for attempt in range(3):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            # Parse JSON response
            parsed = json.loads(text)
            return {
                "modified_code": parsed["modified_code"],
                "bug_description": parsed.get("bug_description", "unknown"),
                "bug_category": parsed.get("bug_category", "unknown"),
            }
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                try:
                    parsed = json.loads(m.group())
                    return {
                        "modified_code": parsed["modified_code"],
                        "bug_description": parsed.get("bug_description", "unknown"),
                        "bug_category": parsed.get("bug_category", "unknown"),
                    }
                except Exception:
                    pass
            if attempt < 2:
                print(f"    JSON parse failed, retrying ({attempt+1}/3)...")
                time.sleep(1)
                continue
            raise RuntimeError(f"Failed to parse bug insertion response: {text[:200]}")
        except Exception as e:
            if attempt < 2:
                wait = 2 ** attempt
                print(f"    API error: {e}, retrying in {wait}s...")
                time.sleep(wait)
                continue
            raise


def generate_bug_ladder(
    gold_code: str,
    filename: str,
    model: str,
) -> tuple[list[str], list[dict]]:
    """
    Generate a 5-level bug ladder for a single file.
    Returns (ladder_codes[5], bug_info[4]).
    """
    ladder = [gold_code]  # Level 0 = original
    bug_infos = []
    current_code = gold_code
    inserted_bugs = []

    for level in range(1, N_BUG_LEVELS):
        print(f"    Generating level {level} (inserting bug {level})...")
        result = call_claude_for_bug_insertion(
            current_code=current_code,
            already_inserted_bugs=inserted_bugs,
            n_existing_bugs=level - 1,
            model=model,
        )
        current_code = result["modified_code"]
        inserted_bugs.append(result["bug_description"])
        ladder.append(current_code)
        bug_infos.append({
            "level": level,
            "bug_description": result["bug_description"],
            "bug_category": result["bug_category"],
        })
        time.sleep(0.5)  # rate limit courtesy

    return ladder, bug_infos


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(
    model: str = DEFAULT_MODEL,
    n_repeats: int = 3,
    n_files: int = 0,
    skip_generation: bool = False,
    judge_model: str = "",
):
    """
    Run the full scaled bug ladder experiment.

    Args:
        model: Model for bug insertion (and judging unless judge_model is set).
        n_repeats: Number of judge calls per pair (for stability/P4).
        n_files: Limit to first N files (0 = all). Use 5-10 for testing.
        skip_generation: If True, skip bug generation and only run judging
                         (assumes ladders already exist in results/bug_ladders/).
        judge_model: Model for judging (defaults to same as model).
    """
    from utils.judge_caller import judge
    from utils.metrics import spearman_r, weak_monotonicity_pct

    if not judge_model:
        judge_model = model

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    LADDERS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("EXPERIMENT 05: Scaled Bug Ladder (P2 at Scale)")
    print(f"  Bug insertion model : {model}")
    print(f"  Judge model         : {judge_model}")
    print(f"  Repeats per pair    : {n_repeats}")
    print(f"  Bug levels          : {N_BUG_LEVELS} (0=gold, 1-4=cumulative bugs)")
    print("=" * 70)

    files = collect_lean_files(n_files)
    if not files:
        print("ERROR: No VeriBench files found.")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Phase 1: Generate bug ladders (or load from disk)
    # ------------------------------------------------------------------
    all_bug_descriptions = {}  # filename -> list of bug_info dicts
    all_ladders = {}  # filename -> list of code strings

    if not skip_generation:
        print(f"\n--- Phase 1: Generating bug ladders for {len(files)} files ---\n")
        for idx, (split, fpath) in enumerate(files):
            fname = fpath.name
            gold_code = fpath.read_text()
            print(f"[{idx+1}/{len(files)}] {split}/{fname} ({len(gold_code)} chars)")

            # Check if ladder already generated (resume support)
            ladder_meta_path = LADDERS_DIR / f"{fname}.meta.json"
            if ladder_meta_path.exists():
                meta = json.loads(ladder_meta_path.read_text())
                if len(meta.get("bug_infos", [])) == N_BUG_LEVELS - 1:
                    print(f"  Already generated, skipping.")
                    all_bug_descriptions[fname] = meta["bug_infos"]
                    ladder_codes = [gold_code]
                    for lvl in range(1, N_BUG_LEVELS):
                        lvl_path = LADDERS_DIR / f"{fname}_level{lvl}.lean"
                        if lvl_path.exists():
                            ladder_codes.append(lvl_path.read_text())
                    all_ladders[fname] = ladder_codes
                    continue

            try:
                ladder_codes, bug_infos = generate_bug_ladder(gold_code, fname, model)
            except Exception as e:
                print(f"  ERROR generating ladder: {e}")
                continue

            # Save ladder files
            for lvl, code in enumerate(ladder_codes):
                lvl_path = LADDERS_DIR / f"{fname}_level{lvl}.lean"
                lvl_path.write_text(code)

            # Save metadata
            meta = {
                "filename": fname,
                "split": split,
                "gold_chars": len(gold_code),
                "bug_infos": bug_infos,
            }
            ladder_meta_path.write_text(json.dumps(meta, indent=2))

            all_bug_descriptions[fname] = bug_infos
            all_ladders[fname] = ladder_codes
            print(f"  Ladder saved ({len(ladder_codes)} levels)")

        # Save all bug descriptions
        desc_path = RESULTS_DIR / "bug_descriptions.json"
        desc_path.write_text(json.dumps(all_bug_descriptions, indent=2))
        print(f"\nBug descriptions saved to {desc_path}")
    else:
        print("\n--- Phase 1: Loading existing bug ladders ---\n")
        for idx, (split, fpath) in enumerate(files):
            fname = fpath.name
            gold_code = fpath.read_text()
            ladder_meta_path = LADDERS_DIR / f"{fname}.meta.json"
            if not ladder_meta_path.exists():
                print(f"  WARNING: No ladder found for {fname}, skipping")
                continue
            meta = json.loads(ladder_meta_path.read_text())
            all_bug_descriptions[fname] = meta.get("bug_infos", [])
            ladder_codes = [gold_code]
            for lvl in range(1, N_BUG_LEVELS):
                lvl_path = LADDERS_DIR / f"{fname}_level{lvl}.lean"
                if lvl_path.exists():
                    ladder_codes.append(lvl_path.read_text())
            all_ladders[fname] = ladder_codes
        print(f"Loaded {len(all_ladders)} existing ladders")

    # ------------------------------------------------------------------
    # Phase 2: Judge scoring
    # ------------------------------------------------------------------
    print(f"\n--- Phase 2: Judging {len(all_ladders)} ladders ---\n")

    # Map filename -> split for per-split analysis
    file_to_split = {fpath.name: split for split, fpath in files}

    all_scores = {}  # filename -> {level: {mean, std, scores}}
    all_level_scores_flat = []  # (level, score) for aggregate Spearman
    per_split_data = {s: {"levels": [], "scores": []} for s in SPLITS}
    per_file_results = []

    for idx, (fname, ladder_codes) in enumerate(all_ladders.items()):
        gold_code = ladder_codes[0]
        split = file_to_split.get(fname, "unknown")
        print(f"[{idx+1}/{len(all_ladders)}] {split}/{fname}")

        file_scores = {}
        level_score_pairs = []

        for level, code in enumerate(ladder_codes):
            result = judge(
                generated_theorem=code,
                reference_impl=gold_code,
                model=judge_model,
                n_repeats=n_repeats,
                cache_namespace="exp05_scaled_bug_ladder",
            )
            file_scores[level] = {
                "mean": result["mean"],
                "std": result["std"],
                "scores": result["scores"],
                "cached": result.get("cached", False),
            }
            print(f"  Level {level}: {result['mean']:.3f} +/- {result['std']:.3f}"
                  f" {'(cached)' if result.get('cached') else ''}")

            all_level_scores_flat.append((level, result["mean"]))
            per_split_data[split]["levels"].append(level)
            per_split_data[split]["scores"].append(result["mean"])
            level_score_pairs.append((level, result["mean"]))

        all_scores[fname] = file_scores

        # Per-file metrics
        levels_list = [p[0] for p in level_score_pairs]
        scores_list = [p[1] for p in level_score_pairs]
        if len(levels_list) >= 3:
            r_file, p_file = spearman_r(levels_list, scores_list)
        else:
            r_file, p_file = 0.0, 1.0

        # Per-file weak monotonicity
        ladder_scores = [file_scores[l]["mean"] for l in sorted(file_scores.keys())]
        mono_pairs = 0
        mono_ok = 0
        for i in range(len(ladder_scores) - 1):
            mono_pairs += 1
            if ladder_scores[i] >= ladder_scores[i + 1]:
                mono_ok += 1
        weak_mono_file = (mono_ok / mono_pairs * 100) if mono_pairs > 0 else 0.0

        per_file_results.append({
            "filename": fname,
            "split": split,
            "spearman_r": round(r_file, 4),
            "spearman_p": round(p_file, 4),
            "weak_mono_pct": round(weak_mono_file, 1),
            "level_means": {str(l): round(file_scores[l]["mean"], 4) for l in sorted(file_scores.keys())},
            "identity_score": round(file_scores[0]["mean"], 4),
        })

    # ------------------------------------------------------------------
    # Phase 3: Aggregate metrics
    # ------------------------------------------------------------------
    print(f"\n--- Phase 3: Computing aggregate metrics ---\n")

    all_levels = [p[0] for p in all_level_scores_flat]
    all_judge_scores = [p[1] for p in all_level_scores_flat]

    r_agg, p_agg = spearman_r(all_levels, all_judge_scores)

    # Weak monotonicity across all ladders
    all_ladder_sequences = []
    for fname, file_scores in all_scores.items():
        seq = [file_scores[l]["mean"] for l in sorted(file_scores.keys())]
        all_ladder_sequences.append(seq)
    weak_mono_agg = weak_monotonicity_pct(all_ladder_sequences)

    # Per-level means
    per_level_all = {l: [] for l in range(N_BUG_LEVELS)}
    for fname, file_scores in all_scores.items():
        for l in file_scores:
            per_level_all[l].append(file_scores[l]["mean"])
    per_level_means = {l: statistics.mean(s) for l, s in per_level_all.items() if s}
    per_level_stds = {l: statistics.stdev(s) if len(s) > 1 else 0.0 for l, s in per_level_all.items() if s}

    # P1 identity from Level 0
    identity_scores = per_level_all.get(0, [])
    p1_identity = statistics.mean(identity_scores) if identity_scores else 0.0

    # P4 stability from repeated scores
    repeat_scores_by_item = {}
    for fname, file_scores in all_scores.items():
        for l in file_scores:
            key = f"{fname}_level{l}"
            repeat_scores_by_item[key] = file_scores[l]["scores"]

    from cert_judge.hsj_scoring import compute_p4_stability
    p4_stability = compute_p4_stability(repeat_scores_by_item, tau=0.05)

    # Per-split aggregate
    per_split_summary = {}
    for split in SPLITS:
        sd = per_split_data[split]
        if len(sd["levels"]) >= 3:
            r_s, p_s = spearman_r(sd["levels"], sd["scores"])
        else:
            r_s, p_s = 0.0, 1.0
        per_split_summary[split] = {
            "n_pairs": len(sd["levels"]),
            "spearman_r": round(r_s, 4),
            "spearman_p": round(p_s, 4),
        }

    # Print summary
    print("=" * 70)
    print("AGGREGATE RESULTS")
    print(f"  Files scored         : {len(all_scores)}")
    print(f"  Total judge calls    : {len(all_level_scores_flat) * n_repeats}")
    print(f"  Spearman r(level, score) = {r_agg:.4f} (p={p_agg:.6f})")
    print(f"  Weak monotonicity %  = {weak_mono_agg:.1f}%")
    print(f"  P1 identity (Level 0)= {p1_identity:.4f}")
    print(f"  P4 stability         = {p4_stability:.4f}")
    print(f"\n  Per-level mean scores:")
    for l in range(N_BUG_LEVELS):
        m = per_level_means.get(l, 0.0)
        s = per_level_stds.get(l, 0.0)
        print(f"    Level {l}: {m:.3f} +/- {s:.3f}")

    print(f"\n  Per-split Spearman:")
    for split, info in per_split_summary.items():
        print(f"    {split}: r={info['spearman_r']:.3f} (n={info['n_pairs']})")

    passed = (weak_mono_agg >= 80.0) and (r_agg <= -0.60)
    print(f"\n  Pass criteria: weak_mono >= 80% AND Spearman <= -0.60")
    print(f"  Result: {'PASS' if passed else 'FAIL'}")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Save results
    # ------------------------------------------------------------------
    summary = {
        "experiment": "05_scaled_bug_ladder",
        "model_bug_insertion": model,
        "model_judge": judge_model,
        "n_files": len(all_scores),
        "n_bug_levels": N_BUG_LEVELS,
        "n_repeats": n_repeats,
        "aggregate": {
            "spearman_r": round(r_agg, 4),
            "spearman_p": round(p_agg, 6),
            "weak_monotonicity_pct": round(weak_mono_agg, 2),
            "p1_identity_mean": round(p1_identity, 4),
            "p4_stability": round(p4_stability, 4),
            "passed": passed,
        },
        "per_level_means": {str(k): round(v, 4) for k, v in per_level_means.items()},
        "per_level_stds": {str(k): round(v, 4) for k, v in per_level_stds.items()},
        "per_split": per_split_summary,
    }
    (RESULTS_DIR / "summary.json").write_text(json.dumps(summary, indent=2))

    # Per-file CSV
    import csv
    csv_path = RESULTS_DIR / "per_file_results.csv"
    if per_file_results:
        keys = per_file_results[0].keys()
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for row in per_file_results:
                # Flatten level_means dict to string for CSV
                row_copy = dict(row)
                row_copy["level_means"] = json.dumps(row_copy["level_means"])
                writer.writerow(row_copy)

    # Save all scores
    (RESULTS_DIR / "judge_scores.json").write_text(json.dumps(all_scores, indent=2))

    print(f"\nResults saved to {RESULTS_DIR}/")

    # ------------------------------------------------------------------
    # Phase 4: Figures
    # ------------------------------------------------------------------
    _make_figures(all_scores, all_ladder_sequences, per_level_means, per_level_stds,
                  per_file_results, per_split_data, r_agg, weak_mono_agg, judge_model)

    return summary


def _make_figures(all_scores, all_ladder_sequences, per_level_means, per_level_stds,
                  per_file_results, per_split_data, r_agg, weak_mono_agg, model):
    """Generate all figures."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("WARNING: matplotlib not available, skipping figures")
        return

    levels = list(range(N_BUG_LEVELS))

    # --- Figure 1: All-file monotonicity overlay ---
    fig, ax = plt.subplots(figsize=(8, 6))
    for seq in all_ladder_sequences:
        ax.plot(levels[:len(seq)], seq, color="lightgray", alpha=0.4, linewidth=0.8)

    means = [per_level_means.get(l, 0) for l in levels]
    stds = [per_level_stds.get(l, 0) for l in levels]
    ax.errorbar(levels, means, yerr=stds, color="darkblue", linewidth=3,
                marker="o", markersize=8, capsize=5, label="Mean +/- std")

    ax.set_xlabel("Bug Level (0 = gold, 4 = 4 cumulative bugs)", fontsize=12)
    ax.set_ylabel("Judge Score", fontsize=12)
    ax.set_title(
        f"Scaled Bug Ladder: P2 Monotonicity ({len(all_ladder_sequences)} files, {model})\n"
        f"Spearman r = {r_agg:.3f}, Weak Mono = {weak_mono_agg:.1f}%",
        fontsize=12,
    )
    ax.set_xticks(levels)
    ax.set_xticklabels([f"L{l}" for l in levels])
    ax.set_ylim(-0.05, 1.1)
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "monotonicity_ladder_all.png", dpi=150)
    plt.savefig(FIGURES_DIR / "monotonicity_ladder_all.pdf", dpi=150)
    plt.close()

    # --- Figure 2: Per-split subplots ---
    active_splits = [s for s in SPLITS if len(per_split_data[s]["levels"]) > 0]
    if active_splits:
        fig, axes = plt.subplots(1, len(active_splits), figsize=(5 * len(active_splits), 5))
        if len(active_splits) == 1:
            axes = [axes]
        for ax, split in zip(axes, active_splits):
            sd = per_split_data[split]
            # Group by level
            level_scores = {l: [] for l in levels}
            for lv, sc in zip(sd["levels"], sd["scores"]):
                level_scores[lv].append(sc)
            split_means = [statistics.mean(level_scores[l]) if level_scores[l] else 0 for l in levels]
            ax.plot(levels, split_means, "o-", color="steelblue", linewidth=2, markersize=6)
            ax.set_title(split, fontsize=11)
            ax.set_xlabel("Bug Level")
            ax.set_ylabel("Mean Judge Score")
            ax.set_ylim(-0.05, 1.1)
            ax.set_xticks(levels)
        plt.suptitle("Monotonicity by VeriBench Split", fontsize=13)
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "monotonicity_by_split.png", dpi=150)
        plt.close()

    # --- Figure 3: Per-file Spearman histogram ---
    spearman_vals = [r["spearman_r"] for r in per_file_results if r["spearman_p"] < 1.0]
    if spearman_vals:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(spearman_vals, bins=20, color="steelblue", edgecolor="white", alpha=0.8)
        ax.axvline(statistics.mean(spearman_vals), color="red", linestyle="--",
                   label=f"Mean = {statistics.mean(spearman_vals):.3f}")
        ax.set_xlabel("Per-file Spearman r (level vs score)")
        ax.set_ylabel("Count")
        ax.set_title(f"Distribution of Per-File Monotonicity (n={len(spearman_vals)})")
        ax.legend()
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "per_file_spearman_hist.png", dpi=150)
        plt.close()

    print(f"Figures saved to {FIGURES_DIR}/")


if __name__ == "__main__":
    fire.Fire(main)
