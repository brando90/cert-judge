### T1. Old set, per judge series, against the corrected VeriBench labels (H_vb: 59 artifacts, 20 tasks, 4.5 ratings each). Lower is better for RPS, CE, TVD. Intervals: task-bootstrap 95%.

| family | judge series | RPS [95%] | CE | TVD | Spearman [95%] | Pearson |
|---|---|---|---|---|---|---|
| Codex | gpt-5.3-codex|P8_STRICT_B | 0.244 [0.206, 0.288] | 2.26 | 0.671 | -0.24 [-0.60, +0.20] | -0.10 |
| Codex | gpt-5.3-codex|P4_CHECKLIST | 0.265 [0.223, 0.311] | 2.29 | 0.681 | -0.34 [-0.57, +0.00] | -0.30 |
| Codex | gpt-5.3-codex|P1_BASELINE | 0.251 [0.211, 0.296] | 2.22 | 0.662 | -0.21 [-0.46, +0.11] | -0.07 |
| Codex | gpt-5.3-codex|BAD_STRINGY | 0.286 [0.237, 0.341] | 2.27 | 0.676 | -0.47 [-0.71, -0.07] | -0.41 |
| Codex | gpt-4o-mini|P8_STRICT_B | 0.206 [0.175, 0.241] | 1.96 | 0.559 | -0.33 [-0.55, -0.04] | -0.37 |
| Codex | gpt-4o-mini|P4_CHECKLIST | 0.199 [0.170, 0.231] | 2.00 | 0.575 | -0.03 [-0.32, +0.26] | -0.07 |
| Codex | editdist_e1 | 0.437 [0.373, 0.505] | 2.99 | 0.823 | -0.56 [-0.81, -0.11] | -0.47 |
| Codex | random_r1 | 0.236 [0.208, 0.269] | 2.43 | 0.659 | +0.18 [-0.06, +0.45] | +0.26 |
| Claude Opus | claude-opus-4-7|P8_STRICT_B | 0.271 [0.229, 0.319] | 2.30 | 0.689 | -0.21 [-0.51, +0.11] | -0.24 |
| Claude Opus | claude-opus-4-7|P4_CHECKLIST | 0.252 [0.211, 0.303] | 2.24 | 0.668 | -0.29 [-0.58, +0.08] | -0.30 |
| Claude Opus | claude-opus-4-7|P1_BASELINE | 0.206 [0.183, 0.232] | 2.07 | 0.596 | +0.16 [-0.22, +0.49] | +0.20 |
| Claude Opus | claude-opus-4-7|BAD_STRINGY | 0.277 [0.230, 0.331] | 2.27 | 0.678 | -0.35 [-0.66, +0.06] | -0.33 |
| Claude Opus | gpt-4o-mini|P8_STRICT_B | 0.200 [0.171, 0.232] | 1.98 | 0.566 | -0.21 [-0.42, +0.05] | -0.24 |
| Claude Opus | gpt-4o-mini|P4_CHECKLIST | 0.195 [0.167, 0.227] | 1.94 | 0.553 | -0.21 [-0.44, +0.05] | -0.28 |
| Claude Opus | editdist_e1 | 0.315 [0.269, 0.365] | 2.36 | 0.712 | -0.56 [-0.81, -0.11] | -0.47 |
| Claude Opus | random_r1 | 0.195 [0.174, 0.218] | 1.99 | 0.578 | +0.18 [-0.06, +0.45] | +0.26 |
| Qwen3-Coder | Qwen/Qwen3-Coder-30B-A3B-Instruct|P8_STRICT_B | 0.217 [0.191, 0.248] | 2.11 | 0.618 | -0.35 [-0.59, -0.06] | -0.37 |
| Qwen3-Coder | Qwen/Qwen3-Coder-30B-A3B-Instruct|P4_CHECKLIST | 0.205 [0.174, 0.239] | 2.06 | 0.608 | -0.17 [-0.44, +0.13] | -0.23 |
| Qwen3-Coder | Qwen/Qwen3-Coder-30B-A3B-Instruct|P1_BASELINE | 0.219 [0.190, 0.250] | 2.11 | 0.618 | -0.28 [-0.47, -0.04] | -0.32 |
| Qwen3-Coder | Qwen/Qwen3-Coder-30B-A3B-Instruct|BAD_STRINGY | 0.272 [0.227, 0.323] | 2.28 | 0.682 | -0.25 [-0.58, +0.20] | -0.29 |
| Qwen3-Coder | gpt-4o-mini|P8_STRICT_B | 0.204 [0.175, 0.238] | 2.00 | 0.572 | -0.16 [-0.45, +0.18] | -0.18 |
| Qwen3-Coder | gpt-4o-mini|P4_CHECKLIST | 0.193 [0.166, 0.224] | 1.96 | 0.568 | -0.03 [-0.33, +0.29] | -0.05 |
| Qwen3-Coder | editdist_e1 | 0.315 [0.269, 0.365] | 2.36 | 0.712 | -0.56 [-0.81, -0.11] | -0.47 |
| Qwen3-Coder | random_r1 | 0.195 [0.174, 0.218] | 1.99 | 0.578 | +0.18 [-0.06, +0.45] | +0.26 |

### T2. Calibrated forecasts, leave-one-task-out, mean over the 8 series of each family (H_vb). Negative difference = first is better.

| family | CONST RPS | CE-fit RPS | Pearson-fit RPS | CE-fit minus CONST: series better / significantly better (RPS) | CE-fit minus Pearson-fit: series better (RPS / CE / TVD) |
|---|---|---|---|---|---|
| Codex | 0.1737 | 0.1724 | 0.1722 | 5/8 / 0 | 4 / 5 / 0 of 8 |
| Claude Opus | 0.1737 | 0.1726 | 0.1724 | 7/8 / 0 | 4 / 3 / 0 of 8 |
| Qwen3-Coder | 0.1737 | 0.1725 | 0.1726 | 6/8 / 0 | 5 / 7 / 0 of 8 |
| ALL 24 | 0.1737 | 0.1725 | 0.1724 | 18/24 / 0 | 13 / 15 / 0 of 24 |

### T3. Human side: old and new

| | old (corrected labels) | new (returned so far) |
|---|---|---|
| artifacts / tasks | 59 / 20 | 100 / 25 |
| ratings per artifact | 4.5 | 2.5 (two raters complete: 2.0 on each of the 100) |
| split-half Spearman, Spearman-Brown corrected | 0.70 | 0.77 (from two raters, so a mean of 2) |
| ceiling on judge-human correlation (sqrt) | 0.84 | 0.88 |
| two raters: Spearman [95%], exact, within 1, weighted kappa | n/a | 0.62 [0.43, 0.77], 0.62, 1.00, 0.75 |
| share of ratings at 5 / at 4 or 5 | 0.20 / 0.43 | 0.73 / 0.92 |

### T4. Task-bootstrap interval width of the judge-free edit-distance baseline's Spearman (so it can be compared across old, new and pooled without any judge scores on the new files)

| set | tasks | artifacts | Spearman [95%] | width |
|---|---|---|---|---|
| old only | 20 | 59 | -0.56 [-0.81, -0.11] | 0.70 |
| new only | 25 | 100 | -0.05 [-0.26, +0.19] | 0.46 |
| pooled | 45 | 159 | +0.50 [+0.30, +0.63] | 0.33 |
| pooled, within-set ranks | 45 | 159 | -0.24 [-0.44, -0.02] | 0.43 |

### T5. Learning curve, headline judge series on old H_vb (random k of 20 tasks, 500 draws, 2.5 to 97.5 percentile of Spearman); last row is the task-bootstrap of all tasks

| series | k=4 | k=8 | k=12 | k=16 | all 20 (bootstrap) |
|---|---|---|---|---|---|
| Codex P8_STRICT_B | -0.29 (width 1.44) | -0.22 (width 1.00) | -0.22 (width 0.73) | -0.23 (width 0.45) | -0.24 (width 0.80) |
| Claude Opus P8_STRICT_B | -0.29 (width 1.27) | -0.22 (width 0.84) | -0.20 (width 0.55) | -0.20 (width 0.33) | -0.21 (width 0.62) |
| Qwen3-Coder P8_STRICT_B | -0.34 (width 1.06) | -0.36 (width 0.67) | -0.35 (width 0.47) | -0.35 (width 0.28) | -0.35 (width 0.53) |

### T6. Learning curve of the edit-distance baseline, pooled with within-set ranks (random k of 45 tasks)

| k tasks | 10 | 20 | 30 | 40 |
|---|---|---|---|---|
| median (width) | -0.25 (0.82) | -0.22 (0.47) | -0.25 (0.32) | -0.24 (0.16) |

### T7. Does the Trust Index track alignment? Spearman of TI_var with each alignment over the 8 judge series of a family (H_vb); interval = task-bootstrap, p = exact permutation

| family | alignment | rho [95%] | p |
|---|---|---|---|
| Codex | judge Spearman vs H_vb | -0.33 [-0.67, +0.26] | 0.428 |
| Codex | -mean RPS vs H_vb | -0.57 [-0.57, -0.10] | 0.151 |
| Codex | -mean CE vs H_vb | -0.10 [-0.50, -0.05] | 0.840 |
| Codex | -mean TVD vs H_vb | -0.52 [-0.66, -0.05] | 0.197 |
| Claude Opus | judge Spearman vs H_vb | -0.17 [-0.62, +0.49] | 0.703 |
| Claude Opus | -mean RPS vs H_vb | -0.50 [-0.55, -0.07] | 0.216 |
| Claude Opus | -mean CE vs H_vb | -0.52 [-0.64, -0.10] | 0.197 |
| Claude Opus | -mean TVD vs H_vb | -0.52 [-0.66, -0.05] | 0.197 |
| Qwen3-Coder | judge Spearman vs H_vb | -0.60 [-0.79, +0.19] | 0.132 |
| Qwen3-Coder | -mean RPS vs H_vb | -0.71 [-0.79, -0.29] | 0.058 |
| Qwen3-Coder | -mean CE vs H_vb | -0.71 [-0.83, -0.38] | 0.058 |
| Qwen3-Coder | -mean TVD vs H_vb | -0.74 [-0.83, -0.38] | 0.046 |
