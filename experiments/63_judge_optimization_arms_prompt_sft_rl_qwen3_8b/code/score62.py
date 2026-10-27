#!/usr/bin/env python3
"""E62 scoring: one script for every arm and baseline. Input: result files (res = {pid: {ev, T, human, item, task, split, kind}}).
For a split's 'crit' items (human-rated): Spearman, Pearson, Kendall, ICC(C,1), ICC(A,1) of EV against the expert mean with task-cluster
bootstrap 95% CIs (10,000 draws Spearman, 2,000 others, seed 62); teacher agreement (Spearman of EV with T over all prompts of the split);
across-run SD for groups of seeds. Usage: score62.py --split test NAME=file[,file...] ... --out report.md"""
import argparse, json, sys
import numpy as np
from scipy.stats import kendalltau, rankdata
SEED = 62
def rho(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0: return float("nan")
    return float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])
def pear(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0: return float("nan")
    return float(np.corrcoef(x, y)[0, 1])
def kend(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0: return float("nan")
    return float(kendalltau(x, y).statistic)
def icc(x, y, kind):
    d = np.column_stack([np.asarray(x, float), np.asarray(y, float)]); n, k = d.shape
    if n < 3: return float("nan")
    gm = d.mean(); msr = k * ((d.mean(1) - gm) ** 2).sum() / (n - 1); msc = n * ((d.mean(0) - gm) ** 2).sum() / (k - 1)
    sse = ((d - d.mean(1, keepdims=True) - d.mean(0, keepdims=True) + gm) ** 2).sum(); mse = sse / ((n - 1) * (k - 1))
    den = msr + (k - 1) * mse if kind == "C" else msr + (k - 1) * mse + k * (msc - mse) / n
    return float((msr - mse) / den) if den > 0 else float("nan")
METRICS = {"spearman": (rho, 10000), "pearson": (pear, 2000), "kendall": (kend, 2000),
           "icc_c1": (lambda a, b: icc(a, b, "C"), 2000), "icc_a1": (lambda a, b: icc(a, b, "A"), 2000)}
def boot(x, y, tasks, fn, draws):
    x, y, tasks = np.asarray(x, float), np.asarray(y, float), np.asarray(tasks)
    uniq = sorted(set(tasks)); idx = {t: np.where(tasks == t)[0] for t in uniq}; rng = np.random.default_rng(SEED); v = []
    for _ in range(draws):
        ii = np.concatenate([idx[uniq[j]] for j in rng.integers(0, len(uniq), len(uniq))]); t = fn(x[ii], y[ii])
        if t == t: v.append(t)
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) > 50 else None
def load(path):
    return json.load(open(path))["res"] if "res" in json.load(open(path)) else json.load(open(path))
def crit_table(res, split):
    rows = [v for v in res.values() if v["split"] == split and v["human"] is not None]
    rows.sort(key=lambda v: v["item"]); return rows
def metrics(res, split, draws_scale=1.0):
    rows = crit_table(res, split)
    x = [r["ev"] for r in rows]; y = [r["human"] for r in rows]; t = [r["task"] for r in rows]; out = {"n_items": len(rows), "n_tasks": len(set(t))}
    for name, (fn, d) in METRICS.items():
        out[name] = fn(x, y); out[name + "_ci"] = boot(x, y, t, fn, int(d * draws_scale)) if len(rows) > 3 else None
    allp = [v for v in res.values() if v["split"] == split]
    out["teacher_rho_all_prompts"] = rho([v["ev"] for v in allp], [v["T"] for v in allp]); out["n_prompts"] = len(allp)
    out["mean_digit_mass"] = float(np.mean([v["mass"] for v in allp])) if "mass" in allp[0] else None
    return out
def fmt(v, ci=None):
    if v != v: return "nan"
    s = f"{v:.2f}"; return s + (f" [{ci[0]:.2f}, {ci[1]:.2f}]" if ci else "")
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--split", default="test"); ap.add_argument("--out"); ap.add_argument("--draws_scale", type=float, default=1.0)
    ap.add_argument("runs", nargs="+"); a = ap.parse_args()
    lines = [f"Human agreement on {a.split} items (95% task-cluster bootstrap CIs); EV = expected 0-5 score from the digit distribution", "",
             "| arm | runs | n items/tasks | Spearman | Pearson | Kendall | ICC(C,1) | ICC(A,1) | teacher rho (all prompts) | SD of Spearman across runs |", "|---|---|---|---|---|---|---|---|---|---|"]
    allj = {}
    for spec in a.runs:
        name, files = spec.split("=", 1); files = files.split(","); ms = [metrics(load(f), a.split, a.draws_scale) for f in files]
        m = ms[0] if len(ms) == 1 else None
        if len(ms) > 1:   # mean over runs of each metric; CI of the item-mean ensemble not computed, SD across runs reported
            m = {k: float(np.nanmean([x[k] for x in ms])) if isinstance(ms[0][k], float) else ms[0][k] for k in ms[0] if not k.endswith("_ci")}
            for k in METRICS: m[k + "_ci"] = None
        sd = float(np.nanstd([x["spearman"] for x in ms], ddof=1)) if len(ms) > 1 else None
        allj[name] = dict(per_run=ms, summary=m, sd_spearman_across_runs=sd)
        lines.append(f"| {name} | {len(files)} | {m['n_items']}/{m['n_tasks']} | {fmt(m['spearman'], m.get('spearman_ci'))} | {fmt(m['pearson'], m.get('pearson_ci'))} | "
                     f"{fmt(m['kendall'], m.get('kendall_ci'))} | {fmt(m['icc_c1'], m.get('icc_c1_ci'))} | {fmt(m['icc_a1'], m.get('icc_a1_ci'))} | "
                     f"{fmt(m['teacher_rho_all_prompts'])} | {'' if sd is None else f'{sd:.2f}'} |")
    open(a.out, "w").write("\n".join(lines) + "\n"); json.dump(allj, open(a.out.rsplit(".", 1)[0] + ".json", "w"), indent=1); print("\n".join(lines))
