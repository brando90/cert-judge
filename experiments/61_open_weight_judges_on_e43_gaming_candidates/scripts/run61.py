#!/usr/bin/env python3
"""TLDR: Experiment 61 driver: one open-weight model (vLLM offline, single call, no tools) over the rendered experiment 43 candidate prompts (prompts61.jsonl), 2 repeats each; appends raw rows to <run>/raw/<model>.jsonl (resumable).
Usage: run61.py --model qwen3_4b --prompts PROMPTS61.jsonl --run RUN --weights DIR [--limit-cells N]
Needs register61 (experiments 58-60 code tree), vLLM and free GPUs (CUDA_VISIBLE_DEVICES)."""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import register61  # noqa: E402
e58 = register61.e58
from judge_vllm import chat_ids, make_llm  # noqa: E402

MAX_TOKENS = {"D0": 16384, "H2": 32000, "P1": 16384}      # experiment 43's PROMPTS
REPEATS = 2
CHUNK = 128


def seed_of(model: str, prompt: str, cell: str, k: int) -> int:
    return int(e58.sha(f"61|{model}|{prompt}|{cell}|r{k}".encode())[:8], 16)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=register61.PANEL)
    ap.add_argument("--prompts", type=Path, required=True)
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--weights", type=Path, required=True)
    ap.add_argument("--limit-cells", type=int, default=None)
    a = ap.parse_args()
    from vllm.inputs import TokensPrompt
    m = e58.MODELS[a.model]
    rows = [json.loads(l) for l in a.prompts.read_text().splitlines() if l.strip()]
    rows = [r for r in rows if r["status"] == "render"]
    if a.limit_cells:
        rows = rows[:a.limit_cells]
    raw = a.run / "raw" / f"{a.model}.jsonl"
    raw.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if raw.exists():
        for l in raw.read_text().splitlines():
            if l.strip():
                d = json.loads(l)
                done.add((d["cell"], d["repeat"]))
    llm = make_llm(a.model, a.weights)
    tok = llm.get_tokenizer()
    base = llm.get_default_sampling_params()
    ids, pre = {}, {}
    for r in rows:
        ids[r["cell"]], pre[r["cell"]] = chat_ids(tok, r["system"], r["user"], m.get("chat_kwargs", {}))
    todo, over = [], []
    for r in rows:
        budget = min(MAX_TOKENS[r["prompt"]], m["max_model_len"] - len(ids[r["cell"]]))
        for k in range(1, REPEATS + 1):
            if (r["cell"], k) in done:
                continue
            if budget < e58.MIN_GENERATION_BUDGET:
                over.append({"cell": r["cell"], "repeat": k, "prompt": r["prompt"], "status": "unmeasured_over_context",
                             "n_prompt_tokens": len(ids[r["cell"]]), "budget": budget})
            else:
                todo.append((r, k, budget))
    with open(raw, "a") as fh:
        for o in over:
            fh.write(json.dumps(o) + "\n")
    print(json.dumps({"model": a.model, "cells": len(rows), "to_generate": len(todo), "over_context": len(over),
                      "max_prompt_tokens": max(len(v) for v in ids.values())}), flush=True)
    t0, n_out = time.time(), 0
    for s in range(0, len(todo), CHUNK):
        chunk = todo[s:s + CHUNK]
        params, prompts = [], []
        for r, k, budget in chunk:
            sp = base.clone()
            sp.max_tokens, sp.seed, sp.skip_special_tokens = budget, seed_of(a.model, r["prompt"], r["cell"], k), True
            params.append(sp)
            prompts.append(TokensPrompt(prompt_token_ids=ids[r["cell"]]))
        outs = llm.generate(prompts, params, use_tqdm=False)
        with open(raw, "a") as fh:
            for (r, k, budget), sp, o in zip(chunk, params, outs):
                c = o.outputs[0]
                n_out += len(c.token_ids)
                fh.write(json.dumps({"cell": r["cell"], "repeat": k, "prompt": r["prompt"], "status": "generated",
                                     "text": ("<think>" if pre[r["cell"]] else "") + c.text, "think_prefilled": pre[r["cell"]],
                                     "finish_reason": c.finish_reason, "n_prompt_tokens": len(ids[r["cell"]]),
                                     "n_output_tokens": len(c.token_ids), "budget": budget, "seed": sp.seed}) + "\n")
        print(json.dumps({"generated": min(s + CHUNK, len(todo)), "of": len(todo), "elapsed_s": round(time.time() - t0, 1),
                          "output_tokens": n_out}), flush=True)
    import torch
    import vllm
    meta = {"model": a.model, "repo": m["repo"], "revision": m["revision"], "quantization": m.get("quantization"),
            "thinking": m["thinking"], "max_model_len": m["max_model_len"], "tensor_parallel_size": m["gpus"],
            "vllm": vllm.__version__, "torch": torch.__version__, "python": platform.python_version(),
            "gpu": torch.cuda.get_device_name(0), "host": platform.node(), "harness": "vllm_offline single call, no tools",
            "sampling": {"source": "model generation_config defaults (vLLM get_default_sampling_params)", "temperature": base.temperature,
                         "top_p": base.top_p, "top_k": base.top_k, "min_p": base.min_p, "repetition_penalty": base.repetition_penalty,
                         "max_tokens_rule": "min(prompt max_tokens, max_model_len - prompt tokens)", "repeats": REPEATS,
                         "seed_rule": "int(sha256('61|<model>|<prompt>|<cell>|r<k>')[:8],16)"},
            "cells_generated": len(todo), "output_tokens": n_out, "seconds": round(time.time() - t0, 1),
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"), "finished_utc": e58.stamp()}
    e58.write_json(a.run / f"meta_{a.model}.json", meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
