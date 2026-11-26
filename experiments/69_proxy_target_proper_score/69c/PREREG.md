# PREREG: experiment 69C, formulation ③ versus ④ on the new ratings

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/69_proxy_target_proper_score/69c/PREREG.md>

**Written 11-26-2026 before any 69B forecast existed.** Primary metric is sealed-test Ranked Probability Score (RPS). The comparison follows the proper-score-versus-Pearson question in [judges-dont-need-psychometrics-or-corr experiment 29](https://github.com/brando90/judges-dont-need-psychometrics-or-corr/blob/main/experiments/29_four_objectives_lora_and_shape_control_chaosnli_dices_helpsteer2_start_23Nov2026/PROTOCOL_11-23-2026.md): cross-entropy (CE) and RPS objectives against a Pearson objective, with the checkpoint or selector chosen on held-out validation loss. This run does not train a low-rank adapter. It selects among the native forecasts from 69B and two post-hoc maps of each forecast's expected score. $0 beyond whatever 69B already spent.

## Formulations

Cert-judge formulations, Brando 11-09-2026:

- ④ uses the train tasks only. Fit the map on train. Pick the candidate with the best train score.
- ③ uses train to fit and validation to pick. The test tasks are untouched.

Objectives: RPS (lower better), CE (lower better), and Pearson of the expected score with the artifact mean rating (higher better).

Candidates, for each 69B judge that measured every item in the split: the native 6-class vector; a cumulative-logit CE map of its expected score (`fit_ce_ordinal` in experiment 68); a discretized-Gaussian Pearson map (`fit_pearson_gauss`); and CONST, the train-task marginal.

## Sealed task split

Hash order is `sha256("exp69c|" + task_folder)`, then sorted. The first 10 are train, the next 5 validation, the last 10 test. Assignment:

| Split | Tasks |
|---|---|
| Train | `task_16_certificate_hostname`, `task_05_factorial`, `task_25_maximum_list_element`, `task_14_statistical_quantiles`, `task_10_lower_median`, `task_22_shell_quoting`, `task_15_prime_fibonacci_search`, `task_06_counting_sort`, `task_21_tor_hidden_service`, `task_02_edit_distance` |
| Validation | `task_07_transport_layer_security_downgrade`, `task_01_heap_sort`, `task_17_heapsort_algorithm`, `task_19_string_prefixes`, `task_23_duplicate_characters` |
| Test | `task_09_sum_of_digits`, `task_03_application_entitlements`, `task_11_html_escaping`, `task_12_mean_absolute_deviation`, `task_13_primality_testing`, `task_08_base32_encoding`, `task_20_integer_exponentiation`, `task_24_trusted_platform_module_hash_safe`, `task_04_integer_string_sequence`, `task_18_topological_sorting` |

## Decision

Primary number: test RPS of the selected candidate. ③ wins against ④ on an objective only when `test RPS(③) − test RPS(④)` is negative and the 95% task interval on the 10 test tasks excludes 0 (2,000 draws, seed 69, p-val=n/a). The same rule compares the RPS selector with the Pearson selector. A tie, or an interval that covers 0, goes to ④. CE and TVD are secondary. Spearman is diagnostic. A `DRY_RUN` forecast file does not decide the comparison.
