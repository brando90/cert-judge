# Experiment 39 protocol: best-of-K selection bias on the 72-pair validation set

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/39_best_of_k_judge_selection_bias_validation_set/PROTOCOL.md>

**TLDR:** Frozen plan for four zero-inference analyses (A null best-of-K, B split-half selection, C synthetic sweep, D judge-level adjustment over the reported index forms), with the pool rule, parameters, seeds, reproduction gates and decision rules fixed before any analysis output was seen.

Frozen: 09-26-2026 16:56 PDT, before the analysis script existed. Any later deviation is recorded under "Deviations" at the bottom with its reason; this plan is not rewritten.

## Definitions

- **Items.** The (gold, candidate) keys present in all three label files and scored by the judges: 72 pairs. The problem of an item is its gold-file stem. The run aborts unless there are exactly 24 problems with 3 candidates each.
- **Label views.** `avg` (primary), `pass1`, `pass2`, loaded as exp16 loads them (mean of duplicate rows per key).
- **Agreement.** `rho(j, L, S)` is the Spearman correlation (average ranks for ties; `scipy.stats.spearmanr` semantics) between configuration `j`'s recorded repeat-aggregated score (`score_mean` in `detail_rows.csv`) and label view `L` over item set `S`. It is undefined when either vector is constant on `S`; an undefined value never wins a selection, and means exclude undefined values with their counts reported.
- **Configuration pool.** (1) Every `detail_rows.csv` under `experiments/archive/` with `row_type == human_eval_union`. (2) Keep each (source directory, `judge_id`) whose rows cover exactly the 72 items. (3) Drop deterministic controls (`judge_id` starting with `random` or `editdist`). (4) Drop configurations with constant scores. (5) Deduplicate exact duplicates of the 72-score vector as recorded, keeping the first in lexicographic (source path, `judge_id`) order and recording every alias. (6) The label-free property statistic of a configuration is `cert_index` (the exp16 v1 index: identity mean, bug-rank monotonicity, bug weak monotonicity and decision stability, all from probes of the golds, no labels) from the sibling `judge_rows.csv` row of the kept representative.
- **Reproduction gate (stop rule).** For every kept configuration and view, the recomputed agreement must match the frozen `human_spearman_r_<view>` in its `judge_rows.csv` within 1e-3 (the recorded scores are rounded to six decimals), and the paper's Codex values in Table `tab:codex_configs` (0.466, 0.419, 0.365, 0.435, -0.014, 0.092 on averaged labels) must reproduce at three decimals. Any failure stops the run and is reported.

## Analysis A: null best-of-K over real configurations

- Views: `avg`, `pass1`, `pass2`. K grid: 1, 2, 4, 8, 16, 32 and the pool size N (values above N dropped). Draws: B = 4000 per view.
- Each draw: a uniformly random ordering of the pool (the first K configurations form the K-subset, so subsets are nested across K); a block permutation of the labels (a uniform permutation of the 24 problems and an independent uniform shuffle of the 3 labels within each block); `M_K` = the largest agreement among the first K configurations with the permuted labels on all 72 items.
- Report the mean, median and 95th percentile of `M_K`, and the Monte Carlo standard error of the mean. `E[M_K]` is the apparent agreement of the winner when no configuration tracks the labels.

## Analysis B: split-half selection on real labels

- Same views and K grid; R = 4000 replicates per view. Each replicate draws a uniform ordering of the pool (nested K-subsets) and a uniform split of the 24 problems into a selection half S and a held-out half H of 12 problems (36 items each).
- Selection rules within the K-subset: **label** (largest `rho` on S), **random** (uniform), **property** (largest `cert_index`, ties broken uniformly), and **oracle** (largest `rho` on H; a reference upper bound, not a usable rule).
- For each rule record `rho(w, L, S)` and `rho(w, L, H)`; optimism = S minus H. Report per rule the mean selection-half and held-out agreement, the mean optimism with its Monte Carlo standard error, and the 2.5/50/97.5 percentiles of the optimism across replicates.
- `cert_index` uses probes of all 24 golds; it consults no labels, so the property rule cannot select on label noise. The percentile spread describes variation across splits; it is not a confidence interval for a population quantity.

## Analysis C: synthetic sweep

- Latent quality for P problems with 3 candidates: `q = sqrt(tau) a_problem + sqrt(1 - tau) e_item`. Two label passes `y_p = sqrt(r) q + sqrt(1 - r) noise_p`, each quantile-mapped to the observed marginal of the corresponding pass (integers 0 to 5); the averaged label is their mean.
- Judges: `s_k = beta_k q + sqrt(1 - beta_k^2) n_k`, with `n_k = sqrt(c) u + sqrt(1 - c) v_k`; `u` (shared) and `v_k` (judge-specific) have problem intraclass correlation `tau_s`.
- Calibration, fixed from data before any selection output: `r` by grid search so that the simulated inter-pass Spearman matches the observed pass1-pass2 Spearman on the 72 items (the paper reports 0.249); then `tau` by grid search so that the simulated averaged-label one-way intraclass correlation over problems matches the observed one; `tau_s` = the median one-way intraclass correlation of the pool's 72-score vectors; `c_pool` = the median pairwise Spearman among pool configurations.
- Settings: **null-indep** (`beta = 0`, `c = 0`), **null-shared** (`beta = 0`, `c = c_pool`), **weak-equal** (every judge has fresh-data agreement 0.30 with the averaged label; `c = 0`), **weak-hetero** (fresh-data agreements drawn uniformly from [0, 0.45]; `c = 0`). Fresh-data agreement is the Spearman with the averaged label on a large simulated sample; a lookup table maps it to `beta`.
- K: 1, 2, 4, 8, 16, 32, 64 (nested); panel sizes P = 24 (72 items) and P = 12 (36 items); B = 4000 replicates per cell. Statistic: the winner's panel agreement minus its fresh-data agreement. Report the mean with its standard error and the 2.5/97.5 percentiles.
- Consistency check (reported, not fitted): weak-hetero at 36 items against the real label-rule optimism of analysis B at the same K.

## Analysis D: judge-level association adjusted for the choice among reported index forms

- Families and sources as in `experiments/34_iclr_mega_rewrite_astra/analysis/rebuild_paper_evidence.py`: Codex (`results_exp16_final_robust_r9_median`), Claude Opus 4.7 (`results_exp16_opus47_r3_median`), Qwen3-Coder (`13_qwen_replication_exp16_exp19/results/exp16_qwen_r3_median`); the eight configurations of each panel; views `pass1`, `pass2`, `avg`.
- Forms: v1 (`cert_index`) and v2 (`cert_index_v2`) from exp16 `judge_rows.csv`; `GM_{.4,.6}` (`geo_trust_index` rows of the exp22/exp25 `mono_stab_40_60` summaries; label-free, so one vector serves every view); `TI_var` (`TI_variance_aware` from the exp28 `judge_trust_vector.csv` of each view, checked to be identical across views). Target: the eight human agreements of the view.
- Reproduction gate: the paper's Table `tab:tivar_cross_model_results` Spearman entries reproduce at three decimals, and the exact permutation probabilities of experiment 38's `judge_level_diagnostics.csv` reproduce.
- Exact permutation over all 8! = 40320 orderings of the target. Report the unadjusted one-sided exact p for `TI_var`, the adjusted p = P(max over the four forms of the permuted Spearman >= observed `TI_var` Spearman), and the adjusted p for the best observed form.
- Scope: this accounts only for the choice among the four reported forms. It does not account for the six-weight search, the local weight grid, forms tried but not reported, or the fitting of the `GM` weights on pass1, so the adjusted values remain optimistic.

## Seeds and environment

- Master seed 20260926; per-analysis generators come from `numpy.random.SeedSequence(20260926).spawn(...)` in the fixed order A, B, C, D.
- Python 3.11 with numpy 2.2.6, scipy 1.17.1, matplotlib 3.11.1 (the versions in `uv.lock`); versions and input SHA-256 hashes are recorded in `results/summary.json`.

## Decision rules (fixed before the run)

1. **Magnitude sentence.** If the null inflation `E[M_8]` on averaged labels (analysis A) is at least 0.10, the introduction's adaptive-overfitting sentence gets a quantitative clause built from A and B. If it is below 0.05, the drafted sentence says selection effects at this panel size are small. Between the two, the sentence reports the number without an adjective.
2. **Real-data optimism.** Analysis B's label-rule mean optimism at K = 8 on averaged labels is reported whatever its sign or size. If the random rule's mean optimism is not within three Monte Carlo standard errors of zero, the split machinery is treated as broken and the run stops.
3. **Property rule.** The property rule's held-out agreement is compared with the label rule's at each K and reported descriptively in both directions; no claim of superiority is drawn from one validation set.
4. **Judge-level adjustment.** Adjusted and unadjusted p-values are reported side by side for all nine family-view cells; no cell is dropped.
5. **No paper edits.** Drafted sentences go to `REPORT.md`; the paper owner applies them.

## Deviations

_None yet._
