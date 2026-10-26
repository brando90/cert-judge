"""Deterministic regression tests for the cache-only EFG judge adapter."""

from __future__ import annotations

import importlib

import pytest

efg = importlib.import_module("cert_judge.efg_judge")


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    """Keep every test cache-only and independent of the checkout path."""
    monkeypatch.setattr(efg, "_CACHE_DIR", tmp_path / "efg-cache")


def _cache_key(model: str, reference: str, candidate: str) -> str:
    return f"{model}|{efg._sha256(reference)}|{efg._sha256(candidate)}"


def test_parse_efg_response_extracts_canonical_judgement_and_explanation():
    judgement, explanation = efg.parse_efg_response(
        "Explanation: The theorem preserves addition.\nJudgement: True\n%%%%%%%%%%"
    )

    assert judgement is True
    assert explanation == "The theorem preserves addition."


def test_direct_cache_recomputes_for_requested_weights():
    reference = "def add (x y : Nat) := x + y"
    candidate = "theorem add_ok (x y : Nat) : add x y = x + y := rfl"
    model = "cached-model"
    efg._save_cache(
        "direct",
        {
            _cache_key(model, reference, candidate): {
                "aspect_scores": {"LP": 1.0, "MC": 0.0, "FV": 0.0, "FQ": 0.0},
                "overall_score": 0.99,
            }
        },
    )

    default_result = efg.efg_judge_direct(reference, candidate, model=model, cache_namespace="direct")
    lp_only_result = efg.efg_judge_direct(
        reference, candidate, model=model, cache_namespace="direct", weights={"LP": 1.0}
    )

    assert default_result.overall_score == pytest.approx(efg.DEFAULT_WEIGHTS["LP"])
    assert lp_only_result.overall_score == pytest.approx(1.0)


def test_cache_hit_does_not_construct_a_provider_client(monkeypatch):
    reference = "def f := 1"
    candidate = "theorem f_ok : f = 1 := rfl"
    model = "cached-model"
    efg._save_cache(
        "hit-only",
        {
            _cache_key(model, reference, candidate): {
                "aspect_scores": {"LP": 1.0, "MC": 1.0, "FV": 1.0, "FQ": 1.0},
                "overall_score": 1.0,
            }
        },
    )
    monkeypatch.setattr(efg, "_make_client", lambda _model: pytest.fail("cache hit constructed a client"))

    result = efg.efg_judge_direct(reference, candidate, model=model, cache_namespace="hit-only")

    assert result.overall_score == pytest.approx(1.0)


def test_uncached_direct_mode_uses_each_aspect_and_populates_cache(monkeypatch):
    reference = "def f := 1"
    candidate = "theorem f_ok : f = 1 := rfl"
    responses = iter(
        [
            "Explanation: yes\nJudgement: True",
            "Explanation: no\nJudgement: False",
            "Explanation: yes\nJudgement: True",
            "Explanation: no\nJudgement: False",
        ]
    )
    calls = []
    monkeypatch.setattr(efg, "_make_client", lambda _model: (object(), "mock"))
    monkeypatch.setattr(
        efg,
        "_call_llm",
        lambda _client, _backend, system, _user, _model, _temperature: calls.append(system) or next(responses),
    )
    monkeypatch.setattr(efg.time, "sleep", lambda _seconds: None)

    result = efg.efg_judge_direct(reference, candidate, model="mock-model", cache_namespace="uncached")

    assert result.aspect_scores == {"LP": 1.0, "MC": 0.0, "FV": 1.0, "FQ": 0.0}
    assert result.overall_score == pytest.approx(0.57)
    assert len(calls) == len(efg.ASPECT_DESCRIPTIONS)
    cached = efg._load_cache("uncached")
    assert _cache_key("mock-model", reference, candidate) in cached


def test_weighted_aggregation_is_independent_of_aspect_answer_order():
    ordered = efg.EFGResult(
        mode="direct", model="cached", aspect_scores={"LP": 1.0, "MC": 0.0, "FV": 1.0, "FQ": 0.0}
    )
    reordered = efg.EFGResult(
        mode="direct", model="cached", aspect_scores={"FQ": 0.0, "FV": 1.0, "MC": 0.0, "LP": 1.0}
    )

    assert ordered.compute_overall() == pytest.approx(reordered.compute_overall())
    assert ordered.compute_overall() == pytest.approx(0.57)
