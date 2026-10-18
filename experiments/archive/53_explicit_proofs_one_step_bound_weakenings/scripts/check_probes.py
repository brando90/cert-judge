#!/usr/bin/env python3
"""TLDR: Lean-check five one-step weakenings with explicit forward proofs. Zero judge calls.

    python3 experiments/archive/53_explicit_proofs_one_step_bound_weakenings/scripts/check_probes.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

E53 = Path(__file__).resolve().parents[1]
REPO = next(q for q in E53.parents if (q / "py_src" / "cert_judge").is_dir())
VB = Path("/Users/brandomiranda/veribench")
REF_DIR = VB / "experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/references/annotation"
LAKE = VB / "veribench_dataset/lean_src"
LAKE_BIN = Path.home() / ".elan/bin/lake"
sys.path[:0] = [str(REPO / "experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/scripts"), str(REPO / "py_src")]
import semantic_probes as S  # noqa: E402

EDITS = [
    {"task": "18_MyFibonacci", "decl": "fibonacci_increasing_prop",
     "old": "myFibonacci (n + 1) > myFibonacci n", "new": "myFibonacci (n + 1) ≥ myFibonacci n"},
    {"task": "humaneval_31_is_prime", "decl": "prime_def_prop",
     "old": "2 ≤ d → d < n → n % d ≠ 0", "new": "2 ≤ d → d + 1 < n → n % d ≠ 0"},
    {"task": "humaneval_3_below_zero", "decl": "monotonicity_prop",
     "old": "x ≥ 0", "new": "x ≥ 1"},
    {"task": "13_MyUppercase", "decl": "length_preservation_prop",
     "old": "(myUppercase s).length = s.length", "new": "(myUppercase s).length ≤ s.length"},
    {"task": "0_bisect_right", "decl": "Post",
     "old": "lo ≤ idx ∧ idx ≤ hi", "new": "lo ≤ idx ∧ idx ≤ hi + 1"},
]

PROOFS = {
    "18_MyFibonacci": {
        "fibonacci_increasing_prop": """intro n h
unfold fibonacci_increasing_prop_e42o at h
unfold fibonacci_increasing_prop
intro hn
exact Nat.le_of_lt (h hn)""",
        "fibonacci_increasing_thm": """intro h n
unfold fibonacci_increasing_prop_e42o at h
unfold fibonacci_increasing_prop
intro hn
exact Nat.le_of_lt (h n hn)""",
        "correctness_thm": """intro h n hp
unfold Post_prop_e42o at h
unfold Post_prop
unfold fibonacci_increasing_prop_e42o at h
unfold fibonacci_increasing_prop
obtain ⟨a, b, c, d, e⟩ := h n hp
refine ⟨a, b, c, d, ?_⟩
intro hn
exact Nat.le_of_lt (e hn)""",
    },
    "humaneval_31_is_prime": {
        "prime_def_prop": """intro n h
unfold prime_def_prop_e42o at h
unfold prime_def_prop
intro hp
obtain ⟨hn, hall⟩ := h hp
refine ⟨hn, ?_⟩
intro d hd2 hlt
exact hall d hd2 (Nat.lt_of_succ_lt hlt)""",
        "prime_def_thm": """intro h n
unfold prime_def_prop_e42o at h
unfold prime_def_prop
intro hp
obtain ⟨hn, hall⟩ := h n hp
refine ⟨hn, ?_⟩
intro d hd2 hlt
exact hall d hd2 (Nat.lt_of_succ_lt hlt)""",
        "correctness_thm": """intro h n hp
unfold Post_prop_e42o at h
unfold Post_prop
unfold prime_def_prop_e42o at h
unfold prime_def_prop
obtain ⟨a, b, c, d⟩ := h n hp
refine ⟨a, b, c, ?_⟩
intro hp2
obtain ⟨hn, hall⟩ := d hp2
refine ⟨hn, ?_⟩
intro d2 hd2 hlt
exact hall d2 hd2 (Nat.lt_of_succ_lt hlt)""",
    },
    "humaneval_3_below_zero": {
        "monotonicity_prop": """intro ops x h
unfold monotonicity_prop_e42o at h
unfold monotonicity_prop
rintro ⟨hb, hx⟩
apply h
constructor
· exact hb
· omega""",
        "monotonicity_thm": """intro h ops x
unfold monotonicity_prop_e42o at h
unfold monotonicity_prop
rintro ⟨hb, hx⟩
apply h ops x
constructor
· exact hb
· omega""",
        "correctness_thm": """intro h ops hp
unfold Post_prop_e42o at h
unfold Post_prop
unfold monotonicity_prop_e42o at h
unfold monotonicity_prop
obtain ⟨a, b, c, d, e⟩ := h ops hp
refine ⟨a, b, c, ?_, e⟩
intro ops2 x
rintro ⟨hb, hx⟩
apply d ops2 x
constructor
· exact hb
· omega""",
    },
    "13_MyUppercase": {
        "length_preservation_prop": """intro s h
unfold length_preservation_prop_e42o at h
unfold length_preservation_prop
exact Nat.le_of_eq h""",
        "length_preservation_thm": """intro h s
unfold length_preservation_prop_e42o at h
unfold length_preservation_prop
exact Nat.le_of_eq (h s)""",
        "correctness_thm": """intro h s hp
unfold Post_prop_e42o at h
unfold Post_prop
unfold length_preservation_prop_e42o at h
unfold length_preservation_prop
obtain ⟨a, b, c, d, e⟩ := h s hp
refine ⟨a, ?_, c, d, e⟩
exact Nat.le_of_eq b""",
    },
    "0_bisect_right": {
        "Post": """intros
rename_i h
unfold Post_e42o at h
unfold Post
obtain ⟨hlo, hhi, hl, hr⟩ := h
exact ⟨hlo, Nat.le_trans hhi (Nat.le_succ hi), hl, hr⟩""",
        "correctness_thm": """intros
rename_i h
unfold Post_e42o at h
unfold Post
obtain ⟨hlo, hhi, hl, hr⟩ := h
exact ⟨hlo, Nat.le_trans hhi (Nat.le_succ hi), hl, hr⟩""",
    },
}


def main() -> int:
    validator = S.Validator(LAKE, LAKE_BIN, timeout=180)
    rows = []
    for spec in EDITS:
        ref = (REF_DIR / f"{spec['task']}.lean").read_text(encoding="utf-8")
        text, err, edited, _th = S.apply_edits(ref, [spec])
        row = {"task": spec["task"], "decl": spec["decl"], "valid": False, "reason": err, "reverse": None}
        print(f"START {spec['task']}", flush=True)
        try:
            if text is None:
                raise RuntimeError(err)
            closure = S.closure_of(ref, set(edited))
            probe = S.Probe("weak", 1, text, "one-step bound relaxation with an explicit forward proof")
            S.judge_semantic(probe, validator, ref, edited_defs=set(edited), closure=closure, proofs=PROOFS[spec["task"]])
            row.update(valid=bool(probe.valid), reason=probe.reason, reverse=probe.reverse,
                       n_checks=len(probe.checks),
                       forward=[(c["theorem"], c["status"]) for c in probe.checks if c["kind"] == "forward"],
                       sha256=probe.sha256)
            print(f"DONE {spec['task']} valid={probe.valid} reverse={probe.reverse} {probe.reason}", flush=True)
        except Exception as exc:
            row.update(valid=False, reason=f"{type(exc).__name__}: {exc}")
            print(f"FAIL {spec['task']}: {row['reason']}", flush=True)
        rows.append(row)
    n_valid = sum(1 for r in rows if r["valid"])
    payload = {"written_utc": datetime.now(timezone.utc).isoformat(), "n_valid": n_valid, "n_declared": len(EDITS),
               "construction": "SUCCESS" if n_valid >= 4 else "STOP", "rows": rows}
    out = E53 / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "probe_validity.json").write_text(json.dumps(payload, indent=1) + "\n")
    print(payload["construction"], n_valid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
