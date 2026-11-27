import json
import sys
from pathlib import Path

import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from common import digit_probs_from_top, items_from_ratings, reject_model, within_cap  # noqa: E402
from eval_69b import beats_const, evaluate  # noqa: E402


def test_repairs_t06_path_and_counts_100():
    items = items_from_ratings()
    assert len(items) == 100
    item = next(it for it in items if it["item_id"].endswith("item020"))
    assert item["candidate_file"] == "task_16_certificate_hostname/agent_lean/agent_2.lean"
    assert sum(len(it["ratings"]) for it in items) == 250


def test_digit_logprobs_and_budget_and_agy():
    probs, mass = digit_probs_from_top([("5", 0.0), ("4", -10.0)])
    assert probs is not None and abs(probs[5] - 1) < 1e-3
    assert digit_probs_from_top([("hello", 0.0)])[0] is None
    assert within_cap(26.9, 0.05) is True
    assert within_cap(26.9, 0.2) is False
    try:
        reject_model("google/gemini-2.5-pro")
    except SystemExit:
        pass
    else:
        raise AssertionError("gemini should be refused")


def test_point_mass_five_is_dry_run_not_a_decision():
    items = items_from_ratings()
    rows = [{
        "judge": "dry_run_point5", "source": "dry_run", "item_id": it["item_id"],
        "task": it["task"], "probs": [0, 0, 0, 0, 0, 1],
    } for it in items]
    out = evaluate(rows, items)
    assert out["dry_run"] is True
    judge = out["judges"][0]
    assert judge["beats_const_rps"] is False
    assert judge["status"] == "DRY_RUN"
    assert np.isfinite(judge["vs_const_rps"]["diff"])


def test_beats_const_sign():
    assert beats_const(-0.01, -0.001) is True
    assert beats_const(-0.01, 0.001) is False
    assert beats_const(0.01, 0.02) is False
