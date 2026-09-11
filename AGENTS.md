# AGENTS.md

## Global Agent Rules (load first, every session)

Fetch and follow the global rules from brando90/agents-config before doing anything else:
- **Primary (always works — cloud, phone, local):** fetch `https://raw.githubusercontent.com/brando90/agents-config/main/INDEX_RULES.md` and follow all Hard Rules, Trigger Rules, and Guidelines listed there.
- **Local optimization:** if `~/agents-config/` exists locally, read `~/agents-config/INDEX_RULES.md` instead (faster, same content). Run `git -C ~/agents-config pull` first to ensure it's current.
- **Sync discipline:** after any git commit+push in this repo, also pull agents-config (`git -C ~/agents-config pull` or re-fetch the URL) so all agents stay on the latest rules. If you edit agents-config itself, commit+push there too.

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Purpose

`cert-judge` studies LLM-based judges for Lean 4 theorem/specification scoring. Keep these scientific objects distinct:

- `TW_m`: the scoped trustworthiness construct;
- `TI_m`: an expensive human-grounded criterion;
- `PTI_p`, currently `PTI_v0`: a label-free behavioral proxy/screening instrument.

The older P1–P7/JTI and TIvar pipelines remain historical compatibility code. Their outputs are not PTI-v0 and must not be relabeled as such.

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

The frozen PTI-v0 numerical specification is `docs/spec/PTI_V0.md`. Its zero-spend entry point is:

```bash
python experiments/04_veribench_validation/run_pti_v0.py --help
```

That CLI has no inference client and cannot load credentials. Paid judge inference requires a separate exact call/cost quote and explicit approval. Historical JTI evaluations remain under `experiments/00_overall_cert_judge_metric_with_properties/`.

## Architecture

### Core Package: `py_src/cert_judge/`

**`pti_v0.py`** — canonical, versioned PTI-v0 numerics: tie-aware ladder correlations, repeat instability, exact-zero log geometric means, coverage-aware properties, and three-/four-property aggregation.

**`probe_validation.py`** — conservative alpha-renaming and cumulative bug/missing-spec probe construction with fail-closed Lean elaboration.

**`hsj_scoring.py`** — legacy JTI/HSJ compatibility logic, including `compute_p1_identity()`, `compute_p2_or_p3_ordering_auc()`, `compute_p4_stability()`, `compute_jti()`, and calibration/fusion helpers.

**`tvd_mi_tools.py`** — TVD-MI information robustness metric:
- `tvd_mi_from_critic()` — Youden's J (TPR+TNR-1) from categorical labels
- `per_item_auc_macro()`, `tamper_suite_report()` — P5 sub-metrics

The PTI-v0 properties are exact equality (`P_eq`), bug monotonicity (`P_bm`), missing-specification monotonicity (`P_ms`), and alpha-renaming invariance (`P_eqalpha`). Structurally valid constant judge-score ladders remain included with `C=0`; structurally invalid probes are excluded independently of judge outputs; missing score coverage yields `NOT_COMPUTABLE/DEFER`.

### PTI-v0 Data Layout

- Base candidates: `data/generated_agents/`, frozen as typed `f=(item,agent,generation)` rows in `experiments/04_veribench_validation/pti_v0_v4/base_pool_manifest.json`.
- Golds: resolved by the frozen precedence policy across the legacy and newest VeriBench roots.
- Probe validity, requests, cache inventory, quotes, and results: new artifacts under `experiments/04_veribench_validation/results_pti_v0_v4/`; legacy result directories are never overwritten.

Historical P1–P5 fixtures retained for compatibility:

- P1 identity: directories of `.lean` files (scored against themselves)
- P2 bug ladder: `data/file_equiv_08_19_2025/my_add_file_eq_with_bugs/` — numbered files with increasing bugs
- P3 spec ladder: `data/file_equiv_08_19_2025/my_add_file_eq_with_missing_specs/` — numbered files with increasing spec deletions
- P5 pairwise: 25 same-source + 25 different-source file pairs sampled at runtime

## LaTeX Paper Sources

The active manuscript is `paper_latex/ICLR_2027_submission/main.tex`. Older ICML/NeurIPS trees are historical. Populate PTI-v0 claims only from committed machine-readable PTI-v0 outputs.

Build with: `latexmk -pdf <main_file.tex>`
