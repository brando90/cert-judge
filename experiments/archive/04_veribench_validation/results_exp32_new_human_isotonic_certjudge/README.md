# EXP32 New Human Labels: Isotonic Oracle and CertJudge Train Fit
**TLDR:** This run aggregates the new human-label TSVs, fits an isotonic oracle on the test split, and searches train-side CertJudge weights for high judge-level correlation.

## Data
- Human files used: 7
- Usable labels: 837
- Distinct labeled items: 90
- Items overlapping judge scores: 72
- Train items: 57
- Test items: 15
- Dropped labels: 60

## Test-Set Isotonic Oracle
This intentionally fits the monotone mapping on test labels, so it is an upper-bound diagnostic, not deployment-valid calibration.
- `editdist_e1`: isotonic Spearman=0.696, Pearson=0.929, MAE=0.060 (n=15)
- `gpt-5.3-codex|P1_BASELINE`: isotonic Spearman=0.696, Pearson=0.929, MAE=0.060 (n=15)
- `gpt-5.3-codex|P4_CHECKLIST`: isotonic Spearman=0.696, Pearson=0.929, MAE=0.060 (n=15)
- `labs-leanstral-2603|P1_BASELINE`: isotonic Spearman=0.637, Pearson=0.535, MAE=0.124 (n=15)
- `gpt-4o-mini|P1_BASELINE`: isotonic Spearman=0.603, Pearson=0.725, MAE=0.097 (n=15)

## Train-Optimized CertJudge
- Best train Spearman: 0.283
- Same weights on test Spearman: 0.285
- Best weights: {'ident': 0.07580390202411648, 'mono_rank': 0.261516702628434, 'weak_mono': 0.08985829940442296, 'stability': 0.005512637224518113, 'anti_string': 0.5416448063176496, 'subtle_bug': 0.025663652400858796}

## Outputs
- `new_human_labels_cleaned.csv`
- `new_human_item_targets.csv`
- `test_isotonic_oracle_per_judge.csv`
- `test_isotonic_oracle_predictions.csv`
- `train_certjudge_weight_search.csv`
- `summary.json`
