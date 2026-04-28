# Experiment 07: Per-judge property sanity checks (P1, P2, P4) on expanded panel

Follow `~/agents-config/INDEX_RULES.md` throughout. This experiment is the
within-judge complement to Folder 06 (across-judge trust-index → human).

## Scientific question

For each judge in the expanded panel, do its individual properties behave
as defined? Score correlation with perturbation level on the x-axis:

- **P1 Identity**: score = 1.0 when candidate = reference, per variant
  (STYLE / RENAME / REORDER / ALPHA reported separately)
- **P2 Bug ladder**: score ↓ as bug count k ↑ — target Spearman ρ ≤ −0.7
- **P4 Stability**: low variance across repeats. **Locked metric**:
  per-item Cronbach's α over the `n_repeats=9` repeated LLM calls per
  item; aggregate per-judge as the median α across items;
  threshold ≥ 0.9.

  *Why repeat-variant and not prompt-variant:* Folder 06's `detail_rows.csv`
  records `repeat_scores` (a JSON list of n_repeats LLM calls of the
  *same* prompt per item). It does NOT record prompt-variant rows
  (different semantically-equivalent prompts per judge). Cronbach's α
  over repeat scores measures *repeat reliability* of the
  `(LLM + prompt + n_repeats + aggregation)` judge unit — exactly the
  unit defined in §3. Prompt-variant α would measure something different
  (cross-prompt agreement) and require a new prompt-rewording generation
  step that does not exist in Folder 06's pipeline. **Prompt-variant
  stability is therefore deferred to a follow-up experiment "Folder 07b:
  prompt-variant stability".**

### P3 (spec ablation) scope note — out of scope, by design

P3 spec-ablation rows are **NOT** present in Folder 06's `detail_rows.csv`.
The exp16 pipeline (`experiments/04_veribench_validation/exp16_multi_judge_human_sets.py`)
writes only three `row_type` values:
`{human_eval_union, property_identity, property_bug}` (verified by
inspecting `results_exp16_final_robust/detail_rows.csv`). There is no
`property_spec`. The P3 spec-ablation data lives at
`data/file_equiv_08_19_2025/my_add_file_eq_with_missing_specs/` and is
consumed by `experiments/02_reviewer_response_neurips_math_ai_2026/exp3_multi_model.py`,
which is a different pipeline.

P3 is therefore **explicitly out of scope** for this experiment (Mode A
only). Do NOT attempt to manufacture P3 rows via a compatibility shim
— the data is genuinely absent. A follow-up experiment **"Folder 07c:
P3 spec-ablation on expanded judge panel"** should be filed separately
and is to be listed under `REPORT.md` → "Open questions for Ethan /
Future experiments".

## Pre-commit protocol — LOCKED

- Reuse Folder 06's `full_run/{median,mean}/detail_rows.csv` (Mode A)

  **Verified real schema of Folder 06's `detail_rows.csv`:**
  ```
  judge_id, row_type, item_key, score_mean, score_std, repeat_scores
  ```
  where:
  - `row_type ∈ {human_eval_union, property_identity, property_bug}`
  - `item_key` for `property_identity` = `"{problem}::{variant}"`
    (variant ∈ {STYLE, RENAME, REORDER, ALPHA})
  - `item_key` for `property_bug` = `"{problem}::L{0..4}"`
  - `repeat_scores` = JSON list of `n_repeats=9` per-call scores

  Step 2 (Mode A check) parses this schema directly. The
  `(file, perturbation_type, perturbation_level, repeat, score)`
  long-form view is computed by an in-script reshape, NOT expected as
  literal columns in `detail_rows.csv`.

- All 5 metrics per property: Spearman, Kendall τ, Pearson r, R²,
  weak-monotonicity %
- Per-judge variance under mean and median
- 95% CI + SE on every correlation; bootstrap 10K, permutation 20K
- **Pass/fail thresholds** (locked):
  - P1: ≥0.9 on STYLE/RENAME/REORDER; ALPHA isolated per
    halting-problem argument
  - P2: ρ ≤ −0.7
  - P4: per-judge median Cronbach's α ≥ 0.9 over the n_repeats=9
    repeat scores

Write `PROTOCOL.md` with these BEFORE running. If pass-fail thresholds
collapse the panel (0 of N pass), DO NOT relax them silently — keep the
locked thresholds and report the collapse as a finding in `REPORT.md`.

## Folder

```
experiments/07_property_vs_expected_behavior_corr/
  per_judge/{judge_id}/{p1,p2,p4}.csv + figures/
  cross_judge_summary/
    properties_table.csv         # one row per (judge, property)
                                 #  for P1/P2/P4
    pass_fail_certification.csv  # pass/fail per judge × property
```

(P3 outputs live in a separate folder filed as Folder 07c follow-up.)

## Steps

1. Write `PROTOCOL.md`.

2. **Mode A check**: read
   `experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/median/detail_rows.csv`.

   Verify `row_type` values (expect `{human_eval_union,
   property_identity, property_bug}`) and `item_key` parse:
   - `property_identity` rows: parse `{problem, variant}` from `item_key`
   - `property_bug` rows: parse `{problem, level=L0..L4}` from `item_key`

   For P4: explode the `repeat_scores` JSON list into per-repeat values
   for per-item Cronbach's α computation.

   If the schema differs from the verified spec above, document the
   deviation in `REPORT.md` → "Open questions for Ethan" and write a
   reshape function that bridges what's available to what's needed.
   If a column is genuinely missing and no reshape is feasible, fall
   back to running a single-property sub-pipeline from
   `experiments/04_veribench_validation/` for the affected property
   only; document the fallback. P3 is excluded by design (see scope
   note above) — do NOT attempt a shim for P3.

3. Write `run_property_analysis.py` reading `detail_rows.csv`, producing
   per-judge CSVs + figures + cross-judge tables for P1, P2, P4:
   - For P1 keep ALPHA isolated.
   - For P2 compute Spearman/Kendall/Pearson/R²/weak-monotonicity-% on
     the L0..L4 ladder per judge × problem; aggregate per-judge.
   - For P4 compute Cronbach's α over the 9-element `repeat_scores`
     list per (judge, item), then aggregate per-judge as the median α
     across items. Threshold: per-judge median α ≥ 0.9.
   - All 5 correlation metrics per (judge, property) with bootstrap CI
     + permutation p.

4. Run on both `median` and `mean` `detail_rows`; produce parallel outputs.

5. Pass/fail certification table using the locked thresholds.

6. **`REPORT.md`** per writing-rules:
   - locked protocol + thresholds
   - full per-judge per-property table
   - pass/fail summary
   - mean-vs-median comparison
   - ALPHA breakdown (input data for planned Exp 20)
   - anomalies
   - transparency self-check
   - **"Open questions for Ethan"** section that includes:
     - "P3 is out of scope; should we file Folder 07c as a follow-up
       with separate spec-ablation pipeline?"
     - "P4 is locked to repeat-variant Cronbach's α; prompt-variant
       stability deferred to Folder 07b — confirm this scope?"
     - any judge that fails a property unexpectedly
     - any reshape/fallback decisions made in step 2

## Manuscript update — TRANSPARENT

Following `~/agents-config/writing/ml_research_writing.md`:

- Regenerate §3 P1, P2, P4 sanity-check figures (currently Fig 1) with
  expanded judge panel. P3 figures remain on existing data; flag in
  limitations that P3 expanded-panel rerun is pending (Folder 07c).
- Add per-judge pass/fail certification table (P1/P2/P4) to appendix.
- In §3, document pre-committed thresholds and ALPHA exclusion via
  halting-problem argument; cite planned Exp 20 alpha-intensity ladder.
- Update Table 1 (Identity by variant) with expanded-panel numbers,
  keeping ALPHA isolation.
- If any judge fails P2 unexpectedly, REPORT IT — failures are
  findings, do not quietly drop judges.
- Update §4 numbers wherever Folder 07 contradicts current paper.

  *ρ_bug reconciliation:* The current paper cites
  Codex-only `ρ_bug ≈ −0.808`; the verified value from
  `results_exp16_final_robust/judge_rows.csv` is
  `bug_spearman_r = −0.776` for `gpt-5.3-codex|P8_STRICT_B`. Verify
  which number the paper actually cites and from which run before
  updating; do NOT silently overwrite. Document the reconciliation
  in `REPORT.md` → "Open questions for Ethan."

## Closing

Run Mega QA per `~/agents-config/workflows/qa-correctness.md`. Open PR
titled
`"[Folder 07] Per-judge property sanity checks (P1, P2, P4) + pass/fail certification + paper update for NeurIPS"`;
**assign to GitHub user `ehersch`** (Ethan's GitHub login is `ehersch`,
NOT `ethanhersch` — verified via PR #10 / Issue #11). Completion email
per Guideline 23 to `brandojazz@gmail.com` (CC `ethanhersch@stanford.edu`)
with headline numbers, pass/fail counts, PR URL, and the
"Open questions for Ethan" list.

## Guardrails

- Folder 06 data is read-only.
- Pass/fail thresholds locked; do not adjust silently.
- Make defensible best-effort decisions when something is ambiguous; log
  every such decision in "Open questions for Ethan" so he can overturn
  in PR review.
- Mega QA mandatory before PR.
- Transparency clause: every variant in `REPORT.md`; no post-hoc changes.
- The PR is the review gate. Ethan can request changes there.

## Identity / contact crib (verified)

- Ethan's GitHub login: `ehersch`
- Ethan's Stanford email: `ethanhersch@stanford.edu`
- Brando's primary email: `brandojazz@gmail.com`
