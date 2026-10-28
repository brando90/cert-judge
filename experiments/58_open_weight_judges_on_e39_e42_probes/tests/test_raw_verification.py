"""Corruption controls for raw replay; no generation or private examples needed."""
import copy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import e58
import harvest_lib as H
import verify_raw as V


@pytest.fixture
def case():
    prompt = dict(cell="one", status="render", prompt_sha256="a" * 64)
    raw = dict(cell="one", status="generated", prompt_sha256=prompt["prompt_sha256"],
               text="<think>unfinished", finish_reason="length", n_prompt_tokens=100,
               n_output_tokens=16384, budget=16384,
               seed=int(e58.sha(b"58|qwen3_4b|D0|one")[:8], 16))
    return [raw], [prompt]


def test_incomplete_response_is_preserved_not_fixed(case):
    rows, prompts = case
    V.validate_raw(rows, prompts, "qwen3_4b", "D0")
    cell = H.judge_cell("D0", rows[0], False)
    assert cell["status"] == "incomplete" and "score" not in cell
    assert cell["final_from"] == "unclosed_think"


@pytest.mark.parametrize("field,value,error", [
    ("prompt_sha256", "b" * 64, "raw prompt hash"),
    ("seed", 0, "per-cell seed"),
    ("budget", 1000, "generation budget"),
    ("n_output_tokens", 16385, "output token count"),
    ("n_prompt_tokens", -1, "prompt token count"),
    ("status", "success", "unknown raw status"),
    ("cell", "unknown", "unknown or non-rendered"),
])
def test_raw_corruption_is_rejected(case, field, value, error):
    rows, prompts = case
    rows[0][field] = value
    with pytest.raises(ValueError, match=error):
        V.validate_raw(rows, prompts, "qwen3_4b", "D0")


def test_duplicate_rows_cannot_silently_choose_last_response(case):
    rows, prompts = case
    rows.append(copy.deepcopy(rows[0]))
    rows[-1]["text"] = "a conflicting response"
    with pytest.raises(ValueError, match="duplicate"):
        V.validate_raw(rows, prompts, "qwen3_4b", "D0")


def test_raw_response_for_a_deterministic_cell_is_rejected(case):
    rows, prompts = case
    prompts[0]["status"] = "deterministic"
    with pytest.raises(ValueError, match="non-rendered"):
        V.validate_raw(rows, prompts, "qwen3_4b", "D0")


def test_over_context_obeys_minimum_budget(case):
    rows, prompts = case
    rows[0] = dict(cell="one", status="unmeasured_over_context", n_prompt_tokens=40000, budget=960)
    V.validate_raw(rows, prompts, "qwen3_4b", "D0")
    rows[0].update(n_prompt_tokens=39000, budget=1960)
    with pytest.raises(ValueError, match="incorrect over-context"):
        V.validate_raw(rows, prompts, "qwen3_4b", "D0")


def test_empty_collection_does_not_pass(tmp_path):
    (tmp_path / "MANIFEST.sha256").write_text("")
    with pytest.raises(ValueError, match="no observed harvests"):
        V.verify(tmp_path)


def test_raw_input_requires_manifest_coverage(tmp_path):
    (tmp_path / "MANIFEST.sha256").write_text("")
    (tmp_path / "raw").mkdir()
    (tmp_path / "raw/extra.jsonl").write_text("{}\n")
    with pytest.raises(ValueError, match="not all covered"):
        V.verify(tmp_path)


def test_only_written_timestamp_is_ignored_in_comparison():
    h = dict(written_utc="yesterday", cells=[dict(score=0.1)], engine=dict(tensor_parallel_size=1))
    other = copy.deepcopy(h)
    other["written_utc"] = "today"
    assert V.comparable(h) == V.comparable(other)
    other["cells"][0]["score"] = 0.2
    assert V.comparable(h) != V.comparable(other)
