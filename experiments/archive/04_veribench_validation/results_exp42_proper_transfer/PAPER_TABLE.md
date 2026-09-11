# EXP42 Judge–Human Alignment: Proper Calibration Transfer

Human target: **zscore_mean** (five-rater z-score mean)  
Train/test split: 18 train tasks / 8 test tasks (seed=42)  
Calibration: **global isotonic** (PAV), fit on train tasks, applied to test tasks.  
**No test-task human labels used anywhere in the calibration pipeline.**

Best prompt per model family selected by raw item Spearman on train tasks only.

---

## Primary Table — Global Isotonic Calibration Transfer

| Model | Best judge | Raw item ρ | Train item ρ | **Test item ρ** | Train task ρ | Test task ρ |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| LeanStral | `labs-leanstral-2603|P1_BASELINE` | 0.426 | 0.566 | -0.084 | 0.716 | -0.174 |
| GPT-4o-mini | `gpt-4o-mini|P1_BASELINE` | 0.266 | 0.419 | 0.295 | 0.574 | 0.239 |
| GPT-5.3 Codex | `gpt-5.3-codex|P7_STRICT_A` | -0.052 | 0.119 | -0.460 | 0.235 | -0.530 |
| Claude Opus 4.7 | `claude-opus-4-7|P1_BASELINE` | 0.203 | -0.001 | -0.108 | 0.021 | 0.185 |
| Qwen | N/A | N/A | N/A | N/A | N/A | N/A |

**✓** = Test item ρ ≥ 0.70.

---

## Oracle Upper Bound (per-task isotonic, same items — NOT held-out)

| Model | Best judge | Full item ρ | Full task ρ |
| --- | --- | ---: | ---: |
| LeanStral | `labs-leanstral-2603|P1_BASELINE` | 0.675 | 0.759 |
| GPT-4o-mini | `gpt-4o-mini|P1_BASELINE` | 0.843 **✓** | 0.910 |
| GPT-5.3 Codex | `gpt-5.3-codex|P7_STRICT_A` | 0.472 | 0.504 |
| Claude Opus 4.7 | `claude-opus-4-7|P1_BASELINE` | 0.870 **✓** | 0.934 |
| Qwen | N/A | N/A | N/A |

---

## Methodology

- **Global isotonic calibration**: fit a single monotone step function (PAV) on all
  train-task items (judge score → human score). Applied as-is to test-task judge scores.
  No per-task adaptation — the calibration must transfer across tasks.
- **Split**: tasks randomly partitioned 70/30 by seed. Calibration never touches test labels.
- **Oracle**: per-task isotonic on the same 3 items used for evaluation — an upper bound,
  not a valid claim for unseen tasks.
- **Qwen**: excluded — no item-level judge caches against the five-human panel.

## Honest Assessment

- Global calibration transfers the monotone shape learned on train tasks.
- Per-task scale differences (task difficulty) are NOT corrected without test labels.
- This is the most defensible claim for TMLR: held-out test ρ with zero test leakage.
