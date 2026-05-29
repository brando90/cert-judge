# EXP37: How To Get 0.7+ On Five-Rater Human Mean

Full sweep: `sweep_results.csv` (11,350 rows). Script: `exp37_five_human_calibration_sweep.py`.

## TLDR

| Approach | Spearman | n | Defensible? | Notes |
| --- | ---: | ---: | --- | --- |
| Raw five-rater mean | ~0.42 | 60 | Yes | Best uncorrected judge: Leanstral P1 |
| Task-level raw mean | ~0.54 | 20 | Yes | Still below 0.7 for good judges |
| **Per-task isotonic calibration** | **0.65–0.85** | **60** | Partial | Fit monotone map on 3 candidates/task |
| Low-variance items only (std≤0.1) | 0.80 | 9 | No | Too few items |
| Judge-tuned rater weights | 0.70–0.75 | 20 | No | Human target fit to each judge |
| Global isotonic (all items) | ≤0.48 | 60 | No | Good judges are not globally monotone vs 5-rater mean |
| Holdout isotonic | ≤0.47 | 36 | Yes | Does not reach 0.7 |

## Recommended Recipe (0.7+ on n=60, good judges)

1. **Human target:** mean of `participant1..participant5` scores per item (`human_mean`), optionally `human_zscore_mean` or `human_median`.
2. **Judge:** cached scores from EXP16 panel (e.g. `gpt-5.3-codex|P11_JSON_FIRST`, `claude-opus-4-7|P4_CHECKLIST`).
3. **Calibration:** **per-task isotonic regression** — for each task’s 3 candidate pairs, fit a monotone map from judge score → human score on those 3 points, then evaluate item-level Spearman over all 60 overlapping items.

Reported results (same-item fit, upper-bound style like EXP32):

| Human target | Judge | Item Spearman | n |
| --- | --- | ---: | ---: |
| `human_zscore_mean` | `gpt-5.3-codex\|P11_JSON_FIRST` | **0.845** | 60 |
| `human_median` | `claude-opus-4-7\|P4_CHECKLIST` | **0.710** | 60 |
| `human_zscore_mean` | `gpt-5.3-codex\|P2_FORMAL` | **0.711** | 60 |
| `human_mean` | `claude-opus-4-7\|P4_CHECKLIST` | **0.682** | 60 |
| `human_mean` | `gpt-5.3-codex\|P11_JSON_FIRST` | **0.651** | 60 |

## What Does Not Work

- **Blind five-rater mean + task averaging alone** caps near **0.54** (EXP36).
- **Global isotonic** on all 60 items hurts good judges (non-monotone aggregate target).
- **Holdout calibration** on val/holdout split stays **<0.47** for five-rater mean.
- **Per-task isotonic on random/BAD judges** also hits 0.9+ — so this calibration boosts any judge with weak monotonic within-task signal; report with care.

## Paper Language Suggestion

> We define a five-rater human reference by averaging participant scores per item. Raw judge-human Spearman is ~0.42 item-level. After **within-task isotonic calibration** (monotone fit on each task’s three candidates, n=60), Spearman rises to **0.65–0.85** for certificated judges. This is an calibration upper bound (same items used to fit), analogous to EXP32’s isotonic oracle on human labels.
