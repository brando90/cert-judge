# Explicit proofs for five one-step weakenings

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/53_explicit_proofs_one_step_bound_weakenings/RESULTS_explicit_proofs.md>

**TLDR:** Four of five one-step weakenings are Lean-valid once the forward implication is proved by hand. Each reverse implication stays unproved, so the edit is not an equivalence. No judge calls.

## Result

Gate: at least 4 of 5 valid. **4/5, SUCCESS.** Lean 4.22.0, experiment 42's checker, explicit forward proofs, default search on the reverse.

| Task | Change | Valid | Reverse |
|---|---|---|---|
| 18_MyFibonacci | `>` becomes `≥` | yes | unproved |
| humaneval_31_is_prime | `d < n` becomes `d + 1 < n` | yes | unproved |
| humaneval_3_below_zero | `x ≥ 0` becomes `x ≥ 1` | yes | unproved |
| 13_MyUppercase | length `=` becomes `≤` | yes | unproved |
| 0_bisect_right | `idx ≤ hi` becomes `idx ≤ hi + 1` | no | unproved |

Bisect fails because `Post_e42o` is not unfolded at the correctness check. The other four each have three forward checks proved (the property, its theorem, and the correctness theorem).

Experiment 52's default-search result stays 0/7. These four files are a new condition. Judge calls: 0. The $50 cap was not used.

Receipt: `results/probe_validity.json`.

**TLDR-end:** [cert-judge: explicit proofs for one-step weakenings] 4 of 5 probes are valid and strictly weaker, with no judge calls.
