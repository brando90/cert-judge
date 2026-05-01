## TLDR

- **Exp16** — Run multi-judge certification -> human trend with **Qwen coder** as the primary judge model (`repeats=3`, `median`, `threshold=0.85`).
- **Exp19** — Replot Exp16 detail rows as low-variance diagnostics (monotonicity, alpha breakdown, bug-reversal rates).
- **Exp25 (GM)** — Re-aggregate Exp16 with geometric cert-index `TI_geom = mono^0.4 * stab^0.6` for `avg/pass1/pass2` and compare against baseline.

## Copy-paste prompt for Claude Code

Please run a strict replication of our Codex/Opus evaluation pipeline, but with **Qwen coder** as the primary judge family.

Requirements:
- Complete full pipeline end-to-end: Exp16 -> Exp19 -> Exp25 (avg/pass1/pass2).
- Keep methodology identical: `judge-repeats=3`, `repeat-agg=median`, `threshold=0.85`, `plot-error-bars=on`.
- Use these 8 judges:
  - `llm:<QWEN_MODEL>:P8_STRICT_B`
  - `llm:<QWEN_MODEL>:P4_CHECKLIST`
  - `llm:<QWEN_MODEL>:P1_BASELINE`
  - `llm_bad:<QWEN_MODEL>:BAD_STRINGY`
  - `llm:gpt-4o-mini:P8_STRICT_B`
  - `llm:gpt-4o-mini:P4_CHECKLIST`
  - `editdist:e1:na`
  - `random:r1:na`
- Geometric index definition:
  - `mono = (1 - bug_spearman_r) / 2`
  - `stab = 1 - flip_rate`
  - `TI_geom = exp(0.4*log(mono) + 0.6*log(stab))`
- Print final summary:
  1. Exp16 trend v1/v2 for pass1/pass2/avg
  2. `rho_baseline` vs `rho_geometric` for pass1/pass2/avg
  3. Output paths for all `summary.json` + plots
  4. Any skipped rows

## Shell commands

```bash
export MPLCONFIGDIR=/tmp/mpl

# If your Qwen endpoint is OpenAI-compatible, set these:
# export OPENAI_API_KEY="<your_key>"
# export OPENAI_BASE_URL="<your_openai_compatible_base_url>"

# Primary target requested:
export QWEN_MODEL="${QWEN_MODEL:-qwen-3-coder-instruct}"

# One-step fallback list if the primary model ID is unavailable.
# Keep the first available and continue the full run.
QWEN_LADDER=(
  "qwen-3-coder-instruct"
  "Qwen/Qwen3-Coder"
  "Qwen2.5-Coder-32B-Instruct"
  "Qwen/Qwen2.5-Coder-32B-Instruct"
)

pick_qwen () {
  # If you can query models via your endpoint, add a check here.
  # Default behavior: take first model from ladder; user can override QWEN_MODEL directly.
  echo "${QWEN_MODEL:-${QWEN_LADDER[0]}}"
}

QWEN_MODEL="$(pick_qwen)"
echo "MODEL_USED=${QWEN_MODEL}" | tee experiments/04_veribench_validation/results_exp16_qwen_r3_median.MODEL_USED.txt

# 1) Exp16
python3 experiments/04_veribench_validation/exp16_multi_judge_human_sets.py \
  --judge-repeats 3 \
  --repeat-agg median \
  --threshold 0.85 \
  --plot-error-bars on \
  --cache-tag qwen_full_r3_median \
  --judges "llm:${QWEN_MODEL}:P8_STRICT_B,llm:${QWEN_MODEL}:P4_CHECKLIST,llm:${QWEN_MODEL}:P1_BASELINE,llm_bad:${QWEN_MODEL}:BAD_STRINGY,llm:gpt-4o-mini:P8_STRICT_B,llm:gpt-4o-mini:P4_CHECKLIST,editdist:e1:na,random:r1:na" \
  --out-dir experiments/04_veribench_validation/results_exp16_qwen_r3_median

# 2) Exp19
python3 experiments/04_veribench_validation/exp19_replot_low_variance.py \
  --detail-rows experiments/04_veribench_validation/results_exp16_qwen_r3_median/detail_rows.csv \
  --judge-rows experiments/04_veribench_validation/results_exp16_qwen_r3_median/judge_rows.csv \
  --repeat-agg median \
  --bootstrap-iters 4000 \
  --out-dir experiments/04_veribench_validation/results_exp19_low_variance_replot_qwen

# 3) Exp25 geometric reanalysis (offline)
for LS in avg pass1 pass2; do
  python3 experiments/04_veribench_validation/exp25_plot_baseline_vs_geometric.py \
    --summary-json experiments/04_veribench_validation/results_exp16_qwen_r3_median/summary.json \
    --label-set "$LS" \
    --mono-weight 0.4 \
    --stab-weight 0.6 \
    --out-dir "experiments/04_veribench_validation/results_exp22_geometric_trust_index/qwen_r3_median_mono_stab_40_60_${LS}"
done
```

## Expected outputs

Exp16:
- `experiments/04_veribench_validation/results_exp16_qwen_r3_median/summary.json`
- `.../fig_cert_vs_human_scatter_pass1.png`
- `.../fig_cert_vs_human_scatter_pass2.png`
- `.../fig_cert_vs_human_scatter_avg.png`

Exp19:
- `experiments/04_veribench_validation/results_exp19_low_variance_replot_qwen/fig_main_monotonicity_lowvar.png`
- `.../fig_failure_alpha_variant_breakdown.png`
- `.../fig_failure_bug_reversal_rates.png`

Exp25 / GM:
- `experiments/04_veribench_validation/results_exp22_geometric_trust_index/qwen_r3_median_mono_stab_40_60_avg/summary.json`
- `...pass1/summary.json`
- `...pass2/summary.json`
- plus `fig7_trend_update_baseline_vs_geom.png` in each folder

## Notes

- This is **Qwen-only** prompting (no Opus ladder in this runbook).
- If `QWEN_MODEL` is not recognized by your endpoint, set it explicitly to the exact deployed model ID.
- Keep weak controls (`gpt-4o-mini`, `editdist`, `random`) unchanged for comparability.
