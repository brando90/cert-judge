"""E64 (AT-1631) additional-seed report: teacher-only SFT and human-mix SFT on Qwen3-8B, all seeds that exist, test scored once per run by score62.py's metrics.
Reports per-seed Spearman (task-cluster CI), mean and SD across seeds, fraction of seeds >= 0.75, task-cluster bootstrap CI of the seed-average Spearman
(same task resample for every seed) and of the mean-EV ensemble. Usage: e64_report.py [--out report_e64.md]. Extra seeds only; no selection on test."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score62 as S
R = os.environ.get("E62_RUNS", "/var/lib/agent/scratch/e62/results/runs/")
G = {"teacher_only_SFT": ["sft_q3_8b_s%d" % i for i in range(6)], "human_mix_SFT": ["sft_q3_8b_hm_s%d" % i for i in range(5)]}
def avg_boot(rs, draws=5000):
    rows = [S.crit_table(r, "test") for r in rs]; ids = [x["item"] for x in rows[0]]
    for r in rows: assert [x["item"] for x in r] == ids
    task = np.array([x["task"] for x in rows[0]]); H = np.array([x["human"] for x in rows[0]], float)
    E = np.array([[x["ev"] for x in r] for r in rows], float)
    uniq = sorted(set(task)); idx = {t: np.where(task == t)[0] for t in uniq}; rng = np.random.default_rng(S.SEED); v = []; ve = []
    for _ in range(draws):
        ii = np.concatenate([idx[uniq[j]] for j in rng.integers(0, len(uniq), len(uniq))])
        a = [S.rho(E[k][ii], H[ii]) for k in range(len(rs))]; e = S.rho(E.mean(0)[ii], H[ii])
        if all(x == x for x in a): v.append(np.mean(a))
        if e == e: ve.append(e)
    ci = lambda x: [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]
    return ci(v), ci(ve), float(S.rho(E.mean(0), H))
out = {}; L = ["| arm | seeds | per-seed Spearman | mean | SD | seeds >= 0.75 | seed-average 95% CI (task-cluster) | ensemble Spearman [95% CI] |", "|---|---|---|---|---|---|---|---|"]
for g, runs in G.items():
    runs = [r for r in runs if os.path.exists(R + r + "/eval_test.json")]
    rs = [S.load(R + r + "/eval_test.json") for r in runs]
    per = [S.metrics(r, "test", 0.3) for r in rs]; h = [p["spearman"] for p in per]
    ci_avg, ci_ens, ens = avg_boot(rs)
    out[g] = dict(runs=runs, per_seed=h, per_seed_ci=[p["spearman_ci"] for p in per], mean=float(np.mean(h)), sd=float(np.std(h, ddof=1)),
                  n_ge_075=int(sum(x >= 0.75 for x in h)), avg_ci=ci_avg, ens=ens, ens_ci=ci_ens)
    L.append(f"| {g} | {len(runs)} | " + ", ".join(f"{x:.2f}" for x in h) + f" | {np.mean(h):.2f} | {np.std(h, ddof=1):.2f} | {sum(x >= 0.75 for x in h)}/{len(h)} | [{ci_avg[0]:.2f}, {ci_avg[1]:.2f}] | {ens:.2f} [{ci_ens[0]:.2f}, {ci_ens[1]:.2f}] |")
d = os.path.dirname(os.path.abspath(__file__)); o = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(d, "..", "report_e64.md")
open(o, "w").write("\n".join(L) + "\n"); json.dump(out, open(o.rsplit(".", 1)[0] + ".json", "w"), indent=1); print("\n".join(L))
for g in out: print(g, out[g]["runs"])
