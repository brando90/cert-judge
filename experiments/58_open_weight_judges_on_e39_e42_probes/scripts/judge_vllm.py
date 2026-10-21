#!/usr/bin/env python3
"""TLDR: Experiment 58's local judge driver. Loads one open-weight model with vLLM offline (no server, no network),
sends every rendered cell of experiment 39 (or 42) for each of the nine prompt configurations through the model's own
chat template, appends the raw outputs to <run>/raw/<exp>/<model>/<prompt>.jsonl in resumable chunks, and writes the
harvest in experiment 39's schema after each configuration (harvest_lib). Cells whose prompt leaves fewer than
MIN_GENERATION_BUDGET new tokens are unmeasured_over_context, never truncated.

Usage: judge_vllm.py --model qwen3_4b --exp e39 --run ~/e58/runs/main --weights ~/e58/models/qwen3_4b
                     [--prompts all] [--limit-cells N] [--dry-run]"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e58                                                    # noqa: E402
import harvest_lib as H                                       # noqa: E402


def cell_seed(config: str, cell: str) -> int:
    """Per-cell sampling seed: the three repeats of one probe are three independent samples, reproducibly."""
    return int(e58.sha(f"{e58.SEED}|{config}|{cell}".encode())[:8], 16)


def load_prompts(exp: str, prompt_key: str) -> list[dict]:
    """The rebuilt, hash-verified prompt rows. A row whose text does not hash to its frozen prompt_sha256 stops the
    run: the package was damaged in transit and nothing it would score is experiment 39's prompt."""
    rows = e58.read_jsonl(e58.prompts_path(exp, prompt_key))
    for r in rows:
        if r["status"] == "render" and e58.prompt_sha(r["system"], r["user"]) != r["prompt_sha256"]:
            raise SystemExit(f"STOP: {exp} {prompt_key} {r['cell']}: prompt text does not hash to the frozen prompt_sha256")
    return rows


def pick_limited(rows: list[dict], n: int, n_tokens: dict[str, int]) -> list[dict]:
    """The smoke's subset: n cells spread evenly over prompt length, so the longest prompt is always in it."""
    ordered = sorted(rows, key=lambda r: (n_tokens[r["cell"]], r["cell"]))
    if n >= len(ordered):
        return ordered
    idx = sorted({round(i * (len(ordered) - 1) / max(n - 1, 1)) for i in range(n)})
    return [ordered[i] for i in idx]


def chat_ids(tokenizer, system: str, user: str, chat_kwargs: dict) -> tuple[list[int], bool]:
    """Token ids of the model's own chat template over [system, user], and whether the template itself opens the
    thinking block (then the generation starts inside it and '<think>' is restored in front of the raw text)."""
    text = tokenizer.apply_chat_template([{"role": "system", "content": system}, {"role": "user", "content": user}],
                                         tokenize=False, add_generation_prompt=True, **chat_kwargs)
    return tokenizer.encode(text, add_special_tokens=False), text.rstrip().endswith("<think>")


def engine_info(llm, model: dict, weights: Path) -> dict:
    import torch
    import vllm
    return {"vllm": vllm.__version__, "torch": torch.__version__, "python": platform.python_version(),
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "tensor_parallel_size": model["gpus"], "max_model_len": model["max_model_len"],
            "gpu_memory_utilization": e58.GPU_MEMORY_UTILIZATION, "quantization": model.get("quantization"),
            "weights_dir": str(weights), "host": platform.node()}


def make_llm(model_key: str, weights: Path):
    from vllm import LLM
    m = e58.MODELS[model_key]
    kw = dict(model=str(weights), tokenizer=str(weights), tensor_parallel_size=m["gpus"], max_model_len=m["max_model_len"],
              gpu_memory_utilization=e58.GPU_MEMORY_UTILIZATION, enable_prefix_caching=True, seed=e58.SEED,
              trust_remote_code=False)
    if m.get("quantization"):
        kw["quantization"] = m["quantization"]
    if m.get("mm_limits"):
        kw["limit_mm_per_prompt"] = m["mm_limits"]     # text-only judging: no image/video slots reserved
    return LLM(**kw)


def run_config(llm, tokenizer, model_key: str, exp: str, prompt_key: str, run: Path, limit: int | None, dry: bool) -> dict:
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    e39, _, _ = e58.e39_modules()
    m, p = e58.MODELS[model_key], e39.PROMPTS[prompt_key]
    config = e58.config_id(model_key, prompt_key)
    rows = [r for r in load_prompts(exp, prompt_key) if r["status"] == "render"]
    ids, prefilled = {}, {}
    for r in rows:
        ids[r["cell"]], prefilled[r["cell"]] = chat_ids(tokenizer, r["system"], r["user"], m.get("chat_kwargs", {}))
    n_tok = {c: len(v) for c, v in ids.items()}
    if limit:
        rows = pick_limited(rows, limit, n_tok)
    raw_file = H.raw_path(run, exp, model_key, prompt_key)
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    done = {r["cell"] for r in e58.read_jsonl(raw_file)} if raw_file.exists() else set()
    todo = [r for r in rows if r["cell"] not in done]
    # Model defaults (its generation_config.json: temperature, top_p, top_k), as each model's card recommends; only
    # the token budget, the per-cell seed and detokenization are set here (PROTOCOL.md section 4).
    base = llm.get_default_sampling_params()
    sampling_meta = {"source": "model generation_config defaults (vLLM get_default_sampling_params)",
                     "temperature": base.temperature, "top_p": base.top_p, "top_k": base.top_k, "min_p": base.min_p,
                     "repetition_penalty": base.repetition_penalty, "max_tokens_rule": f"min({p['max_tokens']}, max_model_len - prompt tokens)",
                     "min_generation_budget": e58.MIN_GENERATION_BUDGET, "seed_rule": "int(sha256('58|<config>|<cell>')[:8], 16)",
                     "skip_special_tokens": not m.get("harmony")}
    t0, n_out_tokens, n_called = time.time(), 0, 0
    over = []
    for r in list(todo):
        budget = min(p["max_tokens"], m["max_model_len"] - n_tok[r["cell"]])
        if budget < e58.MIN_GENERATION_BUDGET:
            over.append({"cell": r["cell"], "status": "unmeasured_over_context", "n_prompt_tokens": n_tok[r["cell"]],
                         "budget": budget, "reason": f"prompt {n_tok[r['cell']]} tokens leaves {budget} < {e58.MIN_GENERATION_BUDGET} new tokens"})
            todo.remove(r)
    if over and not dry:
        with open(raw_file, "a") as fh:
            for o in over:
                fh.write(json.dumps(o) + "\n")
    print(json.dumps({"config": config, "exp": exp, "cells": len(rows), "already_done": len(done), "to_generate": len(todo),
                      "over_context": len(over), "max_prompt_tokens": max(n_tok.values(), default=0)}), flush=True)
    if dry:
        return {"config": config, "to_generate": len(todo), "over_context": len(over)}
    for start in range(0, len(todo), e58.CHUNK):
        chunk = todo[start:start + e58.CHUNK]
        params, prompts = [], []
        for r in chunk:
            sp = base.clone()
            sp.max_tokens = min(p["max_tokens"], m["max_model_len"] - n_tok[r["cell"]])
            sp.seed = cell_seed(config, r["cell"])
            sp.skip_special_tokens = not m.get("harmony")
            params.append(sp)
            prompts.append(TokensPrompt(prompt_token_ids=ids[r["cell"]]))
        outs = llm.generate(prompts, params, use_tqdm=False)
        with open(raw_file, "a") as fh:
            for r, sp, o in zip(chunk, params, outs):
                c = o.outputs[0]
                text = ("<think>" if prefilled[r["cell"]] else "") + c.text
                n_out_tokens += len(c.token_ids)
                n_called += 1
                fh.write(json.dumps({"cell": r["cell"], "status": "generated", "prompt_sha256": r["prompt_sha256"],
                                     "text": text, "think_prefilled": prefilled[r["cell"]], "finish_reason": c.finish_reason,
                                     "n_prompt_tokens": n_tok[r["cell"]], "n_output_tokens": len(c.token_ids),
                                     "budget": sp.max_tokens, "seed": sp.seed}) + "\n")
        print(json.dumps({"config": config, "generated": min(start + e58.CHUNK, len(todo)), "of": len(todo),
                          "elapsed_s": round(time.time() - t0, 1), "output_tokens": n_out_tokens}), flush=True)
    meta_path = raw_file.with_suffix(".meta.json")
    meta = e58.read_json(meta_path) if meta_path.exists() else {"timing": []}
    meta.update(sampling=sampling_meta, run_ids={"slurm_job_id": os.environ.get("SLURM_JOB_ID"),
                                                 "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID")},
                limit_cells=limit)
    meta["timing"].append({"utc": e58.stamp(), "cells_generated": n_called, "output_tokens": n_out_tokens,
                           "seconds": round(time.time() - t0, 1), "gpus": m["gpus"]})
    e58.write_json(meta_path, meta)
    return meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=e58.MODEL_ORDER)
    ap.add_argument("--exp", required=True, choices=e58.EXPS)
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--weights", type=Path, required=True, help="local snapshot of the pinned revision (prepare.sh)")
    ap.add_argument("--prompts", default="all")
    ap.add_argument("--limit-cells", type=int, default=None, help="smoke only: this many cells per prompt configuration")
    ap.add_argument("--dry-run", action="store_true", help="tokenize and count only (needs the tokenizer, no GPU)")
    args = ap.parse_args()
    prompts = e58.PROMPT_ORDER if args.prompts == "all" else tuple(args.prompts.split(","))
    m = e58.MODELS[args.model]
    if args.dry_run:
        from transformers import AutoTokenizer
        llm, tokenizer = None, AutoTokenizer.from_pretrained(str(args.weights))
    else:
        llm = make_llm(args.model, args.weights)
        tokenizer = llm.get_tokenizer()
    for prompt_key in prompts:
        meta = run_config(llm, tokenizer, args.model, args.exp, prompt_key, args.run, args.limit_cells, args.dry_run)
        if not args.dry_run:
            rp = H.raw_path(args.run, args.exp, args.model, prompt_key).with_suffix(".meta.json")
            meta["engine"] = engine_info(llm, m, args.weights)
            e58.write_json(rp, meta)
            blob = H.harvest_one(args.run, args.exp, args.model, prompt_key)
            print(json.dumps({"harvest": blob["config"], "status_counts": blob["status_counts"]}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
