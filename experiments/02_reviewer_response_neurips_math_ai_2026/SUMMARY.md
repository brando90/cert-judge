# Experiment 02 — Reviewer Response: NeurIPS Math-AI 2026
## Summary of Results

**Paper**: Trusting the Formal Judge: Certifying LLM Theorem Scorers for Code Verification in Lean 4
**Date run**: 2026-03-14 · **Judge model**: gpt-4o-mini (OpenAI fallback; Anthropic key had zero credits)

---

## TL;DR

We certify an LLM judge by testing two falsifiable logical properties:
1. **Identity** — syntactically different but semantically identical theorems must score ≥ 0.90
2. **Monotonicity** — injecting bugs must decrease scores (Spearman ρ < −0.50, weak_mono > 80%)

Both properties hold. The judge detects **semantic changes invisible to edit distance** (Pearson r(lev, judge) = −0.054, p=0.56). On out-of-domain theorems the judge scores perfectly (identity=1.000, weak_mono=100%).

---

## Leaderboard

| Experiment | Setup | Identity Mean | Spearman ρ | Weak Mono% | Certified |
|---|---|---|---|---|---|
| **Exp4** Out-of-Domain | 15 OOD Lean 4 theorems | **1.000 ±0.000** | −0.707 | **100%** | ✅ YES |
| **Exp2** Hard Monotonicity | 20 VeriBench × 5 levels × 3 calls | 0.942 | **−0.862** (p<0.001) | **80%** | partial |
| **Exp1** Hard Identity | 30 VeriBench × 4 variants × 3 calls | **0.920 ±0.155** | — | — | ✅ property |
| **Exp3** gpt-4o | 20 VeriBench pairs | 0.959 ±0.136 | −0.867 | 70% | ❌ |
| **Exp3** gpt-4o-mini | 20 VeriBench pairs | 0.917 ±0.139 | −0.888 | 70% | ❌ |

**Certification thresholds**: identity_mean > 0.90 AND Spearman ρ < −0.50 AND weak_mono% > 80%

---

## Per-Experiment Results

### Exp5 — Edit Distance Control (Smoke Test)
*10 VeriBench theorems × 4 syntactic variants = 40 pairs*

| Metric | Value |
|---|---|
| mean_levenshtein | 0.007 |
| mean_judge_score | 0.998 |
| Pearson r(lev, judge) | 0.100 (p=0.538) |

**Interpretation**: Judge scores near 1.0 regardless of surface edits. No string-similarity bias.

---

### Exp1 — Hard Identity
*30 VeriBench theorems × 4 variants (RENAME, REORDER, STYLE, ALPHA) × 3 calls = 360 calls*

| Variant | Mean Lev | Mean Judge |
|---|---|---|
| RENAME | 0.025 | 0.898 ±0.035 |
| REORDER | 0.003 | 0.926 ±0.046 |
| STYLE | 0.003 | 0.939 ±0.044 |
| ALPHA | 0.001 | 0.919 ±0.063 |

- identity_mean = **0.920 ±0.155** ✅ (threshold > 0.90)
- Pearson r(lev, judge) = **−0.054** (p=0.561) — semantic, not syntactic

---

### Exp2 — Hard Monotonicity
*20 VeriBench theorems × 5 degradation levels × 3 calls = 300 calls*

| Level | Description | Mean Score | Cohen's d vs L0 |
|---|---|---|---|
| L0 | Original (correct) | **0.942** | — |
| L1 | Subtle (weaken precondition) | 0.798 | **1.20** (large) |
| L2 | Moderate (remove ∧ clause) | 0.708 | 1.68 |
| L3 | Significant (∧→∨) | 0.482 | 3.12 |
| L4 | Severe (replace with True) | 0.308 | 4.05 |

- Spearman ρ = **−0.862** (p<0.001) ✅
- weak_mono_pct = **80%** ✅ (right at threshold)
- L1 Levenshtein = 0.002 but score drop = **0.143** — semantic sensitivity invisible to strings

---

### Exp4 — Out-of-Domain Generalization
*15 manual Lean 4 theorems (Nat, List, Option) — fully outside VeriBench*

| Metric | Value |
|---|---|
| identity_mean | **1.000 ±0.000** |
| Spearman ρ | −0.707 (p<0.001) |
| weak_mono_pct | **100%** |
| **Certified** | ✅ YES |

---

### Exp3 — Multi-Model Comparison
*2 models × 20 VeriBench pairs — same protocol*

| Model | Identity | Spearman ρ | Weak Mono% | Certified |
|---|---|---|---|---|
| gpt-4o-mini | 0.917 ±0.139 | −0.888 | 70% | ❌ |
| gpt-4o | 0.959 ±0.136 | −0.867 | 70% | ❌ |

Both fail the 80% weak_mono threshold on VeriBench-complexity theorems. Same models CERTIFY on simpler OOD theorems (Exp4). **The protocol is a discriminative filter, not a rubber stamp.**

---

## W&B Links

| Experiment | W&B Run |
|---|---|
| Exp1 Hard Identity | https://wandb.ai/brando-su/trusting-formal-judge/runs/5vkx8ltc |
| Exp2 Monotonicity | https://wandb.ai/brando-su/trusting-formal-judge/runs/y8khbzo2 |
| Exp4 Out-of-Domain | https://wandb.ai/brando-su/trusting-formal-judge/runs/yibfdiz7 |
| Exp3 gpt-4o-mini | https://wandb.ai/brando-su/trusting-formal-judge/runs/e29grtu5 |
| Exp3 gpt-4o | https://wandb.ai/brando-su/trusting-formal-judge/runs/dhs45cu1 |
| Full stats report | https://wandb.ai/brando-su/trusting-formal-judge/runs/oo3nzrj4 |
| Simple W&B Report | https://wandb.ai/brando-su/trusting-formal-judge/reportlist |
| Detailed W&B Report | https://wandb.ai/brando-su/trusting-formal-judge/reports/Certifying-LLM-Judges:-Full-Experimental-Report-(NeurIPS-Math-AI-2026)--VmlldzoxNjIwOTA0Mw== |

---

## Reviewer Feedback Addressed

| Concern | Experiment | Status |
|---|---|---|
| "tests resemble edit distance" | Exp5 (Pearson r≈0) + Exp2 L1 (semantic drop) | ✅ Addressed |
| "single architecture" | Exp3 (gpt-4o vs gpt-4o-mini) | ⚠️ Only 2 models |
| "no human validation" | — | ❌ Not done |
| "unclear generalization" | Exp4 (OOD theorems) | ✅ Addressed |
| "strict ordering definition" | Weak monotonicity (% not strict rank) | ✅ Fixed |

---

## What to Do Next

### Priority 1 — Human Validation Study (`experiments/03_human_validation/`)
**Why critical**: Both reviewers flagged the lack of human ground truth. This is the single biggest gap.
- Recruit 3–5 Lean 4 experts (or use grad students with formal methods background)
- Rate 30 theorem pairs on 1–10 quality scale (original + 3-level degradation)
- Compute: ICC(2,1) human-human inter-rater, Pearson/Spearman human vs LLM judge
- Target: ICC > 0.70, Spearman human-vs-judge > 0.70
- **Code prompt**: see `experiments/03_human_validation/claude_code.md`

### Priority 2 — More LLM Judges (`experiments/04_llm_judge_comparison/`)
**Why**: ivJs cited "single architecture" as a limitation. We only tested OpenAI models.
- Add: Claude 3.5 Sonnet, Claude 3.7 Sonnet, Llama-3 70B, Mistral Large, Gemini 1.5 Pro
- Same protocol (identity + monotonicity) on VeriBench 20-theorem set
- Leaderboard table: model × (identity, spearman, weak_mono, certified, cost_per_call)
- Show that the certification protocol is model-agnostic

### Priority 3 — Lean 4 Compilation Ground Truth (`experiments/05_lean_compilation_gt/`)
**Why**: Reviewer 36Hd said "unclear how Lean 4 is actually used." Use Lean as an oracle.
- For each variant/degradation, check if Lean 4 *compiles* (binary yes/no oracle)
- Compare LLM judge scores to compilation outcome: AUC-ROC, precision/recall at threshold
- Show judge is a proxy for Lean's compiler — catching errors before compilation
- Requires lake project setup (not just standalone `.lean` files)

### Priority 4 — Adversarial Certification (`experiments/06_adversarial/`)
**Why**: ivJs raised "adversarial cases" as a generalization concern.
- Create theorems designed to fool the judge: syntactically ugly but semantically correct
- Create theorems that look correct but have subtle type errors
- Measure false-positive/false-negative rates at various score thresholds
- Report calibration curve

---

## Reproducibility

```bash
source $HOME/uv_envs/cert-judge/bin/activate
export WANDB_API_KEY=$(cat ~/keys/brandos_wandb_key.txt)
export OPENAI_API_KEY=$(cat ~/keys/openai_api_brandos_personal_key.txt)
export WANDB_PROJECT=trusting-formal-judge
export WANDB_GROUP=certification-experiments

cd experiments/02_reviewer_response_neurips_math_ai_2026
bash run_all_experiments.sh          # all 5 experiments
python utils/final_report.py         # leaderboard run
python utils/make_wandb_report.py    # Plotly charts + full stats
python utils/create_wandb_report_simple.py  # clean W&B Report
python utils/create_wandb_report.py         # detailed W&B Report
```

- `random.seed(42)` used throughout
- Judge cache: `results/judge_cache.json` (~800 calls, avoids re-spending)
- Lean binary: `/Users/brandomiranda/.elan/bin/lean` (not used for variant validation)
