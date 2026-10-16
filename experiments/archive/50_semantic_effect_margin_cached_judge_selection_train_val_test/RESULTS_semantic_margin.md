# Semantic effect margin: cached judge selection

**Doc link:** https://github.com/brando90/cert-judge/tree/codex/cj-e50-semantic-margin/experiments/archive/50_semantic_effect_margin_cached_judge_selection_train_val_test

## Result

On the historical VeriBench version 1 test split, maximum training semantic margin selected `t2_sonnet5|D0` and had expected Spearman 0.815 [0.414, 0.950], versus fixed H2 0.826 [0.507, 0.934]; the paired margin-minus-H2 difference is -0.012 [-0.197, 0.183] (p-val=n/a).
The interval spans zero, so this exploratory cached analysis supplies no positive selection evidence; validation is unavailable under the frozen common-support rule (13/15 files, 14 required).

## Frozen scope and provenance

The selector was frozen before outcome loading: `selection_receipt.json` records `human_outcomes_read=false` and SHA-256 `5cce7bd559bfae1ddd3fb531ef268aeb0cafaf5f5fc5b79b31b24254523bd858`.
The post-selection evaluator correction only fixed return-value unpacking and added deterministic adapter fixtures; `evaluation_source_manifest.json` hashes the correction, selection bytes, and imported experiment-45 inventory dependency.
Inputs are archived experiment-46/39/42/44/45 cached artifacts; there were zero new judge calls, no new human data, and no manuscript/reference changes.

## Common support

| Split | Status | Common / declared files | Requirement | Tasks |
| --- | --- | ---: | ---: | ---: |
| validation | UNAVAILABLE_SHARED_SUPPORT | 13 / 15 | 14 | n/a |
| test | COMPUTED | 29 / 30 | 27 | 10 |

## Test utility: current-five target

| Selector | Spearman [95% task bootstrap] | Pearson | Kendall tau-b | MAE | Bias | Judge mean | Human mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_H2 | 0.826 [0.507, 0.934] | 0.855 [0.659, 0.951] | 0.704 [0.419, 0.843] | 0.142 [0.100, 0.195] | 0.038 [-0.016, 0.093] | 0.627 [0.456, 0.789] | 0.589 [0.453, 0.723] |
| max_train_C_ms_gold | 0.700 [0.383, 0.852] | 0.686 [0.460, 0.824] | 0.587 [0.315, 0.760] | 0.221 [0.168, 0.273] | -0.095 [-0.182, 0.000] | 0.494 [0.316, 0.670] | 0.589 [0.453, 0.723] |
| max_train_prior_strict_minus_format | 0.768 [0.455, 0.888] | 0.779 [0.573, 0.887] | 0.648 [0.374, 0.796] | 0.173 [0.136, 0.212] | -0.006 [-0.059, 0.053] | 0.583 [0.420, 0.741] | 0.589 [0.453, 0.723] |
| max_train_semantic_margin | 0.815 [0.414, 0.950] | 0.826 [0.520, 0.954] | 0.666 [0.322, 0.866] | 0.197 [0.120, 0.290] | -0.120 [-0.246, -0.005] | 0.469 [0.257, 0.686] | 0.589 [0.453, 0.723] |
| property_deletion_tvd | undefined | undefined | undefined | undefined | undefined | undefined | undefined |
| property_repeat_tvd | 0.844 [0.472, 0.951] | 0.876 [0.728, 0.954] | 0.723 [0.384, 0.871] | 0.148 [0.102, 0.196] | 0.087 [0.020, 0.145] | 0.676 [0.500, 0.828] | 0.589 [0.453, 0.723] |
| property_semantic_auc | 0.768 [0.455, 0.888] | 0.779 [0.573, 0.887] | 0.648 [0.374, 0.796] | 0.173 [0.136, 0.212] | -0.006 [-0.059, 0.053] | 0.583 [0.420, 0.741] | 0.589 [0.453, 0.723] |
| random_primary12 | 0.774 [0.469, 0.891] | 0.784 [0.578, 0.890] | 0.655 [0.388, 0.799] | 0.171 [0.135, 0.211] | 0.002 [-0.050, 0.058] | 0.590 [0.428, 0.747] | 0.589 [0.453, 0.723] |

## Margin contrasts: current-five test target

| Comparator | Delta Spearman (margin minus comparator) [95% interval] |
| --- | --- |
| fixed_H2 | -0.012 [-0.197, 0.183] |
| max_train_C_ms_gold | 0.115 [-0.026, 0.242] |
| max_train_prior_strict_minus_format | 0.047 [-0.080, 0.150] |
| property_deletion_tvd | undefined |
| property_repeat_tvd | -0.029 [-0.120, 0.058] |
| property_semantic_auc | 0.047 [-0.080, 0.150] |
| random_primary12 | 0.041 [-0.095, 0.152] |

## Test utility: current-three sensitivity

| Selector | Spearman [95% task bootstrap] | Pearson | Kendall tau-b | MAE | Bias | Judge mean | Human mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_H2 | 0.848 [0.569, 0.941] | 0.853 [0.721, 0.936] | 0.742 [0.494, 0.869] | 0.179 [0.127, 0.234] | 0.145 [0.082, 0.210] | 0.627 [0.456, 0.789] | 0.482 [0.316, 0.655] |
| max_train_C_ms_gold | 0.694 [0.348, 0.860] | 0.690 [0.443, 0.841] | 0.589 [0.283, 0.788] | 0.199 [0.147, 0.251] | 0.012 [-0.087, 0.114] | 0.494 [0.316, 0.670] | 0.482 [0.316, 0.655] |
| max_train_prior_strict_minus_format | 0.771 [0.452, 0.891] | 0.767 [0.578, 0.867] | 0.662 [0.383, 0.817] | 0.195 [0.152, 0.237] | 0.101 [0.027, 0.175] | 0.583 [0.420, 0.741] | 0.482 [0.316, 0.655] |
| max_train_semantic_margin | 0.798 [0.335, 0.965] | 0.834 [0.454, 0.972] | 0.663 [0.251, 0.906] | 0.155 [0.095, 0.236] | -0.013 [-0.138, 0.087] | 0.469 [0.257, 0.686] | 0.482 [0.316, 0.655] |
| property_deletion_tvd | undefined | undefined | undefined | undefined | undefined | undefined | undefined |
| property_repeat_tvd | 0.840 [0.414, 0.975] | 0.853 [0.707, 0.945] | 0.737 [0.332, 0.935] | 0.208 [0.133, 0.281] | 0.194 [0.115, 0.269] | 0.676 [0.500, 0.828] | 0.482 [0.316, 0.655] |
| property_semantic_auc | 0.771 [0.452, 0.891] | 0.767 [0.578, 0.867] | 0.662 [0.383, 0.817] | 0.195 [0.152, 0.237] | 0.101 [0.027, 0.175] | 0.583 [0.420, 0.741] | 0.482 [0.316, 0.655] |
| random_primary12 | 0.778 [0.475, 0.894] | 0.770 [0.589, 0.867] | 0.669 [0.401, 0.819] | 0.197 [0.153, 0.239] | 0.109 [0.036, 0.181] | 0.590 [0.428, 0.747] | 0.482 [0.316, 0.655] |

| Current-three comparator | Delta Spearman (margin minus comparator) [95% interval] |
| --- | --- |
| fixed_H2 | -0.050 [-0.314, 0.117] |
| max_train_C_ms_gold | 0.104 [-0.072, 0.223] |
| max_train_prior_strict_minus_format | 0.027 [-0.157, 0.122] |
| property_deletion_tvd | undefined |
| property_repeat_tvd | -0.042 [-0.124, 0.020] |
| property_semantic_auc | 0.027 [-0.157, 0.122] |
| random_primary12 | 0.020 [-0.178, 0.123] |

Per-judge results, repeat-count histograms, every seven-metric contrast, and all leave-one-out tables are committed in `results/evaluation.json` and `results/robustness.json`.

## Cross-configuration association

| Training property | Configurations | Spearman [95% task bootstrap] | Pearson | Kendall tau-b |
| --- | ---: | --- | --- | --- |
| deletion_tvd | 0 | undefined | undefined | undefined |
| repeat_tvd | 12 | -0.168 [-0.529, 0.252] | -0.290 [-0.461, 0.207] | -0.091 [-0.364, 0.182] |
| semantic_auc | 12 | -0.306 [-0.480, 0.306] | -0.181 [-0.382, 0.275] | -0.260 [-0.408, 0.260] |
| semantic_margin | 12 | -0.580 [-0.846, 0.636] | -0.414 [-0.679, 0.601] | -0.394 [-0.667, 0.443] |

## Robustness and limitations

`results/robustness.json` retains every leave-training-task selector, every leave-test-task paired estimate, and each four-way model/harness exclusion evaluated on the original full-pool common test rows.
Deletion total-variation distance remains unavailable because the frozen gold-deletion cache has one accepted repeat per level, below the required two.
A high semantic margin is a response-effect property, not proof of correctness: the deterministic fixture includes a high-margin scorer with reversed human ordering.
All intervals are 95% percentile intervals from 10,000 paired task-cluster draws at seed 20261008, p-val=n/a; they condition on cached scores, selectors, the fixed pool, and current raters and omit selector, model-population, and new-rater uncertainty.
Archived-baseline reproduction: PASS over 550 comparable cells at absolute tolerance 1e-12.

## Artifacts

Numerical tables: `results/configuration_overview.json`, `per_probe_task_components.json`, `selectors.json`, `evaluation.json`, `association.json`, `robustness.json`, `baseline_reproduction.json`, and `runtime.json`.
Archive-only source provenance and the exact non-mutating verification command are in [ARCHIVE_INTEGRITY.md](ARCHIVE_INTEGRITY.md).

**TLDR-end:** [cert-judge: 50_semantic_effect_margin_cached_judge_selection_train_val_test] The frozen semantic-margin selector does not show a positive historical cached-selection advantage over fixed H2 on the 29-file test support; all numerical artifacts and conditional uncertainty are committed.

**Snapshot:**
```text
margin selector: t2_sonnet5|D0
test support: 29/30 files, 10 tasks
margin Spearman: 0.815
fixed H2 Spearman: 0.826
paired delta: -0.012 [-0.197, 0.183]
validation: UNAVAILABLE_SHARED_SUPPORT (13/15)
```
