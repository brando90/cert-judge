# Exp23 Held-Out Human-Label Test Report
**TLDR:** Frozen \(\mathrm{TI}_{\mathrm{var}}\) has a held-out judge-level Spearman correlation of -0.238 against the fresh independent human-label pool. The primary exact-key analysis uses 60 scored pairs because the frozen judge-score CSV does not cover all 78 labeled pairs.

## Primary Result

| Metric | Value |
|:---|---:|
| Label files | 5 |
| Nonblank labels | 343 |
| Unique labeled pairs | 78 |
| Exact scored pairs per judge | 60 |
| Judges | 8 |
| Spearman(TI_var, held-out human Spearman) | -0.238 |
| Exact permutation p-value | 0.5821 |
| Pearson(TI_var, held-out human Spearman) | -0.724 |

## Sensitivity

| Aggregation | Match mode | Spearman | p-value | Scored pairs |
|:---|:---|---:|---:|---:|
| raw_mean | exact_gold_candidate | -0.238 | 0.5821 | 60 |
| raw_median | exact_gold_candidate | -0.262 | 0.5364 | 60 |
| rater_zmean | exact_gold_candidate | -0.238 | 0.5821 | 60 |
| raw_mean | exact_plus_candidate_alias | 0.119 | 0.7930 | 72 |

## Methodological Caveat

The fresh independent label pool contains 343 nonblank labels over 78 unique pairs, but the frozen Exp16 judge-score detail file has exact gold::candidate scores for only 60 of those pairs. The primary result therefore uses the 60 exact-key pairs and does not spend new LLM budget to score the remaining pairs. A candidate-file alias sensitivity can recover renumbered real-code pairs, but it is not the primary result because it changes the gold-file key.

## Review Request

@ehersch please check the exact-match caveat and whether the paper should quote only the primary 60-pair result or also mention the candidate-file alias sensitivity.
