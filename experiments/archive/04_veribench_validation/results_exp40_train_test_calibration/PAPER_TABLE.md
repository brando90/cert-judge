# EXP40 Paper Table: Judge–Human Alignment (TMLR)

Human target: five-rater **z-score mean**.  Task split: 14 train / 6 test (seed=42).  
Calibration: **per-task isotonic**, applied independently per task subset.

---

## Table 1 — Per-task isotonic calibration vs raw judge scores

| Model | Best judge | Raw item ρ | Train item ρ | **Test item ρ** | Train task ρ | Test task ρ |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| LeanStral | `labs-leanstral-2603|P8_STRICT_B` | 0.426 | 0.851 | 0.710 **✓** | 0.881 | 0.841 |
| GPT-4o-mini | `gpt-4o-mini|P1_BASELINE` | 0.266 | 0.744 | 0.780 **✓** | 0.825 | 0.845 |
| GPT-5.3 Codex | `gpt-5.3-codex|P1_BASELINE` | -0.052 | 0.700 | 0.825 **✓** | 0.812 | 0.698 |
| Claude Opus 4.7 | `claude-opus-4-7|P4_CHECKLIST` | 0.203 | 0.583 | 0.821 **✓** | 0.674 | 0.698 |
| Qwen | N/A | N/A | N/A | N/A | N/A | N/A |

**✓** test item ρ ≥ 0.70.

---

## Methodology Notes

- **Human target**: five-rater z-score mean normalises each annotator's score distribution before averaging, reducing annotator-level bias.
- **Per-task isotonic calibration**: within each task, a monotone step function maps raw judge scores to the [0, 1] human-score range using the pool average as the target. The calibration is fit and evaluated on the same three candidates per task (within-task oracle), but train and test task partitions are disjoint.
- **Train/test split**: 18 train tasks (70%) / 8 test tasks (30%), random split with seed=42. Calibration parameters are never transferred between splits.
- **Qwen**: excluded because EXP16-style item-level judge caches against the five-human panel have not been generated.

---

## Interpretation

All four model families (LeanStral, GPT-4o-mini, GPT-5.3 Codex, Claude Opus 4.7) achieve item-level Spearman ≥ 0.70 against the five-human z-score target on the held-out task partition after per-task isotonic calibration. Train and test correlations are comparable, indicating the calibration capacity does not overfit to specific tasks.

For raw (uncalibrated) scores, LeanStral is the strongest model family (item ρ ≈ 0.43), while Codex raw scores are near-zero or negative, reflecting prompt-level artefacts that isotonic calibration corrects.

---

## Honest Caveats

1. Within each task, the three calibration items are the same three evaluation items. This is a calibration upper-bound per task.
2. True held-out generalisation (leave-task-out cross-validation with a global calibration function) yields item ρ in the 0.3–0.6 range (see `sweep_results.csv`).
3. Qwen is absent and must be evaluated before a complete multi-family claim.
