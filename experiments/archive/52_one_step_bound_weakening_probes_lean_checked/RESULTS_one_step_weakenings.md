# One-step bound weakenings

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/52_one_step_bound_weakening_probes_lean_checked/RESULTS_one_step_weakenings.md>

**TLDR:** The locked construction stops. Zero of seven one-step bound relaxations are valid under experiment 42's checker (forward proved and reverse unproved). Scoring does not start. The incoming human ratings stay on VeriBench experiment 102's frozen fixed rubric.

## Set N

Cert-judge adopts the analysis already locked in VeriBench `experiments/102_rescore_vbv1_paper_fsc_with_validated_judge_rewrite_tmlr_icml` (C4–C8 and addenda C7–C15). Those ratings evaluate the fixed H2 rubric once. This experiment did not open the sheets or the sealed scores.

## Construction

Checker: experiment 42's `judge_semantic`, Lean 4.22.0, VeriBench lake project. Gate written before the run: at least 4 of 7 valid. Result: **0/7, STOP**.

| Task | Elaborates | Reverse | Why it is not valid |
|---|---|---|---|
| 33_MyMinimum | no | unavailable | The existing proof of `minimum_thm` still has type `≤ z`, so `≤ (z + 1)` does not typecheck |
| 1_MyAdd | no | unavailable | The existing proof does not typecheck against the weaker disjunction (`unsolved goals`) |
| 18_MyFibonacci | yes | unproved | Default search did not prove `>` implies `≥` (`aesop` made no progress) |
| humaneval_31_is_prime | yes | unproved | Default search did not prove the smaller divisor range |
| humaneval_3_below_zero | yes | unproved | Default search did not prove the stronger premise weakens the implication |
| 13_MyUppercase | yes | unproved | Default search did not prove equality implies `≤` |
| 0_bisect_right | yes | unproved | Default search did not prove `idx ≤ hi` implies `idx ≤ hi + 1` |

Five files elaborate and their reverse implications are unproved, so the edits are not equivalences. The forward direction, which is true, is not proved by the checker's default tactics. Two files do not elaborate because a finished proof was written for the tighter statement.

## Scoring

The protocol starts judge calls only after at least 4 valid probes. That bar was not met. The $50 cap was not spent. Calls: 0.

Receipt: `results/probe_validity.json`.

**TLDR-end:** [cert-judge: one-step bound weakening probes] Construction stops at 0/7 valid probes, so no judge calls were made, and the human ratings stay on the frozen fixed rubric.
