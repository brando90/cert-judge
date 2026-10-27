"""Shared helpers for E62 (cluster side: numpy only for statistics)."""
import json, math, re
import numpy as np

def load_pack(path):
    return [json.loads(l) for l in open(path)]

def build_prompt(tok, rec, addendum=""):
    sysm = rec["system"]
    if addendum.strip():
        k = sysm.rfind("Answer with ONLY one digit")
        sysm = sysm[:k] + "<additional_guidance>\n" + addendum.strip() + "\n</additional_guidance>\n\n" + sysm[k:]
    msgs = [{"role": "system", "content": sysm}, {"role": "user", "content": rec["user"]}]
    try:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

def digit_ids(tok):
    return [tok.convert_tokens_to_ids(str(d)) for d in range(6)]

def rank(x):
    x = np.asarray(x, float); o = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); i = 0
    xs = x[o]
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]: j += 1
        r[o[i:j + 1]] = (i + j) / 2.0; i = j + 1
    return r

def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0: return float("nan")
    return float(np.corrcoef(rank(x), rank(y))[0, 1])

def from_logprobs(lp_dict, dids):
    """lp_dict: token_id -> Logprob (vLLM). Returns (probs over digits 0..5 normalised, raw mass)."""
    p = np.array([math.exp(lp_dict[d].logprob) if d in lp_dict else 0.0 for d in dids])
    mass = float(p.sum())
    return (p / mass if mass > 0 else np.full(6, 1 / 6)), mass

def ev01(probs):
    return float((np.arange(6) * probs).sum() / 5.0)
