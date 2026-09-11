# Exp23 pass1+pass2 split for calibration/generalization

This folder contains a deterministic split built from **overlapping pass1/pass2 pair rows**.

Protocol:
- Combine pass1 and pass2 by key `(gold_file, candidate_file)`.
- Keep only overlap rows (72 rows total across 24 problems, 3 candidates/problem).
- Split by `gold_file` to avoid leakage across candidates of the same problem.
- Create:
  - `val` = 15 rows (5 problems) for index/weight calibration.
  - `test` = 15 rows (5 problems) for held-out generalization reporting.
  - `holdout` = remaining 42 rows (14 problems), unused in this 15/15 setup.

Files in `splits/`:
- `val_pass1.tsv`, `val_pass2.tsv`, `val_avg.tsv`
- `test_pass1.tsv`, `test_pass2.tsv`, `test_avg.tsv`
- `holdout_pass1.tsv`, `holdout_pass2.tsv`, `holdout_avg.tsv`
- `*_pairs.tsv` key-only files for reproducibility.

Recommended usage:
- Fit cert-index weights/hyperparameters on `val_avg.tsv`.
- Lock them.
- Report final correlation + CI on `test_avg.tsv`.

Metadata including exact `gold_file` membership is in `summary.json`.
