#!/usr/bin/env python3
"""TLDR: Offline tests for experiment 42 (parser, probe constructors, check-file scaffolding, edit guards, analysis
metrics, naming); the Lean-backed tests run only when the pinned Lean project is present. Zero model calls.
Run: $PY -m pytest scripts/test_e42.py -q"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import analyze                                                # noqa: E402
import e42                                                    # noqa: E402
import lean_text as L                                         # noqa: E402
import semantic_probes as S                                   # noqa: E402

SAMPLE = '''import Std

namespace Demo

/-- implementation -/
def f (xs : List Nat) : Nat := xs.length

-- a line comment
def Post (xs : List Nat) (r : Nat) : Prop :=
  r ≤ xs.length ∧ r = xs.length

/-- spec theorem -/
@[simp] theorem f_post (xs : List Nat) (h : xs ≠ []) :
    Post xs (f xs) := sorry

theorem f_nil : f [] = 0 := by rfl

/-- expected: 1 -/
example : f [3] = 1 := by decide

theorem f_let (n : Nat) :
    let m := n + 1
    f (List.replicate m 0) = m := sorry

end Demo
'''


def test_decls_and_heads():
    ths = L.theorems(SAMPLE)
    assert [d.name for d in ths] == ["f_post", "f_nil", "f_let"]
    post = ths[0]
    assert L.binder_texts(SAMPLE, post) == ["(xs : List Nat)", "(h : xs ≠ [])"]
    assert L.type_text(SAMPLE, post) == "Post xs (f xs)"
    assert post.namespace == ("Demo",)
    # `let m := ...` inside a type does not end the head
    assert "f (List.replicate m 0) = m" in L.type_text(SAMPLE, ths[2])


def test_split_premises():
    assert L.split_premises("Pre xs → Post xs (f xs)") == (["Pre xs"], "Post xs (f xs)")
    assert L.split_premises("∀ x, P x → Q x") == ([], "∀ x, P x → Q x")
    assert L.split_premises("A ↔ B → C") == ([], "A ↔ B → C")


def test_rename_word_boundaries():
    assert L.rename("Post xs ∧ Post_prop ∧ Demo.Post", {"Post": "Post_e42o"}) == "Post_e42o xs ∧ Post_prop ∧ Demo.Post"


def test_comment_spans_and_fmt_comments():
    kinds = [k for _, _, k in L.comment_spans(SAMPLE)]
    assert kinds.count("doc") == 3 and "line" in kinds
    out = S.fmt_comments(SAMPLE)
    assert "-- a line comment" not in out and "/-- spec theorem -/" in out


def test_vacuity_constructors():
    v1 = S.vac_true(SAMPLE)
    assert "theorem f_post : True := sorry" in v1 and "@[simp]" not in v1.split("theorem f_post")[0].splitlines()[-1]
    assert "theorem f_nil : True := trivial" in v1
    v2 = S.vac_hyp(SAMPLE)
    assert "(h : xs ≠ []) :\n    True := sorry" in v2


def test_overconstraint_constructor():
    made = S.overc(SAMPLE, 1)
    assert made is not None
    code, added = made
    assert added[0]["hypothesis"] in ("(hrange : n < 0)", "(hrange : xs.length < 0)")
    assert added[0]["hypothesis"] in code


def test_check_base_axiomatizes_and_drops_tests():
    base, ax, _ = S.check_base(SAMPLE)
    assert "axiom f (xs : List Nat) : Nat" in base and ax == ["f"]
    assert "example" not in base and "expected: 1" not in base       # orphan docstring removed with its test
    assert "def Post" in base                                         # Prop definitions keep their bodies
    assert "theorem f_nil : f [] = 0 := sorry" in base


def test_apply_edits_guards():
    ok, err, defs, ths = S.apply_edits(SAMPLE, [{"decl": "Post", "old": " ∧ r = xs.length", "new": ""}])
    assert ok is not None and defs == {"Post"} and not err
    bad, err, _, _ = S.apply_edits(SAMPLE, [{"decl": "f", "old": "xs.length", "new": "0"}])
    assert bad is None and "not a theorem or a Prop-valued definition" in err
    bad, err, _, _ = S.apply_edits(SAMPLE, [{"decl": "Post", "old": "xs", "new": "ys"}])
    assert bad is None and "occurs" in err


def test_weak_levels_reject_new_declarations():
    spec = {"levels": [{"level": 1, "edits": [{"decl": "Post", "old": "r = xs.length", "new": "r = xs.length\n\ntheorem extra : True := trivial"}]}]}
    (p, _), = S.weak_levels(SAMPLE, spec)
    assert p.valid is False and "declarations" in p.reason


def test_closure_and_build_checks():
    edited, _, defs, _ = S.apply_edits(SAMPLE, [{"decl": "Post", "old": " ∧ r = xs.length", "new": ""}])
    closure = S.closure_of(SAMPLE, defs)
    assert closure == {"Post"}
    checks, copies, _ = S.build_checks(SAMPLE, edited, tag="t", closure=closure, edited_defs=defs)
    fwd = [c for c in checks if c.kind == "forward"]
    assert {c.theorem for c in fwd} == {"f_post", "Post"}
    assert "Post_e42o xs (f xs)" in [c for c in fwd if c.theorem == "f_post"][0].prop
    assert copies["Post"].startswith("def Post_e42o")


def test_parse_output_maps_errors_to_blocks():
    chk = S.Check("e42chk_x_fwd_0", "forward", "t", "t", "", "True", "trivial", True)
    text = "a\n-- e42chk-begin e42chk_x_fwd_0\ntheorem e42chk_x_fwd_0 : True := by\n  trivial\n-- e42chk-end e42chk_x_fwd_0\n"
    ok = S.parse_output(text, "'Demo.e42chk_x_fwd_0' depends on axioms: [propext]\n", [chk])
    assert ok["e42chk_x_fwd_0"]["status"] == "proved"
    bad = S.parse_output(text, "/tmp/p.lean:4:2: error: unsolved goals\n'Demo.e42chk_x_fwd_0' depends on axioms: [sorryAx]\n", [chk])
    assert bad["e42chk_x_fwd_0"]["status"] == "failed"


def _harvest(scores: dict) -> dict:
    cells = []
    for (kind, task, level), vals in scores.items():
        for r, v in enumerate(vals, 1):
            cells.append({"kind": kind, "task": task, "level": level, "repeat": r, "status": "measured", "score": v})
    return {"config": "m|P", "cells": cells}


def test_screen_metrics_and_rule():
    rows = [{"kind": "ident", "family": "identity", "task": t, "level": 1, "valid": True} for t in ("a", "b")]
    for t in ("a", "b"):
        rows += [{"kind": "vac_true", "family": "vacuity", "task": t, "level": 1, "valid": True},
                 {"kind": "weak", "family": "weakening", "task": t, "level": 1, "valid": True},
                 {"kind": "weak", "family": "weakening", "task": t, "level": 2, "valid": True},
                 {"kind": "overc", "family": "overconstraint", "task": t, "level": 1, "valid": True},
                 {"kind": "fmt_comments", "family": "formatting", "task": t, "level": 1, "valid": True}]
    good = {}
    for t in ("a", "b"):
        good.update({("ident", t, 1): [0.9, 0.9, 0.9], ("vac_true", t, 1): [0.1] * 3, ("weak", t, 1): [0.7] * 3,
                     ("weak", t, 2): [0.5] * 3, ("overc", t, 1): [0.2] * 3, ("fmt_comments", t, 1): [0.9] * 3})
    u = analyze.screen_one(_harvest(good), rows, draws=200)
    assert u["verdict"] == "PASS" and u["metrics"]["weakening_kendall_tau"]["value"] == -1.0
    tie = dict(good)
    tie[("weak", "a", 1)] = [0.9] * 3                                  # a tie with the identity is a miss
    u2 = analyze.screen_one(_harvest(tie), rows, draws=200)
    assert u2["metrics"]["weakening"]["value"] == 0.75 and u2["verdict"] == "FAIL"
    sparse = dict(good)
    sparse[("vac_true", "a", 1)] = [0.1]                              # 1 of 3 repeats -> unscored probe
    sparse[("vac_true", "b", 1)] = [0.1]
    assert analyze.screen_one(_harvest(sparse), rows, draws=200)["verdict"] == "NOT_COMPUTABLE"


def test_naming_and_ports():
    assert e42.benchmark_of("t2_luna") == "certjudge42-t2-luna"
    assert sorted(e42.port_of(k) for k in e42.MODELS) == list(range(9460, 9469))
    assert len([u for u in e42.panel_units() if u["kind"] == "llm"]) == 56


LEAN = e42.LAKE_DIR.is_dir() and e42.LAKE_BIN.is_file()


@pytest.mark.skipif(not LEAN, reason="pinned Lean project not present")
def test_lean_harness_rejects_strengthening_and_equivalence():
    ref = e42.references()["0_bisect_right"]["text"]
    v = S.Validator(e42.LAKE_DIR, e42.LAKE_BIN)
    cases = {"strengthen": ("Pre", "lo ≤ hi ∧ hi ≤ a.size ∧", "lo ≤ hi ∧", False),
             "equivalent": ("Post", "lo ≤ idx ∧ idx ≤ hi ∧", "idx ≥ lo ∧ hi ≥ idx ∧", False),
             "weaken": ("Post", "lo ≤ idx ∧ idx ≤ hi ∧\n", "lo ≤ idx ∧\n", True)}
    for name, (decl, old, new, expect) in cases.items():
        (p, info), = S.weak_levels(ref, {"levels": [{"level": 1, "edits": [{"decl": decl, "old": old, "new": new}]}]})
        S.judge_semantic(p, v, ref, proofs=info["proofs"], closure=info["closure"], edited_defs=info["edited_defs"])
        assert p.valid is expect, (name, p.reason)
