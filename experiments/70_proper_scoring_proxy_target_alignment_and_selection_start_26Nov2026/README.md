# Experiment 70: Proper-Scoring Proxy-vs-Target Alignment, Selection, and Live VeriBench Ratings Check (`11-26-2026`)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/70_proper_scoring_proxy_target_alignment_and_selection_start_26Nov2026/README.md>

Date: 11-26-2026

**TLDR:** Replaces the legacy double-correlation meta-metric (`Spearman(proxy, human_Spearman)`) with proper-scoring targets (`RPS`, `CE`, `TVD`, `Brier`, `ICC(A,1)`), decision-theoretic / proper-scoring proxy-vs-target similarity (`Top-1 Regret`, `Subpool Regret`, `UWA_RPS`, `Beat-CONST Meta-Brier/Meta-CE`, `Meta-RMSE`), and label-free proper-scoring behavioral proxies (`P_e42_fullcov_brier`, `P_e39_fullcov_brier`, `P_dsti_proper`) across Experiment 39/42 (`60` configs), Experiment 60 (`62` open-weight harvests), Experiment 58 (`117` units), Experiment 63 (`6` training arms), and the live `11-26-2026` VeriBench team ratings (`250` ratings across `100` native files / `25` tasks) at `$0` API spend.

## Motivation

Two findings motivate this experiment:
1. From `brando90/judges-dont-need-psychometrics-or-corr` (Experiments `01`, `23`–`29`, `34`–`36`), rank and linear correlation are affine-invariant and blind to scale, calibration, and distributional shape. Evaluating a label-free behavioral proxy $P(j)$ solely by `Spearman(P(j), human_Spearman(j))` inherits that double-correlation blind spot.
2. In `cert-judge` (`39_label_free_proxy_index_train_val_test_over_judge_families`, `42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges`, `66_prover_target_judge_selection_by_behavioral_index`, and `68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026`), rank-monotonicity proxies such as `C_ms_gold` can achieve high rank correlation with human alignment yet still be hijacked by deterministic lexical controls (`name_jaccard`, `editdist`, `count_ratio`) or ignore judge scale/calibration errors on raw proper scores.

## Studies

1. **Study 1 — Live VeriBench Human Ratings Check (`11-26-2026`):** Read-only verification of all `33` accessible VeriBench team Google Sheets against `trustworthy-theorem-judges` Experiment 09 (`460466d`, `250` non-coordinator ratings across `100` files / `25` tasks; `T30` HTTP `401` unverified), Leave-One-Rater-Out (`LORO`) ceilings, and pairwise agreement.
2. **Study 2 — Proper-Scoring Proxy-vs-Target Alignment & Selection (`E39` + `E42`, `60` units):** Evaluates legacy proxies (`TI_var_trainnorm`, `PTI_v0_frozen`, `C_ms_gold`, `C_bm_gold`) alongside new label-free proper-scoring behavioral proxies (`P_e39_fullcov_brier`, `P_e39_probe_rps`, `P_e42_fullcov_brier`, `P_e42_fullcov_ce`, `P_dsti_proper`) on both `LLM-only` and `LLM + 4 controls` pools, plus a zero-leakage `Meta-Corr` vs `Meta-Proper-RPS` selection comparison on `18` held-out test judge configs (`+ 4` controls).
3. **Study 3 — Independent Open-Weight Replication (`E60` `62` raw harvests + `E58` `117` units):** Streams `e60_harv0.tgz` (`26` seed-0 units) and `e60_harv1.tgz` (`36` seed-1 replicates) in memory to test proper-scoring proxy-vs-target alignment and seed stability on open-weight models, plus cross-checks `E58` (`117` units across `13` open-weight judges).
4. **Study 4 — `native_main` (`N=100`, `250` ratings) & `E63` Distributional Bridge:** Links `H2_astra`, `H2_opus`, `H3_astra`, `P8_STRICT_B` (`Codex`, `Opus`, `Qwen3-Coder`), and judge-free baselines on the `100` live-synced native files to their frozen E39/E42 behavioral proxies, and verifies E63 (`6`-arm `Qwen3-8B`) parity.

## Reproduction (`$0` API spend, CPU only)

```bash
python3 -m unittest discover -s experiments/70_proper_scoring_proxy_target_alignment_and_selection_start_26Nov2026/tests -p 'test_*.py' -v
python3 experiments/70_proper_scoring_proxy_target_alignment_and_selection_start_26Nov2026/scripts/run_exp70.py
```

## Files

- [PROTOCOL.md](PROTOCOL.md) — Frozen measurement contract, exact definitions, zero-leakage split rules, and pre-registered predictions (`P1`–`P4`).
- [results.md](results.md) — Live experiment ledger.
- [RESULTS_proper_scoring_proxy_target_11-26-2026.md](RESULTS_proper_scoring_proxy_target_11-26-2026.md) — Full results report.
- [derivation/proxy_target_proper_scoring_derivation.pdf](derivation/proxy_target_proper_scoring_derivation.pdf) — LaTeX-typeset mathematical derivation (Rule 91).
- [scripts/](scripts/) — `proxy_metrics.py`, `run_exp70.py`.
- [tests/](tests/) — `test_exp70.py`.
- [results/](results/) & [figures/](figures/) — Aggregate JSON/CSV tables and figures (`0` raw rater rows or personal identifiers).
