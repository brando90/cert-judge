# Experiment 32 ranking table — judge P1_BASELINE on `gpt-5.6-terra` (effort low), median of 3 repeats (certified-panel rule); mean-of-repeats variant in results/ranking.json analyses['mean__*']

Cells: 591/1680 ok; CLI invocations incl. retries: 611; provider API spend: $0.

Analysis `median_available_repeats__sec_6858_only`: paired items 140 (per split: {'easy_set': 41, 'cs_set': 10, 'real_code': 5, 'humaneval_set': 56, 'security_6858': 22, 'security_python': 6}); repeats present per (item, agent): [1, 2, 3]. 95% percentile bootstrap over items within split, 10000 draws, seed 0.

| Agent | Easy | CS | Real | HE | Sec | **Avg** (95% CI) | ItemMean (95% CI) |
|---|---|---|---|---|---|---|---|
| Baseline | 0.076 | 0.050 | 0.140 | 0.071 | 0.043 | **0.076** [0.050, 0.106] | 0.066 [0.053, 0.080] |
| DSPy ReAct | 0.189 | 0.060 | 0.450 | 0.112 | 0.080 | **0.178** [0.119, 0.240] | 0.136 [0.110, 0.166] |
| Trace+ | 0.078 | 0.070 | 0.220 | 0.135 | 0.091 | **0.119** [0.080, 0.162] | 0.106 [0.089, 0.124] |
| Trace++ | 0.123 | 0.060 | 0.180 | 0.112 | 0.084 | **0.112** [0.077, 0.149] | 0.105 [0.083, 0.130] |

Per-split 95% CIs:

| Agent | Easy | CS | Real | HE | Sec |
|---|---|---|---|---|---|
| Baseline | [0.055, 0.098] | [0.020, 0.080] | [0.020, 0.280] | [0.047, 0.096] | [0.018, 0.073] |
| DSPy ReAct | [0.123, 0.267] | [0.030, 0.090] | [0.180, 0.750] | [0.084, 0.141] | [0.023, 0.159] |
| Trace+ | [0.050, 0.107] | [0.030, 0.110] | [0.050, 0.410] | [0.113, 0.158] | [0.036, 0.157] |
| Trace++ | [0.082, 0.172] | [0.020, 0.100] | [0.040, 0.320] | [0.083, 0.145] | [0.023, 0.180] |

Ordering by Avg: DSPy ReAct > Trace+ > Trace++ > Baseline; Claude 3.7 table: DSPy ReAct > Trace++ > Trace+ > Baseline; identical: False; Spearman over the four Avg values: 0.800; Spearman over the 20 split cells: -0.067.

Bootstrap frequency of each full Avg ordering:

- DSPy ReAct > Trace+ > Trace++ > Baseline: 0.479
- DSPy ReAct > Trace++ > Trace+ > Baseline: 0.325
- DSPy ReAct > Trace+ > Baseline > Trace++: 0.080
- Trace+ > DSPy ReAct > Trace++ > Baseline: 0.048
- Trace+ > Trace++ > DSPy ReAct > Baseline: 0.029
- DSPy ReAct > Baseline > Trace+ > Trace++: 0.011

Pairwise Avg differences (point, 95% CI, two-sided bootstrap p):

- baseline-dspy_react: -0.102 [-0.177, -0.034], p=0.000
- baseline-trace_plus: -0.043 [-0.097, -0.001], p=0.040
- baseline-trace_plusplus: -0.036 [-0.087, +0.017], p=0.190
- dspy_react-trace_plus: +0.059 [-0.022, +0.146], p=0.175
- dspy_react-trace_plusplus: +0.066 [-0.008, +0.149], p=0.089
- trace_plus-trace_plusplus: +0.007 [-0.031, +0.042], p=0.701
