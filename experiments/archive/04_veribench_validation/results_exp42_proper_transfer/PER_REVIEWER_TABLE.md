# EXP42 Per-Reviewer Judge–Human Alignment (Test Tasks)

Global isotonic calibration, fit on train tasks, applied to test tasks.  
Best prompt per model selected on train raw ρ (primary target = zscore_mean).

Each reviewer shown separately; 'Agg' = zscore_mean of all five.

| Model | P1 Train ρ | P1 Test ρ | P2 Train ρ | P2 Test ρ | P3 Train ρ | P3 Test ρ | P4 Train ρ | P4 Test ρ | P5 Train ρ | P5 Test ρ | Agg Test ρ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LeanStral | 0.578 | -0.234 | 0.538 | -0.152 | -0.362 | — | 0.472 | -0.030 | 0.083 | -0.271 | -0.084 |
| GPT-4o-mini | 0.270 | 0.027 | 0.366 | 0.035 | — | — | 0.287 | 0.499 | 0.257 | 0.097 | 0.295 |
| GPT-5.3 Codex | 0.238 | -0.573 | 0.089 | -0.564 | 0.191 | -0.380 | 0.053 | -0.165 | 0.048 | -0.318 | -0.460 |
| Claude Opus 4.7 | -0.086 | -0.014 | -0.116 | -0.025 | -0.362 | 0.553 | 0.165 | -0.070 | 0.318 | -0.143 | -0.108 |
| Qwen | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

**✓** = ρ ≥ 0.70.
