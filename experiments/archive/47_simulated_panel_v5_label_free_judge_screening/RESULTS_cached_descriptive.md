# Cached Opus judge agreement with the frozen simulated panel

**Doc link:** [Experiment ledger](results.md)

**TLDR:** Both exactly reproduced cached Opus configurations have 691/691 nonblank aggregate scores on 50 tasks. These are descriptive simulated-panel results for two of the twelve declared configurations; property selection and the complete campaign remain pending.

All intervals below are 95% percentile intervals from 10,000 paired task-cluster draws, seed 47. Repeated task multiplicity is retained. `p-val=n/a`: no hypothesis test was performed. Scores are normalized to [0,1]; bias is judge minus simulated panel, positive meaning lenient. Intervals condition on the existing panel and these fixed judges; they omit new-rater and model-population uncertainty.

## T_C0 — late_G16_G17

| Configuration | Spearman | Pearson | Kendall tau-b |
|---|---|---|---|
| opus55x / H0 | 0.673 [0.529, 0.779] | 0.745 [0.576, 0.856] | 0.575 [0.452, 0.674] |
| opus55x / H2 | 0.613 [0.446, 0.730] | 0.726 [0.558, 0.821] | 0.520 [0.379, 0.622] |

| Configuration | Mean absolute error | Bias | Judge mean | Panel mean | Rows / tasks |
|---|---|---|---|---|---|
| opus55x / H0 | 0.073 [0.059, 0.088] | 0.044 [0.024, 0.064] | 0.918 [0.884, 0.948] | 0.874 [0.848, 0.899] | 100/100 / 50 |
| opus55x / H2 | 0.091 [0.075, 0.107] | 0.088 [0.071, 0.105] | 0.962 [0.936, 0.984] | 0.874 [0.848, 0.899] | 100/100 / 50 |

## T_C0 — original_G01_G13

| Configuration | Spearman | Pearson | Kendall tau-b |
|---|---|---|---|
| opus55x / H0 | 0.925 [0.900, 0.941] | 0.945 [0.934, 0.955] | 0.825 [0.798, 0.846] |
| opus55x / H2 | 0.886 [0.852, 0.910] | 0.902 [0.880, 0.921] | 0.771 [0.735, 0.799] |

| Configuration | Mean absolute error | Bias | Judge mean | Panel mean | Rows / tasks |
|---|---|---|---|---|---|
| opus55x / H0 | 0.072 [0.064, 0.081] | 0.042 [0.030, 0.054] | 0.756 [0.714, 0.795] | 0.714 [0.678, 0.748] | 591/591 / 50 |
| opus55x / H2 | 0.101 [0.089, 0.114] | 0.067 [0.051, 0.084] | 0.781 [0.741, 0.820] | 0.714 [0.678, 0.748] | 591/591 / 50 |

## T_C0 — pooled

| Configuration | Spearman | Pearson | Kendall tau-b |
|---|---|---|---|
| opus55x / H0 | 0.907 [0.879, 0.928] | 0.941 [0.929, 0.950] | 0.805 [0.775, 0.829] |
| opus55x / H2 | 0.873 [0.834, 0.902] | 0.903 [0.882, 0.921] | 0.758 [0.720, 0.789] |

| Configuration | Mean absolute error | Bias | Judge mean | Panel mean | Rows / tasks |
|---|---|---|---|---|---|
| opus55x / H0 | 0.073 [0.065, 0.081] | 0.042 [0.030, 0.054] | 0.779 [0.742, 0.815] | 0.737 [0.705, 0.768] | 691/691 / 50 |
| opus55x / H2 | 0.099 [0.088, 0.111] | 0.070 [0.055, 0.085] | 0.808 [0.771, 0.842] | 0.737 [0.705, 0.768] | 691/691 / 50 |

## T_all — late_G16_G17

| Configuration | Spearman | Pearson | Kendall tau-b |
|---|---|---|---|
| opus55x / H0 | 0.711 [0.594, 0.800] | 0.809 [0.640, 0.901] | 0.602 [0.501, 0.686] |
| opus55x / H2 | 0.613 [0.448, 0.728] | 0.800 [0.618, 0.890] | 0.517 [0.378, 0.620] |

| Configuration | Mean absolute error | Bias | Judge mean | Panel mean | Rows / tasks |
|---|---|---|---|---|---|
| opus55x / H0 | 0.055 [0.043, 0.067] | 0.009 [-0.009, 0.026] | 0.918 [0.884, 0.948] | 0.909 [0.883, 0.932] | 100/100 / 50 |
| opus55x / H2 | 0.058 [0.045, 0.071] | 0.053 [0.039, 0.067] | 0.962 [0.936, 0.984] | 0.909 [0.883, 0.932] | 100/100 / 50 |

## T_all — original_G01_G13

| Configuration | Spearman | Pearson | Kendall tau-b |
|---|---|---|---|
| opus55x / H0 | 0.925 [0.900, 0.943] | 0.956 [0.945, 0.965] | 0.820 [0.791, 0.842] |
| opus55x / H2 | 0.900 [0.867, 0.924] | 0.932 [0.915, 0.947] | 0.784 [0.750, 0.812] |

| Configuration | Mean absolute error | Bias | Judge mean | Panel mean | Rows / tasks |
|---|---|---|---|---|---|
| opus55x / H0 | 0.057 [0.051, 0.063] | 0.011 [0.000, 0.021] | 0.756 [0.714, 0.795] | 0.745 [0.708, 0.781] | 591/591 / 50 |
| opus55x / H2 | 0.074 [0.064, 0.085] | 0.036 [0.023, 0.050] | 0.781 [0.741, 0.820] | 0.745 [0.708, 0.781] | 591/591 / 50 |

## T_all — pooled

| Configuration | Spearman | Pearson | Kendall tau-b |
|---|---|---|---|
| opus55x / H0 | 0.910 [0.882, 0.931] | 0.953 [0.943, 0.962] | 0.803 [0.772, 0.828] |
| opus55x / H2 | 0.885 [0.849, 0.913] | 0.933 [0.916, 0.947] | 0.769 [0.733, 0.800] |

| Configuration | Mean absolute error | Bias | Judge mean | Panel mean | Rows / tasks |
|---|---|---|---|---|---|
| opus55x / H0 | 0.057 [0.051, 0.063] | 0.010 [0.000, 0.020] | 0.779 [0.742, 0.815] | 0.769 [0.736, 0.801] | 691/691 / 50 |
| opus55x / H2 | 0.072 [0.062, 0.082] | 0.039 [0.026, 0.051] | 0.808 [0.771, 0.842] | 0.769 [0.736, 0.801] | 691/691 / 50 |

## T_common_excluding_Anthropic_Alibaba — late_G16_G17

| Configuration | Spearman | Pearson | Kendall tau-b |
|---|---|---|---|
| opus55x / H0 | 0.705 [0.583, 0.796] | 0.800 [0.618, 0.898] | 0.601 [0.498, 0.687] |
| opus55x / H2 | 0.615 [0.449, 0.730] | 0.812 [0.629, 0.897] | 0.523 [0.383, 0.626] |

| Configuration | Mean absolute error | Bias | Judge mean | Panel mean | Rows / tasks |
|---|---|---|---|---|---|
| opus55x / H0 | 0.057 [0.045, 0.069] | 0.006 [-0.012, 0.024] | 0.918 [0.884, 0.948] | 0.912 [0.886, 0.935] | 100/100 / 50 |
| opus55x / H2 | 0.056 [0.044, 0.069] | 0.050 [0.038, 0.063] | 0.962 [0.936, 0.984] | 0.912 [0.886, 0.935] | 100/100 / 50 |

## T_common_excluding_Anthropic_Alibaba — original_G01_G13

| Configuration | Spearman | Pearson | Kendall tau-b |
|---|---|---|---|
| opus55x / H0 | 0.923 [0.897, 0.942] | 0.952 [0.940, 0.962] | 0.820 [0.791, 0.843] |
| opus55x / H2 | 0.898 [0.863, 0.923] | 0.932 [0.913, 0.947] | 0.787 [0.751, 0.816] |

| Configuration | Mean absolute error | Bias | Judge mean | Panel mean | Rows / tasks |
|---|---|---|---|---|---|
| opus55x / H0 | 0.059 [0.052, 0.065] | 0.009 [-0.001, 0.019] | 0.756 [0.714, 0.795] | 0.747 [0.710, 0.782] | 591/591 / 50 |
| opus55x / H2 | 0.074 [0.064, 0.085] | 0.035 [0.021, 0.048] | 0.781 [0.741, 0.820] | 0.747 [0.710, 0.782] | 591/591 / 50 |

## T_common_excluding_Anthropic_Alibaba — pooled

| Configuration | Spearman | Pearson | Kendall tau-b |
|---|---|---|---|
| opus55x / H0 | 0.908 [0.880, 0.930] | 0.949 [0.937, 0.959] | 0.804 [0.772, 0.828] |
| opus55x / H2 | 0.884 [0.846, 0.912] | 0.933 [0.915, 0.948] | 0.773 [0.736, 0.804] |

| Configuration | Mean absolute error | Bias | Judge mean | Panel mean | Rows / tasks |
|---|---|---|---|---|---|
| opus55x / H0 | 0.059 [0.052, 0.065] | 0.009 [-0.001, 0.018] | 0.779 [0.742, 0.815] | 0.771 [0.737, 0.802] | 691/691 / 50 |
| opus55x / H2 | 0.071 [0.062, 0.082] | 0.037 [0.025, 0.049] | 0.808 [0.771, 0.842] | 0.771 [0.737, 0.802] | 691/691 / 50 |

## T_excluding_Anthropic — late_G16_G17

| Configuration | Spearman | Pearson | Kendall tau-b |
|---|---|---|---|
| opus55x / H0 | 0.696 [0.573, 0.790] | 0.796 [0.620, 0.892] | 0.590 [0.484, 0.678] |
| opus55x / H2 | 0.615 [0.452, 0.729] | 0.801 [0.631, 0.889] | 0.519 [0.382, 0.622] |

| Configuration | Mean absolute error | Bias | Judge mean | Panel mean | Rows / tasks |
|---|---|---|---|---|---|
| opus55x / H0 | 0.057 [0.045, 0.069] | 0.010 [-0.008, 0.028] | 0.918 [0.884, 0.948] | 0.908 [0.882, 0.932] | 100/100 / 50 |
| opus55x / H2 | 0.058 [0.045, 0.072] | 0.054 [0.040, 0.068] | 0.962 [0.936, 0.984] | 0.908 [0.882, 0.932] | 100/100 / 50 |

## T_excluding_Anthropic — original_G01_G13

| Configuration | Spearman | Pearson | Kendall tau-b |
|---|---|---|---|
| opus55x / H0 | 0.921 [0.894, 0.940] | 0.951 [0.939, 0.961] | 0.815 [0.785, 0.838] |
| opus55x / H2 | 0.896 [0.862, 0.921] | 0.929 [0.910, 0.944] | 0.781 [0.746, 0.809] |

| Configuration | Mean absolute error | Bias | Judge mean | Panel mean | Rows / tasks |
|---|---|---|---|---|---|
| opus55x / H0 | 0.060 [0.053, 0.066] | 0.013 [0.002, 0.024] | 0.756 [0.714, 0.795] | 0.743 [0.706, 0.779] | 591/591 / 50 |
| opus55x / H2 | 0.077 [0.066, 0.088] | 0.039 [0.024, 0.053] | 0.781 [0.741, 0.820] | 0.743 [0.706, 0.779] | 591/591 / 50 |

## T_excluding_Anthropic — pooled

| Configuration | Spearman | Pearson | Kendall tau-b |
|---|---|---|---|
| opus55x / H0 | 0.906 [0.876, 0.928] | 0.948 [0.936, 0.958] | 0.798 [0.765, 0.823] |
| opus55x / H2 | 0.882 [0.845, 0.910] | 0.930 [0.912, 0.945] | 0.767 [0.729, 0.797] |

| Configuration | Mean absolute error | Bias | Judge mean | Panel mean | Rows / tasks |
|---|---|---|---|---|---|
| opus55x / H0 | 0.059 [0.053, 0.065] | 0.012 [0.002, 0.023] | 0.779 [0.742, 0.815] | 0.767 [0.733, 0.799] | 691/691 / 50 |
| opus55x / H2 | 0.074 [0.064, 0.084] | 0.041 [0.028, 0.054] | 0.808 [0.771, 0.842] | 0.767 [0.733, 0.799] | 691/691 / 50 |

## Repeated-score variability

| Configuration | Accepted raw repeats | Repeats per unit | Mean within-unit sample standard deviation |
|---|---|---|---|
| opus55x / H0 | 2069 | {'2': 4, '3': 687} | 0.0199 |
| opus55x / H2 | 2068 | {'2': 5, '3': 686} | 0.0157 |

The 59 source-declared blank candidates are excluded from these primary results. Raw repeats, identifiers and rejected receipts remain in ignored storage; public aggregate evidence is in [cached_descriptive.json](expt_v1/results/cached_descriptive.json), [cache inventory](expt_v1/results/cached_primary_pool_inventory.json), and [fresh prompt proof](expt_v1/results/fresh_prompt_proof.json). There is only one median aggregate per item, so repeated-aggregate variability is not estimable.

The full pool has three base models (Opus, Qwen and Sonnet) and two provider families. The two Qwen harness variants are one base-model cluster. No cross-judge property association, full-pool selection gain, recommendation or human-validation claim follows from this cached subset.
