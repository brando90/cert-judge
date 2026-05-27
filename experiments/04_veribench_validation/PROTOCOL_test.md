# Exp23 Held-Out Human-Label Test Protocol
**TLDR:** This protocol freezes the held-out test that uses the fresh independent participant labels in `experiments/human_labels/`. The primary analysis correlates frozen Exp28 `TI_var` judge scores with each judge's human Spearman correlation on the held-out participant aggregate, without tuning on the held-out labels.

This file freezes the protocol for the held-out human-label analysis. It is written to prevent post-hoc retuning of the trust index, label aggregation, or pair matching rule; any deviation observed during execution belongs in `results_exp23_heldout_human_labels/report.md`, not in this file.

## Scientific question (locked)

Does the frozen variance-aware trust index, `TI_var`, predict judge-level agreement with the fresh independent human-label pool?

The operational test is the Spearman correlation, across the eight frozen judge configurations, between:

1. each judge's frozen `TI_var` value from `experiments/04_veribench_validation/results_exp28_varaware_codex_avg/judge_trust_vector.csv`; and
2. that judge's Spearman correlation with held-out human labels aggregated from the top-level `participant*.tsv` files in `experiments/human_labels/`.

The primary result is descriptive, not a pass/fail gate. A positive correlation in the same direction as validation supports held-out generalization; a weak, null, or negative correlation is reported as a methodological caveat rather than retuned.

## Locked parameters

- Human-label files: top-level `experiments/human_labels/participant*.tsv`.
- Excluded label files: `experiments/human_labels/old_prompt/*.tsv`, `expert_harsh_set_data.tsv`, and `lenient_set_data.tsv`.
- Primary human aggregation: raw arithmetic mean over all nonblank participant labels for each `gold_file::candidate_file` pair.
- Sensitivity aggregations: raw median and rater-z-scored mean.
- Frozen judge scores: `experiments/04_veribench_validation/results_exp16_final_robust_r9_median/detail_rows.csv`.
- Frozen trust vector: `experiments/04_veribench_validation/results_exp28_varaware_codex_avg/judge_trust_vector.csv`.
- Primary match rule: exact `gold_file::candidate_file` key match only.
- Sensitivity match rule: optional unique candidate-filename alias for rows whose gold filename changed across dataset versions.
- Primary statistic: Spearman(`TI_var`, held-out human Spearman) across judges.
- P-value: exact two-sided permutation p-value over the eight judge-level human-correlation values.
- No new LLM judge calls are allowed in this protocol.

## Scale verification (no further normalization)

Human labels are already on a 0--5 ordinal rubric. Spearman correlations are invariant to monotone rescaling, so the primary analysis does not divide labels by 5.

Judge `score_mean` values in the Exp16 detail CSV are already normalized to the 0--1 scale used by the validation scripts.

`TI_var` values are already computed in `[0, 1]` by Exp28 and are consumed as frozen inputs.

## Verified data schema

Human TSV columns:

- `gold_file`: gold Lean artifact filename.
- `candidate_file`: candidate Lean artifact filename.
- `human_score_0_5`: participant score on the 0--5 rubric; blank values are skipped.

Frozen judge detail CSV columns:

- `judge_id`: judge configuration identifier.
- `row_type`: primary held-out rows use `human_eval_union`.
- `item_key`: `gold_file::candidate_file` key.
- `score_mean`: frozen judge score mean.
- `repeat_scores`: serialized repeated judge scores, not used by the held-out analysis.

Frozen trust-vector CSV columns:

- `judge_id`: same identifier as the detail CSV.
- `TI_variance_aware`: frozen Exp28 trust index used as the predictor.

## Pre-conditions for run

- Run from `/Users/brandomiranda/cert-judge`.
- Do not load LLM-provider API keys and do not make new LLM calls.
- The analysis script must run without requiring NumPy/SciPy because local arm64 Python environments may contain stale x86 wheels.
- Output directory: `experiments/04_veribench_validation/results_exp23_heldout_human_labels/`.

## Estimated wall-clock

The analysis is CPU-only and should finish in under one minute. Exact permutation p-values over eight judges enumerate `8! = 40320` permutations per aggregation.

## Pass/fail / abort rules

- Abort if no top-level participant TSVs are found.
- Abort if fewer than four judges have finite held-out human correlations.
- Report, rather than silently impute, any labeled pair missing from the frozen judge-score CSV.
- Do not promote the candidate-filename alias sensitivity to the primary result unless a human reviewer verifies that the aliased gold files are semantically identical.
- Do not retune weights, thresholds, judge sets, label aggregation, or pair matching after observing the held-out result.

## Identity / contact crib (verified)

- Reviewer requested by Brando: Ethan Hersch, GitHub `@ehersch`.
- Review request: Ethan should check the exact-match coverage caveat, the candidate-filename alias sensitivity, and whether the paper should quote only the primary exact-match result.
