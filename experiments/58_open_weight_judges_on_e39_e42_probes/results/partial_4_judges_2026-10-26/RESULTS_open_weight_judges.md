# Experiment 58 results: open-weight judges on experiment 39's frozen probes

**TLDR:** plain FAIL; model-clustered FAIL. `C_ms_gold` vs the held-out criterion over 35 units: Spearman 0.433 (permutation p 0.0052); model-clustered p 0.3280 over 3 models.

## Gate (E39's: rho >= 0.45 and p < 0.05)

| Test | n | Spearman | p | 95% CI | Gate |
|---|---:|---:|---:|---|---|
| plain permutation | 35 | 0.433 | 0.0052 | 0.120 to 0.676 | FAIL |
| model-clustered | 3 models | 0.399 | 0.3280 | 0.350 to 0.633 | FAIL |

## Always reported

| Index | n | Spearman | p |
|---|---:|---:|---:|
| PTI_v0_frozen | 31 | n/a | n/a |
| TI_var_trainnorm | 36 | 0.159 | 0.1738 |

PTI_v0 status counts: {'COMPUTED': 31, 'NOT_COMPUTABLE': 5}

## Scale within family (descriptive)

| Family | Model | Params (B) | Criterion (mean over prompts) | C_ms_gold (mean) |
|---|---|---:|---:|---:|
| llama3 | llama31_8b | 8.0 | 0.219 | 0.545 |
| qwen3 | qwen3_4b | 4.0 | 0.293 | 0.715 |
| qwen3 | qwen3_8b | 8.2 | 0.174 | 0.770 |
| qwen3 | qwen3_14b | 14.8 | 0.349 | 0.864 |

## E42 semantic screen

Verdicts: {'PASS': 5, 'FAIL': 30, 'NOT_COMPUTABLE': 1}; descriptive association with the criterion: {'vacuity': {'n_units': 36, 'spearman_with_criterion': 0.2768988739803923}, 'weakening': {'n_units': 36, 'spearman_with_criterion': 0.7159337881507201}, 'overconstraint': {'n_units': 36, 'spearman_with_criterion': 0.5505291453109397}, 'formatting': {'n_units': 36, 'spearman_with_criterion': -0.5633083569372201}}

## TVD-MI (exploratory; does not freeze E49, W-365 is Brando's call)

| Variant | n | Spearman with criterion |
|---|---:|---:|
| repeat_tvd | 35 | -0.008 |
| deletion_tvd_value | 36 | 0.401 |
| deletion_tvd_information | 36 | -0.130 |

## Bridge: local Qwen3.6-27B vs hosted (E39)

| Prompt | shared cells | cell Spearman | exact agree | crit local | crit hosted | C_ms_gold local | hosted |
|---|---:|---:|---:|---:|---:|---:|---:|
