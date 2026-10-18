# Strict weakening inside the deployable prompt family

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/51_strict_weakening_within_fuller_context_heldout_judges/PROTOCOL.md>

**TLDR:** One cached test, locked before the join: on held-out fuller-context judges only, does experiment 42's file-level strict weakening accuracy meet experiment 39's gate against the existing human-agreement criterion? No new judge calls and no new ratings.

## Scientific question (locked)

Among judge configurations whose prompt shows more than the reference's last theorem (the fuller-context prompts), does directional accuracy on weakenings that the file-level audit labels strict predict judge–human agreement on the held-out test judges?

This is the uncertainty that blocks a useful screen. Experiment 39's gold deletion-monotonicity score passes only when legacy prompts and fuller-context prompts are pooled. Experiment 49 found the fuller-context pool Spearman of that score is 0.302, below the 0.45 gate. Experiment 42's primary weakening score mixes probes that leave the file's guarantee unchanged. Experiment 50 tested a magnitude margin as a selector against a fixed rubric and was inconclusive. None of those is this association.

## Decision rule (locked before measurement)

Primary population: experiment 39 test-split configurations whose prompt key is in {D0, H0, H1, H2, R4}. Controls are excluded. A configuration counts only when experiment 42 stores a finite `file_level_strict_only.weakening.value` and experiment 39's `criteria.heldout` status is `COMPUTED`.

Headline statistics, from experiment 39's `analysis_lib`, seed 51, 10,000 draws: Spearman, Pearson and Kendall between that strict-weakening value and `criteria.heldout.spearman`. The 95% interval resamples configurations. The p-value is the one-sided permutation test of a positive association, `(k+1)/(n+1)`.

Gate, inherited from experiment 39, not refit here: Spearman ≥ 0.45 and permutation p-val < 0.05, and at least 8 configurations (that library's minimum). Readings:

- `PASS` — both gate pieces hold.
- `FAIL` — computable, Spearman > 0, and at least one gate piece fails.
- `REVERSED` — computable and Spearman ≤ 0.
- `NOT_COMPUTABLE` — fewer than 8 paired configurations, or Spearman undefined.

What the reading does:

- `PASS` — freeze this strict-weakening value as the candidate screen for fuller-context judges. Do not invent another formula on this cache. A prospective check still needs new judges or the incoming ratings, and this result does not change experiment 39's registered verdict.
- `FAIL` or `REVERSED` — stop mining this cache for a within-family screen. The December path is the fixed human-style rubric plus the ratings already being collected, not another property on these probes.
- `NOT_COMPUTABLE` — report the count and stop. Do not lower the minimum of 8.

Train and validation fuller-context associations are descriptive. They are not the verdict. Pooling all splits is not computed.

## Comparators and sensitivity (locked, not replacements)

On the same primary configurations, also associate these two cached scores with the same criterion: experiment 42's primary weakening accuracy (every Lean-valid weakening, including file-level-redundant ones) and experiment 39's `C_ms_gold`. A comparator with a missing value is dropped only for that comparator and becomes `NOT_COMPUTABLE` below 8 pairs. These rows explain whether the strict subset changed the within-family result. They do not replace the headline.

Sensitivity, reported beside the verdict and not part of the gate: permute the criterion inside each judge-model key and recompute the one-sided p-value (seed 51, 10,000 draws). If that p-value is ≥ 0.05, the claim does not resolve within judge models. A model-cluster bootstrap (resample model keys with replacement, keep every configuration of a drawn model, 10,000 draws, seed 51) supplies a second 95% interval. Its p-value is `n/a`.

## Reproduction gate

Before the new association is written, recompute experiment 39's registered test association of `C_ms_gold` with `criteria.heldout` through `analysis_lib.association` on `units_test.json`. It must match `TEST_RECEIPT.json` within 1e-9 on Spearman, Kendall, Pearson, interval endpoints, permutation p-value and unit count. A mismatch stops the run with no verdict.

## What this is not

No Valkyrie calls, no provider keys, no new ratings, no VeriBench set-N sheets, no manuscript edit. The strict labels are experiment 42's existing file-level audit, not new countermodels. Configurations share models and the criterion reuses the same rated items, so a pass is a cached within-family association, not a prospective test. Prior published results listed above were already known when this question was written; the join of strict-weakening accuracy to the criterion inside the fuller-context test split was not.
