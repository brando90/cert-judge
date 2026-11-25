### B1a. Proper scores per set: judge vs the constant forecaster (lower is better; 95% task-bootstrap)

| Judge | Set | RPS | const RPS | RPS minus const | CE | const CE | TVD | const TVD |
|---|---|---|---|---|---|---|---|---|
| Codex | old (59 files, 20 tasks) | 0.244 [0.206, 0.288] | 0.174 | 0.070 [0.026, 0.114] | 2.260 [2.161, 2.356] | 1.767 | 0.671 [0.618, 0.724] | 0.486 |
| Codex | new (100 files, 25 tasks) | 0.243 [0.205, 0.283] | 0.070 | 0.173 [0.116, 0.226] | 2.054 [1.915, 2.186] | 0.872 | 0.749 [0.698, 0.797] | 0.364 |
| Codex | pooled (159 files, 45 tasks) | 0.243 [0.215, 0.276] | 0.108 | 0.135 [0.096, 0.177] | 2.130 [2.030, 2.228] | 1.204 | 0.720 [0.682, 0.760] | 0.409 |
| Claude Opus | old (59 files, 20 tasks) | 0.271 [0.229, 0.319] | 0.174 | 0.097 [0.048, 0.148] | 2.301 [2.185, 2.409] | 1.767 | 0.689 [0.626, 0.751] | 0.486 |
| Claude Opus | new (100 files, 25 tasks) | 0.217 [0.175, 0.261] | 0.070 | 0.147 [0.095, 0.198] | 1.838 [1.643, 2.032] | 0.872 | 0.691 [0.628, 0.747] | 0.364 |
| Claude Opus | pooled (159 files, 45 tasks) | 0.237 [0.206, 0.271] | 0.108 | 0.129 [0.091, 0.170] | 2.010 [1.858, 2.149] | 1.204 | 0.690 [0.646, 0.733] | 0.409 |
| Qwen3-Coder | old (59 files, 20 tasks) | 0.217 [0.191, 0.248] | 0.174 | 0.044 [0.026, 0.061] | 2.106 [1.996, 2.221] | 1.767 | 0.618 [0.561, 0.678] | 0.486 |
| Qwen3-Coder | new (100 files, 25 tasks) | 0.126 [0.112, 0.142] | 0.070 | 0.057 [0.025, 0.085] | 1.390 [1.194, 1.600] | 0.872 | 0.562 [0.512, 0.618] | 0.364 |
| Qwen3-Coder | pooled (159 files, 45 tasks) | 0.160 [0.142, 0.179] | 0.108 | 0.052 [0.031, 0.072] | 1.655 [1.494, 1.811] | 1.204 | 0.583 [0.543, 0.623] | 0.409 |

### B1b. Secondary: correlations

| Judge | Set | Spearman | Pearson | Spearman width | RPS width |
|---|---|---|---|---|---|
| Codex | old (59 files, 20 tasks) | -0.24 [-0.60, 0.20] | -0.10 [-0.47, 0.28] | 0.80 | 0.082 |
| Codex | new (100 files, 25 tasks) | 0.24 [-0.01, 0.47] | 0.31 [0.05, 0.54] | 0.49 | 0.078 |
| Codex | pooled (159 files, 45 tasks) | 0.05 [-0.19, 0.29] | 0.16 [-0.06, 0.38] | 0.48 | 0.061 |
| Claude Opus | old (59 files, 20 tasks) | -0.21 [-0.51, 0.11] | -0.24 [-0.51, 0.07] | 0.62 | 0.090 |
| Claude Opus | new (100 files, 25 tasks) | 0.17 [-0.07, 0.39] | 0.36 [0.15, 0.55] | 0.46 | 0.086 |
| Claude Opus | pooled (159 files, 45 tasks) | 0.03 [-0.17, 0.21] | 0.14 [-0.09, 0.34] | 0.38 | 0.065 |
| Qwen3-Coder | old (59 files, 20 tasks) | -0.35 [-0.59, -0.06] | -0.37 [-0.61, -0.05] | 0.53 | 0.057 |
| Qwen3-Coder | new (100 files, 25 tasks) | 0.23 [0.00, 0.45] | 0.28 [0.06, 0.49] | 0.45 | 0.031 |
| Qwen3-Coder | pooled (159 files, 45 tasks) | 0.02 [-0.19, 0.24] | 0.04 [-0.21, 0.27] | 0.43 | 0.037 |

### B3. Calibrated forecasters, leave-one-task-out (difference, negative = first is better; 95% task-bootstrap)

| Judge | Set | Comparison | dRPS | dCE | dTVD |
|---|---|---|---|---|---|
| Codex | new | CE-fit minus CONST | -0.0002 [-0.0045, 0.0045] | -0.003 [-0.041, 0.040] | -0.002 [-0.023, 0.023] |
| Codex | new | CE-fit minus Pearson-fit | -0.0077 [-0.0172, 0.0031] | -0.144 [-0.276, -0.001] | -0.058 [-0.108, -0.002] |
| Codex | new | Pearson-fit minus CONST | 0.0075 [-0.0059, 0.0202] | 0.141 [-0.010, 0.285] | 0.057 [-0.007, 0.118] |
| Codex | pooled | CE-fit minus CONST | 0.0009 [-0.0023, 0.0045] | 0.004 [-0.021, 0.033] | 0.000 [-0.014, 0.017] |
| Codex | pooled | CE-fit minus Pearson-fit | -0.0050 [-0.0116, 0.0014] | -0.092 [-0.179, -0.009] | -0.036 [-0.071, -0.000] |
| Codex | pooled | Pearson-fit minus CONST | 0.0060 [-0.0025, 0.0154] | 0.096 [0.006, 0.195] | 0.036 [-0.004, 0.079] |
| Claude Opus | new | CE-fit minus CONST | -0.0017 [-0.0069, 0.0040] | -0.015 [-0.058, 0.034] | 0.000 [-0.024, 0.028] |
| Claude Opus | new | CE-fit minus Pearson-fit | -0.0077 [-0.0167, 0.0023] | -0.148 [-0.282, -0.008] | -0.048 [-0.100, 0.011] |
| Claude Opus | new | Pearson-fit minus CONST | 0.0061 [-0.0080, 0.0195] | 0.133 [-0.031, 0.286] | 0.048 [-0.016, 0.110] |
| Claude Opus | pooled | CE-fit minus CONST | -0.0013 [-0.0049, 0.0025] | -0.010 [-0.040, 0.022] | -0.000 [-0.016, 0.018] |
| Claude Opus | pooled | CE-fit minus Pearson-fit | -0.0050 [-0.0115, 0.0013] | -0.095 [-0.185, -0.009] | -0.028 [-0.064, 0.008] |
| Claude Opus | pooled | Pearson-fit minus CONST | 0.0036 [-0.0051, 0.0133] | 0.084 [-0.016, 0.194] | 0.028 [-0.014, 0.072] |
| Qwen3-Coder | new | CE-fit minus CONST | -0.0009 [-0.0039, 0.0021] | -0.010 [-0.039, 0.019] | -0.007 [-0.020, 0.007] |
| Qwen3-Coder | new | CE-fit minus Pearson-fit | -0.0073 [-0.0164, 0.0029] | -0.140 [-0.269, 0.002] | -0.052 [-0.104, 0.005] |
| Qwen3-Coder | new | Pearson-fit minus CONST | 0.0064 [-0.0052, 0.0172] | 0.131 [-0.013, 0.253] | 0.045 [-0.014, 0.100] |
| Qwen3-Coder | pooled | CE-fit minus CONST | -0.0024 [-0.0065, 0.0013] | -0.014 [-0.040, 0.011] | -0.006 [-0.015, 0.005] |
| Qwen3-Coder | pooled | CE-fit minus Pearson-fit | -0.0045 [-0.0109, 0.0017] | -0.090 [-0.175, -0.004] | -0.030 [-0.066, 0.006] |
| Qwen3-Coder | pooled | Pearson-fit minus CONST | 0.0022 [-0.0058, 0.0106] | 0.075 [-0.013, 0.165] | 0.025 [-0.014, 0.065] |

Levels (RPS / CE / TVD):

| Judge | Set | CONST | CE-fit | Pearson-fit |
|---|---|---|---|---|
| Codex | new | 0.0698 / 0.872 / 0.364 | 0.0696 / 0.868 / 0.362 | 0.0773 / 1.012 / 0.420 |
| Codex | pooled | 0.1084 / 1.204 / 0.409 | 0.1093 / 1.208 / 0.409 | 0.1144 / 1.300 / 0.445 |
| Claude Opus | new | 0.0698 / 0.872 / 0.364 | 0.0681 / 0.856 / 0.364 | 0.0759 / 1.005 / 0.412 |
| Claude Opus | pooled | 0.1084 / 1.204 / 0.409 | 0.1070 / 1.193 / 0.409 | 0.1120 / 1.288 / 0.437 |
| Qwen3-Coder | new | 0.0698 / 0.872 / 0.364 | 0.0689 / 0.862 / 0.357 | 0.0762 / 1.002 / 0.409 |
| Qwen3-Coder | pooled | 0.1084 / 1.204 / 0.409 | 0.1060 / 1.189 / 0.403 | 0.1105 / 1.279 / 0.434 |

### B4. Learning curves over random k tasks (median over draws)

| Judge | Set | k tasks | Spearman median | Spearman width | dRPS median | dRPS width |
|---|---|---|---|---|---|---|
| Codex | new | 5 | 0.22 | 1.08 | 0.172 | 0.239 |
| Codex | new | 10 | 0.23 | 0.67 | 0.172 | 0.134 |
| Codex | new | 15 | 0.24 | 0.42 | 0.170 | 0.096 |
| Codex | new | 20 | 0.23 | 0.26 | 0.175 | 0.056 |
| Codex | new | 25 | 0.24 | nan | 0.173 | nan |
| Codex | pooled | 10 | 0.06 | 0.87 | 0.133 | 0.159 |
| Codex | pooled | 20 | 0.05 | 0.55 | 0.134 | 0.095 |
| Codex | pooled | 30 | 0.05 | 0.35 | 0.134 | 0.061 |
| Codex | pooled | 40 | 0.05 | 0.18 | 0.136 | 0.029 |
| Codex | pooled | 45 | 0.05 | nan | 0.135 | nan |
| Claude Opus | new | 5 | 0.16 | 0.98 | 0.146 | 0.220 |
| Claude Opus | new | 10 | 0.17 | 0.60 | 0.146 | 0.130 |
| Claude Opus | new | 15 | 0.17 | 0.40 | 0.148 | 0.093 |
| Claude Opus | new | 20 | 0.17 | 0.24 | 0.148 | 0.057 |
| Claude Opus | new | 25 | 0.17 | nan | 0.147 | nan |
| Claude Opus | pooled | 10 | 0.02 | 0.74 | 0.127 | 0.147 |
| Claude Opus | pooled | 20 | 0.02 | 0.46 | 0.127 | 0.088 |
| Claude Opus | pooled | 30 | 0.03 | 0.29 | 0.129 | 0.058 |
| Claude Opus | pooled | 40 | 0.03 | 0.14 | 0.130 | 0.027 |
| Claude Opus | pooled | 45 | 0.03 | nan | 0.129 | nan |
| Qwen3-Coder | new | 5 | 0.20 | 0.89 | 0.059 | 0.124 |
| Qwen3-Coder | new | 10 | 0.22 | 0.59 | 0.057 | 0.074 |
| Qwen3-Coder | new | 15 | 0.23 | 0.38 | 0.056 | 0.050 |
| Qwen3-Coder | new | 20 | 0.23 | 0.23 | 0.057 | 0.031 |
| Qwen3-Coder | new | 25 | 0.23 | nan | 0.057 | nan |
| Qwen3-Coder | pooled | 10 | 0.05 | 0.87 | 0.050 | 0.075 |
| Qwen3-Coder | pooled | 20 | 0.03 | 0.46 | 0.052 | 0.045 |
| Qwen3-Coder | pooled | 30 | 0.03 | 0.33 | 0.051 | 0.032 |
| Qwen3-Coder | pooled | 40 | 0.02 | 0.17 | 0.052 | 0.014 |
| Qwen3-Coder | pooled | 45 | 0.02 | nan | 0.052 | nan |
