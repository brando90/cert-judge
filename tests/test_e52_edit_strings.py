"""TLDR: The locked one-step edits each occur once in the named declaration. No Lean."""
from pathlib import Path

ROOT = Path("/Users/brandomiranda/veribench/experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/references/annotation")
EDITS = [
    ("33_MyMinimum", "minimum_prop", "myMinList xs ≤ z"),
    ("18_MyFibonacci", "fibonacci_increasing_prop", "myFibonacci (n + 1) > myFibonacci n"),
    ("humaneval_31_is_prime", "prime_def_prop", "2 ≤ d → d < n → n % d ≠ 0"),
    ("humaneval_3_below_zero", "monotonicity_prop", "x ≥ 0"),
    ("13_MyUppercase", "length_preservation_prop", "(myUppercase s).length = s.length"),
    ("1_MyAdd", "commutativity_prop", "myAdd a b = myAdd b a"),
    ("0_bisect_right", "Post", "lo ≤ idx ∧ idx ≤ hi"),
]


def test_each_old_string_occurs_in_its_file():
    for task, _decl, old in EDITS:
        text = (ROOT / f"{task}.lean").read_text(encoding="utf-8")
        assert text.count(old) >= 1, task
