# EXP39: AutoMetrics-Inspired AutoTI

**TLDR:** Learns a ridge composition over prompt-level judge scores against the five-human `mean` target. Same-item AutoTI tests the achievable upper bound; leave-one-task-out tests whether it generalizes to unseen tasks.

- Human target: `mean`, min raters per item: `1`.
- Best raw single metric: `0.422` item Spearman for `labs-leanstral-2603|P1_BASELINE`.
- Best same-item AutoTI: `0.625` item Spearman for `gpt-5.3-codex`.
- Best leave-one-task-out AutoTI: `0.335` item Spearman for `gpt-4o-mini`.

## Learned AutoTI By Model

| Model | Method | Item rho | Task rho | n items | n tasks | alpha | n features |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-opus-4-7 | autoti_ridge_leave_one_task_out | 0.224 | 0.289 | 60 | 20 | 10.0 | 4 |
| claude-opus-4-7 | autoti_ridge_same_items | 0.429 | 0.567 | 60 | 20 | 10.0 | 4 |
| gpt-4o-mini | autoti_ridge_leave_one_task_out | 0.335 | 0.585 | 60 | 20 | 0.0 | 3 |
| gpt-4o-mini | autoti_ridge_same_items | 0.518 | 0.750 | 60 | 20 | 0.0 | 3 |
| gpt-5.3-codex | autoti_ridge_leave_one_task_out | 0.285 | 0.306 | 60 | 20 | 10.0 | 11 |
| gpt-5.3-codex | autoti_ridge_same_items | 0.625 | 0.746 | 60 | 20 | 10.0 | 11 |
| labs-leanstral-2603 | autoti_ridge_leave_one_task_out | 0.322 | 0.494 | 60 | 20 | 1.0 | 4 |
| labs-leanstral-2603 | autoti_ridge_same_items | 0.462 | 0.668 | 60 | 20 | 1.0 | 4 |

## Best Raw Single Metrics

| Metric | Item rho | Task rho | n items | cert_v2 |
| --- | ---: | ---: | ---: | ---: |
| labs-leanstral-2603|P1_BASELINE | 0.422 | 0.541 | 60 | 0.724 |
| gpt-4o-mini|P1_BASELINE | 0.263 | 0.353 | 60 | 0.745 |
| claude-opus-4-7|P1_BASELINE | 0.189 | 0.327 | 60 | 0.884 |
| labs-leanstral-2603|BAD_STRINGY | 0.032 | 0.088 | 60 | 0.789 |
| labs-leanstral-2603|P8_STRICT_B | -0.008 | -0.042 | 60 | 0.524 |
| gpt-5.3-codex|P20_TC_RATER_CARD | -0.045 | -0.012 | 60 | 0.913 |
| gpt-5.3-codex|P14_HUMAN_ALIGN_V2 | -0.080 | -0.139 | 60 | 0.876 |
| gpt-5.3-codex|P1_BASELINE | -0.113 | -0.229 | 60 | 0.865 |
| gpt-5.3-codex|P7_STRICT_A | -0.114 | -0.127 | 60 | 0.869 |
| gpt-5.3-codex|P13_HUMAN_ALIGN_STRICT | -0.173 | -0.252 | 60 | 0.874 |
| gpt-4o-mini|P4_CHECKLIST | -0.174 | -0.224 | 60 | 0.747 |
| gpt-5.3-codex|P11_JSON_FIRST | -0.222 | -0.326 | 60 | 0.880 |

## Interpretation
- Same-item learned AutoTI is an AutoMetrics-style calibration upper bound, not a held-out validity claim.
- Leave-one-task-out is the safer number for paper claims. If it does not clear 0.7, report the high same-item result as calibration capacity only.
- Compare against EXP38 per-task isotonic: that method can exceed 0.7 for LeanStral, but it also boosts random/edit-distance baselines, so it should be labeled as an oracle diagnostic.
