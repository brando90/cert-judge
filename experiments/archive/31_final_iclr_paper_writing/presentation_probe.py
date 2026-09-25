"""Zero-spend check: do existing human labels track presentation (size/bloat) proxies of candidate files?"""
import csv, re, glob, collections, random
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, rankdata

R = Path(__file__).resolve().parents[3]
V = R / "experiments/archive/04_veribench_validation"

def load_labels(paths):
    acc = collections.defaultdict(list)
    for p in paths:
        for row in csv.DictReader(open(p), delimiter="\t"):
            s = (row.get("human_score_0_5") or "").strip()
            c = (row.get("candidate_file") or "").strip()
            if not s or not c:
                continue
            try:
                acc[c].append(float(s))
            except ValueError:
                continue
    return {k: float(np.mean(v)) for k, v in acc.items()}

views = {
    "panel_avg":  load_labels([V / "data/ethan_human_scores_avg_two_passes_20260425.tsv"]),
    "panel_pass1": load_labels([V / "data/ethan_human_scores_20260425.tsv"]),
    "panel_pass2": load_labels([V / "data/ethan_human_scores_ORIGINAL.tsv"]),
    "pool_mean":  load_labels(sorted(glob.glob(str(R / "experiments/human_labels/participant*_*.tsv")))),
}

judge = {}
for row in csv.DictReader(open(V / "results_exp16_consensus5_codex_r5_med/detail_rows.csv")):
    if row["judge_id"] == "gpt-5.3-codex|P4_CHECKLIST" and row["row_type"] == "human_eval_union":
        judge[row["item_key"].split("::")[1]] = float(row["score_mean"])

THM = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+)?(theorem|lemma)\s", re.M)
DEF = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|partial\s+|noncomputable\s+)*def\s", re.M)
TRIV = re.compile(r"(theorem|lemma)\s+\S+[^:]*:\s*True\s*:=")
def strip_comments(t):
    t = re.sub(r"/-.*?-/", "", t, flags=re.S)
    return re.sub(r"--.*", "", t)

def proxies(cand):
    p = R / "data/generated_agents" / cand
    if not p.exists():
        return None
    t = strip_comments(p.read_text(errors="ignore"))
    lines = [l for l in t.splitlines() if l.strip()]
    return {"chars": len(t), "lines": len(lines), "n_thm": len(THM.findall(t)),
            "n_def": len(DEF.findall(t)), "n_trivial_True": len(TRIV.findall(t))}

def problem(c):
    return c.rsplit("__agent", 1)[0]

def demean(keys, vals):
    by = collections.defaultdict(list)
    for k, v in zip(keys, vals):
        by[problem(k)].append(v)
    return np.array([v - np.mean(by[problem(k)]) for k, v in zip(keys, vals)])

def resid(y, x):
    X = np.c_[np.ones_like(x), x]
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ b

for vname, lab in views.items():
    keys = [k for k in lab if k in judge and proxies(k) is not None]
    P = {k: proxies(k) for k in keys}
    y = np.array([lab[k] for k in keys])
    j = np.array([judge[k] for k in keys])
    print(f"\n== {vname}: n={len(keys)} pairs, {len({problem(k) for k in keys})} problems; "
          f"rho(label, codex-P4 judge)={spearmanr(y, j)[0]:+.2f}")
    print(f"   {'proxy':15s} {'raw rho':>8s} {'within-prob':>12s} {'within|judge':>13s}   (p within|judge)")
    for name in ["chars", "lines", "n_thm", "n_def", "n_trivial_True"]:
        x = np.array([P[k][name] for k in keys], float)
        if np.all(x == x[0]):
            print(f"   {name:15s}  constant"); continue
        raw = spearmanr(y, x)[0]
        yr, xr, jr = (demean(keys, rankdata(a)) for a in (y, x, j))
        wp = spearmanr(yr, xr)[0]
        ry, rx = resid(yr, jr), resid(xr, jr)
        pc, pv = spearmanr(ry, rx)
        print(f"   {name:15s} {raw:+8.2f} {wp:+12.2f} {pc:+13.2f}   (p={pv:.2f})")
    triv = sum(P[k]["n_trivial_True"] > 0 for k in keys)
    print(f"   candidates with a `: True :=` theorem: {triv}/{len(keys)}")

ALL = [k for k in views["panel_avg"] if proxies(k) is not None]
n_thm_all = np.array([proxies(k)["n_thm"] for k in ALL])
chars_all = np.array([proxies(k)["chars"] for k in ALL])
print(f"\npanel candidates: {len(ALL)} files; theorem/lemma decls min/median/max = "
      f"{n_thm_all.min()}/{int(np.median(n_thm_all))}/{n_thm_all.max()}; chars min/median/max = "
      f"{chars_all.min()}/{int(np.median(chars_all))}/{chars_all.max()}")
