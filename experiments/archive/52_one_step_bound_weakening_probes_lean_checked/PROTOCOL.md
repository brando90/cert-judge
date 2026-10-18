# One-step bound weakenings, Lean-checked

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/52_one_step_bound_weakening_probes_lean_checked/PROTOCOL.md>

**TLDR:** Two decisions Brando approved on 10-18-2026. Cert-judge does not use the incoming human ratings to pick a new screen. Separately, seven one-step bound relaxations are checked in Lean before any judge call: a probe counts only if the reference implies it and the reverse is not proved.

## Set N

VeriBench `experiments/102_rescore_vbv1_paper_fsc_with_validated_judge_rewrite_tmlr_icml` already froze the fixed human-style rubric (the H2 ensemble) and its analysis before ratings, in protocol sections C4–C8 and addenda C7–C15. Cert-judge adopts that freeze. These ratings evaluate that rubric once. They are not an input to a new label-free screen, and this experiment does not open the sheets, the sealed key, or set-N scores.

## Scientific question (locked)

The held-out fuller-context judges in experiment 51 all scored at or next to 1 on the existing strict weakenings, which drop whole conjuncts. Can a one-step relaxation of a single bound produce a file Lean accepts as strictly weaker?

## Edits (locked before elaboration)

The `+ 1` on the minimum bound is parenthesized. Without parentheses Lean parses `≤ z + 1` as `(≤ z) + 1`, which does not elaborate. The weakening is unchanged.

| Task | Declaration | Old | New |
|---|---|---|---|
| 33_MyMinimum | minimum_prop | `myMinList xs ≤ z` | `myMinList xs ≤ (z + 1)` |
| 18_MyFibonacci | fibonacci_increasing_prop | `myFibonacci (n + 1) > myFibonacci n` | `myFibonacci (n + 1) ≥ myFibonacci n` |
| humaneval_31_is_prime | prime_def_prop | `d < n` | `d + 1 < n` |
| humaneval_3_below_zero | monotonicity_prop | `x ≥ 0` | `x ≥ 1` |
| 13_MyUppercase | length_preservation_prop | `(myUppercase s).length = s.length` | `(myUppercase s).length ≤ s.length` |
| 1_MyAdd | commutativity_prop | `myAdd a b = myAdd b a` | `myAdd a b = myAdd b a ∨ a = 0` |
| 0_bisect_right | Post | `lo ≤ idx ∧ idx ≤ hi` | `lo ≤ idx ∧ idx ≤ hi + 1` |

## Decision rule

A probe is valid when it elaborates, every forward implication from the reference statement is proved, and the reverse implication is not proved. Experiment 42's checker is the checker. Construction succeeds when at least 4 of 7 probes are valid. Fewer than 4 stops the method. No judge call happens in this phase.

Scoring, only if construction succeeds: the four held-out fuller-context configurations `opus55x|D0`, `opus55x|H2`, `qwen36|H1`, and `t2_sonnet5|H2`, three repeats, identity plus the valid probe, through the existing Valkyrie judge route. Cap **$50**, authorized by Brando on 10-18-2026 ("do it all! I approve all") as the per-run cap for this pilot only. A separating result is at least one configuration with directional accuracy below 0.8 and at least one at 1. All four at 1 means these probes are still saturated. The cap is the stop, including retries.
