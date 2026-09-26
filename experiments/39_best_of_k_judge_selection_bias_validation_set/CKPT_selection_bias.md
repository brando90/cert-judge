# Experiment 39: selection-bias checkpoint

**TLDR:** Registered and protocol frozen; next step is writing and running `analysis/best_of_k_selection_bias.py`.

Created: 09-26-2026 16:56 PDT
Last updated: 09-26-2026 16:56 PDT

- Task: measure best-of-K selection bias on the 72-pair validation set (item 35.3 of `experiments/35_missing_experiments_from_reviews/EXPERIMENTS.md`), zero inference.
- Branch: `claude/bold-fermat-atoesg` (cloud session); base `b4e3db0` on `main`.
- Environment: `~/uv_envs/cert-judge-analysis` (numpy 2.2.6, scipy 1.17.1, matplotlib 3.11.1, pytest) — minimal venv; the full project environment is not needed.
- Plan: `PROTOCOL.md` (frozen). Outputs go to `results/`, `figures/`, `REPORT.md`.
- Next command: `~/uv_envs/cert-judge-analysis/bin/python experiments/39_best_of_k_judge_selection_bias_validation_set/analysis/best_of_k_selection_bias.py`
- Blockers: none.
