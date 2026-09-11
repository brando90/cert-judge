This folder reproduces Exp16 (multi-judge trend) and Exp19 (low-variance replots) using Claude-compatible judge settings for direct cross-model comparison.

## Model policy (SOTA first)

- Preferred: `claude-opus-4-20250514` (Opus ideal).
- Fallback 1: latest available Claude Sonnet 4.x your account can access.
- Fallback 2: strongest available coding-capable model in your endpoint.

Use the same model string consistently for `P8_STRICT_B`, `P4_CHECKLIST`, `P1_BASELINE`, and `BAD_STRINGY` so comparisons remain valid.

## Commands

```bash
export ANTHROPIC_API_KEY="<your_anthropic_key>"
export MPLCONFIGDIR=/tmp/mpl

python3 experiments/04_veribench_validation/exp16_multi_judge_human_sets.py \
  --judge-repeats 3 \
  --repeat-agg median \
  --threshold 0.85 \
  --plot-error-bars on \
  --cache-tag opus4_full_r3_median \
  --judges "llm:claude-opus-4-20250514:P8_STRICT_B,llm:claude-opus-4-20250514:P4_CHECKLIST,llm:claude-opus-4-20250514:P1_BASELINE,llm_bad:claude-opus-4-20250514:BAD_STRINGY,llm:gpt-4o-mini:P8_STRICT_B,llm:gpt-4o-mini:P4_CHECKLIST,editdist:e1:na,random:r1:na" \
  --out-dir experiments/04_veribench_validation/results_exp16_opus4_r3_median

python3 experiments/04_veribench_validation/exp19_replot_low_variance.py \
  --detail-rows experiments/04_veribench_validation/results_exp16_opus4_r3_median/detail_rows.csv \
  --judge-rows experiments/04_veribench_validation/results_exp16_opus4_r3_median/judge_rows.csv \
  --repeat-agg median \
  --bootstrap-iters 4000 \
  --out-dir experiments/04_veribench_validation/results_exp19_low_variance_replot_opus4
```

## Notes

- `judge_caller.py` uses Anthropic direct API for `claude-*` model names.
- Do not use Bedrock-style model IDs (e.g., `anthropic....:0`) in `--judges` for this script.
