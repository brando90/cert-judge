# Folder 10 — PROTOCOL

## Goal
Compare how well v1 certification score explains human alignment, and whether ensembles add performance beyond cert score.

## Inputs
- Folder 06 summary (per-judge cert_index v1/v2):
  - `experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/{mean,median}/summary.json`
- Folder 09 method-level human correlations:
  - `experiments/09_single_certified_judge_vs_ensemble/full_run/{mean,median}/summary.json`

## Method table
Rows are methods (single judges + ensemble variants).
Columns include:
- method_id
- method_type (`single` or `ensemble`)
- cert_v1 (for singles: judge cert_index; for ensembles: weighted member average)
- rho_human (item-level Spearman from Folder 09)

## Analyses
1. Correlation across methods: cert_v1 vs rho_human.
2. OLS: rho_human ~ cert_v1.
3. OLS: rho_human ~ cert_v1 + is_ensemble.

## Output
- `summary.json`
- `methods_table.csv`
- `report.md`
