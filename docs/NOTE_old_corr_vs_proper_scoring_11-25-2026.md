# Old 0.6/0.8/0.8 correlations versus Experiment 67 and Experiment 68 proper scores (11-25-2026)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/docs/NOTE_old_corr_vs_proper_scoring_11-25-2026.md>

**Date:** 11-25-2026

**As of 11-26-2026 (UTC):** every number below is copied from the committed files named in the text. This note runs no judge, no solver, and no resample. No differential testing. The scoring runs it summarizes were CPU recomputes of saved judge outputs (`no internet`), except the live Sheet read and the interim judge calls, which are labeled where they appear.

**TLDR:** The new results are the more trustworthy measurement of these judges against the corrected VeriBench ratings, and that measurement is a failure to match the ratings. The three headline item-level Spearman correlations on the corrected ratings (59 artifacts, 20 tasks) are $-0.241$ $[-0.603,+0.201]$, $-0.213$ $[-0.509,+0.111]$, and $-0.347$ $[-0.589,-0.062]$ for the strict configurations of GPT-5.3-Codex, Claude Opus 4.7, and Qwen3-Coder. Leave-one-task-out ranked probability score averages $0.1725$ against $0.1737$ for a constant forecast, and $0$ of $24$ configurations is significantly better than that constant. The old train / validation / test Spearman triple $0.6400$ / $0.8800$ / $0.8257$ is quoted in this repository without a confidence interval.

## What a rank correlation can and cannot show

Spearman correlation is the Pearson correlation of midranks. On $n$ judge configurations it is

$$
\rho_s(u,v)=\frac{\sum_{i=1}^{n}(\mathrm{rk}(u_i)-\overline{\mathrm{rk}\,u})(\mathrm{rk}(v_i)-\overline{\mathrm{rk}\,v})}{\sqrt{\sum_{i=1}^{n}(\mathrm{rk}(u_i)-\overline{\mathrm{rk}\,u})^2\sum_{i=1}^{n}(\mathrm{rk}(v_i)-\overline{\mathrm{rk}\,v})^2}}.
$$

A strictly increasing transform of either argument leaves $\rho_s$ unchanged, so a constant shift of the judge (leniency or harshness) and any monotone rescaling leave it unchanged. With eight configurations, one rank swap moves $\rho_s$ by about $0.05$ to $0.1$ (`experiments/67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/RESULTS.md`). Ties use average ranks. Spearman correlation does not see the rating distribution.

The proper scores do see that distribution. Ratings lie in $\{0,1,2,3,4,5\}$. For artifact $i$ with $R_i$ individual ratings $r_{ij}$ and a forecast $q$ on those six categories, with cumulative forecast $F_q(k)=\sum_{c=0}^{k} q_c$, Experiment 68 fixes the item losses as follows (`experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/RESULTS_proper_scoring_expansion_11-24-2026.md`). Lower is better. Each artifact has equal weight $1/N$.

$$
\mathrm{RPS}_i=\frac{1}{R_i}\sum_{j=1}^{R_i}\frac{1}{5}\sum_{k=0}^{4}\bigl(F_q(k)-\mathbf{1}\{r_{ij}\le k\}\bigr)^2,\qquad \mathrm{RPS}_i\in[0,1].
$$

$$
\mathrm{CE}_i=-\frac{1}{R_i}\sum_{j=1}^{R_i}\log\max\bigl(q[r_{ij}],10^{-12}\bigr)
$$

in nats. Let $\hat p_i$ be the empirical distribution of the $R_i$ ratings. Then

$$
\mathrm{TVD}_i=\frac12\|q-\hat p_i\|_1,\qquad \mathrm{TVD}_i\in[0,1].
$$

Ranked probability score (RPS) penalizes the squared error of the cumulative forecast. Cross-entropy (CE) penalizes a small probability on the rating that occurred, so a confident wrong forecast is expensive. Total variation distance (TVD) is half the $L_1$ distance between $q$ and the empirical rating distribution. A constant forecast that copies the training-task rating margin is the baseline: if the judge score carries nothing about which artifact was rated, a refit of $q$ from that score returns this constant. RPS, CE, and TVD change when the judge is shifted or rescaled. Spearman correlation does not.

Bias in this note is the judge mean on the $0$–$5$ scale minus the human mean. Positive bias means the judge is lenient. Absolute agreement is reported with the two-way intraclass correlation $\mathrm{ICC}(A,1)$ and with mean absolute error (MAE), because Spearman correlation hides a constant offset.

## The old 0.6 / 0.8 / 0.8 figures, and the wide intervals this repository does store

Two different old numbers are easy to mix up. They are separate estimands.

**Selected-judge split Spearman.** `experiments/67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/RESULTS.md` quotes trustworthy-theorem-judges experiment 22: the selected judge "jumped across train / validation / test (Spearman = 0.6400, 0.8800, 0.8257)". Those three decimals are the only occurrence of $0.6400$, $0.8800$, and $0.8257$ in this repository. I did not find a $95\%$ interval, a resampling unit, a seed, or a $p$-value for that triple in cert-judge. The slogan $0.6$ / $0.8$ / $0.8$ is that triple rounded. The jump itself (train $0.6400$, validation $0.8800$, test $0.8257$) is the instability the quotation records. An interval for it is unavailable here.

**Judge-level Spearman of the variance-aware trust index.** On the validation set (72 pairs, 24 tasks, one annotator, two passes), the paper reports the Spearman correlation, across eight judge configurations, between the variance-aware trust index $\mathrm{TI}_{\mathrm{var}}$ and each configuration's item-level human Spearman. Source: `paper_latex/ICLR_2027_submission/05_experiments.tex` (the index table) and `experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json`, recomputed by `experiments/archive/21_tmlr_submission/ci_provenance/compute_headline_cis.py`.

| Label view | $\rho_s(\mathrm{TI}_{\mathrm{var}},\text{human Spearman})$ | $95\%$ configuration-bootstrap interval | Permutation $p$ |
|---|---:|---|---:|
| Averaged labels | $0.8333$ | $[0.241, 1.000]$ | $0.0167$ |
| Pass 1 | $0.9048$ | $[0.407, 1.000]$ | $0.0054$ |
| Pass 2 | $0.7381$ | $[0.114, 1.000]$ | $0.0451$ |

The interval resamples the eight configurations with replacement ($10{,}000$ draws, seed $42$). It does not resample tasks or raters. Draws that make either margin constant are skipped. The permutation shuffles the eight $\mathrm{TI}_{\mathrm{var}}$ values against the fixed human-Spearman values; $p=(\text{count}+1)/(10{,}000+1)$. The paper prints the same intervals as $[0.24,1.00]$, $[0.41,1.00]$, and $[0.11,1.00]$, with permutation probabilities $0.017$ / $0.005$ / $0.045$. Widths are $0.759$, $0.593$, and $0.886$. The upper endpoint $1$ is what an eight-point Spearman bootstrap produces when a resample is monotone. `paper_latex/ICLR_2027_submission/05_experiments.tex` states that this resampling does not correct for earlier selection of the evaluation setup.

The same Codex averaged-label correlation, recomputed with a task-clustered bootstrap ($10{,}000$ draws, seed $42$) in `experiments/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/REPORT.md`, is $0.8333$ $[0.238, 0.976]$, exact $8!$ permutation $p=0.0154$. Claude Opus on that view is $0.6429$ $[-0.262, 0.905]$, $p=0.0962$. Qwen3-Coder is $0.9048$ $[0.024, 0.905]$, $p=0.0046$. The task-clustered interval and the configuration-bootstrap interval answer different questions. Both are wide: the Codex interval still runs from about $0.24$ to about $1$.

The item-level human Spearman values that sit under those judge-level correlations are much smaller. On the Codex panel, averaged paper labels, the three semantic prompts have human Spearman $0.466$, $0.419$, and $0.365$ (`paper_latex/ICLR_2027_submission/05_experiments.tex`, configuration table). The $0.8$ figures are correlations across eight configurations, computed on one annotator's two old-prompt passes.

## Experiment 67: corrected ratings, RPS, CE, TVD

Folder: `experiments/67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/`. The morning result (`RESULTS.md`, tables in `results/tables.md`, full precision in `results/old_A1_raw_per_judge.csv` and `results/old_A2_calibrated_loto.csv`) rescores the saved judge outputs. Zero new judge calls. Target $H_{\mathrm{vb}}$: corrected VeriBench ratings with at least four ratings per artifact, $59$ artifacts, $20$ tasks, about $4.5$ ratings each. Intervals are $95\%$ task-bootstrap percentiles, $2{,}000$ draws, seed $0$, except the $\mathrm{TI}_{\mathrm{var}}$ table, which used $500$ draws (`RESULTS.md`, deviations).

The three headline configurations are the strict prompt `P8_STRICT_B`. Point estimates below are the CSV values; the intervals are the Experiment 67 task bootstrap.

| Configuration | RPS $[95\%]$ | CE | TVD | Spearman $[95\%]$ | Pearson |
|---|---|---:|---:|---|---:|
| Codex strict | $0.244$ $[0.206, 0.288]$ | $2.260$ | $0.671$ | $-0.241$ $[-0.603, +0.201]$ | $-0.101$ |
| Opus strict | $0.271$ $[0.229, 0.319]$ | $2.301$ | $0.689$ | $-0.213$ $[-0.509, +0.111]$ | $-0.238$ |
| Qwen strict | $0.217$ $[0.191, 0.248]$ | $2.106$ | $0.618$ | $-0.347$ $[-0.589, -0.062]$ | $-0.373$ |

Kendall correlations on the same scores, from Experiment 68, are $-0.191$, $-0.164$, and $-0.280$ (`study_c_paper_decomposition.json`); that file leaves the Kendall intervals null. No test of "Spearman equals zero" is reported: $p\text{-val}=\mathrm{n/a}$. The Qwen interval excludes $0$. The Codex and Opus intervals include $0$ and include positive values. Full Spearman precision in the CSV is $-0.24081380014647966$, $-0.21330924330813125$, and $-0.3465055623201813$.

On the same $59$ artifacts, the paper labels and the corrected ratings have Spearman correlation $-0.0423$ (`results/old_summary.json`, key `paper_vs_vb_spearman`, $n=59$). A high Spearman correlation with the paper labels says little about the corrected ratings.

Leave-one-task-out refit (the experiment files name this LOTO calibration: a map from the scalar judge score to a distribution on $\{0,1,2,3,4,5\}$, fit on the other tasks, scored on the held-out task):

- Constant-forecast RPS is $0.173727$ on every configuration (`results/old_A2_calibrated_loto.csv`, row `heldout level CONST`).
- Mean over all $24$ configurations: CE-fit RPS $0.172502$, Pearson-fit RPS $0.172377$ (`study_c_paper_decomposition.json`, which Experiment 68 recomputed; Experiment 67 prints $0.1725$ and $0.1724$).
- CE-fit beats the constant on the point estimate for $18$ of $24$ configurations and beats Pearson-fit on RPS for $13$ of $24$. The mean RPS gap versus the constant is about $0.001$. The task-bootstrap interval for CE-fit minus the constant includes $0$ for all $24$ (`RESULTS.md`: "$0$ of $24$ judge series are significantly better than the constant").

Raw RPS, before that refit, is worse than the constant for all $24$ configurations. The best raw RPS in the Experiment 67 table is $0.193$ against $0.174$.

Human agreement on the returned new ratings, still without judge scores in the morning run: two complete raters, Spearman $0.624$ $[0.425, 0.772]$, exact agreement $0.62$, within one point $1.00$, quadratic weighted kappa $0.75$; $180/247$ ratings are $5$ (`results/new_summary.json` and `RESULTS.md` Table T3). Split-half Spearman, Spearman–Brown corrected, is $0.70$ on the old corrected ratings and $0.77$ on the two-rater new set. The square-root ceilings printed in Table T3 are $0.84$ and $0.88$.

The same morning note records the reference-file caveat from Experiment 41: for $7$ of $24$ scored tasks, the reference file the judge saw matches the reference the rater saw. A negative Spearman correlation on the corrected ratings can come from that mismatch.

**Interim judge scores the same evening** (`RESULTS_interim_judged_11-24-2026.md`): $250$ ratings, $100$ files, $25$ tasks, three headline configurations, three repeats, $900$ calls. This run did call judge APIs (about $\$22.50$ at list prices). On the new files, RPS / CE / TVD are Codex $0.243$ / $2.05$ / $0.75$, Opus $0.217$ / $1.84$ / $0.69$, Qwen $0.126$ / $1.39$ / $0.56$, against the constant $0.070$ / $0.87$ / $0.36$. Each RPS-minus-constant $95\%$ task-bootstrap interval lies above $0$ (Codex $+0.173$ $[0.116, 0.226]$, Opus $+0.147$ $[0.095, 0.198]$, Qwen $+0.057$ $[0.025, 0.085]$), so the judges are worse than the constant forecast. Spearman correlations on the new files are $+0.24$ $[-0.01, +0.47]$, $+0.17$ $[-0.07, +0.39]$, and $+0.23$ $[0.00, +0.45]$. Pooled over old and new files, within-set ranks, they are $+0.05$, $+0.03$, and $+0.02$, and each pooled interval includes $0$.

## Experiment 68: the same panel, plus what proper scores catch elsewhere

Folder: `experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/`. CPU only, `$0` API spend. Studies A–C: `no internet`. Study D: read-only HTTPS to public Google Sheet CSV exports (`docs.google.com`). Python $3.11.6$, numpy $2.2.6$, scipy $1.16.3$. Uncertainty in Study C uses $10{,}000$ task-cluster bootstrap draws, seed $68$, and $2{,}000$ task sign-flip draws for paired comparisons (`RESULTS_proper_scoring_expansion_11-24-2026.md`).

**Independent check of Experiment 67** (`results/exp67_independent_crosscheck.json`):

- Archive experiment 51 reproduction error $2.22\times 10^{-16}$.
- $216$ leave-one-task-out scalars (24 configurations $\times$ 3 refits $\times$ 3 losses): maximum absolute error $9.14\times 10^{-7}$.
- $12$ $\mathrm{TI}_{\mathrm{var}}$ correlations: maximum absolute error $1.11\times 10^{-16}$; permutation $p$ error $0$.
- Live re-read of the sheets at 11-24-2026 11:32 PST still has $247$ ratings; T05-versus-T08 Spearman, kappa, exact agreement, within-one, and the share of fives match to numerical noise.

Because the bootstrap settings differ ($2{,}000$ draws, seed $0$ versus $10{,}000$ draws, seed $68$), the interval endpoints move in the second decimal. The Spearman point estimates match. Experiment 68's task-bootstrap intervals for the three headline Spearman correlations are $[-0.593, +0.177]$, $[-0.504, +0.090]$, and $[-0.572, -0.050]$ (`results/study_c_paper_decomposition.json`, `families.*.per_judge[].raw.spearman`). Kendall intervals in that file are missing (`ci_lo` and `ci_hi` are null).

**Bias and absolute agreement on $H_{\mathrm{vb}}$** (same JSON, `raw.bias_05`, `raw.icc_a1`, `raw.mae_05`). Human mean $3.054$ $[2.633, 3.482]$.

| Configuration | Judge mean | Bias $[95\%]$ | MAE | $\mathrm{ICC}(A,1)$ $[95\%]$ |
|---|---:|---|---:|---|
| Codex strict | $1.378$ | $-1.676$ $[-2.207, -1.119]$ | $1.875$ | $-0.040$ $[-0.170, +0.119]$ |
| Opus strict | $0.720$ | $-2.334$ $[-2.845, -1.820]$ | $2.402$ | $-0.046$ $[-0.114, +0.009]$ |
| Qwen strict | $2.831$ | $-0.224$ $[-0.842, +0.434]$ | $1.414$ | $-0.371$ $[-0.590, -0.042]$ |

Codex and Opus are harsh by more than a point and a half, and those bias intervals exclude $0$. Qwen's bias interval includes $0$. Spearman correlation is unchanged by adding a constant to every judge score, so the old $0.8$ correlations could not have shown this offset. $\mathrm{ICC}(A,1)$ is about zero for Codex and Opus and negative for Qwen.

**$\mathrm{TI}_{\mathrm{var}}$ against the corrected ratings, eight configurations.** Experiment 68's configuration bootstrap ($10{,}000$ draws) of the Spearman correlation between $\mathrm{TI}_{\mathrm{var}}$ and item-level human Spearman is Codex $-0.333$ $[-0.846, +0.797]$, exact $8!$ permutation $p=0.428$; Opus $-0.167$ $[-0.846, +0.803]$, $p=0.703$; Qwen $-0.595$ $[-0.975, +0.235]$, $p=0.132$ (`ti_var_meta_vb59.raw_spearman`). After the leave-one-task-out CE-fit removes the harshness gap, the Spearman correlation of $\mathrm{TI}_{\mathrm{var}}$ with negative CE-fit RPS is Codex $+0.024$ $[-0.684, +0.923]$, $p=0.977$; Opus $-0.071$ $[-0.848, +0.923]$, $p=0.882$; Qwen $+0.476$ $[-0.383, +0.973]$, $p=0.243$ (`ce_cal_neg_rps`). These intervals run most of the way from $-1$ to $+1$. Experiment 67's Table T7 intervals are narrower because they resample tasks ($500$ draws) rather than the eight configurations. Both units are reported in the files. Neither shows a stable positive association of $\mathrm{TI}_{\mathrm{var}}$ with better proper scores on this panel.

**A panel where Spearman correlation and the proper scores disagree** (Study A, native six-class forecasts from `experiments/63_judge_optimization_arms_prompt_sft_rl_qwen3_8b/`, VeriBench experiment 100 ratings, $30$ artifacts / $10$ tasks, target `all5`). The GRPO condition `rl_grpo` has Spearman $+0.543$ $[+0.265, +0.737]$ and CE $5.556$ $[3.740, 7.464]$ against the training-margin constant's CE $1.804$ $[1.622, 2.021]$. The paired CE difference is $+3.752$ $[+2.098, +5.460]$, exact $2^{10}$ task sign-flip $p=0.0039$. Its RPS $0.213$ $[0.151, 0.288]$ is worse than the constant's RPS $0.183$ $[0.142, 0.231]$ on the point estimate; the paired RPS difference is $+0.030$ $[-0.004, +0.064]$, $p=0.127$, so the RPS gap does not exclude $0$. The condition `human_mix_sft` has Spearman $+0.746$ $[+0.210, +0.936]$, RPS $0.142$ $[0.100, 0.184]$, bias $-0.012$ $[-0.424, +0.488]$ (judge mean $2.860$, human mean $2.872$), and $\mathrm{ICC}(A,1)$ $+0.740$ $[+0.249, +0.939]$. On the three-expert target, `human_mix_sft` RPS $0.114$ $[0.081, 0.153]$ beats `teacher_only_sft` RPS $0.149$ $[0.110, 0.190]$ at sign-flip $p=0.0332$ and beats the constant $0.180$ $[0.136, 0.223]$ at $p=0.0312$, while the Spearman gap between those two fine-tunes is $+0.056$ with a difference interval that includes $0$. This is a different rating set from the new VeriBench-team packet.

**Label-free index on a $60$-configuration panel** (Study B, `experiments/39_label_free_proxy_index_train_val_test_over_judge_families/`, $45$ held-out artifacts / $15$ tasks). Missing-specification monotonicity $C_{\mathrm{ms,gold}}$ has Spearman $+0.675$ $[+0.251, +0.872]$ with negative CE-fit TVD on $16$ test LLM configurations, permutation $p=0.0042$, within-family permutation $p=0.0243$. $\mathrm{TI}_{\mathrm{var}}$ on negative CE-fit RPS is $-0.255$ $[-0.668, +0.171]$, $p=0.309$ ($n=18$). Frozen $\mathrm{PTI}_{v0}$ is $-0.274$ $[-0.743, +0.109]$, $p=0.661$ ($n=9$). Choosing the maximum $\mathrm{TI}_{\mathrm{var}}$ or $\mathrm{PTI}_{v0}$ selects `opus55x|D0` with CE-fit RPS $0.1667$, regret $+0.0392$ against the best CE-fit RPS $0.1275$ in that pool.

**Live team ratings** (Study D, $247$ non-coordinator ratings, $100/100$ files, $25/25$ tasks). Score counts $\{0:0,1:7,2:1,3:13,4:46,5:180\}$, so $180/247=72.87\%$ are $5$ and $226/247=91.50\%$ are $4$ or $5$. T05 versus T08 ($100$ items, $25$ tasks): Spearman $+0.624$ $[+0.413, +0.776]$, quadratic weighted kappa $0.750$, exact $0.620$, within one $1.000$, $\mathrm{ICC}(A,1)$ $+0.751$, bias $-0.360$ (means $4.380$ and $4.740$). SHA-256 overlap with the frozen experiment 64 set is $0/100$. Unsmoothed leave-one-rater-out RPS on the $100$ files is $0.062$ $[0.036, 0.089]$. The constant forecast's leave-one-task-out RPS is $0.0699$ $[0.0452, 0.0972]$. Human mean $4.572$ $[4.363, 4.767]$.

## Are the new results more trustworthy?

Yes, as a measurement. Four facts support that, and they are all in the files above.

1. The target changed from one annotator's old-prompt passes to corrected multi-rater VeriBench ratings. Those two labelings have Spearman $-0.042$ on the $59$ shared artifacts, so agreement with the paper labels is a different claim from agreement with the corrected ratings.
2. The reported uncertainty now has a named unit. The old paper interval resamples eight configurations and runs from $0.241$ to $1.000$ on the headline averaged-label correlation. The new item-level intervals resample tasks. Qwen's negative Spearman interval excludes $0$ under both Experiment 67 and Experiment 68. Codex and Opus still include $0$.
3. RPS, CE, TVD, bias, MAE, and $\mathrm{ICC}(A,1)$ show the offset Spearman correlation deletes. Codex strict bias is $-1.676$ $[-2.207, -1.119]$ (judge mean $1.378$, human mean $3.054$). After a leave-one-task-out refit, mean RPS is $0.1725$ versus $0.1737$ for the constant, and $0$ of $24$ configurations is significantly better.
4. Experiment 68 recomputes Experiment 67's unchecked leave-one-task-out block to a maximum absolute error of $9.14\times 10^{-7}$, and the $\mathrm{TI}_{\mathrm{var}}$ permutation probabilities to an error of $0$.

The new results are a poor basis for a positive claim that these judges match the VeriBench team. The three headline Spearman correlations are negative. The proper scores sit on the constant forecast. The interim scores on the $100$ new files remain worse than the constant on RPS, CE, and TVD, with difference intervals above $0$. A narrower interval around zero is a more precise zero.

## What a reviewer or a defense examiner should still push on

1. **The $0.6400$ / $0.8800$ / $0.8257$ intervals are not in this repository.** Any sentence that attaches a width to that triple has to come from trustworthy-theorem-judges experiment 22, which is not vendored here. The wide intervals that are vendored belong to $\mathrm{TI}_{\mathrm{var}}$ versus human Spearman on eight configurations.
2. **Three estimands.** Split Spearman of one selected judge, judge-level Spearman of $\mathrm{TI}_{\mathrm{var}}$ on eight configurations, and item-level Spearman of one configuration against ratings are three quantities. A drop from $0.83$ to $-0.24$ compares the second with the third, on different labels.
3. **Reference bytes.** Experiment 41 found a byte match on $7$ of $24$ scored tasks. The negative item-level Spearman correlations are compatible with the judge and the raters having seen different reference files. Experiment 67 records this as untested in that rescore.
4. **The new packet is a ceiling.** $72.87\%$ of the $247$ ratings are $5$. Constant-forecast RPS on those $100$ files is $0.0699$. There is little rank variation and little room for a proper score to beat a constant. Two raters finished all $100$ files. The other raters are partial (T12 $30$, T06 $16$, V04 $1$ in the 11:32 PST snapshot).
5. **The interim judge run is still worse than a constant, and it is interim.** The 11-25 and 12-03 rating waves named in Experiment 67 are outside these files. Pooled within-set-rank Spearman is about $0.02$ to $0.05$ with intervals that include $0$.
6. **Twenty tasks, and two bootstrap units.** Item-level interval widths on the old corrected panel are $0.80$, $0.62$, and $0.53$ (Experiment 67 Table T5, all $20$ tasks). Eight-configuration intervals for $\mathrm{TI}_{\mathrm{var}}$ span most of $[-1,+1]$. Quoting only the narrower unit overstates precision.
7. **The refit uses the human ratings.** Leave-one-task-out CE-fit and Pearson-fit are maps fit on the same rating collection that is being scored. They answer whether the judge score has anything to map. They are not a locked test of a judge chosen without those ratings.
8. **Multiplicity.** Twenty-four configurations and several losses, and twelve $\mathrm{TI}_{\mathrm{var}}$ comparisons in Experiment 67 Table T7, with no multiplicity correction in the frozen text. The one permutation probability under $0.05$ in that table (Qwen, negative mean TVD, $p=0.046$) is one of those twelve.
9. **Studies A and B are another rating set.** The GRPO-versus-constant CE result and the $C_{\mathrm{ms,gold}}$ transfer result use VeriBench experiment 100 and the experiment 39 panel. SHA-256 overlap of the new $100$ files with the frozen experiment 64 set is $0/100$. A proper-score win on experiment 100 does not move the new team packet.
10. **There is still no test-set result under the validation-set rating procedure with new raters**, which `AGENTS.md` already states for the 72-pair panel. Experiment 68 left the paper prose unchanged on purpose.
11. **Kendall intervals were not computed** in `study_c_paper_decomposition.json` (null endpoints). Pearson intervals are in that file and in `old_A1_raw_per_judge.csv`. A defense that leads with Spearman should show Pearson, Kendall, bias, and $\mathrm{ICC}(A,1)$ beside it, as the tables above do.

## Source paths

- Old split triple, quoted only: `experiments/67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/RESULTS.md`
- Paper index table and item-level Codex Spearman: `paper_latex/ICLR_2027_submission/05_experiments.tex`
- Configuration-bootstrap intervals: `experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json`, procedure in `compute_headline_cis.py`
- Task-clustered recomputation of the same judge-level correlations: `experiments/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/REPORT.md`
- Experiment 67 tables, interim scores, and the $-0.042$ label comparison: `experiments/67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/RESULTS.md`, `RESULTS_interim_judged_11-24-2026.md`, `results/old_A1_raw_per_judge.csv`, `results/old_A2_calibrated_loto.csv`, `results/old_summary.json`, `results/new_summary.json`
- Experiment 68 formulas, bias, independent check, Studies A–D: `experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/RESULTS_proper_scoring_expansion_11-24-2026.md`, `results/study_c_paper_decomposition.json`, `results/exp67_independent_crosscheck.json`, `results/study_a_e63_proper_scores.json`
