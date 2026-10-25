# Experiment 59 status (live; updated by hand at each check)

Caveat first: the human ratings are 75 Claude 3.7 Sonnet zero-shot items only; there are no ratings of frontier-judge outputs until 2026-11-06, so everything here tests agreement with those ratings and with the saved frontier/open reference judges, not agreement on frontier outputs.

## 2026-10-24 21:00 (first look, Part 1 only)

| Lane | Host / GPU | Model (prompts) | State |
|---|---|---|---|
| A | skampere1 GPU 5 (A100 80 GB) | llama31_8b (9 prompts) | done 20:26, 9 of 9 harvested |
| A | same GPU | llama33_70b_awq (H2 only; the open reference) | running since 20:49 (521 cells) |
| A | same GPU, next | q25_14b_awq, q3_30b_a3b_fp8, qwen3_8b, qwen3_14b | queued; each waits for the GPU to be empty (< 500 MiB) |
| B | mercury2 GPU 9 (16 GB) | qwen3_4b (9 prompts, thinking) | running; D0 done, R4 under way at 20:50 (about 40 min per prompt, so about 6 h for the model) |

Notes: Qwen3 4B did not start at the 40,960-token context on the 16 GB card, so it runs at 28,672 (protocol addendum 2). Lane A was re-queued once to run the 70B reference early (addendum 3). Other GPUs on skampere1-3 and mercury1-2 were not empty (>= 2 GiB used), so nothing else was started. Weights live under /dfs/scratch0/brando9/at1209_hf and are deleted per model (llama31_8b's are still there until its run ends).

### First look (Part 1 only, no learner fitted, test split not read; `results/interim_2026-10-24_2105_part1_only/`)

Units: the 9 Llama 3.1 8B prompts (new) plus the 9 saved Qwen3.6-27B units (hosted open-weight, E39), so 18 units from 2 models. Criterion = Spearman of the unit's median-of-3 item score with the three-expert mean over the 45 val+test items (human ratings are Claude 3.7 Sonnet outputs only). Intervals are unit-bootstrap and the model-clustered test is not computable with 2 models, so every verdict here is INCONCLUSIVE by design, not a result.

- Llama 3.1 8B units agree poorly with the experts (criterion rho from -0.30 to 0.44; D0 0.44, H2 0.08); Qwen3.6-27B units are mostly high (H1 0.86, R4 0.83, H0 0.83, H2 0.82, D0 0.73; LEX -0.29).
- Over the 18 units: `F2_item` (agreement with the frontier consensus on the 75 items) 0.971 [0.89, 0.99]; `F1_probe` 0.709 [0.31, 0.88]; frozen `C_ms_gold` 0.664 [0.16, 0.91] (n=15 computable); `TI_var_trainnorm` -0.063. The frozen `C_ms_gold` is high mainly because the two models differ, not within a model: over the 8 computable Llama units alone it is 0.357 and `F1_probe` 0.000, while `F2_item` is 0.933 (n=9).
- Open-reference arm (reference = Qwen3.6-27B, subjects = the 9 Llama units): `F2_item@O_qwen36` 0.950 [0.72, 1.00], `F1_probe@O_qwen36` -0.133. The 70B reference is still running; `O_llama70` and `O_both` appear after it lands.

Read this as a plumbing check and a direction, not as evidence: two models, nine small-model units, one pass.
