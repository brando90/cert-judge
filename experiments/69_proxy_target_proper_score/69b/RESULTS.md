# Experiment 69B — Measured Native 6-Class Forecast Results (2026-11-27)

Evaluated on the frozen 2026-11-26 TTJ Exp 09 human rating snapshot (`100` files, `25` tasks, `250` ratings; `185/250 = 74%` score 5; LOTO constant-forecast RPS `0.0698`).

All 5 models scored all 100 files as native 6-class probability distributions (one digit token, `temperature=0`, digit logprobs; no Gemini/Antigravity). API runs used Stanford Koyejo Lab OpenAI key (`openai_bm_key_koyejolab.txt`) under Brando's $100 cap (estimated worst-case upper bound ~$47 across all 4 API models; SNAP `Qwen/Qwen3-8B` was $0).

| Judge | Model | Source | RPS (↓) | vs. CONST RPS [95% CI] | Beats CONST? | vs. CONST CE | vs. CONST TVD | Spearman | Pearson |
|---|---|---|---:|---:|:---:|---:|---:|---:|---:|
| `api_gpt_4_1` | `gpt-4.1` | OpenAI | **0.1379** | +0.0681 [+0.0331, +0.1146] | No | +4.68 | +0.101 | +0.013 | +0.054 |
| `api_gpt_4_1_mini` | `gpt-4.1-mini` | OpenAI | 0.1718 | +0.1020 [+0.0711, +0.1321] | No | +5.08 | +0.302 | −0.030 | +0.041 |
| `snap_qwen3_8b` | `Qwen/Qwen3-8B` | SNAP vLLM ($0) | 0.2732 | +0.2034 [+0.1511, +0.2554] | No | +4.03 | +0.491 | +0.0005 | −0.055 |
| `api_gpt_5_4_mini` | `gpt-5.4-mini` | OpenAI | 0.3093 | +0.2395 [+0.1709, +0.3158] | No | +12.16 | +0.467 | −0.033 | +0.124 |
| `api_gpt_5_4` | `gpt-5.4` | OpenAI | 0.3819 | +0.3121 [+0.2373, +0.3846] | No | +23.73 | +0.538 | **+0.036** | **+0.125** |

**Key takeaway:** 0/5 raw native 6-class judges beat the constant forecast (`0.0698`) on RPS. Notably, `gpt-5.4` has the **highest Pearson (+0.125) and Spearman (+0.036)** of all 5 models, yet the **worst raw RPS (0.3819) and CE (+23.73 vs CONST)**—a clean empirical example of why correlation cannot replace strictly proper scoring rules.

See `results/eval_69b_all_measured.json` and per-model JSON/JSONL files in `results/`.
