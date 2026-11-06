#!/usr/bin/env python3
"""TLDR: Experiment 66 condition R2 (retrospective, zero calls): on 99 natural solver outputs from VeriBench experiment
106 v5 that a Lean entailment prover already checked (exact candidate-hash join), measure each of 32 committed judge
configurations' agreement with the recorded prover outcome, then ask whether a label-free selection signal picks
low-error judges. The cert-judge index exists for only 4 of these configurations, so it is reported descriptively."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import statistics
import subprocess
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import analyze66_r1 as R1  # noqa: E402  (shared helpers: experiment 39 library, logistic fit, AUC)

A = R1.A
EXP = R1.EXP
REPO = R1.REPO
CFG_PATH = EXP / "config_r2.json"
CFG = json.loads(CFG_PATH.read_text())


class Git:
    def __init__(self, path, rev):
        self.path, self.rev, self.provenance = path, rev, {}

    def show(self, name, record=True):
        out = subprocess.run(["git", "-C", self.path, "show", f"{self.rev}:{name}"], capture_output=True)
        if out.returncode:
            raise FileNotFoundError(name)
        if record:
            self.provenance[name] = hashlib.sha256(out.stdout).hexdigest()
        return out.stdout

    def ls(self, prefix):
        return subprocess.check_output(["git", "-C", self.path, "ls-tree", "-r", "--name-only", self.rev, prefix]).decode().split()


def load_outcomes(g):
    """candidate sha256 -> list of (pool, solver, task, y_first_pass, y_gemini, proved_fraction)."""
    by_hash = {}
    e145 = {r["run"]: r for r in csv.DictReader(io.StringIO(g.show(CFG["e145"]).decode()))}
    e158 = {r["run"]: r for r in csv.DictReader(io.StringIO(g.show(CFG["e158"]).decode()))}
    tiny = json.loads(g.show(CFG["tiny_manifest"]))
    for solver, tasks in tiny.items():
        for task, h in tasks.items():
            r = e145.get(f"tiny256|{task}|{solver}")
            gm = e158.get(f"tiny256|{task}|{solver}")
            if r is None:
                continue
            frac = int(r["proved"]) / int(r["k_gold"]) if r["k_gold"] not in ("", "0") and r["proved"] != "" else None
            by_hash.setdefault(h, []).append({"pool": "tiny256", "solver": solver, "task": task, "y": int(r["counted_all5"]),
                                              "y_gemini": int(gm["G"]) if gm and gm.get("G") not in (None, "") else None,
                                              "frac": frac})
    for exp, solver in CFG["core_batches"].items():
        base = f"experiments/{exp}/"
        man = {}
        for name in g.ls(base + "inputs/"):
            if "solver_sha_manifest" in name:
                man.update(json.loads(g.show(name)).get(solver, {}))
        converted = set(CFG["retry_converted_runs"].get(exp, []))
        for r in csv.DictReader(io.StringIO(g.show(base + "lean_entailment/E_LEAN_CHECKED.csv").decode())):
            h = man.get(r["task"])
            if h is None:
                continue
            y = 0 if r["mod"] in converted else int(r["E_lean"])
            frac = int(r["proved"]) / int(r["gold_theorems"]) if r["gold_theorems"] not in ("", "0") and r["proved"] != "" else None
            by_hash.setdefault(h, []).append({"pool": exp[:3], "solver": solver, "task": r["task"], "y": y, "y_gemini": None,
                                              "frac": frac})
    return by_hash


def load_artifacts(g, by_hash):
    arts = []
    prefix = CFG["e106"] + "/inputs/candidates/"
    for name in g.ls(prefix):
        group, fname = name[len(prefix):].split("/")
        if group not in CFG["groups"]:
            continue
        h = hashlib.sha256(g.show(name, record=False)).hexdigest()
        srcs = by_hash.get(h, [])
        ys = {s["y"] for s in srcs}
        assert len(ys) <= 1, f"conflicting outcomes for {name}"
        task = fname[:-5]
        arts.append({"item": f"{group}__{task}", "group": group, "task": task, "sha256": h, "n_sources": len(srcs),
                     "pool": srcs[0]["pool"] if srcs else None, "y": srcs[0]["y"] if srcs else None,
                     "y_gemini": next((s["y_gemini"] for s in srcs if s["y_gemini"] is not None), None),
                     "frac": srcs[0]["frac"] if srcs else None})
    return arts


def load_scores(g, items):
    configs = {}
    for run, spec in CFG["runs"].items():
        rows = [json.loads(line) for line in g.show(f"{CFG['e106']}/runs/{run}/cells.jsonl").decode().splitlines() if line.strip()]
        frames = spec.get("frames") or [None]
        for frame in frames:
            cfgname = run + (f"|{frame}" if frame else "")
            vals = {}
            for r in rows:
                if r.get("item") not in items or r.get("category") != "COMPLETE":
                    continue
                if frame and r.get("frame") != frame:
                    continue
                v = r.get("score") if spec["field"] == "score" else r.get("score_0_5")
                if v is None:
                    continue
                vals.setdefault(r["item"], []).append(float(v) / spec["scale"])
            configs[cfgname] = {"family": spec["family"], "model": spec["model"], "fixed_rubric": spec.get("fixed_rubric", False),
                                "e39_unit": spec.get("e39_unit"),
                                "median": {i: statistics.median(v) for i, v in vals.items()}}
    return configs


def fold_of(task):
    return int(hashlib.sha256((CFG["fold_salt"] + ":" + task).encode()).hexdigest(), 16) % 2


def level1(configs, arts):
    scored = [a for a in arts if a["y"] is not None]
    for name, c in configs.items():
        med = c["median"]
        have = [a for a in scored if a["item"] in med]
        cov = len(have) / len(scored)
        per = []
        for f in (0, 1):
            tr = [a for a in have if fold_of(a["task"]) != f]
            te = [a for a in have if fold_of(a["task"]) == f]
            xs, ys = [med[a["item"]] for a in tr], [a["y"] for a in tr]
            prev = sum(ys) / len(ys)
            if max(xs) - min(xs) > 0:
                b0, b1 = R1.fit_logistic(xs, ys, CFG["map_slope_ridge"])
            else:
                b0, b1 = R1.math.log(prev / (1 - prev)), 0.0
            for a in te:
                s = med[a["item"]]
                q = R1.expit(b0 + b1 * s)
                per.append({"task": a["task"], "y": a["y"], "s": s, "q": q, "e_fit": (q - a["y"]) ** 2,
                            "e_raw": (s - a["y"]) ** 2, "e_const": (prev - a["y"]) ** 2,
                            "y_gemini": a["y_gemini"], "frac": a["frac"]})
        ok = cov + 1e-9 >= CFG["min_criterion_coverage"]
        ys = [r["y"] for r in per]
        ss = [r["s"] for r in per]
        gem = [r for r in per if r["y_gemini"] is not None]
        c["criterion"] = {"coverage": round(cov, 4), "n": len(per), "status": "COMPUTED" if ok else "NOT_COMPUTABLE",
                          "G_P_crossfit": 1 - statistics.mean(r["e_fit"] for r in per) if ok else None,
                          "G_P_raw": 1 - statistics.mean(r["e_raw"] for r in per) if ok else None,
                          "G_P_constant": 1 - statistics.mean(r["e_const"] for r in per) if ok else None,
                          "rank_auc": R1.auc(ss, ys) if ok else None,
                          "rank_spearman": A.spearman(ss, ys) if ok else None,
                          "gemini_prover_auc_tiny256": R1.auc([r["s"] for r in gem], [r["y_gemini"] for r in gem]) if ok and gem else None,
                          "n_gemini": len(gem)}
        c["per"] = per


def consensus(configs, arts):
    """Teacher-assisted label-free signal: Spearman of a configuration's item medians with the mean of every
    configuration from other model families, over all 99 items; no prover outcome is read."""
    items = [a["item"] for a in arts]
    for name, c in configs.items():
        others = [o for o in configs.values() if o["family"] != c["family"]]
        xs, ys = [], []
        for i in items:
            if i in c["median"]:
                vals = [o["median"][i] for o in others if i in o["median"]]
                if vals:
                    xs.append(c["median"][i])
                    ys.append(statistics.mean(vals))
        c["index"] = {"consensus_other_families": A.spearman(xs, ys) if len(xs) >= 10 else None}


def level2(configs, seed, draws):
    us = [dict(config=k, **v) for k, v in configs.items() if v["criterion"]["G_P_crossfit"] is not None
          and v["index"]["consensus_other_families"] is not None]
    x = [u["index"]["consensus_other_families"] for u in us]
    y = [u["criterion"]["G_P_crossfit"] for u in us]
    res = {"units": len(us), "families": len({u["family"] for u in us}), "association": R1.corr_triplet(x, y)}
    rng = random.Random(seed)
    k = sum(1 for _ in range(draws) if A.spearman(rng.sample(x, len(x)), y) >= res["association"]["spearman"] - 1e-12)
    res["permutation_p_one_sided"] = (k + 1) / (draws + 1)
    g = {u["config"]: u["criterion"]["G_P_crossfit"] for u in us}
    chosen = max(us, key=lambda u: (u["index"]["consensus_other_families"], u["config"]))
    oracle = max(us, key=lambda u: g[u["config"]])
    fixed = [g[u["config"]] for u in us if u["fixed_rubric"]]
    res["selection"] = {"picked": chosen["config"], "G_picked": g[chosen["config"]], "oracle": oracle["config"],
                        "G_oracle": g[oracle["config"]], "regret": g[oracle["config"]] - g[chosen["config"]],
                        "G_random_mean": statistics.mean(g.values()), "G_fixed_rubric_mean": statistics.mean(fixed),
                        "G_constant_judge": statistics.mean(u["criterion"]["G_P_constant"] for u in us)}
    fams = sorted({u["family"] for u in us})
    tasks = sorted({r["task"] for u in us for r in u["per"]})
    by_task = {u["config"]: {} for u in us}
    for u in us:
        for r in u["per"]:
            by_task[u["config"]].setdefault(r["task"], []).append(r)
    rho_d, reg_d = [], []
    for _ in range(draws):
        fs = [rng.choice(fams) for _ in fams]
        ts = [rng.choice(tasks) for _ in tasks]
        bu = [u for f in fs for u in us if u["family"] == f]
        gx = [u["index"]["consensus_other_families"] for u in bu]
        gy = [R1.g_from(by_task[u["config"]], ts, "e_fit") for u in bu]
        if len(set(gx)) > 1 and len(set(gy)) > 1:
            rho_d.append(A.spearman(gx, gy))
        gg = list(zip(bu, gy))
        ch = max(gg, key=lambda t: (t[0]["index"]["consensus_other_families"], t[0]["config"]))
        reg_d.append(max(v for _, v in gg) - ch[1])
    q = lambda v: [statistics.quantiles(v, n=40)[0], statistics.quantiles(v, n=40)[-1]] if len(v) > 40 else None
    res["association"]["spearman_ci95_family_task"] = q(rho_d)
    res["association"]["valid_draws"] = len(rho_d)
    res["selection"]["regret_ci95_family_task"] = q(reg_d)
    return res


def main():
    g = Git(str(Path(CFG["veribench_repo"]).expanduser()), CFG["veribench_revision"])
    by_hash = load_outcomes(g)
    arts = load_artifacts(g, by_hash)
    items = {a["item"] for a in arts}
    configs = load_scores(g, items)
    level1(configs, arts)
    consensus(configs, arts)
    e39 = R1.load_e39_units()
    desc4 = []
    for name, c in configs.items():
        if c.get("e39_unit"):
            u = e39[c["e39_unit"]]
            desc4.append({"config": name, "e39_unit": c["e39_unit"], "C_ms_gold": u["indices"]["C_ms_gold"],
                          "G_P_crossfit": c["criterion"]["G_P_crossfit"], "rank_auc": c["criterion"]["rank_auc"]})
    l2 = level2(configs, CFG["seed"], CFG["bootstrap_draws"])
    with_y = [a for a in arts if a["y"] is not None]
    out = {"status": "R2_complete", "retrospective": True, "fresh_test": False,
           "config_sha256": R1.sha(CFG_PATH), "script_sha256": R1.sha(Path(__file__)),
           "veribench_revision": CFG["veribench_revision"], "source_sha256": g.provenance,
           "artifacts": len(arts), "with_outcome": len(with_y), "accepted": sum(a["y"] for a in with_y),
           "tasks": len({a["task"] for a in arts}), "multi_source_artifacts": sum(a["n_sources"] > 1 for a in arts),
           "by_pool": {p: [sum(1 for a in with_y if a["pool"] == p), sum(a["y"] for a in with_y if a["pool"] == p)]
                       for p in sorted({a["pool"] for a in with_y})},
           "gemini_prover_tiny256": [sum(1 for a in with_y if a["y_gemini"] is not None),
                                     sum(a["y_gemini"] for a in with_y if a["y_gemini"] is not None),
                                     sum(1 for a in with_y if a["y_gemini"] is not None and a["y_gemini"] != a["y"])],
           "configs": {k: {kk: v[kk] for kk in ("family", "model", "fixed_rubric", "e39_unit", "criterion", "index")}
                       for k, v in configs.items()},
           "level2_consensus": l2, "cert_judge_index_descriptive_4": desc4,
           "new_model_calls": 0, "cost_usd": 0}
    (EXP / "results").mkdir(exist_ok=True)
    (EXP / "results/r2_natural_target.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("artifacts", "with_outcome", "accepted", "tasks", "by_pool",
                                          "gemini_prover_tiny256", "multi_source_artifacts")}, indent=1))


if __name__ == "__main__":
    main()
