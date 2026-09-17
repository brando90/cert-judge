import importlib.util
from pathlib import Path

import numpy as np
import pytest


path = Path(__file__).resolve().parents[1] / "experiments/archive/30_proxy_trust_index_held_out_validity/expt_v3/run_audit.py"
spec = importlib.util.spec_from_file_location("criterion_audit_test", path)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_pairwise_ties_and_direction():
    assert audit.pair_accuracy([1, 1, 0], [2, 1, 0]) == (5 / 6, 3, 0)
    assert audit.pair_accuracy([0, 1, 2], [2, 1, 0]) == (0, 3, 0)
    value, unequal, tied = audit.pair_accuracy([0, 1, 2], [1, 1, 1])
    assert np.isnan(value) and unequal == 0 and tied == 3


def test_between_problem_effect_does_not_survive_centering():
    prediction = [0, 1, 10, 11]
    target = [1, 0, 11, 10]
    groups = [np.array([0, 1]), np.array([2, 3])]
    assert np.corrcoef(prediction, target)[0, 1] > 0
    assert audit.centered_pearson(prediction, target, groups) == pytest.approx(-1)
    assert np.isnan(audit.centered_pearson([1, 1, 1, 1], target, groups))


def test_problem_bootstrap_preserves_duplicate_weights_and_missingness():
    draws = np.array([[0, 0, 1], [0, 1, 2], [1, 1, 1]])
    values = np.array([1, np.nan, 0])
    result = audit.bootstrap_means(values, draws)
    assert result[0] == 1 and result[1] == 0.5 and np.isnan(result[2])


def test_inventory_selection_does_not_depend_on_labels_or_input_order():
    rows = [{"gold_file": f"p{i}.lean", "label": i} for i in range(12)]
    first = audit.pilot_inventory(rows, [], [], [])
    changed = [{**r, "label": -r["label"]} for r in reversed(rows)]
    second = audit.pilot_inventory(changed, [], [], [])
    assert first == second
    assert len(first["selected_problems"]) == 6
    assert first["status"] == "CACHE_REPLAY_ONLY"


def test_inventory_records_observed_repeats_and_rejects_missing_scores():
    rows = [{"gold_file": "p.lean"}]
    requests = [{"artifact_id": "p|a|g", "judge_id": "j", "score_cell_id": "c", "probe_type": "criterion"}]
    scores = [{"judge_id": "j", "score_cell_id": "c", "repeat_id": i, "normalized_score": 0.5}
              for i in (2, 0, 1)]
    result = audit.pilot_inventory(rows, ["j"], requests, scores)
    assert result["observed_cells"] == [{"judge_id": "j", "score_cell_id": "c", "repeat_ids": [0, 1, 2]}]
    assert result["missing_property_request_types"] == ["eq", "eqalpha", "bm", "ms"]
    with pytest.raises(ValueError):
        audit.pilot_inventory(rows, ["j"], requests, scores[:-1])
    with pytest.raises(ValueError):
        audit.pilot_inventory(rows, ["j"], requests, [])


def test_all_human_ties_have_undefined_intervals_and_render():
    rows = [{"gold_file": f"p{i}.lean"} for i in range(24) for _ in range(3)]
    judges = [audit.STRING, "primary"]
    metadata = {audit.STRING: {"role": "control"}, "primary": {"role": "primary"}}
    result = audit.analyze(judges, metadata, rows, np.full((2, 72, 3), .5),
                           {"average": np.full(72, .5)})
    view = result["views"]["average"]
    assert view["decision"] == "INCONCLUSIVE"
    assert view["differences"]["primary"]["string_minus_primary"] is None
    assert view["differences"]["primary"]["conditional_95_interval"]["undefined_draws"] == 2000
    assert "[undefined, undefined]" in audit.report(result, {"candidate_count": 18})
