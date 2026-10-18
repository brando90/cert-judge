# Explicit proofs for the five one-step weakenings

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/53_explicit_proofs_one_step_bound_weakenings/PROTOCOL.md>

**TLDR:** The same five edits as experiment 52 that already elaborate, with an explicit Lean proof of each forward implication. A probe is valid when it elaborates, every forward check is proved, and the reverse stays unproved. At least 4 of 5 is success. No judge calls.

## Why this is separate

Experiment 52's default search returned 0 of 7. That result stays. This experiment only replaces the proof text. The edits and the validity rule are the same. `33_MyMinimum` and `1_MyAdd` stay out: their finished proofs do not typecheck against the weaker statement.

## Edits

| Task | Declaration | Change |
|---|---|---|
| 18_MyFibonacci | fibonacci_increasing_prop | `>` becomes `≥` |
| humaneval_31_is_prime | prime_def_prop | `d < n` becomes `d + 1 < n` |
| humaneval_3_below_zero | monotonicity_prop | `x ≥ 0` becomes `x ≥ 1` |
| 13_MyUppercase | length_preservation_prop | length `=` becomes `≤` |
| 0_bisect_right | Post | `idx ≤ hi` becomes `idx ≤ hi + 1` |

The proof texts are in `scripts/check_probes.py`. Reverse checks keep experiment 42's default search, so a proof that also shows equivalence still fails the probe.
