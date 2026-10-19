# Experiment 57 — PROTOCOL (LOCKED before the synthetic cases are run)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/57_rating_pool_o1_o2_o3_analysis_synthetic_self_test/PROTOCOL.md>

**TLDR:** Freeze the rating-pool analysis for outputs O1, O2 and O3 and show that it returns the pre-declared reading on four synthetic cases. No human ratings and no model calls.

Written 10-19-2026 13:20 PDT. The cases below are the measurement. Their readings are fixed here, before the script is run.

## Question

When the wave-1 sheets arrive, the analysis must already be frozen. This experiment checks that the script implements the proposal's gates on data whose answer is known by construction.

## Gates, copied from the proposal

- **O1.** PASS only if Spearman ≥ 0.45, one-sided permutation p-val < 0.05, and the configuration-bootstrap lower bound > 0.20. FAIL if the association is computable and any of those three fails. INCONCLUSIVE if more than 14 of 51 units lack a screen or a criterion, or the bootstrap interval is wider than 1.2. Draws 10,000, seed 48. Statistics from experiment 39's `analysis_lib`.
- **O2.** For one judge against one human target: Spearman, MAE, mean bias (judge minus human), both means, ICC(C,1) and ICC(A,1). No accept/reject gate.
- **O3.** τ is the value already frozen in `freeze/FREEZE_10-18-2026.json` (0.901572). The script reads it; it does not recompute it. A unit meets the human gate when its criterion is at least 0.45 and its task-bootstrap lower bound is above 0.20.

## Four cases, readings fixed now

1. Twenty units, screen equal to the criterion, nothing missing. Reading: **PASS**.
2. Twenty units, screen equal to the negative of the criterion. Reading: **FAIL**.
3. Fifty-one declared units, twenty missing, the other thirty-one monotone. Reading: **INCONCLUSIVE**.
4. Thirty items, judge score = human score + 0.2. Spearman 1, MAE 0.2, bias +0.2, and ICC(A,1) below ICC(C,1).

A mismatch is a script failure. The thresholds are not moved.
