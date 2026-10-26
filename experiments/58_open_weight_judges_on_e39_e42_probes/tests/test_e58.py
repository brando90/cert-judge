"""CPU tests for experiment 58: panel config, harvest writer, budget rule, clustered statistics and an end-to-end synthetic
run (fake raw outputs for all 117 units through harvest_lib and analyze58). No GPU, no model, no network.
Run: python -m pytest experiments/58_open_weight_judges_on_e39_e42_probes/tests -q"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path[:0] = [str(SCRIPTS)]
import e58                                                    # noqa: E402
import harvest_lib as H                                       # noqa: E402

HAVE_PROMPTS = all(e58.prompts_path(x, p).exists() for x in e58.EXPS for p in e58.PROMPT_ORDER)
needs_prompts = pytest.mark.skipif(not HAVE_PROMPTS, reason="rebuilt prompts (private/prompts) not present; run rebuild_prompts.py")


def test_panel_config_is_complete_and_pinned():
    assert len(e58.MODELS) == 13 and len(e58.PROMPT_ORDER) == 9
    for k, m in e58.MODELS.items():
        assert re.fullmatch(r"[0-9a-f]{40}", m["revision"]), k
        assert m["gpus"] in (1, 2) and m["max_model_len"] >= 32768 and m["source"] in ("official", "mirror"), k
        assert m["weights_gb"] < 46 * m["gpus"] * 0.95 or m.get("quantization"), k      # weights fit the L40S budget
        if m["source"] == "mirror":
            assert m["official"], k
    assert e58.MODELS["qwen36_27b"]["bridge_e39_model"] == "qwen36"
    assert len(e58.units()) == 117 and all(u["split"] == "test" for u in e58.units())


def test_cell_seed_is_deterministic_and_distinct():
    import judge_vllm as J
    assert J.cell_seed("a|D0", "c1") == J.cell_seed("a|D0", "c1")
    assert J.cell_seed("a|D0", "c1") != J.cell_seed("a|D0", "c2")


def test_final_text_strips_reasoning():
    assert H.final_text("<think>x</think>\nanswer")[0] == "answer"
    assert H.final_text("<think>never closed")[0] == ""
    assert H.final_text("plain")[1] == "plain"
    hm = "<|channel|>analysis<|message|>t<|end|><|start|>assistant<|channel|>final<|message|>ok<|return|>"
    assert H.final_text(hm, harmony=True) == ("ok", "harmony_final")
    assert H.final_text("<|channel|>analysis<|message|>t", harmony=True)[0] == ""


@needs_prompts
def test_prompts_hash_to_committed_cells():
    for exp, folder in (("e39", e58.E39_DIR), ("e42", e58.E42_DIR)):
        for p in ("D0", "LEX"):
            committed = {c["cell"]: c for c in e58.read_json(folder / f"results/cells/{'gem31h' if exp == 'e39' else 'qwen36'}__{p}.json")["cells"]}
            for r in e58.read_jsonl(e58.prompts_path(exp, p)):
                if r["status"] == "render":
                    assert committed[r["cell"]]["prompt_sha256"] == r["prompt_sha256"]
                    assert e58.prompt_sha(r["system"], r["user"]) == r["prompt_sha256"]


def _fake_parse(prompt_key, text):
    v = (int(hashlib.sha256(text.encode()).hexdigest()[:6], 16) % 11) / 10.0
    return v * e58.e39_modules()[0].PROMPTS[prompt_key]["scale"], v, {"rationale": "synthetic"}


@pytest.fixture(scope="module")
def synthetic_run(tmp_path_factory):
    """Fake raw outputs for every (model, prompt, exp): each rendered cell gets text that hashes to a score; two cells per
    configuration are marked over-context and one has no output, to exercise the unmeasured paths."""
    run = tmp_path_factory.mktemp("run")
    H.parse = _fake_parse
    for exp in e58.EXPS:
        for m in e58.MODEL_ORDER:
            for p in e58.PROMPT_ORDER:
                rows = [r for r in e58.read_jsonl(e58.prompts_path(exp, p)) if r["status"] == "render"]
                raw = []
                for i, r in enumerate(rows):
                    if i == 0:
                        continue                                                    # no driver output -> unmeasured_infra
                    if i in (1, 2):
                        raw.append({"cell": r["cell"], "status": "unmeasured_over_context", "reason": "synthetic"})
                    else:
                        raw.append({"cell": r["cell"], "status": "generated", "text": f"<think>t</think> {m}|{r['cell']}", "finish_reason": "stop",
                                    "n_prompt_tokens": 100, "n_output_tokens": 10, "budget": 1024})
                rp = H.raw_path(run, exp, m, p)
                rp.parent.mkdir(parents=True, exist_ok=True)
                rp.write_text("\n".join(json.dumps(x) for x in raw) + "\n")
                H.harvest_one(run, exp, m, p)
    return run


@needs_prompts
def test_synthetic_harvest_matches_e39_schema(synthetic_run):
    A = e58.analysis_lib()
    h = e58.read_json(H.harvest_path(synthetic_run, "e39", "qwen3_4b", "R4"))
    ref = e58.read_json(e58.E39_DIR / "results/harvest/qwen36__R4.json")
    for k in ("config", "family", "split", "kind", "rubric", "scale", "status_counts", "cells"):
        assert k in h and k in ref
    measured = next(c for c in h["cells"] if c["status"] == "measured")
    needed = {"cell", "kind", "key", "task", "item", "level", "repeat", "config", "status", "score", "score_raw", "prompt_sha256"}
    assert needed <= set(measured) and needed <= set(next(c for c in ref["cells"] if c["status"] == "measured"))
    assert h["status_counts"]["unmeasured_infra"] == 1 and h["status_counts"]["unmeasured_over_context"] == 2
    assert h["charges_usd"] == 0.0 and h["n_cells"] == 521
    sc = A.Scores(h)                                                                 # analysis_lib reads it unchanged
    assert sc.cells and sc.config == "qwen3_4b|R4"


@needs_prompts
def test_synthetic_end_to_end_analysis(synthetic_run, tmp_path):
    import analyze58 as Z
    A = e58.analysis_lib()
    items = Z.load_items()
    assert len(items) == 75
    manifest = e58.read_json(e58.E39_DIR / "results/probe_manifest.json")
    units, meta = Z.build_units(A, synthetic_run, items, manifest, draws=100)
    assert len(units) == 117 and meta["ti_var_norm"]["n_train_units"] == 18
    g = Z.gate_block(A, units, 200)
    assert g["plain"]["n_units"] >= 8 and g["verdict"].startswith("plain")
    assert 8 <= g["model_clustered"]["n_models"] <= 13          # models whose nine units are all computable under the synthetic skips
    res = {"gate": g, "secondary": Z.secondary_block(A, units, 200), "scale_curves": Z.scale_curves(units), "tvd_mi": Z.tvd_block(A, units),
           "e42": Z.e42_block(synthetic_run, A, units, 100), "bridge": Z.bridge_block(A, synthetic_run, units)}
    assert res["e42"]["n_units"] == 117 and set(res["e42"]["verdicts"]) == {"PASS", "FAIL", "NOT_COMPUTABLE"}
    assert "qwen3" in res["scale_curves"] and res["tvd_mi"]["repeat_tvd"]["n_units"] >= 8
    assert res["bridge"]["prompts"]["R4"]["n_shared_measured_cells"] > 100
    Z.write_report(tmp_path / "r.md", res)
    assert "plain" in (tmp_path / "r.md").read_text()


def test_clustered_permutation_detects_perfect_association():
    import analyze58 as Z
    A = e58.analysis_lib()
    units = []
    for mi, m in enumerate(e58.MODEL_ORDER):
        for pi, p in enumerate(e58.PROMPT_ORDER):
            v = mi + 0.01 * pi
            units.append({"model_key": m, "prompt_key": p, "indices": {"C": v}, "criteria": {"heldout": {"spearman": v}}})
    out = Z.clustered_stats(A, units, "C", 500)
    assert out["spearman"] == pytest.approx(1.0) and out["permutation_p"] < 0.01 and out["n_models"] == 13


def test_clustered_permutation_ignores_incomplete_models():
    import analyze58 as Z
    A = e58.analysis_lib()
    units = [{"model_key": "m", "prompt_key": "D0", "indices": {"C": 1.0}, "criteria": {"heldout": {"spearman": 1.0}}}]
    assert Z.clustered_stats(A, units, "C", 10)["n_models"] == 0


def test_selection_hash_guard_names_the_frozen_file():
    import analyze58 as Z
    assert e58.sha_file(e58.E39_DIR / "results/SELECTION.json") == Z.E39_SELECTION_SHA


@needs_prompts
def test_cli_main_writes_analysis_files(synthetic_run, tmp_path, monkeypatch):
    import analyze58 as Z
    monkeypatch.setattr(sys, "argv", ["analyze58.py", "--run", str(synthetic_run), "--out", str(tmp_path), "--draws", "50", "--e42-draws", "50"])
    assert Z.main() == 0
    res = json.loads((tmp_path / "ANALYSIS.json").read_text())
    assert res["n_units"] == 117 and "verdict" in res["gate"] and (tmp_path / "RESULTS_open_weight_judges.md").exists()
