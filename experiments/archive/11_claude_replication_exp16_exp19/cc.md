## TLDR

- **Exp16** — Run the multi-judge certification → human trend pipeline with Claude as the judge (repeats=3, median, threshold=0.85), producing pass1/pass2/avg scatter plots and `summary.json`.
- **Exp19** — Replot the Exp16 detail/judge rows as the low-variance package (monotonicity, alpha-variant breakdown, bug-reversal rates) using 4000 bootstrap iters.
- **Exp22 (GM)** — Re-aggregate the Exp16 summary offline with a geometric cert-index `TI_geom = mono^0.4 · stab^0.6` for each label set (avg/pass1/pass2) and report whether ρ_geometric beats ρ_baseline.

## Model policy (best-effort SOTA — must finish)

**The experiment is more important than the exact model. Always complete the run.** Try the strongest Opus first; if it is unreachable, walk *one step at a time* down the ladder until something works — but **never abort** and **never silently substitute**. Log every fallback step to stdout and into the run's `summary.json` under a `model_actually_used` field so the result is auditable.

Current SOTA as of 2026-04-30: `claude-opus-4-7` (released 2026-04-16, knowledge cutoff Jan 2026). Before running, web-search "latest Claude Opus model API ID" and use anything newer (e.g. `claude-opus-4-8`, `claude-opus-5`) if it has shipped — update the model string everywhere below in lockstep.

Fallback ladder (try in order, descend by **one rung at a time**, only on confirmed auth/availability failure of the current rung):

1. `claude-opus-4-7` ← preferred (or newer Opus if shipped).
2. `claude-opus-4-6`
3. `claude-opus-4-5`
4. `claude-opus-4-1` (a.k.a. `claude-opus-4-1-20250805`)
5. `claude-opus-4-20250514` (original Opus 4 — last-resort Opus).
6. Latest Claude Sonnet 4.x your key can reach (e.g. `claude-sonnet-4-5`).
7. Strongest coding-capable model your endpoint exposes (record the exact ID).

Rules of fallback:

- **Never skip rungs** — if 4.7 fails, try 4.6 next, not 4.5. Slow descent so you stay as close to SOTA as possible.
- **Never escalate weak baselines.** The `gpt-4o-mini` judges are intentionally the *weaker-LLM* control; do not "upgrade" them to GPT-5+ even if Opus is unavailable.
- **Same Opus model for all four Opus judge slots** (`P8_STRICT_B`, `P4_CHECKLIST`, `P1_BASELINE`, `BAD_STRINGY`) so comparisons remain valid. If you fall back, fall back consistently across all four.
- **Finish the experiment.** Do not return early or pause for permission. Whatever rung the run settles on, complete Exp16 → Exp19 → Exp22-GM end-to-end and produce all expected outputs.
- **Print and persist** the chosen model: at start of run echo `MODEL_USED=<id>`, and at end re-echo plus write it into each `summary.json`.

# Claude Code Prompt + Commands (Exp16 + Exp19 replication, plus geometric cert-index reanalysis)

## Copy-paste prompt for Claude Code

Please run a strict replication of our Codex evaluation pipeline using Claude as the judge model, then re-aggregate the resulting Exp16 summary with a geometric cert-index (GM) and compare it against the baseline weighted-sum index.

**Critical: this experiment must finish end-to-end.** Use SOTA Opus on best-effort (see Model policy above) — if `claude-opus-4-7` is unavailable, descend the fallback ladder one rung at a time (4.6 → 4.5 → 4.1 → 4-20250514 → Sonnet 4.x → next strongest), record the model actually used in stdout and in each `summary.json`, and **complete the full pipeline regardless**. Do not stop, do not ask for confirmation, do not return partial results.

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

# SOTA-first ladder. Try rung 0; only descend one rung on confirmed failure.
# IMPORTANT: never abort the experiment — keep walking down until one works.
OPUS_LADDER=(
  "claude-opus-4-7"          # rung 0: SOTA (or newer Opus if shipped — bump here)
  "claude-opus-4-6"          # rung 1
  "claude-opus-4-5"          # rung 2
  "claude-opus-4-1-20250805" # rung 3
  "claude-opus-4-20250514"   # rung 4: last-resort Opus
  "claude-sonnet-4-5"        # rung 5: drop family only after Opus exhausted
)

pick_opus () {
  for m in "${OPUS_LADDER[@]}"; do
    if curl -sS -o /dev/null -w "%{http_code}" \
         -H "x-api-key: ${ANTHROPIC_API_KEY}" \
         -H "anthropic-version: 2023-06-01" \
         -H "content-type: application/json" \
         -d "{\"model\":\"$m\",\"max_tokens\":1,\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}]}" \
         https://api.anthropic.com/v1/messages | grep -q "^200$"; then
      echo "$m"; return 0
    fi
    echo "[ladder] $m unreachable, trying next rung..." >&2
  done
  echo "[ladder] ERROR: no rung reachable; falling back to first rung anyway so the experiment finishes" >&2
  echo "${OPUS_LADDER[0]}"
}

OPUS_MODEL="${OPUS_MODEL:-$(pick_opus)}"
echo "MODEL_USED=${OPUS_MODEL}" | tee experiments/04_veribench_validation/results_exp16_opus47_r3_median.MODEL_USED.txt

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

- **The experiment must finish.** SOTA is best-effort, not a blocker. Try `claude-opus-4-7` first; if it 401/403/404s, descend the ladder one rung at a time (`4-6` → `4-5` → `4-1` → `4-20250514` → Sonnet 4.x → next strongest coding model). Never abort, never skip rungs, never silently substitute. The pre-flight `pick_opus` shell function in the runbook performs this descent automatically; you may also implement equivalent logic inside the Python runner.
- **Audit trail required.** Every run must echo `MODEL_USED=<id>` to stdout and persist that ID into each `summary.json` (Exp16, Exp22-GM per label set). If multiple rungs were attempted, also log the failure reason for each attempted rung above the chosen one.
- This script path uses Anthropic direct API for `claude-*` model names.
- Do **not** use Bedrock-style model IDs (`anthropic....:0`) in `--judges` for this runner.
- If auth fails, verify `ANTHROPIC_API_KEY` is valid for the selected Claude model.
- The geometric reanalysis is **offline**: it reads only the existing Exp16 `summary.json` and makes **no model calls**. If `exp25_plot_baseline_vs_geometric.py` is missing from the repo, fall back to `exp22_geometric_trust_index.py` (which computes the same GM index and writes `summary.json`) and add a small plotting wrapper to produce `fig7_trend_update_baseline_vs_geom.png`.
- Weight convention for the GM: `mono=0.4`, `stab=0.6`, all other components (ident/weak/anti/subtle) set to `0`. Equivalently, pass `--weights "0,0.4,0,0.6,0,0"` to the 6-component runner.
- Optional: Opus 4.7 supports a new `xhigh` reasoning-effort level. If the runner exposes a `--reasoning-effort` knob, you may pass `xhigh` for the four `claude-opus-*` judges; leave `gpt-4o-mini` at default.

---

## Multi-Model Replication Matrix (Opus + Leanstral + Qwen2.5-Coder)

Use this when you want the **same exact pipeline** run for additional models, not just Opus.

### Goal

Recreate the full result stack for each target model:

1. Exp16 (`results_exp16_<tag>_r3_median`)
2. Exp19 (`results_exp19_low_variance_replot_<tag>`)
3. Exp25/GM for `avg`, `pass1`, `pass2` (`results_exp22_geometric_trust_index/<tag>_mono_stab_40_60_<label>`)
4. Figure-3-style monotonicity panel (`results_exp27_<tag>_fig3_style`)

### Copy-paste prompt for Claude Code (matrix run)

Run the exact same Exp16/Exp19/Exp25/Exp27 pipeline for three judge-model families:

1. Opus (SOTA Claude, with fallback ladder)
2. Leanstral (open model endpoint we have configured)
3. Qwen2.5-Coder-32B-Instruct (open model endpoint we have configured)

Use identical methodology across all families:
- repeats=3
- repeat-agg=median
- threshold=0.85
- error-bars on
- same judge prompts: P8_STRICT_B, P4_CHECKLIST, P1_BASELINE, BAD_STRINGY
- same weak controls: gpt-4o-mini P8/P4 + editdist + random

For each family, produce:
- Exp16 summary + scatter plots
- Exp19 low-variance package
- Exp25 geometric trend plots/summaries for avg/pass1/pass2
- Exp27 figure-3-style monotonicity panel

Do not alter formulas:
- mono = (1 - bug_spearman_r) / 2
- stab = 1 - flip_rate
- TI_geom = exp(0.4*log(mono) + 0.6*log(stab))

At the end, print a compact comparison table:
- model family
- rho_geometric (avg/pass1/pass2)
- rho_baseline (avg/pass1/pass2)
- geometric-better flag for each set
- key monotonicity Spearman for P8/P4/P1 from Exp27 summary

### Shell runbook (matrix)

```bash
export MPLCONFIGDIR=/tmp/mpl

# Required for Claude direct:
export ANTHROPIC_API_KEY="<your_anthropic_key>"

# If Leanstral/Qwen are served via OpenAI-compatible endpoint, export these too:
# export OPENAI_API_KEY="<your_openai_or_router_key>"
# export OPENAI_BASE_URL="<your_openai_compatible_base_url>"

# ---------- 0) pick Opus model ----------
OPUS_LADDER=(
  "claude-opus-4-7"
  "claude-opus-4-6"
  "claude-opus-4-5"
  "claude-opus-4-1-20250805"
  "claude-opus-4-20250514"
  "claude-sonnet-4-5"
)

pick_opus () {
  for m in "${OPUS_LADDER[@]}"; do
    if curl -sS -o /dev/null -w "%{http_code}" \
         -H "x-api-key: ${ANTHROPIC_API_KEY}" \
         -H "anthropic-version: 2023-06-01" \
         -H "content-type: application/json" \
         -d "{\"model\":\"$m\",\"max_tokens\":1,\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}]}" \
         https://api.anthropic.com/v1/messages | grep -q "^200$"; then
      echo "$m"; return 0
    fi
  done
  echo "${OPUS_LADDER[0]}"
}

OPUS_MODEL="${OPUS_MODEL:-$(pick_opus)}"
echo "MODEL_USED_OPUS=${OPUS_MODEL}"

# ---------- 1) set target families ----------
# IMPORTANT: Replace LEANSTRAL_MODEL and QWEN_MODEL with the exact model IDs
# your runner accepts in --judges llm:<MODEL_ID>:<PROMPT>.
LEANSTRAL_MODEL="${LEANSTRAL_MODEL:-leanstral-latest}"
QWEN_MODEL="${QWEN_MODEL:-Qwen2.5-Coder-32B-Instruct}"

declare -a FAMILIES=(
  "opus47:${OPUS_MODEL}"
  "leanstral:${LEANSTRAL_MODEL}"
  "qwen25coder32b:${QWEN_MODEL}"
)

run_family () {
  TAG="$1"
  MODEL_ID="$2"
  echo "=== Running family tag=${TAG} model=${MODEL_ID} ==="

  OUT16="experiments/04_veribench_validation/results_exp16_${TAG}_r3_median"
  OUT19="experiments/04_veribench_validation/results_exp19_low_variance_replot_${TAG}"
  OUT27="experiments/04_veribench_validation/results_exp27_${TAG}_fig3_style"

  python3 experiments/04_veribench_validation/exp16_multi_judge_human_sets.py \
    --judge-repeats 3 \
    --repeat-agg median \
    --threshold 0.85 \
    --plot-error-bars on \
    --cache-tag "${TAG}_full_r3_median" \
    --judges "llm:${MODEL_ID}:P8_STRICT_B,llm:${MODEL_ID}:P4_CHECKLIST,llm:${MODEL_ID}:P1_BASELINE,llm_bad:${MODEL_ID}:BAD_STRINGY,llm:gpt-4o-mini:P8_STRICT_B,llm:gpt-4o-mini:P4_CHECKLIST,editdist:e1:na,random:r1:na" \
    --out-dir "${OUT16}"

  python3 experiments/04_veribench_validation/exp19_replot_low_variance.py \
    --detail-rows "${OUT16}/detail_rows.csv" \
    --judge-rows "${OUT16}/judge_rows.csv" \
    --repeat-agg median \
    --bootstrap-iters 4000 \
    --out-dir "${OUT19}"

  for LS in avg pass1 pass2; do
    python3 experiments/04_veribench_validation/exp25_plot_baseline_vs_geometric.py \
      --summary-json "${OUT16}/summary.json" \
      --label-set "${LS}" \
      --mono-weight 0.4 \
      --stab-weight 0.6 \
      --out-dir "experiments/04_veribench_validation/results_exp22_geometric_trust_index/${TAG}_mono_stab_40_60_${LS}"
  done

  python3 experiments/04_veribench_validation/exp27_plot_claude_opus_monotonicity_figure3.py \
    --detail-rows "${OUT16}/detail_rows.csv" \
    --out-dir "${OUT27}" \
    --repeat-agg median \
    --judge-ids "${MODEL_ID}|P8_STRICT_B,${MODEL_ID}|P4_CHECKLIST,${MODEL_ID}|P1_BASELINE" \
    --title "${MODEL_ID} Monotonicity (Figure-3 style)" \
    --stem "fig3_style_${TAG}_monotonicity"

  echo "DONE family=${TAG}"
}

for ENTRY in "${FAMILIES[@]}"; do
  TAG="${ENTRY%%:*}"
  MODEL="${ENTRY#*:}"
  run_family "${TAG}" "${MODEL}"
done
```

### Expected outputs per family (`<tag>`)

- `results_exp16_<tag>_r3_median/summary.json`
- `results_exp19_low_variance_replot_<tag>/fig_main_monotonicity_lowvar.png`
- `results_exp22_geometric_trust_index/<tag>_mono_stab_40_60_avg/summary.json`
- `results_exp22_geometric_trust_index/<tag>_mono_stab_40_60_pass1/summary.json`
- `results_exp22_geometric_trust_index/<tag>_mono_stab_40_60_pass2/summary.json`
- `results_exp27_<tag>_fig3_style/fig3_style_<tag>_monotonicity.png`

### Notes for Leanstral/Qwen

- If your `judge_caller` routes unknown model prefixes to OpenAI-compatible chat-completions, these IDs work directly.
- If not, map `LEANSTRAL_MODEL` / `QWEN_MODEL` to the exact IDs your endpoint exposes.
- Keep the same control judges (`gpt-4o-mini`, `editdist`, `random`) unchanged for comparability.
