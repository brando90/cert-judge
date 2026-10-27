#!/usr/bin/env python3
"""E62 arm 1: reflective prompt optimisation of an <additional_guidance> block for a frozen open-weight judge (one-token
digit readout). Objective: Spearman(EV, teacher T) over the train prompts. Proposer = the same model (thinking off).
Selection: top-6 by train are scored on val (teacher Spearman); the val-best is FROZEN. Test is never read here.
Controls logged per candidate: Spearman against a fixed shuffled teacher vector (selection-inflation null), digit mass."""
import argparse, json, time, os, sys, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e62util import *
ap = argparse.ArgumentParser()
ap.add_argument("--model"); ap.add_argument("--tp", type=int, default=2); ap.add_argument("--pack"); ap.add_argument("--outdir")
ap.add_argument("--seed", type=int, default=0); ap.add_argument("--max_cands", type=int, default=40)
ap.add_argument("--per_round", type=int, default=8); ap.add_argument("--max_minutes", type=float, default=150)
ap.add_argument("--maxlen", type=int, default=18000); ap.add_argument("--util", type=float, default=0.90)
a = ap.parse_args()
os.makedirs(a.outdir, exist_ok=True)
rng = random.Random(a.seed)
from vllm import LLM, SamplingParams
llm = LLM(a.model, tensor_parallel_size=a.tp, dtype="bfloat16", max_model_len=a.maxlen, enable_prefix_caching=True,
          gpu_memory_utilization=a.util)
tok = llm.get_tokenizer(); dids = digit_ids(tok)
recs = load_pack(a.pack)
train = [r for r in recs if r["split"] == "train"]; val = [r for r in recs if r["split"] == "val"]
assert not any(r["split"] == "test" for r in recs)
Ttr = np.array([r["T"] for r in train]); Tva = np.array([r["T"] for r in val])
shuf = np.random.default_rng(1000 + a.seed).permutation(len(train))
t_start = time.time()

def score(addendum, rs):
    outs = llm.generate([build_prompt(tok, r, addendum) for r in rs], SamplingParams(max_tokens=1, temperature=0.0, logprobs=20), use_tqdm=False)
    ev, mass = [], []
    for o in outs:
        p, m = from_logprobs(o.outputs[0].logprobs[0], dids); ev.append(ev01(p)); mass.append(m)
    return np.array(ev), np.array(mass)

archive = []
def evaluate(addendum, origin):
    ev, mass = score(addendum, train)
    c = dict(id=len(archive), origin=origin, addendum=addendum, train_rho=spearman(ev, Ttr), train_rho_shuffled=spearman(ev, Ttr[shuf]),
             train_mae=float(np.abs(ev - Ttr).mean()), mass=float(mass.mean()), ev_sd=float(ev.std()), minutes=(time.time() - t_start) / 60)
    archive.append(c)
    json.dump(archive, open(f"{a.outdir}/archive.json", "w"), indent=1)
    print(f"[{c['minutes']:.1f} min] cand {c['id']} ({origin}) train rho {c['train_rho']:.3f} shuffled {c['train_rho_shuffled']:.3f} mae {c['train_mae']:.3f} mass {c['mass']:.3f}", flush=True)
    return c, ev

SEEDS = ["", "Score strictly by the checklist: a gold theorem only counts as covered if the agent states an equivalent or stronger property, not merely a related one.",
         "Check the agent file for sorry-only or vacuous theorems; they cover nothing. Empty or missing statements score 0."]
base, base_ev = evaluate("", "baseline")
pop = [base]
for s in SEEDS[1:]: pop.append(evaluate(s, "seed")[0])
last_ev = {c["id"]: None for c in pop}

PROPOSE = ("You are improving the scoring guidance given to an LLM judge that rates how well an agent's Lean 4 theorem statements cover "
           "the gold theorem statements (score 0-5). The judge reads a fixed rubric and then your extra guidance. Below is the current "
           "guidance and cases where the judge's score disagreed with the consensus of expert raters.\n\nCurrent guidance:\n{cur}\n\n"
           "Disagreements (consensus score vs judge score, kind of case, expert rationale):\n{cases}\n\n"
           "Write an improved guidance block (at most 120 words) of concrete, general scoring rules that would fix these disagreements. "
           "Do not mention task names. Output only the guidance text.")
def cases_for(c):
    ev, _ = score(c["addendum"], train)
    err = np.abs(ev - Ttr); idx = np.argsort(-err)[:6]
    lines = []
    for i in idx:
        r = train[i]
        lines.append(f"- consensus {Ttr[i]*5:.1f}, judge {ev[i]*5:.1f}, kind {r['kind']}: {r.get('rationale','')[:300]}")
    return "\n".join(lines)

while len(archive) < a.max_cands and (time.time() - t_start) / 60 < a.max_minutes:
    pop.sort(key=lambda c: -c["train_rho"] if c["train_rho"] == c["train_rho"] else 1)
    parents = pop[:2]
    msgs = []
    for p in parents:
        cs = cases_for(p)
        for _ in range(a.per_round // 2):
            m = [{"role": "user", "content": PROPOSE.format(cur=p["addendum"] or "(none)", cases=cs)}]
            try: msgs.append(tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True, enable_thinking=False))
            except TypeError: msgs.append(tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True))
    outs = llm.generate(msgs, SamplingParams(max_tokens=300, temperature=1.0, top_p=0.95, seed=rng.randrange(10**6)), use_tqdm=False)
    for o in outs:
        txt = o.outputs[0].text.strip()
        if len(txt) < 20 or len(archive) >= a.max_cands: continue
        pop.append(evaluate(txt, "reflect")[0])
pop.sort(key=lambda c: -c["train_rho"] if c["train_rho"] == c["train_rho"] else 1)
top = pop[:6]
for c in top:
    ev, mass = score(c["addendum"], val)
    c["val_rho_teacher"] = spearman(ev, Tva); c["val_mass"] = float(mass.mean())
    hv = [(e, r["human"]) for e, r in zip(ev, val) if r["human"] is not None]
    c["val_rho_human"] = spearman([h[0] for h in hv], [h[1] for h in hv]) if len(hv) > 3 else None
    print("val", c["id"], "train", round(c["train_rho"], 3), "val teacher", round(c["val_rho_teacher"], 3), "val human", c["val_rho_human"], flush=True)
best = max(top, key=lambda c: c["val_rho_teacher"] if c["val_rho_teacher"] == c["val_rho_teacher"] else -9)
json.dump(dict(frozen=best, top6=top, baseline=base, n_candidates=len(archive), seed=a.seed, model=a.model,
               best_shuffled_null=max(c["train_rho_shuffled"] for c in archive), best_real=max(c["train_rho"] for c in archive)),
          open(f"{a.outdir}/FROZEN.json", "w"), indent=1)
print("FROZEN candidate", best["id"], "val teacher", best["val_rho_teacher"], flush=True)
