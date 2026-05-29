# EXP38: Five-Rater Mean + Per-Task Isotonic Calibration

Five-rater `mean` target with per-task isotonic calibration. Best LLM item Spearman: `0.840` (labs-leanstral-2603|P1_BASELINE) vs raw `0.422`.

## Human Target
- Method: `mean`
- Items: `78`
- Overlap with judge panel: `60` items / `20` tasks

## Top Calibrated LLM Judges (Item-Level)

| Judge | Raw rho | Per-task iso rho | Raw task rho | n items |
| --- | ---: | ---: | ---: | ---: |
| `gpt-4o-mini|P1_BASELINE` | 0.263 | 0.843 | 0.353 | 60 |
| `labs-leanstral-2603|P1_BASELINE` | 0.422 | 0.840 | 0.541 | 60 |
| `labs-leanstral-2603|P8_STRICT_B` | -0.008 | 0.803 | -0.042 | 60 |
| `labs-leanstral-2603|P4_CHECKLIST` | -0.278 | 0.762 | -0.333 | 60 |
| `gpt-5.3-codex|P8_STRICT_B` | -0.487 | 0.758 | -0.617 | 60 |
| `gpt-5.3-codex|P14_HUMAN_ALIGN_V2` | -0.080 | 0.722 | -0.139 | 60 |
| `gpt-5.3-codex|P3_CONCISE` | -0.397 | 0.714 | -0.568 | 60 |
| `claude-opus-4-7|P4_CHECKLIST` | -0.252 | 0.682 | -0.296 | 60 |
| `gpt-5.3-codex|P11_JSON_FIRST` | -0.222 | 0.651 | -0.326 | 60 |
| `gpt-4o-mini|P4_CHECKLIST` | -0.010 | 0.554 | -0.040 | 60 |
| `claude-opus-4-7|P1_BASELINE` | 0.189 | 0.549 | 0.327 | 60 |
| `gpt-5.3-codex|P2_FORMAL` | -0.286 | 0.506 | -0.337 | 60 |

## Outputs
- `per_judge_metrics.csv`
- `item_predictions.csv`
- `task_predictions.csv`
- `human_item_targets.csv`
- `plots/`

## Caveat
Per-task isotonic fits a monotone map on each task's three candidates using the same items used for evaluation (calibration upper bound, analogous to EXP32).
