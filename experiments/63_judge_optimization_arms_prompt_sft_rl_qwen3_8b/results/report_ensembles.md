| arm | seeds | ensemble (mean EV) Spearman [CI] | ensemble Pearson [CI] | mean per-prompt SD of EV across seeds (all 102 test prompts) | per-seed Spearman: min..max | per-seed Spearman lower CI > 0.60 |
|---|---|---|---|---|---|---|
| prompt_opt | 2 | -0.18 [-0.60, 0.47] | -0.59 [-0.81, 0.41] | 0.027 | -0.21..-0.13 | 0/2 |
| sft | 3 | 0.78 [0.44, 0.90] | 0.79 [0.50, 0.93] | 0.046 | 0.65..0.89 | 1/3 |
| sft_humanmix | 2 | 0.82 [0.41, 0.96] | 0.88 [0.54, 0.96] | 0.051 | 0.81..0.85 | 0/2 |
| rl | 3 | 0.56 [0.31, 0.76] | 0.58 [0.38, 0.77] | 0.073 | 0.51..0.59 | 0/3 |

Reference: EV spread over test prompts (SD of EV across the 102 prompts): base 0.235
- prompt_opt: SD of EV across prompts (seed 0) 0.251
- sft: SD of EV across prompts (seed 0) 0.335
- sft_humanmix: SD of EV across prompts (seed 0) 0.293
- rl: SD of EV across prompts (seed 0) 0.271
