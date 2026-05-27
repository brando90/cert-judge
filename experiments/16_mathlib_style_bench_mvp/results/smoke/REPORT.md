# Mathlib Style Bench MVP Report
**TLDR:** This report scores whether a style judge ranks the accepted mathlib-style Lean file above the intentionally worse Lean file for each pair.

## Summary

- MSB-MVP score: `1.0000`
- Style order score: `1.0000`
- Mean good-minus-bad margin: `0.4600`
- P4 stability: `1.0000`
- Scored pairs: `3/3`

## Pair Results

| Pair | Topic | Bad | Good | Margin | Order | Pass |
|---|---|---:|---:|---:|---:|---|
| `list_length_map` | List | 0.640 | 0.980 | +0.340 | 1.0 | PASS |
| `nat_add_comm` | Nat arithmetic | 0.480 | 0.980 | +0.500 | 1.0 | PASS |
| `nat_zero_add` | Nat arithmetic | 0.440 | 0.980 | +0.540 | 1.0 | PASS |

## Metric

`MSB-MVP = 0.70 * style_order_score + 0.20 * margin_strength + 0.10 * P4_stability`.
The order term reuses `cert_judge.hsj_scoring.compute_p2_or_p3_ordering_auc` on a two-level style-defect ladder: good code has defect count 0, bad code has defect count 1.
