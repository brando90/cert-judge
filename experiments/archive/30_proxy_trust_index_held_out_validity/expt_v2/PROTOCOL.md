# Proxy follow-up protocol

**TLDR:** Test the intended human-agreement × repeat-stability criterion, diagnose aggregation zeros, and quantify what the current panel can support. All analyses use previously observed data and are exploratory; no variant will be selected as a validated replacement for the frozen index.

## Scientific question

Does adding measured repeat stability change the relationship between the Proxy
Trust Index (PTI) and human judgments, and do less brittle aggregations improve
ranking resolution without relying on controls? The outcome is a diagnostic
report, including negative results and non-computability, not a pass/fail claim
of generalization. The experiment-29 frozen protocol stays unchanged.

## Data and scale

Join criterion_manifest.json rows to scores.json on BOTH judge_id and
score_cell_id. Require exactly repeat identifiers 0, 1, 2 for every cell, finite
scores in [0,1], and complete structural-probe coverage. Divide human scores in
[0,5] by 5 once. Preserve strict, lenient, and averaged rubric views separately;
they are not independent raters or train/test partitions. Problem identifier is
gold_file, with all three candidates kept together. The agent0/1/2 labels are
generation slots; generator-model provenance is insufficient for family claims.

## Analyses fixed before this follow-up run

1. Reconstruct every per-artifact property factor using the frozen probe validity
   and canonical ladder formula. Require exact agreement, within 1e-12, with
   both frozen aggregate PTI-v0 and its saved epsilon=0.001 sensitivity.
   Compare the frozen aggregate, floors 1e-6/1e-4/1e-3/1e-2 at the per-artifact
   factor level, and a mean within each property followed by a geometric mean
   over four properties. Show property zero counts and leave-one-problem-out
   aggregate sensitivity. No new floor is selected based on its correlation.
2. For each judge and human view, correlate median repeated score with human
   labels using Pearson, Spearman, Kendall tau-b, and ICC(A,1), the two-way
   random-effects absolute-agreement single-measure intraclass correlation.
   Also report Lin concordance and ICC(C,1), fixed-method consistency. ICC is an
   agreement diagnostic, not an independent confirmation of rank correlation.
   Compute Trust Index 2-prime as sqrt(max(correlation,0)*(1-mean sample SD)),
   with within-candidate sample standard deviation (SD), denominator K-1, on
   [0,1] scores. Preserve signed correlations. Separately report the sensitivity
   using twice population SD, the frozen proxy's different noise convention.
3. Report raw proxy versus both agreement alone and the combined target, for
   primary judges and all judges separately. Include stability-only and each
   property as diagnostic comparators. Do not fit on the purported test panel.
4. Resample gold problems jointly across all judges, preserving the three
   candidates and their full observed repeat vectors. Recompute the criterion
   and proxy together using the SAME problem weights. Stratify problems by
   human-label availability so the shared problem sample is synchronized and
   property-only problems retain their separate stratum. Use 2,000 draws,
   seed 20260911, and percentile 95% intervals; count undefined draws. These
   intervals are conditional on observed labels, calls, and configurations,
   not uncertainty over new raters, model families, or future repeat calls.
   Report pairwise combined-criterion ranking probabilities on the primary
   judges and covariance across their criterion estimates.
5. Compare raw, nonnegative-slope linear calibration, unrestricted linear
   calibration, and training-mean prediction leaving out each primary judge
   family. Retain constant-training folds with an explicit training-mean
   fallback. Show slopes, predictions, mean squared error, and baseline errors.
   Do not attach independent-pair bootstrap intervals to these dependent fitted
   predictions. Two primary families cannot supply train/validation/test sets;
   report that explicitly, and do not count controls as additional families.
6. Run an illustrative simulation of independent bivariate-normal judge-level
   proxy/criterion pairs at population correlations 0/0.3/0.5/0.7 and sample
   sizes 5/8/12/20/32/48, with 2,000 datasets per setting. Report Fisher-interval
   coverage, width and zero-exclusion frequency. Repeat at correlation 0.5 with
   2/4/8/12 independent families, 2/4 prompts per family and intrafamily
   correlation 0.7. These are synthetic sensitivity analyses with idealized
   assumptions, not an empirical power estimate for unseen judges or raters.

## Execution and outputs

Run with the repository's existing Python environment:
`PYTHONPATH=py_src .venv/bin/python experiments/30_proxy_trust_index_held_out_validity/expt_v2/run_diagnostics.py`.
The run reads files only, uses no language model, and needs no credentials or
graphics processor. Target duration is minutes on the local processor. Save
machine-readable results, source hashes, seed and installed library versions,
figures, and a timestamped report under expt_v2/results/. Keep results.md live.
Do not open a new human-label pool for model selection; this run uses only
experiment 29's already exposed 72-candidate labels.

## Interpretation safeguards

Inter-rubric Spearman 0.249 is not a measured single-rater reliability for a
new annotation pool. Label-level reliability is not an automatic correction
for correlations across judge-level criteria. Twelve or twenty configurations
are not guaranteed sufficient; related prompts do not create independent
families. A negative training association may be a negative finding, not a
software defect. A learned negative calibration slope does not validate the
raw index's intended direction.

Method references: [ICC forms](https://pmc.ncbi.nlm.nih.gov/articles/PMC4913118/),
[dependence in cross-validation](https://www.jmlr.org/papers/v5/grandvalet04a.html),
and [small-sample Spearman inference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html).
