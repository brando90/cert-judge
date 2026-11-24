"""Shared code for experiment 67 (CPU only, zero model calls).
Metric definitions follow trustworthy-theorem-judges experiment 22 / cert-judge experiment 51 (6 categories 0..5, Laplace alpha 0.5).
Python 3.11+, numpy, scipy (run with a venv that has both)."""
import csv, json, math
from pathlib import Path
import numpy as np
from scipy import stats, optimize

CJ = Path(__file__).resolve().parents[3]
VB04 = CJ / "experiments/archive/04_veribench_validation"
VB13 = CJ / "experiments/archive/13_qwen_replication_exp16_exp19"
HL = CJ / "experiments/human_labels"
ALIAS = {"1_unsafeMultiply_safe.lean": "0_unsafeMultiply_safe.lean"}
FAM = {
    "Codex": (VB04 / "results_exp16_final_robust_r9_median/detail_rows.csv", VB04 / "results_exp28_varaware_codex_avg_newindex/judge_trust_vector.csv"),
    "Claude Opus": (VB04 / "results_exp16_opus47_r3_median/detail_rows.csv", VB04 / "results_exp28_varaware_opus_avg_newindex/judge_trust_vector.csv"),
    "Qwen3-Coder": (VB13 / "results/exp16_qwen_r3_median/detail_rows.csv", VB04 / "results_exp28_varaware_qwen_avg/judge_trust_vector.csv"),
}
HEADLINE = {"Codex": "gpt-5.3-codex|P8_STRICT_B", "Claude Opus": "claude-opus-4-7|P8_STRICT_B", "Qwen3-Coder": "Qwen/Qwen3-Coder-30B-A3B-Instruct|P8_STRICT_B"}

def read_labels(p, rename=False):
    out = {}
    for r in csv.DictReader(open(p), delimiter="\t"):
        g, c, s = r["gold_file"].strip(), r["candidate_file"].strip(), r["human_score_0_5"]
        if not g or not c or s in ("", None): continue
        if rename and g in ALIAS:
            g2 = ALIAS[g]; c = g2[:-5] + c[len(g[:-5]):] if c.startswith(g[:-5]) else c; g = g2
        out[(g, c)] = float(s)
    return out

def load_old_labels():
    eth1 = read_labels(VB04 / "data/ethan_human_scores_20260425.tsv")
    eth2 = read_labels(VB04 / "data/ethan_human_scores_ORIGINAL.tsv")
    vb = [read_labels(HL / f, rename=True) for f in ["participant1_data_correct_prompt.tsv", "participant2_data_pass_1.tsv", "participant3_data_pass_1.tsv", "participant4_data_pass_1.tsv", "participant5_data_pass_1.tsv"]]
    return eth1, eth2, vb

def lists(dicts, items, min_n=1):
    out = {}
    for it in items:
        v = [d[it] for d in dicts if it in d]
        if len(v) >= min_n: out[it] = v
    return out

def load_detail(path):
    out = {}
    for r in csv.DictReader(open(path)):
        if r["row_type"] != "human_eval_union": continue
        g, c = r["item_key"].split("::", 1)
        out.setdefault(r["judge_id"], {})[(g, c)] = (float(r["score_mean"]), json.loads(r["repeat_scores"]))
    return out

def load_ti(path):
    return {r["judge_id"]: float(r["TI_variance_aware"]) for r in csv.DictReader(open(path))}

# ---------- distributions and proper scores (categories 0..5)
def counts(vals):
    c = np.zeros(6)
    for v in vals: c[int(round(v))] += 1
    return c

def smooth(c, a):
    q = c + a
    return q / q.sum()

def rps(P, Q):
    pc, qc = np.cumsum(P)[:5], np.cumsum(Q)[:5]
    return float(np.mean((qc - pc) ** 2 + pc * (1 - pc)))

def ce(P, Q):
    m = P > 0
    return float(-np.sum(P[m] * np.log(np.maximum(Q[m], 1e-12))))

def tvd(P, Q):
    return float(0.5 * np.sum(np.abs(Q - P)))

def judge_dist(repeats):
    return counts([min(5, max(0, math.floor(5 * s + 0.5 + 1e-12))) for s in repeats])

def hum_dist(vals):
    c = counts(vals)
    return c / c.sum()

def scores(P, Q):
    return np.array([rps(P, Q), ce(P, Q), tvd(P, Q)])

# ---------- task-cluster bootstrap
def task_boot(task_ids, stat_fn, B=2000, seed=0):
    """stat_fn(list of item indices) -> float or array; resample tasks with replacement."""
    rng = np.random.default_rng(seed)
    tasks = sorted(set(task_ids)); idx = {t: [i for i, x in enumerate(task_ids) if x == t] for t in tasks}
    pt = np.asarray(stat_fn(list(range(len(task_ids)))), dtype=float)
    draws = []
    for _ in range(B):
        pick = rng.integers(0, len(tasks), len(tasks))
        ii = [i for k in pick for i in idx[tasks[k]]]
        with np.errstate(all="ignore"):
            draws.append(np.asarray(stat_fn(ii), dtype=float))
    d = np.array(draws)
    lo, hi = np.nanpercentile(d, 2.5, axis=0), np.nanpercentile(d, 97.5, axis=0)
    return pt, lo, hi

def sp(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or np.ptp(a) == 0 or np.ptp(b) == 0: return float("nan")
    return float(stats.spearmanr(a, b)[0])

def pe(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or np.ptp(a) == 0 or np.ptp(b) == 0: return float("nan")
    return float(stats.pearsonr(a, b)[0])

# ---------- calibration maps fitted on training tasks (used leave-one-task-out)
def fit_ce_ordinal(s, rating_lists, l2=1e-3):
    """Cumulative-logit P(H<=k) = sigmoid(theta_k - beta*s); fitted by maximum likelihood over every individual rating (= CE fit)."""
    s = np.asarray(s, float)
    C = np.array([counts(v) for v in rating_lists])  # n x 6
    def unpack(w):
        th = np.cumsum(np.concatenate([[w[0]], np.exp(w[1:5])])); return th, w[5]
    def nll(w):
        th, b = unpack(w)
        cum = 1 / (1 + np.exp(-(th[None, :] - b * s[:, None])))  # n x 5
        cum = np.concatenate([np.zeros((len(s), 1)), cum, np.ones((len(s), 1))], 1)
        p = np.clip(np.diff(cum, axis=1), 1e-9, 1)
        return -(C * np.log(p)).sum() / C.sum() + l2 * b * b
    marg = C.sum(0) / C.sum(); cm = np.cumsum(marg)[:5]; cm = np.clip(cm, 1e-3, 1 - 1e-3)
    th0 = np.log(cm / (1 - cm)); w0 = np.concatenate([[th0[0]], np.log(np.maximum(np.diff(th0), 1e-3)), [0.0]])
    r = optimize.minimize(nll, w0, method="L-BFGS-B")
    th, b = unpack(r.x)
    def predict(x):
        cum = 1 / (1 + np.exp(-(th[None, :] - b * np.asarray(x, float)[:, None])))
        cum = np.concatenate([np.zeros((len(x), 1)), cum, np.ones((len(x), 1))], 1)
        return smooth_rows(np.diff(cum, axis=1))
    return predict

def smooth_rows(p, eps=1e-3):
    p = np.clip(p, eps, None); return p / p.sum(1, keepdims=True)

def fit_pearson_gauss(s, rating_lists):
    """Correlation-style fit: least-squares line for the mean rating, then a discretised normal with the training residual SD of individual ratings."""
    s = np.asarray(s, float)
    xs = np.repeat(s, [len(v) for v in rating_lists]); ys = np.concatenate([np.asarray(v, float) for v in rating_lists])
    if np.ptp(xs) == 0: a, b = ys.mean(), 0.0
    else: b, a = np.polyfit(xs, ys, 1)
    sd = max(float(np.std(ys - (a + b * xs))), 0.3)
    def predict(x):
        mu = a + b * np.asarray(x, float)
        edges = np.arange(-0.5, 6.0, 1.0)
        cdf = stats.norm.cdf((edges[None, :] - mu[:, None]) / sd); p = np.diff(cdf, axis=1)
        p[:, 0] += cdf[:, 0]; p[:, -1] += 1 - cdf[:, -1]
        return smooth_rows(p)
    return predict

def fit_const(s, rating_lists):
    m = smooth(sum(counts(v) for v in rating_lists), 0.5)
    return lambda x: np.tile(m, (len(x), 1))

FITTERS = {"CONST": fit_const, "CE-fit": fit_ce_ordinal, "Pearson-fit": fit_pearson_gauss}

def loto(items, tasks, s, rating_lists):
    """Leave-one-task-out held-out [RPS,CE,TVD] per item for each fitter. Returns {name: n x 3 array}."""
    tasks = np.asarray(tasks); s = np.asarray(s, float)
    out = {k: np.zeros((len(items), 3)) for k in FITTERS}
    for t in sorted(set(tasks)):
        te = np.where(tasks == t)[0]; tr = np.where(tasks != t)[0]
        for k, f in FITTERS.items():
            pred = f(s[tr], [rating_lists[i] for i in tr])(s[te])
            for j, i in enumerate(te):
                out[k][i] = scores(hum_dist(rating_lists[i]), pred[j])
    return out
