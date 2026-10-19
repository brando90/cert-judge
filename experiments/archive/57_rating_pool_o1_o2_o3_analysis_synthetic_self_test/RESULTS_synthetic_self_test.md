# Rating-pool analysis on synthetic cases

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/57_rating_pool_o1_o2_o3_analysis_synthetic_self_test/RESULTS_synthetic_self_test.md>

**TLDR:** The frozen script matches every reading locked in the protocol. Monotone association PASS, reversed association FAIL, 20 missing units of 51 INCONCLUSIVE. A constant +0.2 offset keeps Spearman at 1 and moves the level: bias +0.2, MAE 0.2, ICC(C,1) 1, ICC(A,1) 0.822. The accept threshold read from the freeze file is 0.901572. No human ratings and no model calls.

| Case | What was constructed | Reading |
|---|---|---|
| 1 | 20 units, screen = criterion | PASS (Spearman 1, lower bound above 0.20, p-val < 0.05) |
| 2 | 20 units, screen = −criterion | FAIL (Spearman −1) |
| 3 | 51 declared, 20 missing, the rest monotone | INCONCLUSIVE |
| 4 | 30 items, judge = human + 0.2 | Spearman 1, bias +0.200, MAE 0.200, means 0.700 vs 0.500, ICC(C,1) 1, ICC(A,1) 0.822 |

An extra count check, not one of the four readings: of 10 units, 5 are accepted at τ = 0.901572 and 2 of those fail, so the false-acceptance rate is 0.40 against a base rate of 0.50.

Draws for the association cases: 10,000, seed 48, experiment 39's `analysis_lib`. Receipt: `results/self_test.json`.

**TLDR-end:** [cert-judge: rating-pool analysis self-test] The script returns the four locked readings, including a +0.2 bias that correlation alone cannot see.
