"""TLDR: Known-answer checks for the rating-pool analysis. No cached scores."""
import importlib.util
from pathlib import Path

p = Path(__file__).with_name("pool_analysis.py")
spec = importlib.util.spec_from_file_location("pool_analysis", p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_perfect_association_passes():
    x = list(range(20))
    row = mod.o1_gate(x, x, n_declared=20, draws=2000, seed=48)
    assert row["reading"] == "PASS"
    assert row["spearman"] == 1.0
    assert row["ci"]["lo"] > 0.20


def test_reversed_association_fails():
    x = list(range(20))
    row = mod.o1_gate([-v for v in x], x, n_declared=20, draws=2000, seed=48)
    assert row["reading"] == "FAIL"
    assert row["spearman"] == -1.0


def test_too_many_missing_units_are_inconclusive():
    x = list(range(31)) + [None] * 20
    y = list(range(31)) + [None] * 20
    row = mod.o1_gate(x, y, n_declared=51, draws=100, seed=48)
    assert row["reading"] == "INCONCLUSIVE"
    assert row["n_missing"] == 20


def test_constant_offset_is_invisible_to_spearman_and_visible_to_bias():
    human = [i / 29 for i in range(30)]
    judge = [v + 0.2 for v in human]
    row = mod.absolute_agreement(judge, human)
    assert row["spearman"] == 1.0
    assert abs(row["bias"] - 0.2) < 1e-9
    assert abs(row["mae"] - 0.2) < 1e-9
    assert row["icc_a1"] < row["icc_c1"]
    assert abs(row["judge_mean"] - row["human_mean"] - 0.2) < 1e-9


def test_identical_scores_have_icc_one():
    scores = [i / 10 for i in range(15)]
    row = mod.absolute_agreement(scores, scores)
    assert abs(row["icc_c1"] - 1) < 1e-9
    assert abs(row["icc_a1"] - 1) < 1e-9
    assert row["bias"] == 0


def test_false_acceptance_counts():
    screen = [0.95, 0.95, 0.2]
    meets = [True, False, False]
    row = mod.false_acceptance(screen, meets, tau=0.9)
    assert row["n_accepted"] == 2
    assert abs(row["false_acceptance"] - 0.5) < 1e-9
    assert abs(row["base_rate"] - (2 / 3)) < 1e-9


def test_human_gate_needs_both_pieces():
    assert mod.meets_human_gate(0.50, 0.21) is True
    assert mod.meets_human_gate(0.50, 0.20) is False
    assert mod.meets_human_gate(0.44, 0.30) is False
