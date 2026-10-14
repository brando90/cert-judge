# Experiment 48 — PROTOCOL (LOCKED before any number is computed)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/48_c_ms_gold_heldout_judge_association_cluster_bootstrap_and_criterion_sensitivity/PROTOCOL.md>

**TLDR:** Zero-inference sensitivity study of experiment 39's held-out result (the gold deletion-monotonicity screen `C_ms_gold` versus judge–human agreement over the 18 held-out judge configurations: Spearman 0.558 [0.078, 0.762], one-sided permutation p-val=0.0127, 16 of 18 units). It asks whether that association survives (a) the clustering of configurations inside four judge models and nine prompts, (b) estimation noise in the criterion (15 tasks, 45 items), (c) the choice and number of expert raters, and (d) the reference quality of the criterion items. Every view is pre-declared here with its reading rule; the registered PASS verdict of experiment 39 is never re-litigated, only scoped.

Written before any statistic below was computed (10-14-2026). Deviations are recorded in `results.md` under "Deviations", never by editing this file; amendments are numbered and appended at the end and apply prospectively.

## Scientific question (locked)

Experiment 39 (`experiments/39_label_free_proxy_index_train_val_test_over_judge_families/`, archived as `experiments/archive/39_…` on the paper branch) selected `C_ms_gold` on the train and validation judge models and tested it once on the held-out judge models. Its 95% interval resamples configurations as if independent, although the 16 computable test units come from four judge models (Claude Opus 5.5, Qwen3.6-27B, Terminus2 + Claude Sonnet 5, Terminus2 + Qwen3.6-27B) and nine prompts, and its criterion is itself an estimate from 45 items rated by three experts. The paper branch already reports a prompt-group sensitivity (without the lexical prompt 0.453 [−0.177, 0.825]; fuller-context prompts only −0.371 [−0.787, 0.304]). This experiment pre-registers the remaining robustness views so that the paper can state the scope of the held-out claim with measured numbers instead of a verbal caveat.

**Central uncertainty (Trigger Rule 50).** Whether the pooled held-out association is carried by between-model or between-prompt-family differences, by particular raters, or by the placeholder- and ambiguous-reference tasks in the criterion; if it is, the claim "the screen transfers to held-out judges" must be narrowed before new human data are collected.

## Frozen inputs (hashed at first read; `results/input_manifest.json`)

| Input | Path | Use |
|---|---|---|
| Held-out test units | experiment 39 `results/units_test.json` (unlocked by commit `86ae479201e5`) | registered `C_ms_gold` and criterion values; the unit set |
| Train + validation units | experiment 39 `results/units_train_val.json` | descriptive train/validation views; split-half reliabilities |
| Per-cell judge scores | experiment 39 `results/harvest/<config>.json` (60 files) | per-item criterion cells (median of 3 repeats) and gold deletion ladders |
| Probe manifest | experiment 39 `results/probe_manifest.json` | structurally valid gold deletion ladders (24 ladders, 76 valid levels) |
| Registered test receipt | experiment 39 `results/TEST_RECEIPT.json` | the numbers gate G0 must reproduce |
| Expert ratings and reference flags | VeriBench experiment 100 `inputs/items.jsonl`, SHA-256 `ad9ed552fc2ffac6328e6010bf6be82215dd74f1eddd791622d433126877a96c` (75 items, 25 tasks; raters `p1`–`p5` on a 0–5 scale; `split`; `ref_placeholder_at_annotation`; `ref_ambiguous_in_window`) | criterion targets and item views |

Experiment 39's root is resolved at `experiments/39_…` first and `experiments/archive/39_…` second (the paper branch moves it). The VeriBench checkout is `CJ_VERIBENCH_REPO` (default `/Users/brandomiranda/veribench`); the items file is accepted only if its SHA-256 matches. Only `scripts/analysis_lib.py` of experiment 39 is imported (its tie-aware statistics, criterion, components and bootstrap), so every reproduced number uses the frozen code path.

## Gate G0 — reproduction (must PASS before any new number is read)

1. `analysis_lib.association(test_units, "C_ms_gold")` with 10,000 draws and seed 39 reproduces the receipt's test Spearman, interval and permutation p to 1e-9.
2. For every test unit, the held-out criterion Spearman recomputed from the harvest `crit` cells (median of the measured repeats) and `target_expert` matches `units_test.json` to 1e-9.
3. For every test unit, `C_ms_gold` recomputed with `analysis_lib.components` from the harvest and the manifest matches `units_test.json` to 1e-9 (including the two `None` units `qwen36|H2` and `qwen36|R4`, excluded by the frozen 80% ladder-coverage rule).
4. The criterion ranking reproducibility over the 56 LLM configurations (validation items versus test items) reproduces 0.928 to 3 decimals.

A G0 failure stops the experiment; the failure is reported, nothing else is computed.

## Units and fixed conventions

- The unit set is the 16 held-out configurations with a `C_ms_gold` value; it is never changed by a view. A view that makes a unit's criterion NOT_COMPUTABLE (fewer than 90% of the view's declared items scored, experiment 39's rule) drops that unit and reports the drop.
- Spearman (tie-aware, `cert_judge.pti_v0.spearman_rho`) is primary; Kendall τ-b and Pearson are reported beside every Spearman (Hard Rule 11). Intervals are 95% percentile bootstraps with 10,000 draws; draws with an undefined statistic are counted and reported. Permutation p-values are one-sided for a positive association, (k + 1)/(n + 1) over 10,000 draws. Seed 48 for new resampling; seed 39 only for the G0 reproduction.
- Thresholds: 0.45 is experiment 39's pre-registered gate (source: `PROTOCOL.md` of experiment 39); 0 is "no positive association". No new threshold is introduced.

## Pre-registered analyses

**A1 — Cluster-aware uncertainty.** (a) The registered configuration bootstrap (G0). (b) Judge-model cluster bootstrap: resample the four test judge models with replacement, keeping every unit of a drawn model; (c) prompt cluster bootstrap: resample the nine prompt keys present in the test units with replacement; (d) leave-one-model-out and leave-one-prompt-out point estimates with their minimum, median and maximum. Four model clusters admit only 35 distinct resamples, so (b) is reported with that limit and its count of draws with fewer than 8 units.

**A2 — Stratified permutation tests.** Permute criterion values within judge model (four strata) 10,000 times; the one-sided p-value answers whether `C_ms_gold` orders prompts within a model. Permute within prompt-rendering family (legacy P1/P4/P8/LEX versus fuller-context D0/H0/H1/H2/R4): whether the association survives removing the between-family difference. Descriptive within-model Spearman for Claude Opus 5.5 (5 units) and Qwen3.6-27B (7 computable units); the two Terminus2 models have two units each and are not correlated.

**A3 — Criterion-noise-aware intervals.** (a) Task bootstrap: resample the 15 held-out tasks with replacement (all three items of a task move together), recompute every unit's criterion Spearman from its per-item medians, then the outer Spearman over the fixed 16 units; (b) two-level: the task resample of (a) followed by a configuration resample within the same draw. Both reported as intervals with p-val=n/a.

**A4 — Rater views.** Criterion target = each single current rater (`p1`, `p2`, `p4`, `p5` on all 45 held-out items; `p3` on its 27 rated held-out items, reported with that coverage), the mean of all available current raters (five-rater target, experiment 45's view), and each leave-one-rater-out mean (five views). For every target: outer Spearman, Kendall, Pearson, configuration bootstrap interval and permutation p; the range over views is the headline.

**A5 — Reference-quality views of the criterion.** Items from tasks flagged `ref_placeholder_at_annotation` removed (36 items, 12 tasks), tasks flagged `ref_ambiguous_in_window` removed (36 items, 12 tasks), both removed (27 items, 9 tasks), matching experiment 44's views; the original 45 items and the 30 test-task items are reproduced beside them. Same statistics as A4.

**A6 — Attenuation bound (descriptive).** Split-half reliability of the criterion ranking (validation items versus test items, over the 56 LLM configurations; G0 item 4) and of `C_ms_gold` (odd versus even gold ladders in sorted key order, Spearman–Brown corrected), and the disattenuated test association ρ/√(r_criterion · r_proxy). The halves hold 15 versus 30 items and 12 versus 12 ladders; the number is a bound, not an estimate of a population correlation.

## Pre-declared readings (recorded before the numbers)

- For each view in A1(d), A4 and A5: **ROBUST** if Spearman ≥ 0.45 and, where a test is defined, p-val < 0.05; **WEAKENED** if 0 < Spearman < 0.45 or p-val ≥ 0.05; **REVERSED** if Spearman ≤ 0.
- A2: within-model p-val < 0.05 is read as "the association is present within judge models"; otherwise "the pooled association is not shown to hold within models". The same reading for the within-family test.
- A3: report whether the two-level interval's lower bound lies above 0 and above 0.45.
- The headline of the experiment is the triple (within-model p-val; minimum Spearman over the A5 views; two-level lower bound). Experiment 39's registered PASS is unchanged under every outcome; this experiment states its scope.

## Execution

- `python3 scripts/analyze_e48.py` from the repository root writes `results/*.json` and `RESULTS_heldout_association_sensitivity.md`; `python3 -m pytest scripts/test_e48.py` runs the offline tests. Pure Python plus experiment 39's `analysis_lib` (NumPy only if a parity test against `analysis_lib` passes on the full data). No model calls, no credentials, no network.
- Estimated wall-clock: under five minutes on a laptop.

## Amendments

_None._
