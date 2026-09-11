# EXP20 Corr-Variance Tradeoff

- detail_rows: `results_exp16_final_robust_r9_median/detail_rows.csv`
- trials per config: 2000

## Top configs (avg corr - std)
- gpt-5.3-codex|P4_CHECKLIST | k=3 | mean | avg_corr=0.480 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|P1_BASELINE | k=3 | mean | avg_corr=0.469 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|P1_BASELINE | k=3 | median | avg_corr=0.466 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|BAD_STRINGY | k=3 | mean | avg_corr=0.450 ± 0.001 | item_var=0.00000
- gpt-5.3-codex|P1_BASELINE | k=2 | median | avg_corr=0.466 ± 0.020 | item_var=0.00124
- gpt-5.3-codex|P1_BASELINE | k=2 | mean | avg_corr=0.466 ± 0.021 | item_var=0.00124
- gpt-5.3-codex|BAD_STRINGY | k=3 | median | avg_corr=0.435 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|P4_CHECKLIST | k=2 | mean | avg_corr=0.460 ± 0.026 | item_var=0.00062

## Top configs (pass2 corr - std)
- gpt-5.3-codex|P4_CHECKLIST | k=3 | mean | pass2_corr=0.374 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|P4_CHECKLIST | k=2 | mean | pass2_corr=0.355 ± 0.026 | item_var=0.00062
- gpt-5.3-codex|P4_CHECKLIST | k=2 | median | pass2_corr=0.354 ± 0.027 | item_var=0.00062
- gpt-5.3-codex|P4_CHECKLIST | k=3 | median | pass2_corr=0.311 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|BAD_STRINGY | k=3 | mean | pass2_corr=0.300 ± 0.001 | item_var=0.00000
- gpt-5.3-codex|BAD_STRINGY | k=3 | median | pass2_corr=0.294 ± 0.000 | item_var=0.00000
- gpt-5.3-codex|P4_CHECKLIST | k=1 | median | pass2_corr=0.324 ± 0.045 | item_var=0.00246
- gpt-5.3-codex|P1_BASELINE | k=3 | median | pass2_corr=0.278 ± 0.000 | item_var=0.00000

## Caveat
- LLM repeats appear to be cached at 3 in this detail file; to evaluate true k>3 LLM behavior, rerun EXP16 with a fresh cache namespace.