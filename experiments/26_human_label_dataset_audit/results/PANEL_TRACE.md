# EXP21c: the panel the published analyses actually ran on

## 1. Judge-alignment runs (EXP16) report `n = 72`, not 75

Source: `experiments/04_veribench_validation/results_exp16_final_robust/summary.json`

| field | value |
| --- | ---: |
| `n_judges` | 8 |
| `n_union_rows` | 72 |
| `n_skipped_pairs` | 3 |
| `judge_rows[0].n_human_rows_pass1` | 72 |
| `judge_rows[0].n_human_rows_pass2` | 72 |
| `judge_rows[0].n_human_rows_avg` | 72 |

`skipped_pairs.csv` -- the 3 human-rated pairs that every judge analysis drops:

| gold_file | candidate_file | reason |
| --- | --- | --- |
| `0_unsafeMultiply_safe.lean` | `0_unsafeMultiply_safe__agent0.lean` | `missing_gold` |
| `0_unsafeMultiply_safe.lean` | `0_unsafeMultiply_safe__agent1.lean` | `missing_gold` |
| `0_unsafeMultiply_safe.lean` | `0_unsafeMultiply_safe__agent2.lean` | `missing_gold` |

> **Root cause:** {'missing_gold': 3}. The human annotator rated a 25th problem whose Lean
> source file is not present in the artifact corpus, so no judge can score it. The labels
> exist; the code under test does not.

- filesystem check for `0_unsafeMultiply_safe.lean`: 0 match(es) -> **absent from the repo**

## 2. The inter-pass reliability numbers (EXP18) also ran on `n = 72`

Source: `experiments/04_veribench_validation/results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json`

| field | value |
| --- | ---: |
| `n_pass1_pairs` | 72 |
| `n_pass2_pairs` | 75 |
| `n_overlap_pairs` | 72 |
| `n_pass1_only` | 0 |
| `n_pass2_only` | 3 |

| statistic | cached run | paper | match? |
| --- | ---: | ---: | --- |
| Spearman | 0.2486 | 0.249 | MATCH |
| Pearson | 0.3747 | 0.375 | MATCH |
| Kendall tau | 0.2214 | 0.221 | MATCH |
| QWK | 0.3718 | 0.372 | MATCH |
| MAE | 0.7708 | 0.778 | **MISMATCH** |
| MSE (= rmse^2) | 1.1215 | 1.139 | **MISMATCH** |

> The four correlation statistics reproduce the paper exactly. **MAE and MSE do not.**
> `0.778 = 56/72` and `1.139 = 82/72` are the values obtained when the three duplicated
> `4_json_decoder` rows take pass2 `= 1.0` (first-of-duplicates) instead of `1.5`
> (mean-of-duplicates). The appendix ceiling table therefore mixes two duplicate-handling
> conventions across its own rows.

- if the three `1.5` pass2 scores are `1.0`: MAE = 0.7778, MSE = 1.1389
- if the three `1.5` pass2 scores are `1.5`: MAE = 0.7708, MSE = 1.1215
- if the three `1.5` pass2 scores are `2.0`: MAE = 0.7639, MSE = 1.1250

## 3. What changed between the cached runs and the files on disk

- cached analyzed panel: **72** pairs / **24** problems
- current on-disk panel:  **75** pairs / **25** problems
- pairs added since:   `0_unsafeMultiply_safe__agent0.lean`, `0_unsafeMultiply_safe__agent1.lean`, `0_unsafeMultiply_safe__agent2.lean`
- pairs removed since: (none)
- pass1 scores changed on the shared pairs: **0**

> So the underlying ratings are stable; the only delta is that the extra problem
> `0_unsafeMultiply_safe` (3 pairs) was added to the label file *after* the analyses ran,
> and it is precisely the problem that gets skipped for a missing gold artifact.
> **`75` is the label-file row count. `72` is the analyzed panel. Every published
> judge-alignment and inter-pass number in the paper is a `72`-pair number.**

## 4. Exact decomposition of the two stacked `*_set_data.tsv` files

### `experiments/human_labels/expert_harsh_set_data.tsv` (193 rows)

Components are peeled off in order, so the `rows accounted` column sums to the file total.

| component | file rows | rows accounted | fully absorbed |
| --- | ---: | ---: | --- |
| `participant1_data_correct_prompt.tsv` | 74 | 74 | yes |
| `participant2_data_pass_1.tsv` | 75 | 75 | yes |
| `participant3_data_pass_1.tsv` | 44 | 44 | yes |
| **sum** | | **193** | vs file total **193**, unexplained **0** |

### `experiments/human_labels/lenient_set_data.tsv` (297 rows)

Components are peeled off in order, so the `rows accounted` column sums to the file total.

| component | file rows | rows accounted | fully absorbed |
| --- | ---: | ---: | --- |
| `participant4_data_pass_1.tsv` | 75 | 75 | yes |
| `participant5_data_pass_1.tsv` | 75 | 75 | yes |
| `old_prompt/participant1_data_pass_1.tsv` | 75 | 75 | yes |
| `ethan_human_scores_20260425.tsv (72-row subset)` | 75 | 72 | partial |
| **sum** | | **297** | vs file total **297**, unexplained **0** |

> `expert_harsh_set_data.tsv` and `lenient_set_data.tsv` are **long-format concatenations
> of other rater files**, not independent rating sets. Averaging them naively double-counts
> raters. Note `lenient_set_data.tsv` mixes rubrics: it contains both lenient passes *and*
> the harsher `ethan_human_scores_20260425` pass (as its 72-row subset).

## 5. Labeling-protocol drift, quantified

Same annotator (participant 1 / Ethan), two different rubric prompts. The paper's
abstract cites a cross-protocol label correlation of `~0.13`:

| old-prompt view | vs `participant1_data_correct_prompt` | n | Pearson |
| --- | ---: | ---: | ---: |
| `pass1 (old prompt)` | 0.076 | 62 | 0.064 |
| `pass2 (old prompt)` | 0.165 | 62 | 0.052 |
| `avg (old prompt)` | 0.128 | 62 | 0.070 |
| **mean** | **0.123** | | |

> The same person rating the same artifacts under a different rubric prompt produces
> **nearly uncorrelated** scores. That is the reason the frozen held-out test returned a
> null: the calibration panel and the five-rater pool are not the same measurement construct.

