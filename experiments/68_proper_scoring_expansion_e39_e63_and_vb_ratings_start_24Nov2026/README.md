# Experiment 68: Proper-Scoring Expansion Across `63_judge_optimization_arms_prompt_sft_rl_qwen3_8b`, `39_label_free_proxy_index_train_val_test_over_judge_families`, Paper Panels, and Live VeriBench Ratings (`11-24-2026`)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/README.md>
Date: 11-24-2026

**TLDR:** CPU-only (`$0` API spend, zero model calls, no internet evaluation except read-only public Comma-Separated Values (CSV) export in Study D, no Differential Testing (DT) applicable) canonical proper-scoring evaluation — Ranked Probability Score (`RPS`), Cross-Entropy (`CE`), Total Variation Distance (`TVD`), Brier score (`Brier`), Mean Absolute Error (`MAE`), signed mean bias (`judge - human`, positive = lenient), two-way Intra-Class Correlation for absolute agreement (`ICC(A,1)`) and consistency (`ICC(C,1)`), Quadratic Weighted Kappa (`QWK`), and individual rank/linear correlations (`Spearman`, `Kendall`, `Pearson`) — paired with an independent verification of [Experiment 67](../67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/RESULTS.md).

## Why this experiment exists

1. In [67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel](../67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/RESULTS.md), re-scoring the 24 legacy paper series (`results_exp16_*`, 59 items / 20 tasks) showed negative rank correlations (`-0.21` to `-0.35`) against corrected human labels because those legacy prompts/artifacts had `-0.04` correlation with corrected labels, causing every Leave-One-Task-Out (`LOTO`) calibration curve to collapse to the marginal baseline (`0.1737` `RPS`). Furthermore, Experiment 67's first Quality Assurance (`QA`) report left the `LOTO` optimization fits, Variance-Aware Trust Index (`TI_var`) permutation tests, `QWK`, and live Sheets unverified, and misattributed Codex's pass1/pass2 numbers on line 111.
2. Experiment 68 verifies those unchecked numbers independently and tests whether proper scoring rules sharpen real, signal-bearing judge panels:
   - **Study A** evaluates all 18 test runs (`6` training/prompting arms, native 6-class probability forecasts `probs` over `{0..5}`, zero binning approximation) from [63_judge_optimization_arms_prompt_sft_rl_qwen3_8b](../63_judge_optimization_arms_prompt_sft_rl_qwen3_8b/README.md) against individual human ratings from VeriBench Experiment 100 (`all5` primary, `expert3` secondary).
   - **Study B** evaluates all `60` saved judge configurations (`56` Large Language Model (`LLM`) configs across prompt families + `4` non-LLM controls) from [39_label_free_proxy_index_train_val_test_over_judge_families](../39_label_free_proxy_index_train_val_test_over_judge_families/README.md) on `45` held-out items (`15` validation + `30` test, `15` tasks), testing raw vs strictly train-task-calibrated `RPS`/`CE`/`TVD`/`ICC(A,1)` and meta-evaluation of `C_ms_gold`, `TI_var`, and Frozen Proxy Trust Index (`PTI_v0`).
   - **Study C** reproduces [archive/51_certjudge_rescore_rps_ce_tvd_nov2026](../archive/51_certjudge_rescore_rps_ce_tvd_nov2026/rescore_proper.py) (`max_err <= 2.22e-16`), diagnoses wide 95% Confidence Intervals (`CI`) via task-subset resampling and Leave-One-Judge-Out (`LOJO`) sensitivity on the 8-configuration paper panels, and cross-verifies `216` LOTO scalars, `12` `TI_var` permutation tests, and `new_summary.json` from Experiment 67.
   - **Study D** aggregates live read-only public Google Sheet CSV exports from VeriBench `trustworthy-theorem-judges` Experiment 09 (`33/34` readable sheets; `247` non-coordinator ratings across `100` files / `25` tasks; `0/100` Secure Hash Algorithm 256-bit (`SHA-256`) file overlap with frozen [64_cert_judge_nov6_confirmatory_test_setN_preregistration](../64_cert_judge_nov6_confirmatory_test_setN_preregistration/PROTOCOL.md)), computes human Leave-One-Rater-Out (`LORO`) proper-scoring ceilings and judge-free LOTO baselines without storing any raw per-rater Sheet rows, rationales, or notes.

## Files

- `scripts/metrics.py` — Canonical proper-scoring, agreement (`ICC(A,1)`, `ICC(C,1)`, `QWK`), `LORO` ceiling, calibration fitters (`CONST`, ordinal `CE_fit`, Gaussian `Pearson_fit`), vectorized exact/Monte Carlo (`MC`) permutation tests, and task-cluster / family-cluster bootstraps.
- `tests/test_metrics.py` — `11` deterministic unit tests verifying mathematical identities, bias sensitivity of `ICC(A,1)`, equal artifact weighting, exact small-sample permutation tests, vectorized within-family permutations, and fast Spearman parity with `scipy.stats`.
- `scripts/run_expansion.py` — End-to-end deterministic analysis runner for Studies A–D and Experiment 67 independent cross-checks.
- `RESULTS_proper_scoring_expansion_11-24-2026.md` — Full report with verification tables, intervals, and QA record.
- `results/` — Machine-readable aggregate JavaScript Object Notation (`JSON`) and CSV outputs (`study_a_e63_*`, `study_b_e39_*`, `study_c_paper_*`, `study_d_live_vb_ratings_aggregate.json`, `exp67_independent_crosscheck.json`, and QA output record).

## Reproduction

Run under an arm64/working Python `>= 3.11` environment with `numpy` and `scipy` (for example `/Users/brandomiranda/uv_envs/no-gold-ref-judge/bin/python3`):

```bash
cd /Users/brandomiranda/cert-judge
python3 -m unittest discover -s experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/tests -p 'test_*.py' -v
python3 -u experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/scripts/run_expansion.py
python3 py_src/cert_judge/experiment_layout.py --check
```
