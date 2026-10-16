# Semantic effect margin for cached judge selection

**Doc link:** https://github.com/brando90/cert-judge/tree/codex/cj-e50-semantic-margin/experiments/50_semantic_effect_margin_cached_judge_selection_train_val_test

**Summary:** Test one frozen magnitude-sensitive semantic property against the existing information-inspired properties and fixed human-instruction rubric, using historical VeriBench version 1 caches only.
**Freeze date:** 10-16-2026. Commit this definition before calculating the new property; commit hashed inputs and analysis code before the selection phase. This is an exploratory refinement informed by published historical results, not an independent prospective test.

## Question and decision

Does retaining semantic effect magnitude resolve the old eleven-way training tie and improve expected selected-judge agreement with current human ratings?
The primary estimate is the paired difference in historical-test Spearman agreement between maximum-training-margin selection and the fixed H2 human-instruction-rubric selector.
A positive point estimate is descriptive. A positive lower bound of its 95% paired task-bootstrap interval supports further study within this fixed historical pool, not deployment or a prospective claim. An interval spanning zero is inconclusive; an upper bound at or below zero provides no positive selection evidence. No universal usefulness threshold is invented. Report absolute error and mean bias alongside ranking agreement: large semantic drops can be overreaction.
Do not choose a different formula, threshold, pool, target or split after observing the new results. Correct code defects with dated deviation records while retaining this protocol and original evidence.

## Frozen definition

Use the existing semantic declarations and accepted-cell parser from archived experiment 46: structurally valid probes with existing audit label `strict` for weakening, and valid formatting probes, on tasks with both kinds. The audits are existing judgments, not newly proved countermodels.
For task t and judge j, let b be the median identity score (kind ident, level 1), w_k the median score of weakening k, and f_l the median score of formatting edit l.
Define S_jt = mean_k(b - w_k), F_jt = mean_l(abs(b - f_l)), and M_jt = S_jt - F_jt.
Define semantic_margin_j = the arithmetic mean of M_jt over observed eligible tasks, with equal task weights.
Keep the signed value: no clipping, fitted weights, normalization, threshold optimization, score binning or outcome-dependent transformations. Report S and F separately, baseline headroom, and every observed probe median, accepted repeat count and task margin.
Each median requires at least two accepted unique repeats. Accepted statuses are measured and deterministic, with finite scores in [0,1]. Duplicate cells/repeat identifiers and invalid scores fail closed. A task requires its identity median, all declared formatting medians, and at least ceil(0.8 * declared strict probes) weakening medians. A split property requires at least ceil(0.8 * declared eligible tasks) observed tasks, and at least one declared task. Preserve missing cells and reasons; no imputation or reduced denominators.

## Data and comparators

Inputs are only the original experiment-46 source allowlist, its committed numerical property/selector artifacts for regression comparison, and the new experiment's own code/protocol. Hash all inputs. Do not read VeriBench set N, v6, set-B predictions, private/sealed data, or new human sheets. No inference calls, new raters, reference changes or manuscript edits belong to this experiment.
Use all 56 measured language-model configurations for the property overview. Use the exact existing 12-member `primary_full_context` pool for selection and the exact four-member `same_H2` baseline from experiment 44. H2 is uniform random choice among its four judges, not the deployed score-averaged ensemble.
Preserve original task splits: 10 train / 5 validation / 10 test tasks, with 30 / 15 / 30 candidate files. Semantic eligibility currently yields 5 / 2 / 5 tasks; verify metadata rather than altering membership.
Primary human target is experiment 45's published `current5_mean_0_to_1`; `current3_mean_0_to_1` is the fixed sensitivity. Old participant-one pass1/pass2 outcomes are excluded throughout. Metadata-only projection of experiment 44 items is permitted; old outcome fields are never used.
Comparators are the exact experiment-46 selectors: semantic_auc, repeat_tvd, deletion_tvd, maximum train C_ms_gold, maximum train prior_strict_minus_format, random_primary12, and fixed_H2. Preserve deletion_tvd as unavailable if its frozen two-repeat requirement fails; do not relax it.
Each property selects maximum TRAIN-only value, uniformly across ties within 1e-12. Noncomputable property configurations are ineligible only for that selector. All 12 configurations remain in the common criterion-support calculation. Compute new weights and commit their digest in a separate select phase before the evaluate phase loads human outcome values. Existing historical results have already been seen; this phase separation prevents additional outcome-dependent selection but does not restore independence.

## Analysis

Evaluate validation and test separately against both human targets, requiring ceil(0.9 * declared files) common criterion support across the original 12 judges. Keep unavailable splits unavailable. No pooling validation and test to pass coverage.
Report selected weights, per-judge agreement, and expected utility of choosing a judge (weighted mean of individual-judge metrics, never correlation of weighted scores). Metrics: Spearman, Pearson, Kendall tau-b, mean absolute error, bias (judge minus human; positive means leniency), judge mean and human mean. Report accepted repeat counts and mean within-file sample standard deviation.
Use 10,000 paired task-cluster bootstrap draws with seed 20261008, matching the archived baseline analysis for exact comparison. Keep all files from a sampled task together, including variable task sizes. Compute paired differences of the new margin selector versus EVERY comparator on identical draws. Record finite/undefined draw counts and p-val=n/a; no new significance tests. Intervals condition on fixed selectors, cached scores, the existing judge pool and raters; they omit selector, model-population and new-rater uncertainty.
Secondary: property-versus-test-human-agreement association across the same 12 correlated configurations, reporting Spearman, Pearson and Kendall with task-bootstrap intervals and the small/nonindependent judge-pool caveat.
Prespecified descriptive robustness: (a) leave each eligible training task out and recompute the margin selector under unchanged 80% coverage; (b) leave each test task out and recompute the paired primary point difference; (c) exclude each of the four model/harness identifiers in the primary pool, recompute margin and fixed-H2 selection within the remaining pool, and evaluate on the ORIGINAL full-pool common test rows. Report every omission and unavailable case. These are sensitivities, not additional independent tests or replacements for the primary comparison.

## Verification and execution

Before scientific computation, freeze input hashes and analysis source; execute on Stanford Network Analysis Project (SNAP) in a named persistent session. New judge inference and incremental model-provider charges are zero. Subscription coding is separate from measured judge inference.
Test hand-computed margins, constant scores, reversed semantic responses, formatting changes in both directions, equal task weighting, duplicate rejection, exact coverage boundaries, tie weights, undefined correlations, and selector-metric averaging rather than score ensembling. Include a deliberately exaggerated semantic-response fixture to document that a high margin alone does not prove correctness.
Regression-check all historical comparator weights and numerical results against experiment 46 on its exact shared support and bootstrap seed; explain any mismatch before accepting a result. Do not overwrite archived code or artifacts.
Commit per-probe/per-task/configuration tables, hashes, selector receipt, complete metric/paired-comparison tables, controls, runtime receipt, report, live results ledger and checkpoint. Archive this experiment when complete, preserving protocol and result bytes. No paper-framing change is authorized by this run.
