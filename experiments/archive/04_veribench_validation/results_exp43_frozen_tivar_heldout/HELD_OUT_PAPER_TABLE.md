# EXP43 TMLR Paper Table: Frozen TIvar Held-Out Validation

Human target: mean of participant1–5 (343 labels, 60 overlapping items per judge).  
TIvar frozen from EXP30; labels never seen during TIvar development.  

| Judge family | n | Held-out ρ (95% CI) | Calib ρ (avg) |
| --- | ---: | --- | ---: |
| GPT-5.3-Codex | 8 | -0.071 [-0.852, 0.950] | 0.762 **✓** |
| Claude Opus 4.7 | 8 | 0.119 [-0.852, 0.918] | 0.429 |
| Qwen3-Coder-30B | 8 | -0.333 [-1.000, 0.615] | 0.667 |
| LeanStral | 8 | 0.048 [-0.919, 0.974] | -0.333 |

**✓** = ρ ≥ 0.70.

**Held-out ρ**: Spearman between frozen TIvar and judge-level human Spearman
on the held-out participant corpus. Calibration panel labels were never used.
