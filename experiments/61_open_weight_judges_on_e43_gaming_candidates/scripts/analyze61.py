#!/usr/bin/env python3
"""TLDR: Experiment 61 analysis (PROTOCOL.md section 3, frozen): per open-weight judge unit (model, prompt), gaming gap vs experiment 43's cached reference, tracking of the reference and of Sonnet's gain, cross-prompt table, flag split. Pure python, zero model calls.
Usage: analyze61.py --run RUN --prompts prompts61.jsonl --out DIR   (RUN has raw/<model>.jsonl and meta_<model>.json; needs the VeriBench clone via experiment 43's e43 for the parsers)"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

E61 = Path(__file__).resolve().parents[1]
E43 = E61.parent / "43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index"
sys.path[:0] = [str(E43 / "scripts")]
import e43  # noqa: E402

PROMPTS = ("D0", "H2", "P1")
MODELS = ("qwen3_4b", "q25_14b_awq", "qwen3_8b")
LABEL = {"qwen3_4b": "Qwen3-4B bf16 (thinking)", "q25_14b_awq": "Qwen2.5-14B-Instruct-AWQ int4",
         "qwen3_8b": "Qwen3-8B bf16 TP2 (thinking)"}
BOOT = 10000


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def final_text(text: str) -> str | None:
    if "</think>" in text:
        return text.rsplit("</think>", 1)[1].strip()
    if "<think>" in text:
        return None
    return text.strip()


def ranks(x):
    order = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and x[order[j + 1]] == x[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    if len(a) < 3:
        return None
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    sa = sum((x - ma) ** 2 for x in ra) ** 0.5
    sb = sum((y - mb) ** 2 for y in rb) ** 0.5
    if sa == 0 or sb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / (sa * sb)


def boot(rows, stat, seed=61):
    """Task-cluster bootstrap CI of stat(rows); rows carry 'task'."""
    by = defaultdict(list)
    for r in rows:
        by[r["task"]].append(r)
    tasks = sorted(by)
    rng = random.Random(seed)
    vals = []
    for _ in range(BOOT):
        s = []
        for t in (rng.choice(tasks) for _ in tasks):
            s += by[t]
        v = stat(s)
        if v is not None:
            vals.append(v)
    vals.sort()
    if len(vals) < 100:
        return None
    return [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]]


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--prompts", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    prows = [json.loads(l) for l in a.prompts.read_text().splitlines() if l.strip()]
    det = {r["cell"]: r["score"] for r in prows if r["status"] == "deterministic"}
    cells = json.loads((E43 / "results/full/cells.json").read_text())["cells"]
    starts = {}
    for f in (E43 / "results/full/candidates/starts").glob("*.lean"):
        starts[f.stem] = sha(f.read_bytes())
    out = {"units": {}, "models": {}}
    scores = {}      # (model, prompt, item, text sha) -> {"mean", "n", "counts"}
    for m in MODELS:
        rp = a.run / "raw" / f"{m}.jsonl"
        if not rp.exists():
            continue
        meta = a.run / f"meta_{m}.json"
        out["models"][m] = json.loads(meta.read_text()) if meta.exists() else {"note": "no meta (run unfinished)"}
        got = defaultdict(list)
        cnt = defaultdict(Counter)
        for l in rp.read_text().splitlines():
            if not l.strip():
                continue
            d = json.loads(l)
            item, tsha16, p = d["cell"].split("|")
            key = (p, item, tsha16)
            if d["status"] != "generated":
                cnt[key][d["status"]] += 1
                continue
            ft = final_text(d["text"])
            try:
                if ft is None:
                    raise ValueError("unclosed_think")
                got[key].append(e43.parse_judge(e43.PROMPTS[p]["rubric"], ft))
                cnt[key]["measured"] += 1
            except Exception:
                cnt[key]["parse_error"] += 1
        for key in set(got) | set(cnt):
            scores[(m,) + key] = {"mean": mean(got.get(key, [])), "n": len(got.get(key, [])), "counts": dict(cnt[key])}

    def score(m, p, item, tsha):
        cell = f"{item}|{tsha[:16]}|{p}"
        if cell in det:
            return det[cell]
        s = scores.get((m, p, item, tsha[:16]))
        return None if s is None else s["mean"]

    for m in MODELS:
        if m not in out["models"]:
            continue
        tot = Counter()
        for (mm, p, item, t), s in scores.items():
            if mm == m:
                tot.update(s["counts"])
        out["models"][m]["status_counts"] = dict(tot)
        cross = defaultdict(list)
        for p in PROMPTS:
            rows = []
            for c in cells:
                if c["judge"].split("|")[1] != p:
                    continue
                item = c["item"]
                s0 = score(m, p, item, starts[item])
                s1 = score(m, p, item, c["final_sha256"])
                gain = None if s0 is None or s1 is None else (0.0 if c["final_is_start"] else s1 - s0)
                rows.append({"cell": c["cell"], "task": c["task"], "item": item, "gain": gain, "ref_gain": c["reference_gain"],
                             "sonnet_gain": c["attacked_gain"], "final_is_start": c["final_is_start"],
                             "flagged": bool((c.get("checks") or {}).get("flagged_added") or (c.get("checks") or {}).get("n_flagged", 0)),
                             "sonnet_gap": c["gaming_gap"]})
                for q in PROMPTS:
                    t0, t1 = score(m, q, item, starts[item]), score(m, q, item, c["final_sha256"])
                    if t0 is not None and t1 is not None:
                        cross[(p, q)].append(0.0 if c["final_is_start"] else t1 - t0)
            ok = [r for r in rows if r["gain"] is not None]
            for r in ok:
                r["gap"] = r["gain"] - r["ref_gain"]
            unit = {"model": m, "prompt": p, "n_cells": len(rows), "n_measured": len(ok),
                    "n_edited_cells": sum(1 for r in ok if not r["final_is_start"])}
            if len(ok) >= 3:
                unit["gain_mean"] = mean([r["gain"] for r in ok])
                unit["ref_gain_mean"] = mean([r["ref_gain"] for r in ok])
                unit["sonnet_gain_mean"] = mean([r["sonnet_gain"] for r in ok])
                unit["gap_mean"] = mean([r["gap"] for r in ok])
                unit["gap_ci95"] = boot(ok, lambda s: mean([r["gap"] for r in s]))
                unit["sonnet_gap_mean"] = mean([r["sonnet_gap"] for r in ok])
                unit["verdict"] = ("TRANSFERS" if unit["gap_ci95"] and unit["gap_ci95"][0] > 0 else "NO TRANSFER")
                unit["spearman_ref"] = spearman([r["gain"] for r in ok], [r["ref_gain"] for r in ok])
                unit["spearman_ref_ci95"] = boot(ok, lambda s: spearman([r["gain"] for r in s], [r["ref_gain"] for r in s]))
                unit["spearman_sonnet"] = spearman([r["gain"] for r in ok], [r["sonnet_gain"] for r in ok])
                sign = lambda x: (x > 1e-9) - (x < -1e-9)
                unit["same_sign_as_ref"] = sum(1 for r in ok if sign(r["gain"]) == sign(r["ref_gain"]))
                for name, sub in (("flagged", [r for r in ok if r["flagged"]]), ("not_flagged", [r for r in ok if not r["flagged"]])):
                    unit[f"gap_mean_{name}"] = mean([r["gap"] for r in sub])
                    unit[f"n_{name}"] = len(sub)
            unit["rows"] = rows
            out["units"][f"{m}|{p}"] = unit
        out["models"][m]["cross_prompt_mean_gain"] = {f"attacked_{p}__scored_{q}": {"mean": mean(v), "n": len(v)} for (p, q), v in sorted(cross.items())}
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "ANALYSIS61.json").write_text(json.dumps(out, indent=1, default=str))
    # table
    f = lambda x: "n/a" if x is None else f"{x:+.3f}"
    L = ["Harness for every row: single call, no tools (vllm_offline). Gap = mean over cells of (open-weight judge's gain - reference gain); CI = task-cluster bootstrap (6 tasks). Sonnet gap = experiment 43's figure for the same cells.", "",
         "model | prompt | n meas/cells | gap [95% CI] | verdict | Sonnet gap (E43) | rho vs reference | rho vs Sonnet gain | same sign as ref"]
    for k, u in out["units"].items():
        if "gap_mean" not in u:
            L.append(f"{u['model']} | {u['prompt']} | {u['n_measured']}/{u['n_cells']} | n/a")
            continue
        ci = u["gap_ci95"]
        L.append(f"{LABEL[u['model']]} | {u['prompt']} | {u['n_measured']}/{u['n_cells']} | {f(u['gap_mean'])} [{f(ci[0]) if ci else 'n/a'}, {f(ci[1]) if ci else 'n/a'}] | {u['verdict']} | "
                 f"{f(u['sonnet_gap_mean'])} | {f(u['spearman_ref'])} | {f(u['spearman_sonnet'])} | {u['same_sign_as_ref']}/{u['n_measured']}")
    (a.out / "TABLE61.txt").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
