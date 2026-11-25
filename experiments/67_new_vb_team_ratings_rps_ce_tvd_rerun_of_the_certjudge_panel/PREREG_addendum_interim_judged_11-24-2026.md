# PREREG addendum (interim, judge-scored): experiment 67, headline CertJudge series on the 100 native VeriBench-packet files

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/PREREG_addendum_interim_judged_11-24-2026.md>

**Written 11-24-2026 (PST), about 19:30, committed before any judge call on the 100 files and before any judge-scored analysis.** This is an addendum to [PREREG.md](PREREG.md), which said judge scores on the new files were out of scope until a rating wave had arrived. Brando asked (11-24-2026 19:09, WhatsApp, voice) not to wait: run now on the sheets returned so far and see whether the judge results start to get better. Everything below is **interim**: the Wed 11-25 6 PM PT wave and the Thu 12-3 wave are not in.
Seen before writing this: the experiment 67 results (11-24-2026, old set), the human-side counts below, and one smoke call per lane on one file (to check the wiring; its score is not used anywhere).

## Data (frozen reading)
- **New set N (interim):** the 100 native frontier files (25 tasks x 4 agents). Ratings = every row with a filled integer `final_score_0_5` in the raters' live Sheets, read 11-24-2026 about 19:12 PST: **250 ratings** (T05 100, T08 100, T12 30, T06 16, V04 3, V02 1; ids only, no raw ratings or names in the repo), 100 files with at least 1 rating (52 with 2, 46 with 3, 2 with 4), 25 tasks. Against the 10:05 read of experiment 67 (247 ratings): +3 ratings (T05's sheet was also edited by its rater, 5:47 PM), so this interim run is nearly the same human data as the morning one.
- **Old set O:** the 59 artifacts / 20 tasks of H_vb (4 or 5 ratings each), with the saved judge scores of experiment 67 (unchanged).
- **Pooled P = O + N:** 159 artifacts, 45 tasks.

## Judges (the three headline series of experiment 67, each P8_STRICT_B, 3 repeats per file)
The prompt is the `P8_STRICT_B` template of `experiments/archive/02_neurips_reviews/utils/sensitivity_sweep.py`; the protocol is that of `exp16_multi_judge_human_sets.py` (reference = last theorem block of `gold_lean/reference.lean`; generated text = the whole agent file; one JSON score in [0,1] per call). Calls per series: 100 files x 3 repeats = 300 (900 in all).
- gpt-5.3-codex: OpenAI Responses API through the Vals key (the Vals lane), max_output_tokens 1024 (paper run: 256; a reasoning model can spend them before the answer).
- claude-opus-4-7: Claude Code CLI (`-p`, no tools, minimal system prompt) on the Vals Claude plan; paper run used the Anthropic API with no system prompt. Harness differs from the paper run, so it is not identical to the saved old scores.
- Qwen/Qwen3-Coder-30B-A3B-Instruct: vLLM, bf16, one GPU of skampere1 (the lab cluster), default sampling of the model's generation config, max_tokens 256; as the paper's Qwen run.
- No agy, no extra charges. Calls that fail 6 times, or answers that do not parse, are reported as failures and left out, never scored 0.5.

## Metrics and statistics (as PREREG.md)
RPS first (normalized, 6 categories 0..5), then CE and TVD, then Spearman and Pearson (secondary). Raw judge distribution = the 3 repeats binned to 0..5 plus Laplace alpha 0.5. Human distribution of a file = its returned ratings. Lower is better for RPS, CE, TVD. Every interval = 95% percentile interval of a task-cluster bootstrap (2,000 draws, seed 0), tasks resampled over the union of tasks in each table.

## Analyses
- **B1 per set:** per headline series on N: RPS / CE / TVD / Spearman / Pearson against the human distribution and mean; constant forecast (training marginal, leave-one-task-out) as reference. Same for O (saved scores; reproduces experiment 67 T1).
- **B2 pooled with set-aware scoring:** P over 45 tasks. RPS / CE / TVD are item means (set-level level shifts are therefore included, and reported next to a *set-aware* constant = the marginal of each item's own set, leave-one-task-out). Spearman and Pearson on **within-set ranks / within-set z-scores** (pooling within set), not on raw pooled scores.
- **B3 calibrated forecaster (layer 4 of Corr-vs-CE) on N:** leave-one-task-out CE-fit, Pearson-fit and CONST on N alone, held-out RPS / CE / TVD, paired differences with task-bootstrap intervals.
- **B4 widths:** interval widths for old, new, pooled, and a task-count learning curve (random k tasks) for the Spearman and for RPS.
- **B5 verdict versus earlier numbers:** compare with experiment 67 T1 (old set: RPS 0.244 / 0.271 / 0.217 and Spearman -0.24 / -0.21 / -0.35 for Codex / Opus / Qwen headline) and with the human-ceiling numbers.

## Predictions (written before the run)
1. On N, Spearman of each headline series with the human mean is positive and clearly above the old negative values (the new files are native frontier outputs rated by the VeriBench team), but below the N human ceiling (about 0.88 from two raters); point estimates between 0.2 and 0.7.
2. Raw RPS on N is lower (better) than on O for all three series, because 73% of N ratings are 5s and the judges' scores are high; but not below the constant forecast of N by more than the interval for at least one series.
3. Pooled interval widths (45 tasks) are narrower than old-alone widths (20 tasks) by a factor near 0.6 to 0.7 for Spearman, not near 1.
4. CE-fit does not beat CONST on N for any series with an interval below 0 (2 or 3 ratings per file, ceiling effect).
5. Rank order of the three series on N differs from their order on O.

## Decision rules
- "Starting to get better" is judged as in PREREG.md: a narrower task-bootstrap interval AND a stable or better point estimate on more tasks, with the human ceiling stated. A higher number with a wide interval is "not yet". Because only +3 ratings arrived since the morning, I state plainly that the human side is not new; what is new is the judge scores on N.
- Results that fail a prediction are reported as failed. Analyses added after seeing the results go in a labelled, dated post-hoc section.
- Cost is reported in dollars at list prices and as out-of-pocket (plan lanes: $0 extra; the Vals OpenAI key is pay-per-call, counted).
- The refresh after the 11-25 6 PM wave is a separate run (same scripts, same PREREG).
