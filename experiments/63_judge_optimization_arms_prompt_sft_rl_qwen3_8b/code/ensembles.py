import sys, json, numpy as np
sys.path.insert(0, "/var/lib/agent/scratch/e62/code")
import score62 as S
R = "/var/lib/agent/scratch/e62/results/runs/"
G = {"prompt_opt": ["arm1_q3_8b_s0", "arm1_q3_8b_s1"], "sft": ["sft_q3_8b_s0", "sft_q3_8b_s1", "sft_q3_8b_s2"],
     "sft_humanmix": ["sft_q3_8b_hm_s0", "sft_q3_8b_hm_s1"], "rl": ["rl_q3_8b_s0", "rl_q3_8b_s1", "rl_q3_8b_s2"]}
base = S.load(R + "base_q3_8b_test.json")
out = {}; lines = ["| arm | seeds | ensemble (mean EV) Spearman [CI] | ensemble Pearson [CI] | mean per-prompt SD of EV across seeds (all 102 test prompts) | per-seed Spearman: min..max | per-seed Spearman lower CI > 0.60 |", "|---|---|---|---|---|---|---|"]
for g, runs in G.items():
    rs = [S.load(R + r + "/eval_test.json") for r in runs]
    ens = {}
    for pid, v in rs[0].items():
        e = dict(v); e["ev"] = float(np.mean([r[pid]["ev"] for r in rs])); ens[pid] = e
    m = S.metrics(ens, "test"); per = [S.metrics(r, "test", 0.3) for r in rs]
    sd = float(np.mean([np.std([r[pid]["ev"] for r in rs], ddof=1) for pid in rs[0]]))
    hum = [S.rho(*[list(t) for t in zip(*[(x["ev"], x["human"]) for x in S.crit_table(r, "test")])]) for r in rs]
    out[g] = dict(ens=m, sd_ev=sd, per_seed_spearman=hum, per_seed_ci=[p["spearman_ci"] for p in per])
    lines.append(f"| {g} | {len(runs)} | {S.fmt(m['spearman'], m['spearman_ci'])} | {S.fmt(m['pearson'], m['pearson_ci'])} | {sd:.3f} | {min(hum):.2f}..{max(hum):.2f} | {sum(1 for p in per if p['spearman_ci'] and p['spearman_ci'][0] > 0.60)}/{len(runs)} |")
# base EV spread for reference
allev = [v["ev"] for v in base.values()]
lines.append(""); lines.append(f"Reference: EV spread over test prompts (SD of EV across the 102 prompts): base {np.std(allev):.3f}")
for g, runs in G.items():
    rs = [S.load(R + r + "/eval_test.json") for r in runs]; lines.append(f"- {g}: SD of EV across prompts (seed 0) {np.std([v['ev'] for v in rs[0].values()]):.3f}")
open("/var/lib/agent/scratch/e62/report_ensembles.md", "w").write("\n".join(lines) + "\n"); json.dump(out, open("/var/lib/agent/scratch/e62/report_ensembles.json", "w"), indent=1)
print("\n".join(lines))
