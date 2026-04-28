# EXP20 Quick Corr-Variance Summary

Computed from results_exp16_final_robust_r9_median/detail_rows.csv
Important caveat: LLM rows currently have repeat_len=3 due cache reuse; only deterministic baselines have 9 repeats.

Top configs by objective = avg_spearman - 0.5*raw_call_var
- gpt-5.3-codex|P4_CHECKLIST | agg=mean | repeat_len=3 | avg_rho=0.480 | raw_var=0.00368 | bug_rho=-0.791
- gpt-5.3-codex|P1_BASELINE | agg=mean | repeat_len=3 | avg_rho=0.469 | raw_var=0.00746 | bug_rho=-0.807
- gpt-5.3-codex|P1_BASELINE | agg=median | repeat_len=3 | avg_rho=0.466 | raw_var=0.00746 | bug_rho=-0.799
- gpt-5.3-codex|BAD_STRINGY | agg=mean | repeat_len=3 | avg_rho=0.448 | raw_var=0.00068 | bug_rho=-0.682
- gpt-5.3-codex|BAD_STRINGY | agg=median | repeat_len=3 | avg_rho=0.435 | raw_var=0.00068 | bug_rho=-0.702
- gpt-5.3-codex|P4_CHECKLIST | agg=median | repeat_len=3 | avg_rho=0.419 | raw_var=0.00368 | bug_rho=-0.791
- gpt-5.3-codex|P8_STRICT_B | agg=median | repeat_len=3 | avg_rho=0.365 | raw_var=0.00407 | bug_rho=-0.762
- gpt-5.3-codex|P8_STRICT_B | agg=mean | repeat_len=3 | avg_rho=0.356 | raw_var=0.00407 | bug_rho=-0.767