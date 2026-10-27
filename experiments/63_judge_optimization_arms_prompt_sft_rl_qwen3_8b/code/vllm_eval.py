#!/usr/bin/env python3
"""E62: zero-shot / fixed-prompt evaluation of a vLLM model on a pack. Reads the first generated token's digit
distribution (0..5) per unique prompt (temperature 0, max_tokens 1, top-20 logprobs) and writes probs, EV and the digit mass.
Usage: vllm_eval.py --model DIR --tp 2 --pack pack.jsonl --out out.json [--addendum FILE]"""
import argparse, json, time, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e62util import *
ap = argparse.ArgumentParser()
ap.add_argument("--model"); ap.add_argument("--tp", type=int, default=2); ap.add_argument("--pack"); ap.add_argument("--out")
ap.add_argument("--addendum", default=""); ap.add_argument("--maxlen", type=int, default=18000)
ap.add_argument("--util", type=float, default=0.90)
a = ap.parse_args()
from vllm import LLM, SamplingParams
t0 = time.time()
llm = LLM(a.model, tensor_parallel_size=a.tp, dtype="bfloat16", max_model_len=a.maxlen, enable_prefix_caching=True,
          gpu_memory_utilization=a.util, enforce_eager=False)
tok = llm.get_tokenizer(); dids = digit_ids(tok)
recs = load_pack(a.pack)
add = open(a.addendum).read() if a.addendum else ""
prompts = [build_prompt(tok, r, add) for r in recs]
ntok = [len(tok(p).input_ids) for p in prompts]
print("load s", round(time.time() - t0), "prompts", len(prompts), "tokens mean/max", sum(ntok) / len(ntok), max(ntok), flush=True)
t1 = time.time()
outs = llm.generate(prompts, SamplingParams(max_tokens=1, temperature=0.0, logprobs=20))
dt = time.time() - t1
res = {}
for r, o in zip(recs, outs):
    p, mass = from_logprobs(o.outputs[0].logprobs[0], dids)
    res[r["pid"]] = dict(probs=p.tolist(), ev=ev01(p), mass=mass, split=r["split"], kind=r["kind"], T=r["T"], human=r["human"], item=r["item"], task=r["task"])
json.dump(dict(model=a.model, tp=a.tp, seconds=dt, tokens=sum(ntok), tok_per_s=sum(ntok) / dt, addendum=add, res=res), open(a.out, "w"))
for sp in ("train", "val", "test"):
    ids = [k for k, v in res.items() if v["split"] == sp]
    if ids: print(sp, len(ids), "spearman(EV,T)", round(spearman([res[i]["ev"] for i in ids], [res[i]["T"] for i in ids]), 3),
                  "mean mass", round(sum(res[i]["mass"] for i in ids) / len(ids), 4))
print("eval s", round(dt), "tok/s", round(sum(ntok) / dt))
