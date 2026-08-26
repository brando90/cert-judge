from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "experiments" / "29_pti_v0_cli_bridge" / "run_pti_v0_cli.py"


def _module():
    spec = importlib.util.spec_from_file_location("pti_v0_cli_tested", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_frozen_panel_roles_and_backends() -> None:
    module = _module()
    config = module.frozen_config()
    judges = config["judges"]
    assert len(judges) == 8
    assert sum(judge["role"] == "primary" for judge in judges) == 5
    assert sum(judge["role"] == "control" for judge in judges) == 3
    assert {judge["backend"] for judge in judges} == {"codex", "clauded", "local"}
    assert {judge["model"] for judge in judges if judge["model"]} == {
        "gpt-5.6-terra",
        "claude-sonnet-5",
    }
    assert all(judge["repeat_count"] == 3 for judge in judges)


def test_runner_contains_no_provider_or_key_surface() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    forbidden = (
        "openai.OpenAI(",
        "OpenAI(",
        "anthropic.Anthropic(",
        "messages.create(",
        "chat.completions.create(",
        "responses.create(",
        "~/keys/",
        "api.openai.com",
        "api.anthropic.com",
    )
    assert not any(value in text for value in forbidden)
    assert text.count("env=_child_env()") == 2


def test_child_environment_strips_all_api_keys() -> None:
    module = _module()
    source = {
        "PATH": "/bin",
        "OPENAI_API_KEY": "not-a-real-key",
        "ANTHROPIC_API_KEY": "not-a-real-key",
        "ARBITRARY_API_KEY": "not-a-real-key",
        "SAFE_VALUE": "retained",
    }
    assert module._child_env(source) == {"PATH": "/bin", "SAFE_VALUE": "retained"}


def test_batch_score_validation_is_fail_closed() -> None:
    module = _module()
    expected = ["a", "b"]
    valid = {
        "scores": [
            {"id": "a", "score": 0.0, "reasoning": "first"},
            {"id": "b", "score": 1.0, "reasoning": "second"},
        ]
    }
    assert [row["score"] for row in module._validate_batch_scores(valid, expected)] == [
        0.0,
        1.0,
    ]
    with pytest.raises(ValueError, match="id mismatch"):
        module._validate_batch_scores({"scores": valid["scores"][:1]}, expected)
    with pytest.raises(ValueError, match="duplicate"):
        module._validate_batch_scores(
            {"scores": [valid["scores"][0], valid["scores"][0]]}, expected
        )
    with pytest.raises(ValueError, match="invalid score"):
        module._validate_batch_scores(
            {
                "scores": [
                    {"id": "a", "score": -0.1, "reasoning": "bad"},
                    valid["scores"][1],
                ]
            },
            expected,
        )
    for invalid in (True, "0.7"):
        with pytest.raises(TypeError, match="JSON number"):
            module._validate_batch_scores(
                {
                    "scores": [
                        {"id": "a", "score": invalid, "reasoning": "bad"},
                        valid["scores"][1],
                    ]
                },
                expected,
            )


def test_config_fingerprint_and_batch_schema_are_stable() -> None:
    module = _module()
    left = module.frozen_config()
    right = module.frozen_config()
    assert left == right
    assert left["config_fingerprint"] == right["config_fingerprint"]
    assert len(left["config_fingerprint"]) == 64
    schema = json.loads(module.BATCH_SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["required"] == ["scores"]
    assert schema["additionalProperties"] is False


def test_manifest_build_is_deterministic_and_complete(tmp_path: Path) -> None:
    module = _module()
    frozen = tmp_path / "frozen.json"
    module._write_json_atomic(frozen, module.frozen_config())
    first = tmp_path / "first"
    second = tmp_path / "second"
    assert module.main(["build", "--config", str(frozen), "--out-dir", str(first)]) == 0
    assert (
        module.main(["build", "--config", str(frozen), "--out-dir", str(second)]) == 0
    )
    for name in (
        "score_requests.json",
        "criterion_manifest.json",
        "batch_manifest.json",
    ):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    requests = json.loads((first / "score_requests.json").read_text())
    criterion = json.loads((first / "criterion_manifest.json").read_text())
    batches = json.loads((first / "batch_manifest.json").read_text())
    assert requests["property_point_count_per_judge"] == 780
    assert requests["criterion_point_count_per_judge"] == 72
    assert requests["judge_count"] == 8
    assert criterion["panel_row_count"] == 72
    assert batches["cli_invocation_count"] == batches["batch_count"] * 3
    assert all(batch["case_count"] <= 16 for batch in batches["batches"])
    assert all(
        batch["rendered_prompt_utf8_bytes"] <= 180_000 for batch in batches["batches"]
    )
    unique = module._unique_requests(requests)
    for batch in batches["batches"]:
        artifact_ids = [
            unique[cell_id]["artifact_id"] for cell_id in batch["score_cell_ids"]
        ]
        assert len(artifact_ids) == len(set(artifact_ids))

    empty_scores = tmp_path / "empty_scores.json"
    module._write_json_atomic(
        empty_scores,
        {
            "schema_version": module.SCORE_SCHEMA_VERSION,
            "metric_version": module.METRIC_VERSION,
            "request_manifest_fingerprint": requests["manifest_fingerprint"],
            "records": [],
        },
    )
    properties_dir = tmp_path / "properties"
    v4 = module._load_v4_runner()
    assert (
        v4.main(
            [
                "compute-properties",
                "--probe-manifest",
                str(module.V4_PROBES_PATH),
                "--requests",
                str(first / "score_requests.json"),
                "--config",
                str(frozen),
                "--scores",
                str(empty_scores),
                "--out-dir",
                str(properties_dir),
                "--bootstrap-iters",
                "10",
                "--seed",
                "0",
                "--no-api",
            ]
        )
        == 0
    )
    properties = json.loads((properties_dir / "properties.json").read_text())
    assert len(properties["judges"]) == 8
    assert properties["hard_gate"]["bridge_allowed"] is False


def test_raw_resume_validation_binds_execution_and_transcripts(tmp_path: Path) -> None:
    module = _module()
    batch = {
        "batch_id": "batch",
        "judge_id": "judge",
        "backend": "codex",
        "model": "gpt-5.6-terra",
        "effort": "low",
        "rendered_prompt_sha256": "prompt",
        "score_cell_ids": ["cell"],
    }
    path = tmp_path / "batch__r0.json"
    stdout = path.with_suffix(".stdout.txt")
    stderr = path.with_suffix(".stderr.txt")
    stdout.write_text("stdout")
    stderr.write_text("stderr")
    payload = {
        "schema_version": module.BATCH_SCHEMA_VERSION,
        "protocol_version": module.PROTOCOL_VERSION,
        "batch_id": "batch",
        "repeat_id": 0,
        "judge_id": "judge",
        "backend": "codex",
        "requested_model": "gpt-5.6-terra",
        "effort": "low",
        "rendered_prompt_sha256": "prompt",
        "provider_api_spend_usd": 0.0,
        "cli_stdout_sha256": module._sha256_file(stdout),
        "cli_stderr_sha256": module._sha256_file(stderr),
        "scores": [{"id": "cell", "score": 0.5, "reasoning": "ok"}],
    }
    module._validate_raw_result(payload, batch, 0, path)
    payload["effort"] = "high"
    with pytest.raises(ValueError, match="effort mismatch"):
        module._validate_raw_result(payload, batch, 0, path)
