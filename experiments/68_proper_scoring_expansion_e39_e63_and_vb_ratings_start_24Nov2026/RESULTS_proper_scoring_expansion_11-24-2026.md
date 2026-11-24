# Experiment 68: Proper-Scoring Expansion (`RPS`, `CE`, `TVD`, `ICC(A,1)`), Live VeriBench Ratings, and Experiment 67 Independent Verification (`11-24-2026`)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/RESULTS_proper_scoring_expansion_11-24-2026.md>
Date: 11-24-2026

**TLDR:** Expanding canonical proper scoring rules — Ranked Probability Score (`RPS`), Cross-Entropy (`CE`), Total Variation Distance (`TVD`), and Brier score (`Brier`), alongside Mean Absolute Error (`MAE`), signed mean bias (`judge - human`, positive = lenient), two-way Intra-Class Correlation for absolute agreement (`ICC(A,1)`) and consistency (`ICC(C,1)`), Quadratic Weighted Kappa (`QWK`), Leave-One-Rater-Out (`LORO`) ceilings, and Leave-One-Task-Out (`LOTO`) calibration — to signal-bearing panels shows concretely where rank correlations fail and resolves every open numerical check from [67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel](../67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/RESULTS.md). Across native 6-class distributional judges (`Qwen3-8B` in `63_judge_optimization_arms_prompt_sft_rl_qwen3_8b`), Group Relative Policy Optimization (`rl_grpo`) achieves moderate Spearman (`+0.543` on `all5` / `+0.565` on `expert3`) while scoring worse than a naive training-margin constant forecast (`CONST_trainval`) on `RPS` and suffering catastrophic `CE` (`5.5558` vs `1.8037`, `p-val=0.0039`), whereas `human_mix_sft` beats `teacher_only_sft` and `CONST_trainval` (`expert3` `RPS 0.1141` vs `0.1494` [`p-val=0.0332`] and `0.1795` [`p-val=0.0312`]) where Spearman alone appears statistically tied. Across `39_label_free_proxy_index_train_val_test_over_judge_families` (`60` configs on `45` held-out items), missing-specification monotonicity (`C_ms_gold`) tracks calibrated proper losses (`test_llm` `n=16` Spearman `+0.675` on `CE-calibrated TVD`, `p-val=0.0042`, within-family `p-val=0.0243`) while `TI_var` and Frozen Proxy Trust Index (`PTI_v0`) fail (`-0.255` and `-0.274` on `CE-calibrated RPS`). On legacy 8-config panels (`n=59` artifacts, `20` tasks), `archive/51` reproduces to `2.22e-16` and Experiment 67's unchecked `216` LOTO scalars and `12` permutation tests match to `< 1e-6`. Live read-only public Comma-Separated Values (`CSV`) exports across `33/34` VeriBench team Google Sheets (`11-24-2026 11:32 PST`) show `247` non-coordinator ratings covering `100/100` files (`25/25` tasks) with strong `T05`/`T08`/`T12` agreement (`QWK 0.75–0.88`), `0/100` SHA-256 overlap with frozen [64_cert_judge_nov6_confirmatory_test_setN_preregistration](../64_cert_judge_nov6_confirmatory_test_setN_preregistration/PROTOCOL.md), and `$0` API spend.

---

## Run provenance, compute spend, and scope constraints

- **Zero paid API / Valkyrie spend (`$0`):** Honors the `10-15-2026` Vals / Valkyrie spending pause in `AGENTS.md`. Zero new Large Language Model (`LLM`) calls or Differential Testing (`DT`) agent solver runs were executed (`no DT applicable`: offline judge-scoring analysis). Studies A–C ran strictly offline with `no internet` on saved local files; Study D ran with read-only HTTPS access to public Google Sheet Comma-Separated Values (`CSV`) exports (`docs.google.com`) and zero LLM calls. Every number is computed deterministically on CPU (`Python 3.11.6`, `numpy 2.2.6`, `scipy 1.16.3`).
- **Metric specification:** Matches `judges-dont-need-psychometrics-or-corr` (`EVALUATION_CRITERION_11-09-2026.md`) over discrete rating categories `{0, 1, 2, 3, 4, 5}`:
  - Equal weight per artifact (`1/N` mean over item losses; never weighted by rater count per item).
  - Normalized individual-rating `RPS`: mean across the `R_i` ratings of artifact `i` of `(1/5) * sum_{k=0}^{4} (F_q(k) - 1{r <= k})^2`, bounded in `[0, 1]`, decomposing into `RPS_dist_err + RaterDisagreement`.
  - `CE`: `-(1/R_i) * sum_{j=1}^{R_i} log(max(q[r_{ij}], 1e-12))` (natural log, nats).
  - `TVD`: `(1/2) * ||q - p_hat_i||_1` where `p_hat_i` is the empirical rating distribution of artifact `i`, bounded in `[0, 1]`.
  - `Brier`: `sum_{k=0}^{5} q_k^2 - 2 q_{r} + 1` averaged over individual ratings `r`, bounded in `[0, 2]`.
  - Uncertainty: `10,000` task-cluster bootstrap draws (`seed=68`; `2,000` draws for single-seed E63 runs and legacy paper LOTO fits; `2,000` config/family bootstrap draws with `10,000` vectorized permutation draws in Study B's `112`-pair meta grid). Paired comparisons use exact two-sided task sign-flip permutation tests (`2^10 = 1,024` exact enumeration on `10` test tasks in Study A; `2^20` MC `2,000` draws [`PAPER_BOOT_DRAWS = 2000`] on `20` tasks in Study C). Correlation differences report task-bootstrap 95% Confidence Intervals (`CI`) with `p-val=n/a`.
  - Unit tests (`tests/test_metrics.py`): `11/11` passed in `0.199 s`.

---

## Study A: Native 6-Class Distributional Judges (`experiments/63_judge_optimization_arms_prompt_sft_rl_qwen3_8b/`)

**Why this study matters:** Experiment 63 (`Qwen3-8B`) actually trained and evaluated judges that natively emit 6-class probability vectors `probs` over `{0..5}` (`expected_score` verified against `probs` within `< 1e-6`), eliminating the 3-repeat histogram-binning approximation that confounded Experiment 67 (`67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel`). All `18` test runs across `6` arms were evaluated against both the full 5-rater test target (`all5`: `4–5` individual ratings per item across `p1..p5`, `30` items / `10` tasks) and the 3-expert subset (`expert3`: `p1..p3`, `2–3` ratings per item, `30` items / `10` tasks) from VeriBench Experiment 100 (`items.jsonl` SHA-256 `ad9ed552...`). Frozen `report_e64.json` Spearman values reproduce with max discrepancy `2.22e-16` across per-seed runs and `<= 1.11e-16` on ensembles.

### A1. Primary Target: All 5 Raters (`all5`, `30` held-out test artifacts / `10` tasks)

Ensembles average seed probability vectors equally (`q_ens = mean_s probs_s`). Intervals are `10,000` task-cluster bootstrap 95% CIs (`p-val` against `CONST_trainval` is listed in Table A3; Kendall `tau` CI is `n/a` for speed, point estimate exact). Negative `RPS` / `CE` / `TVD` / `Brier` / `MAE` differences mean lower error; positive `bias_05 = judge_mean_05 - human_mean_05` means the judge is more lenient than humans (`human_mean_05 = 2.872 [2.150, 3.585]`).

```
Arm (n seeds)         RPS [95% CI]              CE [95% CI]             TVD [95% CI]            Brier   MAE    Bias_05 [95% CI] (J_mean, H_mean)       ICC(A,1) [95% CI]        ICC(C,1)  Spearman [95% CI]        Kendall  Pearson
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
LORO smoothed (ref)   0.1478 [0.1216, 0.1757]   1.6709 [1.4447, 1.8995] 0.7644 [0.7113, 0.8153] 0.7917  1.116  n/a                                     n/a                      n/a       0.567 [0.344, 0.752]*    n/a      n/a
LORO empirical (ref)  0.1586 [0.1150, 0.2028]   n/a (unsmoothed)        0.7078 [0.6044, 0.8033] 0.9093  1.048  n/a                                     n/a                      n/a       (single-draw LORO)       n/a      n/a
CONST_trainval        0.1833 [0.1415, 0.2311]   1.8037 [1.6217, 2.0213] 0.5148 [0.4471, 0.5949] 0.8375  0.941  +0.174 [-0.540, +0.895] (3.045, 2.872)  ~0 (const)               ~0        n/a                      n/a      n/a
shuffled_control (1)  0.1852 [0.1551, 0.2204]   1.8312 [1.6792, 1.9566] 0.5469 [0.5037, 0.5941] 0.8451  0.936  +0.064 [-0.649, +0.782] (2.935, 2.872)  +0.002 [-0.013, +0.020]  +0.002    -0.039 [-0.429, +0.383]  -0.028   +0.058
zero_shot_base (1)    0.2641 [0.1872, 0.3478]   4.1780 [2.8964, 5.6354] 0.6921 [0.5551, 0.8224] 1.1170  1.325  +0.563 [-0.381, +1.423] (3.435, 2.872)  -0.280 [-0.590, +0.072]  -0.317    -0.162 [-0.586, +0.555]  -0.075   -0.425
prompt_opt_arm1 (2)   0.2924 [0.1936, 0.4043]   3.9644 [2.7718, 5.3140] 0.6958 [0.5552, 0.8284] 1.1307  1.468  +0.383 [-0.812, +1.378] (3.255, 2.872)  -0.511 [-0.790, +0.060]  -0.518    -0.181 [-0.633, +0.471]  -0.113   -0.544
rl_grpo (3)           0.2133 [0.1507, 0.2883]   5.5558 [3.7401, 7.4640] 0.6337 [0.4906, 0.7695] 1.1411  0.840  +0.462 [-0.086, +1.055] (3.334, 2.872)  +0.380 [+0.160, +0.600]  +0.416    +0.543 [+0.265, +0.737]  +0.436   +0.530
teacher_only_sft (6)  0.1569 [0.1182, 0.1946]   1.7415 [1.4039, 2.0558] 0.4499 [0.3512, 0.5544] 0.8360  0.682  +0.194 [-0.277, +0.670] (3.065, 2.872)  +0.685 [+0.359, +0.845]  +0.688    +0.710 [+0.285, +0.845]  +0.516   +0.700
human_mix_sft (5)     0.1416 [0.1003, 0.1843]   1.6205 [1.2770, 1.9369] 0.3850 [0.2878, 0.4925] 0.7447  0.555  -0.012 [-0.424, +0.488] (2.860, 2.872)  +0.740 [+0.249, +0.939]  +0.733    +0.746 [+0.210, +0.936]  +0.596   +0.745
```
*Note on LORO `TVD` and single-draw Spearman:* `LORO smoothed` applies symmetric Laplace smoothing (`alpha=0.5`) to `3–4` held-out ratings per item (denominator `~6–7`), shifting `43–50%` of probability mass onto unchosen bins and inflating smoothed LORO `TVD` (`0.7644`) above multi-class judge ensembles (`0.3850`). Unsmoothed `LORO empirical` avoids smoothing dilution (`TVD 0.7078`), while `0.567 [0.344, 0.752]` is the mean `[2.5th, 97.5th]` percentile across `500` single held-out-rater draws vs the remaining raters' mean.

Per-seed mean `+/-` standard deviation (`SD`) across seeds confirms tight seed stability in `human_mix_sft` and high `CE` variance in `rl_grpo`:
- `human_mix_sft` (`n=5` seeds): `RPS 0.1494 +/- 0.0119`, `CE 1.7668 +/- 0.1421`, `TVD 0.4027 +/- 0.0269`, `Spearman 0.763 +/- 0.025`, `ICC(A,1) 0.710`.
- `teacher_only_sft` (`n=6` seeds): `RPS 0.1727 +/- 0.0136`, `CE 1.9966 +/- 0.2505`, `TVD 0.4820 +/- 0.0366`, `Spearman 0.685 +/- 0.108`, `ICC(A,1) 0.621`.
- `rl_grpo` (`n=3` seeds): `RPS 0.2357 +/- 0.0137`, `CE 8.4393 +/- 3.0610`, `TVD 0.6918 +/- 0.0795`, `Spearman 0.490 +/- 0.070`, `ICC(A,1) 0.336`.

### A2. Secondary Target: 3 Experts (`expert3`, `p1..p3`, `30` items / `10` tasks, `human_mean_05 = 2.361`)

Caveat: `human_mix_sft` mixed `p1..p3` training items into Supervised Fine-Tuning (`SFT`), so `expert3` evaluates against the same 3-expert subpopulation whose training split entered `human_mix_sft` (`all5` includes `p4..p5` held out by rater too).

```
Arm (n seeds)         RPS [95% CI]              CE [95% CI]             TVD [95% CI]            Brier   MAE    Bias_05 [95% CI] (J_mean, H_mean)       ICC(A,1) [95% CI]        ICC(C,1)  Spearman [95% CI]        Kendall  Pearson
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
LORO smoothed (ref)   0.1349 [0.1095, 0.1607]   1.6910 [1.5158, 1.8688] 0.7844 [0.7425, 0.8253] 0.8062  1.035  n/a                                     n/a                      n/a       0.786 [0.722, 0.868]*    n/a      n/a
LORO empirical (ref)  0.1467 [0.1100, 0.1867]   n/a                     0.7111 [0.6000, 0.8333] 1.2333  0.833  n/a                                     n/a                      n/a       (single-draw LORO)       n/a      n/a
CONST_trainval        0.1795 [0.1364, 0.2226]   1.7915 [1.6468, 1.9471] 0.6586 [0.5954, 0.7165] 0.8313  1.205  +0.360 [-0.513, +1.182] (2.721, 2.361)  ~0                       ~0        n/a                      n/a      n/a
shuffled_control (1)  0.1978 [0.1614, 0.2382]   1.9622 [1.7595, 2.1244] 0.7061 [0.6406, 0.7635] 0.8886  1.293  +0.574 [-0.297, +1.392] (2.935, 2.361)  +0.002 [-0.010, +0.012]  +0.002    +0.024 [-0.378, +0.480]  +0.034   +0.057
zero_shot_base (1)    0.3125 [0.2252, 0.4072]   5.0710 [3.4544, 6.9034] 0.8071 [0.6965, 0.9147] 1.2411  1.829  +1.074 [-0.028, +2.050] (3.435, 2.361)  -0.220 [-0.500, +0.041]  -0.319    -0.165 [-0.573, +0.539]  -0.082   -0.478
prompt_opt_arm1 (2)   0.3384 [0.2370, 0.4460]   4.7102 [3.3743, 6.1327] 0.8065 [0.6899, 0.9177] 1.2432  1.975  +0.894 [-0.454, +2.013] (3.255, 2.361)  -0.429 [-0.793, +0.042]  -0.528    -0.184 [-0.594, +0.463]  -0.105   -0.589
rl_grpo (3)           0.2372 [0.1652, 0.3180]   6.2595 [4.1386, 8.5346] 0.7272 [0.5782, 0.8674] 1.2372  1.279  +0.973 [+0.288, +1.621] (3.334, 2.361)  +0.297 [+0.116, +0.433]  +0.409    +0.565 [+0.308, +0.761]  +0.475   +0.578
teacher_only_sft (6)  0.1494 [0.1100, 0.1898]   1.6585 [1.3544, 1.9443] 0.5628 [0.4500, 0.6704] 0.8567  0.939  +0.704 [+0.195, +1.178] (3.065, 2.361)  +0.638 [+0.323, +0.800]  +0.736    +0.772 [+0.423, +0.895]  +0.595   +0.781
human_mix_sft (5)     0.1141 [0.0814, 0.1531]   1.3921 [1.1527, 1.6413] 0.4740 [0.3719, 0.5772] 0.7218  0.676  +0.499 [+0.101, +0.916] (2.860, 2.361)  +0.766 [+0.348, +0.907]  +0.823    +0.828 [+0.431, +0.963]  +0.700   +0.870
```

### A3. Paired Task Contrasts (Difference `A - B`; `10,000` task-cluster bootstrap 95% CIs, exact `2^10` task sign-flip `p-val`)

```
Target    Contrast (A - B)                      dRPS [95% CI]              p-val   dCE [95% CI]                p-val   dTVD      p-val   dSpearman [95% CI] (p-val=n/a)
------------------------------------------------------------------------------------------------------------------------------------------------------------------------
all5      human_mix_sft - teacher_only_sft     -0.0152 [-0.0317, -0.0002]  0.1074  -0.1210 [-0.2259, -0.0195]  0.0547  -0.0649   0.0332  +0.0357 [-0.1876, +0.2502]
all5      human_mix_sft - rl_grpo              -0.0717 [-0.1140, -0.0332]  0.0059  -3.9353 [-5.5846, -2.3962]  0.0020  -0.2487   0.0039  +0.2032 [-0.1800, +0.3959]
all5      human_mix_sft - prompt_opt_arm1      -0.1507 [-0.2711, -0.0553]  0.0098  -2.3439 [-3.4913, -1.3218]  0.0020  -0.3108   0.0078  +0.9270 [-0.0169, +1.5040]
all5      human_mix_sft - zero_shot_base       -0.1225 [-0.1932, -0.0538]  0.0098  -2.5575 [-3.8093, -1.4605]  0.0020  -0.3071   0.0059  +0.9076 [-0.1313, +1.4693]
all5      human_mix_sft - CONST_trainval       -0.0416 [-0.0812, -0.0032]  0.0664  -0.1832 [-0.4560, +0.0632]  0.2285  -0.1297   0.0586  n/a (CONST undef)
all5      teacher_only_sft - CONST_trainval    -0.0264 [-0.0681, +0.0148]  0.2520  -0.0622 [-0.3550, +0.2364]  0.7090  -0.0649   0.3340  n/a (CONST undef)
all5      rl_grpo - CONST_trainval             +0.0301 [-0.0037, +0.0642]  0.1270  +3.7522 [+2.0977, +5.4597]  0.0039  +0.1189   0.1348  n/a (CONST undef)
expert3   human_mix_sft - teacher_only_sft     -0.0352 [-0.0653, -0.0091]  0.0332  -0.2664 [-0.4907, -0.0735]  0.0273  -0.0888   0.0098  +0.0556 [-0.1063, +0.2528]
expert3   human_mix_sft - rl_grpo              -0.1231 [-0.1750, -0.0733]  0.0020  -4.8674 [-6.9742, -2.9136]  0.0020  -0.2533   0.0039  +0.2627 [-0.0335, +0.4358]
expert3   human_mix_sft - prompt_opt_arm1      -0.2243 [-0.3303, -0.1311]  0.0020  -3.3181 [-4.5798, -2.0955]  0.0020  -0.3325   0.0020  +1.0116 [+0.1622, +1.5025]
expert3   human_mix_sft - zero_shot_base       -0.1983 [-0.2749, -0.1254]  0.0020  -3.6789 [-5.3825, -2.2039]  0.0020  -0.3331   0.0020  +0.9923 [+0.0738, +1.4821]
expert3   human_mix_sft - CONST_trainval       -0.0654 [-0.1128, -0.0225]  0.0312  -0.3994 [-0.6531, -0.1742]  0.0078  -0.1846   0.0039  n/a (CONST undef)
expert3   teacher_only_sft - CONST_trainval    -0.0301 [-0.0866, +0.0255]  0.3438  -0.1331 [-0.4768, +0.2082]  0.4863  -0.0958   0.1738  n/a (CONST undef)
expert3   rl_grpo - CONST_trainval             +0.0577 [-0.0025, +0.1132]  0.1016  +4.4680 [+2.4226, +6.6246]  0.0039  +0.0686   0.3477  n/a (CONST undef)
```

**Two concrete methodological takeaways from Study A:**
1. **`rl_grpo` exposes Spearman's blind spot:** Ranked on Spearman alone, `rl_grpo` looks like a respectable `+0.543` (`all5`) / `+0.565` (`expert3`) judge. Measured as a proper probabilistic forecast, `rl_grpo` performs **worse than `CONST_trainval`** on `RPS` (`+0.0301` on `all5`, `+0.0577` on `expert3`) and collapses into extreme log-loss overconfidence (`CE = 5.56–6.26`, `p-val = 0.0039` vs `CONST_trainval`).
2. **Proper scores detect calibration & distributional improvements invisible to Spearman:** `human_mix_sft` and `teacher_only_sft` sit within `0.036` Spearman on `all5` (`0.746` vs `0.710`) and `0.056` on `expert3` (`0.828` vs `0.772`), with wide `dSpearman` CIs straddling `0`. Proper scoring resolves `human_mix_sft` as strictly better calibrated (unbiased `-0.012` on `all5`, `ICC(A,1) = 0.740`, `TVD p-val = 0.0332` on `all5`; `RPS p-val = 0.0332`, `CE p-val = 0.0273`, `TVD p-val = 0.0098` on `expert3`), matching or edging out the `LORO` smoothed human baseline.

---

## Study B: `39_label_free_proxy_index_train_val_test_over_judge_families` (`60`-Unit Multi-Family Panel)

All `60` harvest configs (`56` LLMs spanning OpenAI, Anthropic, Google, Qwen, Terminus2 agents, and prompts `P1`, `P4`, `P8`, `LEX`, `D0`, `H0`, `H1`, `H2`, `R4` + `4` non-LLM controls `count_ratio`, `editdist`, `name_jaccard`, `random`) were evaluated on `45` held-out items (`validation 15 + test 30`, `15` tasks). Frozen E39 `expert3` held-out Spearman values reproduce to `< 1e-9` across every eligible config. Calibration (`CONST`, `CE_fit`, `Pearson_fit`) was fit strictly on the `30` train items (`10` tasks).

### B1. Held-Out Panel Summary (`all5` target, `45` held-out items / `15` tasks)

- `CONST_train` (`all5`): `RPS 0.1739`, `CE 1.7537`, `TVD 0.5025`, `Brier 0.8248`, `MAE 0.857`, `bias_05 +0.045 (judge_mean 3.004, human_mean 2.959)`.
- Human `LORO` ceiling on the same `45` held-out items: smoothed `RPS 0.1469 [0.1249, 0.1691]`, `CE 1.6667 [1.4782, 1.8583]`, `TVD 0.7630`; empirical `RPS 0.1588 [0.1250, 0.1923]`, `TVD 0.7037`.
- **Train-task `CE_fit` calibration unlocks strong proper-scoring accuracy on signal-bearing judges** (unlike legacy Experiment 67):
  - Across the `18` held-out test LLM configs (`all5`): mean `raw RPS` drops from `0.1698` (range `0.1298–0.2755`) to `0.1491` (`0.1275–0.1855`) after `CE_fit` (`Pearson_fit` `0.1503`), `CE` drops from `1.8166` to `1.6175` (beating `LORO smoothed 1.6667`), and `TVD` drops from `0.5173` to `0.4442`. Best raw `RPS`: `qwen36|H0` (`0.1298`); best `CE_fit RPS`: `qwen36|H2` (`0.1275`, `CE 1.4944`, `TVD 0.3969`, `ICC(A,1) +0.822` raw / `Spearman +0.805`); best `CE_fit TVD`: `t2_qwen|D0` (`0.3877`, `RPS 0.1309`).
  - Across all `56` LLM configs (`all5`): mean `raw RPS 0.1916 -> CE_fit RPS 0.1536` (`Pearson_fit 0.1547`), `raw CE 1.9128 -> 1.6428`, `raw TVD 0.5548 -> 0.4549`.
  - Non-LLM structural controls on `all5`: `ctl|count_ratio` reaches `CE_fit RPS 0.1605` (`raw Spearman +0.470`), whereas `ctl|editdist` (`raw RPS 0.2531`, `raw Spearman -0.419`, `TI_var = 1.000`, `PTI_v0 = 1.000`), `ctl|name_jaccard` (`CE_fit RPS 0.1740`, `C_ms_gold = 1.000`), and `ctl|random` (`CE_fit RPS 0.1807`) stay near or worse than `CONST_train` (`0.1739`). `ctl|name_jaccard` having `C_ms_gold = 1.000` is an adversarial lexical-control failure already documented in `experiments/39_.../` and `experiments/66_.../`; excluding controls (`kind == 'llm'`) matches E39's scope.

### B2. Meta-Evaluation: Behavioral Indices vs Proper Scoring Criteria & Scalar Agreement

Higher values are oriented so positive correlation = index predicts **better** alignment (`-RPS`, `-CE`, `-TVD`, `+ICC(A,1)`, `+Spearman`). Intervals use `2,000` config-bootstrap draws and `2,000` model-family cluster draws (`seed=68`); two-sided permutation `p-val` and within-family stratified permutation `wf_p` use `10,000` vectorized rank draws. Note `test_llm` has `n=16` for `C_ms_gold` (`qwen36|H2` and `qwen36|R4` lacked E39 `ms_gold` coverage), `n=18` for `TI_var_trainnorm` and `C_bm_gold`, and `n=9` for `PTI_v0_frozen`; `all_llm` has `n=54`, `n=56`, `n=56`, and `n=42`, respectively.

```
Subset    Criterion             Index              n   Spearman [config 95% CI]   Kendall  Pearson  perm_p  fam_cluster_CI    within_fam_p
------------------------------------------------------------------------------------------------------------------------------------------
test_llm  ce_cal_all5_rps (-1)  C_ms_gold         16   +0.589 [+0.127, +0.813]    +0.377   +0.718   0.0163  [-1.000, +0.665]  0.0914
test_llm  ce_cal_all5_ce  (-1)  C_ms_gold         16   +0.630 [+0.203, +0.848]    +0.427   +0.706   0.0105  [-0.800, +0.720]  0.0669
test_llm  ce_cal_all5_tvd (-1)  C_ms_gold         16   +0.675 [+0.251, +0.872]    +0.460   +0.767   0.0042  [-0.400, +0.770]  0.0243
test_llm  ce_cal_all5_icc (+1)  C_ms_gold         16   +0.664 [+0.210, +0.887]    +0.460   +0.808   0.0065  [-0.400, +0.770]  0.0161
test_llm  raw_all5_rps    (-1)  C_ms_gold         16   +0.561 [+0.061, +0.746]    +0.310   +0.704   0.0258  [-0.800, +0.669]  0.0583
test_llm  raw_all5_tvd    (-1)  C_ms_gold         16   +0.624 [+0.205, +0.797]    +0.360   +0.742   0.0107  [+0.000, +0.685]  0.0272
test_llm  raw_all5_spear  (+1)  C_ms_gold         16   +0.555 [+0.101, +0.782]    +0.360   +0.636   0.0270  [-1.000, +0.683]  0.0872
test_llm  ce_cal_all5_rps (-1)  TI_var_trainnorm  18   -0.255 [-0.668, +0.171]    -0.211   -0.232   0.3089  [-0.375, +0.300]  0.2719
test_llm  ce_cal_all5_tvd (-1)  TI_var_trainnorm  18   -0.142 [-0.573, +0.312]    -0.053   -0.213   0.5881  [-0.279, +0.842]  0.5306
test_llm  ce_cal_all5_rps (-1)  PTI_v0_frozen      9   -0.274 [-0.743, +0.109]    -0.236   -0.377   0.6614  [-0.292, -0.053]  0.8029
test_llm  ce_cal_all5_rps (-1)  C_bm_gold         18   +0.508 [-0.006, +0.794]    +0.294   +0.447   0.0313  [-0.842, +0.851]  0.0198
all_llm   ce_cal_all5_rps (-1)  C_ms_gold         54   +0.754 [+0.619, +0.836]    +0.528   +0.715   0.0001  [+0.648, +0.807]  0.0001
all_llm   ce_cal_all5_ce  (-1)  C_ms_gold         54   +0.759 [+0.628, +0.840]    +0.532   +0.693   0.0001  [+0.650, +0.824]  0.0001
all_llm   ce_cal_all5_tvd (-1)  C_ms_gold         54   +0.816 [+0.700, +0.880]    +0.605   +0.752   0.0001  [+0.690, +0.874]  0.0001
all_llm   ce_cal_all5_icc (+1)  C_ms_gold         54   +0.814 [+0.694, +0.881]    +0.598   +0.798   0.0001  [+0.688, +0.870]  0.0001
all_llm   pe_cal_all5_rps (-1)  C_ms_gold         54   +0.766 [+0.638, +0.837]    +0.538   +0.729   0.0001  [+0.627, +0.820]  0.0001
all_llm   ce_cal_all5_rps (-1)  TI_var_trainnorm  56   -0.170 [-0.427, +0.094]    -0.115   -0.202   0.2071  [-0.314, -0.003]  0.3477
all_llm   ce_cal_all5_tvd (-1)  PTI_v0_frozen     42   +0.171 [-0.058, +0.431]    +0.140   +0.109   0.3092  [-0.102, +0.413]  0.4991
```

**Selection regret on `test_llm` (maximizing each index vs best unit in that index's eligible pool and vs `H2` prompt average):**
- Maximizing `C_ms_gold` (`n=16`) selects `t2_sonnet5|D0` (`C_ms_gold = 0.9957` in `test_llm`; `ce_cal_all5_rps = 0.1360` vs oracle `t2_sonnet5|H2` `0.1288`, regret `+0.0071`; `ce_cal_all5_ce = 1.5376` vs oracle `opus55x|H2` `1.5022`, regret `+0.0353`; `ce_cal_all5_tvd = 0.4124` vs oracle `t2_qwen|D0` `0.3877`, regret `+0.0247`; fixed `H2` mean `RPS = 0.1295`). *(Note: `qwen36|H2` reaches `ce_cal_all5_rps = 0.1275` in the full `18`-unit pool but has `C_ms_gold = None`.)*
- Maximizing `TI_var_trainnorm` (`n=18`) or `PTI_v0_frozen` (`n=9`) both select `opus55x|D0` (`ce_cal_all5_rps = 0.1667`, regret `+0.0392` vs `0.1275` / `+0.0379` vs `0.1288`; `CE = 1.7118`, regret `+0.2174` / `+0.2096`; `TVD = 0.4741`, regret `+0.0864`). **Proper scoring confirms E39's core finding even more sharply:** `C_ms_gold` transfers strongly to `TVD` and `ICC(A,1)` within model families (`wf_p = 0.016–0.024` on `test_llm`, `0.0001` across all `54` LLMs), whereas `TI_var` and `PTI_v0` fail.

---

## Study C: Legacy 8-Configuration Paper Panels, Wide-CI Diagnosis, and Experiment 67 Independent Verification

### C1. Exact Reproduction & Independent Cross-Check of Experiment 67

All reproduction checks passed (`results/exp67_independent_crosscheck.json`):
1. **`archive/51` (`rescore_proper_results.json`, `min_n=1` -> `60` items):** `archive51_max_repro_err = 2.22e-16` across all `36` (`family × target × alignment`) Spearman and exact permutation `p-val` checks. Note the item-count difference already flagged by Experiment 67: `archive/51` kept `13_MyUppercase__agent1.lean` (`3` VB ratings -> `60` items), whereas Experiment 67's `min_n >= 4` rule yields **`59` items / `20` tasks** (the human `LORO` smoothed floor here is `RPS 0.1492 [0.1296, 0.1691]`, `CE 1.7195 [1.5542, 1.8732]`, `TVD 0.7755 [0.7345, 0.8117]`).
2. **Experiment 67 `old_A2_calibrated_loto.csv` (`216` scalar checks across `24` series × `3` LOTO arms [`CONST`, `CE-fit`, `Pearson-fit`] × `3` losses [`RPS`, `CE`, `TVD`]):** Independently verified with `a2_loto_max_err = 9.14e-07` (`< 1e-6`, numerical L-BFGS-B convergence tolerance). Winner counts match identically: `CE_fit` beats `CONST` on `18/24` point estimates (`0/24` with upper 95% CI `< 0`) and beats `Pearson_fit` on `13/24` `RPS` point estimates (`mean diff` near `0`, `p-val` all `> 0.08` except trivial flat-noise fits around `CONST = 0.1737`).
3. **Experiment 67 `old_A5_TI_vs_alignment.csv` (`12` `TI_var` correlations and exact `8!` permutation `p-val`):** Verified with `a5_max_rho_err = 1.11e-16`, `a5_max_p_err = 0.0`.
4. **Experiment 67 `new_summary.json` (`T05` vs `T08` agreement & `share_5` on `247` ratings):** Independently re-fetched live Google Sheets (`11-24-2026 11:32 PST`, still `247` ratings across `100` items), confirming `t05_t08_spearman_diff = 1.11e-16`, `qwk_diff = 0.0`, `exact_diff = 0.0`, `within1_diff = 0.0`, and `share_5_diff = 0.0`.
5. **Factual defect fixed in Experiment 67 `RESULTS.md` line 111:** Experiment 67 had written `"0.833 (Codex), 0.905 (Claude Opus) and 0.738 (Qwen3-Coder)"` (misattributing Codex's `avg / pass1 / pass2` from `05_experiments.tex` Table 1 as the three families). Corrected to `Codex 0.833 (pass1 0.905, pass2 0.738), Claude Opus 0.643 (pass1 0.810, pass2 0.595), Qwen3-Coder 0.905 (pass1 0.476, pass2 0.857)`.

### C2. Why Legacy Paper Raw Scores Fail (`bias_05`, `ICC(A,1)`), What `CE_fit` Does to `TI_var`, and Why `n=8` CIs Are Wide

Using the `59`-artifact / `20`-task `H_vb` panel (`human_mean_05 = 3.054`):
- **Severe harshness bias & missing signal on corrected labels:** Raw binned judges are harshly negative (`bias_05 = -1.676` for `gpt-5.3-codex|P8_STRICT_B` [`J=1.378` vs `H=3.054`, `raw RPS 0.2437`, `ICC(A,1) -0.040`, `Spearman -0.241`, `Kendall -0.191`, `Pearson -0.101`]; `bias_05 = -2.334` for `claude-opus-4-7|P8_STRICT_B` [`J=0.720`, `raw RPS 0.2711`, `ICC(A,1) -0.046`, `Spearman -0.213`, `Kendall -0.164`, `Pearson -0.238`]; `bias_05 = -0.224` for `Qwen3-Coder|P8_STRICT_B` [`J=2.831`, `raw RPS 0.2173`, `ICC(A,1) -0.371`, `Spearman -0.347`, `Kendall -0.280`, `Pearson -0.373`]).
- **LOTO calibration eliminates harshness mismatch across `TI_var`:** Raw `-RPS` vs `TI_var` looks strongly negative (`Codex -0.571 [p=0.1511]`, `Opus -0.500 [p=0.2162]`, `Qwen -0.714 [p=0.0576]`) **mainly because high-`TI_var` models (`BAD_STRINGY`, `P8_STRICT_B`, `editdist_e1`) are much harsher (`bias -1.7` to `-2.8`) than `random_r1` (`bias -0.066`) or `gpt-4o-mini` (`bias -0.45`)!** Once LOTO `CE_fit` aligns every judge to the `H_vb` marginal scale, that artificial penalty disappears and `TI_var` vs `-CE_fit RPS` sits near noise (`Codex +0.024 [LOJO -0.286..+0.286, p=0.9768]`, `Opus -0.071 [LOJO -0.357..+0.393, p=0.8820]`, `Qwen +0.476 [LOJO +0.214..+0.714, p=0.2431]`).
- **Task-subset resampling & LOJO instability explain the wide CIs:** Subsampling `k` of `20` tasks (`1,000` draws) shrinks `P8_STRICT_B` Spearman 95% intervals roughly at `1/sqrt(k)` (`Codex`: width `1.480` at `k=4` -> `1.034` at `k=8` -> `0.733` at `k=12` -> `0.453` at `k=16`; `Opus`: `1.276 -> 0.762 -> 0.520 -> 0.301`; `Qwen`: `1.099 -> 0.657 -> 0.442 -> 0.289`), while `n = 8` judges per panel gives config-bootstrap CIs spanning `[-0.97, +0.97]` and single-judge LOJO shifts of `0.30–0.75`! That mirrors why the legacy paper's `0.833 / 0.905 / 0.738` (and the older single-split `"0.6, 0.8, 0.8"` VeriBench numbers) had fragile CIs even before Experiment 41 uncovered the old-prompt / mismatched-gold bugs.

---

## Study D: Live VeriBench Team `N=100` Native Ratings Snapshot & Human Ceiling

- **Read-only live CSV pull (`11-24-2026 11:32 PST` / `2026-11-24T19:32:12Z`):** `33/34` VeriBench team Google Sheets loaded cleanly via public CSV export (OAuth token `gspread_authorized_user.json` is expired; `T30` Max Sieb returns HTTP `401: Unauthorized`, leaving `33` verified sheets accessible). **Zero raw Sheet rows, item scores, notes, or rationales are written to disk.**
- **Coverage (`247` non-coordinator ratings across `100/100` files / `25/25` tasks):**
  - `T05` (Srivatsava Daruru (Sri)): `100/100`
  - `T08` (Amy Lu): `100/100`
  - `T12` (Rakshit Kaushik): `30/100`
  - `T06` (Donald Poindexter Jr): `16/100`
  - `V04` (Vaibhav Mahajan): `1/100`
  - `A1` (Brando Miranda, excluded from human-rater target totals): `0/100`
  - `>= 2` non-`A1` ratings: **`100/100` files (`25/25` tasks)**; `>= 3` non-`A1` ratings: **`45/100` files (`22/25` tasks)**.
  - Score histogram (`0..5`): `{0: 0, 1: 7, 2: 1, 3: 13, 4: 46, 5: 180}` (`180/247 = 72.87%` score `5`, `226/247 = 91.50%` score `4` or `5`; severe ceiling concentration).
- **Packet separation verified:** Exact SHA-256 comparison between the `100` `agent_*.lean` files in `trustworthy-theorem-judges` Experiment 09 and the `125` `set-N v7` files in frozen `64_cert_judge_nov6_confirmatory_test_setN_preregistration` shows **`0/100` file overlap**.

### D1. Pairwise Human Agreement (`>= 10` shared items)

```
Pair         Items  Tasks  Exact   Within-1  QWK     MAE_05  Bias_05 (A-B) (Mean_A, Mean_B)   ICC(A,1)  ICC(C,1)  Spearman [95% task CI]   Kendall  Pearson
-----------------------------------------------------------------------------------------------------------------------------------------------------------
T05 vs T08     100     25  0.6200  1.0000    0.7496  0.380   -0.360 (4.380, 4.740)            +0.751    +0.820    +0.624 [+0.413, +0.776]  +0.600   +0.829
T05 vs T12      30     20  0.7000  1.0000    0.8615  0.300   -0.300 (4.200, 4.500)            +0.866    +0.899    +0.781 [+0.604, +0.934]  +0.753   +0.905
T08 vs T12      30     20  0.7667  1.0000    0.8814  0.233   +0.100 (4.600, 4.500)            +0.885    +0.886    +0.665 [+0.344, +0.929]  +0.649   +0.888
T05 vs T06      16      5  0.9375  1.0000    0.0000* 0.063   -0.063 (4.938, 5.000)             0.000*    0.000*   n/a (T06 const 5.0)      n/a      n/a
T06 vs T08      16      5  1.0000  1.0000    n/a*    0.000    0.000 (5.000, 5.000)             n/a*      n/a*     n/a (both const 5.0)     n/a      n/a
```
*\*`T06` scored `5` on all `16/16` items graded so far, making variance-normalized reliability coefficients (`QWK`, `ICC`, correlations) zero or undefined on that `16`-item subset.*

### D2. Proper-Scoring Human Ceiling (`LORO`) & Judge-Free LOTO Baselines (`100` files / `25` tasks)

- **Human `LORO` ceiling (`100` items / `25` tasks):**
  - Unsmoothed empirical: `RPS 0.0620 [0.0360, 0.0890]`, `TVD 0.3367 [0.1967, 0.4800]`, `Brier 0.6200`, `MAE 0.337`, single-draw `Spearman 0.477 [0.434, 0.513]`. *(Note: smoothed `LORO` with `alpha=0.5` has `RPS 0.1420 [0.1332, 0.1504]`, `CE 1.2413 [1.0670, 1.4182]`, `TVD 0.6672` — artificially diluted because most items have only `2` raters so only `1` held-out rater enters smoothing `1 + 3 = 4`.)*
- **Judge-free LOTO baselines (`human_mean_05 = 4.572 [4.363, 4.767]`):**
  - `gold_candidate_edit_similarity` (`difflib.SequenceMatcher.ratio` vs `gold_lean/reference.lean`): raw binned `RPS 0.3688 [0.3450, 0.3915]`, `CE 2.0794`, `bias -4.412 (J=0.159, H=4.572)`, raw `Spearman +0.240 [-0.058, +0.491]`, `Kendall +0.177`, `Pearson +0.173`. After LOTO `CE_fit`: `RPS 0.0698 [0.0447, 0.0976]`, `CE 0.8876`, `TVD 0.3669`, indistinguishable from LOTO `CONST` (`RPS 0.0699 [0.0452, 0.0972]`, `CE 0.8873`, `TVD 0.3703`). *(Orientation/definition note: Experiment 67 `run_new.py` used `rapidfuzz.distance.Levenshtein.normalized_similarity`, obtaining raw `Spearman -0.05 [-0.26, +0.19]`; both text similarities perform identically to `CONST` after calibration.)*
  - `length_ratio_capped` (`min(1, len_cand / len_gold)`): raw binned `RPS 0.1634 [0.1559, 0.1713]`, `CE 1.2958`, `TVD 0.6138`, `bias +0.270 (J=4.842, H=4.572)`, raw `Spearman +0.407 [+0.181, +0.584]`, `Kendall +0.365`, `Pearson +0.447`, `ICC(A,1) +0.389`. LOTO `CE_fit` lowers `RPS` slightly to `0.0649 [0.0413, 0.0910]`, `CE 0.8504`, `TVD 0.3498` (`Pearson +0.371`, `ICC(A,1) +0.143`; note LOTO `Spearman` flips to `-0.346` purely as a leave-one-out fold artifact on tied `1.0` ratios, illustrating why LOTO `CONST` itself gets spurious `Spearman -0.799` across folds and must be judged by proper losses, not LOTO rank correlation!).
  - `seeded_random_uniform`: raw `RPS 0.2770 [0.2536, 0.2997]`, `Spearman +0.015 [-0.182, +0.213]`; LOTO `CE_fit` collapses to `CONST` (`RPS 0.0703` vs `0.0699`).

---

## Limitations & Next Steps

1. **No judge scores exist yet on the `100` native VeriBench files (`Study D`):** Because of the `10-15-2026` Vals / Valkyrie spending pause, no paid judge inference was run here. Moreover, the `72.87%` score-`5` ceiling leaves little ordinal variance (`CONST` LOTO `RPS = 0.0699`), meaning calibrated proper-score improvements over `CONST` on this cohort alone will have a tight headroom unless stronger non-`5` frontier failures or hard-item subsets are included.
2. **Legacy paper `TI_var` claim stays inconclusive, not rewritten:** No paper `.tex` prose was edited (paper framing remains Brando's call pending the fresh human-data round).
3. **`T30` (Max Sieb) Sheet unreachable via public CSV:** Returns HTTP `401: Unauthorized`; re-authorizing `gspread` OAuth is needed only when full raw CSV sync in `trustworthy-theorem-judges` runs.
4. **Separate cohort from `64_cert_judge_nov6_confirmatory_test_setN_preregistration`:** Zero SHA-256 overlap (`0/100` vs `125`), so frozen Experiment 64 pre-registration remains uncontaminated and ready for confirmatory testing on free local GPUs (`Qwen3-8B` / open-weight panel) or authorized lanes.

---

## Light Quality Assurance (`QA`) Verification Record

- **Reviewer:** Antigravity CLI (`agy --dangerously-skip-permissions --model gemini-pro-orchestrator`, **`Orchestrator (Carbon)`**), ONE read-only pass relative to base commit `2df283ac6947cde013676f905d4a15e4573507cf` (`11-24-2026`), auditing all five owned paths (`experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/`, `experiments/67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/RESULTS.md`, `experiments/archive/layout.json`, `experiments/README.md`, `README.md`).
- **Full QA output:** [results/qa_light_carob_orchestrator_11-24-2026_output.txt](results/qa_light_carob_orchestrator_11-24-2026_output.txt).
- **Verbatim structured verdict block:**
```text
VERDICT: PASS_WITH_FIXES
CRITICAL_ISSUES: none
MAJOR_ISSUES: 3
FIXES_APPLIED: none (read-only audit)
STRUCTURAL: unittest 11/11 PASS (0.396s); experiment_layout.py --check PASS (15 active); git diff --check PASS; CSV-vs-JSON parity PASS; E64/E39/archive51/Exp67 reproduction PASS; Exp67 L111 vs 05_experiments.tex Table 1 PASS; privacy/secrets scan PASS.
SUMMARY: Core metric math, zero-leakage split/LOTO design, all reproduction cross-checks, the Exp 67 line-111 correction, headline README tables, and privacy/secrets safeguards are all clean and verified. Three prose-vs-artifact discrepancies in RESULTS_proper_scoring_expansion_11-24-2026.md should be reconciled: Study C LORO 95% CIs on line 148 ([0.1296, 0.1691] / [1.5542, 1.8732] / [0.7345, 0.8117] in JSON vs older bounds in text), the C_ms_gold typo on line 138 (0.9947 vs 0.9957), and the Study C sign-flip (2,000 vs 10,000) and LORO single-draw (500 vs 200) draw counts on lines 19 and 45.
```
- **Reconciliation applied (`11-24-2026`):**
  1. Reconciled all 3 major prose discrepancies in `RESULTS_proper_scoring_expansion_11-24-2026.md`: Study C `LORO` smoothed 95% CIs (`[0.1296, 0.1691]`, `[1.5542, 1.8732]`, `[0.7345, 0.8117]`), `t2_sonnet5|D0` `C_ms_gold = 0.9957`, Study C paired task sign-flip draws (`2,000`), and `LORO` single-draw Spearman draws (`500`).
  2. Applied both hardening notes: fixed the stale `200` comment to `500` in `scripts/metrics.py`, and changed `_selection_regret`'s tie-breaker in `scripts/run_expansion.py` to strictly label-free `r["config"]`.
  3. Applied both internal plan-review prose fixes: corrected `Dual-Tasking (DT)` -> `Differential Testing (DT)` across `README.md` and `RESULTS_proper_scoring_expansion_11-24-2026.md` and fixed the RPS empirical indicator typo `1{r >= k}` -> `1{r <= k}` in `RESULTS_proper_scoring_expansion_11-24-2026.md`.
  4. Re-ran full deterministic verification (`unittest`, `run_expansion.py`, `experiment_layout.py --check`, `git diff --check`, and secret scan) after all final edits.
