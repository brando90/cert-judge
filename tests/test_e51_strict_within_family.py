"""TLDR: Locked reading rule for experiment 51. Does not join the cached scores."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "experiments/archive/51_strict_weakening_within_fuller_context_heldout_judges/scripts/analyze_e51.py"


def load():
    spec = importlib.util.spec_from_file_location("analyze_e51", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_readings_match_the_locked_gate():
    mod = load()
    assert mod.reading(0.56, 0.01, 12) == "PASS"
    assert mod.reading(0.44, 0.01, 12) == "FAIL"
    assert mod.reading(0.80, 0.05, 12) == "FAIL"
    assert mod.reading(0.0, 0.01, 12) == "REVERSED"
    assert mod.reading(-0.2, 0.9, 12) == "REVERSED"
    assert mod.reading(0.9, 0.01, 7) == "NOT_COMPUTABLE"
    assert mod.reading(None, 0.01, 12) == "NOT_COMPUTABLE"


def test_protocol_locks_the_inherited_gate():
    text = (SCRIPT.parent.parent / "PROTOCOL.md").read_text()
    assert "Spearman ≥ 0.45" in text
    assert "p-val < 0.05" in text
    assert "file_level_strict_only.weakening" in text
