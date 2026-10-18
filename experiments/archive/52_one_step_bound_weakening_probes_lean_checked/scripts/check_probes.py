#!/usr/bin/env python3
"""TLDR: Lean-check the seven locked one-step bound weakenings with experiment 42's checker.
Zero judge calls. Run from the cert-judge repo root:

    python3 experiments/52_one_step_bound_weakening_probes_lean_checked/scripts/check_probes.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

E52 = Path(__file__).resolve().parents[1]
REPO = next(q for q in E52.parents if (q / "py_src" / "cert_judge").is_dir())
VB = Path("/Users/brandomiranda/veribench")
REF_DIR = VB / "experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/references/annotation"
LAKE = VB / "veribench_dataset/lean_src"
LAKE_BIN = Path.home() / ".elan/bin/lake"
E42_SCRIPTS = REPO / "experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/scripts"
sys.path[:0] = [str(E42_SCRIPTS), str(REPO / "py_src")]
import semantic_probes as S  # noqa: E402

EDITS = [
    {"task": "33_MyMinimum", "decl": "minimum_prop", "old": "myMinList xs ≤ z", "new": "myMinList xs ≤ (z + 1)"},
    {"task": "18_MyFibonacci", "decl": "fibonacci_increasing_prop", "old": "myFibonacci (n + 1) > myFibonacci n", "new": "myFibonacci (n + 1) ≥ myFibonacci n"},
    {"task": "humaneval_31_is_prime", "decl": "prime_def_prop", "old": "2 ≤ d → d < n → n % d ≠ 0", "new": "2 ≤ d → d + 1 < n → n % d ≠ 0"},
    {"task": "humaneval_3_below_zero", "decl": "monotonicity_prop", "old": "x ≥ 0", "new": "x ≥ 1"},
    {"task": "13_MyUppercase", "decl": "length_preservation_prop", "old": "(myUppercase s).length = s.length", "new": "(myUppercase s).length ≤ s.length"},
    {"task": "1_MyAdd", "decl": "commutativity_prop", "old": "myAdd a b = myAdd b a", "new": "myAdd a b = myAdd b a ∨ a = 0"},
    {"task": "0_bisect_right", "decl": "Post", "old": "lo ≤ idx ∧ idx ≤ hi", "new": "lo ≤ idx ∧ idx ≤ hi + 1"},
]


def main() -> int:
    validator = S.Validator(LAKE, LAKE_BIN, timeout=180)
    rows = []
    for spec in EDITS:
        ref_path = REF_DIR / f"{spec['task']}.lean"
        ref = ref_path.read_text(encoding="utf-8")
        text, err, edited_defs, _th = S.apply_edits(ref, [spec])
        row = {"task": spec["task"], "decl": spec["decl"], "old": spec["old"], "new": spec["new"],
               "valid": False, "reason": err, "reverse": None}
        print(f"START {spec['task']}", flush=True)
        try:
            if text is None:
                rows.append(row)
                print(f"FAIL {spec['task']}: {err}", flush=True)
                continue
            probe = S.Probe("weak", 1, text, "one-step bound relaxation")
            closure = S.closure_of(ref, set(edited_defs))
            S.judge_semantic(probe, validator, ref, edited_defs=set(edited_defs), closure=closure)
            row.update(valid=bool(probe.valid), reason=probe.reason, reverse=probe.reverse,
                       n_checks=len(probe.checks),
                       forward_failed=sum(1 for c in probe.checks if c["kind"] == "forward" and c["status"] != "proved"),
                       sha256=probe.sha256)
            print(f"DONE {spec['task']} valid={probe.valid} reverse={probe.reverse} {probe.reason}", flush=True)
        except Exception as exc:  # one task must not drop the other six
            row.update(valid=False, reason=f"{type(exc).__name__}: {exc}")
            print(f"FAIL {spec['task']}: {row['reason']}", flush=True)
        rows.append(row)
    n_valid = sum(1 for r in rows if r["valid"])
    payload = {"written_utc": datetime.now(timezone.utc).isoformat(), "n_valid": n_valid, "n_declared": len(EDITS),
               "construction": "SUCCESS" if n_valid >= 4 else "STOP", "rows": rows}
    out = E52 / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "probe_validity.json").write_text(json.dumps(payload, indent=1) + "\n")
    print(payload["construction"], n_valid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
