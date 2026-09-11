# EXP35: Aggregation Strategy Sweep

Goal: find human-target aggregations that raise judge-human task Spearman toward 0.7+.

## Top strategies (LLM judges only, by best task Spearman)

| Strategy | Best task rho | Best judge | Meta rho (cert_v2) | n tasks |
| --- | ---: | --- | ---: | ---: |
| `no_calibration|lowvar_0.1_mean` | 1.000 | `claude-opus-4-7|P1_BASELINE` | 0.014 | 6 |
| `participants_no_calibration|lowvar_0.1_mean` | 1.000 | `claude-opus-4-7|P1_BASELINE` | 0.014 | 6 |
| `participants_only|lowvar_0.1_mean` | 1.000 | `claude-opus-4-7|P1_BASELINE` | 0.014 | 6 |
| `all_files|lowvar_0.1_mean` | 0.969 | `claude-opus-4-7|P1_BASELINE` | 0.460 | 11 |
| `all_files|lowvar_0.1_mean_with_old_prompt` | 0.954 | `claude-opus-4-7|P1_BASELINE` | 0.221 | 10 |
| `no_calibration|lowvar_0.1_mean_with_old_prompt` | 0.954 | `claude-opus-4-7|P1_BASELINE` | 0.312 | 10 |
| `participants_no_calibration|lowvar_0.1_mean_with_old_prompt` | 0.954 | `claude-opus-4-7|P1_BASELINE` | 0.312 | 10 |
| `participants_only|lowvar_0.1_mean_with_old_prompt` | 0.954 | `claude-opus-4-7|P1_BASELINE` | 0.312 | 10 |
| `no_calibration|lowvar_0.15_mean` | 0.819 | `labs-leanstral-2603|P1_BASELINE` | -0.145 | 12 |
| `participants_no_calibration|lowvar_0.15_mean` | 0.819 | `labs-leanstral-2603|P1_BASELINE` | -0.145 | 12 |
| `participants_only|lowvar_0.15_mean` | 0.819 | `labs-leanstral-2603|P1_BASELINE` | -0.145 | 12 |
| `all_files|lowvar_0.05_mean` | 0.816 | `claude-opus-4-7|P8_STRICT_B` | 0.480 | 5 |
| `all_files|lowvar_0.05_mean_with_old_prompt` | 0.816 | `claude-opus-4-7|P8_STRICT_B` | 0.480 | 5 |
| `all_files|lowvar_0.15_mean` | 0.802 | `claude-opus-4-7|P1_BASELINE` | 0.275 | 14 |
| `all_files|lowvar_0.15_mean_with_old_prompt` | 0.751 | `claude-opus-4-7|P8_STRICT_B` | 0.460 | 13 |
