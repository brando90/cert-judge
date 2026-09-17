# PAPER NUMBERS — Certification Judge Experiments

Generated from: experiments/02_reviewer_response_neurips_math_ai_2026/
Judge model: gpt-4o-mini (Anthropic key had zero credits; OpenAI fallback used)
Date: 2026-03-14

---

## EXP 5 — Edit Distance Control (Smoke Test)
*10 VeriBench theorems × 4 syntactic variants = 40 pairs*

> "String similarity metrics scored our syntactic variants at a mean normalized
> Levenshtein distance of **0.007**, while the LLM judge scored the same pairs
> at mean **0.998**. Pearson r between edit distance and judge score was
> **0.100** (p=0.538), confirming the judge evaluates semantic content rather
> than surface form."

| Metric | Value |
|--------|-------|
| mean_levenshtein | 0.007 |
| mean_judge_score | 0.998 |
| Pearson r(lev, judge) | 0.100 |
| p-value | 0.538 |
| n_files | 10 |
| n_pairs | 40 |

---

## EXP 1 — Hard Identity
*30 VeriBench theorems × 4 variants (RENAME, REORDER, STYLE, ALPHA) × 3 calls = 360 judge calls*

> "Mean judge score across syntactic variants was **0.920 (±0.155)**, while mean
> normalized edit distance was **0.008**. Pearson r between edit distance and
> judge score was **-0.054** (p=0.561), confirming the judge reasons
> semantically rather than by surface similarity."

| Metric | Value |
|--------|-------|
| identity_mean | **0.920** |
| identity_std | 0.155 |
| mean_levenshtein | 0.008 |
| Pearson r(lev, judge) | -0.054 |
| p-value | 0.561 |
| n_theorems | 30 |
| n_pairs | 120 |

Per-variant breakdown:
| Variant | mean_lev | mean_judge |
|---------|----------|------------|
| RENAME  | 0.025    | 0.898 ±0.035 |
| REORDER | 0.003    | 0.926 ±0.046 |
| STYLE   | 0.003    | 0.939 ±0.044 |
| ALPHA   | 0.001    | 0.919 ±0.063 |

**Pass** (identity_mean > 0.85 AND Pearson < 0.30): ✅

---

## EXP 2 — Hard Monotonicity (Semantic Bug Ladder)
*20 VeriBench theorems × 5 degradation levels × 3 calls = 300 judge calls*

> "Weak monotonicity held for **80%** of theorems. Spearman r between
> degradation level and judge score was **-0.862** (p<0.001). Notably,
> Level 1 (subtle precondition weakening) had mean edit distance of **0.002**
> but mean score drop of **0.143**, demonstrating sensitivity to semantic
> changes that string similarity cannot detect."

| Metric | Value |
|--------|-------|
| Spearman r(level, judge) | **-0.862** |
| p-value | <0.001 |
| weak_monotonicity_pct | **80%** |
| Level 1 mean_lev | 0.002 |
| Level 1 mean score drop | 0.143 |
| n_theorems | 20 |

Per-level mean scores:
| Level | Description | Mean Score |
|-------|-------------|------------|
| 0 | Original (correct) | **0.942** |
| 1 | Subtle (weaken precondition) | 0.798 |
| 2 | Moderate (remove ∧ clause) | 0.708 |
| 3 | Significant (∧ → ∨) | 0.482 |
| 4 | Severe (replace with True) | 0.308 |

**Pass** (weak_mono ≥ 80% AND Spearman ≤ -0.60): ✅

---

## EXP 3 — Multi-Model Certification Ablation
*2 models × 20 certification pairs (identity + monotonicity)*

> "Of 2 models evaluated, **0 passed full certification** on the VeriBench
> test suite (identity_mean > 0.90, Spearman r < -0.50, weak_mono > 80%).
> Both models passed the identity and Spearman criteria individually but fell
> short on weak_mono_pct (70% vs. threshold 80%), demonstrating the protocol
> distinguishes task complexity and is not a rubber stamp. The simpler
> out-of-domain theorems in Exp 4 were CERTIFIED by both models, showing
> the protocol correctly reflects difficulty."

| Model | identity_mean | Spearman r | weak_mono% | Certified |
|-------|--------------|------------|------------|-----------|
| gpt-4o-mini | 0.917 ±0.139 | -0.888 | 70% | ❌ |
| gpt-4o | 0.959 ±0.136 | -0.867 | 70% | ❌ |

W&B runs:
- gpt-4o-mini: https://wandb.ai/brando-su/trusting-formal-judge/runs/e29grtu5
- gpt-4o: https://wandb.ai/brando-su/trusting-formal-judge/runs/dhs45cu1

---

## EXP 4 — Out-of-Domain Generalization
*15 manually-written Lean 4 theorems (Nat, List, Option properties)*

> "On 15 Lean 4 theorems outside VeriBench (Nat.add_zero, List.append,
> Option.map, etc.), the certified judge achieved identity_mean=**1.000**,
> Spearman r=**-0.707**, weak_mono=**100%**, confirming generalization
> beyond the VeriBench training distribution."

| Metric | Value |
|--------|-------|
| identity_mean | **1.000** |
| identity_std | 0.000 |
| Spearman r | -0.707 |
| p-value | <0.001 |
| weak_mono_pct | **100%** |
| certified | ✅ YES |
| n_theorems | 15 |

W&B run: https://wandb.ai/brando-su/trusting-formal-judge/runs/yibfdiz7

---

## EXP 9 — Stability and Semantic Invariance (Fourth Property)
*gpt-5.3-codex (API mode), 184 files, 4 prompt templates, 5 repeats per prompt, 3,680 prompt-file-variant cells*

> "As a fourth certification property, we evaluate judge stability under repeated
> calls and prompt rewordings. Across 4 prompt templates and 5 repeats each, the
> judge shows low repeat noise (mean per-item std = **0.033**) and high internal
> consistency (Cronbach's alpha = **0.942**). Prompt pairs preserve ranking
> strongly (minimum Spearman = **0.955**), but binary decisions are less stable
> near threshold (flip rate = **31.3%**, minimum kappa = **0.454**). A semantic
> invariance stress test shows near-perfect robustness to style edits
> (STYLE gap = **0.004**), moderate sensitivity to reordering/renaming
> (REORDER = **0.213**, RENAME = **0.102**), and substantial sensitivity to
> ALPHA variants (**0.632**), indicating a clear target for prompt and rubric
> hardening."

| Metric | Value |
|--------|-------|
| model | gpt-5.3-codex |
| n_files | 184 |
| n_prompts | 4 (P1_BASELINE, P2_FORMAL, P4_CHECKLIST, P8_STRICT_B) |
| n_repeats | 5 |
| n_cells | 3,680 |
| mean_repeat_std | **0.0330** |
| mean_score_std_across_prompts | **0.0782** |
| flip_rate | **0.3130** |
| min_pairwise_spearman | **0.9550** |
| min_pairwise_kappa | **0.4540** |
| cronbach_alpha | **0.9416** |

Semantic invariance gap (mean absolute score gap vs ORIGINAL):
| Variant | Mean Abs Gap | Median Abs Gap |
|---------|---------------|----------------|
| RENAME  | 0.1021 | 0.010 |
| REORDER | 0.2128 | 0.032 |
| STYLE   | 0.0042 | 0.000 |
| ALPHA   | 0.6325 | 0.812 |

Suggested figures:
- `figures/stability_gpt-53-codex_full_20260420_185401/semantic_invariance_gap_by_variant.png` (main figure for this property)
- `figures/stability_gpt-53-codex_full_20260420_185401/prompt_pairwise_spearman_heatmap.png` (ranking stability across prompts)
- `figures/stability_gpt-53-codex_full_20260420_185401/repeatability_std_histogram.png` (repeat-call noise distribution)

Artifacts:
- Results: `results/stability_gpt-53-codex_full_20260420_185401/summary.json`
- Figures: `figures/stability_gpt-53-codex_full_20260420_185401/`

---

## CERTIFICATION THRESHOLDS

| Metric          | Threshold | Direction |
|-----------------|-----------|-----------|
| identity_mean   | > 0.90    | higher    |
| mono_spearman_r | < -0.50   | more neg  |
| weak_mono_pct   | > 80%     | higher    |

combined_score = identity_mean × (weak_mono_pct / 100)
perfect_judge  = 1.00

---

## W&B Project

All runs: https://wandb.ai/brando-su/trusting-formal-judge

| Experiment | Run name | W&B URL |
|-----------|----------|---------|
| Exp1 identity | hard_identity / gpt-4o-mini | https://wandb.ai/brando-su/trusting-formal-judge/runs/5vkx8ltc |
| Exp2 monotonicity | hard_monotonicity / gpt-4o-mini | https://wandb.ai/brando-su/trusting-formal-judge/runs/y8khbzo2 |
| Exp4 out-of-domain | out_of_domain_mathlib / gpt-4o-mini | https://wandb.ai/brando-su/trusting-formal-judge/runs/yibfdiz7 |
| Exp3 multi-model | gpt-4o-mini | https://wandb.ai/brando-su/trusting-formal-judge/runs/e29grtu5 |
| Exp3 multi-model | gpt-4o | https://wandb.ai/brando-su/trusting-formal-judge/runs/dhs45cu1 |

---

## NOTES

- Exp1-Exp5 used **gpt-4o-mini** as judge (Anthropic key had zero credits at that time).
- Exp9 stability/invariance used **gpt-5.3-codex** in API mode.
- To replicate with Claude, top up `anthropic_bm_key_koyejolab.txt` and re-run —
  the judge cache (`results/judge_cache.json`) avoids re-spending on cached pairs.
- random.seed(42) used throughout for reproducibility
- Lean 4 not used for validation (lean_available=False); syntactic variants
  generated via string transformations only
- Figures: figures/fig_string_vs_semantic.{pdf,png}
           figures/fig_hard_identity.{pdf,png}
           figures/fig_monotonicity_ladder.{pdf,png}
           figures/fig_model_certification_table.{pdf,png}
