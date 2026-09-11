# EXP37: Five-Human Calibration / Aggregation Sweep

**TLDR:** Swept human aggregation + judge calibration methods. Methods reaching **>=0.70** Spearman: **329** rows.

## Methods >= 0.70 (sorted by Spearman)

| Spearman | Level | Calibration | Split | Method | Judge | n |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1.000 | task | none | all | `human_mean_std0.1|claude-opus-4-7` | `P1_BASELINE` | 4 |
| 1.000 | task | linear_oracle | all | `human_mean_std0.1|claude-opus-4-7` | `P1_BASELINE` | 4 |
| 1.000 | task | quantile_oracle | all | `human_mean_std0.1|claude-opus-4-7` | `P1_BASELINE` | 4 |
| 1.000 | task | none | all | `human_mean_std0.1` | `ensemble_top3_cert` | 4 |
| 1.000 | task | linear_oracle | all | `human_mean_std0.1` | `ensemble_top3_cert` | 4 |
| 1.000 | task | linear_oracle | all | `human_mean_std0.1|gpt-5.3-codex` | `P1_BASELINE` | 4 |
| 0.986 | item | per_task_isotonic_oracle | all | `human_mean_std0.1|labs-leanstral-2603` | `P1_BASELINE` | 9 |
| 0.986 | item | per_task_isotonic_oracle | all | `human_mean_std0.1` | `random_r1` | 9 |
| 0.977 | item | per_task_isotonic_oracle | all | `human_mean_std0.1|gpt-5.3-codex` | `P1_BASELINE` | 9 |
| 0.969 | item | per_task_isotonic_oracle | all | `human_mean_std0.15|labs-leanstral-2603` | `P1_BASELINE` | 17 |
| 0.958 | item | per_task_isotonic_oracle | all | `human_mean_std0.1|gpt-5.3-codex` | `P4_CHECKLIST` | 9 |
| 0.954 | item | per_task_isotonic_oracle | all | `human_mean_std0.15|gpt-5.3-codex` | `BAD_STRINGY` | 17 |
| 0.951 | item | per_task_isotonic_oracle | all | `human_weighted_for_gpt-5.3-codex|P20_TC_RATER_CARD` | `random_r1` | 60 |
| 0.949 | task | isotonic_oracle | all | `human_mean_std0.1|claude-opus-4-7` | `P1_BASELINE` | 4 |
| 0.949 | task | linear_oracle | all | `human_mean_std0.1|gpt-5.3-codex` | `P4_CHECKLIST` | 4 |
| 0.949 | task | none | all | `human_mean_std0.1|labs-leanstral-2603` | `P8_STRICT_B` | 4 |
| 0.949 | task | isotonic_oracle | all | `human_mean_std0.1|labs-leanstral-2603` | `P8_STRICT_B` | 4 |
| 0.949 | task | linear_oracle | all | `human_mean_std0.1|labs-leanstral-2603` | `P8_STRICT_B` | 4 |
| 0.949 | task | quantile_oracle | all | `human_mean_std0.1|labs-leanstral-2603` | `P8_STRICT_B` | 4 |
| 0.943 | item | per_task_isotonic_oracle | all | `human_median` | `random_r1` | 60 |
| 0.943 | item | per_task_isotonic_oracle | all | `human_weighted_for_labs-leanstral-2603|P1_BASELINE` | `random_r1` | 60 |
| 0.942 | item | per_task_isotonic_oracle | all | `human_mean_std0.1` | `editdist_e1` | 9 |
| 0.942 | item | per_task_isotonic_oracle | all | `human_mean_std0.1|labs-leanstral-2603` | `P8_STRICT_B` | 9 |
| 0.939 | item | per_task_isotonic_oracle | all | `human_median|gpt-5.3-codex` | `BAD_STRINGY` | 60 |
| 0.936 | item | per_task_isotonic_oracle | all | `human_mean_min4` | `random_r1` | 59 |
| 0.936 | item | per_task_isotonic_oracle | all | `human_drop_extreme_min3` | `random_r1` | 60 |
| 0.936 | item | per_task_isotonic_oracle | all | `human_trim1_min3` | `random_r1` | 60 |
| 0.934 | item | per_task_isotonic_oracle | all | `human_mean` | `random_r1` | 60 |
| 0.932 | item | per_task_isotonic_oracle | all | `human_median` | `editdist_e1` | 60 |
| 0.931 | item | per_task_isotonic_oracle | all | `human_weighted_for_labs-leanstral-2603|P1_BASELINE` | `editdist_e1` | 60 |
| 0.930 | item | per_task_isotonic_oracle | all | `human_mean_std0.15|claude-opus-4-7` | `P1_BASELINE` | 17 |
| 0.929 | item | per_task_isotonic_oracle | all | `human_rank_mean` | `random_r1` | 60 |
| 0.927 | item | per_task_isotonic_oracle | all | `human_weighted_for_labs-leanstral-2603|P1_BASELINE|gpt-5.3-codex` | `BAD_STRINGY` | 60 |
| 0.927 | item | per_task_isotonic_oracle | all | `human_weighted_for_gpt-5.3-codex|P20_TC_RATER_CARD` | `editdist_e1` | 60 |
| 0.925 | item | per_task_isotonic_oracle | all | `human_median` | `ensemble_top3_cert` | 60 |
| 0.925 | item | per_task_isotonic_oracle | all | `human_mean_std0.15` | `ensemble_top3_cert` | 17 |
| 0.925 | item | per_task_isotonic_oracle | all | `human_rank_mean` | `editdist_e1` | 60 |
| 0.924 | item | per_task_isotonic_oracle | all | `human_mean_std0.15` | `editdist_e1` | 17 |
| 0.922 | item | per_task_isotonic_oracle | all | `human_mean` | `editdist_e1` | 60 |
| 0.922 | item | per_task_isotonic_oracle | all | `human_drop_extreme_min3|gpt-5.3-codex` | `BAD_STRINGY` | 60 |

## Best Raw (No Calibration) Item-Level

| Spearman | Method | Judge | n |
| ---: | --- | --- | ---: |
| 0.803 | `human_mean_std0.1|claude-opus-4-7|P1_BASELINE` | | 9 |
| 0.715 | `human_mean_std0.15|labs-leanstral-2603|P1_BASELINE` | | 17 |
| 0.708 | `human_mean_std0.1|labs-leanstral-2603|P1_BASELINE` | | 9 |
| 0.538 | `human_mean_std0.1|ensemble_top3_cert` | | 9 |
| 0.525 | `human_mean_std0.15|gpt-4o-mini|P1_BASELINE` | | 17 |
| 0.503 | `human_mean_std0.15|claude-opus-4-7|P1_BASELINE` | | 17 |
| 0.484 | `human_weighted_for_labs-leanstral-2603|P1_BASELINE|labs-leanstral-2603|P1_BASELINE` | | 60 |
| 0.479 | `human_mean_std0.1|labs-leanstral-2603|P4_CHECKLIST` | | 9 |
| 0.474 | `human_mean_std0.1_taskz|random_r1` | | 9 |
| 0.462 | `human_weighted_for_labs-leanstral-2603|P4_CHECKLIST|labs-leanstral-2603|P1_BASELINE` | | 60 |
| 0.451 | `human_weighted_for_gpt-4o-mini|P1_BASELINE|labs-leanstral-2603|P1_BASELINE` | | 60 |
| 0.448 | `human_weighted_for_gpt-5.3-codex|P14_HUMAN_ALIGN_V2|labs-leanstral-2603|P1_BASELINE` | | 60 |
| 0.435 | `human_rank_mean|labs-leanstral-2603|P1_BASELINE` | | 60 |
| 0.426 | `human_zscore_mean|labs-leanstral-2603|P1_BASELINE` | | 60 |
| 0.422 | `human_mean|labs-leanstral-2603|P1_BASELINE` | | 60 |

## Notes
- `isotonic_oracle` / `per_task_isotonic_oracle` fit on the same items they are evaluated on (upper-bound diagnostics).
- `holdout_items` fits on val split and evaluates on holdout split when available.
- Raw five-rater mean typically stays ~0.4-0.5 item-level; reaching 0.7+ generally requires monotone calibration or per-task fitting.
