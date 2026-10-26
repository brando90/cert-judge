#!/usr/bin/env python3
"""TLDR: GPU-hour estimate per panel model for experiment 58 (no model call). Prefill + decode time per model from the cell
counts (E39 4624 + E42 5238 generated cells) and measured prompt lengths, under stated throughput and output-length
ASSUMPTIONS (printed in the table); the smoke job prints the real tokens/s, rerun with --decode/--prefill to update.

Usage: estimate_gpu_hours.py [--out slurm/GPU_HOURS.md] [--prompt-tokens 4800]"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / "scripts")]
import e58                                                    # noqa: E402

CELLS = 4624 + 5238
# Assumed per-model aggregate throughput on L40S (batched vLLM, per replica) and mean output tokens per cell.
# decode tok/s and prefill tok/s are for the whole replica (all of its GPUs). Reasoning models' output length is the
# largest uncertainty: mean 3500 tokens (range 1500-8000 in prior Qwen3 judging runs); non-reasoning ~350.
ASSUME = {
    "qwen3_4b": (5000, 30000, 3500), "qwen3_8b": (3200, 18000, 3500), "qwen3_14b": (1900, 10000, 3500),
    "qwen3_32b": (1500, 9000, 3500), "qwen36_27b": (1700, 9500, 4500),
    "llama31_8b": (3500, 18000, 350), "llama33_70b_awq": (900, 5500, 350),
    "gemma3_4b": (4500, 28000, 350), "gemma3_12b": (2300, 13000, 350), "gemma3_27b": (1500, 8000, 350),
    "olmo3_7b": (3300, 19000, 5000), "olmo3_32b": (1400, 8500, 5000), "gpt_oss_20b": (4200, 16000, 2500),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "GPU_HOURS.md")
    ap.add_argument("--prompt-tokens", type=int, default=4800, help="mean prompt tokens per cell (chars/3.3 of the rebuilt prompts)")
    args = ap.parse_args()
    lines = ["# GPU-hour estimate (assumptions, not measurements)", "",
             f"{CELLS} generated cells per model (E39 4624 + E42 5238), mean prompt {args.prompt_tokens} tokens. "
             "Replace the assumed throughput with the smoke job's printed tokens/s (`--decode`, `--prefill` columns) before relying on a total.", "",
             "| Model | GPUs | Assumed decode tok/s | Assumed prefill tok/s | Mean out tokens | Wall h (1 replica) | GPU-h |", "|---|---:|---:|---:|---:|---:|---:|"]
    total_gpu, total_wall = 0.0, 0.0
    for k in e58.MODEL_ORDER:
        dec, pre, out = ASSUME[k]
        wall = (CELLS * out / dec + CELLS * args.prompt_tokens / pre) / 3600
        gpu = wall * e58.MODELS[k]["gpus"]
        total_gpu += gpu
        total_wall += wall
        lines.append(f"| {k} | {e58.MODELS[k]['gpus']} | {dec} | {pre} | {out} | {wall:.1f} | {gpu:.1f} |")
    lines += ["", f"**Total: about {total_gpu:.0f} GPU-hours** (sum of the rows). With the FarmShare cap of 4 GPUs at once the wall time is about "
              f"{total_gpu / 4:.0f} h ({total_gpu / 4 / 24:.1f} days) if the queue is free; the 13 jobs are independent and resumable, each under 2 days.",
              "", "Cheapest useful subset (qwen3_4b, qwen3_8b, llama31_8b, gemma3_4b, gemma3_12b, olmo3_7b, gpt_oss_20b, 1 GPU each): "
              f"about {sum(CELLS * ASSUME[k][2] / ASSUME[k][0] / 3600 + CELLS * args.prompt_tokens / ASSUME[k][1] / 3600 for k in ('qwen3_4b', 'qwen3_8b', 'llama31_8b', 'gemma3_4b', 'gemma3_12b', 'olmo3_7b', 'gpt_oss_20b')):.0f} GPU-hours.",
              "", "Order to run if GPU time is short: smoke, qwen3_4b, qwen3_8b, qwen3_14b, qwen36_27b (the bridge), gemma3_4b, gemma3_12b, llama31_8b, olmo3_7b, gpt_oss_20b, then the 2-GPU 32B/70B models."]
    args.out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
