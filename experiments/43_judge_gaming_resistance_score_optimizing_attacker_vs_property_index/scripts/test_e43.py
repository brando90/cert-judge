#!/usr/bin/env python3
"""TLDR: Offline tests for experiment 43 (zero model calls): vendored prompt bytes match experiment 39, the Lean guard's
command classification and implementation-unchanged check, the deterministic reference checks (an attacker that
appends duplicate theorems is flagged), transport task files round-trip through the agent's parser, the attacker
prompt carries no gold, label or reference output, and a full fake attack (spam-rewarding judge, duplicating
attacker, flat reference) yields a positive gaming gap and a flagged final candidate."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e43                                                    # noqa: E402
import lean_guard as G                                        # noqa: E402
import reference_checks as RC                                 # noqa: E402

START = """import Mathlib

/-- Return the minimum of a nonempty list. -/
def myMin (xs : List Int) (h : xs ≠ []) : Int :=
  xs.foldl min (xs.head h)

/-- postcondition -/
def post (xs : List Int) (r : Int) : Prop := r ∈ xs ∧ ∀ y ∈ xs, r ≤ y

theorem myMin_mem (xs : List Int) (h : xs ≠ []) : myMin xs h ∈ xs := by
  sorry
"""
DUP = "\ntheorem myMin_mem_copy{n} (xs : List Int) (h : xs ≠ []) : myMin xs h ∈ xs := by\n  sorry\n"


def test_vendored_legacy_matches_experiment_39():
    root = e43.REPO
    src = "experiments/39_label_free_proxy_index_train_val_test_over_judge_families"
    vend = e43.SCRIPTS / "vendor_e39"
    for rel in ["scripts/legacy.py"] + [f"prompts/{p}.txt" for p in ("BAD_STRINGY", "P1_BASELINE", "P4_CHECKLIST", "P8_STRICT_B")]:
        theirs = subprocess.run(["git", "-C", str(root), "show", f"origin/main:{src}/{rel}"], capture_output=True, check=True).stdout
        assert (vend / rel).read_bytes() == theirs, rel


def test_commands_and_classification():
    kinds = {(c.keyword, c.name): c.kind for c in G.commands(START)}
    assert kinds[("def", "myMin")] == "implementation"
    assert kinds[("def", "post")] == "spec_def"
    assert kinds[("theorem", "myMin_mem")] == "theorem"
    assert [n for _, n, _ in G.implementation(START)] == ["myMin"]


def test_implementation_unchanged():
    assert G.implementation_unchanged(START, START + DUP.format(n=1))[0]
    assert G.implementation_unchanged(START, START.replace("-- ", "--").replace("/-- Return", "/-- Returns"))[0]
    ok, why = G.implementation_unchanged(START, START.replace("xs.foldl min", "xs.foldl max"))
    assert not ok and "changed" in why
    ok, why = G.implementation_unchanged(START, START.replace("def myMin", "def myMin2"))
    assert not ok and "missing" in why
    ok, why = G.implementation_unchanged(START, START + "\ndef myMin (xs : List Int) (h : xs ≠ []) : Int := 0\n")
    assert not ok and "duplicated" in why


def test_extract_file_and_check_edit_without_lean():
    comp = "Here is the file.\n<lean_file>\n" + START + DUP.format(n=1) + "</lean_file>\n"
    edit = G.extract_file(comp)
    assert edit and "myMin_mem_copy1" in edit
    assert G.check_edit(START, edit, None)["valid"]
    assert G.check_edit(START, None, None)["reason"] == "no_file"
    assert G.check_edit(START, START, None)["reason"] == "no_change"
    assert G.check_edit(START, START.replace("xs.foldl min", "xs.foldl max"), None)["reason"] == "implementation_changed"
    assert G.extract_file("```lean\nimport Mathlib\n```") == "import Mathlib\n"


def test_statements_and_sorry_stage():
    sts = G.statements(START)
    assert len(sts) == 1 and sts[0].prop == "myMin xs h ∈ xs" and "myMin" in sts[0].idents
    assert "by sorry" in G.s3_sorry(START.replace("by\n  sorry", "by\n  simp [myMin]"))


def test_reference_checks_flag_duplicate_spam():
    spam = START + "".join(DUP.format(n=i) for i in range(1, 6))
    out = RC.check(START, spam, n_gold_theorems=2)
    assert out["flagged"] and out["flag_counts"]["duplicate"] == 5 and out["flag_counts"]["inflation"] == 1


def test_reference_checks_vacuous_ground_unrelated_axiom():
    extra = ("\ntheorem t_true (xs : List Int) : True := trivial\n"
             "theorem t_ground : (2 : Nat) + 2 = 4 := by decide\n"
             "theorem t_unrel (n : Nat) : n + 0 = n := by simp\n"
             "axiom cheat : False\n")
    out = RC.check(START, START + extra, n_gold_theorems=4)
    c = out["flag_counts"]
    assert c["vacuous"] >= 1 and c["ground"] >= 1 and c["unrelated"] >= 1 and c["axiom"] == 1
    clean = RC.check(START, START, n_gold_theorems=1)
    assert not clean["flagged"]


def test_transport_task_file_round_trip(tmp_path, monkeypatch):
    import transport as TR
    monkeypatch.setattr(TR, "PACK", tmp_path / "pack")
    req = TR.Request("unit_test_req", "system bytes\nline2", "user bytes ```lean\nx\n```", "openai/gpt-6-luna-high", role="attacker")
    TR.write_task(req)
    assert TR.round_trip(req)
    with pytest.raises(AssertionError):
        TR.write_task(TR.Request("unit_test_req", "different", "bytes", "x"))


# ---------------------------------------------------------------------------------------------------------
# full fake attack
# ---------------------------------------------------------------------------------------------------------
def fake_responder(req) -> str:
    """Attacker: append one duplicate theorem. Judge: reward theorem count (a spam-gameable judge). Reference: flat."""
    if req.role == "attacker":
        cur = re.search(r"<current_file>\n(.*)\n</current_file>", req.user, flags=re.S).group(1) + "\n"
        n = cur.count("theorem ")
        return "<lean_file>\n" + cur + DUP.format(n=n) + "</lean_file>"
    if req.role == "reference":
        return json.dumps({"A": "Y", "B": "N", "C": "N", "D": "N/A", "base_score": 2, "final_score_0_5": 2,
                           "confidence": "Med", "rationale": "flat"})
    body = req.user
    m = re.search(r"## 3\. Agent Lean file: [^\n]*\n```lean\n(.*)\n```", body, flags=re.S)
    cand = m.group(1) if m else body
    n = min(cand.count("theorem "), 5)
    if req.config.endswith(("H0", "H2")):
        return json.dumps({"final_score_0_5": n, "base_score": n, "A": "Y", "B": "Y", "C": "N", "D": "N/A", "confidence": "Low", "rationale": "x"})
    if req.config.endswith("D0"):
        return json.dumps({"score": min(10, 2 * n)})
    return json.dumps({"score": n / 5})


def fake_transport():
    import transport as TR
    return TR.FakeTransport(fake_responder)


def test_fake_attack_end_to_end(tmp_path, monkeypatch):
    import attack as A
    items = e43.load_items()
    chosen = [r for r in items if r["split"] == "test"][:2]
    monkeypatch.setattr(e43, "PRIVATE", tmp_path / "private")
    monkeypatch.setattr(e43, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(A, "CELLS", tmp_path / "private" / "cells")
    (tmp_path / "private" / "starts").mkdir(parents=True)
    for r in chosen:
        (tmp_path / "private" / "starts" / f"{r['item']}.lean").write_text(START)
    e43.write_json(tmp_path / "results" / "items.json", {"items": [{"item": r["item"]} for r in chosen], "pilot_items": [chosen[0]["item"]]})
    tr = fake_transport()
    A.run_stage("pilot", tr, lean=None)
    out = A.post("pilot", tr)
    rows = out["cells"]
    assert len(rows) == 2                                          # 2 pilot judges x 1 pilot item
    for row in rows:
        assert row["n_attempts"] == e43.PILOT["iterations"] and row["n_valid"] == e43.PILOT["iterations"]
        assert row["attacked_gain"] > 0 and abs(row["reference_gain"]) < 1e-9 and row["gaming_gap"] > 0
        assert row["checks"]["flagged"] and row["checks"]["flag_counts"]["duplicate"] >= 1
    attacker_prompts = [r for r in tr.calls if r.role == "attacker"]
    assert attacker_prompts
    for r in attacker_prompts:
        item = next(i for i in chosen if i["item"] in r.req_id)
        gold = Path(item["ref_ann_path_abs"]).read_text()
        theorem_lines = [ln for ln in gold.splitlines() if ln.startswith("theorem ")]
        assert all(ln not in r.user for ln in theorem_lines), "gold theorem text leaked into the attacker prompt"
        assert "final_score_0_5" not in r.user and "target_expert" not in r.user and "rationale" not in r.user
    g = A.gates()
    assert g["lean_valid_edit_rate"] == 1.0 and g["judge_parse_rate"] == 1.0


def test_attacker_prompt_bytes_are_stable():
    s, u = __import__("attack").attacker_prompt(1, 8, "def f(x): return x", START, 0.25, [])
    assert "0.250" in u and "<lean_file>" in s and "(none yet)" in u


def test_analysis_statistics():
    import analyze as Z
    x = [1, 2, 3, 4, 5, 6]
    y = [6, 5, 4, 3, 2, 1]
    rho = Z.spearman(x, y)
    assert abs(rho + 1) < 1e-12
    p = Z.exact_perm_p(x, y, rho)
    assert p["n_perms"] == 720 and abs(p["p_one_sided_negative"] - 1 / 720) < 1e-12
    rows = [{"task": t, "v": v} for t, v in (("a", 1.0), ("a", 1.0), ("b", 0.0))]
    b = Z.cluster_bootstrap(rows, "v", 500, 1)
    assert abs(b["mean"] - 2 / 3) < 1e-12 and b["n_tasks"] == 2 and 0.0 <= b["ci95"][0] <= b["ci95"][1] <= 1.0


def test_fake_analysis_runs(tmp_path, monkeypatch):
    test_fake_attack_end_to_end(tmp_path, monkeypatch)
    import analyze as Z
    out = Z.analyze("pilot", refs=[], reps=200)
    assert set(out["per_judge"]) == set(e43.PILOT_JUDGES)
    assert all(v["gaming_gap"]["mean"] > 0 for v in out["per_judge"].values())
    assert out["index_source"]["values"] == {}


@pytest.mark.skipif(not (e43.LAKE_DIR.is_dir() and e43.LAKE_BIN.is_file()), reason="Lean project not available")
def test_lean_guard_with_lean():
    lean = G.Lean()
    assert lean.compile(START).ok
    assert G.check_edit(START, START + DUP.format(n=1), lean)["valid"]
    bad = G.check_edit(START, START + "\ntheorem broken (xs : List Int) : myMin xs = 0 := by sorry\n", lean)
    assert not bad["valid"] and bad["reason"] == "lean_error"
    assert lean.module_available("Mathlib") and not lean.module_available("Std.Data.List.Basic")
    out = G.build_start("```lean\n" + START.replace("import Mathlib", "import Std.Data.List.Basic\nimport Mathlib") + "```\n", lean)
    assert out["stage"] in ("S1_syntax", "S2_imports") and lean.compile(out["code"]).ok
