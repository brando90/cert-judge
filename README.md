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
