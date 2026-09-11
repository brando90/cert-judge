from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "experiments" / "archive" / "04_veribench_validation" / "run_pti_v0.py"
SPEC = importlib.util.spec_from_file_location("run_pti_v0_test_module", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
PIPELINE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PIPELINE
SPEC.loader.exec_module(PIPELINE)


def test_pipeline_has_no_inference_client_or_credential_loader() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    forbidden = (
        "import openai",
        "from openai",
        "import anthropic",
        "from anthropic",
        "load_dotenv",
        "api_key",
    )

    assert all(token not in source for token in forbidden)


def test_config_fingerprint_ignores_only_pipeline_source_hash() -> None:
    first = {
        "metric_version": "PTI_v0",
        "implementation_provenance": {
            "pipeline_version": "v1",
            "pipeline_sha256": "a" * 64,
            "metric_sha256": "m" * 64,
        },
    }
    second = json.loads(json.dumps(first))
    second["implementation_provenance"]["pipeline_sha256"] = "b" * 64

    assert PIPELINE._config_fingerprint(first) == PIPELINE._config_fingerprint(second)
    second["implementation_provenance"]["metric_sha256"] = "n" * 64
    assert PIPELINE._config_fingerprint(first) != PIPELINE._config_fingerprint(second)


def test_fallback_reason_classifier_includes_bare_number_recovery() -> None:
    assert (
        PIPELINE._fallback_reason_class("Extracted bare number: 7")
        == "extracted bare number"
    )


def test_filesystem_case_probe_matches_observed_behavior(tmp_path: Path) -> None:
    probe = tmp_path / "IndependentCaseProbe"
    probe.write_text("probe\n", encoding="utf-8")
    observed = not (tmp_path / "independentcaseprobe").exists()

    assert PIPELINE._filesystem_case_sensitive(tmp_path) is observed


def test_score_reference_matches_frozen_exp16_last_theorem_contract() -> None:
    source = (
        "def helper := 1\n"
        "theorem first : True := by trivial\n"
        "theorem second : True := by trivial\n"
        "#check second\n"
    )

    reference = PIPELINE._score_reference(source)

    assert reference.startswith("theorem second")
    assert "theorem first" not in reference
    assert reference.endswith("#check second")
    assert PIPELINE._score_reference("def noTheorem := 1\n") == ("def noTheorem := 1\n")


def test_seeded_control_reproduces_historical_exp16_fixture() -> None:
    gold = (
        REPO_ROOT
        / "data/veribench_dataset/lean_src/veribench/real_code/0_bisect_right.lean"
    ).read_text(encoding="utf-8")
    candidate = (
        REPO_ROOT / "data/generated_agents/0_bisect_right__agent0.lean"
    ).read_text(encoding="utf-8")

    score = PIPELINE._deterministic_random_score(
        "random_r1",
        PIPELINE._score_reference(gold),
        candidate,
        seed=42,
    )

    assert round(score, 6) == 0.811802


def test_exclusive_lock_rejects_concurrent_writer_and_cleans_up(tmp_path: Path) -> None:
    lock_path = tmp_path / "audit.lock"

    with PIPELINE._exclusive_lock(lock_path):
        assert lock_path.exists()
        with (
            pytest.raises(RuntimeError, match="another PTI process"),
            PIPELINE._exclusive_lock(lock_path),
        ):
            pass
    assert not lock_path.exists()


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_materialize_local_controls_is_complete_and_deterministic(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate.lean"
    gold = tmp_path / "gold.lean"
    candidate.write_text("def answer := 42\n", encoding="utf-8")
    gold.write_text("def answer := 42\n", encoding="utf-8")
    content_hash = PIPELINE.sha256_text(candidate.read_text(encoding="utf-8"))
    probes = {
        "manifest_fingerprint": "probe-fingerprint",
        "artifacts": [
            {
                "artifact_id": "item|agent0|q0",
                "candidate_path": str(candidate),
                "candidate_sha256": content_hash,
                "gold_path": str(gold),
                "gold_sha256": content_hash,
                "P_eq": {"structurally_valid": True},
                "P_bm": {"structurally_valid": False},
                "P_ms": {"structurally_valid": False},
                "P_eqalpha": {"structurally_valid": False},
            }
        ],
    }
    request_template = {
        "artifact_id": "item|agent0|q0",
        "probe_type": "eq",
        "level": 0,
        "variant": "self",
        "candidate_sha256": content_hash,
        "reference_sha256": content_hash,
        "repeat_count": 3,
    }
    requests = {
        "probe_manifest_fingerprint": "probe-fingerprint",
        "config_fingerprint": "config-fingerprint",
        "manifest_fingerprint": "request-fingerprint",
        "requests": [
            {
                **request_template,
                "judge_id": "editdist_e1",
                "judge_kind": "deterministic_control",
                "score_cell_id": "edit-cell",
            },
            {
                **request_template,
                "judge_id": "random_r1",
                "judge_kind": "seeded_control",
                "score_cell_id": "random-cell",
            },
        ],
    }
    config = {
        "config_fingerprint": "config-fingerprint",
        "control_policy": {},
        "judges": [
            {
                "judge_id": "editdist_e1",
                "kind": "deterministic_control",
                "decoding": {"deterministic": True},
            },
            {
                "judge_id": "random_r1",
                "kind": "seeded_control",
                "decoding": {"seed": 0},
            },
        ],
    }
    probe_path = tmp_path / "probes.json"
    request_path = tmp_path / "requests.json"
    config_path = tmp_path / "config.json"
    output_path = tmp_path / "scores.json"
    _write_json(probe_path, probes)
    _write_json(request_path, requests)
    _write_json(config_path, config)

    result = PIPELINE.command_materialize_local_controls(
        argparse.Namespace(
            probe_manifest=probe_path,
            requests=request_path,
            config=config_path,
            out=output_path,
        )
    )

    assert result == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["record_count"] == 6
    edit_scores = [
        record["normalized_score"]
        for record in payload["records"]
        if record["score_cell_id"] == "edit-cell"
    ]
    assert edit_scores == [1.0, 1.0, 1.0]
    random_scores = [
        record["normalized_score"]
        for record in payload["records"]
        if record["score_cell_id"] == "random-cell"
    ]
    assert len(set(random_scores)) == 1
    assert 0.0 <= random_scores[0] <= 1.0


def test_cache_inventory_reports_exact_legacy_matches_but_admits_none(
    tmp_path: Path,
) -> None:
    candidate_hash = "a" * 64
    reference_hash = "b" * 64
    prompt_hash = "c" * 64
    requests_path = tmp_path / "requests.json"
    cache_path = tmp_path / "cache.json"
    out_path = tmp_path / "inventory.json"
    _write_json(
        requests_path,
        {
            "manifest_fingerprint": "requests",
            "requests": [
                {
                    "score_cell_id": "cell",
                    "model": "model",
                    "prompt_sha256": prompt_hash,
                    "candidate_sha256": candidate_hash,
                    "reference_sha256": reference_hash,
                    "repeat_count": 3,
                }
            ],
        },
    )
    _write_json(
        cache_path,
        {
            f"namespace|judge|model|{prompt_hash}|{candidate_hash}|{reference_hash}": {
                "scores": [0.5, 0.5, 0.5],
                "reasoning": "openai_error: unauthorized",
            }
        },
    )

    PIPELINE.command_inventory_cache(
        argparse.Namespace(
            requests=requests_path,
            cache=cache_path,
            out=out_path,
        )
    )

    result = json.loads(out_path.read_text())
    assert result["potential_content_model_matches"] == 1
    assert result["prompt_content_model_matches"] == 1
    assert result["prompt_content_model_repeat_matches"] == 1
    assert result["fallback_matched_request_cells"] == 1
    assert result["admissible_request_cells"] == 0


def test_build_pool_manifest_records_missing_grid_member(tmp_path: Path) -> None:
    candidates = tmp_path / "candidates"
    old_gold = tmp_path / "old"
    new_gold = tmp_path / "new"
    candidates.mkdir()
    old_gold.mkdir()
    new_gold.mkdir()
    (old_gold / "task.lean").write_text("def gold := 1\n", encoding="utf-8")
    (new_gold / "task.lean").write_text("def newer := 2\n", encoding="utf-8")
    (new_gold / "newOnly.lean").write_text("def newest := 3\n", encoding="utf-8")
    for agent in ("agent0", "agent2"):
        (candidates / f"task__{agent}.lean").write_text(
            f"def {agent} := 1\n", encoding="utf-8"
        )
    (candidates / "newOnly__agent0.lean").write_text(
        "def generated := 3\n", encoding="utf-8"
    )

    manifest = PIPELINE.build_pool_manifest(candidates, [old_gold, new_gold])

    assert manifest["observed_artifact_count"] == 3
    assert manifest["nominal_grid_count"] == 6
    assert manifest["missing_expected_artifacts"] == [
        {
            "artifact_id": "newOnly|agent1|q0",
            "item_id": "newOnly",
            "agent_id": "agent1",
            "generation_id": 0,
            "reason": "missing_candidate_file",
        },
        {
            "artifact_id": "newOnly|agent2|q0",
            "item_id": "newOnly",
            "agent_id": "agent2",
            "generation_id": 0,
            "reason": "missing_candidate_file",
        },
        {
            "artifact_id": "task|agent1|q0",
            "item_id": "task",
            "agent_id": "agent1",
            "generation_id": 0,
            "reason": "missing_candidate_file",
        },
    ]
    task_rows = [row for row in manifest["artifacts"] if row["item_id"] == "task"]
    new_only = next(row for row in manifest["artifacts"] if row["item_id"] == "newOnly")
    assert all(row["gold_path"].endswith("old/task.lean") for row in task_rows)
    assert all(row["gold_resolution_root_rank"] == 0 for row in task_rows)
    assert all(
        row["gold_alternatives"][0].endswith("new/task.lean") for row in task_rows
    )
    assert new_only["gold_path"].endswith("new/newOnly.lean")
    assert new_only["gold_resolution_root_rank"] == 1


def test_supplied_score_schema_computes_ideal_four_property_pti(tmp_path: Path) -> None:
    artifact_id = "task|agent0|q0"
    original_hash = "a" * 64
    gold_path = tmp_path / "gold.lean"
    gold_code = "def gold := 42\n"
    gold_path.write_text(gold_code, encoding="utf-8")
    gold_hash = PIPELINE.sha256_text(gold_code)
    alpha_hash = "c" * 64
    bug_hashes = [original_hash, "d" * 64, "e" * 64, "f" * 64, "1" * 64]
    spec_hashes = [original_hash, "2" * 64, "3" * 64, "4" * 64, "5" * 64]
    probe_row = {
        "artifact_id": artifact_id,
        "item_id": "task",
        "agent_id": "agent0",
        "generation_id": 0,
        "candidate_sha256": original_hash,
        "candidate_utf8_bytes": 100,
        "gold_path": str(gold_path),
        "gold_sha256": gold_hash,
        "gold_utf8_bytes": len(gold_code.encode("utf-8")),
        "P_eq": {"structurally_valid": True},
        "P_bm": {
            "structurally_valid": True,
            "levels": [
                {"level": index, "sha256": digest, "utf8_bytes": 100}
                for index, digest in enumerate(bug_hashes)
            ],
        },
        "P_ms": {
            "structurally_valid": True,
            "levels": [
                {"level": index, "sha256": digest, "utf8_bytes": 100}
                for index, digest in enumerate(spec_hashes)
            ],
        },
        "P_eqalpha": {
            "structurally_valid": True,
            "original_sha256": original_hash,
            "alpha_sha256": alpha_hash,
            "alpha_utf8_bytes": 100,
        },
    }
    probes = {
        "manifest_fingerprint": "probe-fingerprint",
        "valid_probe_counts": {"P_eq": 1, "P_bm": 1, "P_ms": 1, "P_eqalpha": 1},
        "artifacts": [probe_row],
    }
    config = {
        "prompt_provenance": {"source": "test", "sha256": "0" * 64},
        "score_policy": {
            "judge_repeats": 3,
            "property_score_coverage_threshold": 1.0,
            "output_token_upper_bound_per_call": 256,
        },
        "judges": [
            {
                "judge_id": "judge",
                "kind": "llm",
                "model": "model",
                "prompt": "prompt",
                "prompt_sha256": "9" * 64,
                "role": "primary",
                "family": "family",
                "prompt_static_utf8_bytes": 100,
                "pricing_usd_per_million_tokens": {
                    "input": 1.0,
                    "cached_input": 0.1,
                    "output": 2.0,
                    "source": "test",
                },
            }
        ],
    }
    probes_path = tmp_path / "probes.json"
    config_path = tmp_path / "config.json"
    requests_path = tmp_path / "requests.json"
    scores_path = tmp_path / "scores.json"
    out_dir = tmp_path / "properties"
    _write_json(probes_path, probes)
    _write_json(config_path, config)
    PIPELINE.command_build_requests(
        argparse.Namespace(
            probe_manifest=probes_path, config=config_path, out=requests_path
        )
    )
    requests = json.loads(requests_path.read_text())
    score_by_hash = {
        original_hash: 1.0,
        alpha_hash: 1.0,
        bug_hashes[1]: 0.8,
        bug_hashes[2]: 0.6,
        bug_hashes[3]: 0.4,
        bug_hashes[4]: 0.2,
        spec_hashes[1]: 0.8,
        spec_hashes[2]: 0.6,
        spec_hashes[3]: 0.4,
        spec_hashes[4]: 0.2,
    }
    unique_requests = {
        request["score_cell_id"]: request for request in requests["requests"]
    }
    records = [
        {
            "score_cell_id": cell_id,
            "repeat_id": repeat_id,
            "normalized_score": score_by_hash[request["candidate_sha256"]],
        }
        for cell_id, request in unique_requests.items()
        for repeat_id in range(3)
    ]
    _write_json(
        scores_path,
        {
            "schema_version": PIPELINE.SCORE_SCHEMA_VERSION,
            "metric_version": PIPELINE.METRIC_VERSION,
            "request_manifest_fingerprint": requests["manifest_fingerprint"],
            "records": records,
        },
    )

    PIPELINE.command_compute_properties(
        argparse.Namespace(
            probe_manifest=probes_path,
            requests=requests_path,
            config=config_path,
            scores=scores_path,
            out_dir=out_dir,
            bootstrap_iters=100,
            seed=0,
        )
    )

    result = json.loads((out_dir / "properties.json").read_text())
    judge = result["judges"][0]
    assert all(
        judge["properties"][name]["value"] == pytest.approx(1.0, abs=1e-12)
        for name in probes["valid_probe_counts"]
    )
    assert judge["PTI_eq_bm_ms"]["value"] == pytest.approx(1.0, abs=1e-12)
    assert judge["PTI_v0"]["value"] == pytest.approx(1.0, abs=1e-12)
    assert result["hard_gate"]["bridge_allowed"] is True


def test_score_schema_rejects_duplicate_repeat(tmp_path: Path) -> None:
    requests = {
        "manifest_fingerprint": "fingerprint",
        "requests": [{"score_cell_id": "cell", "repeat_count": 1}],
    }
    requests_path = tmp_path / "requests.json"
    scores_path = tmp_path / "scores.json"
    _write_json(requests_path, requests)
    _write_json(
        scores_path,
        {
            "schema_version": PIPELINE.SCORE_SCHEMA_VERSION,
            "metric_version": PIPELINE.METRIC_VERSION,
            "request_manifest_fingerprint": "fingerprint",
            "records": [
                {"score_cell_id": "cell", "repeat_id": 0, "normalized_score": 0.5},
                {"score_cell_id": "cell", "repeat_id": 0, "normalized_score": 0.5},
            ],
        },
    )

    try:
        PIPELINE._load_score_cells(scores_path, requests)
    except ValueError as error:
        assert "duplicate score record" in str(error)
    else:
        raise AssertionError("duplicate repeat must fail closed")


def test_criterion_uses_paired_panel_and_median_repeats(tmp_path: Path) -> None:
    candidate_dir = tmp_path / "candidates"
    gold_root = tmp_path / "gold"
    candidate_dir.mkdir()
    gold_root.mkdir()
    panel_rows = [
        {
            "gold_file": f"gold{index}.lean",
            "candidate_file": f"candidate{index}.lean",
            "strict_score_0_5": float(index),
            "lenient_score_0_5": float(index),
            "average_score_0_5": float(index),
        }
        for index in (1, 2, 3)
    ]
    panel_path = tmp_path / "panel.json"
    config_path = tmp_path / "config.json"
    detail_path = tmp_path / "detail.csv"
    out_dir = tmp_path / "criterion"
    cache_path = tmp_path / "cache.json"
    judge = {
        "judge_id": "judge",
        "kind": "llm",
        "model": "model",
        "prompt": "prompt",
        "prompt_sha256": "e" * 64,
        "role": "primary",
        "family": "family",
    }
    _write_json(panel_path, {"manifest_fingerprint": "panel", "rows": panel_rows})
    cache = {}
    for index in (1, 2, 3):
        gold = f"def gold{index} := {index}\n"
        candidate = f"def candidate{index} := {index}\n"
        (gold_root / f"gold{index}.lean").write_text(gold, encoding="utf-8")
        (candidate_dir / f"candidate{index}.lean").write_text(
            candidate, encoding="utf-8"
        )
        cache[PIPELINE._criterion_cache_key(judge, candidate, gold)] = {
            "model": "model",
            "scores": [index / 5, 0.0, index / 5],
            "reasoning": "valid judgment",
        }
    _write_json(cache_path, cache)
    _write_json(
        config_path,
        {
            "score_policy": {"judge_repeats": 3},
            "judges": [judge],
        },
    )
    with detail_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["judge_id", "row_type", "item_key", "repeat_scores"],
        )
        writer.writeheader()
        for index in (1, 2, 3):
            writer.writerow(
                {
                    "judge_id": "judge",
                    "row_type": "human_eval_union",
                    "item_key": f"gold{index}.lean::candidate{index}.lean",
                    "repeat_scores": json.dumps([index / 5, 0.0, index / 5]),
                }
            )

    PIPELINE.command_compute_criterion(
        argparse.Namespace(
            panel_manifest=panel_path,
            config=config_path,
            detail_rows=detail_path,
            legacy_cache=cache_path,
            candidate_dir=candidate_dir,
            gold_root=gold_root,
            bootstrap_iters=100,
            seed=0,
            out_dir=out_dir,
        )
    )

    result = json.loads((out_dir / "criterion.json").read_text())
    average = result["records"][0]["views"]["average"]
    assert average["status"] == PIPELINE.COMPUTED
    assert average["value"] == 1.0
    assert average["coverage"] == 1.0


def test_criterion_excludes_legacy_error_fallback(tmp_path: Path) -> None:
    candidate_dir = tmp_path / "candidates"
    gold_root = tmp_path / "gold"
    candidate_dir.mkdir()
    gold_root.mkdir()
    panel_rows = []
    detail_path = tmp_path / "detail.csv"
    panel_path = tmp_path / "panel.json"
    config_path = tmp_path / "config.json"
    cache_path = tmp_path / "cache.json"
    out_dir = tmp_path / "criterion"
    judge = {
        "judge_id": "model|prompt",
        "kind": "llm",
        "model": "model",
        "prompt": "prompt",
        "prompt_sha256": "f" * 64,
        "role": "primary",
        "family": "family",
    }
    cache = {}
    with detail_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["judge_id", "row_type", "item_key", "repeat_scores"],
        )
        writer.writeheader()
        for index in range(3):
            gold_file = f"gold{index}.lean"
            candidate_file = f"candidate{index}.lean"
            gold = f"def gold{index} := {index}\n"
            candidate = f"def candidate{index} := {index}\n"
            (gold_root / gold_file).write_text(gold, encoding="utf-8")
            (candidate_dir / candidate_file).write_text(candidate, encoding="utf-8")
            panel_rows.append(
                {
                    "gold_file": gold_file,
                    "candidate_file": candidate_file,
                    "average_score_0_5": float(index),
                    "strict_score_0_5": float(index),
                    "lenient_score_0_5": float(index),
                }
            )
            item_key = f"{gold_file}::{candidate_file}"
            writer.writerow(
                {
                    "judge_id": judge["judge_id"],
                    "row_type": "human_eval_union",
                    "item_key": item_key,
                    "repeat_scores": "[0.5, 0.5, 0.5]",
                }
            )
            key = PIPELINE._criterion_cache_key(judge, candidate, gold)
            cache[key] = {
                "model": "model",
                "scores": [0.5, 0.5, 0.5],
                "reasoning": (
                    "openai_error: unauthorized" if index == 0 else "valid judgment"
                ),
            }
    _write_json(panel_path, {"manifest_fingerprint": "panel", "rows": panel_rows})
    _write_json(
        config_path,
        {
            "score_policy": {"judge_repeats": 3},
            "criterion_policy": {"score_coverage_threshold": 1.0},
            "judges": [judge],
        },
    )
    _write_json(cache_path, cache)

    PIPELINE.command_compute_criterion(
        argparse.Namespace(
            panel_manifest=panel_path,
            config=config_path,
            detail_rows=detail_path,
            legacy_cache=cache_path,
            candidate_dir=candidate_dir,
            gold_root=gold_root,
            bootstrap_iters=100,
            seed=0,
            out_dir=out_dir,
        )
    )

    result = json.loads((out_dir / "criterion.json").read_text())
    record = result["records"][0]
    assert record["lineage"]["fallback_count"] == 1
    assert record["lineage"]["verified_count"] == 2
    assert record["views"]["average"]["status"] == PIPELINE.NOT_COMPUTABLE
    assert record["views"]["average"]["coverage"] == pytest.approx(2 / 3)


def test_sesoi_simulation_reports_frozen_decision_power(tmp_path: Path) -> None:
    criterion_path = tmp_path / "criterion.json"
    out_path = tmp_path / "sesoi.json"
    _write_json(
        criterion_path,
        {
            "records": [
                {
                    "role": "primary",
                    "views": {"average": {"status": PIPELINE.COMPUTED, "value": value}},
                }
                for value in (-0.2, 0.0, 0.2, 0.4, 0.6)
            ]
        },
    )

    PIPELINE.command_simulate_sesoi(
        argparse.Namespace(
            criterion=criterion_path,
            rhos=[0.0, 0.99],
            draws=1000,
            seed=0,
            sesoi=0.5,
            decision_bootstrap_iters=1000,
            out=out_path,
        )
    )

    result = json.loads(out_path.read_text())
    low, high = result["rows"]
    assert low["positive_decision_rate"] < 0.15
    assert high["positive_decision_rate"] > 0.85
    latent = 2.0 * math.sin(math.pi * high["rho_target"] / 6.0)
    expected = 0.5 - math.asin(latent) / math.pi
    assert high["gaussian_reference_pairwise_misordering_rate"] == pytest.approx(
        expected
    )
    assert "analytic_top1_benefit_retention" not in high


def test_frozen_artifacts_quarantine_fallbacks_and_bind_lean_environment() -> None:
    results = REPO_ROOT / "experiments/archive/04_veribench_validation/results_pti_v0_v4"
    criterion = json.loads((results / "criterion/criterion.json").read_text())
    records = {record["judge_id"]: record for record in criterion["records"]}
    affected = records["gpt-5.3-codex|P8_STRICT_B"]

    assert affected["lineage"]["fallback_count"] == 8
    assert affected["lineage"]["verified_count"] == 64
    assert affected["views"]["average"]["status"] == PIPELINE.NOT_COMPUTABLE
    assert affected["views"]["average"]["coverage"] == pytest.approx(64 / 72)
    assert all(
        record["lineage"]["fallback_count"] == 0
        and record["views"]["average"]["coverage"] == 1.0
        for judge_id, record in records.items()
        if judge_id != "gpt-5.3-codex|P8_STRICT_B"
    )

    probes = json.loads((results / "probe_validity_manifest.json").read_text())
    environment = probes["lean_environment"]
    assert [record["module"] for record in environment["prepared_local_modules"]] == [
        "VeriBench",
        "VeriBench.Common",
        "VeriBench.Prelude",
    ]
    assert all(record["ok"] for record in environment["prepared_local_modules"])
    assert environment["platform_system"]
    assert environment["platform_release"]
    assert environment["platform_machine"]
    assert isinstance(environment["filesystem_case_sensitive"], bool)
    assert "platform-dependent" in environment["module_case_caveat"]
    assert environment["lake_manifest_sha256"]
    assert environment["available_olean_module_count"] == len(
        environment["available_olean_modules"]
    )
    rejected_timeouts = sum(
        row["P_bm"].get("rejected_compile_classes", {}).get("timeout", 0)
        + row["P_ms"].get("rejected_compile_classes", {}).get("timeout", 0)
        for row in probes["artifacts"]
    )
    assert rejected_timeouts == 4


def test_bridge_status_does_not_compute_statistic_without_properties(
    tmp_path: Path,
) -> None:
    properties_path = tmp_path / "properties_status.json"
    criterion_path = tmp_path / "criterion.json"
    out_path = tmp_path / "bridge.json"
    _write_json(
        properties_path, {"status": PIPELINE.NOT_COMPUTABLE, "reason": "no scores"}
    )
    _write_json(criterion_path, {"records": []})

    PIPELINE.command_compute_bridge(
        argparse.Namespace(
            properties=properties_path,
            criterion=criterion_path,
            variant="PTI_v0",
            prebridge_commit=None,
            bootstrap_iters=100,
            seed=0,
            out=out_path,
        )
    )

    result = json.loads(out_path.read_text())
    assert result["status"] == PIPELINE.NOT_COMPUTABLE
    assert result["bridge_statistic_computed"] is False


def test_bridge_status_does_not_compute_statistic_when_hard_gate_fails(
    tmp_path: Path,
) -> None:
    properties_path = tmp_path / "properties.json"
    criterion_path = tmp_path / "criterion.json"
    out_path = tmp_path / "bridge.json"
    hard_gate = {
        "bridge_allowed": False,
        "primary_judge_count": 5,
        "not_computable_primary_judges_by_property": {"P_eq": 5},
    }
    _write_json(
        properties_path,
        {"judges": [{"judge_id": "control"}], "hard_gate": hard_gate},
    )
    _write_json(criterion_path, {"records": []})

    PIPELINE.command_compute_bridge(
        argparse.Namespace(
            properties=properties_path,
            criterion=criterion_path,
            variant="PTI_v0",
            prebridge_commit=None,
            bootstrap_iters=100,
            seed=0,
            out=out_path,
        )
    )

    result = json.loads(out_path.read_text())
    assert result["status"] == PIPELINE.NOT_COMPUTABLE
    assert result["bridge_statistic_computed"] is False
    assert result["hard_gate"] == hard_gate
