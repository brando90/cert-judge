# Experiment 67, interim judge-scored results: do the CertJudge and trustworthy-judge numbers start to get better? (11-24-2026, PST evening)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/RESULTS_interim_judged_11-24-2026.md>

**Cost (plain dollars):** about **$22.50 at list prices** (gpt-5.3-codex about $4.28, estimated from token counts at an assumed list price of $1.75 per M input and $14 per M output, not a billed figure; claude-opus-4-7 $18.21 as reported by the CLI; Qwen $0, lab GPU). **Out of pocket: about $4 on the Vals OpenAI key** (pay-per-call); the Opus calls ran on the Vals Claude plan (131 calls, until it hit its spend limit) and the Stanford Claude plan (169 calls); no extra charge on any plan.

## Headline (INTERIM: 250 ratings, 100 files, 25 tasks; the Wed 11-25 6 PM PT wave is not in)
- **Not yet better in the proper scores.** On the 100 new files, all three headline judges (gpt-5.3-codex, claude-opus-4-7, Qwen3-Coder-30B, each P8_STRICT_B, 3 repeats) are still **worse than the constant forecast** on RPS, CE and TVD, with intervals that exclude zero. RPS / CE / TVD, new set: Codex 0.243 / 2.05 / 0.75, Opus 0.217 / 1.84 / 0.69, Qwen 0.126 / 1.39 / 0.56, against the constant 0.070 / 0.87 / 0.36 (lower is better).
- **Correlations moved from negative to weakly positive, but are not significant.** Spearman on the new set: Codex 0.24, Opus 0.17, Qwen 0.23 (old set: -0.24 / -0.21 / -0.35); the intervals reach zero. Pooled over old + new (45 tasks, within-set ranks): 0.05 / 0.03 / 0.02, i.e. nothing. The human ceiling is about 0.88, so the judges are far from it.
- **Intervals got narrower with more tasks** (pooled Spearman width about 0.6 times the old one for Codex and Opus, 0.8 for Qwen), as predicted. A narrower interval around about zero says the judge ordering carries no signal we can measure yet, not that it improved.
- **CE-fit calibration does not beat the constant** on the new or pooled set for any judge (all intervals include 0); it beats Pearson-fit on CE for Codex and Opus (new and pooled), the layer-4 pattern of Corr vs CE.
- **The human side is nearly unchanged since this morning** (250 vs 247 ratings, 74% fives): what is new is the judge scores on the new files, not new human data. Verdict by the preregistered rule ("narrower interval AND stable or better point estimate"): **not yet** for the proper scores; **a weak first sign** only in the sign of the correlations on the new files.

TLDR-end: [cert judge] Interim (250 ratings, 25 tasks): the three headline judges are still worse than the constant on RPS, CE and TVD, and Spearman went from -0.2/-0.35 (old) to +0.17 to +0.24 (new, not significant), pooled about 0: not yet better.

## Setup (see the PREREG addendum, committed before any judge call: commit f752f27)
- Files: the 100 native frontier files of the VeriBench rating packet (25 tasks x 4 agents). Ratings: every filled integer `final_score_0_5` in the raters' live sheets at 11-24-2026 about 19:12 PST: 250 ratings (T05 100, T08 100, T12 30, T06 16, V04 3, V02 1; ids only). Old set: 59 artifacts / 20 tasks, saved experiment 67 scores. Pooled: 159 / 45.
- Judge score on a file = median of the 3 repeats (new) and the saved score (old); judge distribution = the 3 repeats binned to 0..5 plus Laplace alpha 0.5. Intervals: 95% percentile task-cluster bootstrap, 2,000 draws, seed 0. Pooled RPS/CE/TVD are item means beside a set-aware constant; pooled Spearman/Pearson use within-set ranks and z-scores.
- Harness and model per lane: gpt-5.3-codex through the OpenAI Responses API (Vals key), max_output_tokens 1024; claude-opus-4-7 through the Claude Code CLI (-p, no tools, minimal system prompt) on the Vals and Stanford plans; Qwen3-Coder-30B-A3B-Instruct on vLLM, one lab GPU (skampere1), max_tokens 256. 900 calls, 0 failures.
- Human reference: T05 vs T08 Spearman 0.635 [0.43, 0.78], exact agreement 0.66, within-1 0.99, QWK 0.757; two-rater ceiling for a judge about 0.88.

## Tables (RPS, CE, TVD first; Spearman and Pearson secondary)
### B1a. Proper scores per set: judge vs the constant forecaster (lower is better; 95% task-bootstrap)

| Judge | Set | RPS | const RPS | RPS minus const | CE | const CE | TVD | const TVD |
|---|---|---|---|---|---|---|---|---|
| Codex | old (59 files, 20 tasks) | 0.244 [0.206, 0.288] | 0.174 | 0.070 [0.026, 0.114] | 2.260 [2.161, 2.356] | 1.767 | 0.671 [0.618, 0.724] | 0.486 |
| Codex | new (100 files, 25 tasks) | 0.243 [0.205, 0.283] | 0.070 | 0.173 [0.116, 0.226] | 2.054 [1.915, 2.186] | 0.872 | 0.749 [0.698, 0.797] | 0.364 |
| Codex | pooled (159 files, 45 tasks) | 0.243 [0.215, 0.276] | 0.108 | 0.135 [0.096, 0.177] | 2.130 [2.030, 2.228] | 1.204 | 0.720 [0.682, 0.760] | 0.409 |
| Claude Opus | old (59 files, 20 tasks) | 0.271 [0.229, 0.319] | 0.174 | 0.097 [0.048, 0.148] | 2.301 [2.185, 2.409] | 1.767 | 0.689 [0.626, 0.751] | 0.486 |
| Claude Opus | new (100 files, 25 tasks) | 0.217 [0.175, 0.261] | 0.070 | 0.147 [0.095, 0.198] | 1.838 [1.643, 2.032] | 0.872 | 0.691 [0.628, 0.747] | 0.364 |
| Claude Opus | pooled (159 files, 45 tasks) | 0.237 [0.206, 0.271] | 0.108 | 0.129 [0.091, 0.170] | 2.010 [1.858, 2.149] | 1.204 | 0.690 [0.646, 0.733] | 0.409 |
| Qwen3-Coder | old (59 files, 20 tasks) | 0.217 [0.191, 0.248] | 0.174 | 0.044 [0.026, 0.061] | 2.106 [1.996, 2.221] | 1.767 | 0.618 [0.561, 0.678] | 0.486 |
| Qwen3-Coder | new (100 files, 25 tasks) | 0.126 [0.112, 0.142] | 0.070 | 0.057 [0.025, 0.085] | 1.390 [1.194, 1.600] | 0.872 | 0.562 [0.512, 0.618] | 0.364 |
| Qwen3-Coder | pooled (159 files, 45 tasks) | 0.160 [0.142, 0.179] | 0.108 | 0.052 [0.031, 0.072] | 1.655 [1.494, 1.811] | 1.204 | 0.583 [0.543, 0.623] | 0.409 |

### B1b. Secondary: correlations

| Judge | Set | Spearman | Pearson | Spearman width | RPS width |
|---|---|---|---|---|---|
| Codex | old (59 files, 20 tasks) | -0.24 [-0.60, 0.20] | -0.10 [-0.47, 0.28] | 0.80 | 0.082 |
| Codex | new (100 files, 25 tasks) | 0.24 [-0.01, 0.47] | 0.31 [0.05, 0.54] | 0.49 | 0.078 |
| Codex | pooled (159 files, 45 tasks) | 0.05 [-0.19, 0.29] | 0.16 [-0.06, 0.38] | 0.48 | 0.061 |
| Claude Opus | old (59 files, 20 tasks) | -0.21 [-0.51, 0.11] | -0.24 [-0.51, 0.07] | 0.62 | 0.090 |
| Claude Opus | new (100 files, 25 tasks) | 0.17 [-0.07, 0.39] | 0.36 [0.15, 0.55] | 0.46 | 0.086 |
| Claude Opus | pooled (159 files, 45 tasks) | 0.03 [-0.17, 0.21] | 0.14 [-0.09, 0.34] | 0.38 | 0.065 |
| Qwen3-Coder | old (59 files, 20 tasks) | -0.35 [-0.59, -0.06] | -0.37 [-0.61, -0.05] | 0.53 | 0.057 |
| Qwen3-Coder | new (100 files, 25 tasks) | 0.23 [0.00, 0.45] | 0.28 [0.06, 0.49] | 0.45 | 0.031 |
| Qwen3-Coder | pooled (159 files, 45 tasks) | 0.02 [-0.19, 0.24] | 0.04 [-0.21, 0.27] | 0.43 | 0.037 |

### B3. Calibrated forecasters, leave-one-task-out (difference, negative = first is better; 95% task-bootstrap)

| Judge | Set | Comparison | dRPS | dCE | dTVD |
|---|---|---|---|---|---|
| Codex | new | CE-fit minus CONST | -0.0002 [-0.0045, 0.0045] | -0.003 [-0.041, 0.040] | -0.002 [-0.023, 0.023] |
| Codex | new | CE-fit minus Pearson-fit | -0.0077 [-0.0172, 0.0031] | -0.144 [-0.276, -0.001] | -0.058 [-0.108, -0.002] |
| Codex | new | Pearson-fit minus CONST | 0.0075 [-0.0059, 0.0202] | 0.141 [-0.010, 0.285] | 0.057 [-0.007, 0.118] |
| Codex | pooled | CE-fit minus CONST | 0.0009 [-0.0023, 0.0045] | 0.004 [-0.021, 0.033] | 0.000 [-0.014, 0.017] |
| Codex | pooled | CE-fit minus Pearson-fit | -0.0050 [-0.0116, 0.0014] | -0.092 [-0.179, -0.009] | -0.036 [-0.071, -0.000] |
| Codex | pooled | Pearson-fit minus CONST | 0.0060 [-0.0025, 0.0154] | 0.096 [0.006, 0.195] | 0.036 [-0.004, 0.079] |
| Claude Opus | new | CE-fit minus CONST | -0.0017 [-0.0069, 0.0040] | -0.015 [-0.058, 0.034] | 0.000 [-0.024, 0.028] |
| Claude Opus | new | CE-fit minus Pearson-fit | -0.0077 [-0.0167, 0.0023] | -0.148 [-0.282, -0.008] | -0.048 [-0.100, 0.011] |
| Claude Opus | new | Pearson-fit minus CONST | 0.0061 [-0.0080, 0.0195] | 0.133 [-0.031, 0.286] | 0.048 [-0.016, 0.110] |
| Claude Opus | pooled | CE-fit minus CONST | -0.0013 [-0.0049, 0.0025] | -0.010 [-0.040, 0.022] | -0.000 [-0.016, 0.018] |
| Claude Opus | pooled | CE-fit minus Pearson-fit | -0.0050 [-0.0115, 0.0013] | -0.095 [-0.185, -0.009] | -0.028 [-0.064, 0.008] |
| Claude Opus | pooled | Pearson-fit minus CONST | 0.0036 [-0.0051, 0.0133] | 0.084 [-0.016, 0.194] | 0.028 [-0.014, 0.072] |
| Qwen3-Coder | new | CE-fit minus CONST | -0.0009 [-0.0039, 0.0021] | -0.010 [-0.039, 0.019] | -0.007 [-0.020, 0.007] |
| Qwen3-Coder | new | CE-fit minus Pearson-fit | -0.0073 [-0.0164, 0.0029] | -0.140 [-0.269, 0.002] | -0.052 [-0.104, 0.005] |
| Qwen3-Coder | new | Pearson-fit minus CONST | 0.0064 [-0.0052, 0.0172] | 0.131 [-0.013, 0.253] | 0.045 [-0.014, 0.100] |
| Qwen3-Coder | pooled | CE-fit minus CONST | -0.0024 [-0.0065, 0.0013] | -0.014 [-0.040, 0.011] | -0.006 [-0.015, 0.005] |
| Qwen3-Coder | pooled | CE-fit minus Pearson-fit | -0.0045 [-0.0109, 0.0017] | -0.090 [-0.175, -0.004] | -0.030 [-0.066, 0.006] |
| Qwen3-Coder | pooled | Pearson-fit minus CONST | 0.0022 [-0.0058, 0.0106] | 0.075 [-0.013, 0.165] | 0.025 [-0.014, 0.065] |

Levels (RPS / CE / TVD):

| Judge | Set | CONST | CE-fit | Pearson-fit |
|---|---|---|---|---|
| Codex | new | 0.0698 / 0.872 / 0.364 | 0.0696 / 0.868 / 0.362 | 0.0773 / 1.012 / 0.420 |
| Codex | pooled | 0.1084 / 1.204 / 0.409 | 0.1093 / 1.208 / 0.409 | 0.1144 / 1.300 / 0.445 |
| Claude Opus | new | 0.0698 / 0.872 / 0.364 | 0.0681 / 0.856 / 0.364 | 0.0759 / 1.005 / 0.412 |
| Claude Opus | pooled | 0.1084 / 1.204 / 0.409 | 0.1070 / 1.193 / 0.409 | 0.1120 / 1.288 / 0.437 |
| Qwen3-Coder | new | 0.0698 / 0.872 / 0.364 | 0.0689 / 0.862 / 0.357 | 0.0762 / 1.002 / 0.409 |
| Qwen3-Coder | pooled | 0.1084 / 1.204 / 0.409 | 0.1060 / 1.189 / 0.403 | 0.1105 / 1.279 / 0.434 |

### B4. Learning curves over random k tasks (median over draws)

| Judge | Set | k tasks | Spearman median | Spearman width | dRPS median | dRPS width |
|---|---|---|---|---|---|---|
| Codex | new | 5 | 0.22 | 1.08 | 0.172 | 0.239 |
| Codex | new | 10 | 0.23 | 0.67 | 0.172 | 0.134 |
| Codex | new | 15 | 0.24 | 0.42 | 0.170 | 0.096 |
| Codex | new | 20 | 0.23 | 0.26 | 0.175 | 0.056 |
| Codex | new | 25 | 0.24 | nan | 0.173 | nan |
| Codex | pooled | 10 | 0.06 | 0.87 | 0.133 | 0.159 |
| Codex | pooled | 20 | 0.05 | 0.55 | 0.134 | 0.095 |
| Codex | pooled | 30 | 0.05 | 0.35 | 0.134 | 0.061 |
| Codex | pooled | 40 | 0.05 | 0.18 | 0.136 | 0.029 |
| Codex | pooled | 45 | 0.05 | nan | 0.135 | nan |
| Claude Opus | new | 5 | 0.16 | 0.98 | 0.146 | 0.220 |
| Claude Opus | new | 10 | 0.17 | 0.60 | 0.146 | 0.130 |
| Claude Opus | new | 15 | 0.17 | 0.40 | 0.148 | 0.093 |
| Claude Opus | new | 20 | 0.17 | 0.24 | 0.148 | 0.057 |
| Claude Opus | new | 25 | 0.17 | nan | 0.147 | nan |
| Claude Opus | pooled | 10 | 0.02 | 0.74 | 0.127 | 0.147 |
| Claude Opus | pooled | 20 | 0.02 | 0.46 | 0.127 | 0.088 |
| Claude Opus | pooled | 30 | 0.03 | 0.29 | 0.129 | 0.058 |
| Claude Opus | pooled | 40 | 0.03 | 0.14 | 0.130 | 0.027 |
| Claude Opus | pooled | 45 | 0.03 | nan | 0.129 | nan |
| Qwen3-Coder | new | 5 | 0.20 | 0.89 | 0.059 | 0.124 |
| Qwen3-Coder | new | 10 | 0.22 | 0.59 | 0.057 | 0.074 |
| Qwen3-Coder | new | 15 | 0.23 | 0.38 | 0.056 | 0.050 |
| Qwen3-Coder | new | 20 | 0.23 | 0.23 | 0.057 | 0.031 |
| Qwen3-Coder | new | 25 | 0.23 | nan | 0.057 | nan |
| Qwen3-Coder | pooled | 10 | 0.05 | 0.87 | 0.050 | 0.075 |
| Qwen3-Coder | pooled | 20 | 0.03 | 0.46 | 0.052 | 0.045 |
| Qwen3-Coder | pooled | 30 | 0.03 | 0.33 | 0.051 | 0.032 |
| Qwen3-Coder | pooled | 40 | 0.02 | 0.17 | 0.052 | 0.014 |
| Qwen3-Coder | pooled | 45 | 0.02 | nan | 0.052 | nan |

## Predictions (written before the run) and what happened
1. *Spearman positive, 0.2 to 0.7, below the ceiling:* **partly failed.** Point estimates are positive for all three (Codex 0.24, Qwen 0.23, Opus 0.17) and above the old negative values, but Opus is below the 0.2 floor and the intervals of Codex (-0.01, 0.47) and Opus (-0.07, 0.39) include 0; only Qwen's reaches 0.00 from above, and Qwen's score takes only 3 distinct values (97% ties).
2. *Raw RPS on the new set lower than on the old set, but not below the constant:* **holds for the part about the constant** (every judge is worse than the constant by 0.06 to 0.17 RPS); **raw RPS lower than old:** Opus 0.217 vs 0.271 and Qwen 0.126 vs 0.217 yes, Codex 0.2428 vs 0.2437 only by 0.001, which is no change. The lower raw RPS is mostly the easier new set (74% fives, so the constant itself is at 0.070), not a better judge.
3. *Pooled Spearman interval about 0.6 to 0.7 of the old one:* **holds for Codex (0.60) and Opus (0.61), fails for Qwen (0.81).** RPS interval widths pooled / old: 0.75, 0.72, 0.65.
4. *CE-fit does not beat CONST on the new set:* **holds** (CE-fit minus CONST dCE -0.003, -0.015, -0.010; all intervals include 0).
5. *Rank order of the series differs from the old set:* **holds.** By RPS the old order is Qwen, Codex, Opus (0.217, 0.244, 0.271); new is Qwen, Opus, Codex (0.126, 0.217, 0.243). By Spearman the old order is Codex, Opus, Qwen; new is Codex, Qwen, Opus.

## Verdict versus the earlier numbers
| Judge | Old RPS | New RPS | Old Spearman | New Spearman | Pooled Spearman (within set) |
|---|---|---|---|---|---|
| Codex | 0.244 | 0.243 | -0.24 | 0.24 | 0.05 |
| Opus | 0.271 | 0.217 | -0.21 | 0.17 | 0.03 |
| Qwen | 0.217 | 0.126 | -0.35 | 0.23 | 0.02 |

Better in the sign of the correlation on the new native files; not better against the constant forecast, not better on CE or TVD relative to the constant, and about zero when old and new are pooled within set. The old set and the new set are different files, so the comparison is not like for like; the human ratings of the new set are mostly 5s (ceiling effect), which both lowers raw RPS and makes the constant hard to beat.

## Appendix: caveats
- **Interim.** 2 to 3 ratings per file (52 files with 2, 46 with 3, 2 with 4), and only +3 ratings since the morning run. The refresh after the Wed 11-25 6 PM PT wave is a separate step.
- **Opus lane mix.** 131 calls ran on the Vals Claude plan and 169 on the Stanford Claude plan (same model id, claude-opus-4-7). The Vals lane hit its individual spend limit; 12 failed rows were dropped and re-run on the Stanford lane. The old saved Opus scores came from the Anthropic API with no system prompt; the harness here differs, so the old and new Opus numbers are not identical in harness.
- **gpt-5.3-codex** used max_output_tokens 1024 (paper run 256), because a reasoning model can spend a small cap before it answers.
- **Reference** is the last theorem block of the gold reference.lean only; the generated text is the whole agent file. No Lean check of the new files was run.
- **Ties.** Share of tied scores on the new files: Codex 0.77 (23 distinct values), Opus 0.90 (10), Qwen 0.97 (3). Repeat SD: 0.053, 0.018, 0.023. Spearman on such scores is coarse; read it with the proper scores.
- **Cost figure for gpt** is an estimate from token counts (2,278,644 input, 21,236 output) at an assumed list price, not a billed amount.
- Raw ratings and rater names are not in the repository; only aggregates. Judge outputs per call are on the lab host and in the run's scratch.
- Files: `results/interim_11-24-2026/` (judged_B1, B3, B4 csv, judged_summary.json, new_log.txt, tables_interim.md); code `scripts/run_new.py` (flags `--judge-scores`, `--judged-only`, `--out-tag`) and `scripts/make_tables_interim.py`.
