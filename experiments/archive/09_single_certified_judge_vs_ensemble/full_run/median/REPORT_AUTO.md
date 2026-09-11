# Folder 09 Auto Report (median)

- n_items used: 72
- single_best_certified: `claude-sonnet-4-20250514|P8_STRICT_B`
- certified_llm_judges: 7

## Spearman with human labels

| label_set | method | rho | 95% bootstrap CI |
|---|---|---:|---|
| union_avg | `single_best_certified` | 0.103 | [-0.151, 0.338] |
| union_avg | `ens_all_llm_uniform` | 0.259 | [0.012, 0.476] |
| union_avg | `ens_certified_uniform` | 0.259 | [0.012, 0.476] |
| union_avg | `ens_all_llm_certv2_weighted` | 0.252 | [0.003, 0.469] |
| union_avg | `ens_certified_certv2_weighted` | 0.252 | [0.003, 0.469] |

## Pairwise delta (single - ensemble)

| label_set | comparison | delta rho | 95% bootstrap CI |
|---|---|---:|---|
| union_avg | `single_best_certified - ens_all_llm_uniform` | -0.153 | [-0.395, 0.081] |
| union_avg | `single_best_certified - ens_certified_uniform` | -0.153 | [-0.395, 0.081] |
| union_avg | `single_best_certified - ens_all_llm_certv2_weighted` | -0.146 | [-0.384, 0.085] |
| union_avg | `single_best_certified - ens_certified_certv2_weighted` | -0.146 | [-0.384, 0.085] |
