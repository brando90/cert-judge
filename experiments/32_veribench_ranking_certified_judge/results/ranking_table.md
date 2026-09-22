# Experiment 32 ranking table — judge P1_BASELINE on `gpt-5.6-terra` (effort low), median of 3 repeats (certified-panel rule); mean-of-repeats variant in results/ranking.json analyses['mean__*']

Cells: 826/1680 ok; CLI invocations incl. retries: 846; provider API spend: $0.

Analysis `median_available_repeats__sec_6858_only`: paired items 140 (per split: {'easy_set': 41, 'cs_set': 10, 'real_code': 5, 'humaneval_set': 56, 'security_6858': 22, 'security_python': 6}); repeats present per (item, agent): [1, 2, 3]. 95% percentile bootstrap over items within split, 10000 draws, seed 0.

| Agent | Easy | CS | Real | HE | Sec | **Avg** (95% CI) | ItemMean (95% CI) |
|---|---|---|---|---|---|---|---|
| Baseline | 0.077 | 0.040 | 0.125 | 0.067 | 0.053 | **0.072** [0.050, 0.097] | 0.065 [0.053, 0.078] |
| DSPy ReAct | 0.184 | 0.065 | 0.450 | 0.119 | 0.072 | **0.178** [0.118, 0.241] | 0.136 [0.110, 0.165] |
| Trace+ | 0.083 | 0.075 | 0.220 | 0.127 | 0.094 | **0.120** [0.081, 0.163] | 0.105 [0.088, 0.123] |
| Trace++ | 0.145 | 0.060 | 0.190 | 0.118 | 0.081 | **0.119** [0.082, 0.159] | 0.114 [0.093, 0.137] |

Per-split 95% CIs:

| Agent | Easy | CS | Real | HE | Sec |
|---|---|---|---|---|---|
| Baseline | [0.057, 0.098] | [0.015, 0.070] | [0.020, 0.235] | [0.045, 0.091] | [0.030, 0.081] |
| DSPy ReAct | [0.120, 0.260] | [0.030, 0.100] | [0.180, 0.740] | [0.093, 0.147] | [0.020, 0.149] |
| Trace+ | [0.050, 0.122] | [0.040, 0.115] | [0.050, 0.410] | [0.107, 0.146] | [0.043, 0.159] |
| Trace++ | [0.102, 0.195] | [0.025, 0.100] | [0.040, 0.350] | [0.095, 0.146] | [0.022, 0.175] |

Ordering by Avg: DSPy ReAct > Trace+ > Trace++ > Baseline; Claude 3.7 table: DSPy ReAct > Trace++ > Trace+ > Baseline; identical: False; Spearman over the four Avg values: 0.800; Spearman over the 20 split cells: -0.054.

Bootstrap frequency of each full Avg ordering:

- DSPy ReAct > Trace++ > Trace+ > Baseline: 0.427
- DSPy ReAct > Trace+ > Trace++ > Baseline: 0.416
- Trace+ > Trace++ > DSPy ReAct > Baseline: 0.039
- Trace+ > DSPy ReAct > Trace++ > Baseline: 0.037
- DSPy ReAct > Trace+ > Baseline > Trace++: 0.034
- Trace++ > Trace+ > DSPy ReAct > Baseline: 0.022

Pairwise Avg differences (point, 95% CI, two-sided bootstrap p):

- baseline-dspy_react: -0.105 [-0.179, -0.038], p=0.000
- baseline-trace_plus: -0.047 [-0.099, -0.008], p=0.008
- baseline-trace_plusplus: -0.046 [-0.098, +0.004], p=0.071
- dspy_react-trace_plus: +0.058 [-0.026, +0.147], p=0.197
- dspy_react-trace_plusplus: +0.059 [-0.020, +0.146], p=0.162
- trace_plus-trace_plusplus: +0.001 [-0.035, +0.035], p=0.943
