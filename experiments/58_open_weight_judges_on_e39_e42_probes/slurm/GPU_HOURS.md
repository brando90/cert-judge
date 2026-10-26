# GPU-hour estimate (assumptions, not measurements)

9862 generated cells per model (E39 4624 + E42 5238), mean prompt 4800 tokens. Replace the assumed throughput with the smoke job's printed tokens/s (`--decode`, `--prefill` columns) before relying on a total.

| Model | GPUs | Assumed decode tok/s | Assumed prefill tok/s | Mean out tokens | Wall h (1 replica) | GPU-h |
|---|---:|---:|---:|---:|---:|---:|
| qwen3_4b | 1 | 5000 | 30000 | 3500 | 2.4 | 2.4 |
| qwen3_8b | 1 | 3200 | 18000 | 3500 | 3.7 | 3.7 |
| qwen3_14b | 1 | 1900 | 10000 | 3500 | 6.4 | 6.4 |
| qwen3_32b | 2 | 1500 | 9000 | 3500 | 7.9 | 15.7 |
| qwen36_27b | 2 | 1700 | 9500 | 4500 | 8.6 | 17.3 |
| llama31_8b | 1 | 3500 | 18000 | 350 | 1.0 | 1.0 |
| llama33_70b_awq | 2 | 900 | 5500 | 350 | 3.5 | 6.9 |
| gemma3_4b | 1 | 4500 | 28000 | 350 | 0.7 | 0.7 |
| gemma3_12b | 1 | 2300 | 13000 | 350 | 1.4 | 1.4 |
| gemma3_27b | 2 | 1500 | 8000 | 350 | 2.3 | 4.6 |
| olmo3_7b | 1 | 3300 | 19000 | 5000 | 4.8 | 4.8 |
| olmo3_32b | 2 | 1400 | 8500 | 5000 | 11.3 | 22.7 |
| gpt_oss_20b | 1 | 4200 | 16000 | 2500 | 2.5 | 2.5 |

**Total: about 90 GPU-hours** (sum of the rows). With the FarmShare cap of 4 GPUs at once the wall time is about 22 h (0.9 days) if the queue is free; the 13 jobs are independent and resumable, each under 2 days.

Cheapest useful subset (qwen3_4b, qwen3_8b, llama31_8b, gemma3_4b, gemma3_12b, olmo3_7b, gpt_oss_20b, 1 GPU each): about 16 GPU-hours.

Order to run if GPU time is short: smoke, qwen3_4b, qwen3_8b, qwen3_14b, qwen36_27b (the bridge), gemma3_4b, gemma3_12b, llama31_8b, olmo3_7b, gpt_oss_20b, then the 2-GPU 32B/70B models.
