# EXP34 Report: All-Human Task Aggregation
**TLDR:** Aggregates all current human labels by item and task, then correlates cached judge scores with the aggregate human target. The task-level view gives the strongest absolute judge-human agreement, while trust-index meta-correlation remains modest.

## Data
- Human label files used: 7
- Usable human labels: 835
- Distinct labeled items: 90
- Distinct labeled tasks: 30
- Items overlapping cached judge scores: 72
- Tasks overlapping cached judge scores: 24

## Main Result
- Item-level meta-Spearman between `cert_index_v2` and judge-human alignment: `0.263`.
- Task-level meta-Spearman between `cert_index_v2` and judge-human alignment: `0.169`.
- Best task-level judge-human Spearman over the all-rater target: `0.510` for `labs-leanstral-2603|P1_BASELINE`.

## Top Task-Level Judges
| Judge | cert_v2 | Task Spearman | Task Pearson | n tasks | Source |
| --- | ---: | ---: | ---: | ---: | --- |
| labs-leanstral-2603|P1_BASELINE | 0.724 | 0.510 | 0.569 | 24 | experiments/04_veribench_validation/results_exp16_leanstral_r3_median |
| random_r1 | 0.576 | 0.404 | 0.521 | 24 | experiments/04_veribench_validation/results_exp22_expanded_judges_stable/exp16 |
| claude-opus-4-7|P1_BASELINE | 0.884 | 0.396 | 0.466 | 24 | experiments/04_veribench_validation/results_exp16_opus47_r3_median |
| gpt-4o-mini|P1_BASELINE | 0.745 | 0.356 | 0.488 | 24 | experiments/04_veribench_validation/results_exp22_expanded_judges_stable/exp16 |
| gpt-5.3-codex|P20_TC_RATER_CARD | 0.913 | 0.192 | 0.205 | 24 | experiments/04_veribench_validation/results_exp16_tc_card_fast |
| gpt-5.3-codex|P14_HUMAN_ALIGN_V2 | 0.876 | 0.169 | 0.124 | 24 | experiments/04_veribench_validation/results_exp16_codex_p14_only_r5_med |
| labs-leanstral-2603|BAD_STRINGY | 0.789 | 0.139 | 0.152 | 24 | experiments/04_veribench_validation/results_exp16_leanstral_r3_median |
| gpt-5.3-codex|P13_HUMAN_ALIGN_STRICT | 0.874 | 0.067 | 0.050 | 24 | experiments/04_veribench_validation/results_exp16_codex_good_only_r9_med |
| labs-leanstral-2603|P8_STRICT_B | 0.524 | -0.026 | -0.092 | 24 | experiments/04_veribench_validation/results_exp16_leanstral_r3_median |
| claude-opus-4-7|P8_STRICT_B | 0.930 | -0.069 | -0.043 | 24 | experiments/04_veribench_validation/results_exp16_opus47_r3_median |

## Interpretation
- Aggregating all current human raters by task gives the strongest aggregate judge-human agreement in this run, but it remains moderate rather than 0.7+.
- This should be written as task-level agreement with the aggregate human evaluation function; it is smoother than item-level agreement.
- The trust-index-to-human-alignment meta-correlation remains modest, so this supports reporting the strongest task-level judge-human agreement separately from any claim that the trust index alone ranks judges across the panel.
