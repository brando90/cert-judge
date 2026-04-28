# EXP20 Corr-Variance Tradeoff

- detail_rows: `experiments/04_veribench_validation/results_exp16_final_robust_r9_median/detail_rows.csv`
- trials per config: 20

## Top configs (avg corr - std)
- gpt-5.3-codex|P4_CHECKLIST | k=3 | mean | avg_corr=0.480 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|P1_BASELINE | k=3 | mean | avg_corr=0.469 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|P1_BASELINE | k=3 | median | avg_corr=0.466 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|P1_BASELINE | k=2 | mean | avg_corr=0.476 ± 0.022 | item_var=0.00133
- gpt-5.3-codex|P1_BASELINE | k=2 | median | avg_corr=0.471 ± 0.020 | item_var=0.00119
- gpt-5.3-codex|BAD_STRINGY | k=3 | mean | avg_corr=0.450 ± 0.001 | item_var=0.00000
- gpt-5.3-codex|P4_CHECKLIST | k=2 | mean | avg_corr=0.464 ± 0.022 | item_var=0.00059
- gpt-5.3-codex|P4_CHECKLIST | k=2 | median | avg_corr=0.460 ± 0.023 | item_var=0.00063

## Top configs (pass2 corr - std)
- gpt-5.3-codex|P4_CHECKLIST | k=3 | mean | pass2_corr=0.374 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|P4_CHECKLIST | k=2 | mean | pass2_corr=0.363 ± 0.024 | item_var=0.00059
- gpt-5.3-codex|P4_CHECKLIST | k=2 | median | pass2_corr=0.353 ± 0.018 | item_var=0.00063
- gpt-5.3-codex|P4_CHECKLIST | k=3 | median | pass2_corr=0.311 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|BAD_STRINGY | k=3 | mean | pass2_corr=0.300 ± 0.001 | item_var=0.00000
- gpt-5.3-codex|BAD_STRINGY | k=3 | median | pass2_corr=0.294 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|P1_BASELINE | k=3 | median | pass2_corr=0.278 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|BAD_STRINGY | k=2 | mean | pass2_corr=0.296 ± 0.019 | item_var=0.00011

## Caveat
- LLM repeats appear to be cached at 3 in this detail file; to evaluate true k>3 LLM behavior, rerun EXP16 with a fresh cache namespace.