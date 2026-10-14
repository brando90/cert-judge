# Experiment 49 results: how many tasks, raters and held-out judges the cert-judge rating pool needs

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/49_human_rating_round_design_precision_and_power_from_cached_judge_scores_and_five_raters/RESULTS_rating_round_design.md>

**TLDR:** Measured by resampling experiment 39's cached scores (56 LLM judge configurations × 75 VeriBench items × 3 repeats) and VeriBench experiment 100's five current raters, with no new inference and no new labels. Against the agent-suggested targets (ranking reliability ≥ 0.90 and gate agreement ≥ 0.90 versus the 25-task five-rater reference; power ≥ 0.80 for the pre-registered held-out test, Spearman ≥ 0.45 with one-sided permutation p-val < 0.05): the smallest adequate rating design is **20 tasks × 2 raters (120 nominal ratings; mean ranking reliability 0.950, gate agreement 0.915)**; the smallest adequate number of independently drawn held-out judge configurations from the all-configuration pool is **K = 12 (power 0.915)**; from the fuller-context pool **unmet within K ≤ 48 (best power 0.286)**; with judge models drawn as clusters, **M = 2 judge models (power 0.809)**. The registered design (15 tasks, raters 1–3) has ranking reliability 0.961 and gate agreement 0.929 against the reference, and its held-out association is 0.558 [0.08, 0.76] p-val=0.0127 (one-sided permutation over 16 configurations). Nothing here changes experiment 39's verdict or set N's evaluation-only rule.

Generated 2026-10-14T20:17:19.058151+00:00 by `scripts/analyze_e49.py` at worktree commit `83d1e853b6940192352b7bf880aafd4de8fdd191`; runtime 89 s; seed 49 (G0: 39). Inputs and hashes: `results/input_manifest.json`.

## Gate G0 — reproduction

- Criterion of every configuration from the harvest versus the unit files: max |Δ| = 0.00e+00 over 56 configurations → PASS.
- Registered `C_ms_gold` test association through `analysis_lib.association` (seed 39): Spearman 0.558 [0.078, 0.762] p-val=0.0127 on 16 units; max |Δ| versus `TEST_RECEIPT.json` = 1.11e-16 → PASS.
- NumPy parity (vectorized tie-aware Spearman versus `analysis_lib.spearman` on the registered design, every configuration): max |Δ| = 0.00e+00 → PASS.
- G0 overall: **PASS**.

## Reference criterion and the two fixed designs

| Design | Items (tasks) | Raters | Ratings used | Computable configurations | Held-out association of `C_ms_gold` (n) | Kendall τ-b | Pearson | Ranking reliability vs reference | Gate agreement vs reference |
|---|---|---|---|---|---|---|---|---|---|
| Reference | 75 (25) | all available (5; 4 where `p3` is missing) | 345 | 56/56 | 0.596 [0.13, 0.78] p-val=0.0093 (16) | 0.377 | 0.696 | 1 (by definition) | 1 |
| Registered (experiment 39) | 45 (15) | 1–3 (stored `target_expert`) | 117 | 56/56 | 0.558 [0.08, 0.76] p-val=0.0127 (16) | 0.360 | 0.643 | 0.961 | 0.929 |

Intervals are 95% percentile bootstraps over judge configurations (10,000 draws); p-values are one-sided permutation tests of a positive association (10,000 permutations); the reference uses seed 49, the registered design seed 39.

## Q1 — criterion precision and ranking reliability versus tasks and raters

1000 draws per cell (seed 49); tasks drawn without replacement (all three outputs of a task together), raters drawn without replacement from the five current raters; a configuration's criterion needs ≥ 90% of the drawn items scored. Reliability and gate agreement are against the reference (25 tasks, all available raters); the held-out association is the Spearman between `C_ms_gold` and the draw's criterion over the computable test configurations.

| Tasks T | Raters R | Items | Ratings used (mean) | Criterion SD (mean over 56) | Criterion SD (H2, 8) | Ranking reliability mean [5th pct] | Gate agreement | Held-out association mean [5th, 95th pct] | Draws ≥ 0.45 | Not computable |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 1 | 15 | 13.9 | 0.346 | 0.304 | 0.595 [-0.176] | 0.709 | 0.420 [-0.23, 0.79] | 0.59 | 0.048 |
| 5 | 2 | 15 | 27.5 | 0.294 | 0.234 | 0.756 [0.343] | 0.787 | 0.525 [0.11, 0.79] | 0.72 | 0.020 |
| 5 | 3 | 15 | 41.4 | 0.275 | 0.197 | 0.804 [0.531] | 0.812 | 0.551 [0.17, 0.79] | 0.76 | 0.019 |
| 5 | 5 | 15 | 69.2 | 0.273 | 0.182 | 0.817 [0.595] | 0.816 | 0.563 [0.24, 0.80] | 0.77 | 0.018 |
| 8 | 1 | 24 | 22.2 | 0.274 | 0.246 | 0.715 [0.069] | 0.752 | 0.490 [-0.07, 0.77] | 0.68 | 0.015 |
| 8 | 2 | 24 | 44.4 | 0.222 | 0.173 | 0.847 [0.621] | 0.836 | 0.556 [0.25, 0.75] | 0.81 | 0.004 |
| 8 | 3 | 24 | 66.3 | 0.199 | 0.133 | 0.890 [0.774] | 0.869 | 0.581 [0.35, 0.75] | 0.87 | 0.004 |
| 8 | 5 | 24 | 110.4 | 0.197 | 0.123 | 0.903 [0.812] | 0.875 | 0.594 [0.40, 0.76] | 0.91 | 0.005 |
| 10 | 1 | 30 | 27.2 | 0.247 | 0.216 | 0.758 [0.236] | 0.770 | 0.508 [0.02, 0.78] | 0.72 | 0.011 |
| 10 | 2 | 30 | 55.2 | 0.192 | 0.155 | 0.875 [0.681] | 0.858 | 0.578 [0.36, 0.75] | 0.87 | 0.000 |
| 10 | 3 | 30 | 82.8 | 0.166 | 0.109 | 0.917 [0.833] | 0.893 | 0.594 [0.43, 0.74] | 0.94 | 0.000 |
| 10 | 5 | 30 | 138.1 | 0.167 | 0.104 | 0.928 [0.871] | 0.897 | 0.589 [0.43, 0.73] | 0.94 | 0.000 |
| 15 | 1 | 45 | 41.7 | 0.190 | 0.163 | 0.838 [0.564] | 0.804 | 0.557 [0.20, 0.78] | 0.82 | 0.003 |
| 15 | 2 | 45 | 82.9 | 0.142 | 0.115 | 0.927 [0.846] | 0.898 | 0.601 [0.46, 0.72] | 0.95 | 0.000 |
| 15 | 3 | 45 | 124.8 | 0.117 | 0.078 | 0.951 [0.913] | 0.926 | 0.608 [0.50, 0.72] | 0.99 | 0.000 |
| 15 | 5 | 45 | 206.9 | 0.110 | 0.069 | 0.963 [0.934] | 0.934 | 0.599 [0.49, 0.69] | 0.99 | 0.000 |
| 20 | 1 | 60 | 55.2 | 0.162 | 0.141 | 0.874 [0.665] | 0.813 | 0.557 [0.23, 0.77] | 0.79 | 0.000 |
| 20 | 2 | 60 | 110.8 | 0.113 | 0.098 | 0.950 [0.882] | 0.915 | 0.605 [0.49, 0.72] | 0.98 | 0.000 |
| 20 | 3 | 60 | 166.0 | 0.079 | 0.051 | 0.970 [0.941] | 0.953 | 0.609 [0.54, 0.69] | 1.00 | 0.000 |
| 20 | 5 | 60 | 276.0 | 0.067 | 0.042 | 0.985 [0.972] | 0.962 | 0.599 [0.54, 0.65] | 1.00 | 0.000 |
| 25 | 1 | 75 | 69.0 | 0.135 | 0.115 | 0.903 [0.808] | 0.842 | 0.596 [0.36, 0.78] | 0.80 | 0.000 |
| 25 | 2 | 75 | 138.2 | 0.088 | 0.082 | 0.965 [0.909] | 0.930 | 0.618 [0.55, 0.73] | 1.00 | 0.000 |
| 25 | 3 | 75 | 206.2 | 0.040 | 0.026 | 0.982 [0.955] | 0.981 | 0.623 [0.57, 0.69] | 1.00 | 0.000 |
| 25 | 5 | 75 | 345.0 | 0.000 | 0.000 | 1.000 [1.000] | 1.000 | 0.596 [0.60, 0.60] | 1.00 | 0.000 |

The T = 25, R = 5 cell is the reference itself (no variation). p-val=n/a throughout this table (descriptive resampling).

## Q2 — power of the held-out test versus the number of held-out judge configurations

Gate: Spearman ≥ 0.45 and one-sided permutation p-val < 0.05 (experiment 39's pre-registered rule). 1000 draws per cell with 1000 permutations each (seed 49); pairs (`C_ms_gold`, reference criterion) drawn with replacement, so configurations are treated as independent (optimistic; see the clustered variant).

| Pool (n, pool Spearman) | K = 8 | K = 12 | K = 16 | K = 24 | K = 32 | K = 48 |
|---|---|---|---|---|---|---|
| all_configurations (54, 0.763) | 0.69 (ρ̄ 0.69, sd 0.19) | 0.92 (ρ̄ 0.70, sd 0.15) | 0.98 (ρ̄ 0.72, sd 0.11) | 0.99 (ρ̄ 0.74, sd 0.08) | 1.00 (ρ̄ 0.74, sd 0.06) | 1.00 (ρ̄ 0.75, sd 0.05) |
| test_16 (16, 0.596) | 0.38 (ρ̄ 0.53, sd 0.26) | 0.73 (ρ̄ 0.56, sd 0.19) | 0.79 (ρ̄ 0.55, sd 0.17) | 0.86 (ρ̄ 0.58, sd 0.12) | 0.88 (ρ̄ 0.58, sd 0.10) | 0.94 (ρ̄ 0.59, sd 0.08) |
| fuller_context (32, 0.302) | 0.19 (ρ̄ 0.28, sd 0.37) | 0.23 (ρ̄ 0.27, sd 0.29) | 0.29 (ρ̄ 0.29, sd 0.26) | 0.24 (ρ̄ 0.29, sd 0.20) | 0.18 (ρ̄ 0.29, sd 0.18) | 0.14 (ρ̄ 0.30, sd 0.14) |
| legacy (22, -0.357) | 0.01 (ρ̄ -0.31, sd 0.32) | 0.01 (ρ̄ -0.33, sd 0.25) | 0.00 (ρ̄ -0.35, sd 0.20) | 0.00 (ρ̄ -0.34, sd 0.16) | 0.00 (ρ̄ -0.34, sd 0.14) | 0.00 (ρ̄ -0.35, sd 0.11) |

Parametric (bivariate normal pairs, 2000 draws per cell, same gate):

| True ρ | K = 8 | K = 12 | K = 16 | K = 24 | K = 32 | K = 48 |
|---|---|---|---|---|---|---|
| 0.30 | 0.15 | 0.21 | 0.23 | 0.19 | 0.15 | 0.09 |
| 0.45 | 0.25 | 0.40 | 0.48 | 0.47 | 0.43 | 0.43 |
| 0.56 | 0.36 | 0.56 | 0.66 | 0.69 | 0.73 | 0.78 |
| 0.70 | 0.56 | 0.78 | 0.89 | 0.93 | 0.96 | 0.98 |

Model-clustered (M judge models drawn with replacement from the nine model keys; every computable configuration of a drawn model enters; draws with fewer than 8 configurations count as failures):

| Models M | K mean [min, max] | Draws with K < 8 | Power | ρ̄ (sd) [5th, 95th pct] |
|---|---|---|---|---|
| 2 | 12.0 [4, 18] | 187 | 0.81 | 0.71 (0.06) [0.62, 0.83] |
| 3 | 18.2 [6, 27] | 26 | 0.94 | 0.72 (0.08) [0.54, 0.82] |
| 4 | 23.9 [8, 36] | 0 | 0.96 | 0.71 (0.13) [0.57, 0.81] |
| 6 | 36.1 [12, 54] | 0 | 0.99 | 0.73 (0.07) [0.63, 0.81] |
| 9 | 53.6 [18, 81] | 0 | 1.00 | 0.74 (0.05) [0.66, 0.80] |

## Q3 — allocation at equal rating budgets (from the Q1 grid)

Rule: per nominal budget 3*T*R shared by more than one cell: the cell with the highest mean ranking reliability (ties: more tasks).

| Nominal ratings | Cells (T × R → reliability, gate agreement, criterion SD) | Best |
|---|---|---|
| 30 | 5×2 → 0.756, 0.79, 0.294; 10×1 → 0.758, 0.77, 0.247 | 10 tasks × 1 rater |
| 45 | 5×3 → 0.804, 0.81, 0.275; 15×1 → 0.838, 0.80, 0.190 | 15 tasks × 1 rater |
| 60 | 10×2 → 0.875, 0.86, 0.192; 20×1 → 0.874, 0.81, 0.162 | 10 tasks × 2 raters |
| 75 | 5×5 → 0.817, 0.82, 0.273; 25×1 → 0.903, 0.84, 0.135 | 25 tasks × 1 rater |
| 90 | 10×3 → 0.917, 0.89, 0.166; 15×2 → 0.927, 0.90, 0.142 | 15 tasks × 2 raters |
| 120 | 8×5 → 0.903, 0.87, 0.197; 20×2 → 0.950, 0.92, 0.113 | 20 tasks × 2 raters |
| 150 | 10×5 → 0.928, 0.90, 0.167; 25×2 → 0.965, 0.93, 0.088 | 25 tasks × 2 raters |
| 225 | 15×5 → 0.963, 0.93, 0.110; 25×3 → 0.982, 0.98, 0.040 | 25 tasks × 3 raters |

More tasks (fewer raters) wins 7 of 8 equal-budget comparisons.

## Q4 — model-based extrapolation (labelled; not a measurement beyond 75 items and 5 raters)

(a) Two-way additive model on all 345 ratings (75 items × 5 raters, missing allowed): σ²_item 1.023, σ²_rater 0.330, σ²_error 0.956 (0–5 scale); single-rater ICC(C,1) 0.517, ICC(A,1) 0.443. Balanced checks: 45 items × 5 raters ICC(C,1) 0.481, ICC(A,1) 0.353; 75 items × 4 raters (without `p3`) ICC(C,1) 0.488, ICC(A,1) 0.420.

| Raters R | ICC(C,R) of the R-rater mean | ρ_max = √ICC(C,R) | ICC(A,R) | ρ_max (agreement) |
|---|---|---|---|---|
| 1 | 0.517 | 0.719 | 0.443 | 0.666 |
| 2 | 0.682 | 0.826 | 0.614 | 0.784 |
| 3 | 0.763 | 0.873 | 0.705 | 0.839 |
| 5 | 0.843 | 0.918 | 0.799 | 0.894 |

(b) Design effect: task bootstrap at 25 tasks, all available raters, per-configuration SD of Fisher z across draws, divided by 1/sqrt(N-3), N=75; 1000 draws. Median per-configuration SD of the criterion 0.130 (Fisher z SD 0.192) against the independent-items Fisher SE 0.118: design effect median 2.64, mean 2.70.

| Items N | Extrapolated SD (Fisher z) | 95% half-width above ρ = 0.5 | below ρ = 0.5 | above ρ = 0.8 | below ρ = 0.8 |
|---|---|---|---|---|---|
| 75 | 0.192 | 0.228 | 0.328 | 0.100 | 0.181 |
| 90 | 0.174 | 0.212 | 0.295 | 0.094 | 0.161 |
| 120 | 0.150 | 0.188 | 0.251 | 0.084 | 0.134 |
| 150 | 0.134 | 0.171 | 0.221 | 0.077 | 0.116 |

(c) ρ_max is the attenuation ceiling for any proxy–criterion correlation implied by the R-rater target's reliability (model-based).

## Pre-declared readings

Targets (agent-suggested, PROTOCOL.md): ranking reliability ≥ 0.9, gate agreement ≥ 0.9, power ≥ 0.8.

- Smallest adequate (T, R): 20 tasks × 2 raters (120 nominal ratings; mean ranking reliability 0.950, gate agreement 0.915).
- Smallest adequate K, all-configuration pool: K = 12 (power 0.915).
- Smallest adequate K, fuller-context pool: unmet within K ≤ 48 (best power 0.286).
- Smallest adequate M, model-clustered: M = 2 judge models (power 0.809).
- Power at K = 16 by pool: all_configurations 0.98, test_16 0.79, fuller_context 0.29, legacy 0.00.

**Headline triple:** (smallest adequate (T, R) = 20 × 2; smallest adequate K for the all-configuration pool = 12; power at K = 16 for the fuller-context pool = 0.29).

**Reading the power numbers.** The all-configuration pool mixes the two prompt-rendering families: the legacy prompts (P1/P4/P8/LEX) have both low `C_ms_gold` and low agreement, so its pool Spearman (0.76) and its power are carried by the between-family contrast. Within the fuller-context family (the configurations anyone would deploy) the pool Spearman is 0.30, below the 0.45 gate, and no number of held-out configurations reaches 0.80 power; the parametric row at ρ = 0.30 shows why: as K grows the estimate concentrates below the gate and power falls. The all-configuration and model-clustered pools also contain the 38 train and validation configurations on which `C_ms_gold` was selected, so their pool Spearman is optimistic relative to the held-out 16 (0.56 registered, 0.60 against the reference). More ratings do not change this either (the held-out association column of Q1 is flat in T and R once the criterion is reliable). For the next pool the decisive lever is the size of the within-family effect (a better screen or a gate chosen for the deployable family), not more judges or more ratings; the model-clustered rows inherit the same between-family contrast.

Nothing here changes experiment 39's verdict, the frozen screen, or set N's evaluation-only rule.

**TLDR-end:** [cert-judge: experiment 49 rating-round design from cached scores] Smallest adequate rating design 20 tasks × 2 raters; held-out test power reaches 0.8 at K = 12 independently drawn configurations of the mixed-family pool (power 0.92), but the fuller-context pool gives only 0.29 at K = 16 and never reaches it, because its pool Spearman (0.30) sits below the 0.45 gate.
