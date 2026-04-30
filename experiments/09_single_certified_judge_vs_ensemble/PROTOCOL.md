# Folder 09 — PROTOCOL

## Goal
Test whether one strong certified judge can outperform ensemble judges on human alignment.

## Hypothesis
A top single certified judge (selected by certification signal, not by human labels) can match or beat common ensemble strategies on human Spearman correlation.

## Inputs (no new LLM calls)
- Folder 06 detail rows:
  - `experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/median/detail_rows.csv`
  - `experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/mean/detail_rows.csv`
- Folder 06 per-judge cert/human summary:
  - `.../full_run/{median,mean}/summary.json`
- Folder 07 property pass/fail:
  - `experiments/07_property_vs_expected_behavior_corr/full_run/{median,mean}/summary.json`

## Selection rule for "single certified judge"
1. Candidate pool: judges with `all_pass_p1_p2_p4 = true` in Folder 07.
2. Choose the judge with highest cert v2 score from Folder 06 summary.
3. Tie-breaker: higher cert v1.

This selection is fixed before looking at ensemble-vs-human results.

## Compared predictors
For each item, build predicted score then evaluate Spearman with human labels (`pass1`, `pass2`, `avg`):

- `single_best_certified`: selected rule above.
- `ens_all_llm_uniform`: mean over all LLM judges (exclude editdist/random).
- `ens_certified_uniform`: mean over certified-pass LLM judges.
- `ens_all_llm_certv2_weighted`: weighted mean over all LLM judges, weights proportional to cert v2.
- `ens_certified_certv2_weighted`: weighted mean over certified-pass LLM judges, weights proportional to cert v2.

## Statistics
- Primary metric: Spearman rho with human labels.
- Uncertainty: bootstrap CI over items (default 10,000).
- Pairwise comparison: bootstrap CI for delta rho = rho(single) - rho(ensemble).
- Optional permutation p for delta sign (default off; can enable with `--perm-iters`).

## Run modes
- Smoke: low bootstrap iterations for quick integrity check.
- Full: report-quality bootstrap/permutation.

## Outputs
Under `experiments/09_single_certified_judge_vs_ensemble/{smoke|full_run/{median,mean}}/`:
- `summary.json`
- `comparison_table.csv`
- `pairwise_delta_table.csv`
- `REPORT_AUTO.md`
