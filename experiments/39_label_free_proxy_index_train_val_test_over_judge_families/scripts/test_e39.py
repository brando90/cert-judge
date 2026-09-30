#!/usr/bin/env python3
"""TLDR: Offline unit tests for experiment 39 (no Lean, no model calls): probe constructors on a small Lean file,
the legacy prompt renderer/parser, the rank statistics, the components and frozen indices on synthetic scores,
the train-then-val selection rule, and the sealed test unlock. Run: python3 -m pytest scripts/test_e39.py -q"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import pytest

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import analysis_lib as A                                      # noqa: E402
import legacy                                                 # noqa: E402
import probes as P                                            # noqa: E402

LEAN = """import Mathlib

namespace Demo

/-- add two numbers -/
def add (a b : Nat) : Nat := a + b

def mul (a b : Nat) : Nat := a * b

example : add 1 2 = 3 := by decide

/-- commutativity -/
theorem add_comm' (a b : Nat) : add a b = add b a := by
  unfold add
  omega

@[simp]
theorem add_zero' (a : Nat) : add a 0 = a := by
  unfold add
  rfl

theorem mul_one' (a : Nat) : mul a 1 = a := by
  unfold mul
  simp

end Demo
"""


# ------------------------------------------------------------------ probes
def test_theorem_decls_and_statements():
    assert P.theorem_names(LEAN) == ["add_comm'", "add_zero'", "mul_one'"]
    stmts = P.statement_texts(LEAN)
    assert stmts[0].startswith("theorem add_comm' (a b : Nat) : add a b = add b a")
    assert all(":=" not in s for s in stmts)


def test_cut_points():
    assert P.cut_points(1, 4) == [1]
    assert P.cut_points(3, 4) == [1, 2, 3]
    assert P.cut_points(7, 4) == [2, 4, 6, 7]
    assert P.cut_points(23, 4) == [6, 12, 18, 23]
    assert P.cut_points(0, 4) == []


def test_delete_theorems_ladder_removes_from_the_end_with_doc_and_attribute():
    ladder = P.delete_theorems_ladder(LEAN, 4)
    assert [a.level for a in ladder] == [0, 1, 2, 3]
    l1, l2, l3 = ladder[1].code, ladder[2].code, ladder[3].code
    assert "mul_one'" not in l1 and "add_zero'" in l1 and "add_comm'" in l1
    assert "add_zero'" not in l2 and "@[simp]" not in l2, "the attribute line goes with its theorem"
    assert "add_comm'" not in l3 and "/-- commutativity -/" not in l3, "the doc comment goes with its theorem"
    assert "def add" in l3 and "example : add 1 2 = 3" in l3 and "end Demo" in l3
    assert len({a.sha256 for a in ladder}) == 4


def test_delete_theorems_ladder_respects_validator():
    ladder = P.delete_theorems_ladder(LEAN, 4, validate=lambda code: "add_zero'" in code)
    assert [a.level for a in ladder] == [0, 1], "stops at the first level the validator rejects"


def test_strip_proofs_keeps_statements():
    art = P.strip_proofs(LEAN)
    assert art is not None
    assert P.statement_texts(art.code) == P.statement_texts(LEAN)
    assert art.code.count("by sorry") == 3 and "omega" not in art.code and "@[simp]" in art.code
    assert "example : add 1 2 = 3 := by decide" in art.code, "tests are left alone"


def test_reorder_swaps_independent_neighbours_and_keeps_bytes():
    art = P.reorder(LEAN)
    assert art is not None
    assert sorted(P.statement_texts(art.code)) == sorted(P.statement_texts(LEAN))
    names = P.theorem_names(art.code)
    assert names == ["add_comm'", "mul_one'", "add_zero'"]
    assert art.code.index("theorem mul_one'") < art.code.index("@[simp]\ntheorem add_zero'")
    assert len(art.code) == len(LEAN)


def test_reorder_refuses_dependent_pair():
    dep = LEAN.replace("theorem mul_one' (a : Nat) : mul a 1 = a := by\n  unfold mul\n  simp",
                       "theorem mul_one' (a : Nat) : mul a 1 = a := by\n  have := add_zero' a\n  simp [mul]")
    art = P.reorder(dep)
    assert art is not None and P.theorem_names(art.code) == ["add_zero'", "add_comm'", "mul_one'"], "falls back to the earlier pair"


def test_spam_appends_fresh_theorems_once():
    art = P.spam(LEAN)
    assert art is not None and art.code.startswith(LEAN.rstrip("\n")) and art.code.count("e39_extra_fact") == 3
    assert P.spam(art.code) is None


def test_alpha_is_conservative():
    art = P.alpha(LEAN)
    assert art is not None and "ptiAlpha0" in art.code
    assert P.theorem_names(art.code) == P.theorem_names(LEAN)


def test_bug_ladder_mutates_definitions_only():
    ladder = P.bug_ladder(LEAN)
    assert ladder[0].level == 0 and len(ladder) >= 2
    for art in ladder[1:]:
        assert P.statement_texts(art.code) == P.statement_texts(LEAN)


# ------------------------------------------------------------------ legacy prompts
def test_legacy_render_uses_last_theorem_block_and_parses_score():
    system, user = legacy.render("P1_BASELINE", LEAN, "theorem foo : True := trivial")
    assert "REFERENCE IMPLEMENTATION:\ntheorem mul_one'" in user and "GENERATED THEOREM:\ntheorem foo" in user
    assert '{"score": <float 0.0-1.0>' in user
    assert legacy.parse('```json\n{"score": 0.7, "reasoning": "ok"}\n```')[1] == 0.7
    with pytest.raises(ValueError):
        legacy.parse('{"score": 1.5, "reasoning": "x"}')
    with pytest.raises(ValueError):
        legacy.parse('{"score": 0.2} {"score": 0.3}')
    assert legacy.template("BAD_STRINGY").startswith("You are a text similarity grader.")


# ------------------------------------------------------------------ statistics
def test_rank_statistics():
    assert A.spearman([1, 2, 3, 4], [1, 2, 3, 4]) == pytest.approx(1.0)
    assert A.spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    assert A.spearman([1, 1, 1], [1, 2, 3]) is None
    assert A.kendall([1, 2, 3, 4], [1, 2, 4, 3]) == pytest.approx(2 / 3)
    assert A.pearson([1, 2, 3], [2, 4, 6]) == pytest.approx(1.0)
    assert A.geometric_mean([0.5, 0.5]) == pytest.approx(0.5) and A.geometric_mean([0.0, 0.9]) == 0.0


def test_permutation_p_and_bootstrap():
    rng = random.Random(0)
    x = [rng.random() for _ in range(20)]
    y = [v + 0.05 * rng.random() for v in x]
    assert A.permutation_p(x, y, draws=500, seed=1) < 0.01
    ci = A.bootstrap_ci(x, y, draws=300, seed=1)
    assert ci["lo"] is not None and ci["lo"] > 0.7 and ci["valid_draws"] > 0
    z = [rng.random() for _ in range(20)]
    assert A.permutation_p(x, z, draws=500, seed=1) > 0.05


def test_ladder_quality_orientation():
    assert A.ladder_quality([0, 1, 2, 3], [1.0, 0.8, 0.5, 0.1]) == pytest.approx(1.0)
    assert A.ladder_quality([0, 1, 2], [0.2, 0.5, 0.9]) == pytest.approx(0.0)
    assert A.ladder_quality([0, 1, 2], [0.5, 0.5, 0.5]) == 0.0


# ------------------------------------------------------------------ synthetic panel
def synthetic_harvest(config: str, split: str, quality: float, seed: int, items: list[dict], probes: dict) -> dict:
    """A judge whose scores follow the human target with noise 1-quality, and whose probes degrade accordingly."""
    rng = random.Random(seed)
    cells = []

    def add(kind, key, task, item, level, repeats, value):
        for r in range(1, repeats + 1):
            v = min(1.0, max(0.0, value + rng.gauss(0, 0.03 * (1.5 - quality))))
            cells.append({"cell": f"{kind}__{key}__L{level}__r{r}", "kind": kind, "key": key, "task": task, "item": item, "level": level,
                          "repeat": r, "config": config, "status": "measured", "score": v, "score_raw": v})
    crit_value = {}
    for it in items:
        v = quality * it["target_expert"] + (1 - quality) * rng.random()
        crit_value[it["item"]] = v
        add("crit", it["item"], it["task"], it["item"], 0, 3, v)
    for r in probes["ident"]:
        add("ident", r["key"], r["task"], None, 0, 3, 0.7 + 0.3 * quality)
    for r in probes["blank"]:
        add("blank", r["key"], r["task"], None, 0, 1, 0.3 * (1 - quality))
    for kind, base in (("ms_gold", 1.0), ("bm_gold", 1.0)):
        for r in probes[kind]:
            add(kind, r["key"], r["task"], None, r["level"], 3 if kind == "bm_gold" else 1, base - quality * 0.2 * r["level"] + (1 - quality) * rng.random() * 0.5)
    for r in probes["ms_cand"]:
        add("ms_cand", r["key"], r["task"], r["item"], r["level"], 1, crit_value[r["item"]] * (1 - quality * 0.3 * r["level"]))
    for kind in ("alpha", "reorder", "sorry"):
        for r in probes[kind]:
            add(kind, r["key"], r["task"], r["item"], 1, 1, crit_value[r["item"]] + (1 - quality) * rng.uniform(-0.4, 0.4))
    for r in probes["spam"]:
        add("spam", r["key"], r["task"], r["item"], 1, 1, crit_value[r["item"]] + (1 - quality) * 0.4)
    return {"config": config, "family": config.split("|")[0], "split": split, "kind": "llm", "status_counts": {"measured": len(cells)}, "cells": cells}


def make_world(tmp_path: Path, n_tasks: int = 15):
    items, rows = [], []
    for t in range(n_tasks):
        task = f"task{t}"
        split = ("train", "val", "test")[t % 3]
        for a in range(3):
            items.append({"item": f"{task}__agent{a}", "task": task, "split": split, "target_expert": round(((t * 7 + a * 3) % 11) / 10, 2)})
        rows.append({"probe_id": f"ident__{task}__L0", "kind": "ident", "key": task, "task": task, "item": None, "level": 0, "valid": True})
        rows.append({"probe_id": f"blank__{task}__L0", "kind": "blank", "key": task, "task": task, "item": None, "level": 0, "valid": True})
        for level in (1, 2, 3):
            rows.append({"probe_id": f"ms_gold__{task}__L{level}", "kind": "ms_gold", "key": task, "task": task, "item": None, "level": level, "valid": True})
        for level in (1, 2, 3, 4):
            rows.append({"probe_id": f"bm_gold__{task}__L{level}", "kind": "bm_gold", "key": task, "task": task, "item": None, "level": level, "valid": True})
        for a in range(3):
            item = f"{task}__agent{a}"
            rows.append({"probe_id": f"crit__{item}__L0", "kind": "crit", "key": item, "task": task, "item": item, "level": 0, "valid": True})
            rows.append({"probe_id": f"ms_cand__{item}__L1", "kind": "ms_cand", "key": item, "task": task, "item": item, "level": 1, "valid": True})
            for kind in ("alpha", "reorder", "sorry", "spam"):
                rows.append({"probe_id": f"{kind}__{item}__L1", "kind": kind, "key": item, "task": task, "item": item, "level": 1, "valid": True})
    return items, {"rows": rows}


def test_components_and_indices_track_quality(tmp_path):
    items, manifest = make_world(tmp_path)
    probes = A.valid_probes(manifest)
    good = A.Scores(synthetic_harvest("m|good", "train", 0.95, 1, items, probes))
    bad = A.Scores(synthetic_harvest("m|bad", "train", 0.2, 2, items, probes))
    cg, cb = A.components(good, probes), A.components(bad, probes)
    for name in A.COMPONENTS:
        assert cg[name]["value"] is not None and cb[name]["value"] is not None, name
        assert 0.0 <= cg[name]["value"] <= 1.0
    assert cg["ms_gold"]["value"] > cb["ms_gold"]["value"] and cg["alpha"]["value"] > cb["alpha"]["value"] and cg["stab"]["value"] > cb["stab"]["value"]
    crit_g = A.criterion(good, items, ("val", "test"), draws=200)
    crit_b = A.criterion(bad, items, ("val", "test"), draws=200)
    assert crit_g["status"] == "COMPUTED" and crit_g["spearman"] > crit_b["spearman"]
    pti = A.pti_v0_frozen(good, probes)
    assert pti["status"] == "COMPUTED" and 0.0 <= pti["value"] <= 1.0
    raw = A.ti_var_raw(good, probes)
    assert raw and raw["n_ladders"] == 15
    norm = {"V_c": (0.0, max(raw["V_c"], 1e-3)), "V_s": (0.0, max(raw["V_s"], 1e-3))}
    assert 0.0 < A.ti_var(raw, norm) <= 1.0
    for name in A.CANDIDATES:
        if A.CANDIDATES[name][0] != "frozen":
            assert A.candidate_value(name, cg, {}) is not None, name


def test_selection_and_sealed_test_on_synthetic_panel(tmp_path, monkeypatch):
    import e39
    import analyze
    items, manifest = make_world(tmp_path)
    probes = A.valid_probes(manifest)
    results = tmp_path / "results"
    private = tmp_path / "private"
    (results / "harvest").mkdir(parents=True)
    private.mkdir()
    monkeypatch.setattr(e39, "RESULTS", results)
    monkeypatch.setattr(e39, "PRIVATE", private)
    monkeypatch.setattr(e39, "load_items", lambda: items)
    monkeypatch.setattr(analyze, "UNITS_OPEN", results / "units_train_val.json")
    monkeypatch.setattr(analyze, "UNITS_SEALED", private / "units_test_sealed.json")
    monkeypatch.setattr(analyze, "FINALISTS", results / "FINALISTS.json")
    monkeypatch.setattr(analyze, "SELECTION", results / "SELECTION.json")
    monkeypatch.setattr(analyze, "TEST_RECEIPT", results / "TEST_RECEIPT.json")
    (results / "probe_manifest.json").write_text(json.dumps(manifest))
    seed = 0
    for split, models in (("train", ("m1", "m2")), ("val", ("m3", "m4")), ("test", ("m5", "m6"))):
        for model in models:
            for k, quality in enumerate((0.15, 0.35, 0.55, 0.75, 0.95)):
                seed += 1
                h = synthetic_harvest(f"{model}|p{k}", split, quality, seed, items, probes)
                (results / "harvest" / f"{model}__p{k}.json").write_text(json.dumps(h))
    monkeypatch.setattr(A, "bootstrap_ci", lambda *a, **k: {"lo": None, "hi": None, "valid_draws": 0})
    monkeypatch.setattr(A, "permutation_p", lambda x, y, fn=A.spearman, draws=10000, seed=39: 0.001)

    class Args:
        allow_unvalidated = False
        finalists_commit = "deadbeef"
        allow_uncommitted = True
    assert analyze.cmd_units(Args()) == 0
    open_units = json.loads((results / "units_train_val.json").read_text())["units"]
    assert {u["split"] for u in open_units} == {"train", "val"}, "test rows are sealed"
    assert analyze.cmd_select(Args()) == 0
    fin = json.loads((results / "FINALISTS.json").read_text())
    assert fin["selected"] in A.CANDIDATES and len(fin["finalists"]) == 3
    sel = json.loads((results / "SELECTION.json").read_text())
    assert sel["train_ranking"][0]["spearman"] >= sel["train_ranking"][-1]["spearman"]
    assert analyze.cmd_test(Args()) == 0
    rec = json.loads((results / "TEST_RECEIPT.json").read_text())
    assert rec["n_test_units"] == 10 and rec["gate"]["test_spearman"] > 0.5 and rec["gate"]["PASS"]
    assert set(rec["reported"]) >= {"PTI_v0_frozen", "TI_var_trainnorm"}
    assert analyze.cmd_report(Args()) == 0
    assert (results / "RESULTS_proxy_index_train_val_test.md").exists()
    # The unlock refuses when the open units change after selection.
    (results / "units_train_val.json").write_text("{}")
    with pytest.raises(SystemExit):
        analyze.cmd_test(Args())
