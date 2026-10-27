#!/usr/bin/env python3
"""TLDR: Re-check the five one-step weakenings after an explicit bisect correctness proof. Zero judge calls.

    python3 experiments/archive/57_bisect_correctness_forward_proof/scripts/check_probes.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

E57 = Path(__file__).resolve().parents[1]
REPO = next(q for q in E57.parents if (q / "py_src" / "cert_judge").is_dir())
E53_SCRIPT = REPO / "experiments/archive/53_explicit_proofs_one_step_bound_weakenings/scripts/check_probes.py"

# The correctness theorem quantifies over implicit type-class binders before the named
# arguments. `rename_i` assigns oldest-first. Applying the old `Post` at the function
# result, then relaxing `idx ≤ hi` to `idx ≤ hi + 1`, is the forward direction.
BISECT_CORRECTNESS = """intro H
intros
rename_i α γ iLE iLT iDec iCoe iInh a x lo hi key? hPre
have hOld : Post_e42o a x lo hi key? (bisect_right_functional a x lo hi key?) := H a x lo hi key? hPre
unfold Post_e42o at hOld
unfold Post
obtain ⟨hlo, hhi, hl, hr⟩ := hOld
exact ⟨hlo, Nat.le_trans hhi (Nat.le_succ hi), hl, hr⟩"""


def _load_e53():
    spec = importlib.util.spec_from_file_location("e53_check_probes", E53_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    e53 = _load_e53()
    proofs = {task: dict(body) for task, body in e53.PROOFS.items()}
    proofs["0_bisect_right"]["correctness_thm"] = BISECT_CORRECTNESS
    validator = e53.S.Validator(e53.LAKE, e53.LAKE_BIN, timeout=180)
    rows = []
    for spec in e53.EDITS:
        ref = (e53.REF_DIR / f"{spec['task']}.lean").read_text(encoding="utf-8")
        text, err, edited, _th = e53.S.apply_edits(ref, [spec])
        row = {"task": spec["task"], "decl": spec["decl"], "valid": False, "reason": err, "reverse": None}
        print(f"START {spec['task']}", flush=True)
        try:
            if text is None:
                raise RuntimeError(err)
            closure = e53.S.closure_of(ref, set(edited))
            probe = e53.S.Probe("weak", 1, text, "one-step bound relaxation; bisect correctness proved by hand")
            e53.S.judge_semantic(
                probe, validator, ref, edited_defs=set(edited), closure=closure, proofs=proofs[spec["task"]]
            )
            row.update(
                valid=bool(probe.valid),
                reason=probe.reason,
                reverse=probe.reverse,
                n_checks=len(probe.checks),
                forward=[(c["theorem"], c["status"]) for c in probe.checks if c["kind"] == "forward"],
                sha256=probe.sha256,
            )
            print(f"DONE {spec['task']} valid={probe.valid} reverse={probe.reverse} {probe.reason}", flush=True)
        except Exception as exc:
            row.update(valid=False, reason=f"{type(exc).__name__}: {exc}")
            print(f"FAIL {spec['task']}: {row['reason']}", flush=True)
        rows.append(row)
    n_valid = sum(1 for r in rows if r["valid"])
    bisect = next(r for r in rows if r["task"] == "0_bisect_right")
    payload = {
        "written_utc": datetime.now(timezone.utc).isoformat(),
        "parent": "experiments/archive/53_explicit_proofs_one_step_bound_weakenings",
        "change": "0_bisect_right correctness_thm uses oldest-first rename_i and applies Post_e42o at the function result",
        "n_valid": n_valid,
        "n_declared": len(e53.EDITS),
        "bisect_valid": bool(bisect["valid"]),
        "construction": "SUCCESS" if n_valid == 5 and bisect["valid"] and bisect["reverse"] == "unproved" else "STOP",
        "judge_calls": 0,
        "rows": rows,
    }
    out = E57 / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "probe_validity.json").write_text(json.dumps(payload, indent=1) + "\n")
    print(payload["construction"], n_valid, file=sys.stderr)
    return 0 if payload["construction"] == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
