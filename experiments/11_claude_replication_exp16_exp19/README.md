This folder reproduces Exp16 (multi-judge trend) and Exp19 (low-variance replots) using Claude-compatible judge settings for direct cross-model comparison.

## Commands

```bash
export ANTHROPIC_API_KEY="<your_anthropic_key>"
export MPLCONFIGDIR=/tmp/mpl

python3 experiments/04_veribench_validation/exp16_multi_judge_human_sets.py \
  --judge-repeats 3 \
  --repeat-agg median \
  --threshold 0.85 \
  --plot-error-bars on \
  --cache-tag claude37_full_r3_median \
  --judges "llm:claude-3-7-sonnet-20250219:P8_STRICT_B,llm:claude-3-7-sonnet-20250219:P4_CHECKLIST,llm:claude-3-7-sonnet-20250219:P1_BASELINE,llm_bad:claude-3-7-sonnet-20250219:BAD_STRINGY,llm:gpt-4o-mini:P8_STRICT_B,llm:gpt-4o-mini:P4_CHECKLIST,editdist:e1:na,random:r1:na" \
  --out-dir experiments/04_veribench_validation/results_exp16_claude37_r3_median

python3 experiments/04_veribench_validation/exp19_replot_low_variance.py \
  --detail-rows experiments/04_veribench_validation/results_exp16_claude37_r3_median/detail_rows.csv \
  --judge-rows experiments/04_veribench_validation/results_exp16_claude37_r3_median/judge_rows.csv \
  --repeat-agg median \
  --bootstrap-iters 4000 \
  --out-dir experiments/04_veribench_validation/results_exp19_low_variance_replot_claude37
```

## Notes

- `judge_caller.py` uses Anthropic direct API for `claude-*` model names.
- Do not use Bedrock-style model IDs (e.g., `anthropic....:0`) in `--judges` for this script.
