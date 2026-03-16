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

Certification experiments (NeurIPS reviewer response, `experiments/02_*`):
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

cd experiments/02_reviewer_response_neurips_math_ai_2026
bash run_all_experiments.sh          # Exp5→Exp1→Exp2→Exp4→Exp3
python utils/make_wandb_report.py    # Plotly charts + full stats
python utils/create_wandb_report_simple.py  # clean W&B leaderboard report
```

Results land in `results/` with per-experiment `summary.json` files.
Judge call results are cached in `results/judge_cache.json` (~800 calls).

### Full JTI evaluation (P1–P7)
```bash
cd experiments/00_overall_cert_judge_metric_with_properties
bash main_overall_judge_score.sh
```

## Repo Structure

```
py_src/cert_judge/
  hsj_scoring.py       — P1–P5 scoring functions, JTI computation
  tvd_mi_tools.py      — TVD-MI information-robustness metric (P5)

experiments/
  00_overall_cert_judge_metric_with_properties/   — full P1–P7 JTI pipeline
  02_reviewer_response_neurips_math_ai_2026/      — certification experiments
    SUMMARY.md                                    — results + next steps
    exp1_hard_identity.py / exp2_hard_monotonicity.py / ...
    utils/  judge_caller.py · metrics.py · variant_generator.py · ...
  03_human_validation/
    claude_code.md     — full code prompt for human-judge agreement study (ICC, next experiment)

paper_latex/
  ICML_2026/           — main.tex (latexmk -pdf main.tex)
  NeurIPS_2025/        — neurips_2025.tex
```

## Certification Thresholds

| Metric | Threshold |
|---|---|
| identity_mean | > 0.90 |
| Spearman ρ (bug level → score) | < −0.50 |
| Weak monotonicity % | > 80% |

`combined_score = identity_mean × (weak_mono_pct / 100)` — perfect judge = 1.00

## Next Experiments

See `experiments/02_reviewer_response_neurips_math_ai_2026/SUMMARY.md` for full details.

1. **Human validation** (`experiments/03_human_validation/`) — ICC(2,1) + Spearman human-vs-judge; code prompt ready
2. **More LLM judges** — Claude 3.5/3.7, Llama 3, Gemini on the same certification protocol
3. **Lean 4 compilation ground truth** — use Lean as binary oracle; AUC-ROC for judge as compiler proxy
