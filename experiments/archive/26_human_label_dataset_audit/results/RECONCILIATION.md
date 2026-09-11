# EXP21b: reconciling the paper's inter-pass statistics

Paper values (`paper_latex/TMLR_2026/main.tex` lines 388 / 1043 / 1056 / 1057):

| stat | paper |
| --- | ---: |
| spearman | 0.249 |
| pearson | 0.375 |
| kendall | 0.221 |
| qwk | 0.372 |
| mae | 0.778 |
| mse | 1.139 |

The only ambiguity in the raw data is `ethan_human_scores_ORIGINAL.tsv`, which has 78 rows for 75 pairs: the problem `4_json_decoder.lean` appears twice (all 3 of its candidates).

## Convention sweep

Each row is one way of collapsing those duplicate rows, crossed with the row subset.
`|delta|` is the max absolute deviation from the paper across the 6 statistics.

| dupe rule | subset | n | Spearman | Pearson | Kendall | QWK | MAE | MSE | max abs delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `mean_of_dupes` | `all_pairs` | 75 | 0.280 | 0.398 | 0.251 | 0.336 | 0.767 | 1.103 | 0.036 |
| `mean_of_dupes` | `drop_4_json_decoder` | 72 | 0.169 | 0.207 | 0.154 | 0.185 | 0.778 | 1.139 | 0.187 |
| `first_of_dupes` | `all_pairs` | 75 | 0.280 | 0.424 | 0.251 | 0.390 | 0.773 | 1.120 | 0.049 |
| `first_of_dupes` | `drop_4_json_decoder` | 72 | 0.169 | 0.207 | 0.154 | 0.185 | 0.778 | 1.139 | 0.187 |
| `last_of_dupes` | `all_pairs` | 75 | 0.273 | 0.366 | 0.245 | 0.336 | 0.760 | 1.107 | 0.036 |
| `last_of_dupes` | `drop_4_json_decoder` | 72 | 0.169 | 0.207 | 0.154 | 0.185 | 0.778 | 1.139 | 0.187 |
| `min_of_dupes` | `all_pairs` | 75 | 0.280 | 0.424 | 0.251 | 0.390 | 0.773 | 1.120 | 0.049 |
| `min_of_dupes` | `drop_4_json_decoder` | 72 | 0.169 | 0.207 | 0.154 | 0.185 | 0.778 | 1.139 | 0.187 |
| `max_of_dupes` | `all_pairs` | 75 | 0.273 | 0.366 | 0.245 | 0.336 | 0.760 | 1.107 | 0.036 |
| `max_of_dupes` | `drop_4_json_decoder` | 72 | 0.169 | 0.207 | 0.154 | 0.185 | 0.778 | 1.139 | 0.187 |

**Closest convention:** `max_of_dupes` / `all_pairs` (n=75), max abs deviation `0.036`.

> No convention reproduces the published numbers exactly. The published inter-pass
> statistics therefore came from a **snapshot of the label files that no longer matches**
> what is on disk (or from an intermediate cleaned frame that was not checked in).
> The qualitative claim ("agreement between passes is moderate") survives under every
> convention; the exact decimals do not.

## QWK grid sensitivity (mean-of-dupes, all 75 pairs)

| QWK variant | value | paper 0.372 |
| --- | ---: | --- |
| `qwk_round` | 0.336 | **MISMATCH** |
| `qwk_floor` | 0.390 | **MISMATCH** |
| `qwk_ceil` | 0.336 | **MISMATCH** |
| `qwk_half_grid` | 0.366 | **MISMATCH** |

## Is the `avg` file really mean(pass1, pass2)?

- reproduces on **73/75** pairs
- exceptions:

| pair | avg file | pass1 | pass2 (mean-of-dupes) | mean(pass1,pass2) |
| --- | ---: | ---: | ---: | ---: |
| `0_unsafeMultiply_safe.lean` / `0_unsafeMultiply_safe__agent1.lean` | 5 | 4 | 5 | 4.5 |
| `0_unsafeMultiply_safe.lean` / `0_unsafeMultiply_safe__agent2.lean` | 5 | 4 | 5 | 4.5 |

## Problem-level composition of every rater file

Which gold problems each file actually contains (`.lean` suffix stripped).
This is what makes the overlap counts in `AUDIT.md` non-obvious.

| problem | pass1 | pass2 | p1_correct_prompt | p2 | p3 | p4 | p5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0_bisect_right` | 3 | 3 | 3 | 3 | 2 | 3 | 3 |
| `0_unsafeCopy_safe` | 3 | 3 | 3 | 3 | - | 3 | 3 |
| `0_unsafeMultiply_safe` | 3 | 3 | 3 | - | - | - | - |
| `13_MyUppercase` | 3 | 3 | 2 | 3 | - | 3 | 3 |
| `18_MyFibonacci` | 3 | 3 | 3 | 3 | - | 3 | 3 |
| `1_MyAdd` | 3 | 3 | 3 | 3 | - | 3 | 3 |
| `1_bisect_left` | 3 | 3 | - | - | - | - | - |
| `1_unsafeMultiply_safe` | - | - | - | 3 | - | 3 | 3 |
| `24_json_decoder` | - | - | 3 | 3 | 3 | 3 | 3 |
| `2_bisect_left` | - | - | 3 | 3 | 3 | 3 | 3 |
| `2_heappush` | 3 | 3 | - | - | - | - | - |
| `33_MyMinimum` | 3 | 3 | 3 | 3 | - | 3 | 3 |
| `3_heappop` | 3 | 3 | - | - | - | - | - |
| `43_replace_spaces` | 3 | 3 | 3 | 3 | - | 3 | 3 |
| `4_heappush` | - | - | 3 | 3 | 3 | 3 | 3 |
| `4_json_decoder` | 3 | 3 | - | - | - | - | - |
| `4_unsafeCounter_safe` | 3 | 3 | 3 | 3 | - | 3 | 3 |
| `5_heappop` | - | - | 3 | 3 | 3 | 3 | 3 |
| `5_unsafeFormatString_safe` | 3 | 3 | 3 | 3 | - | 3 | 3 |
| `9_pathTraversal_safe` | 3 | 3 | 3 | 3 | - | 3 | 3 |
| `binary_search` | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| `bubble_sort` | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| `humaneval_13__gcd` | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| `humaneval_31_is_prime` | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| `humaneval_3_below_zero` | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| `humaneval_47_median` | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| `humaneval_8_sum_product` | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| `insertion_sort` | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| `merge_sort` | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| `selection_sort` | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| **total problems** | 25 | 25 | 25 | 25 | 15 | 25 | 25 |

- distinct problems across **all** human-label files: **30**
- distinct problems in the `n=75` calibration panel: **25**
- distinct problems in the 5-rater held-out pool: **26**
- in pool but not panel: `1_unsafeMultiply_safe`, `24_json_decoder`, `2_bisect_left`, `4_heappush`, `5_heappop`
- in panel but not pool: `1_bisect_left`, `2_heappush`, `3_heappop`, `4_json_decoder`

