# Experiment 40: selection-bias checkpoint

**TLDR:** Complete. All four analyses ran, the report and drafted paper text are written, and the experiment is archived; nothing is running.

Created: 09-26-2026 16:56 PDT
Last updated: 09-26-2026 17:25 PDT

- Task: measure best-of-K selection bias on the 72-pair validation set (item 35.3 of `experiments/35_missing_experiments_from_reviews/EXPERIMENTS.md`), zero inference.
- Branch: `claude/bold-fermat-atoesg` (cloud session); base `b4e3db0` on `main`. Commits: `7548c3a` (protocol freeze), `d5d6ea2` (script and pre-run deviations), then the results and archive commits on the same branch.
- Environment: `~/uv_envs/cert-judge-analysis` (numpy 2.2.6, scipy 1.17.1, matplotlib 3.11.1, pytest; pypdf and pymupdf only for the drop-in page check). Tectonic 0.17.0 was downloaded to the session scratchpad for the scratch paper builds.
- Outputs: `results/` (CSV and JSON with input hashes), `figures/best_of_k_selection_bias.{pdf,png}`, `REPORT.md`.
- Open item for the paper owner: apply or reject the drafted text in `REPORT.md` § Drafted paper text, and copy the figure into `paper_latex/ICLR_2027_submission/figures/` if the appendix subsection is used.
- Next command if resumed (re-verification only): `~/uv_envs/cert-judge-analysis/bin/python experiments/archive/40_best_of_k_judge_selection_bias_validation_set/analysis/best_of_k_selection_bias.py && ~/uv_envs/cert-judge-analysis/bin/python -m pytest tests/test_best_of_k_selection_bias.py`
- Blockers: none.
