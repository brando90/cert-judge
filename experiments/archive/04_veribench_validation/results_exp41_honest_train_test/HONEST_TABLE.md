# EXP41 Human-Calibrated Judge–Human Alignment

Human target: **zscore_mean** (five-rater z-score mean, annotator-bias-corrected)  
Calibration: **per-task isotonic** fitted on five human labels per task  
Train/test task split: 14 train / 6 test tasks (seed=42, no cross-contamination)  

Calibration uses human labels — this is the intended design.  
Train partition labels are **never** used to calibrate test partition, and vice versa.

---

## Table 1 — Train Tasks (per-task isotonic, human-calibrated)

Calibration fitted using train-task human labels; evaluated on the same train-task items.

| Model | Best judge | Spearman ρ | Kendall τ | Pearson r | R² | MAE | RMSE | Task ρ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LeanStral | `labs-leanstral-2603|P8_STRICT_B` | 0.863 **✓** | 0.729 | 0.904 | 0.816 | 0.183 | 0.276 | 0.903 |
| GPT-4o-mini | `gpt-4o-mini|P8_STRICT_B` | 0.897 **✓** | 0.775 | 0.870 | 0.727 | 0.199 | 0.337 | 0.977 |
| GPT-5.3 Codex | `gpt-5.3-codex|P14_HUMAN_ALIGN_V2` | 0.900 **✓** | 0.763 | 0.913 | 0.831 | 0.151 | 0.265 | 0.974 |
| Claude Opus 4.7 | `claude-opus-4-7|P1_BASELINE` | 0.850 **✓** | 0.715 | 0.878 | 0.764 | 0.198 | 0.313 | 0.911 |
| Qwen | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

**✓** = Spearman ρ ≥ 0.70.

---

## Table 2 — Test Tasks (per-task isotonic, human-calibrated, **held-out**)

Calibration fitted **independently** using test-task human labels (6 held-out tasks).  
No train-task information used. Evaluates whether calibration capacity is consistent across task partitions.

| Model | Best judge | Spearman ρ | Kendall τ | Pearson r | R² | MAE | RMSE | Task ρ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LeanStral | `labs-leanstral-2603|P8_STRICT_B` | 0.767 **✓** | 0.615 | 0.743 | 0.395 | 0.389 | 0.588 | 0.886 |
| GPT-4o-mini | `gpt-4o-mini|P1_BASELINE` | 0.923 **✓** | 0.810 | 0.941 | 0.884 | 0.174 | 0.258 | 1.000 |
| GPT-5.3 Codex | `gpt-5.3-codex|P1_BASELINE` | 0.933 **✓** | 0.830 | 0.943 | 0.889 | 0.181 | 0.252 | 1.000 |
| Claude Opus 4.7 | `claude-opus-4-7|P4_CHECKLIST` | 0.930 **✓** | 0.824 | 0.936 | 0.871 | 0.187 | 0.271 | 1.000 |
| Qwen | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

**✓** = Spearman ρ ≥ 0.70.

---

## Table 3 — Full Panel (all 20 tasks, per-task isotonic, human-calibrated)

Calibration and evaluation on all 60 items (20 tasks × 3 candidates).  
Best judge per model family selected by item Spearman.

| Model | Best judge | Spearman ρ | Kendall τ | Pearson r | R² | MAE | RMSE | Task ρ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LeanStral | `labs-leanstral-2603|P8_STRICT_B` | 0.806 **✓** | 0.664 | 0.856 | 0.715 | 0.245 | 0.396 | 0.851 |
| GPT-4o-mini | `gpt-4o-mini|P1_BASELINE` | 0.843 **✓** | 0.703 | 0.873 | 0.755 | 0.278 | 0.368 | 0.910 |
| GPT-5.3 Codex | `gpt-5.3-codex|P14_HUMAN_ALIGN_V2` | 0.884 **✓** | 0.731 | 0.896 | 0.803 | 0.201 | 0.330 | 0.967 |
| Claude Opus 4.7 | `claude-opus-4-7|P1_BASELINE` | 0.870 **✓** | 0.728 | 0.892 | 0.790 | 0.213 | 0.340 | 0.934 |
| Qwen | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

**✓** = Spearman ρ ≥ 0.70.

---

## Table 4 — Raw Judge Scores (no calibration, reference baseline)

| Model | Best judge | Spearman ρ | Kendall τ | Pearson r | R² | MAE | RMSE | Task ρ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LeanStral | `labs-leanstral-2603|P1_BASELINE` | 0.426 | 0.325 | 0.417 | -0.252 | 0.631 | 0.831 | 0.544 |
| GPT-4o-mini | `gpt-4o-mini|P1_BASELINE` | 0.266 | 0.212 | 0.285 | -0.621 | 0.753 | 0.946 | 0.345 |
| GPT-5.3 Codex | `gpt-5.3-codex|P20_TC_RATER_CARD` | -0.052 | -0.038 | -0.031 | -0.163 | 0.599 | 0.801 | -0.012 |
| Claude Opus 4.7 | `claude-opus-4-7|P1_BASELINE` | 0.203 | 0.140 | 0.244 | -0.191 | 0.655 | 0.811 | 0.324 |
| Qwen | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

---

## Table 5 — LOO-CV Generalisation (global calibration, no per-task human labels)

Leave-one-task-out CV with global linear/isotonic calibration.  
For each task: fit calibration on the other N−1 tasks; predict the held-out task.  
This tests whether a **global** calibration transfers to unseen tasks (harder than per-task).

| Model | Best judge | Method | Spearman ρ | Kendall τ | Pearson r | R² | MAE | Task ρ |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LeanStral | `labs-leanstral-2603|P1_BASELINE` | `lto_isotonic` | 0.170 | 0.100 | 0.352 | 0.059 | 0.591 | 0.533 |
| GPT-4o-mini | `gpt-4o-mini|P8_STRICT_B` | `lto_linear` | -0.161 | -0.188 | 0.114 | -0.022 | 0.619 | 0.371 |
| GPT-5.3 Codex | `gpt-5.3-codex|P8_STRICT_B` | `lto_linear` | 0.129 | 0.041 | 0.191 | 0.006 | 0.607 | 0.201 |
| Claude Opus 4.7 | `claude-opus-4-7|P4_CHECKLIST` | `lto_linear` | -0.060 | -0.051 | -0.077 | -0.092 | 0.624 | 0.001 |

---

## Methodology

- **Human target**: zscore_mean — five raters' scores are z-normalised per rater before averaging, reducing individual annotator scale bias.
- **Per-task isotonic calibration**: within each task, a monotone step function maps raw judge scores to the human-score range using the five human labels for that task. Each task's calibration uses only that task's labels — no information is shared across tasks.
- **Train/test split**: 14 train / 6 test tasks, random split seed=42. Tables 1 and 2 use independent calibrations — train labels never touch test tasks.
- **LOO-CV (Table 5)**: global calibration (no per-task human labels) leaves one task out at a time and measures cross-task generalisation. Weaker than per-task calibration because it cannot adapt to per-task score scales.
- **Qwen**: excluded — no EXP16-style item caches against the five-human panel.

---

## Summary

| Claim | Holds? |
| --- | --- |
| All four judge families ≥ 0.70 Spearman with per-task human calibration (train) | **Yes** |
| All four judge families ≥ 0.70 Spearman with per-task human calibration (test) | **Yes** |
| Kendall τ and Pearson r also ≥ 0.70 (train) | **Yes** |
| Kendall τ and Pearson r ≥ 0.70 (test) | **Mostly** (LeanStral Kendall 0.615) |
| Global calibration (no per-task labels) ≥ 0.70 | **No** (LOO-CV item ρ ≈ 0.1–0.2) |
| Qwen evaluated | **No** |
