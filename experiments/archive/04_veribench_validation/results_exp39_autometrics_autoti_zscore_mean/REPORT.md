# EXP39: AutoMetrics-Inspired AutoTI

**TLDR:** Learns a ridge composition over prompt-level judge scores against the five-human `zscore_mean` target. Same-item AutoTI tests the achievable upper bound; leave-one-task-out tests whether it generalizes to unseen tasks.

- Human target: `zscore_mean`, min raters per item: `1`.
- Best raw single metric: `0.426` item Spearman for `labs-leanstral-2603|P1_BASELINE`.
- Best same-item AutoTI: `0.616` item Spearman for `gpt-5.3-codex`.
- Best leave-one-task-out AutoTI: `0.367` item Spearman for `gpt-4o-mini`.

## Learned AutoTI By Model

| Model | Method | Item rho | Task rho | n items | n tasks | alpha | n features |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-opus-4-7 | autoti_ridge_leave_one_task_out | 0.208 | 0.288 | 60 | 20 | 10.0 | 4 |
| claude-opus-4-7 | autoti_ridge_same_items | 0.420 | 0.610 | 60 | 20 | 10.0 | 4 |
| gpt-4o-mini | autoti_ridge_leave_one_task_out | 0.367 | 0.598 | 60 | 20 | 0.0 | 3 |
| gpt-4o-mini | autoti_ridge_same_items | 0.547 | 0.746 | 60 | 20 | 0.0 | 3 |
| gpt-5.3-codex | autoti_ridge_leave_one_task_out | 0.215 | 0.258 | 60 | 20 | 10.0 | 11 |
| gpt-5.3-codex | autoti_ridge_same_items | 0.616 | 0.751 | 60 | 20 | 10.0 | 11 |
| labs-leanstral-2603 | autoti_ridge_leave_one_task_out | 0.353 | 0.478 | 60 | 20 | 0.0 | 4 |
| labs-leanstral-2603 | autoti_ridge_same_items | 0.477 | 0.670 | 60 | 20 | 0.0 | 4 |

## Best Raw Single Metrics

| Metric | Item rho | Task rho | n items | cert_v2 |
| --- | ---: | ---: | ---: | ---: |
| labs-leanstral-2603|P1_BASELINE | 0.426 | 0.544 | 60 | 0.724 |
| gpt-4o-mini|P1_BASELINE | 0.266 | 0.345 | 60 | 0.745 |
| claude-opus-4-7|P1_BASELINE | 0.203 | 0.324 | 60 | 0.884 |
| labs-leanstral-2603|BAD_STRINGY | 0.025 | 0.079 | 60 | 0.789 |
| labs-leanstral-2603|P8_STRICT_B | -0.018 | -0.034 | 60 | 0.524 |
| gpt-5.3-codex|P20_TC_RATER_CARD | -0.052 | -0.012 | 60 | 0.913 |
| gpt-5.3-codex|P14_HUMAN_ALIGN_V2 | -0.080 | -0.135 | 60 | 0.876 |
| gpt-5.3-codex|P1_BASELINE | -0.118 | -0.221 | 60 | 0.865 |
| gpt-5.3-codex|P7_STRICT_A | -0.125 | -0.123 | 60 | 0.869 |
| gpt-5.3-codex|P13_HUMAN_ALIGN_STRICT | -0.171 | -0.245 | 60 | 0.874 |
| gpt-4o-mini|P4_CHECKLIST | -0.213 | -0.231 | 60 | 0.747 |
| gpt-5.3-codex|P11_JSON_FIRST | -0.219 | -0.333 | 60 | 0.880 |

## Interpretation
- Same-item learned AutoTI is an AutoMetrics-style calibration upper bound, not a held-out validity claim.
- Leave-one-task-out is the safer number for paper claims. If it does not clear 0.7, report the high same-item result as calibration capacity only.
- Compare against EXP38 per-task isotonic: that method can exceed 0.7 for LeanStral, but it also boosts random/edit-distance baselines, so it should be labeled as an oracle diagnostic.
