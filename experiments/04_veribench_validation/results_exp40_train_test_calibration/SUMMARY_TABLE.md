# EXP40 Train/Test Calibration Summary

Human target: `mean` | Train tasks: 18 | Test tasks: 8

## Best Held-Out Method Per Model (primary claim)

| Model | Best judge | Method | Train item ρ | **Test item ρ** | Train task ρ | Test task ρ |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| LeanStral-2603 | `labs-leanstral-2603|P4_CHECKLIST` | `split_linear` | 0.247 | 0.294 | 0.316 | 0.232 |
| GPT-4o-mini | `gpt-4o-mini|P8_STRICT_B` | `split_linear` | 0.129 | 0.529 | 0.597 | 0.525 |
| GPT-5.3 Codex | `gpt-5.3-codex|P11_JSON_FIRST` | `raw` | -0.289 | 0.276 | -0.490 | 0.319 |
| Claude Opus 4.7 | `claude-opus-4-7|P4_CHECKLIST` | `rank_within_task` | -0.011 | 0.281 | 0.332 | 0.928 |

## Oracle Upper Bound Per Model (per-task isotonic, same-item)

| Model | Best judge | Train item ρ | **Test item ρ** | Train task ρ | Test task ρ |
| --- | --- | ---: | ---: | ---: | ---: |
| LeanStral-2603 | `labs-leanstral-2603|P8_STRICT_B` | 0.740 | 0.862 **✓** | 0.757 | 0.943 |
| GPT-4o-mini | `gpt-4o-mini|P1_BASELINE` | 0.762 | 0.933 **✓** | 0.850 | 1.000 |
| GPT-5.3 Codex | `gpt-5.3-codex|P1_BASELINE` | 0.369 | 0.563 | 0.370 | 0.551 |
| Claude Opus 4.7 | `claude-opus-4-7|P4_CHECKLIST` | 0.622 | 0.942 **✓** | 0.682 | 1.000 |

## All Methods: Best Judge Per (Model × Method)

| Model | Method | Judge | Train item ρ | Test item ρ | Train task ρ | Test task ρ | Oracle? |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Claude Opus 4.7 | `ensemble_ridge_lto` | `claude-opus-4-7|ENSEMBLE_RIDGE` | 0.024 | 0.259 | 0.051 | 0.429 | No |
| Claude Opus 4.7 | `lto_linear` | `claude-opus-4-7|P8_STRICT_B` | -0.061 | -0.326 | -0.073 | -0.086 | No |
| Claude Opus 4.7 | `per_task_iso_oracle` | `claude-opus-4-7|P4_CHECKLIST` | 0.622 | 0.942 ✓ | 0.682 | 1.000 | Yes |
| Claude Opus 4.7 | `rank_within_task` | `claude-opus-4-7|P4_CHECKLIST` | -0.011 | 0.281 | 0.332 | 0.928 | No |
| Claude Opus 4.7 | `split_linear` | `claude-opus-4-7|P1_BASELINE` | 0.160 | 0.202 | 0.315 | 0.464 | No |
| GPT-4o-mini | `ensemble_ridge_lto` | `gpt-4o-mini|ENSEMBLE_RIDGE` | 0.089 | -0.104 | 0.089 | 0.143 | No |
| GPT-4o-mini | `lto_isotonic` | `gpt-4o-mini|P4_CHECKLIST` | -0.204 | 0.253 | -0.321 | 0.551 | No |
| GPT-4o-mini | `lto_linear` | `gpt-4o-mini|P8_STRICT_B` | -0.320 | 0.153 | 0.348 | 0.257 | No |
| GPT-4o-mini | `per_task_iso_oracle` | `gpt-4o-mini|P1_BASELINE` | 0.762 | 0.933 ✓ | 0.850 | 1.000 | Yes |
| GPT-4o-mini | `rank_within_task` | `gpt-4o-mini|P1_BASELINE` | 0.253 | 0.024 | 0.453 | -0.555 | No |
| GPT-4o-mini | `raw` | `gpt-4o-mini|P4_CHECKLIST` | -0.124 | 0.251 | -0.193 | 0.493 | No |
| GPT-4o-mini | `split_isotonic` | `gpt-4o-mini|P4_CHECKLIST` | -0.130 | 0.302 | -0.213 | 0.441 | No |
| GPT-4o-mini | `split_linear` | `gpt-4o-mini|P8_STRICT_B` | 0.129 | 0.529 | 0.597 | 0.525 | No |
| GPT-5.3 Codex | `ensemble_ridge_lto` | `gpt-5.3-codex|ENSEMBLE_RIDGE` | -0.358 | 0.003 | -0.220 | 0.029 | No |
| GPT-5.3 Codex | `lto_isotonic` | `gpt-5.3-codex|P11_JSON_FIRST` | -0.191 | 0.128 | -0.342 | 0.058 | No |
| GPT-5.3 Codex | `lto_linear` | `gpt-5.3-codex|P7_STRICT_A` | -0.613 | 0.015 | -0.689 | -0.486 | No |
| GPT-5.3 Codex | `rank_within_task` | `gpt-5.3-codex|P1_BASELINE` | 0.179 | 0.272 | 0.592 | 0.883 | No |
| GPT-5.3 Codex | `split_isotonic` | `gpt-5.3-codex|P20_TC_RATER_CARD` | -0.049 | 0.205 | 0.121 | 0.309 | No |
| GPT-5.3 Codex | `split_linear` | `gpt-5.3-codex|P8_STRICT_B` | 0.488 | 0.160 | 0.664 | 0.145 | No |
| LeanStral-2603 | `ensemble_ridge_lto` | `labs-leanstral-2603|ENSEMBLE_RIDGE` | 0.387 | -0.256 | 0.559 | 0.029 | No |
| LeanStral-2603 | `lto_isotonic` | `labs-leanstral-2603|P4_CHECKLIST` | -0.345 | 0.188 | -0.467 | 0.068 | No |
| LeanStral-2603 | `lto_linear` | `labs-leanstral-2603|P4_CHECKLIST` | -0.076 | -0.155 | -0.062 | -0.143 | No |
| LeanStral-2603 | `per_task_iso_oracle` | `labs-leanstral-2603|P8_STRICT_B` | 0.740 | 0.862 ✓ | 0.757 | 0.943 | Yes |
| LeanStral-2603 | `rank_within_task` | `labs-leanstral-2603|P1_BASELINE` | -0.015 | 0.239 | -0.160 | 0.494 | No |
| LeanStral-2603 | `split_linear` | `labs-leanstral-2603|P4_CHECKLIST` | 0.247 | 0.294 | 0.316 | 0.232 | No |

## Qwen Status

Qwen is not included in this table because EXP16-style `detail_rows.csv` with `human_eval_union` rows against the five-participant panel have not been generated for Qwen. See `CALIBRATION_STATUS.md` → Qwen Status for next steps.

## Notes

- Train/test split: 18/8 tasks, seed=42
- `lto_linear` / `lto_isotonic`: leave-one-task-out cross-validation (no data leakage)
- `split_linear` / `split_isotonic`: fit on train tasks, evaluate on held-out test tasks
- `rank_within_task`: unsupervised rank normalization within each task (no human labels used)
- `per_task_iso_oracle`: same-item calibration (upper bound, not held-out)
- `ensemble_ridge_lto`: ridge ensemble over all prompts for the model (LOO-task-out)
- Test set correlations are the primary metric for TMLR paper claims
