# Folder 09 Auto Report (mean)

- n_items used: 72
- single_best_certified: `claude-sonnet-4-20250514|P8_STRICT_B`
- certified_llm_judges: 7

## Spearman with human labels

| label_set | method | rho | 95% bootstrap CI |
|---|---|---:|---|
| union_avg | `single_best_certified` | 0.044 | [-0.200, 0.274] |
| union_avg | `ens_all_llm_uniform` | 0.281 | [0.038, 0.491] |
| union_avg | `ens_certified_uniform` | 0.281 | [0.038, 0.491] |
| union_avg | `ens_all_llm_certv2_weighted` | 0.278 | [0.034, 0.490] |
| union_avg | `ens_certified_certv2_weighted` | 0.278 | [0.034, 0.490] |

## Pairwise delta (single - ensemble)

| label_set | comparison | delta rho | 95% bootstrap CI |
|---|---|---:|---|
| union_avg | `single_best_certified - ens_all_llm_uniform` | -0.235 | [-0.454, -0.019] |
| union_avg | `single_best_certified - ens_certified_uniform` | -0.235 | [-0.454, -0.019] |
| union_avg | `single_best_certified - ens_all_llm_certv2_weighted` | -0.232 | [-0.451, -0.017] |
| union_avg | `single_best_certified - ens_certified_certv2_weighted` | -0.232 | [-0.451, -0.017] |
