# Experiment 46 results: information-inspired properties on measured judge caches

**Status:** COMPLETE — exploratory historical-cache analysis only; this is not prospective validation.

**Paper summary:** [PAPER_SUMMARY.md](PAPER_SUMMARY.md) gives the short manuscript-facing interpretation.

## Operational properties

Semantic AUC compares signed score drops on audit-strict weakenings with absolute score changes on formatting probes.
Repeat TVD is five-bin total variation between paired repeat scores and the product of their repeat marginals.
Deletion TVD is level-score total variation normalized by the finite-level maximum and multiplied by a direction gate.

## Measured property overview

| Split | Property | Computed configurations / 56 | Observed range |
| --- | --- | ---: | --- |
| train | semantic_auc | 56 / 56 | -0.433 to 1.000 |
| train | repeat_tvd | 56 / 56 | 0.000 to 0.267 |
| train | deletion_tvd | 0 / 56 | unavailable |
| val | semantic_auc | 55 / 56 | -0.750 to 1.000 |
| val | repeat_tvd | 52 / 56 | 0.000 to 0.311 |
| val | deletion_tvd | 0 / 56 | unavailable |
| test | semantic_auc | 56 / 56 | -0.533 to 1.000 |
| test | repeat_tvd | 54 / 56 | 0.000 to 0.259 |
| test | deletion_tvd | 0 / 56 | unavailable |

Deletion TVD is unavailable for all 56 configurations: experiment 39's `ms_gold` cache intentionally has one accepted repeat per level, below the frozen two-repeat requirement.

## Primary 12-configuration pool — historical test split

The historical test comparison has 29/30 common candidate files across 10 tasks (requirement: 27); validation is UNAVAILABLE_SHARED_SUPPORT with 13/15 common files (requirement: 14).

| Selector | Spearman (95% task-bootstrap interval) | Pearson | Kendall | Mean absolute error | Bias (judge − human) | Judge mean / human mean | Δ Spearman vs fixed H2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_H2 (opus55x|H2, qwen36|H2, t2_qwen|H2, t2_sonnet5|H2) | 0.826 [0.507, 0.934] | 0.855 | 0.704 | 0.142 | 0.038 | 0.627 / 0.589 | n/a |
| max_train_C_ms_gold (opus55x|D0, qwen36|D0, t2_qwen|D0, t2_sonnet5|D0) | 0.700 [0.383, 0.852] | 0.686 | 0.587 | 0.221 | -0.095 | 0.494 / 0.589 | -0.127 [-0.281, 0.112] |
| max_train_prior_strict_minus_format (opus55x|D0, opus55x|H0, opus55x|H2, qwen36|D0, qwen36|H0, qwen36|H2, qwen36|R4, t2_qwen|D0, t2_qwen|H2, t2_sonnet5|D0, t2_sonnet5|H2) | 0.768 [0.455, 0.888] | 0.779 | 0.648 | 0.173 | -0.006 | 0.583 / 0.589 | -0.059 [-0.156, 0.054] |
| property_deletion_tvd (unavailable) | unavailable | n/a | n/a | n/a | n/a | n/a | n/a |
| property_repeat_tvd (opus55x|H2) | 0.844 [0.472, 0.951] | 0.876 | 0.723 | 0.148 | 0.087 | 0.676 / 0.589 | 0.018 [-0.127, 0.186] |
| property_semantic_auc (opus55x|D0, opus55x|H0, opus55x|H2, qwen36|D0, qwen36|H0, qwen36|H2, qwen36|R4, t2_qwen|D0, t2_qwen|H2, t2_sonnet5|D0, t2_sonnet5|H2) | 0.768 [0.455, 0.888] | 0.779 | 0.648 | 0.173 | -0.006 | 0.583 / 0.589 | -0.059 [-0.156, 0.054] |
| random_primary12 (opus55x|D0, opus55x|H0, opus55x|H2, qwen36|D0, qwen36|H0, qwen36|H1, qwen36|H2, qwen36|R4, t2_qwen|D0, t2_qwen|H2, t2_sonnet5|D0, t2_sonnet5|H2) | 0.774 [0.469, 0.891] | 0.784 | 0.655 | 0.171 | 0.002 | 0.590 / 0.589 | -0.053 [-0.140, 0.051] |

All intervals are 95% percentile intervals from 10,000 paired task-cluster draws, p-val=n/a. The repeat-count histogram and mean within-item sample standard deviation for every pool configuration are recorded in `results/selector_utility.json`.

## Cross-configuration association

These associations are across 12 correlated judge configurations, with the train property fixed and test human-agreement Spearman recomputed inside each task bootstrap draw.

| Train property | Configurations | Association Spearman (95% interval) | Pearson | Kendall |
| --- | ---: | --- | --- | --- |
| semantic_auc | 12 | -0.306 [-0.480, 0.306] | -0.181 | -0.260 |
| repeat_tvd | 12 | -0.168 [-0.529, 0.252] | -0.290 | -0.091 |
| deletion_tvd | 0 | unavailable | n/a | n/a |

## Limitations and next step

The selection and association intervals condition on the fixed configuration pool, cached judge scores, selected weights, and current raters; they omit selector, model-population, and new-rater uncertainty.
The historical train/validation/test labels name the original task splits, but every result here reuses historical data and is exploratory.
Information is not sufficient for correctness: score inversion preserves repeat-distribution information, while the deletion direction gate rejects reversed ladders.
The appropriate next step is prospective evaluation with the properties and selector frozen before collecting new ratings.

## Artifacts

Machine-readable property rows, task detail, frozen selectors, controls, utility, associations, and runtime receipt are under `results/`.

**TLDR-end:** [cert-judge: e46 historical measured-cache information properties] The offline study reports all registered properties and fixed-pool utilities from existing measured caches, with no prospective claim.

**Snapshot:** 56 measured configurations received property rows; the fixed 12-configuration pool was evaluated with 10,000 paired task-bootstrap draws.
