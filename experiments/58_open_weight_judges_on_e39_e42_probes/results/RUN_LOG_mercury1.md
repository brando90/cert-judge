# E58 run log: mercury1 (Stanford CS, no Slurm), 10-26-2026

**TLDR:** the E58 pipeline is installed and smoke-tested on mercury1's A4000s with a different serving stack than the FarmShare plan. No judge cell has been generated for the analysis yet. Protocol, prompts, sampling and analysis are unchanged; only hardware and serving stack differ, and both are written into every `*.meta.json` (`hardware_note`).

| Item | Value |
|---|---|
| Host | mercury1.stanford.edu (via whale), `/lfs/mercury1/0/brando9/e58` |
| GPUs | RTX A4000 16 GB; only GPUs with < 500 MiB in use (the launcher checks; others' jobs are never touched) |
| Driver / CUDA | 570.133.20 / 12.8 |
| Serving stack | vLLM 0.11.0, torch 2.8.0+cu128, transformers 4.57.6, Python 3.12.11 (uv venv) |
| FarmShare stack it replaces | vLLM 0.32.0, torch 2.13.0+cu130, transformers 5.19.0 (torch 2.13 has no cu128 build, so it cannot run on driver 570) |
| Package | `e58_pkg.tgz` sha256 889c8af991634499907e0f97f8f89eceee0341490fa7a6b75805e20f9cefb574 (PR 78 package) |
| Code change | `judge_vllm.py` only: env `E58_TP` overrides the tensor-parallel size, env `E58_HW_NOTE` is recorded in the meta. No prompt, sampling, seed, max_model_len, gpu_memory_utilization or panel change. |
| Weights | `qwen3_4b` (bf16, 8.1 GB) and `gemma3_4b` (bf16, 8.6 GB) at the revisions pinned in `e58.MODELS`, via `fetch_models.py` |
| Quantization | none (bf16) |
| Thinking mode | as in `e58.MODELS` (`thinking: True` for Qwen3 and OLMo 3; none for Gemma 3 and Llama) |
| Harness | `vllm_offline`, `judge_vllm.py`, one process per model, seeds per PROTOCOL section 4 |

## Smoke (12:35 PT)

`gemma3_4b`, E39, prompt D0, `--limit-cells 20`, 1x A4000 (GPU 9), TP=1: 20 cells in 23.2 s, 2,721 output tokens; measured 19, parse_error 1 (plus the deterministic and extraction cells copied from E39). Works.

`qwen3_4b`, TP=2 on GPUs 2+9, failed at engine start because another user's process had taken GPU 2 (1.9 GB in use; vLLM at 0.90 utilisation needs the card empty). `qwen3_4b` on one A4000 cannot hold the 40,960-token KV cache at 0.90 utilisation (about 4.7 GB free after weights vs about 6 GB needed), so it needs two empty A4000s.

## What fits

One empty A4000: `gemma3_4b`. Two empty A4000s (TP=2): `qwen3_4b`, `qwen3_8b`, `llama31_8b`, `olmo3_7b`, `gemma3_12b`. Not on A4000: the 2-GPU L40S models (Qwen3-32B, Qwen3.6-27B, Gemma 3 27B, OLMo 3 32B, Llama 3.3 70B AWQ), `qwen3_14b` and `gpt_oss_20b` (stay on FarmShare or Sherlock).

## Launch

`~/e58_run_e58_mercury1.sh <model> <cuda ids> <tp>` refuses to start unless every named GPU has < 500 MiB in use, runs E39 then E42, and is resumable. Results land in `/lfs/mercury1/0/brando9/e58/runs/main`, the layout `collect.sh` and `analyze58.py` read.

## Launches (10-26-2026, AT-1384)

Launch method that worked: `ssh_run` to skampere1, then `ssh mercury1 '(nohup setsid bash <script> > log 2>&1 < /dev/null &)'` (same as AT-979). A background process loses its Kerberos ticket when the ssh session ends, so anything that needs AFS or a hop to another node must finish inside the session; scripts and weights a run needs are on local disk. `/dfs/scratch0` stalls on many small files and is 100% full, so it is not used.

| Judge | Host / GPUs | Started (PT) | Stack and settings | Status |
|---|---|---|---|---|
| gemma3_4b | mercury1, GPU 9 (1x A4000), TP=1 | 12:47 | vLLM 0.11.0, torch 2.8.0+cu128, transformers 4.57.6, bf16, no quantization, no thinking mode (Gemma 3), `judge_vllm.py` `vllm_offline`, E39 then E42, resumable | Running. Measured about 16 cells/min on one shared A4000 (E39 D0, 456 cells, then R4 256 of 521 in 16 min), so the 9,862 generated cells need about 10 h; expected finish about 23:00 PT (an estimate). |
| gemma3_12b | mercury2, 2 empty A4000s picked at launch, TP=2 | waits for 2 empty GPUs | same stack (mercury2 venv128: vLLM 0.11.0, torch 2.8.0+cu128, transformers 4.57.6), bf16, weights in /dev/shm/brando9_e58_models, code in /tmp/brando9_e58 | A waiter polls every 60 s and launches when 2 GPUs have < 500 MiB in use. |
| olmo3_7b | mercury2, 2 empty A4000s picked at launch, TP=2 | waits for 2 empty GPUs | same, thinking mode as in `e58.MODELS` | Same waiter. |

Not run here: `qwen3_4b` (already COMPLETED on FarmShare, job 1862860_0), `gpt_oss_20b` and the 32B/27B/70B judges (do not fit A4000 16 GB; they stay on FarmShare). Every raw cell's meta records `hardware_note`, so a mixed-hardware panel is visible to the analysis. Protocol, prompts, sampling, seeds and analysis are unchanged.
