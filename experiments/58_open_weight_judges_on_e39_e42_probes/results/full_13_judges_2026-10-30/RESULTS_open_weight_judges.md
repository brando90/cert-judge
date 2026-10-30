# Experiment 58 results: open-weight judges on experiment 39's frozen probes

Protocol: <https://github.com/brando90/cert-judge/blob/main/experiments/58_open_weight_judges_on_e39_e42_probes/PROTOCOL.md>

**Analysis mode:** FROZEN_ANALYSIS. Collection: VERIFIED. A dry run is a diagnostic, not a frozen-protocol result.

Recorded runtime settings: MATCH; 234/234 harvests present. 0 mismatched or missing setting fields (listed in JSON).

**TLDR:** plain PASS; model-clustered PASS. `C_ms_gold` vs the held-out criterion over 114 units: Spearman 0.460 (permutation p 0.0001); model-clustered p 0.0066 over 10 models.

## Gate (E39's: rho >= 0.45 and p < 0.05)

| Test | n | Spearman | p | 95% CI | Gate |
|---|---:|---:|---:|---|---|
| plain permutation | 114 | 0.460 | 0.0001 | 0.292 to 0.603 | PASS |
| model-clustered | 10 models | 0.487 | 0.0066 | 0.141 to 0.691 | PASS |

Intervals: the imported E39 association resamples judge units; each unit's criterion interval resamples tasks. The clustered association resamples whole models. The frozen E39 code and seeds are unchanged.

## Always reported

| Index | n | Spearman | p | 95% CI |
|---|---:|---:|---:|---|
| PTI_v0_frozen | 97 | n/a | n/a | n/a |
| TI_var_trainnorm | 115 | -0.092 | 0.8314 | -0.260 to 0.082 |

PTI_v0 status counts: {'COMPUTED': 98, 'NOT_COMPUTABLE': 19}

## Scale within family (descriptive)

| Family | Model | Params (B) | Criterion (mean over prompts) | C_ms_gold (mean) |
|---|---|---:|---:|---:|
| gemma3 | gemma3_4b | 4.3 | 0.130 | 0.417 |
| gemma3 | gemma3_12b | 12.2 | 0.214 | 0.297 |
| gemma3 | gemma3_27b | 27.4 | -0.049 | 0.382 |
| gpt-oss | gpt_oss_20b | 20.9 | 0.194 | 0.881 |
| llama3 | llama31_8b | 8.0 | 0.219 | 0.545 |
| llama3 | llama33_70b_awq | 70.6 | 0.055 | 0.419 |
| olmo3 | olmo3_7b | 7.3 | 0.260 | 0.460 |
| olmo3 | olmo3_32b | 32.2 | 0.209 | 0.761 |
| qwen3.6 | qwen36_27b | 27.0 | 0.549 | 0.911 |
| qwen3 | qwen3_4b | 4.0 | 0.293 | 0.715 |
| qwen3 | qwen3_8b | 8.2 | 0.174 | 0.770 |
| qwen3 | qwen3_14b | 14.8 | 0.349 | 0.864 |
| qwen3 | qwen3_32b | 32.8 | 0.454 | 0.842 |

## E42 semantic screen

Verdicts: {'PASS': 19, 'FAIL': 96, 'NOT_COMPUTABLE': 2}; descriptive association with the criterion: {'vacuity': {'n_units': 115, 'spearman_with_criterion': 0.380117717359974}, 'weakening': {'n_units': 115, 'spearman_with_criterion': 0.6000771364872153}, 'overconstraint': {'n_units': 115, 'spearman_with_criterion': 0.5533519713963776}, 'formatting': {'n_units': 115, 'spearman_with_criterion': -0.5356085201447666}}

## TVD-MI (exploratory; does not freeze E49, W-365 is Brando's call)

| Variant | n | Spearman with criterion |
|---|---:|---:|
| repeat_tvd | 114 | 0.007 |
| deletion_tvd_value | 0 | n/a |
| deletion_tvd_information | 0 | n/a |

## Bridge: local Qwen3.6-27B vs hosted (E39)

| Prompt | shared cells | cell Spearman | exact agree | mean absolute difference | crit local | crit hosted | C_ms_gold local | hosted |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D0 | 449 | 0.829 | 0.679 | 0.101 | 0.799 | 0.727 | 0.996 | 0.993 |
| R4 | 497 | 0.881 | 0.696 | 0.076 | 0.750 | 0.830 | 0.990 | n/a |
| H0 | 497 | 0.894 | 0.698 | 0.080 | 0.807 | 0.829 | 0.984 | 0.986 |
| H1 | 498 | 0.900 | 0.743 | 0.067 | 0.792 | 0.857 | 0.989 | 0.987 |
| H2 | 471 | 0.908 | 0.726 | 0.068 | 0.876 | 0.817 | 0.994 | n/a |
| P1 | 499 | 0.877 | 0.725 | 0.067 | 0.504 | 0.462 | 0.794 | 0.658 |
| P4 | 511 | 0.836 | 0.564 | 0.119 | 0.354 | 0.544 | 0.779 | 0.834 |
| P8 | 496 | 0.861 | 0.589 | 0.108 | 0.349 | 0.385 | 0.835 | 0.833 |
| LEX | 487 | 0.899 | 0.729 | 0.028 | -0.288 | -0.288 | 0.837 | 0.839 |

## Prespecified failure sensitivity (protocol section 10)

Flag models with more than 20% incomplete or parse-error cells; denominator is all declared E39 + E42 cells per model. Missing harvests remain unmeasured and are not counted as parse errors.

Flagged models: none. Without these models: plain PASS; model-clustered PASS.

| Model | present / declared harvests | failed / declared cells | failure fraction | flagged |
|---|---:|---:|---:|---|
| qwen3_4b | 18/18 | 6/9927 | 0.001 | False |
| qwen3_8b | 18/18 | 23/9927 | 0.002 | False |
| qwen3_14b | 18/18 | 5/9927 | 0.001 | False |
| qwen3_32b | 18/18 | 8/9927 | 0.001 | False |
| qwen36_27b | 18/18 | 77/9927 | 0.008 | False |
| llama31_8b | 18/18 | 254/9927 | 0.026 | False |
| llama33_70b_awq | 18/18 | 15/9927 | 0.002 | False |
| gemma3_4b | 18/18 | 135/9927 | 0.014 | False |
| gemma3_12b | 18/18 | 61/9927 | 0.006 | False |
| gemma3_27b | 18/18 | 26/9927 | 0.003 | False |
| olmo3_7b | 18/18 | 71/9927 | 0.007 | False |
| olmo3_32b | 18/18 | 3/9927 | 0.000 | False |
| gpt_oss_20b | 18/18 | 203/9927 | 0.020 | False |

Without flagged models, plain: Spearman 0.460 [0.292 to 0.603], p-val=0.0001 (one-sided permutation).

Without flagged models, model-clustered: Spearman 0.487 [0.141 to 0.691], p-val=0.0066 (one-sided permutation).

## Complete frozen panel and cell coverage

Missing units are retained as NOT_COMPUTABLE; n/a is never a zero score. Criterion uses 45 validation + test items, each summarized by the imported E39 median rule.

| Unit | harvest | criterion items | criterion Spearman [95% task CI] | C_ms_gold | PTI-v0 | cell status counts |
|---|---|---:|---|---:|---|---|
| gemma3_12b/D0 | present | 42/45 | 0.741 [0.460 to 0.879] | 0.892 | COMPUTED | {'measured': 455, 'deterministic': 56, 'unmeasured_extraction': 9, 'parse_error': 1} |
| gemma3_12b/H0 | present | 45/45 | 0.016 [-0.446 to 0.470] | 0.125 | COMPUTED | {'measured': 520, 'parse_error': 1} |
| gemma3_12b/H1 | present | 45/45 | -0.041 [-0.507 to 0.421] | 0.000 | COMPUTED | {'measured': 519, 'parse_error': 2} |
| gemma3_12b/H2 | present | 45/45 | 0.115 [-0.289 to 0.492] | 0.120 | COMPUTED | {'measured': 521} |
| gemma3_12b/LEX | present | 45/45 | 0.333 [-0.138 to 0.682] | 0.745 | COMPUTED | {'measured': 521} |
| gemma3_12b/P1 | present | 45/45 | 0.122 [-0.412 to 0.596] | 0.220 | COMPUTED | {'measured': 521} |
| gemma3_12b/P4 | present | 45/45 | 0.150 [-0.397 to 0.595] | 0.352 | COMPUTED | {'measured': 521} |
| gemma3_12b/P8 | present | 45/45 | 0.042 [-0.486 to 0.559] | 0.148 | COMPUTED | {'measured': 521} |
| gemma3_12b/R4 | present | 45/45 | 0.450 [-0.246 to 0.774] | 0.073 | COMPUTED | {'measured': 521} |
| gemma3_27b/D0 | present | 42/45 | 0.689 [0.257 to 0.920] | 0.962 | COMPUTED | {'measured': 456, 'deterministic': 56, 'unmeasured_extraction': 9} |
| gemma3_27b/H0 | present | 45/45 | 0.005 [-0.357 to 0.359] | 0.188 | COMPUTED | {'measured': 520, 'parse_error': 1} |
| gemma3_27b/H1 | present | 45/45 | -0.147 [-0.543 to 0.351] | 0.130 | COMPUTED | {'measured': 519, 'parse_error': 2} |
| gemma3_27b/H2 | present | 45/45 | -0.075 [-0.581 to 0.421] | 0.109 | NOT_COMPUTABLE | {'measured': 509, 'parse_error': 12} |
| gemma3_27b/LEX | present | 45/45 | -0.245 [-0.638 to 0.216] | 0.746 | COMPUTED | {'measured': 521} |
| gemma3_27b/P1 | present | 45/45 | -0.197 [-0.555 to 0.203] | 0.381 | COMPUTED | {'measured': 521} |
| gemma3_27b/P4 | present | 45/45 | -0.235 [-0.662 to 0.278] | 0.414 | COMPUTED | {'measured': 521} |
| gemma3_27b/P8 | present | 45/45 | -0.306 [-0.661 to 0.127] | 0.345 | COMPUTED | {'measured': 520, 'parse_error': 1} |
| gemma3_27b/R4 | present | 45/45 | 0.074 [-0.276 to 0.425] | 0.167 | COMPUTED | {'measured': 521} |
| gemma3_4b/D0 | present | 42/45 | 0.232 [-0.284 to 0.583] | 0.805 | COMPUTED | {'measured': 453, 'deterministic': 56, 'parse_error': 3, 'unmeasured_extraction': 9} |
| gemma3_4b/H0 | present | 45/45 | 0.077 [-0.326 to 0.454] | 0.423 | NOT_COMPUTABLE | {'measured': 518, 'parse_error': 3} |
| gemma3_4b/H1 | present | 45/45 | -0.347 [-0.676 to 0.116] | 0.484 | COMPUTED | {'measured': 517, 'parse_error': 4} |
| gemma3_4b/H2 | present | 45/45 | n/a [n/a] | 0.043 | NOT_COMPUTABLE | {'measured': 513, 'parse_error': 8} |
| gemma3_4b/LEX | present | 45/45 | 0.343 [-0.196 to 0.775] | 0.400 | COMPUTED | {'measured': 521} |
| gemma3_4b/P1 | present | 45/45 | 0.307 [-0.223 to 0.739] | 0.439 | COMPUTED | {'measured': 519, 'parse_error': 2} |
| gemma3_4b/P4 | present | 45/45 | 0.443 [0.175 to 0.646] | 0.331 | COMPUTED | {'measured': 519, 'parse_error': 2} |
| gemma3_4b/P8 | present | 45/45 | 0.251 [-0.189 to 0.599] | 0.517 | COMPUTED | {'measured': 520, 'parse_error': 1} |
| gemma3_4b/R4 | present | 44/45 | -0.268 [-0.553 to 0.150] | 0.313 | NOT_COMPUTABLE | {'measured': 485, 'parse_error': 36} |
| gpt_oss_20b/D0 | present | 42/45 | 0.060 [-0.237 to 0.359] | 0.989 | COMPUTED | {'measured': 452, 'deterministic': 56, 'parse_error': 4, 'unmeasured_extraction': 9} |
| gpt_oss_20b/H0 | present | 45/45 | 0.323 [-0.040 to 0.660] | 0.967 | NOT_COMPUTABLE | {'measured': 507, 'parse_error': 14} |
| gpt_oss_20b/H1 | present | 45/45 | 0.734 [0.464 to 0.877] | 0.969 | COMPUTED | {'measured': 506, 'parse_error': 15} |
| gpt_oss_20b/H2 | present | 45/45 | 0.624 [0.149 to 0.905] | 0.981 | NOT_COMPUTABLE | {'measured': 506, 'parse_error': 15} |
| gpt_oss_20b/LEX | present | 45/45 | -0.004 [-0.306 to 0.297] | 0.788 | COMPUTED | {'measured': 515, 'parse_error': 6} |
| gpt_oss_20b/P1 | present | 45/45 | 0.081 [-0.332 to 0.441] | 0.744 | NOT_COMPUTABLE | {'measured': 503, 'parse_error': 18} |
| gpt_oss_20b/P4 | present | 45/45 | -0.279 [-0.646 to 0.241] | 0.714 | COMPUTED | {'measured': 521} |
| gpt_oss_20b/P8 | present | 45/45 | -0.193 [-0.537 to 0.178] | 0.800 | COMPUTED | {'measured': 514, 'parse_error': 7} |
| gpt_oss_20b/R4 | present | 45/45 | 0.404 [0.064 to 0.649] | 0.974 | NOT_COMPUTABLE | {'parse_error': 5, 'measured': 516} |
| llama31_8b/D0 | present | 42/45 | 0.463 [0.015 to 0.771] | 0.967 | COMPUTED | {'measured': 455, 'deterministic': 56, 'unmeasured_extraction': 9, 'parse_error': 1} |
| llama31_8b/H0 | present | 44/45 | 0.154 [-0.349 to 0.625] | n/a | NOT_COMPUTABLE | {'parse_error': 80, 'measured': 438, 'incomplete': 3} |
| llama31_8b/H1 | present | 45/45 | 0.438 [0.007 to 0.735] | 0.588 | NOT_COMPUTABLE | {'measured': 513, 'incomplete': 3, 'parse_error': 5} |
| llama31_8b/H2 | present | 45/45 | -0.105 [-0.537 to 0.314] | 0.459 | NOT_COMPUTABLE | {'measured': 506, 'incomplete': 15} |
| llama31_8b/LEX | present | 45/45 | 0.335 [0.026 to 0.575] | 0.599 | COMPUTED | {'measured': 521} |
| llama31_8b/P1 | present | 45/45 | 0.238 [-0.197 to 0.589] | 0.476 | COMPUTED | {'measured': 521} |
| llama31_8b/P4 | present | 45/45 | -0.015 [-0.318 to 0.311] | 0.382 | COMPUTED | {'measured': 518, 'parse_error': 3} |
| llama31_8b/P8 | present | 44/45 | -0.112 [-0.467 to 0.281] | 0.348 | COMPUTED | {'measured': 518, 'parse_error': 3} |
| llama31_8b/R4 | present | 45/45 | 0.574 [0.255 to 0.809] | 0.543 | COMPUTED | {'measured': 516, 'parse_error': 5} |
| llama33_70b_awq/D0 | present | 42/45 | 0.125 [-0.388 to 0.651] | 0.978 | COMPUTED | {'measured': 456, 'deterministic': 56, 'unmeasured_extraction': 9} |
| llama33_70b_awq/H0 | present | 45/45 | -0.123 [-0.396 to 0.302] | 0.208 | COMPUTED | {'measured': 521} |
| llama33_70b_awq/H1 | present | 45/45 | 0.251 [0.240 to 0.460] | 0.244 | COMPUTED | {'measured': 521} |
| llama33_70b_awq/H2 | present | 45/45 | n/a [n/a] | 0.208 | COMPUTED | {'measured': 521} |
| llama33_70b_awq/LEX | present | 45/45 | -0.243 [-0.571 to 0.149] | 0.466 | COMPUTED | {'measured': 521} |
| llama33_70b_awq/P1 | present | 45/45 | 0.050 [-0.444 to 0.489] | 0.236 | COMPUTED | {'measured': 521} |
| llama33_70b_awq/P4 | present | 45/45 | 0.193 [-0.322 to 0.576] | 0.554 | COMPUTED | {'measured': 521} |
| llama33_70b_awq/P8 | present | 45/45 | 0.033 [-0.534 to 0.558] | 0.266 | COMPUTED | {'measured': 520, 'parse_error': 1} |
| llama33_70b_awq/R4 | present | 45/45 | 0.156 [-0.315 to 0.574] | 0.606 | COMPUTED | {'measured': 519, 'parse_error': 2} |
| olmo3_32b/D0 | present | 42/45 | 0.093 [-0.321 to 0.446] | 0.966 | COMPUTED | {'measured': 456, 'deterministic': 56, 'unmeasured_extraction': 9} |
| olmo3_32b/H0 | present | 45/45 | 0.122 [-0.363 to 0.542] | 0.757 | COMPUTED | {'measured': 521} |
| olmo3_32b/H1 | present | 45/45 | 0.436 [0.012 to 0.733] | 0.736 | COMPUTED | {'measured': 521} |
| olmo3_32b/H2 | present | 45/45 | 0.409 [-0.043 to 0.755] | 0.757 | COMPUTED | {'measured': 521} |
| olmo3_32b/LEX | present | 45/45 | 0.113 [-0.266 to 0.424] | 0.854 | NOT_COMPUTABLE | {'measured': 520, 'parse_error': 1} |
| olmo3_32b/P1 | present | 45/45 | 0.394 [-0.103 to 0.742] | 0.574 | COMPUTED | {'measured': 521} |
| olmo3_32b/P4 | present | 45/45 | 0.030 [-0.383 to 0.434] | 0.578 | COMPUTED | {'measured': 521} |
| olmo3_32b/P8 | present | 45/45 | -0.104 [-0.454 to 0.269] | 0.721 | COMPUTED | {'measured': 520, 'incomplete': 1} |
| olmo3_32b/R4 | present | 45/45 | 0.391 [-0.041 to 0.702] | 0.901 | COMPUTED | {'measured': 521} |
| olmo3_7b/D0 | present | 42/45 | 0.149 [-0.244 to 0.494] | 0.952 | COMPUTED | {'measured': 442, 'deterministic': 56, 'incomplete': 14, 'unmeasured_extraction': 9} |
| olmo3_7b/H0 | present | 45/45 | 0.626 [0.273 to 0.850] | 0.101 | COMPUTED | {'measured': 516, 'parse_error': 5} |
| olmo3_7b/H1 | present | 45/45 | 0.518 [0.094 to 0.785] | 0.172 | NOT_COMPUTABLE | {'measured': 518, 'parse_error': 3} |
| olmo3_7b/H2 | present | 45/45 | 0.472 [0.052 to 0.775] | 0.200 | NOT_COMPUTABLE | {'measured': 518, 'parse_error': 3} |
| olmo3_7b/LEX | present | 45/45 | 0.011 [-0.379 to 0.387] | 0.872 | NOT_COMPUTABLE | {'measured': 512, 'incomplete': 5, 'parse_error': 4} |
| olmo3_7b/P1 | present | 45/45 | 0.235 [-0.268 to 0.624] | 0.516 | COMPUTED | {'measured': 521} |
| olmo3_7b/P4 | present | 45/45 | 0.184 [-0.097 to 0.439] | 0.396 | COMPUTED | {'measured': 521} |
| olmo3_7b/P8 | present | 45/45 | -0.255 [-0.603 to 0.129] | 0.629 | COMPUTED | {'measured': 514, 'incomplete': 3, 'parse_error': 4} |
| olmo3_7b/R4 | present | 45/45 | 0.402 [0.017 to 0.700] | 0.302 | COMPUTED | {'measured': 521} |
| qwen36_27b/D0 | present | 42/45 | 0.799 [0.525 to 0.922] | 0.996 | COMPUTED | {'measured': 456, 'deterministic': 56, 'unmeasured_extraction': 9} |
| qwen36_27b/H0 | present | 45/45 | 0.807 [0.554 to 0.911] | 0.984 | COMPUTED | {'measured': 516, 'parse_error': 5} |
| qwen36_27b/H1 | present | 45/45 | 0.792 [0.573 to 0.897] | 0.989 | NOT_COMPUTABLE | {'measured': 513, 'parse_error': 8} |
| qwen36_27b/H2 | present | 45/45 | 0.876 [0.712 to 0.938] | 0.994 | NOT_COMPUTABLE | {'measured': 501, 'parse_error': 20} |
| qwen36_27b/LEX | present | 45/45 | -0.288 [-0.563 to 0.001] | 0.837 | COMPUTED | {'measured': 517, 'incomplete': 4} |
| qwen36_27b/P1 | present | 45/45 | 0.504 [0.084 to 0.777] | 0.794 | COMPUTED | {'measured': 520, 'incomplete': 1} |
| qwen36_27b/P4 | present | 45/45 | 0.354 [-0.052 to 0.675] | 0.779 | COMPUTED | {'measured': 521} |
| qwen36_27b/P8 | present | 45/45 | 0.349 [-0.155 to 0.720] | 0.835 | COMPUTED | {'measured': 520, 'incomplete': 1} |
| qwen36_27b/R4 | present | 45/45 | 0.750 [0.441 to 0.894] | 0.990 | COMPUTED | {'measured': 514, 'parse_error': 7} |
| qwen3_14b/D0 | present | 42/45 | 0.496 [0.131 to 0.760] | 0.992 | COMPUTED | {'measured': 456, 'deterministic': 56, 'unmeasured_extraction': 9} |
| qwen3_14b/H0 | present | 45/45 | 0.534 [0.206 to 0.764] | 0.947 | COMPUTED | {'measured': 520, 'parse_error': 1} |
| qwen3_14b/H1 | present | 45/45 | 0.553 [0.207 to 0.794] | 0.952 | COMPUTED | {'measured': 521} |
| qwen3_14b/H2 | present | 45/45 | 0.659 [0.383 to 0.838] | 0.883 | COMPUTED | {'measured': 521} |
| qwen3_14b/LEX | present | 45/45 | -0.246 [-0.601 to 0.133] | 0.813 | COMPUTED | {'measured': 521} |
| qwen3_14b/P1 | present | 45/45 | 0.407 [0.048 to 0.676] | 0.654 | COMPUTED | {'measured': 521} |
| qwen3_14b/P4 | present | 45/45 | 0.246 [-0.063 to 0.534] | 0.747 | COMPUTED | {'measured': 521} |
| qwen3_14b/P8 | present | 45/45 | 0.025 [-0.300 to 0.362] | 0.845 | COMPUTED | {'measured': 521} |
| qwen3_14b/R4 | present | 45/45 | 0.465 [0.102 to 0.738] | 0.940 | COMPUTED | {'measured': 521} |
| qwen3_32b/D0 | present | 42/45 | 0.686 [0.287 to 0.881] | 0.995 | COMPUTED | {'measured': 456, 'deterministic': 56, 'unmeasured_extraction': 9} |
| qwen3_32b/H0 | present | 45/45 | 0.633 [0.291 to 0.840] | 0.922 | COMPUTED | {'measured': 521} |
| qwen3_32b/H1 | present | 45/45 | 0.734 [0.453 to 0.870] | 0.953 | COMPUTED | {'measured': 520, 'parse_error': 1} |
| qwen3_32b/H2 | present | 45/45 | 0.821 [0.615 to 0.931] | 0.935 | COMPUTED | {'measured': 521} |
| qwen3_32b/LEX | present | 45/45 | -0.212 [-0.597 to 0.258] | 0.774 | COMPUTED | {'measured': 521} |
| qwen3_32b/P1 | present | 45/45 | 0.441 [0.099 to 0.702] | 0.606 | COMPUTED | {'measured': 521} |
| qwen3_32b/P4 | present | 45/45 | 0.089 [-0.171 to 0.384] | 0.613 | COMPUTED | {'measured': 521} |
| qwen3_32b/P8 | present | 45/45 | 0.224 [-0.104 to 0.535] | 0.830 | COMPUTED | {'measured': 521} |
| qwen3_32b/R4 | present | 45/45 | 0.665 [0.287 to 0.852] | 0.948 | COMPUTED | {'measured': 521} |
| qwen3_4b/D0 | present | 42/45 | 0.332 [-0.075 to 0.663] | 0.966 | COMPUTED | {'measured': 456, 'deterministic': 56, 'unmeasured_extraction': 9} |
| qwen3_4b/H0 | present | 45/45 | 0.475 [0.046 to 0.731] | 0.752 | COMPUTED | {'measured': 520, 'incomplete': 1} |
| qwen3_4b/H1 | present | 45/45 | 0.452 [0.058 to 0.729] | 0.742 | COMPUTED | {'measured': 521} |
| qwen3_4b/H2 | present | 45/45 | 0.471 [0.036 to 0.776] | 0.729 | COMPUTED | {'measured': 520, 'incomplete': 1} |
| qwen3_4b/LEX | present | 45/45 | 0.231 [-0.163 to 0.550] | 0.863 | COMPUTED | {'measured': 521} |
| qwen3_4b/P1 | present | 45/45 | 0.302 [-0.159 to 0.661] | 0.574 | COMPUTED | {'measured': 520, 'incomplete': 1} |
| qwen3_4b/P4 | present | 45/45 | 0.010 [-0.360 to 0.399] | 0.519 | COMPUTED | {'measured': 521} |
| qwen3_4b/P8 | present | 45/45 | -0.150 [-0.592 to 0.311] | 0.568 | COMPUTED | {'measured': 521} |
| qwen3_4b/R4 | present | 45/45 | 0.512 [0.104 to 0.755] | 0.717 | COMPUTED | {'measured': 521} |
| qwen3_8b/D0 | present | 42/45 | 0.392 [-0.072 to 0.764] | 0.985 | NOT_COMPUTABLE | {'measured': 454, 'deterministic': 56, 'unmeasured_extraction': 9, 'parse_error': 1, 'incomplete': 1} |
| qwen3_8b/H0 | present | 45/45 | 0.234 [-0.033 to 0.556] | 0.888 | NOT_COMPUTABLE | {'measured': 519, 'parse_error': 2} |
| qwen3_8b/H1 | present | 45/45 | 0.344 [-0.160 to 0.711] | 0.818 | COMPUTED | {'measured': 521} |
| qwen3_8b/H2 | present | 45/45 | 0.474 [0.017 to 0.793] | 0.789 | COMPUTED | {'measured': 520, 'parse_error': 1} |
| qwen3_8b/LEX | present | 45/45 | -0.036 [-0.390 to 0.268] | 0.862 | COMPUTED | {'measured': 520, 'incomplete': 1} |
| qwen3_8b/P1 | present | 45/45 | 0.056 [-0.290 to 0.381] | 0.712 | COMPUTED | {'measured': 521} |
| qwen3_8b/P4 | present | 45/45 | -0.159 [-0.541 to 0.286] | 0.436 | COMPUTED | {'measured': 521} |
| qwen3_8b/P8 | present | 45/45 | -0.389 [-0.696 to 0.054] | 0.700 | COMPUTED | {'measured': 521} |
| qwen3_8b/R4 | present | 45/45 | 0.648 [0.323 to 0.857] | 0.739 | COMPUTED | {'measured': 513, 'parse_error': 8} |

### Semantic-screen coverage

| Unit | harvest | verdict | cell status counts |
|---|---|---|---|
| gemma3_12b/D0 | present | FAIL | {'measured': 582} |
| gemma3_12b/H0 | present | FAIL | {'measured': 582} |
| gemma3_12b/H1 | present | FAIL | {'measured': 582} |
| gemma3_12b/H2 | present | FAIL | {'measured': 582} |
| gemma3_12b/LEX | present | FAIL | {'measured': 582} |
| gemma3_12b/P1 | present | FAIL | {'measured': 582} |
| gemma3_12b/P4 | present | FAIL | {'measured': 582} |
| gemma3_12b/P8 | present | FAIL | {'measured': 582} |
| gemma3_12b/R4 | present | NOT_COMPUTABLE | {'measured': 525, 'parse_error': 57} |
| gemma3_27b/D0 | present | FAIL | {'measured': 582} |
| gemma3_27b/H0 | present | FAIL | {'measured': 582} |
| gemma3_27b/H1 | present | FAIL | {'measured': 580, 'parse_error': 2} |
| gemma3_27b/H2 | present | FAIL | {'measured': 574, 'parse_error': 8} |
| gemma3_27b/LEX | present | FAIL | {'measured': 582} |
| gemma3_27b/P1 | present | FAIL | {'measured': 582} |
| gemma3_27b/P4 | present | FAIL | {'measured': 582} |
| gemma3_27b/P8 | present | FAIL | {'measured': 582} |
| gemma3_27b/R4 | present | FAIL | {'measured': 582} |
| gemma3_4b/D0 | present | FAIL | {'measured': 581, 'parse_error': 1} |
| gemma3_4b/H0 | present | FAIL | {'measured': 579, 'parse_error': 3} |
| gemma3_4b/H1 | present | FAIL | {'measured': 581, 'parse_error': 1} |
| gemma3_4b/H2 | present | FAIL | {'measured': 574, 'parse_error': 8} |
| gemma3_4b/LEX | present | FAIL | {'measured': 581, 'parse_error': 1} |
| gemma3_4b/P1 | present | FAIL | {'measured': 581, 'parse_error': 1} |
| gemma3_4b/P4 | present | FAIL | {'measured': 582} |
| gemma3_4b/P8 | present | FAIL | {'measured': 582} |
| gemma3_4b/R4 | present | FAIL | {'measured': 521, 'parse_error': 61} |
| gpt_oss_20b/D0 | present | PASS | {'measured': 578, 'parse_error': 4} |
| gpt_oss_20b/H0 | present | PASS | {'measured': 572, 'parse_error': 10} |
| gpt_oss_20b/H1 | present | PASS | {'measured': 563, 'parse_error': 19} |
| gpt_oss_20b/H2 | present | PASS | {'measured': 567, 'parse_error': 15} |
| gpt_oss_20b/LEX | present | FAIL | {'measured': 568, 'parse_error': 14} |
| gpt_oss_20b/P1 | present | FAIL | {'measured': 556, 'parse_error': 26} |
| gpt_oss_20b/P4 | present | FAIL | {'measured': 578, 'parse_error': 4} |
| gpt_oss_20b/P8 | present | FAIL | {'measured': 565, 'parse_error': 17} |
| gpt_oss_20b/R4 | present | PASS | {'measured': 572, 'parse_error': 10} |
| llama31_8b/D0 | present | FAIL | {'measured': 582} |
| llama31_8b/H0 | present | NOT_COMPUTABLE | {'measured': 504, 'parse_error': 70, 'incomplete': 8} |
| llama31_8b/H1 | present | FAIL | {'measured': 555, 'parse_error': 14, 'incomplete': 13} |
| llama31_8b/H2 | present | FAIL | {'measured': 563, 'incomplete': 18, 'parse_error': 1} |
| llama31_8b/LEX | present | FAIL | {'measured': 582} |
| llama31_8b/P1 | present | FAIL | {'measured': 582} |
| llama31_8b/P4 | present | FAIL | {'measured': 581, 'parse_error': 1} |
| llama31_8b/P8 | present | FAIL | {'measured': 579, 'parse_error': 3} |
| llama31_8b/R4 | present | FAIL | {'measured': 574, 'parse_error': 8} |
| llama33_70b_awq/D0 | present | PASS | {'measured': 582} |
| llama33_70b_awq/H0 | present | FAIL | {'measured': 582} |
| llama33_70b_awq/H1 | present | FAIL | {'measured': 582} |
| llama33_70b_awq/H2 | present | FAIL | {'measured': 582} |
| llama33_70b_awq/LEX | present | FAIL | {'measured': 582} |
| llama33_70b_awq/P1 | present | FAIL | {'measured': 582} |
| llama33_70b_awq/P4 | present | FAIL | {'measured': 582} |
| llama33_70b_awq/P8 | present | FAIL | {'measured': 581, 'parse_error': 1} |
| llama33_70b_awq/R4 | present | FAIL | {'measured': 571, 'parse_error': 11} |
| olmo3_32b/D0 | present | FAIL | {'measured': 581, 'parse_error': 1} |
| olmo3_32b/H0 | present | FAIL | {'measured': 582} |
| olmo3_32b/H1 | present | PASS | {'measured': 582} |
| olmo3_32b/H2 | present | FAIL | {'measured': 582} |
| olmo3_32b/LEX | present | FAIL | {'measured': 582} |
| olmo3_32b/P1 | present | FAIL | {'measured': 582} |
| olmo3_32b/P4 | present | FAIL | {'measured': 582} |
| olmo3_32b/P8 | present | FAIL | {'measured': 582} |
| olmo3_32b/R4 | present | FAIL | {'measured': 582} |
| olmo3_7b/D0 | present | FAIL | {'measured': 573, 'incomplete': 8, 'parse_error': 1} |
| olmo3_7b/H0 | present | FAIL | {'measured': 576, 'parse_error': 6} |
| olmo3_7b/H1 | present | FAIL | {'measured': 580, 'parse_error': 2} |
| olmo3_7b/H2 | present | FAIL | {'measured': 576, 'parse_error': 6} |
| olmo3_7b/LEX | present | FAIL | {'measured': 582} |
| olmo3_7b/P1 | present | FAIL | {'measured': 581, 'parse_error': 1} |
| olmo3_7b/P4 | present | FAIL | {'measured': 582} |
| olmo3_7b/P8 | present | FAIL | {'measured': 577, 'parse_error': 5} |
| olmo3_7b/R4 | present | FAIL | {'measured': 581, 'parse_error': 1} |
| qwen36_27b/D0 | present | FAIL | {'measured': 580, 'parse_error': 2} |
| qwen36_27b/H0 | present | PASS | {'measured': 577, 'parse_error': 5} |
| qwen36_27b/H1 | present | PASS | {'measured': 574, 'parse_error': 8} |
| qwen36_27b/H2 | present | PASS | {'measured': 569, 'parse_error': 13} |
| qwen36_27b/LEX | present | FAIL | {'measured': 581, 'incomplete': 1} |
| qwen36_27b/P1 | present | FAIL | {'measured': 582} |
| qwen36_27b/P4 | present | FAIL | {'measured': 582} |
| qwen36_27b/P8 | present | FAIL | {'measured': 582} |
| qwen36_27b/R4 | present | PASS | {'measured': 580, 'parse_error': 2} |
| qwen3_14b/D0 | present | PASS | {'measured': 579, 'parse_error': 3} |
| qwen3_14b/H0 | present | FAIL | {'measured': 582} |
| qwen3_14b/H1 | present | FAIL | {'measured': 581, 'parse_error': 1} |
| qwen3_14b/H2 | present | FAIL | {'measured': 582} |
| qwen3_14b/LEX | present | FAIL | {'measured': 582} |
| qwen3_14b/P1 | present | FAIL | {'measured': 582} |
| qwen3_14b/P4 | present | FAIL | {'measured': 582} |
| qwen3_14b/P8 | present | FAIL | {'measured': 582} |
| qwen3_14b/R4 | present | PASS | {'measured': 582} |
| qwen3_32b/D0 | present | PASS | {'measured': 579, 'incomplete': 1, 'parse_error': 2} |
| qwen3_32b/H0 | present | PASS | {'measured': 581, 'parse_error': 1} |
| qwen3_32b/H1 | present | FAIL | {'measured': 579, 'parse_error': 3} |
| qwen3_32b/H2 | present | FAIL | {'measured': 582} |
| qwen3_32b/LEX | present | FAIL | {'measured': 582} |
| qwen3_32b/P1 | present | FAIL | {'measured': 582} |
| qwen3_32b/P4 | present | FAIL | {'measured': 582} |
| qwen3_32b/P8 | present | FAIL | {'measured': 582} |
| qwen3_32b/R4 | present | PASS | {'measured': 582} |
| qwen3_4b/D0 | present | PASS | {'measured': 582} |
| qwen3_4b/H0 | present | FAIL | {'measured': 581, 'incomplete': 1} |
| qwen3_4b/H1 | present | FAIL | {'measured': 582} |
| qwen3_4b/H2 | present | FAIL | {'measured': 581, 'incomplete': 1} |
| qwen3_4b/LEX | present | FAIL | {'measured': 582} |
| qwen3_4b/P1 | present | FAIL | {'measured': 582} |
| qwen3_4b/P4 | present | FAIL | {'measured': 581, 'incomplete': 1} |
| qwen3_4b/P8 | present | FAIL | {'measured': 582} |
| qwen3_4b/R4 | present | FAIL | {'measured': 582} |
| qwen3_8b/D0 | present | PASS | {'measured': 582} |
| qwen3_8b/H0 | present | FAIL | {'measured': 582} |
| qwen3_8b/H1 | present | FAIL | {'measured': 582} |
| qwen3_8b/H2 | present | FAIL | {'measured': 582} |
| qwen3_8b/LEX | present | FAIL | {'measured': 582} |
| qwen3_8b/P1 | present | FAIL | {'measured': 582} |
| qwen3_8b/P4 | present | FAIL | {'measured': 582} |
| qwen3_8b/P8 | present | FAIL | {'measured': 581, 'parse_error': 1} |
| qwen3_8b/R4 | present | PASS | {'measured': 574, 'parse_error': 8} |

Per-prompt scale curves, semantic metrics and task intervals, descriptive associations, bridge status counts and all index values are preserved in the adjacent JSON analysis.
