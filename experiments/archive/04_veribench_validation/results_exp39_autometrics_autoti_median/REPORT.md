# EXP39: AutoMetrics-Inspired AutoTI

**TLDR:** Learns a ridge composition over prompt-level judge scores against the five-human `median` target. Same-item AutoTI tests the achievable upper bound; leave-one-task-out tests whether it generalizes to unseen tasks.

- Human target: `median`, min raters per item: `1`.
- Best raw single metric: `0.315` item Spearman for `labs-leanstral-2603|P1_BASELINE`.
- Best same-item AutoTI: `0.661` item Spearman for `gpt-5.3-codex`.
- Best leave-one-task-out AutoTI: `0.413` item Spearman for `gpt-5.3-codex`.

## Learned AutoTI By Model

| Model | Method | Item rho | Task rho | n items | n tasks | alpha | n features |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-opus-4-7 | autoti_ridge_leave_one_task_out | 0.173 | 0.113 | 60 | 20 | 1.0 | 4 |
| claude-opus-4-7 | autoti_ridge_same_items | 0.433 | 0.565 | 60 | 20 | 1.0 | 4 |
| gpt-4o-mini | autoti_ridge_leave_one_task_out | 0.336 | 0.516 | 60 | 20 | 0.0 | 3 |
| gpt-4o-mini | autoti_ridge_same_items | 0.497 | 0.695 | 60 | 20 | 0.0 | 3 |
| gpt-5.3-codex | autoti_ridge_leave_one_task_out | 0.413 | 0.492 | 60 | 20 | 10.0 | 11 |
| gpt-5.3-codex | autoti_ridge_same_items | 0.661 | 0.725 | 60 | 20 | 10.0 | 11 |
| labs-leanstral-2603 | autoti_ridge_leave_one_task_out | 0.203 | 0.344 | 60 | 20 | 0.1 | 4 |
| labs-leanstral-2603 | autoti_ridge_same_items | 0.396 | 0.681 | 60 | 20 | 0.1 | 4 |

## Best Raw Single Metrics

| Metric | Item rho | Task rho | n items | cert_v2 |
| --- | ---: | ---: | ---: | ---: |
| labs-leanstral-2603|P1_BASELINE | 0.315 | 0.449 | 60 | 0.724 |
| claude-opus-4-7|P1_BASELINE | 0.266 | 0.354 | 60 | 0.884 |
| gpt-4o-mini|P1_BASELINE | 0.209 | 0.262 | 60 | 0.745 |
| labs-leanstral-2603|BAD_STRINGY | 0.101 | 0.158 | 60 | 0.789 |
| labs-leanstral-2603|P8_STRICT_B | 0.030 | -0.047 | 60 | 0.524 |
| gpt-5.3-codex|P20_TC_RATER_CARD | -0.000 | 0.100 | 60 | 0.913 |
| gpt-5.3-codex|P7_STRICT_A | -0.062 | -0.034 | 60 | 0.869 |
| gpt-5.3-codex|P14_HUMAN_ALIGN_V2 | -0.082 | -0.122 | 60 | 0.876 |
| gpt-5.3-codex|P1_BASELINE | -0.134 | -0.218 | 60 | 0.865 |
| claude-opus-4-7|P8_STRICT_B | -0.137 | -0.167 | 60 | 0.930 |
| gpt-5.3-codex|P13_HUMAN_ALIGN_STRICT | -0.137 | -0.196 | 60 | 0.874 |
| claude-opus-4-7|P4_CHECKLIST | -0.161 | -0.202 | 60 | 0.883 |

## Interpretation
- Same-item learned AutoTI is an AutoMetrics-style calibration upper bound, not a held-out validity claim.
- Leave-one-task-out is the safer number for paper claims. If it does not clear 0.7, report the high same-item result as calibration capacity only.
- Compare against EXP38 per-task isotonic: that method can exceed 0.7 for LeanStral, but it also boosts random/edit-distance baselines, so it should be labeled as an oracle diagnostic.
