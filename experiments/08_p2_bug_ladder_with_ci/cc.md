# Experiment 08: P2 bug-ladder with per-x 95% CI error bars

Follow `~/agents-config/INDEX_RULES.md` throughout (writing rules,
experiment-folder convention, Mega QA workflow, email-via-uutils completion
rule, PR + QA gating). This experiment is a measurement-rigor complement
to Folder 07's per-judge property sanity checks: it patches the original
veribench Figure 6 ("Bug Count vs LLM Judge File Equivalence Score") so
that uncertainty is *visible*, not absorbed into a single dot per bug count.

## Scientific question

When a single LLM judge is asked the same `(candidate, gold)` query
multiple times under non-deterministic decoding, how stable is the
reported P2 monotonicity signal — i.e. does the apparent
"score ↓ as bug count ↑" trend survive once per-x sampling uncertainty
is shown as 95% confidence intervals on each bug-count file?

Operational form:

- **P2-CI(judge):** for each bug count k ∈ {0, …, 9} on the
  `my_add_file_eq_with_bugs` ladder, draw `num_samples` independent
  judge calls and compute (mean, SE, 95% CI).
- Report Spearman ρ, Kendall τ, Pearson r, R², and OLS slope on
  *both* (a) per-call points (S·N) and (b) per-file means.
- Locked threshold (matches Folder 07 P2 lock): per-file Spearman
  ρ ≤ −0.7. If the per-call Spearman differs from per-file Spearman
  by more than 0.1 in absolute value, the sampling-noise channel is
  non-trivial and should be flagged as a finding.

### Why this experiment is needed

Verified problem in the original figure:

- `~/veribench/experiments/10_file_equiv/main.py:382` plots `ax.scatter`
  over the *flat S × N list* of every individual judge call. It never
  aggregates per bug count and never calls `ax.errorbar`.
- `~/veribench/experiments/10_file_equiv/main.sh:23` defaults
  `NUM_JUDGE_CALLS=1`. With one call per file × ten files, Figure 6's
  ten points are ten LLM calls — there is no within-x replication and
  therefore no per-x error bar can exist.
- Even at `NUM_JUDGE_CALLS > 1`, the plotter would still emit
  overlapping individual dots (identical color/size/alpha), not
  mean ± CI markers.

Folder 08 is the corrected, statistically-honest re-plot of the same
property on the same ladder.

### Out of scope, by design

- **Multi-judge panel.** Folder 07 already runs P1/P2/P4 across an
  expanded judge panel using cached `detail_rows.csv`. This folder
  is single-judge by design — its purpose is the per-x CI methodology
  and the figure replacement, not panel expansion. Multi-judge overlay
  is filed as **Folder 08b: cross-judge P2 CI overlay** (follow-up).
- **P3 spec ladder.** Folder 07c (filed) covers P3 expanded-panel
  rerun. The same per-x CI machinery here trivially extends to P3
  (only the filename regex changes); do NOT fork the runner — point
  `bug_ladder_path` at the spec ladder and adjust the regex inside
  `_parse_bug_count`. Document any such reuse in `REPORT.md`.
- **Sample-set (file resampling) uncertainty.** The default bootstrap
  resamples *judge calls within a file*. A second outer bootstrap that
  resamples files and refits the OLS slope is filed as
  **Folder 08c: P2 slope CI via file resampling** (follow-up).

## Pre-commit protocol — LOCKED, do not change after seeing results

- `num_samples = 15` (LLM calls per bug-count file)
- Default CI = t-based two-sided 95% on per-file means; bootstrap
  CI (percentile, 2000 iters) reported as ablation in `REPORT.md`
- Judge unit (matches Folder 07): `(LLM + prompt + n_repeats=15 + per-x mean)`
- Single-judge headline = the model selected via the active
  `claude_dotenv_path`; default `.env_claude_3_5_v1` (matches the
  original Figure 6 label "Claude 3.5 Sonnet")
- Bug ladder = `data/file_equiv_08_19_2025/my_add_file_eq_with_bugs/`
  (10 files, k = 0..9), gold = the k=0 file
- Both correlation flavors (per-call S·N points AND per-file means)
  reported on every figure; legend includes Pearson r, Spearman ρ,
  Kendall τ, R², and OLS slope
- Pass/fail (locked, matches Folder 07 P2 threshold):
  - per-file Spearman ρ ≤ −0.7 → judge passes P2 monotonicity
  - per-call vs per-file Spearman gap > 0.1 → flag sampling noise
    as a finding (does NOT fail the judge)

Write `PROTOCOL.md` with these locked parameters BEFORE any expensive
run. Report every variant tried in `REPORT.md`. No silent post-hoc
parameter changes — if a smoke test reveals an assumption is wrong,
document it in `REPORT.md` → "Open questions for Ethan", make a
defensible choice, and proceed.

## Folder

`experiments/08_p2_bug_ladder_with_ci/`
(per `~/agents-config/workflows/expts-and-results.md` convention)

```
experiments/08_p2_bug_ladder_with_ci/
  cc.md                              # this file
  PROTOCOL.md                        # locked params (mirror)
  run_p2_bug_ladder_with_ci.py       # runner: builds raw S x N matrix, aggregates, plots
  run_p2_bug_ladder_with_ci.sh       # wrapper: loads claude env, calls runner
  notes/                             # diagnostic notes from sub-runs
  smoke/                             # smoke-test outputs (small num_samples)
  full_run/
    {model_name}/
      raw_score_matrix.npy
      summary.json
      p2_bug_ladder_with_ci.png
```

## Steps

1. Set `ANTHROPIC_API_KEY` from the chosen `.env_claude_*` (the wrapper
   does this via `claude_dotenv_path`). Confirm `TRACE_CUSTOMLLM_MODEL`
   is exported before the Python process starts. Write `PROTOCOL.md`.

2. **Smoke test (3 samples, 1 judge, no WandB):**

   ```bash
   num_samples=3 wandb_off=1 \
     output_dir=experiments/08_p2_bug_ladder_with_ci/smoke \
     bash experiments/08_p2_bug_ladder_with_ci/run_p2_bug_ladder_with_ci.sh
   ```

   Smoke must produce a valid `summary.json` (10 files matched, NaN
   rate < 0.1, plausible per-file means descending in k) before the
   full run is launched. If it fails, diagnose and fix the most likely
   cause (auth, path, prompt parse), document the fix in `REPORT.md`
   under "Open questions for Ethan", and retry.

3. **Full run — primary (t-based CI, headline model):**

   ```bash
   num_samples=15 \
     output_dir=experiments/08_p2_bug_ladder_with_ci/full_run/claude_3_5_sonnet \
     bash experiments/08_p2_bug_ladder_with_ci/run_p2_bug_ladder_with_ci.sh
   ```

4. **Full run — ablation (bootstrap CI, same model):**

   ```bash
   bootstrap=1 num_samples=15 \
     output_dir=experiments/08_p2_bug_ladder_with_ci/full_run/claude_3_5_sonnet_bootstrap \
     bash experiments/08_p2_bug_ladder_with_ci/run_p2_bug_ladder_with_ci.sh
   ```

   The two CI flavors should agree to within ~0.02 on every per-x
   half-width when `num_samples >= 15` and scores are not boundary-stuck;
   document any wider disagreement in `REPORT.md`.

5. **(Optional) cross-model rerun.** Loop step 3 with alternate
   `claude_dotenv_path` values (e.g. `.env_claude_3_7`,
   `.env_claude_3_5_v2`) into distinct `output_dir`s. Do NOT bake
   multi-model logic into the runner — keep the runner single-judge.
   Cross-judge overlay is Folder 08b.

6. **`REPORT.md`** per writing-rules conventions:
   - locked protocol + thresholds (copy from `PROTOCOL.md`)
   - headline figure (the new P2 plot with 95% CI)
   - per-file table: `(k, n, mean, ci_lo, ci_hi, sem)`
   - per-call vs per-file correlation comparison
   - t-CI vs bootstrap-CI ablation table
   - cross-model headline numbers if step 5 was run
   - anomalies (boundary saturation at k=0 or large k; failed calls)
   - transparency self-check (every variant tried, every defensible
     best-effort decision made when something was ambiguous)
   - **"Open questions for Ethan"** section that includes:
     - "Should we keep the t-CI as headline or move to bootstrap given
       boundary saturation in this ladder?"
     - "Folder 08b (cross-judge overlay) and Folder 08c (file-resampling
       slope CI) — file as follow-ups now or later?"
     - any judge that fails per-file ρ ≤ −0.7 unexpectedly
     - any reshape/fallback decisions made in step 2

## Manuscript update — TRANSPARENT

Following `~/agents-config/writing/ml_research_writing.md`:

- Replace the original Figure 6 ("Bug Count vs LLM Judge File
  Equivalence Score") in
  `paper_latex/NeurIPS_2025/mathai_neurips2025_template/neurips_2025.tex`
  and `paper_latex/ICML_2026/sections/appendix.tex` with the new
  per-x 95% CI plot from step 3.
- Caption update: state explicitly that each marker is the mean of
  `num_samples=15` judge calls and that vertical bars are 95% CIs
  (t-based; bootstrap variant in appendix).
- In the figure-introducing paragraph, add one sentence acknowledging
  that the prior version of this figure rendered single LLM calls
  with no per-x replication, and that this rendering corrects the
  measurement-rigor issue without changing the underlying property
  definition.
- Update §3 P2 paragraph to cite the per-file Spearman ρ AND the
  per-call Spearman ρ side-by-side; if they disagree by more than
  0.1, report both and discuss the gap.
- Limitations: state that this is single-judge; the cross-judge
  overlay is filed as Folder 08b. Do NOT silently drop judges or
  cherry-pick the most monotonic model.

## Closing

Run Mega QA per `~/agents-config/workflows/qa-correctness.md` before
opening the PR. Open PR titled
`"[Folder 08] P2 bug-ladder with per-x 95% CI error bars + Fig 6 replacement"`;
**assign to GitHub user `ehersch`** (Ethan Hersch's GitHub login is
`ehersch`, NOT `ethanhersch` — verified via PR #10 / Issue #11). Send
completion email per Guideline 23 to `brandojazz@gmail.com`
(CC `ethanhersch@stanford.edu`) with headline numbers (per-file
Spearman ρ, OLS slope, NaN rate), PR URL, and the
"Open questions for Ethan" list.

## Guardrails

- The runner is single-judge by design. Don't bake multi-judge logic
  into `run_p2_bug_ladder_with_ci.py` — that's Folder 08b's job.
- Don't move the LLM call layer out of veribench. The runner imports
  `veribench.metrics.sim_file_eq_llm_judge.get_sim_score_file_eq_llm_result_in_json_str`
  exactly like Folder 00 does — keep it that way.
- Env vars must be loaded BEFORE Python starts (the wrapper
  `source`s the `.env_claude_*` file). `TRACE_CUSTOMLLM_MODEL`
  binds at module import time inside veribench.
- Pass/fail thresholds locked; do not adjust silently.
- Make defensible best-effort decisions when something is ambiguous;
  log every such decision in "Open questions for Ethan" so Ethan can
  overturn in PR review.
- Mega QA mandatory before PR.
- Transparency clause: every variant in `REPORT.md`; no post-hoc
  parameter changes.
- The PR is the review gate. Ethan can request changes there.

## Identity / contact crib (verified)

- Ethan's GitHub login: `ehersch`
- Ethan's Stanford email: `ethanhersch@stanford.edu`
- Brando's primary email: `brandojazz@gmail.com`
- Anthropic key path: `~/keys/anthropic_bm_key_koyejolab.txt`
