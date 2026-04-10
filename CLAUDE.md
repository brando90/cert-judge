# Claude Code: read `~/agents-config/INDEX_RULES.md` for all agent documentation and routing.
# If `~/agents-config/` is not present, clone it: `git clone https://github.com/brando90/agents-config.git ~/agents-config`

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

`cert-judge` is a certification framework for LLM-based judges used in formal verification (Lean 4 theorem scoring). It measures judge reliability through seven properties (P1–P7) and combines them into a **Judge Trust Index (JTI)**. The judge scores how well AI-generated Lean 4 theorems align with a reference implementation.

## Environment Setup

Uses `uv` for environment management (not pip/conda):

```bash
# One-time setup
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv venv $HOME/uv_envs/cert-judge
source $HOME/uv_envs/cert-judge/bin/activate
cd ~/cert-judge && uv pip install -e . && uv sync --active
```

Some dependencies (`vllm`, `sglang`, `unsloth`, `flash-attn`) are Linux-only and excluded on macOS via `pyproject.toml` markers.

## Running Evaluations

The main entry point is `experiments/00_overall_cert_judge_metric_with_properties/`:

```bash
# Run via shell wrapper (recommended — sets all paths/env vars)
cd experiments/00_overall_cert_judge_metric_with_properties
bash main_overall_judge_score.sh

# Or directly with python fire CLI
python main_overall_judge_score.py \
    --mode online \
    --eval_mode hsj_real \
    --claude_dotenv_path /path/to/.env \
    --judge_prompt_temp_path /path/to/prompt.txt \
    --max_score 30 \
    --paths_p1 /path/to/dir1 /path/to/dir2 \
    --path_p2 /path/to/bug_ladder \
    --path_p3 /path/to/missing_spec_ladder \
    --num_llm_judge_calls_per_file_pair 7
```

P5, P6, P7 can be toggled via CLI flags. WandB is used for experiment tracking.

## Architecture

### Core Package: `py_src/cert_judge/`

**`hsj_scoring.py`** — Primary scoring logic:
- `compute_p1_identity()`, `compute_p2_or_p3_ordering_auc()`, `compute_p4_stability()`, `compute_p5_tvd_mi()` — individual property scores in [0,1]
- `compute_jti()` — weighted mean of P1–P7 into a single trust index
- `IsotonicCalibrator` — monotone regression calibrator (PAV algorithm) for aligning judge/MI scores
- `compute_hsj_scores()` — fusion formula: `Q = (1-α)*S_unsup + α*JTI*S_sup` blending unsupervised MI signal with judge scores

**`tvd_mi_tools.py`** — TVD-MI information robustness metric:
- `tvd_mi_from_critic()` — Youden's J (TPR+TNR-1) from categorical labels
- `per_item_auc_macro()`, `tamper_suite_report()` — P5 sub-metrics

**`cert_judge_2/p5_metric.py`** — Extended P5 implementation with `P5Inputs` and `P5Report` dataclasses.

### Main Evaluation Script: `experiments/00_overall_cert_judge_metric_with_properties/main_overall_judge_score.py`

Orchestrates the full pipeline (654 lines):
1. Loads LLM credentials from `.env` file and prompt template
2. Scores file pairs via the LLM judge for each property ladder
3. Calls property functions from `hsj_scoring.py`
4. Logs all results to WandB

### Property Definitions

Each property tests a different aspect of judge reliability:
- **P1**: Reflexivity — identical files must score maximum
- **P2**: Bug monotonicity — scores decrease as bugs are introduced (AUC on bug ladder)
- **P3**: Spec completeness — scores decrease as specs are removed (AUC on spec ladder)
- **P4**: Stability — low variance across repeated evaluations of same pair
- **P5**: TVD-MI — discriminates same-source vs different-source file pairs
- **P6/P7**: Human/prover correlation (defined in `experiments/scoring_judges.md`, not yet fully implemented)

Full algorithmic specification for all properties is in `experiments/scoring_judges.md`.

### Test Data Layout

- P1 identity: directories of `.lean` files (scored against themselves)
- P2 bug ladder: `data/file_equiv_08_19_2025/my_add_file_eq_with_bugs/` — numbered files with increasing bugs
- P3 spec ladder: `data/file_equiv_08_19_2025/my_add_file_eq_with_missing_specs/` — numbered files with increasing spec deletions
- P5 pairwise: 25 same-source + 25 different-source file pairs sampled at runtime

## LaTeX Paper Sources

See `paper_latex/README.md` for build instructions. Two submissions:
- `paper_latex/ICML_2026/` — main file `main.tex`
- `paper_latex/NeurIPS_2025/mathai_neurips2025_template/` — main file `neurips_2025.tex`

Build with: `latexmk -pdf <main_file.tex>`
