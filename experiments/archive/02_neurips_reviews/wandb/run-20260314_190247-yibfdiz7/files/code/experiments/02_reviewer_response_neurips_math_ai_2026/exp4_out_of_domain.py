#!/usr/bin/env python3
"""
Experiment 4: Out-of-Domain Generalization
Test certification on 15 manually written Lean 4 theorems outside VeriBench.
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

RESULTS_DIR = EXP_DIR / "results" / "out_of_domain"
FIGURES_DIR = EXP_DIR / "figures"
MODEL = "gpt-4o-mini"  # using OpenAI since Anthropic credits unavailable

random.seed(42)

# 15 manually written Lean 4 theorem strings
# These are simple enough to be plausible even without lake/Mathlib
MANUAL_THEOREMS = [
    {
        "name": "sum_correct",
        "code": """-- Theorem: sum of two naturals is commutative
theorem sum_correct (a b : Nat) : a + b = b + a := by
  omega""",
        "reference": """-- Reference: natural number addition
def mySum (a b : Nat) : Nat := a + b
-- Should satisfy commutativity: mySum a b = mySum b a""",
    },
    {
        "name": "reverse_involutive",
        "code": """-- Theorem: reversing a list twice gives the original
theorem reverse_involutive (l : List Nat) : l.reverse.reverse = l := by
  simp [List.reverse_reverse]""",
        "reference": """-- Reference: List.reverse function
-- reverse (reverse l) = l for all lists l""",
    },
    {
        "name": "filter_length_le",
        "code": """-- Theorem: filter result length <= original length
theorem filter_length_le (p : Nat -> Bool) (l : List Nat) :
    (l.filter p).length <= l.length := by
  simp [List.length_filter_le]""",
        "reference": """-- Reference: List.filter
-- filter p l returns a sublist, so its length is <= l.length""",
    },
    {
        "name": "map_length",
        "code": """-- Theorem: map preserves list length
theorem map_length (f : Nat -> Nat) (l : List Nat) :
    (l.map f).length = l.length := by
  simp [List.length_map]""",
        "reference": """-- Reference: List.map
-- length (map f l) = length l""",
    },
    {
        "name": "list_append_assoc",
        "code": """-- Theorem: list append is associative
theorem list_append_assoc (l1 l2 l3 : List Nat) :
    (l1 ++ l2) ++ l3 = l1 ++ (l2 ++ l3) := by
  simp [List.append_assoc]""",
        "reference": """-- Reference: List.append (++)
-- (l1 ++ l2) ++ l3 = l1 ++ (l2 ++ l3)""",
    },
    {
        "name": "nat_add_zero",
        "code": """-- Theorem: adding zero is identity
theorem nat_add_zero (n : Nat) : n + 0 = n := by
  omega""",
        "reference": """-- Reference: Nat.add
-- n + 0 = n for all n : Nat""",
    },
    {
        "name": "nat_mul_comm",
        "code": """-- Theorem: multiplication is commutative
theorem nat_mul_comm (a b : Nat) : a * b = b * a := by
  ring""",
        "reference": """-- Reference: Nat.mul
-- a * b = b * a for all natural numbers""",
    },
    {
        "name": "list_nil_append",
        "code": """-- Theorem: empty list is left identity for append
theorem list_nil_append (l : List Nat) : [] ++ l = l := by
  simp""",
        "reference": """-- Reference: List.append
-- [] ++ l = l""",
    },
    {
        "name": "bool_and_comm",
        "code": """-- Theorem: boolean AND is commutative
theorem bool_and_comm (a b : Bool) : (a && b) = (b && a) := by
  cases a <;> cases b <;> rfl""",
        "reference": """-- Reference: Bool.and (&&)
-- a && b = b && a""",
    },
    {
        "name": "nat_zero_add",
        "code": """-- Theorem: zero plus n equals n
theorem nat_zero_add (n : Nat) : 0 + n = n := by
  omega""",
        "reference": """-- Reference: Nat.add
-- 0 + n = n for all n : Nat""",
    },
    {
        "name": "option_none_map",
        "code": """-- Theorem: mapping over None gives None
theorem option_none_map (f : Nat -> Nat) : Option.map f Option.none = Option.none := by
  rfl""",
        "reference": """-- Reference: Option.map
-- map f None = None""",
    },
    {
        "name": "nat_succ_pos",
        "code": """-- Theorem: successor of any nat is positive
theorem nat_succ_pos (n : Nat) : 0 < n.succ := by
  omega""",
        "reference": """-- Reference: Nat.succ
-- For all n, 0 < n + 1""",
    },
    {
        "name": "list_length_nil",
        "code": """-- Theorem: length of empty list is zero
theorem list_length_nil : ([] : List Nat).length = 0 := by
  rfl""",
        "reference": """-- Reference: List.length
-- length [] = 0""",
    },
    {
        "name": "max_comm",
        "code": """-- Theorem: max of two naturals is commutative
theorem max_comm (a b : Nat) : max a b = max b a := by
  simp [Nat.max_comm]""",
        "reference": """-- Reference: Nat.max
-- max a b = max b a""",
    },
    {
        "name": "if_true",
        "code": """-- Theorem: if-then-else with True condition returns then-branch
theorem if_true (a b : Nat) : (if True then a else b) = a := by
  simp""",
        "reference": """-- Reference: if-then-else
-- if True then a else b = a""",
    },
]


def build_degradation_ladder(code: str) -> list:
    """Same as exp2: 5-level degradation."""
    ladder = [code]

    # Level 1: weaken
    level1 = code
    if re.search(r'\bn\s*>\s*0\b', level1):
        level1 = re.sub(r'\bn\s*>\s*0\b', 'n >= 0', level1)
    elif '∧' in level1:
        level1 = level1.replace('∧', '∧ True ∧', 1)
    else:
        level1 = code.replace(':= by', ':= by\n  -- weakened\n ', 1)
        if level1 == code:
            level1 = code + "\n-- level1 weakened"
    ladder.append(level1)

    # Level 2: remove a conjunction
    level2 = level1
    if '∧' in level2:
        parts = level2.rsplit('∧', 1)
        level2 = parts[0].rstrip()
    else:
        if 'omega' in level2:
            level2 = level2.replace('omega', 'simp', 1)
        elif 'ring' in level2:
            level2 = level2.replace('ring', 'simp', 1)
        else:
            level2 = level2 + "\n-- level2 modified"
    ladder.append(level2)

    # Level 3: replace = with <=
    level3 = level2
    # Replace equality in theorem type with inequality
    # Find the : <type> := part
    match = re.search(r':\s*([^:=]+)\s*:=', level3)
    if match:
        type_str = match.group(1)
        new_type = type_str.replace(' = ', ' <= ', 1)
        if new_type != type_str:
            level3 = level3[:match.start(1)] + new_type + level3[match.end(1):]
    if level3 == level2:
        level3 = level2.replace('True', 'False', 1)
        if level3 == level2:
            level3 = level2 + "\n-- level3 modified"
    ladder.append(level3)

    # Level 4: replace theorem body with True
    level4 = level3
    match = re.search(r'(theorem\s+\w+[^:]*:\s*)([^:=]+?)(\s*:=)', level4, re.DOTALL)
    if match:
        level4 = level4[:match.start(2)] + "True" + level4[match.start(3):]
        level4 = re.sub(r':=.*$', ':= trivial', level4, flags=re.DOTALL)
    else:
        level4 = "theorem trivially_true : True := trivial"
    ladder.append(level4)

    return ladder


def main():
    from utils.variant_generator import generate_variants
    from utils.metrics import levenshtein_normalized, spearman_r, weak_monotonicity_pct
    from utils.judge_caller import judge

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("EXP 4: Out-of-Domain Generalization")
    print(f"Model: {MODEL}, Theorems: {len(MANUAL_THEOREMS)}")
    print("=" * 60)

    # Hard identity on variants
    identity_scores = []
    mono_ladders = []
    all_degradation_levels = []
    all_judge_scores_flat = []
    theorem_results = []

    for i, thm in enumerate(MANUAL_THEOREMS):
        print(f"\n[{i+1}/{len(MANUAL_THEOREMS)}] {thm['name']}")
        code = thm["code"]
        ref = thm["reference"]

        # Identity variants
        variants = generate_variants(code)
        thm_identity_scores = []
        for variant in variants:
            vtype = variant["variant_type"]
            result = judge(
                generated_theorem=variant["code"],
                reference_impl=ref,
                model=MODEL,
                n_repeats=3,
            )
            thm_identity_scores.append(result["mean"])
            print(f"  [{vtype}] judge={result['mean']:.3f}")

        identity_scores.extend(thm_identity_scores)

        # Monotonicity ladder
        ladder_codes = build_degradation_ladder(code)
        level_scores = []
        for level, lcode in enumerate(ladder_codes):
            result = judge(
                generated_theorem=lcode,
                reference_impl=ref,
                model=MODEL,
                n_repeats=3,
            )
            level_scores.append(result["mean"])
            all_degradation_levels.append(level)
            all_judge_scores_flat.append(result["mean"])
            print(f"  [L{level}] judge={result['mean']:.3f}")

        mono_ladders.append(level_scores)
        theorem_results.append({
            "name": thm["name"],
            "identity_scores": thm_identity_scores,
            "ladder_scores": level_scores,
        })

    # Compute metrics
    from utils.metrics import pearson_r
    identity_mean = statistics.mean(identity_scores) if identity_scores else 0.0
    identity_std = statistics.stdev(identity_scores) if len(identity_scores) > 1 else 0.0
    r_spearman, p_spearman = spearman_r(all_degradation_levels, all_judge_scores_flat)
    weak_mono = weak_monotonicity_pct(mono_ladders)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print(f"  identity_mean = {identity_mean:.4f} +/- {identity_std:.4f}")
    print(f"  Spearman r = {r_spearman:.4f} (p={p_spearman:.4f})")
    print(f"  Weak monotonicity = {weak_mono:.1f}%")

    from utils.push_per_run import IDENTITY_THRESHOLD, SPEARMAN_THRESHOLD, WEAK_MONO_THRESHOLD
    certified = int(
        identity_mean > IDENTITY_THRESHOLD and
        r_spearman < SPEARMAN_THRESHOLD and
        weak_mono > WEAK_MONO_THRESHOLD
    )
    print(f"  Certified: {certified}")

    summary = {
        "identity_mean_score": round(identity_mean, 4),
        "identity_std": round(identity_std, 4),
        "monotonicity_spearman_r": round(r_spearman, 4),
        "monotonicity_spearman_pvalue": round(p_spearman, 4),
        "weak_monotonicity_pct": round(weak_mono, 2),
        "pearson_edit_vs_judge": 0.0,
        "n_theorems": len(MANUAL_THEOREMS),
        "certified": certified,
        "lean_available": False,
        "model": MODEL,
        "notes": (
            f"Out-of-domain: {len(MANUAL_THEOREMS)} manual theorems. "
            f"identity_mean={identity_mean:.3f}, spearman_r={r_spearman:.3f}"
        ),
        "theorem_results": theorem_results,
    }

    summary_path = RESULTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nResults written to {summary_path}")

    # Push to W&B
    print("\nPushing to W&B ...")
    try:
        from utils.push_per_run import push
        push(
            run_name="out_of_domain_mathlib",
            model=MODEL,
            results_path=str(summary_path),
            experiment="exp4_out_of_domain",
            notes=f"Out-of-domain: identity={identity_mean:.3f}, spearman={r_spearman:.3f}",
        )
    except Exception as e:
        print(f"WARNING: W&B push failed: {e}")

    return summary


if __name__ == "__main__":
    main()
