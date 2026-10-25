# Experiment 59 status (live; updated by hand at each check)

Caveat first: the human ratings are 75 Claude 3.7 Sonnet zero-shot items only; there are no ratings of frontier-judge outputs until 2026-11-06, so everything here tests agreement with those ratings and with the saved frontier/open reference judges, not agreement on frontier outputs.

## 2026-10-24 20:30 (no scores read yet)

| Lane | Host / GPU | Model (prompts) | State |
|---|---|---|---|
| A | skampere1 GPU 5 (A100 80 GB) | llama31_8b (9 prompts) | 5 of 9 prompts harvested (D0, H0, H1, R4 done; H2 at 256/521 cells at 20:18) |
| A | same GPU, next | llama33_70b_awq (H2 only; the open reference), q25_14b_awq, q3_30b_a3b_fp8, qwen3_8b, qwen3_14b | queued; waits for the GPU to be empty (< 500 MiB) |
| B | mercury2 GPU 9 (16 GB) | qwen3_4b (9 prompts, thinking) | running; first prompt (D0, 456 cells) took about 40 min, so about 6 h for the model |

Notes: Qwen3 4B did not start at the 40,960-token context on the 16 GB card, so it runs at 28,672 (protocol addendum 2). Lane A was re-queued once to run the 70B reference early (addendum 3). Other GPUs on skampere1-3 and mercury1-2 were not empty (>= 2 GiB used), so nothing else was started. Weights live under /dfs/scratch0/brando9/at1209_hf and are deleted per model (llama31_8b's are still there until its run ends).
