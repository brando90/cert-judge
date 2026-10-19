"""TLDR: The inherited in-distribution rule, on numbers small enough to check by hand."""
import importlib.util
from pathlib import Path
import numpy as np

p = Path(__file__).resolve().parent / "analyze_e54.py"
spec = importlib.util.spec_from_file_location("analyze_e54", p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def test_inside_when_median_and_coverage_hold():
    pool = np.array([0, 0, 0, 1, 1, 1, 1, 1, 1, 2], dtype=float)
    wave = np.array([1, 1, 1, 1], dtype=float)
    row = mod.in_distribution(pool, wave)
    assert row["in_distribution"] is True

def test_shift_when_median_is_outside():
    pool = np.array([1, 1, 1, 1, 2, 2, 2, 2, 3, 3], dtype=float)
    wave = np.array([10, 11, 12, 13], dtype=float)
    row = mod.in_distribution(pool, wave)
    assert row["in_distribution"] is False
    assert row["median"] == 11.5

def test_coverage_can_fail_while_the_median_is_inside():
    pool = np.linspace(0, 100, 21)
    wave = np.array([50, 50, 0, 100], dtype=float)
    row = mod.in_distribution(pool, wave, coverage=0.70)
    assert 0 <= row["pool_lo"] <= row["median"] <= row["pool_hi"]
    assert row["frac_inside"] < 0.70
    assert row["in_distribution"] is False
