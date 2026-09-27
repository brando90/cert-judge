# Experiment 39: live results

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/39_best_of_k_judge_selection_bias_validation_set/results.md>

**Status:** DONE (started 09-26-2026 16:56 PDT; completed 09-26-2026 17:25 PDT)
**Last updated:** 09-26-2026 17:25 PDT

| Phase | Status | Evidence |
|---|---|---|
| Register experiment, freeze protocol | DONE | `PROTOCOL.md` frozen 16:56 PDT, commit `7548c3a` |
| Build configuration pool; reproduction gate | DONE | 109 distinct configurations of 185 scanned. The gate stopped the first run; all 18 over-tolerance deviations were explained mechanically (10 floating-point ties, 7 older averaged-label file, 1 both) and recorded as Deviation 1 in commit `d5d6ea2` |
| A. Null best-of-K | DONE | Best of 8 with permuted labels: mean Spearman 0.150 (95th pct 0.317); best of 109: 0.263 (0.399) |
| B. Split-half selection | DONE | Best of 8 chosen on 12 problems: 0.488 there, 0.335 on the other 12 (overstatement +0.153, SE 0.004) |
| C. Synthetic sweep | DONE | Label model extended with problem-clustered rater noise (Deviation 2). Reproduces B within 0.02 at 36 items; +0.100 at K = 8 and +0.149 at K = 32 for 72 items |
| D. Judge-level adjustment | DONE | Max over 4 index forms multiplies the exact p-values by 1.9–3.2; Codex averaged 0.015 → 0.037; 4 of 9 cells below 0.05 instead of 6 |
| Report and drafted sentences | DONE | `REPORT.md`; drafted text builds in a scratch copy of the paper (21 pages, main text still ends on page 9 with 9 lines free) |

## Headline numbers (averaged labels unless stated)

| Quantity | Value |
|---|---|
| Pool | 109 configurations; agreement −0.083 to 0.506, median 0.315 |
| Null best of 8 / 32 / 109: mean (95th pct) | 0.150 (0.317) / 0.216 (0.360) / 0.263 (0.399) |
| Configurations above the null-maximum 95th percentile | 31 of 109 |
| Split-half overstatement, labels rule, K = 8 / 32 / 109 | +0.153 / +0.236 / +0.297 (pass1 +0.117 / +0.167 / +0.218; pass2 +0.194 / +0.286 / +0.368) |
| Held-out agreement at K = 8: labels / v1 index / random / best in subset | 0.335 / 0.258 / 0.278 / 0.492 |
| Modelled overstatement for all 72 pairs, K = 8 / 32 / 64 | +0.100 / +0.149 / +0.170 |
| Judge-level p, Codex averaged, two-sided unadjusted → adjusted | 0.015 → 0.037 |

No model calls, credentials or network were used for the analysis; the inputs are frozen archive files. The one network use was downloading Tectonic and its TeX packages for the drop-in build.

**TLDR-end:** [cj: exp39 selection bias] Done: choosing the best of 8 configurations on the validation labels overstates its agreement by 0.15 on half-panels and about 0.10 on all 72 pairs, and the index-form adjustment leaves 4 of 9 judge-level cells below 0.05.
