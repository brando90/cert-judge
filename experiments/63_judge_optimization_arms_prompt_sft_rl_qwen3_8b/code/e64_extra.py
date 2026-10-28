"""E64 (AT-1631) extra stats: frozen epochs, train-loss trend, bootstrap P(seed-average >= 0.75), paired human-mix minus teacher-only. Extra seeds only."""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score62 as S
R = "/var/lib/agent/scratch/e62/results/runs/"
G = {"teacher": ["sft_q3_8b_s%d" % i for i in range(6)], "hm": ["sft_q3_8b_hm_s%d" % i for i in range(5)]}
for g, rs in G.items():
    for r in rs:
        f = json.load(open(R + r + "/FROZEN.json")); c = f["curves"]["epochs"]
        print(g, r, "frozen_ep", f["frozen_epoch"], "train_loss", [round(e["train_loss"], 2) for e in c], "val_rho_h", [round(e["summary"]["val"]["rho_human"], 2) for e in c])
A = {g: [S.crit_table(S.load(R + r + "/eval_test.json"), "test") for r in rs] for g, rs in G.items()}
ids = [x["item"] for x in A["teacher"][0]]; task = np.array([x["task"] for x in A["teacher"][0]]); H = np.array([x["human"] for x in A["teacher"][0]], float)
for g in A:
    for r in A[g]: assert [x["item"] for x in r] == ids
E = {g: np.array([[x["ev"] for x in r] for r in A[g]], float) for g in A}
uniq = sorted(set(task)); idx = {t: np.where(task == t)[0] for t in uniq}; rng = np.random.default_rng(S.SEED)
av = {g: [] for g in E}; diff = []; draws = 5000
for _ in range(draws):
    ii = np.concatenate([idx[uniq[j]] for j in rng.integers(0, len(uniq), len(uniq))])
    m = {g: np.mean([S.rho(E[g][k][ii], H[ii]) for k in range(len(E[g]))]) for g in E}
    if all(v == v for v in m.values()):
        for g in E: av[g].append(m[g])
        diff.append(m["hm"] - m["teacher"])
for g in av:
    a = np.array(av[g]); print(g, "P(seed-avg>=0.75)", round(float((a >= 0.75).mean()), 3), "P(seed-avg>0.60)", round(float((a > 0.60).mean()), 3), "CI", np.percentile(a, [2.5, 97.5]).round(2))
d = np.array(diff); print("hm - teacher seed-avg", round(float(d.mean()), 3), np.percentile(d, [2.5, 97.5]).round(3), "P(>0)", round(float((d > 0).mean()), 3))
# pooled per-seed point estimates
for g in E:
    h = [S.rho(e, H) for e in E[g]]; print(g, "min/max per-seed", round(min(h), 2), round(max(h), 2))
