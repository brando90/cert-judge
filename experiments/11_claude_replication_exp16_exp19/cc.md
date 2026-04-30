## TLDR

- **Exp16** — Run the multi-judge certification → human trend pipeline with Claude as the judge (repeats=3, median, threshold=0.85), producing pass1/pass2/avg scatter plots and `summary.json`.
- **Exp19** — Replot the Exp16 detail/judge rows as the low-variance package (monotonicity, alpha-variant breakdown, bug-reversal rates) using 4000 bootstrap iters.
- **Exp22 (GM)** — Re-aggregate the Exp16 summary offline with a geometric cert-index `TI_geom = mono^0.4 · stab^0.6` for each label set (avg/pass1/pass2) and report whether ρ_geometric beats ρ_baseline.

## Model policy (SOTA first — strict)

**Always use the strongest currently available Claude Opus.** As of 2026-04-30 this is `claude-opus-4-7` (released 2026-04-16, knowledge cutoff Jan 2026). Do **not** silently downgrade to older builds (`claude-opus-4-20250514`, `claude-opus-4-6`, etc.) — those are for historical comparison only.

Before you start, web-search "latest Claude Opus model API ID" and confirm whether anything newer than `claude-opus-4-7` (e.g. `claude-opus-4-8`, `claude-opus-5`) has shipped. If yes, use that instead and update the model string everywhere below in lockstep.

- Preferred: `claude-opus-4-7` (Opus 4.7, current SOTA).
- Fallback 1: previous Opus 4.x your key can access (`claude-opus-4-6`, then `claude-opus-4-5`, …).
- Fallback 2: latest Claude Sonnet 4.x.
- Fallback 3: strongest coding-capable model your endpoint exposes.

Use the same model string consistently for `P8_STRICT_B`, `P4_CHECKLIST`, `P1_BASELINE`, and `BAD_STRINGY` so comparisons remain valid. The `gpt-4o-mini` judges are intentionally a *weaker-LLM* comparison baseline — leave them as-is, do not upgrade them to a frontier OpenAI model.

# Claude Code Prompt + Commands (Exp16 + Exp19 replication, plus geometric cert-index reanalysis)

## Copy-paste prompt for Claude Code

Please run a strict replication of our Codex evaluation pipeline using Claude as the judge model, then re-aggregate the resulting Exp16 summary with a geometric cert-index (GM) and compare it against the baseline weighted-sum index.

Goal:

- Reproduce Exp16 (multi-judge certification → human trend with pass1/pass2/avg plots).
- Reproduce Exp19 (low-variance replot package).
- Reanalyze the Exp16 outputs with a geometric trust index (no extra model calls) and report whether GM beats the baseline on each label set (avg, pass1, pass2).
- Keep methodology identical to our reported setup: repeats=3, repeat aggregation=median, threshold=0.85, error bars on.

Use exactly these judge specs (Opus pinned to current SOTA = 4.7; bump in lockstep if a newer Opus exists when you read this):

- llm:claude-opus-4-7:P8_STRICT_B
- llm:claude-opus-4-7:P4_CHECKLIST
- llm:claude-opus-4-7:P1_BASELINE
- llm_bad:claude-opus-4-7:BAD_STRINGY
- llm:gpt-4o-mini:P8_STRICT_B
- llm:gpt-4o-mini:P4_CHECKLIST
- editdist:e1:na
- random:r1:na

Geometric cert-index (GM) definition:

- mono = (1 − bug_spearman_r) / 2
- stab = 1 − flip_rate
- TI_geom = mono^0.4 · stab^0.6 = exp(0.4·log(mono) + 0.6·log(stab))

Run the GM reanalysis on the Exp16 summary for each label set ∈ {avg, pass1, pass2}, using script `experiments/04_veribench_validation/exp25_plot_baseline_vs_geometric.py`.

Write outputs to (note `opus47` tag to keep this run distinct from prior Opus-4 results):

- `experiments/04_veribench_validation/results_exp16_opus47_r3_median`
- `experiments/04_veribench_validation/results_exp19_low_variance_replot_opus47`
- `experiments/04_veribench_validation/results_exp22_geometric_trust_index/opus47_r3_median_mono_stab_40_60_<label_set>` (one dir per label set)

After all runs complete, print:

1. Exp16 trend values (pass1/pass2/avg, v1 and v2) and paths to generated figures.
2. ρ_baseline vs ρ_geometric for avg / pass1 / pass2, and whether the geometric index improved over the baseline in each set.
3. Exact output paths for `summary.json` and `fig7_trend_update_baseline_vs_geom.png` per label set.
4. Whether any rows were skipped.

## Shell commands

```bash
export ANTHROPIC_API_KEY="<your_anthropic_key>"
export MPLCONFIGDIR=/tmp/mpl

# SOTA pin (bump if a newer Opus has shipped — verify before running):
OPUS_MODEL="claude-opus-4-7"

# 1) Exp16 — multi-judge certification → human trend
python3 experiments/04_veribench_validation/exp16_multi_judge_human_sets.py \
  --judge-repeats 3 \
  --repeat-agg median \
  --threshold 0.85 \
  --plot-error-bars on \
  --cache-tag opus47_full_r3_median \
  --judges "llm:${OPUS_MODEL}:P8_STRICT_B,llm:${OPUS_MODEL}:P4_CHECKLIST,llm:${OPUS_MODEL}:P1_BASELINE,llm_bad:${OPUS_MODEL}:BAD_STRINGY,llm:gpt-4o-mini:P8_STRICT_B,llm:gpt-4o-mini:P4_CHECKLIST,editdist:e1:na,random:r1:na" \
  --out-dir experiments/04_veribench_validation/results_exp16_opus47_r3_median

# 2) Exp19 — low-variance replot package
python3 experiments/04_veribench_validation/exp19_replot_low_variance.py \
  --detail-rows experiments/04_veribench_validation/results_exp16_opus47_r3_median/detail_rows.csv \
  --judge-rows experiments/04_veribench_validation/results_exp16_opus47_r3_median/judge_rows.csv \
  --repeat-agg median \
  --bootstrap-iters 4000 \
  --out-dir experiments/04_veribench_validation/results_exp19_low_variance_replot_opus47

# 3) Geometric cert-index reanalysis (GM = mono^0.4 · stab^0.6) for each label set
for LS in avg pass1 pass2; do
  python3 experiments/04_veribench_validation/exp25_plot_baseline_vs_geometric.py \
    --summary-json experiments/04_veribench_validation/results_exp16_opus47_r3_median/summary.json \
    --label-set "$LS" \
    --mono-weight 0.4 \
    --stab-weight 0.6 \
    --out-dir "experiments/04_veribench_validation/results_exp22_geometric_trust_index/opus47_r3_median_mono_stab_40_60_${LS}"
done
```

## Expected key outputs

Exp16:

- `experiments/04_veribench_validation/results_exp16_opus47_r3_median/summary.json`
- `experiments/04_veribench_validation/results_exp16_opus47_r3_median/fig_cert_vs_human_scatter_pass1.png`
- `experiments/04_veribench_validation/results_exp16_opus47_r3_median/fig_cert_vs_human_scatter_pass2.png`
- `experiments/04_veribench_validation/results_exp16_opus47_r3_median/fig_cert_vs_human_scatter_avg.png`

Exp19:

- `experiments/04_veribench_validation/results_exp19_low_variance_replot_opus47/fig_main_monotonicity_lowvar.png`
- `experiments/04_veribench_validation/results_exp19_low_variance_replot_opus47/fig_failure_alpha_variant_breakdown.png`
- `experiments/04_veribench_validation/results_exp19_low_variance_replot_opus47/fig_failure_bug_reversal_rates.png`

Geometric reanalysis (one dir per label_set ∈ {avg, pass1, pass2}):

- `experiments/04_veribench_validation/results_exp22_geometric_trust_index/opus47_r3_median_mono_stab_40_60_<label_set>/summary.json` (must include `rho_baseline` and `rho_geometric`)
- `experiments/04_veribench_validation/results_exp22_geometric_trust_index/opus47_r3_median_mono_stab_40_60_<label_set>/fig7_trend_update_baseline_vs_geom.png`

## Important notes

- **SOTA is non-negotiable.** Before running, web-search the latest Claude Opus model ID. As of 2026-04-30 it is `claude-opus-4-7`. If your key cannot reach 4.7, do *not* fall through to `claude-opus-4-20250514` silently — pick the most recent Opus 4.x your key supports (`claude-opus-4-6`, then `4-5`) and **state in stdout which model was actually used** so the run is auditable.
- This script path uses Anthropic direct API for `claude-*` model names.
- Do **not** use Bedrock-style model IDs (`anthropic....:0`) in `--judges` for this runner.
- If auth fails, verify `ANTHROPIC_API_KEY` is valid for the selected Claude model.
- The geometric reanalysis is **offline**: it reads only the existing Exp16 `summary.json` and makes **no model calls**. If `exp25_plot_baseline_vs_geometric.py` is missing from the repo, fall back to `exp22_geometric_trust_index.py` (which computes the same GM index and writes `summary.json`) and add a small plotting wrapper to produce `fig7_trend_update_baseline_vs_geom.png`.
- Weight convention for the GM: `mono=0.4`, `stab=0.6`, all other components (ident/weak/anti/subtle) set to `0`. Equivalently, pass `--weights "0,0.4,0,0.6,0,0"` to the 6-component runner.
- Optional: Opus 4.7 supports a new `xhigh` reasoning-effort level. If the runner exposes a `--reasoning-effort` knob, you may pass `xhigh` for the four `claude-opus-*` judges; leave `gpt-4o-mini` at default.
