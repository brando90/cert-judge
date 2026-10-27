# Experiment 62 Stage A: does a label-free score pick the judge that matches humans? (zero model calls)

Caveat first: human ratings are 75 Claude 3.7 Sonnet items only; each unit's human rho is on the 45 val+test items (CI about +/-0.3 per unit); there are no human ratings of frontier-judge outputs until 2026-11-06.

Harness for every row: single-call LLM, no tools (open-weight judge units of experiments 59/60: 10 model families x up to 9 prompts, seed 58, median of 3 samples). N = judge units; 'family' = model. Human rho = Spearman of the unit's item scores with the 3-expert mean on 45 items. Regret = best unit's human rho minus the picked unit's. CIs resample model families (the unit of independence).

Units: 90 have a human rho; every table uses the 87 with all three label-free scores (the common pool), so the rules are compared on the same units (3 qwen36/llama units lack a gold-probe index). Scores: C_ms_gold = frozen label-free gold-probe index; F2_item = agreement with the frontier-judge consensus on the 75 items (no human labels, but it needs frontier-judge calls, so it is not a free, self-contained open-weight selector); F1_probe = probe-cell agreement with the frontier judge.

## Bar (pre-registered in the design Doc)

Success = the picked judge reaches human rho >= 0.75, CI above 0, and clearly beats 0.60 (best label-free single unit of experiment 60). Null = no better than 0.60: keep stacking open-weight judges.

## Table 1. Global pick: one unit chosen from the whole pool 

| rule | N units | picked unit | picked human rho [95% CI] | regret | oracle rho | random-pick mean rho | rank of pick by human rho | meets bar (rho >= 0.75 and CI above 0) | clearly above 0.60 (CI lower bound > 0.60) |
|---|---|---|---|---|---|---|---|---|---|
| C_ms_gold | 87 | qwen36|D0 | 0.727 [0.45, 0.90] | 0.130 | 0.857 (qwen36|H1) | 0.244 | 6 | no (point below 0.75) | no (point 0.727, CI lower bound 0.45 includes 0.60) |
| F2_item | 87 | qwen36|H1 | 0.857 [0.67, 0.93] | 0.000 | 0.857 (qwen36|H1) | 0.244 | 1 | yes | yes (lower bound 0.67) |
| F1_probe | 87 | gpt_oss_20b|H2 | 0.628 [0.25, 0.86] | 0.229 | 0.857 (qwen36|H1) | 0.244 | 14 | no (point below 0.75) | no (point 0.628, CI lower bound 0.25 includes 0.60) |

Oracle over the 87 common-pool units: qwen36|H1 0.857; random pick expectation 0.244.

## Table 2. Does the score rank units like humans? (pooled over units, family-bootstrap CI)

| rule | N units | N families | Spearman(score, human rho) | 95% CI |
|---|---|---|---|---|
| C_ms_gold | 87 | 10 | 0.583 | [0.36, 0.70] |
| F2_item | 87 | 10 | 0.948 | [0.91, 0.96] |
| F1_probe | 87 | 10 | 0.694 | [0.57, 0.78] |

## Table 3. Leave-one-family-out, global pick (drop a model family, pick among the rest; regret and random are within the remaining pool)

| rule | mean human rho of pick | min | max | picks >= 0.75 | mean regret (max) | random-pick mean | distinct picks |
|---|---|---|---|---|---|---|---|
| C_ms_gold | 0.725 | 0.707 | 0.727 | 0/10 | 0.127 (0.130) | 0.244 | qwen36|D0, qwen3_32b|D0 |
| F2_item | 0.842 | 0.707 | 0.857 | 9/10 | 0.010 (0.097) | 0.244 | qwen36|H1, qwen3_32b|D0 |
| F1_probe | 0.638 | 0.628 | 0.727 | 0/10 | 0.213 (0.229) | 0.244 | gpt_oss_20b|H2, qwen36|D0 |

## Table 4. Leave-one-family-out prompt transfer (best prompt by mean score over the OTHER families, applied to the held-out family)

| rule | N families | pick human rho (mean) | oracle prompt | random prompt | regret | gain over random [95% CI] |
|---|---|---|---|---|---|---|
| C_ms_gold | 10 | 0.492 | 0.656 | 0.248 | 0.164 | 0.244 [0.09, 0.40] |
| F2_item | 10 | 0.352 | 0.656 | 0.248 | 0.304 | 0.104 [-0.03, 0.24] |
| F1_probe | 10 | 0.492 | 0.656 | 0.248 | 0.164 | 0.244 [0.09, 0.40] |

## Table 5. Within-family pick (the practical case: which prompt for this model), versus random and oracle

| rule | N families | mean pick rho | mean oracle rho | mean random rho | mean regret [95% CI] | gain over random [95% CI] | permutation p (scores shuffled in family) | families where pick = oracle |
|---|---|---|---|---|---|---|---|---|
| C_ms_gold | 10 | 0.533 | 0.656 | 0.248 | 0.123 [0.03, 0.26] | 0.285 [0.13, 0.42] | 0.0005 | 4/10 |
| F2_item | 10 | 0.614 | 0.656 | 0.248 | 0.042 [0.01, 0.08] | 0.366 [0.30, 0.45] | 0.0001 | 6/10 |
| F1_probe | 10 | 0.474 | 0.656 | 0.248 | 0.182 [0.05, 0.35] | 0.226 [0.05, 0.39] | 0.0056 | 3/10 |

Per family (C_ms_gold): gemma3_27b pick 0.682 / oracle 0.682 / random -0.021; gpt_oss_20b pick 0.628 / oracle 0.678 / random 0.230; llama31_8b pick 0.443 / oracle 0.443 / random 0.113; q25_14b_awq pick 0.564 / oracle 0.564 / random 0.100; q3_30b_a3b_bf16 pick 0.605 / oracle 0.605 / random 0.208; qwen36 pick 0.727 / oracle 0.857 / random 0.502; qwen3_14b pick 0.556 / oracle 0.651 / random 0.393; qwen3_32b pick 0.707 / oracle 0.804 / random 0.462; qwen3_4b pick 0.461 / oracle 0.631 / random 0.286; qwen3_8b pick -0.042 / oracle 0.647 / random 0.208

## Table 6. Rule vs rule (within-family pick, family-clustered paired difference)

| a | b | N families | mean (a - b) human rho | 95% CI |
|---|---|---|---|---|
| C_ms_gold | F2_item | 10 | -0.081 | [-0.19, 0.00] |
| C_ms_gold | F1_probe | 10 | 0.059 | [-0.01, 0.19] |
| F2_item | F1_probe | 10 | 0.140 | [0.01, 0.29] |

## Table 7. Seed retest: pick with the seed-58 score, evaluate on the seed-1058 replicate (families with replicates only)

| rule | family | picked unit | rho seed 58 | rho seed 1058 | best unit rho (seed 1058) | mean unit rho (seed 1058) |
|---|---|---|---|---|---|---|
| C_ms_gold | q25_14b_awq | q25_14b_awq|D0 | 0.564 | 0.590 | 0.590 | 0.094 |
| C_ms_gold | q3_30b_a3b_bf16 | q3_30b_a3b_bf16|D0 | 0.605 | 0.617 | 0.617 | 0.197 |
| C_ms_gold | qwen3_14b | qwen3_14b|D0 | 0.556 | 0.497 | 0.760 | 0.405 |
| C_ms_gold | qwen3_8b | qwen3_8b|D0 | -0.042 | 0.154 | 0.595 | 0.294 |
| F2_item | q25_14b_awq | q25_14b_awq|H1 | 0.462 | 0.319 | 0.590 | 0.094 |
| F2_item | q3_30b_a3b_bf16 | q3_30b_a3b_bf16|D0 | 0.605 | 0.617 | 0.617 | 0.197 |
| F2_item | qwen3_14b | qwen3_14b|H2 | 0.651 | 0.551 | 0.760 | 0.405 |
| F2_item | qwen3_8b | qwen3_8b|H2 | 0.475 | 0.502 | 0.595 | 0.294 |
| F1_probe | q25_14b_awq | q25_14b_awq|D0 | 0.564 | 0.590 | 0.590 | 0.094 |
| F1_probe | q3_30b_a3b_bf16 | q3_30b_a3b_bf16|LEX | -0.024 | 0.084 | 0.617 | 0.197 |
| F1_probe | qwen3_14b | qwen3_14b|H1 | 0.562 | 0.616 | 0.760 | 0.405 |
| F1_probe | qwen3_8b | qwen3_8b|D0 | -0.042 | 0.154 | 0.595 | 0.294 |
