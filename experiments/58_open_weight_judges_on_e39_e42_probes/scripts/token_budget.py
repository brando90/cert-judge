#!/usr/bin/env python3
"""TLDR: Pre-run check with no model call: tokenize every rendered cell of experiments 39 and 42 through each panel
model's own chat template (tokenizer files only) and record prompt lengths, the cells that would be
unmeasured_over_context under the frozen budget rule, whether the template opens the thinking block, and each model's
generation_config sampling defaults. Writes results/TOKEN_BUDGET.json (prompt lengths only, no scores).

Usage: token_budget.py --tokenizers <dir with one subfolder per model key> [--models all]"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e58                                                    # noqa: E402
from judge_vllm import chat_ids                               # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizers", type=Path, required=True)
    ap.add_argument("--models", default="all")
    args = ap.parse_args()
    from transformers import AutoTokenizer
    e39, _, _ = e58.e39_modules()
    models = e58.MODEL_ORDER if args.models == "all" else args.models.split(",")
    rows_by = {(exp, p): [r for r in e58.read_jsonl(e58.prompts_path(exp, p)) if r["status"] == "render"]
               for exp in e58.EXPS for p in e58.PROMPT_ORDER}
    out = {"written_utc": e58.stamp(), "rule": f"budget = min(prompt max_tokens, max_model_len - prompt tokens); "
           f"budget < {e58.MIN_GENERATION_BUDGET} -> unmeasured_over_context", "models": {}}
    for k in models:
        m = e58.MODELS[k]
        tdir = args.tokenizers / k
        tok = AutoTokenizer.from_pretrained(str(tdir))
        gen_path = tdir / "generation_config.json"
        gen = json.loads(gen_path.read_text()) if gen_path.exists() else {}
        rec = {"repo": m["repo"], "revision": m["revision"], "max_model_len": m["max_model_len"],
               "generation_config": {x: gen.get(x) for x in ("temperature", "top_p", "top_k", "min_p", "repetition_penalty")},
               "configs": {}}
        for exp in e58.EXPS:
            for p in e58.PROMPT_ORDER:
                n, pre = [], set()
                for r in rows_by[(exp, p)]:
                    ids, prefilled = chat_ids(tok, r["system"], r["user"], m.get("chat_kwargs", {}))
                    n.append(len(ids))
                    pre.add(prefilled)
                max_tokens = e39.PROMPTS[p]["max_tokens"]
                over = sum(1 for x in n if min(max_tokens, m["max_model_len"] - x) < e58.MIN_GENERATION_BUDGET)
                rec["configs"][f"{exp}|{p}"] = {"cells": len(n), "prompt_tokens_total": sum(n), "prompt_tokens_mean": round(statistics.mean(n)),
                                                "prompt_tokens_max": max(n), "over_context": over, "think_prefilled": sorted(pre)}
        rec["over_context_total"] = {exp: sum(v["over_context"] for c, v in rec["configs"].items() if c.startswith(exp)) for exp in e58.EXPS}
        rec["prompt_tokens_total"] = {exp: sum(v["prompt_tokens_total"] for c, v in rec["configs"].items() if c.startswith(exp)) for exp in e58.EXPS}
        rec["prompt_tokens_max"] = max(v["prompt_tokens_max"] for v in rec["configs"].values())
        rec["think_prefilled"] = sorted({x for v in rec["configs"].values() for x in v["think_prefilled"]})
        out["models"][k] = rec
        print(json.dumps({k: {"max": rec["prompt_tokens_max"], "over": rec["over_context_total"], "prefilled": rec["think_prefilled"],
                              "gen": rec["generation_config"]}}), flush=True)
    e58.write_json(e58.RESULTS / "TOKEN_BUDGET.json", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
