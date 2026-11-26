"""Frozen decision rule and the individual-rating RPS endpoint. No data files."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/scripts"))
import metrics as M  # noqa: E402
from run_69a import success_rule  # noqa: E402


def test_perfect_forecast_rps_is_zero():
    q = np.array([0, 0, 0, 0, 0, 1], dtype=float)
    assert M.rps_item(q, [5, 5, 5]) == 0.0


def test_success_requires_both_clauses():
    assert success_rule(-0.02, -0.04, -0.01, 0.01, 0.03) is True
    assert success_rule(-0.02, -0.04, 0.01, 0.01, 0.03) is False
    assert success_rule(-0.02, -0.04, -0.01, -0.01, 0.02) is False
    assert success_rule(0.01, 0.00, 0.02, 0.01, 0.03) is False
