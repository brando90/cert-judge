#!/usr/bin/env python3
"""E62 arms 2 and 3: LoRA training of an open-weight judge on the one-digit readout (single A100).
  --loss soft_ce : SFT, cross-entropy of the digit distribution against the teacher (frontier consensus) histogram
  --loss grpo    : RL pilot, GRPO-style policy gradient; the policy is the digit distribution at the answer token,
                   reward = 1 - |digit - 5T|/5 (closeness to the teacher consensus), group of G samples per prompt
Test prompts are never loaded (the train pack holds train+val only). Sanity controls: --overfit_n (tiny-batch overfit),
--shuffle_labels (teacher labels permuted over train prompts), digit mass, start loss vs prior loss, grad norm and LR logged
(jsonl + W&B offline).  Usage: sft_lora.py --model DIR --pack P --out OUT --seed 0 [--loss grpo] [--epochs 5]"""
import argparse, json, math, os, sys, time, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e62util import load_pack, build_prompt, digit_ids, spearman
sys.path.append(os.environ.get("E62_EXTRA_LIBS", "/nonexistent"))      # peft/accelerate/wandb only if the venv lacks them
import torch, torch.nn.functional as F
ap = argparse.ArgumentParser()
ap.add_argument("--model"); ap.add_argument("--pack"); ap.add_argument("--out"); ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--loss", default="soft_ce"); ap.add_argument("--epochs", type=int, default=5); ap.add_argument("--lr", type=float, default=2e-4)
ap.add_argument("--accum", type=int, default=8); ap.add_argument("--rank", type=int, default=16)
ap.add_argument("--shuffle_labels", action="store_true"); ap.add_argument("--human_mix", type=float, default=0.0)
ap.add_argument("--overfit_n", type=int, default=0); ap.add_argument("--overfit_steps", type=int, default=40)
ap.add_argument("--G", type=int, default=8); ap.add_argument("--beta", type=float, default=0.02)
ap.add_argument("--eval_pack", default=""); ap.add_argument("--adapter", default="")   # eval-only mode (frozen adapter on a pack)
ap.add_argument("--ngpu", type=int, default=1); ap.add_argument("--maxtok", type=int, default=24000); ap.add_argument("--name", default="")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, PeftModel
tok = AutoTokenizer.from_pretrained(a.model); dids = digit_ids(tok)
if a.ngpu > 1: model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="balanced")   # naive model parallel over the visible GPUs
else: model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16).cuda()
DEV0 = model.get_input_embeddings().weight.device
model.config.use_cache = False

def last_logits(pm, text):
    ids = tok(text, return_tensors="pt", add_special_tokens=False).input_ids[:, -a.maxtok:].to(DEV0)
    base = pm.get_base_model() if hasattr(pm, "get_base_model") else pm
    h = base.model(input_ids=ids, use_cache=False).last_hidden_state[:, -1]
    return base.lm_head(h).float()[0]                   # [vocab]

def digit_probs(logits):
    full = F.log_softmax(logits, -1)
    return full[dids], full                             # log-probs (full-vocab normalised) of the 6 digit tokens

@torch.no_grad()
def evaluate(pm, recs, label):
    pm.eval(); out = {}
    for r in recs:
        lp, _ = digit_probs(last_logits(pm, build_prompt(tok, r)))
        p = lp.exp(); mass = float(p.sum()); pn = (p / p.sum()).cpu().numpy()
        out[r["pid"]] = dict(probs=pn.tolist(), ev=float((np.arange(6) * pn).sum() / 5), mass=mass, split=r["split"], kind=r["kind"],
                             T=r["T"], human=r["human"], item=r["item"], task=r["task"])
    return out

def summarize(res, tag):
    s = {}
    for sp in ("train", "val", "test"):
        ids = [k for k, v in res.items() if v["split"] == sp]
        if not ids: continue
        s[sp] = dict(n=len(ids), rho_teacher=spearman([res[i]["ev"] for i in ids], [res[i]["T"] for i in ids]),
                     mass=float(np.mean([res[i]["mass"] for i in ids])))
        hv = [(res[i]["ev"], res[i]["human"]) for i in ids if res[i]["human"] is not None]
        if len(hv) > 3: s[sp]["rho_human"] = spearman([h[0] for h in hv], [h[1] for h in hv]); s[sp]["n_human"] = len(hv)
    print(tag, json.dumps(s), flush=True); return s

if a.eval_pack:                                           # frozen adapter -> pack
    pm = PeftModel.from_pretrained(model, a.adapter) if a.adapter else model
    recs = load_pack(a.eval_pack); res = evaluate(pm, recs, "eval")
    json.dump(dict(model=a.model, adapter=a.adapter, res=res), open(f"{a.out}/eval_{a.name or 'pack'}.json", "w")); summarize(res, "EVAL"); sys.exit(0)

recs = load_pack(a.pack); assert not any(r["split"] == "test" for r in recs)
train = [r for r in recs if r["split"] == "train"]; val = [r for r in recs if r["split"] == "val"]
def human_hist(h):
    x = 5 * h; lo = int(math.floor(x)); q = np.zeros(6); q[lo] += 1 - (x - lo)
    if lo < 5: q[lo + 1] += x - lo
    return q
targets = {}
for r in train:
    q = np.array(r["hist"])
    if a.human_mix > 0 and r["human"] is not None: q = (1 - a.human_mix) * q + a.human_mix * human_hist(r["human"])
    targets[r["pid"]] = q
if a.shuffle_labels:
    keys = [r["pid"] for r in train]; perm = np.random.default_rng(a.seed + 77).permutation(len(keys))
    targets = {keys[i]: targets[keys[perm[i]]] for i in range(len(keys))}
Tfix = {r["pid"]: r["T"] for r in train}
if a.shuffle_labels:
    Tfix = {keys[i]: Tfix[keys[perm[i]]] for i in range(len(keys))}
prior = np.mean([targets[r["pid"]] for r in train], 0)
prior_ce = float(-(prior * np.log(prior + 1e-9)).sum())
print("train prompts", len(train), "val", len(val), "prior (trivial) CE", round(prior_ce, 3), flush=True)

cfg = LoraConfig(r=a.rank, lora_alpha=2 * a.rank, lora_dropout=0.0, task_type="CAUSAL_LM",
                 target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])
pm = get_peft_model(model, cfg); pm.print_trainable_parameters()
model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False}); model.enable_input_require_grads()
params = [p for p in pm.parameters() if p.requires_grad]
opt = torch.optim.AdamW(params, lr=a.lr, weight_decay=0.0)
import wandb
os.environ.setdefault("WANDB_MODE", "offline")
wandb.init(project="e62-cert-judge", name=a.name or os.path.basename(a.out.rstrip("/")), dir=a.out, mode="offline", config=vars(a))
logf = open(f"{a.out}/train_log.jsonl", "a")
def log(d): logf.write(json.dumps(d) + "\n"); logf.flush(); wandb.log(d)

def step_loss(r):
    logits = last_logits(pm, build_prompt(tok, r))
    lp, full = digit_probs(logits)
    if a.loss == "soft_ce":
        q = torch.tensor(targets[r["pid"]], dtype=torch.float32, device=lp.device)
        return -(q * lp).sum(), dict(entropy=float(-(lp.exp() * lp).sum()))
    # GRPO-style: policy = digit distribution renormalised over 0..5; reference = adapter disabled
    pol = F.log_softmax(lp, -1)
    with torch.no_grad(), pm.disable_adapter():
        ref = F.log_softmax(digit_probs(last_logits(pm, build_prompt(tok, r)))[0], -1)
    d = torch.multinomial(pol.exp().detach(), a.G, replacement=True)
    reward = 1 - (d.float() - 5 * Tfix[r["pid"]]).abs() / 5
    adv = (reward - reward.mean()) / (reward.std() + 1e-4)
    kl = (pol.exp() * (pol - ref)).sum()
    return -(adv.detach() * pol[d]).mean() + a.beta * kl, dict(reward=float(reward.mean()), kl=float(kl), entropy=float(-(pol.exp() * pol).sum()))

# start-of-training reference numbers
if a.overfit_n: res0, s0 = {}, {}
else:
    res0 = evaluate(pm, val, "start"); s0 = summarize(res0, "START (untrained adapter = base model)")
    json.dump(res0, open(f"{a.out}/res_start.json", "w"))
curves = dict(prior_ce=prior_ce, start=s0, epochs=[])
if a.overfit_n:
    sub = train[:a.overfit_n]; losses = []
    for st in range(a.overfit_steps):
        pm.train(); tot = 0
        for r in sub:
            l, _ = step_loss(r); (l / len(sub)).backward(); tot += float(l) / len(sub)
        gn = float(torch.nn.utils.clip_grad_norm_(params, 1.0)); opt.step(); opt.zero_grad(); losses.append(tot)
        log(dict(step=st, loss=tot, grad_norm=gn)); print("overfit step", st, round(tot, 4), "gn", round(gn, 2), flush=True)
    ok = losses[-1] < 0.25 * losses[0]
    json.dump(dict(losses=losses, passed=bool(ok)), open(f"{a.out}/OVERFIT_TEST.json", "w")); print("OVERFIT TEST", "PASS" if ok else "FAIL", flush=True); sys.exit(0)

order = list(range(len(train))); total_steps = a.epochs * math.ceil(len(train) / a.accum); step = 0; t0 = time.time()
for ep in range(1, a.epochs + 1):
    random.shuffle(order); pm.train(); eloss = []; i = 0
    while i < len(order):
        batch = [train[j] for j in order[i:i + a.accum]]; i += a.accum; tot = 0; extra = {}
        for r in batch:
            try:
                l, ex = step_loss(r); (l / len(batch)).backward(); tot += float(l) / len(batch)
            except torch.OutOfMemoryError:        # a very long prompt does not fit on the 16 GB cards: skipped, counted, logged
                opt.zero_grad(set_to_none=False) if False else None; torch.cuda.empty_cache(); curves["oom_skipped"] = curves.get("oom_skipped", 0) + 1
                print("OOM skip", r["pid"], flush=True); continue
            for k, v in ex.items(): extra[k] = extra.get(k, 0) + v / len(batch)
        gn = float(torch.nn.utils.clip_grad_norm_(params, 1.0))
        lr = a.lr * min(1.0, (step + 1) / 3) * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * step / max(1, total_steps))))
        for g in opt.param_groups: g["lr"] = lr
        opt.step(); opt.zero_grad(); step += 1; eloss.append(tot)
        log(dict(step=step, epoch=ep, loss=tot, grad_norm=gn, lr=lr, minutes=(time.time() - t0) / 60, **extra))
    pm.save_pretrained(f"{a.out}/ep{ep}")
    res = evaluate(pm, val, "ep"); s = summarize(res, f"EPOCH {ep} train_loss {np.mean(eloss):.4f}")
    json.dump(res, open(f"{a.out}/res_ep{ep}.json", "w"))
    curves["epochs"].append(dict(epoch=ep, train_loss=float(np.mean(eloss)), summary=s))
    json.dump(curves, open(f"{a.out}/curves.json", "w"), indent=1)
key = "rho_human" if a.human_mix > 0 else "rho_teacher"
best = max(curves["epochs"], key=lambda e: (e["summary"]["val"].get(key) if e["summary"]["val"].get(key) == e["summary"]["val"].get(key) else -9))
json.dump(dict(frozen_epoch=best["epoch"], adapter=f"{a.out}/ep{best['epoch']}", selected_on=f"val {key}", curves=curves, args=vars(a)),
          open(f"{a.out}/FROZEN.json", "w"), indent=1)
print("FROZEN epoch", best["epoch"], flush=True)
