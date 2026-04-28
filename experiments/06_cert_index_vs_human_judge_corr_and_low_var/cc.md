# Experiment 06: Trust-index → human correlation + reliability

Follow `~/agents-config/INDEX_RULES.md` throughout (writing rules, experiment
folder convention, Mega QA workflow, email-via-uutils completion rule,
PR + QA gating).

## Scientific question

Across LLM judges, does our trust index predict each judge's correlation
with human ratings, AND is the relationship reliable (low variance) under
the deployed protocol?

A judge is trustworthy iff BOTH:

(a) High correlation with humans across:
   - Spearman, Kendall τ, Pearson r, R²
   - ICC(3,1) absolute agreement (primary)
   - ICC(3,k) absolute agreement (for trust-index-v1 as ensemble rater)
   - Lin's CCC (robustness check)

   NO ICC(2,_) — judges/humans are fixed, not sampled from a population.

   **Scale verification (do NOT re-normalize already-normalized data):**
   - Judge scores are returned in [0,1] by exp16's `_score_once`
     (see `experiments/04_veribench_validation/exp16_multi_judge_human_sets.py:222–248`).
     Confirm at smoke-test time and document in `REPORT.md`.
   - Human labels are 1–5 raw; the loader divides by 5
     (`exp16_multi_judge_human_sets.py:598`: `float(h)/5.0`),
     producing [0,1].
   - Both inputs are therefore already in [0,1] before ICC/CCC. Do NOT
     divide by 10 or apply additional re-scaling. If a smoke-test
     observation contradicts this, document the deviation in `REPORT.md`
     under "Open questions for Ethan" and proceed with whatever range
     is empirically observed.

(b) Low variance under repeated calls. The judge unit is
   `(LLM + prompt + n_repeats + aggregation)`. Report variance under
   both mean and median aggregation side-by-side.

## Pre-commit protocol — LOCKED, do not change after seeing results

- `JUDGE_REPEATS = 9`
- `REPEAT_AGG = median` primary, `mean` reported as ablation
- **Trust-index v1 as headline; v2 as appendix ablation.**

  Pre-commit reasoning for the v1 headline (write into `PROTOCOL.md`):
  v1 is the canonical certification index defined first in §2 of the
  paper. v2 is an extension introduced as an ablation. Keeping v1 as
  the headline is the conservative pre-commit choice — using the
  simpler/canonical form for the main story and the extension as the
  ablation. The choice is made before this run, regardless of which
  has higher correlation in the final results.

- Bootstrap 10K (item-level), permutation 20K
- Per-judge human-Spearman with both 95% CI and SE
- Headline figure (paper Fig 7) uses v1 on x-axis
- All 3 label sets (Annotator-A R₁, R₂, avg); headline = avg

Write `PROTOCOL.md` with these locked parameters BEFORE any expensive run.
Report every variant tried in `REPORT.md`. No silent post-hoc parameter
changes — if a smoke test reveals an assumption is wrong, document the
issue in `REPORT.md`, make a defensible choice, and proceed.

## Folder

`experiments/06_cert_index_vs_human_judge_corr_and_low_var/`
(per `~/agents-config/workflows/expts-and-results.md` convention)

Existing infrastructure (do NOT modify):

- `experiments/04_veribench_validation/run_exp16_multi_judge_human_sets.sh`
- `experiments/04_veribench_validation/exp17_property_human_analysis.py`
- `experiments/04_veribench_validation/exp19_replot_low_variance.py`

## Steps

1. Set `ANTHROPIC_API_KEY` from `~/keys/anthropic_bm_key_koyejolab.txt`;
   confirm `OPENAI_API_KEY`. Write `PROTOCOL.md`.

2. **Smoke test (3 repeats, 1K bootstrap, MIXED Claude+Codex panel to catch
   model-side breakage cheaply):**

   ```bash
   JUDGES="llm:claude-sonnet-4-20250514:P8_STRICT_B,llm:claude-sonnet-4-20250514:P4_CHECKLIST,llm:claude-sonnet-4-20250514:P1_BASELINE,llm_bad:claude-sonnet-4-20250514:BAD_STRINGY,llm:gpt-5.3-codex:P8_STRICT_B,editdist:e1:na,random:r1:na" \
   JUDGE_REPEATS=3 REPEAT_AGG=median BOOTSTRAP_ITERS=1000 PERM_ITERS=2000 \
   OUT_DIR=experiments/06_cert_index_vs_human_judge_corr_and_low_var/smoke \
   bash experiments/04_veribench_validation/run_exp16_multi_judge_human_sets.sh
   ```

   If the smoke test fails, diagnose, fix the most likely cause (auth,
   path, missing dependency), and retry. Document what failed and how
   you fixed it in `REPORT.md` under "Open questions for Ethan." Only
   proceed to step 3 once a smoke test produces a valid `summary.json`
   (judges listed, no NaN flood, plausible correlations).

3. **Full run — median (Claude + Codex mixed panel):**

   ```bash
   JUDGES="llm:claude-sonnet-4-20250514:P8_STRICT_B,llm:claude-sonnet-4-20250514:P4_CHECKLIST,llm:claude-sonnet-4-20250514:P1_BASELINE,llm_bad:claude-sonnet-4-20250514:BAD_STRINGY,llm:gpt-5.3-codex:P8_STRICT_B,llm:gpt-5.3-codex:P4_CHECKLIST,llm:gpt-5.3-codex:P1_BASELINE,editdist:e1:na,random:r1:na" \
   JUDGE_REPEATS=9 REPEAT_AGG=median BOOTSTRAP_ITERS=10000 PERM_ITERS=20000 \
   OUT_DIR=experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/median \
   bash experiments/04_veribench_validation/run_exp16_multi_judge_human_sets.sh
   ```

   Stream progress to a log file inside `OUT_DIR`.

4. **Full run — mean** (same `JUDGES`, `REPEAT_AGG=mean`,
   `OUT_DIR=.../full_run/mean`) for the variance ablation.

   *Cost note (verified):* The underlying LLM judging is cached at
   `experiments/02_reviewer_response_neurips_math_ai_2026/utils/results/judge_cache.json`
   with cache key
   `"exp16:{judge_id}|{model}|{prompt_hash}|{gold_hash}|{cand_hash}"`
   (see `judge_caller.py:258–263`). The cache key does NOT depend on
   `REPEAT_AGG`, so this re-aggregation hits cache for every LLM call
   and does NOT re-spend Anthropic / OpenAI budget — it only re-runs
   the post-aggregation pipeline. If you observe `cached: false` in
   any result dict during step 4, STOP and document the cause in
   `REPORT.md` before proceeding.

5. **Exp17 on both aggregations × 3 label sets:**

   ```bash
   for AGG in median mean; do
     for LABEL in pass1 pass2 avg; do
       python -u experiments/04_veribench_validation/exp17_property_human_analysis.py \
         --exp16-summary experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/${AGG}/summary.json \
         --out-dir       experiments/06_cert_index_vs_human_judge_corr_and_low_var/exp17/${AGG}_${LABEL} \
         --label-set     ${LABEL} \
         --perm-iters 20000 --seed 42 \
         --bad-judge-pattern "BAD_STRINGY"
     done
   done
   ```

6. **Exp19 replot (median):**

   ```bash
   python experiments/04_veribench_validation/exp19_replot_low_variance.py \
     --detail-rows experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/median/detail_rows.csv \
     --judge-rows  experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_run/median/judge_rows.csv \
     --out-dir     experiments/06_cert_index_vs_human_judge_corr_and_low_var/exp19 \
     --repeat-agg  median
   ```

7. **Full trust-metric panel.** Write a script that reads
   `detail_rows.csv` + exp17 outputs and produces, per (judge × label set):
   - Spearman, Kendall τ, Pearson r, R²
   - ICC(3,1), ICC(3,k)
   - Lin's CCC

   Operate directly on the [0,1]-normalized values produced by the
   loader (judge: native [0,1]; human: divided by 5 in the loader).
   Document the no-further-norm choice in `REPORT.md`. Also report
   per-item variance under mean vs. median.
   Output to `experiments/06_cert_index_vs_human_judge_corr_and_low_var/full_trust_metrics/`.

8. **`REPORT.md`** per writing-rules conventions:
   - locked protocol
   - headline numbers (all metrics)
   - per-property table
   - mean-vs-median variance table
   - comparison vs. Codex-only baseline
   - anomalies
   - transparency self-check (every variant tried, every defensible
     best-effort decision made when something was ambiguous)
   - **"Open questions for Ethan"** section listing anything that needs
     his review.

## Manuscript update — TRANSPARENT

Update `paper_latex/NeurIPS_2025/mathai_neurips2025_template/` following
`~/agents-config/writing/ml_research_writing.md`:

- Abstract: new headline numbers AS THEY ACTUALLY ARE. If trust-index→
  human Spearman shifted from 0.88 to 0.79 with the expanded panel,
  report 0.79. No cherry-picking subsets.
- §4.4: all 5 correlation metrics + ICC(3,1)/(3,k) + CCC.
- Add reliability subsection with mean-vs-median variance comparison;
  justify median empirically.
- §3: reframe judge as `(LLM + prompt + n_repeats + aggregation)` tuple.
- Update Fig 7 (use v1 on x-axis, not v2) and Fig 8 with expanded panel.
- Rename pass1/pass2 → "Annotator-A rubric R₁" / "Annotator-A rubric R₂"
  throughout. Reframe Table 6 as within-rater across-rubric agreement.
- Limitations: state explicitly that humans = 1 annotator × 2 rubrics;
  note Elyas as planned independent second annotator.

## Closing

Run Mega QA per `~/agents-config/workflows/qa-correctness.md` before opening
the PR. Open PR titled
`"[Folder 06] Cross-model judge expansion + reliability + paper update for NeurIPS"`;
**assign to GitHub user `ehersch`** (Ethan Hersch's GitHub login is
`ehersch`, NOT `ethanhersch` — verified via PR #10 and Issue #11 in this
repo). Send completion email per Guideline 23 to `brandojazz@gmail.com`
(CC `ethanhersch@stanford.edu` — Stanford email recipient is `ethanhersch`)
with headline numbers, PR URL, and a list of open questions surfaced in
`REPORT.md`.

## Guardrails

- Don't modify `run_exp16_*`, `exp17_*`, `exp19_*` scripts — invoke via env
  vars only.
- Make defensible best-effort decisions when something is ambiguous (ICC
  form edge cases, missing-column workarounds, scale-norm choices). Log
  every such decision in `REPORT.md` → "Open questions for Ethan" so he
  can review and overturn in PR.
- If full run estimated >12 hr wall-clock, log the estimate in `REPORT.md`
  and proceed.
- Transparency clause: every parameter and variant tried goes in
  `REPORT.md`. No silent post-hoc parameter changes.
- The PR is the review gate. Ethan can request changes there.

## Identity / contact crib (verified)

- Ethan's GitHub login: `ehersch`
- Ethan's Stanford email: `ethanhersch@stanford.edu`
- Brando's primary email: `brandojazz@gmail.com`
- Anthropic key: `~/keys/anthropic_bm_key_koyejolab.txt`
