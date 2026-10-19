# Experiment 56 — Training-only semantic-margin protocol

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex/cj-e56-training-margin/experiments/56_semantic_margin_training_only_diagnosis_and_revisions/PROTOCOL.md>

**TLDR:** This locked, exploratory protocol uses only projected training rows from historical cached scores and the historical current-five human target. It fixes the original semantic margin, two mechanism-based revisions, extraction boundary, inference-free analysis, and reporting rules before any training score or human-label value is read.

This file freezes the protocol before any numerical input or human outcome is read.
Any deviation observed during execution is recorded in the results report rather than by changing this file.

## Scientific question (locked)

Can the original semantic margin's training-only failure mode be diagnosed from its identity baseline, strict semantic weakening drop, formatting penalty, score repeat variability, missingness, and task concentration; and do either of two fixed revisions have exploratory training utility without a claim of test validity?
The study is exploratory post-result method development, not confirmatory validation and not a basis for choosing a new deployed property.

## Access boundary (locked)

The only mixed source files are the historical item registry, ratings artifact, and semantic-score harvests.
`scripts/train_only_projection.py` first reads each item's identifier, task, and declared split, retains only `split == "train"`, and only then extracts score or human-target fields for retained item/task identifiers.
It writes only training rows, training audit declarations, source hashes, and non-reporting exclusion counts.
The analysis consumes only those projected files; it neither opens nor imports archives containing association, evaluation, robustness, or result summaries.
Validation/test outcomes, incoming ratings, private/sealed data, set N, v6/set B, and old pass1/pass2 targets are excluded.

## Frozen configuration pool and target

The pool is the original 12 LLM configurations whose prompt keys are `D0`, `H0`, `H1`, `H2`, or `R4`; the fixed H2 comparator is its original four H2 configurations and represents a uniform choice over individual judges, never score averaging.
The primary target is `current5_mean_0_to_1`; `current3_mean_0_to_1` is a fixed sensitivity target only.
No weights, thresholds, formulas, targets, or candidates may be searched after outcomes are read.

## Frozen candidate definitions

For a task, let `I` be its accepted identity median, `S` the mean of `I - W` over audit-strict weakening medians `W`, and `F` the mean of `abs(I - Q)` over every declared formatting median `Q`.
Accepted cells have status `measured` or `deterministic`, finite normalized score in `[0, 1]`, and at least two repeats per used median.
A task requires identity, every formatting probe, and at least 80% of declared strict probes; a configuration requires at least 80% observed eligible tasks.

1. `original_S_minus_F = S - F`.
2. `headroom_normalized = (S - F) / I`; `I == 0` is unavailable, with no epsilon, clipping, fitted cutoff, or alternate denominator.
3. `semantic_specificity = S - G`, where `G` is the mean absolute identity change for existing audit-confirmed guarantee-preserving semantic edits, requiring matching within-task strict and preservation families. A preservation control is exactly a valid `weakening` probe whose existing audit label is `redundant`, whose `restated_by` field is nonempty, and whose existing `why` rationale records that unchanged theorem statements retain the dropped overall guarantee; `unclear` probes are excluded. The frozen projection writes the exact selected probe IDs, `restated_by`, and rationale before labels are read.

Components remain separately reported. Ties select every maximum configuration within exact tolerance `1e-12` and use a uniform distribution over those individual configurations.

## Frozen analyses and uncertainty

Report per-configuration Spearman, Pearson, Kendall, mean absolute error, signed bias (judge minus human), judge mean, human mean, repeat standard deviation/counts, with 95% percentile task-bootstrap intervals from 10,000 draws and seed `20261019`.
Compare candidates on identical training common support, with the original 90% configuration support requirement and actual support counts shown.
Describe H2 versus alternatives and leave-one-model/harness-out views without treating 12 correlated configurations as independent human samples.
For each leave-one-training-task-out fold, exclude the held task from all property and normalization computations, select by each frozen property, and evaluate the selected individual judge(s) on the omitted task; ties average loss/metric over judge choices, not scores.
Cross-fitted pooled rank statistics are omitted because selected judges vary by fold; report paired absolute-error differences, fold spread, and task-bootstrap selection uncertainty only when selection is recomputed inside the resample.

## Deterministic checks (locked)

Tests cover split/sentinel exclusion, duplicate cells, missing support, zero baseline, affine scaling, formatting-control behavior, and unavailable preservation controls.
The final checks are experiment tests, `python3 py_src/cert_judge/experiment_layout.py --check`, and `git diff --check`.

## Interpretation limits (locked)

All reported associations and selection comparisons reuse historical training labels and cached judges; favorable results do not establish improvement, correctness, transfer, or fresh test validity.
Candidate 3 uses only the pre-existing audited map; it does not create edits, revise golds, or infer preservation from a score pattern.
