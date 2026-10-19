# Experiment 56 — Training-only semantic-margin diagnosis

**TLDR:** Exploratory training-only diagnosis of the frozen semantic margin and two pre-specified revisions. It does not test transfer or fresh-rater validity.

## Scope

The intersection scored by every configuration is 25/30 training items, across 10 tasks.
The frozen common-support rule needs 27, so the pooled comparison is BELOW_90_PERCENT.
Per-configuration agreement below uses the items that configuration actually scored.
No validation or test outcomes were opened.
Score intervals are 95% percentile intervals from 10,000 task-cluster bootstrap draws, seed 20261019.
They resample training tasks with their items kept together, and they do not cover judge selection, new raters, or a new task population.
Bias is the mean of judge minus human, so a positive bias means the judge is lenient.
Configuration-level associations have no interval: the 12 configurations share the same tasks.

## Candidate coverage

| Candidate | Computed configurations | Mean property |
|---|---:|---:|
| original_S_minus_F | 12/12 | 0.378 |
| headroom_normalized | 12/12 | 0.378 |
| semantic_specificity | 11/12 | 0.274 |
| semantic_auc | 12/12 | 0.994 |
| repeat_tvd | 12/12 | 0.201 |
| C_ms_gold | 0/12 | unavailable |

## Why a high margin need not mean better agreement

Formatting penalties were exactly zero on 59 of 59 observed task values.
The largest task's share of the absolute per-task margin has median 0.246 and maximum 0.304 across configurations with an observed margin.

| Property or component | n configs | Spearman vs training agreement | Pearson | Kendall | Spearman vs training MAE |
|---|---:|---:|---:|---:|---:|
| original_S_minus_F | 12 | -0.378 | -0.219 | -0.303 | 0.587 |
| headroom_normalized | 12 | -0.378 | -0.219 | -0.303 | 0.587 |
| semantic_specificity | 11 | -0.228 | -0.125 | -0.183 | 0.483 |
| semantic_auc | 12 | -0.393 | -0.337 | -0.334 | 0.393 |
| repeat_tvd | 12 | 0.210 | 0.090 | 0.121 | 0.035 |
| C_ms_gold | 0 | unavailable | unavailable | unavailable | unavailable |
| identity_baseline | 12 | unavailable | unavailable | unavailable | unavailable |
| semantic_drop | 12 | -0.378 | -0.219 | -0.303 | 0.587 |
| formatting_penalty | 12 | unavailable | unavailable | unavailable | unavailable |
| preserving_penalty | 12 | 0.307 | 0.202 | 0.193 | -0.530 |

These associations are descriptive.
p-val=n/a, and no configuration-level interval is reported, because the configurations are correlated.

### Reading

The identity baseline is 1.000 on every configuration's observed tasks, so dividing the margin by it does not change the value.
Headroom-normalized margin equals the original margin on all 12 configurations.
Semantic-over-format AUC is saturated: 11 of 12 configurations are exactly 1, because a zero formatting change loses to any positive semantic drop.
The original margin's Spearman with training agreement is -0.378 across 12 correlated configurations (Pearson -0.219, Kendall -0.303; p-val=n/a).
Specificity does not reverse that direction, and it is computable on only 3 training tasks.
The two frozen revisions therefore do not provide a training-supported replacement.

## Per-configuration current-five training agreement

| Configuration | n items | Margin | Headroom | Specificity | Spearman (95% task bootstrap) | Pearson | Kendall | MAE | Bias | Judge mean | Human mean | Repeat SD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| opus55x|D0 | 30 | 0.440 | 0.440 | 0.333 | 0.544 [-0.022, 0.861] p-val=n/a | 0.539 | 0.431 | 0.250 | -0.159 | 0.450 | 0.609 | 0.036 |
| opus55x|H0 | 30 | 0.400 | 0.400 | 0.400 | 0.625 [0.059, 0.902] p-val=n/a | 0.708 | 0.496 | 0.174 | -0.042 | 0.567 | 0.609 | 0.038 |
| opus55x|H2 | 30 | 0.380 | 0.380 | 0.367 | 0.767 [0.415, 0.923] p-val=n/a | 0.831 | 0.657 | 0.148 | 0.031 | 0.640 | 0.609 | 0.004 |
| qwen36|D0 | 30 | 0.457 | 0.457 | 0.367 | 0.742 [0.378, 0.928] p-val=n/a | 0.783 | 0.610 | 0.211 | -0.167 | 0.442 | 0.609 | 0.153 |
| qwen36|H0 | 30 | 0.407 | 0.407 | 0.233 | 0.733 [0.318, 0.900] p-val=n/a | 0.749 | 0.612 | 0.122 | -0.019 | 0.590 | 0.609 | 0.091 |
| qwen36|H1 | 28 | 0.253 | 0.253 | 0.067 | 0.791 [0.477, 0.942] p-val=n/a | 0.805 | 0.680 | 0.126 | 0.024 | 0.632 | 0.609 | 0.117 |
| qwen36|H2 | 29 | 0.329 | 0.329 | unavailable | 0.808 [0.570, 0.944] p-val=n/a | 0.818 | 0.704 | 0.129 | -0.031 | 0.576 | 0.607 | 0.086 |
| qwen36|R4 | 29 | 0.360 | 0.360 | 0.100 | 0.660 [0.103, 0.914] p-val=n/a | 0.734 | 0.556 | 0.142 | 0.078 | 0.686 | 0.608 | 0.109 |
| t2_qwen|D0 | 30 | 0.437 | 0.437 | 0.450 | 0.657 [0.144, 0.895] p-val=n/a | 0.767 | 0.523 | 0.187 | -0.102 | 0.507 | 0.609 | 0.086 |
| t2_qwen|H2 | 29 | 0.267 | 0.267 | 0.067 | 0.518 [0.006, 0.864] p-val=n/a | 0.643 | 0.420 | 0.192 | -0.039 | 0.559 | 0.597 | 0.057 |
| t2_sonnet5|D0 | 30 | 0.487 | 0.487 | 0.500 | 0.628 [0.013, 0.907] p-val=n/a | 0.654 | 0.482 | 0.224 | -0.096 | 0.513 | 0.609 | 0.056 |
| t2_sonnet5|H2 | 30 | 0.320 | 0.320 | 0.133 | 0.777 [0.495, 0.930] p-val=n/a | 0.797 | 0.671 | 0.166 | -0.016 | 0.593 | 0.609 | 0.061 |

## Cross-fitted training-task selection

### current5_mean_0_to_1

25/30 items are scored by every configuration, below the frozen ceil(0.9*declared) requirement of 27. The threshold is not relaxed.

### current3_mean_0_to_1

25/30 items are scored by every configuration, below the frozen ceil(0.9*declared) requirement of 27. The threshold is not relaxed.

## Model and harness means

These are descriptive means of the current-five training metrics. They are not a held-out model test.

| Group | Kind | n | Mean Spearman | Mean MAE | Mean bias |
|---|---|---:|---:|---:|---:|
| opus55x | model_key | 3 | 0.645 | 0.191 | -0.057 |
| qwen36 | model_key | 5 | 0.747 | 0.146 | -0.023 |
| t2_qwen | model_key | 2 | 0.587 | 0.189 | -0.070 |
| t2_sonnet5 | model_key | 2 | 0.703 | 0.195 | -0.056 |
| terminus2 | harness | 4 | 0.645 | 0.192 | -0.063 |
| vb103_judge | harness | 8 | 0.709 | 0.163 | -0.036 |

## Limitations

All findings reuse historical training labels and cached judges.
A favorable training comparison does not establish a better property, correctness, transfer, or validity on fresh raters.
Candidate 3 uses only the pre-existing audit of redundant weakenings whose guarantee is still stated elsewhere.

The gold-free repeat total variation on these same training rows is in [ADDENDUM_repeat_tvd_10-19-2026.md](ADDENDUM_repeat_tvd_10-19-2026.md): it spans 0.111 to 0.267 and its Spearman with training agreement is 0.210 (p-val=n/a).

**TLDR-end:** [cert-judge: 56 semantic margin training diagnosis] The frozen training-only analysis reports the original margin, both revisions, and the existing comparators without using validation or test outcomes.
