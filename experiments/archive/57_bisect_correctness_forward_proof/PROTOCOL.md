# Experiment 57 — Bisect correctness forward proof

**TLDR:** Experiment 53 left `0_bisect_right` invalid because its correctness theorem did not unfold the renamed postcondition. This experiment changes only that proof and re-checks the same five one-step weakenings. No judge calls.

## What is frozen from experiment 53

The five edits, the four working proofs, experiment 42's checker, and Lean 4.22.0 stay as they were on 10-18-2026. Experiment 53's 4/5 receipt is not rewritten.

## The new proof

`correctness_thm` for `0_bisect_right` introduces the old postcondition, then the implicit binders oldest-first (`α`, `γ`, the five instances, then `a`, `x`, `lo`, `hi`, `key?`, and the precondition). It applies the old `Post` at `bisect_right_functional` and relaxes `idx ≤ hi` with `Nat.le_trans` and `Nat.le_succ`. The reverse check stays on the default search. Valid means every forward check is proved and the reverse stays unproved.

## Gate

SUCCESS only if all 5 of 5 probes are valid and bisect's reverse is unproved. Otherwise STOP. Judge calls stay 0.
