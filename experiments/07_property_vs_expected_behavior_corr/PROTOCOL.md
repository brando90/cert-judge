# Folder 07 — PROTOCOL (LOCKED before any expensive run)

This file freezes the protocol before analysis begins. It is written
PRIOR to seeing any results. Any deviation observed during execution
is documented in `REPORT.md` → "Open questions for Ethan", not by
editing this file.

## Scientific question (locked)

For each judge in the expanded panel, do its individual properties
behave as the property definitions require, under the canonical
`(LLM + prompt + n_repeats + aggregation)` judge unit defined in §3 of
the paper?

A judge passes its property sanity checks iff ALL of the following hold,
on the data reused from Folder 06's `detail_rows.csv` (Mode A; no new
LLM-budget spend):

- **P1 Identity:** per-variant score ≥ 0.9 on STYLE, RENAME, REORDER
  (ALPHA isolated per the halting-problem argument; reported separately,
  not in pass/fail).
- **P2 Bug ladder:** per-judge Spearman ρ ≤ −0.7 on the L0..L4 ladder
  per judge × problem.
- **P4 Stability:** per-judge median Cronbach's α ≥ 0.9 over the
  `n_repeats=9` repeat scores per item.

P3 (spec ablation) is **explicitly out of scope** for this folder
(detail_rows.csv has no `property_spec` row_type) and is filed as
follow-up Folder 07c.

## Scope (locked)

Per-judge property sanity checks **for P1, P2, P4 only**.

P3 (spec ablation) is **explicitly out of scope** for this folder.
Folder 06's `detail_rows.csv` does not contain a `property_spec`
row_type — exp16's pipeline only writes
`{human_eval_union, property_identity, property_bug}`. P3 spec data
exists at
`data/file_equiv_08_19_2025/my_add_file_eq_with_missing_specs/` but is
consumed by a different pipeline
(`experiments/02_reviewer_response_neurips_math_ai_2026/exp3_multi_model.py`).
P3 expanded-panel rerun is filed as a follow-up: **Folder 07c**.

## Locked metrics & thresholds

- **P1 Identity**: per-variant score (STYLE / RENAME / REORDER / ALPHA).
  Pass: ≥0.9 on STYLE, RENAME, REORDER. ALPHA isolated per
  halting-problem argument (reported separately, not in pass/fail).
- **P2 Bug ladder**: Spearman ρ over L0..L4 per judge × problem.
  Pass: ρ ≤ −0.7.
- **P4 Stability**: per-item Cronbach's α over the n_repeats=9
  `repeat_scores`. Aggregate per-judge as the median α across items.
  Pass: per-judge median α ≥ 0.9.

  *Why repeat-variant and not prompt-variant:* `detail_rows.csv` records
  `repeat_scores` (n_repeats=9 LLM calls of the *same* prompt per item).
  It does not record prompt-variant rows. Cronbach's α over repeat
  scores measures repeat reliability of the canonical
  `(LLM + prompt + n_repeats + aggregation)` judge unit defined in §3.
  Prompt-variant α is a different metric requiring a new prompt-rewording
  generation step → deferred to **Folder 07b**.

## Locked analysis params

- All 5 metrics per (judge, property): Spearman, Kendall τ, Pearson r,
  R², weak-monotonicity %.
- 95% CI + SE on every correlation.
- Bootstrap iters = 10000.
- Permutation iters = 20000.
- Run on both `median` and `mean` `detail_rows` for parallel outputs.
- Pass/fail thresholds locked above. If they collapse the panel
  (0/N pass), do not relax — report the collapse as a finding.

## Verified data schema (Mode A)

Folder 06's `detail_rows.csv` schema is:
```
judge_id, row_type, item_key, score_mean, score_std, repeat_scores
```
- `row_type ∈ {human_eval_union, property_identity, property_bug}`
- `item_key` for `property_identity` = `"{problem}::{variant}"`
  (variant ∈ {STYLE, RENAME, REORDER, ALPHA})
- `item_key` for `property_bug` = `"{problem}::L{0..4}"`
- `repeat_scores` = JSON list of n_repeats=9 per-call scores

Long-form `(file, perturbation_type, perturbation_level, repeat, score)`
view is computed by an in-script reshape — NOT expected as literal
columns in `detail_rows.csv`.

## Pre-conditions for run

- Folder 06's full_run/{median,mean}/detail_rows.csv must exist
  (this folder reuses Folder 06's data — Mode A only).
- Folder 06's PROTOCOL.md must already be in place and frozen.

## Estimated wall-clock

- Mode A schema parse + reshape: ~minutes
- `run_property_analysis.py` per (judge × property × bootstrap): ~1 h
- Cross-judge tables: ~minutes
- REPORT.md + manuscript regen: ~hour

## Identity / contact crib (verified)

- Ethan's GitHub login: `ehersch`
- Ethan's Stanford email: `ethanhersch@stanford.edu`
- Brando's primary email: `brandojazz@gmail.com`
