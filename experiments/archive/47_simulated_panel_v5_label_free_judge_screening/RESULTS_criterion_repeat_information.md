# Criterion repeat-information analyses

**Doc link:** [Criterion agreement and original evidence](RESULTS_criterion_campaign.md)

**TLDR:** The frozen repeat-information property is evaluated for the complete declared pool with missingness retained. Undefined associations, selection gains and planning results remain unavailable; this phase establishes no full-study shortlist.

The property measures total-variation-distance mutual information between binned repeated scores. A task requires at least two candidates with all three accepted repeats; a configuration requires at least 80% task coverage. Selection utility requires at least 90% common item coverage across the declared comparison pool. These thresholds come from the frozen protocol and owner-property amendment. Held-out agent-group candidates are removed before rebuilding task-level repeat distributions.

All intervals below are 95% percentile intervals from 10,000 task bootstrap draws with seed 47, preserving multiplicity and pairings. Associations additionally resample the three observed base-model clusters, keeping both Qwen harness variants in one cluster. Unconditional intervals recompute the selector; conditional intervals hold the observed selection fixed. No hypothesis test is performed (p-val=n/a).

Planning assumes a +0.10 gain alternative, a one-sided centered-null 97.5th-percentile threshold and an 80% target rejection probability, conditional on the observed pool and tasks. Monte Carlo intervals describe simulation error. Independent new-family requirements remain NOT_IDENTIFIABLE.

## T_C0_equal_group_mean

[T_C0_equal_group_mean.json](expt_v1/results/repeat_only_analysis/T_C0_equal_group_mean.json)

### repeat_tvd

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

## T_C0_exclude_base_Opus

[T_C0_exclude_base_Opus.json](expt_v1/results/repeat_only_analysis/T_C0_exclude_base_Opus.json)

Common support: 0/691 items (NOT_COMPUTABLE); 2 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 0/9. Selector: abstains.
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_exclude_base_Qwen

[T_C0_exclude_base_Qwen.json](expt_v1/results/repeat_only_analysis/T_C0_exclude_base_Qwen.json)

Common support: 0/691 items (NOT_COMPUTABLE); 2 base-model clusters and 1 provider families.

### repeat_tvd

Computable property configurations: 2/5. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_exclude_base_Sonnet

[T_C0_exclude_base_Sonnet.json](expt_v1/results/repeat_only_analysis/T_C0_exclude_base_Sonnet.json)

Common support: 0/691 items (NOT_COMPUTABLE); 2 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/10. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_exclude_provider_Alibaba

[T_C0_exclude_provider_Alibaba.json](expt_v1/results/repeat_only_analysis/T_C0_exclude_provider_Alibaba.json)

Common support: 0/691 items (NOT_COMPUTABLE); 2 base-model clusters and 1 provider families.

### repeat_tvd

Computable property configurations: 2/5. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_exclude_provider_Anthropic

[T_C0_exclude_provider_Anthropic.json](expt_v1/results/repeat_only_analysis/T_C0_exclude_provider_Anthropic.json)

Common support: 0/691 items (NOT_COMPUTABLE); 1 base-model clusters and 1 provider families.

### repeat_tvd

Computable property configurations: 0/7. Selector: abstains.
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G01

[T_C0_group_G01.json](expt_v1/results/repeat_only_analysis/T_C0_group_G01.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G02

[T_C0_group_G02.json](expt_v1/results/repeat_only_analysis/T_C0_group_G02.json)

Common support: 0/49 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G03

[T_C0_group_G03.json](expt_v1/results/repeat_only_analysis/T_C0_group_G03.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G04

[T_C0_group_G04.json](expt_v1/results/repeat_only_analysis/T_C0_group_G04.json)

Common support: 0/23 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G05

[T_C0_group_G05.json](expt_v1/results/repeat_only_analysis/T_C0_group_G05.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G06

[T_C0_group_G06.json](expt_v1/results/repeat_only_analysis/T_C0_group_G06.json)

Common support: 0/49 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G07

[T_C0_group_G07.json](expt_v1/results/repeat_only_analysis/T_C0_group_G07.json)

Common support: 0/20 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G08

[T_C0_group_G08.json](expt_v1/results/repeat_only_analysis/T_C0_group_G08.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G09

[T_C0_group_G09.json](expt_v1/results/repeat_only_analysis/T_C0_group_G09.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G10

[T_C0_group_G10.json](expt_v1/results/repeat_only_analysis/T_C0_group_G10.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G11

[T_C0_group_G11.json](expt_v1/results/repeat_only_analysis/T_C0_group_G11.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G12

[T_C0_group_G12.json](expt_v1/results/repeat_only_analysis/T_C0_group_G12.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G13

[T_C0_group_G13.json](expt_v1/results/repeat_only_analysis/T_C0_group_G13.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G16

[T_C0_group_G16.json](expt_v1/results/repeat_only_analysis/T_C0_group_G16.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_group_G17

[T_C0_group_G17.json](expt_v1/results/repeat_only_analysis/T_C0_group_G17.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_planning

[T_C0_planning.json](expt_v1/results/repeat_only_analysis/T_C0_planning.json)

| Pool size | Resampled tasks | Subpools | Status | Finite/draws | Rejections | Power [Monte Carlo 95% interval] | Undefined-draw reasons |
|---:|---:|---:|---|---:|---:|---|---|
| 4 | 25 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 4 | 50 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 4 | 100 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 4 | 200 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 4 | 400 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 25 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 50 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 100 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 200 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 400 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 25 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 50 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 100 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 200 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 400 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 25 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 50 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 100 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 200 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 400 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |

## T_C0_pooled

[T_C0_pooled.json](expt_v1/results/repeat_only_analysis/T_C0_pooled.json)

| Configuration | Tasks with defined repeat information / declared | Required fraction |
|---|---:|---:|
| opus55x / D0 | 26/50 | 0.8 |
| opus55x / H0 | 50/50 | 0.8 |
| opus55x / H2 | 50/50 | 0.8 |
| qwen36 / D0 | 13/50 | 0.8 |
| qwen36 / H0 | 5/50 | 0.8 |
| qwen36 / H1 | 5/50 | 0.8 |
| qwen36 / H2 | 5/50 | 0.8 |
| qwen36 / R4 | 7/50 | 0.8 |
| t2_qwen / D0 | 2/50 | 0.8 |
| t2_qwen / H2 | 0/50 | 0.8 |
| t2_sonnet5 / D0 | 2/50 | 0.8 |
| t2_sonnet5 / H2 | 0/50 | 0.8 |

Common support: 0/691 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_task_fold_0

[T_C0_task_fold_0.json](expt_v1/results/repeat_only_analysis/T_C0_task_fold_0.json)

Common support: 0/138 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_task_fold_1

[T_C0_task_fold_1.json](expt_v1/results/repeat_only_analysis/T_C0_task_fold_1.json)

Common support: 0/141 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_task_fold_2

[T_C0_task_fold_2.json](expt_v1/results/repeat_only_analysis/T_C0_task_fold_2.json)

Common support: 0/138 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_task_fold_3

[T_C0_task_fold_3.json](expt_v1/results/repeat_only_analysis/T_C0_task_fold_3.json)

Common support: 0/140 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_C0_task_fold_4

[T_C0_task_fold_4.json](expt_v1/results/repeat_only_analysis/T_C0_task_fold_4.json)

Common support: 0/134 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_equal_group_mean

[T_all_equal_group_mean.json](expt_v1/results/repeat_only_analysis/T_all_equal_group_mean.json)

### repeat_tvd

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

## T_all_exclude_base_Opus

[T_all_exclude_base_Opus.json](expt_v1/results/repeat_only_analysis/T_all_exclude_base_Opus.json)

Common support: 0/691 items (NOT_COMPUTABLE); 2 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 0/9. Selector: abstains.
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_exclude_base_Qwen

[T_all_exclude_base_Qwen.json](expt_v1/results/repeat_only_analysis/T_all_exclude_base_Qwen.json)

Common support: 0/691 items (NOT_COMPUTABLE); 2 base-model clusters and 1 provider families.

### repeat_tvd

Computable property configurations: 2/5. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_exclude_base_Sonnet

[T_all_exclude_base_Sonnet.json](expt_v1/results/repeat_only_analysis/T_all_exclude_base_Sonnet.json)

Common support: 0/691 items (NOT_COMPUTABLE); 2 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/10. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_exclude_provider_Alibaba

[T_all_exclude_provider_Alibaba.json](expt_v1/results/repeat_only_analysis/T_all_exclude_provider_Alibaba.json)

Common support: 0/691 items (NOT_COMPUTABLE); 2 base-model clusters and 1 provider families.

### repeat_tvd

Computable property configurations: 2/5. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_exclude_provider_Anthropic

[T_all_exclude_provider_Anthropic.json](expt_v1/results/repeat_only_analysis/T_all_exclude_provider_Anthropic.json)

Common support: 0/691 items (NOT_COMPUTABLE); 1 base-model clusters and 1 provider families.

### repeat_tvd

Computable property configurations: 0/7. Selector: abstains.
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G01

[T_all_group_G01.json](expt_v1/results/repeat_only_analysis/T_all_group_G01.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G02

[T_all_group_G02.json](expt_v1/results/repeat_only_analysis/T_all_group_G02.json)

Common support: 0/49 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G03

[T_all_group_G03.json](expt_v1/results/repeat_only_analysis/T_all_group_G03.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G04

[T_all_group_G04.json](expt_v1/results/repeat_only_analysis/T_all_group_G04.json)

Common support: 0/23 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G05

[T_all_group_G05.json](expt_v1/results/repeat_only_analysis/T_all_group_G05.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G06

[T_all_group_G06.json](expt_v1/results/repeat_only_analysis/T_all_group_G06.json)

Common support: 0/49 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G07

[T_all_group_G07.json](expt_v1/results/repeat_only_analysis/T_all_group_G07.json)

Common support: 0/20 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G08

[T_all_group_G08.json](expt_v1/results/repeat_only_analysis/T_all_group_G08.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G09

[T_all_group_G09.json](expt_v1/results/repeat_only_analysis/T_all_group_G09.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G10

[T_all_group_G10.json](expt_v1/results/repeat_only_analysis/T_all_group_G10.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G11

[T_all_group_G11.json](expt_v1/results/repeat_only_analysis/T_all_group_G11.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G12

[T_all_group_G12.json](expt_v1/results/repeat_only_analysis/T_all_group_G12.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G13

[T_all_group_G13.json](expt_v1/results/repeat_only_analysis/T_all_group_G13.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G16

[T_all_group_G16.json](expt_v1/results/repeat_only_analysis/T_all_group_G16.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_group_G17

[T_all_group_G17.json](expt_v1/results/repeat_only_analysis/T_all_group_G17.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_planning

[T_all_planning.json](expt_v1/results/repeat_only_analysis/T_all_planning.json)

| Pool size | Resampled tasks | Subpools | Status | Finite/draws | Rejections | Power [Monte Carlo 95% interval] | Undefined-draw reasons |
|---:|---:|---:|---|---:|---:|---|---|
| 4 | 25 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 4 | 50 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 4 | 100 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 4 | 200 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 4 | 400 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 25 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 50 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 100 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 200 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 400 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 25 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 50 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 100 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 200 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 400 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 25 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 50 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 100 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 200 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 400 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |

## T_all_pooled

[T_all_pooled.json](expt_v1/results/repeat_only_analysis/T_all_pooled.json)

| Configuration | Tasks with defined repeat information / declared | Required fraction |
|---|---:|---:|
| opus55x / D0 | 26/50 | 0.8 |
| opus55x / H0 | 50/50 | 0.8 |
| opus55x / H2 | 50/50 | 0.8 |
| qwen36 / D0 | 13/50 | 0.8 |
| qwen36 / H0 | 5/50 | 0.8 |
| qwen36 / H1 | 5/50 | 0.8 |
| qwen36 / H2 | 5/50 | 0.8 |
| qwen36 / R4 | 7/50 | 0.8 |
| t2_qwen / D0 | 2/50 | 0.8 |
| t2_qwen / H2 | 0/50 | 0.8 |
| t2_sonnet5 / D0 | 2/50 | 0.8 |
| t2_sonnet5 / H2 | 0/50 | 0.8 |

Common support: 0/691 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_task_fold_0

[T_all_task_fold_0.json](expt_v1/results/repeat_only_analysis/T_all_task_fold_0.json)

Common support: 0/138 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_task_fold_1

[T_all_task_fold_1.json](expt_v1/results/repeat_only_analysis/T_all_task_fold_1.json)

Common support: 0/141 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_task_fold_2

[T_all_task_fold_2.json](expt_v1/results/repeat_only_analysis/T_all_task_fold_2.json)

Common support: 0/138 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_task_fold_3

[T_all_task_fold_3.json](expt_v1/results/repeat_only_analysis/T_all_task_fold_3.json)

Common support: 0/140 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_all_task_fold_4

[T_all_task_fold_4.json](expt_v1/results/repeat_only_analysis/T_all_task_fold_4.json)

Common support: 0/134 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_equal_group_mean

[T_common_excluding_Anthropic_Alibaba_equal_group_mean.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_equal_group_mean.json)

### repeat_tvd

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

## T_common_excluding_Anthropic_Alibaba_exclude_base_Opus

[T_common_excluding_Anthropic_Alibaba_exclude_base_Opus.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_exclude_base_Opus.json)

Common support: 0/691 items (NOT_COMPUTABLE); 2 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 0/9. Selector: abstains.
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_exclude_base_Qwen

[T_common_excluding_Anthropic_Alibaba_exclude_base_Qwen.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_exclude_base_Qwen.json)

Common support: 0/691 items (NOT_COMPUTABLE); 2 base-model clusters and 1 provider families.

### repeat_tvd

Computable property configurations: 2/5. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_exclude_base_Sonnet

[T_common_excluding_Anthropic_Alibaba_exclude_base_Sonnet.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_exclude_base_Sonnet.json)

Common support: 0/691 items (NOT_COMPUTABLE); 2 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/10. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_exclude_provider_Alibaba

[T_common_excluding_Anthropic_Alibaba_exclude_provider_Alibaba.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_exclude_provider_Alibaba.json)

Common support: 0/691 items (NOT_COMPUTABLE); 2 base-model clusters and 1 provider families.

### repeat_tvd

Computable property configurations: 2/5. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_exclude_provider_Anthropic

[T_common_excluding_Anthropic_Alibaba_exclude_provider_Anthropic.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_exclude_provider_Anthropic.json)

Common support: 0/691 items (NOT_COMPUTABLE); 1 base-model clusters and 1 provider families.

### repeat_tvd

Computable property configurations: 0/7. Selector: abstains.
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G01

[T_common_excluding_Anthropic_Alibaba_group_G01.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G01.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G02

[T_common_excluding_Anthropic_Alibaba_group_G02.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G02.json)

Common support: 0/49 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G03

[T_common_excluding_Anthropic_Alibaba_group_G03.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G03.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G04

[T_common_excluding_Anthropic_Alibaba_group_G04.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G04.json)

Common support: 0/23 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G05

[T_common_excluding_Anthropic_Alibaba_group_G05.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G05.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G06

[T_common_excluding_Anthropic_Alibaba_group_G06.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G06.json)

Common support: 0/49 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G07

[T_common_excluding_Anthropic_Alibaba_group_G07.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G07.json)

Common support: 0/20 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G08

[T_common_excluding_Anthropic_Alibaba_group_G08.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G08.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G09

[T_common_excluding_Anthropic_Alibaba_group_G09.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G09.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G10

[T_common_excluding_Anthropic_Alibaba_group_G10.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G10.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G11

[T_common_excluding_Anthropic_Alibaba_group_G11.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G11.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G12

[T_common_excluding_Anthropic_Alibaba_group_G12.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G12.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G13

[T_common_excluding_Anthropic_Alibaba_group_G13.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G13.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G16

[T_common_excluding_Anthropic_Alibaba_group_G16.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G16.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_group_G17

[T_common_excluding_Anthropic_Alibaba_group_G17.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_group_G17.json)

Common support: 0/50 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_planning

[T_common_excluding_Anthropic_Alibaba_planning.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_planning.json)

| Pool size | Resampled tasks | Subpools | Status | Finite/draws | Rejections | Power [Monte Carlo 95% interval] | Undefined-draw reasons |
|---:|---:|---:|---|---:|---:|---|---|
| 4 | 25 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 4 | 50 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 4 | 100 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 4 | 200 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 4 | 400 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 25 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 50 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 100 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 200 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 6 | 400 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 25 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 50 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 100 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 200 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 8 | 400 | 100 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 25 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 50 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 100 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 200 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |
| 12 | 400 | 1 | NOT_COMPUTABLE | 0/10000 | undefined | undefined [undefined] | {'common_support_below_90_percent': 10000} |

## T_common_excluding_Anthropic_Alibaba_pooled

[T_common_excluding_Anthropic_Alibaba_pooled.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_pooled.json)

| Configuration | Tasks with defined repeat information / declared | Required fraction |
|---|---:|---:|
| opus55x / D0 | 26/50 | 0.8 |
| opus55x / H0 | 50/50 | 0.8 |
| opus55x / H2 | 50/50 | 0.8 |
| qwen36 / D0 | 13/50 | 0.8 |
| qwen36 / H0 | 5/50 | 0.8 |
| qwen36 / H1 | 5/50 | 0.8 |
| qwen36 / H2 | 5/50 | 0.8 |
| qwen36 / R4 | 7/50 | 0.8 |
| t2_qwen / D0 | 2/50 | 0.8 |
| t2_qwen / H2 | 0/50 | 0.8 |
| t2_sonnet5 / D0 | 2/50 | 0.8 |
| t2_sonnet5 / H2 | 0/50 | 0.8 |

Common support: 0/691 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_task_fold_0

[T_common_excluding_Anthropic_Alibaba_task_fold_0.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_task_fold_0.json)

Common support: 0/138 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_task_fold_1

[T_common_excluding_Anthropic_Alibaba_task_fold_1.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_task_fold_1.json)

Common support: 0/141 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_task_fold_2

[T_common_excluding_Anthropic_Alibaba_task_fold_2.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_task_fold_2.json)

Common support: 0/138 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_task_fold_3

[T_common_excluding_Anthropic_Alibaba_task_fold_3.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_task_fold_3.json)

Common support: 0/140 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.

## T_common_excluding_Anthropic_Alibaba_task_fold_4

[T_common_excluding_Anthropic_Alibaba_task_fold_4.json](expt_v1/results/repeat_only_analysis/T_common_excluding_Anthropic_Alibaba_task_fold_4.json)

Common support: 0/134 items (NOT_COMPUTABLE); 3 base-model clusters and 2 provider families.

### repeat_tvd

Computable property configurations: 2/12. Selector: opus55x|H0 (1).
Finite association: 0 configurations, 0 base-model clusters, 0 provider families.

| Association | Estimate [95% interval]; finite draws |
|---|---|
| kendall | undefined [undefined]; 0/10000 finite |
| pearson | undefined [undefined]; 0/10000 finite |
| spearman | undefined [undefined]; 0/10000 finite |

| Selection quantity | Unconditional: selector recomputed | Conditional: observed selection fixed |
|---|---|---|
| gain_vs_H2 | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| gain_vs_random | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| regret | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |
| selected_spearman | undefined [undefined]; 0/10000 finite | undefined [undefined]; 0/10000 finite |

### Exact control expectations

| Control | Estimate [95% interval]; finite draws |
|---|---|
| hindsight_oracle | undefined [undefined]; 0/10000 finite |
| uniform_H2 | undefined [undefined]; 0/10000 finite |
| uniform_random | undefined [undefined]; 0/10000 finite |

Seeded single-judge variability is separately available in the source JSON. Its distribution intervals combine selector randomness with task resampling and are not confidence intervals for the exact expectations.
