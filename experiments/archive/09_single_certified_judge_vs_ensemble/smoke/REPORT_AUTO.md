# Folder 09 Auto Report (smoke)

- n_items used: 72
- single_best_certified: `claude-sonnet-4-20250514|P8_STRICT_B`
- certified_llm_judges: 7

## Spearman with human labels

| label_set | method | rho | 95% bootstrap CI |
|---|---|---:|---|
| union_avg | `single_best_certified` | 0.103 | [-0.140, 0.335] |
| union_avg | `ens_all_llm_uniform` | 0.259 | [0.046, 0.474] |
| union_avg | `ens_certified_uniform` | 0.259 | [0.046, 0.474] |
| union_avg | `ens_all_llm_certv2_weighted` | 0.252 | [0.032, 0.472] |
| union_avg | `ens_certified_certv2_weighted` | 0.252 | [0.032, 0.472] |

## Pairwise delta (single - ensemble)

| label_set | comparison | delta rho | 95% bootstrap CI |
|---|---|---:|---|
| union_avg | `single_best_certified - ens_all_llm_uniform` | -0.167 | [-0.414, 0.088] |
| union_avg | `single_best_certified - ens_certified_uniform` | -0.167 | [-0.414, 0.088] |
| union_avg | `single_best_certified - ens_all_llm_certv2_weighted` | -0.158 | [-0.399, 0.089] |
| union_avg | `single_best_certified - ens_certified_certv2_weighted` | -0.158 | [-0.399, 0.089] |
