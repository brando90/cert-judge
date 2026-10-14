# Experiment 48 results: cluster-aware intervals and criterion sensitivity of the held-out judge association of `C_ms_gold`

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/48_c_ms_gold_heldout_judge_association_cluster_bootstrap_and_criterion_sensitivity/RESULTS_heldout_association_sensitivity.md>

Generated 2026-10-14T20:09:27.235976+00:00 by `scripts/analyze_e48.py` (zero inference; inputs hashed in `results/input_manifest.json`, repository HEAD `c16120b024a8b3849778a327a18593433210298b`). Unless stated, every number is a tie-aware Spearman correlation between `C_ms_gold` and the judge–human criterion over the 16 computable held-out judge configurations; intervals are 95% percentile bootstraps (10,000 draws) with the resampled unit named; p-values are one-sided permutation tests for a positive association, (k + 1)/(n + 1) over 10,000 draws; seed 48 for every new resample, seed 39 only for the reproduction of experiment 39's receipt. Thresholds: 0.45 and p-val < 0.05 are experiment 39's pre-registered gate (its `PROTOCOL.md`); 0 is 'no positive association'. Readings follow `PROTOCOL.md` § Pre-declared readings (ROBUST / WEAKENED / REVERSED).

## TLDR

- **Headline triple.** Within-judge-model permutation p-val=0.0701 (pooled association not shown to hold within models); minimum Spearman over the reference-quality views 0.530 (view `neither_placeholder_nor_ambiguous`, ROBUST); two-level (task, then configuration) interval lower bound 0.073 (above 0: True; above 0.45: False).
- **Readings.** Leave-one-model-out: {'opus55x': 'ROBUST', 'qwen36': 'WEAKENED', 't2_qwen': 'ROBUST', 't2_sonnet5': 'ROBUST'}; leave-one-prompt-out: {'D0': 'ROBUST', 'H0': 'ROBUST', 'H1': 'ROBUST', 'H2': 'ROBUST', 'LEX': 'WEAKENED', 'P1': 'ROBUST', 'P4': 'ROBUST', 'P8': 'ROBUST'}; rater views: {'single_p1': 'ROBUST', 'single_p2': 'ROBUST', 'single_p3': 'ROBUST', 'single_p4': 'ROBUST', 'single_p5': 'ROBUST', 'all_available_raters_mean': 'ROBUST', 'leave_out_p1': 'ROBUST', 'leave_out_p2': 'ROBUST', 'leave_out_p3': 'ROBUST', 'leave_out_p4': 'ROBUST', 'leave_out_p5': 'ROBUST', 'registered_target_expert': 'ROBUST'}; reference-quality views: {'original45': 'ROBUST', 'no_placeholder_reference_tasks': 'ROBUST', 'no_ambiguous_reference_tasks': 'ROBUST', 'neither_placeholder_nor_ambiguous': 'ROBUST'}.
- **Registered result reproduced (G0 PASS=True):** test Spearman 0.558 [0.078, 0.762] p-val=0.0127 (configuration bootstrap and permutation, seed 39, 16 units); every test unit's criterion and `C_ms_gold` reproduced to 1e-9; criterion ranking reproducibility 0.928 over 47 configurations.
- Experiment 39's registered PASS is unchanged; this report states its scope.

## G0 — reproduction of experiment 39's receipt

| Check | Stored | Recomputed | Pass |
|---|---|---|---|
| Test association `C_ms_gold` (16 units, seed 39) | 0.558 [0.078, 0.762] p-val=0.0127 | 0.558 [0.078, 0.762] p-val=0.0127 | True |
| Held-out criterion of every test unit (18 units, 45 items) | max abs diff 0.0e+00 | from harvest `crit` cells, median of repeats | True |
| `C_ms_gold` of every test unit (18 units; 2 None) | max abs diff 3.3e-16 | `analysis_lib.components` on harvest + manifest | True |
| Criterion ranking reproducibility (validation items vs test items, 47 LLM configurations) | 0.928 | 0.928 | True |

## A1 — cluster-aware uncertainty

| View | Resampled unit | Spearman [95% interval] p-val | Kendall τ-b | Pearson | Draws defined / <8 units | Note |
|---|---|---|---|---|---|---|
| (a) registered configuration bootstrap, seed 39 | judge configuration | 0.558 [0.078, 0.762] p-val=0.0127 | 0.360 | 0.643 | 10000 / 0 | experiment 39's receipt |
| (a) configuration bootstrap, seed 48 | judge configuration | 0.558 [0.091, 0.764] p-val=0.0159 | 0.360 | 0.643 | 10000 / 0 | same statistic, this experiment's seed |
| (b) judge-model cluster bootstrap (4 clusters: opus55x×5, qwen36×7, t2_qwen×2, t2_sonnet5×2) | cluster | 0.558 [-0.842, 0.656] p-val=n/a | — | — | 10000 / 0 | over draws with ≥ 8 units: [-0.842, 0.656] (10000 draws); 35 distinct cluster multisets; undefined draws 0 |
| (c) prompt cluster bootstrap (8 clusters: D0×4, H0×2, H1×1, H2×3, LEX×2, P1×1, P4×2, P8×1) | cluster | 0.558 [-0.123, 0.850] p-val=n/a | — | — | 10000 / 0 | over draws with ≥ 8 units: [-0.123, 0.850] (10000 draws); 6435 distinct cluster multisets; undefined draws 0 |

**(d) Leave one judge model out.** Summary over deletions: min 0.377, median 0.564, max 0.591 (4 views).

| Dropped | Units left | Spearman [95% configuration bootstrap] p-val (configuration permutation) | Kendall τ-b | Pearson | Reading |
|---|---|---|---|---|---|
| `opus55x` | 11 (−5) | 0.545 [-0.174, 0.849] p-val=0.0428 | 0.382 | 0.619 | ROBUST |
| `qwen36` | 9 (−7) | 0.377 [-0.656, 0.842] p-val=0.1575 | 0.197 | 0.772 | WEAKENED |
| `t2_qwen` | 14 (−2) | 0.591 [0.158, 0.782] p-val=0.0139 | 0.385 | 0.612 | ROBUST |
| `t2_sonnet5` | 14 (−2) | 0.583 [0.132, 0.781] p-val=0.0153 | 0.376 | 0.615 | ROBUST |

**(d) Leave one prompt out.** Summary over deletions: min 0.453, median 0.520, max 0.741 (8 views).

| Dropped | Units left | Spearman [95% configuration bootstrap] p-val (configuration permutation) | Kendall τ-b | Pearson | Reading |
|---|---|---|---|---|---|
| `D0` | 12 (−4) | 0.741 [0.299, 0.932] p-val=0.0035 | 0.545 | 0.623 | ROBUST |
| `H0` | 14 (−2) | 0.535 [0.043, 0.719] p-val=0.0241 | 0.309 | 0.626 | ROBUST |
| `H1` | 15 (−1) | 0.595 [0.145, 0.787] p-val=0.0112 | 0.383 | 0.630 | ROBUST |
| `H2` | 13 (−3) | 0.586 [0.127, 0.782] p-val=0.0206 | 0.374 | 0.589 | ROBUST |
| `LEX` | 14 (−2) | 0.453 [-0.190, 0.825] p-val=0.0534 | 0.331 | 0.824 | WEAKENED |
| `P1` | 15 (−1) | 0.506 [-0.040, 0.762] p-val=0.0294 | 0.345 | 0.749 | ROBUST |
| `P4` | 14 (−2) | 0.464 [-0.163, 0.746] p-val=0.0497 | 0.287 | 0.594 | ROBUST |
| `P8` | 15 (−1) | 0.502 [-0.038, 0.745] p-val=0.0300 | 0.325 | 0.638 | ROBUST |

## A2 — stratified permutation tests

Observed Spearman 0.558 over 16 units.

| Strata | Sizes | One-sided permutation p-val (criterion permuted within strata) | Reading |
|---|---|---|---|
| within model | opus55x×5, qwen36×7, t2_qwen×2, t2_sonnet5×2 | p-val=0.0701 | pooled association not shown to hold within models |
| within prompt family | fuller_context×10, legacy×6 | p-val=0.9136 | pooled association not shown to hold within prompt families |

Within-model association (descriptive; fewer than 8 units, so no interval and no test):

| Judge model | Units | Spearman | Kendall τ-b | Pearson | Note |
|---|---|---|---|---|---|
| `opus55x` | 5 | 0.600 | 0.400 | 0.716 | descriptive: fewer than 8 units, no interval and no test |
| `qwen36` | 7 | 0.643 | 0.429 | 0.494 | descriptive: fewer than 8 units, no interval and no test |
| `t2_qwen` | 2 | unavailable | unavailable | unavailable | not computed: fewer than 3 units |
| `t2_sonnet5` | 2 | unavailable | unavailable | unavailable | not computed: fewer than 3 units |

## A3 — criterion-noise-aware intervals

15 held-out tasks (45 items), 16 units, 10000 draws, seed 48; the point estimate is the registered 0.558.

| Interval | Resampled unit | 95% interval | Defined draws | Undefined draws | Draws with < 8 computable units |
|---|---|---|---|---|---|
| (a) task bootstrap only | held-out task (3 items move together) | [0.412, 0.783] p-val=n/a | 10000 | 0 | 0 |
| (b) two-level, task then configuration | held-out task, then judge configuration within the draw | [0.073, 0.871] p-val=n/a | 10000 | 0 | 0 |

Two-level lower bound above 0: True; above 0.45: False. Mean task-only Spearman across draws 0.587. Per-unit criterion SD over task draws (criterion estimation noise, 45 items): `opus55x|D0` 0.209, `opus55x|H0` 0.187, `opus55x|H2` 0.092, `opus55x|LEX` 0.237, `opus55x|P4` 0.215, `qwen36|D0` 0.115, `qwen36|H0` 0.099, `qwen36|H1` 0.073, `qwen36|LEX` 0.171, `qwen36|P1` 0.190, `qwen36|P4` 0.138, `qwen36|P8` 0.212, `t2_qwen|D0` 0.105, `t2_qwen|H2` 0.071, `t2_sonnet5|D0` 0.139, `t2_sonnet5|H2` 0.073.
Draws in which a unit's criterion was NOT_COMPUTABLE (coverage below 90% of the drawn items): `opus55x|D0` 1608, `qwen36|D0` 1608, `qwen36|LEX` 18, `t2_qwen|D0` 1608, `t2_sonnet5|D0` 1608.

## A4 — rater views of the criterion

Registered target check: max |mean of available raters 1–3 ÷ 5 − `target_expert`| = 0.0e+00 over 45 items (18 items without rater 3).

| Target | Declared items | Computable units | Spearman [95% configuration bootstrap] p-val (configuration permutation) | Kendall τ-b | Pearson | Reading |
|---|---|---|---|---|---|---|
| single_p1 | 45 | 16/16 | 0.575 [0.120, 0.812] p-val=0.0115 | 0.410 | 0.644 | ROBUST |
| single_p2 | 45 | 16/16 | 0.596 [0.130, 0.771] p-val=0.0097 | 0.360 | 0.659 | ROBUST |
| single_p3 | 27 | 12/16 | 0.608 [0.134, 0.878] p-val=0.0204 | 0.455 | 0.501 | ROBUST |
| single_p4 | 45 | 16/16 | 0.500 [-0.076, 0.890] p-val=0.0250 | 0.377 | 0.355 | ROBUST |
| single_p5 | 45 | 16/16 | 0.517 [0.039, 0.775] p-val=0.0206 | 0.293 | 0.511 | ROBUST |
| all_available_raters_mean | 45 | 16/16 | 0.555 [0.103, 0.788] p-val=0.0154 | 0.360 | 0.636 | ROBUST |
| leave_out_p1 | 45 | 16/16 | 0.568 [0.112, 0.793] p-val=0.0124 | 0.360 | 0.621 | ROBUST |
| leave_out_p2 | 45 | 16/16 | 0.684 [0.265, 0.903] p-val=0.0021 | 0.494 | 0.583 | ROBUST |
| leave_out_p3 | 45 | 16/16 | 0.595 [0.154, 0.792] p-val=0.0096 | 0.377 | 0.638 | ROBUST |
| leave_out_p4 | 45 | 16/16 | 0.528 [0.054, 0.765] p-val=0.0198 | 0.326 | 0.648 | ROBUST |
| leave_out_p5 | 45 | 16/16 | 0.572 [0.124, 0.774] p-val=0.0125 | 0.377 | 0.643 | ROBUST |
| registered_target_expert | 45 | 16/16 | 0.558 [0.091, 0.764] p-val=0.0159 | 0.360 | 0.643 | ROBUST |

Range over rater views: min 0.500 (`single_p4`), max 0.684 (`leave_out_p2`).

## A5 — reference-quality views of the criterion items

Placeholder-reference tasks: `0_unsafeCopy_safe`, `1_unsafeMultiply_safe`, `4_unsafeCounter_safe`; ambiguous-reference tasks: `binary_search`, `insertion_sort`, `merge_sort` (flags from VeriBench experiment 100's `items.jsonl`; views as in experiment 44).

| View | Items / tasks | Computable units | Spearman [95% configuration bootstrap] p-val (configuration permutation) | Kendall τ-b | Pearson | Reading |
|---|---|---|---|---|---|---|
| original45 | 45 / 15 | 16/16 | 0.558 [0.091, 0.764] p-val=0.0159 | 0.360 | 0.643 | ROBUST |
| no_placeholder_reference_tasks | 36 / 12 | 16/16 | 0.545 [0.039, 0.769] p-val=0.0175 | 0.343 | 0.719 | ROBUST |
| no_ambiguous_reference_tasks | 36 / 12 | 16/16 | 0.543 [0.087, 0.777] p-val=0.0177 | 0.360 | 0.582 | ROBUST |
| neither_placeholder_nor_ambiguous | 27 / 9 | 16/16 | 0.530 [0.084, 0.781] p-val=0.0207 | 0.360 | 0.581 | ROBUST |
| test_tasks_only30 | 30 / 10 | 16/16 | 0.528 [0.075, 0.758] p-val=0.0199 | 0.326 | 0.591 | ROBUST |

Minimum over the four pre-registered reference-quality views: 0.530 (`neither_placeholder_nor_ambiguous`).

## A6 — attenuation bound (descriptive)

| Quantity | Value | Units | Note |
|---|---|---|---|
| Criterion split-half (Spearman / Kendall / Pearson) | 0.928 / 0.750 / 0.913; Spearman–Brown 0.963 | 47 LLM configurations | 15 validation-task items vs 30 test-task items |
| `C_ms_gold` split-half (Spearman / Kendall / Pearson) | 0.888 / 0.712 / 0.866; Spearman–Brown 0.941 | 54 LLM configurations | odd (12) vs even (12) gold ladders in sorted key order |
| Disattenuated test Spearman | 0.586 (Spearman–Brown reliabilities); 0.615 (raw half correlations) | 16 units | a bound from unequal halves (15 vs 30 items; 12 vs 12 ladders), not a population estimate; values above 1 are reported as computed |

## Deviations

Recorded in `results.md`; none affect the pre-registered views unless listed there.
