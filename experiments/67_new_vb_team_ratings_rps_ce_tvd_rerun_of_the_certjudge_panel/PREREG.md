# PREREG: experiment 67, re-run of the CertJudge panel with the VeriBench-team ratings, RPS / CE / TVD first

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/PREREG.md>

**Written 11-24-2026 (PST), committed before any analysis script of this experiment was run.** Zero model calls, CPU only, $0.
What the author had already seen when writing this: the experiment 51 output (11-20-2026: raw RPS / CE / TVD and scalar Spearman of the same 24 judge series), the experiment 41 report, and the inventory counts of the returned ratings (below). Nothing else of the results below was seen.

## Question (Brando, 11-24-2026 09:53 and 09:59, Slack)
New ratings from the VeriBench team are coming in. Do they make the CertJudge numbers (judge-vs-human correlations that looked too different from one split to another, with wide intervals) more trustworthy, and with the Corr-vs-CE finding (correlation is the wrong evaluation metric; use proper scores RPS, CE, TVD) what should the table show?

## Data (frozen reading)
- **Old set O:** the 72 judged (gold, candidate) pairs from 24 tasks, 8 judge series in each of 3 families (Codex, Claude Opus, Qwen3-Coder panels; 24 series), scores saved in `experiments/archive/04_veribench_validation` and `13_qwen_replication_exp16_exp19`. Human targets: **H_vb** = VeriBench participants 1 to 5 (corrected prompt, 4 or 5 ratings per item, 60 items from 20 tasks; the primary target) and **H_paper** = the paper's two old-prompt passes of one annotator (72 items, secondary: a superseded rubric, see experiment 41).
- **New set N:** the 100 native frontier files (25 tasks x 4 frontier agents, VeriBench rating packet of trustworthy-theorem-judges experiment 09) with the ratings returned **as of 11-24-2026 about 10:05 PST**, read from the raters' live Sheets: only rows with a filled `final_score_0_5` count. Per-rater returned counts: T05 100, T08 100, T12 30, T06 16, V04 1, everyone else 0 (247 ratings of 3,300 possible). No judge of the CertJudge panel has scored these 100 files, so on N only human-side statistics and judge-free baselines are possible now (no model call is made here).
- Not used: the 6-file warm-up ratings (a different, tiny item set), set-N packet of experiment 64 (no ratings returned), and any rating from a rater not in the Sheets above. Raw per-rater ratings are not committed here (aggregates only, rater ids only).

## Metrics
RPS (primary, normalized ranked probability score over the 6 categories 0..5, expected score against the human empirical distribution), then CE and TVD, then Spearman and Pearson (secondary, Brando 11-10-2026). Lower is better for RPS, CE and TVD. Raw judge distribution = the repeats binned to 0..5 plus Laplace alpha 0.5 (as experiment 51). Every interval is a 95% percentile interval of a **task-cluster bootstrap** (resample tasks with replacement, 2,000 draws, seed 0).

## Analyses
- **A1 raw table:** per judge series, RPS / CE / TVD / Spearman / Pearson against H_vb (and H_paper), with task-bootstrap intervals, plus the constant-forecast reference (training marginal, leave-one-task-out).
- **A2 calibrated forecaster test (Corr-vs-CE layer 4 on CertJudge scores):** for each of the 24 series, leave-one-task-out; fitters: CONST (training marginal), CE-fit (cumulative-logit on the judge score, maximum likelihood over every individual rating), Pearson-fit (least-squares line for the mean rating, discretised normal). Held-out RPS / CE / TVD, paired differences with task-bootstrap intervals. Counts over the 24 series: CE-fit beats CONST (interval below 0), CE-fit beats Pearson-fit (point estimate), by RPS.
- **A3 human ceiling:** split-half reliability of the human mean on H_vb (500 random rater splits per item with at least 4 ratings, Spearman-Brown corrected) and its square root as the ceiling on any judge-human correlation; on N: agreement of the two complete raters (Spearman, exact and within-1 agreement, quadratic weighted kappa), rating distribution, share of 5s.
- **A4 learning curve:** headline series only (the three P8_STRICT_B series, frozen now): Spearman with the human mean over random subsets of k tasks (k = 4, 8, 12, 16, 20; 500 subsets each), median and 2.5 to 97.5 percentile spread; spread times sqrt(k) as a check of 1/sqrt(k).
- **A5 why the old numbers looked odd:** (i) TI_var against each alignment measure (judge Spearman on paper labels, on H_vb; minus RPS, CE, TVD against H_vb), n = 8 judges per family, exact permutation p and a task-bootstrap interval (alignment recomputed on each draw), leave-one-judge-out range; (ii) leave-one-task-out range of the headline judge-human Spearman; (iii) the share of tied judge scores; (iv) Spearman between the paper's labels and the VeriBench-participant mean on the shared items.
- **A6 new set N and pooled counts:** counts table old / new / pooled (tasks, artifacts, ratings per artifact), judge-free baselines on N (normalized edit distance of candidate to gold, a fixed-seed random score, CONST) with leave-one-task-out RPS / CE / TVD and Spearman with task-bootstrap intervals, using the mean of the returned ratings per file.

## Predictions (written before the run)
1. Raw scalar judge scores are not forecasts of the rating distribution, so on raw RPS most judge series are no better than the constant forecast (as in experiment 51).
2. After CE-fit calibration, the best LLM series beat CONST on held-out RPS, but with 20 tasks the interval includes 0 for most series; CE-fit has lower RPS than Pearson-fit in a majority of the 24 series (the layer-4 direction).
3. The headline judge-human Spearman interval width shrinks about like 1 / sqrt(k) with the number of tasks and is still wide at k = 20 (half-width above 0.2).
4. The returned new ratings are concentrated at 5 (more than 60% of ratings), and the two complete raters agree only moderately; so N will raise the count of tasks and artifacts but, with a ceiling effect and 2 ratings per file, its human-mean reliability is lower than H_vb until the next waves arrive.
5. TI_var does not track the proper-score alignment (RPS, CE, TVD) even where it tracks scalar Spearman (experiment 51: -0.57 / -0.10 / -0.57 for Codex).

## Decision rules
- "More trustworthy" means: a narrower task-bootstrap interval and a stable point estimate on a larger task count with a human ceiling reported, not a higher number. A number that rises while its interval stays wide is reported as not yet trustworthy.
- If a prediction fails it is reported as failed. No analysis is added after seeing results except as a dated, labelled addendum.
- Judge scores on N (new model calls) are out of scope until at least one more rating wave has arrived; the plan and the dollar estimate are in README.md.
