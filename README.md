# Certifying LLM Judges for Lean 4 Theorem Scoring

> **Paper**: *Trusting the Formal Judge: Certifying LLM Theorem Scorers for Code Verification in Lean 4*
> Submitted to ICML 2026 · NeurIPS 2025 Math-AI Workshop

## What this is

Formal proof assistants (Lean 4, Coq) verify that a *proof is correct*, but they cannot verify whether an agent proved the *right* theorem — the specification adequacy problem. This repo provides an **LLM-based judge** that scores AI-generated Lean 4 theorems for correctness, completeness, and semantic alignment with a reference implementation, along with a **certification protocol** that verifies the judge's trustworthiness before deployment.

**Core idea**: a judge is only trustworthy if it satisfies falsifiable logical properties:
- **P1 Reflexivity** — identical inputs yield the maximum score
- **P2 Monotonicity (bugs)** — scores decrease as semantic bugs are injected
- **P3 Monotonicity (specs)** — scores decrease as specifications are removed

We verify these properties via scripted perturbations and rank-correlation tests (Pearson r, Spearman ρ, Kendall τ), producing a **Judge Trust Index (JTI)** that summarises the judge's reliability in [0, 1].

## Key Results

| Property | Metric | Value |
|---|---|---|
| Reflexivity (P1) | R² | **1.000** |
| Monotonicity to bugs (P2) | Pearson r | **−0.973** |
| Monotonicity to missing specs (P3) | Pearson r | **−0.979** |
| Monotonicity (Spearman ρ) | both ladders | **−0.985** |
| VeriBench: agentic vs. baseline | judge score | **0.615 vs. 0.470** |

Certification experiments (NeurIPS reviewer response, `experiments/archive/02_neurips_reviews/`):
- Identity mean on 30 VeriBench theorems × 4 syntactic variants: **0.920 ±0.155**
- Spearman ρ on 5-level bug ladder: **−0.862** (p<0.001) · Weak monotonicity: **80%**
- Out-of-domain (15 manual Lean 4 theorems): identity=**1.000**, weak_mono=**100%**, **CERTIFIED ✅**

W&B runs: [project](https://wandb.ai/brando-su/trusting-formal-judge) · [leaderboard report](https://wandb.ai/brando-su/trusting-formal-judge/reports/Certifying-LLM-Judges-—-Leaderboard--VmlldzoxNjIwOTE0OA==) · [full stats report](https://wandb.ai/brando-su/trusting-formal-judge/reports/Certifying-LLM-Judges:-Full-Experimental-Report-(NeurIPS-Math-AI-2026)--VmlldzoxNjIwOTA0Mw==)

## Setup

```bash
# Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh && source $HOME/.local/bin/env

# Create env and install
uv venv $HOME/uv_envs/cert-judge
source $HOME/uv_envs/cert-judge/bin/activate
cd ~/cert-judge && uv pip install -e . && uv sync --active
```

API keys expected at:
```
~/keys/openai_api_brandos_personal_key.txt
~/keys/anthropic_bm_key_koyejolab.txt
~/keys/brandos_wandb_key.txt
```

## Running Experiments

### Certification protocol (NeurIPS reviewer response)
```bash
source $HOME/uv_envs/cert-judge/bin/activate
export OPENAI_API_KEY=$(cat ~/keys/openai_api_brandos_personal_key.txt)
export WANDB_API_KEY=$(cat ~/keys/brandos_wandb_key.txt)

cd experiments/archive/02_neurips_reviews
bash run_all_experiments.sh          # Exp5→Exp1→Exp2→Exp4→Exp3
python utils/make_wandb_report.py    # Plotly charts + full stats
python utils/create_wandb_report_simple.py  # clean W&B leaderboard report
```

Results land in `results/` with per-experiment `summary.json` files.
Judge call results are cached in `results/judge_cache.json` (~800 calls).

### Full JTI evaluation (P1–P7)
```bash
cd experiments/archive/00_overall_cert_judge_metric_with_properties
bash main_overall_judge_score.sh
```

## Repo Structure

- `experiments/`: active work only, plus shared label data. See [the current index](experiments/README.md).
- `experiments/archive/`: completed, superseded, and parked studies, including the recent proxy-validation results.
- `py_src/cert_judge/`: reusable scoring and plotting code.
- `paper_latex/ICLR_2027_submission/`: active manuscript.

Check for obsolete local folders after pulling:

```bash
python3 py_src/cert_judge/experiment_layout.py --check
```

Use `--reconcile` to preserve and relocate ignored leftovers safely.

## Certification Thresholds

| Metric | Threshold |
|---|---|
| identity_mean | > 0.90 |
| Spearman ρ (bug level → score) | < −0.50 |
| Weak monotonicity % | > 80% |

`combined_score = identity_mean × (weak_mono_pct / 100)` — perfect judge = 1.00

## Historical follow-up suggestions

See `experiments/archive/02_neurips_reviews/SUMMARY.md` for full details.

1. **Human validation** (`experiments/archive/03_human_validation/`) — ICC(2,1) + Spearman human-vs-judge; code prompt ready
2. **More LLM judges** — Claude 3.5/3.7, Llama 3, Gemini on the same certification protocol
3. **Lean 4 compilation ground truth** — use Lean as binary oracle; AUC-ROC for judge as compiler proxy

## Known inconsistencies and fixes (Nov 20 2026)

Check of the CertJudge validation metric (TI_var against human alignment, Spearman 0.833 / 0.905 / 0.738). No paper source was edited and no model was called.

| Item | Finding | Source file | What is open |
| --- | --- | --- | --- |
| Data behind 0.833 / 0.905 / 0.738 | Codex panel, 8 judge configurations (4 gpt-5.3-codex prompts, 2 gpt-4o-mini prompts, edit distance, random), 72 rated pairs from 24 tasks. x = TI_var per judge; y = each judge's own Spearman between its score and the human label, avg of two passes / pass1 / pass2 labels. Reproduced to 3 decimals (0.833333 / 0.904762 / 0.738095). | `experiments/archive/04_veribench_validation/results_exp28_varaware_codex_{avg,pass1,pass2}_newindex/judge_trust_vector.csv`; per-item scores in `results_exp16_final_robust_r9_median/detail_rows.csv`; labels `data/ethan_human_scores_*.tsv`; `experiments/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/results/G0_reproduction.json` | The labels are one annotator's two superseded old-prompt passes (pass names swapped), so n = 8 judges rests on one rater (experiment 41, REPORT.md). |
| Re-score with proper scoring rules (RPS / CE / TVD) | Possible on CPU from saved files, but only through a construction. Saved: per-item judge scores in [0,1] with 3 repeats (not a distribution over the 0-5 rating levels); per-item human rating lists (2 ratings from one annotator, or 4-5 ratings from VeriBench participants 1-5). Judge distribution = repeats binned to 0..5, Laplace alpha 0.5; human distribution = empirical ratings; metric code as in trustworthy-theorem-judges experiment 22. Codex panel, n = 8 judges, Spearman of TI_var against minus mean loss: RPS -0.571, CE -0.095, TVD -0.571 (72 items, paper's two passes); scalar Spearman on the same setup +0.833. With 4-5 VeriBench ratings (60 items): RPS -0.571, CE -0.119, TVD -0.405. Claude Opus and Qwen3-Coder panels are in the output file. | `experiments/archive/51_certjudge_rescore_rps_ce_tvd_nov2026/rescore_proper.py` and `rescore_proper_output.txt` (python 3.11.17, scipy 1.17.1, numpy 2.4.6, CPU, zero model calls) | The judges emit uncalibrated scalar scores on a 0-1 scale, not forecasts of the human rating distribution, so RPS/CE reflect scale mismatch as much as ranking; n = 8 and exact permutation p is 0.15 or higher for Codex. A native distributional judge would need new calls (not run). Which metric to defend is undecided. |
| Failure rates for removed specs / injected bugs | Bug side is reported per judge as ladders with at least one local score increase (a reversal), 24 ladders each. Codex panel: baseline 0/24, checklist 0/24, strict 4/24, lexical 20/24, GPT-4o-mini strict 18/24, GPT-4o-mini checklist 16/24, edit distance 24/24, random 24/24. Opus and Qwen counts are in the saved CSVs (e.g. Opus lexical 17/24, Qwen strict 1/24). Spec-removal (P3) is not measured per judge: "The eight-configuration panels contain rewrite probes and bug ladders but no missing-specification ladders." | `paper_latex/ICLR_2027_submission/05_experiments.tex` lines 23, 46-49, 116-125; `990_appendix_additional_results.tex:9`; CSVs `experiments/archive/04_veribench_validation/results_exp19_low_variance_replot*/bug_reversal_rates.csv` | The older NeurIPS draft and the TMLR PDF (10994) report a missing-spec weak monotonicity of 89.1% (GPT-5.3-Codex only, 920 points, aggregate, not per judge: `paper/neurips2026/main.tex:244-245`) and BAD_STRINGY weak monotonicity 12.5%; the ICLR draft says P3 is unmeasured. The two statements need reconciling. No per-judge spec-removal violation rate is saved. |
| Proper-scoring follow-up (`11-24-2026`) | Follow-up analyses on CPU ($0 API spend, zero model calls) cross-checked Experiment 67 (`247` live non-`A1` VeriBench ratings across `100` files / `25` tasks; QWK `0.75–0.88`; `0/100` SHA-256 overlap with frozen `64_cert_judge_nov6_confirmatory_test_setN_preregistration`, raw legacy paper series negative on corrected labels and `CE_fit` indistinguishable from `CONST` `0.1737` RPS) and expanded canonical proper scoring (`RPS`, `CE`, `TVD`, `ICC(A,1)`) to signal-bearing panels: `63_judge_optimization_arms_prompt_sft_rl_qwen3_8b` (`rl_grpo` Spearman +0.543 yet CE 5.56 vs CONST 1.80, p=0.0039; `human_mix_sft` beats `teacher_only_sft` on `expert3` RPS p=0.0332 & CONST p=0.0312) and `39_label_free_proxy_index_train_val_test_over_judge_families` (`C_ms_gold` test_llm Spearman +0.675 with CE-cal TVD p=0.0042, within-family p=0.0243; `TI_var` -0.255). | `experiments/67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/RESULTS.md`; `experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/RESULTS_proper_scoring_expansion_11-24-2026.md` | No paper `.tex` claims altered (paper framing awaits Brando's call once fresh judge scores on `N=100` / open-weight panels arrive after the 10-15-2026 spending pause or via free local GPUs). |
| Proper-scoring proxy-target alignment & selection (`Exp 70`, `11-26-2026`) | Replaced double-correlation proxy evaluation with proper-scoring targets (`RPS`, `CE`, `TVD`, `Brier`, `ICC(A,1)`), decision-theoretic regret (`Top-1`, `Subpool-10`, `LOFO`, `UWA_RPS`, held-out `Beat-CONST Meta-Brier/RMSE`), and label-free proper-scoring behavioral proxies (`P_e42_fullcov_brier`, `P_e42_strict_brier`, `P_e42_probe_rps`, `P_e39_fullcov_brier`, `P_dsti_proper`). Live VeriBench Sheets remain at `250` non-`A1` ratings (`33/33` Sheets unchanged, `CONST_loto RPS=0.0698`, `74.0%` score-5 ceiling, matching `69_proxy_target_proper_score` `N250`). On `E39+E42` (`n=60`), `C_ms_gold` is hijacked on `+ctrl` (`Top-1 ce_cal regret=0.0390`, `raw=0.1243`) and drops `qwen36|H2`/`R4`, while `P_e42_probe_rps` reaches `UWA=0.8614`/`0.9173` and `P_e42_strict_brier` reaches `Meta-Brier=0.0549` (vs `0.256`); on `E60 seed1` (`n=36`), `P_e39_fullcov_brier` beats `C_ms_gold` (`UWA=0.8514` vs `0.6164` `raw`); `ctl|editdist` (`0.8195`) exposes change-detector loophole (`$0` API spend, CPU-only + read-only public Sheets). | `experiments/70_proper_scoring_proxy_target_alignment_and_selection_start_26Nov2026/results.md`; `experiments/70_proper_scoring_proxy_target_alignment_and_selection_start_26Nov2026/derivation/proxy_target_proper_scoring_derivation.pdf`; `latex/mega_tech_report.pdf` | Fresh probes for `P8_STRICT_B` and new `N=100` judge calls remain paused (`10-15-2026` spend pause); Drive/Gmail MCP connectors returned `Unauthorized` (GDoc companion staged locally; SMTP email used). |
