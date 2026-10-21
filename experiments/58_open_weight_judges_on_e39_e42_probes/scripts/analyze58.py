#!/usr/bin/env python3
"""TLDR: Experiment 58's frozen analysis (PROTOCOL.md sections 5-8), no model calls. Reads the harvests the local judges
wrote (<run>/harvest/e39 and /e42, experiment 39's schema) and reports: the C_ms_gold gate with E39's criterion and gates
(plain permutation, plus model-clustered permutation and model-cluster bootstrap), PTI_v0 and TI_var with E39's frozen
normalization, every other E39 candidate (secondary), the E42 semantic screen, scale-within-family curves, the exploratory
TVD-MI covariates (repeat and deletion variants) and the Qwen3.6 bridge against E39's hosted cells.

Usage: analyze58.py --run ~/e58/runs/main [--out results] [--draws 10000] [--e42-draws 10000]"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]
import e58                                                    # noqa: E402

GATE_RHO, GATE_P = 0.45, 0.05                                 # experiment 39's gates, unchanged
CLUSTER_SEED = 58
E39_SELECTION_SHA = "25cb2aabef5c8881792819926060c87028bedd05f7257c62289ef67658dd2a3f"
SELECTED = "C_ms_gold"
MIN_TASK_COVERAGE = 0.80                                      # a TVD-MI task-mean needs 80% of declared tasks/ladders


def load_items() -> list[dict]:
    return e58.read_json(e58.RESULTS / "criterion_items.json")["items"]


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def cluster_blocks(units: list[dict], index: str):
    """{model_key: {prompt_key: (x, y)}} for units with both numbers; only models with every prompt present are kept."""
    blocks: dict[str, dict[str, tuple[float, float]]] = {}
    for u in units:
        x, y = u["indices"].get(index), (u["criteria"]["heldout"] or {}).get("spearman")
        if x is not None and y is not None:
            blocks.setdefault(u["model_key"], {})[u["prompt_key"]] = (x, y)
    return {m: b for m, b in blocks.items() if set(b) == set(e58.PROMPT_ORDER)}


def clustered_stats(A, units: list[dict], index: str, draws: int, seed: int = CLUSTER_SEED) -> dict:
    """Model-clustered permutation (whole models' criterion vectors are permuted across models, matched by prompt) and
    model-cluster bootstrap CI of the unit-level Spearman. One-sided (positive association), (k+1)/(draws+1)."""
    blocks = cluster_blocks(units, index)
    models = sorted(blocks)
    out = {"index": index, "n_models": len(models), "models": models, "spearman": None, "permutation_p": None, "ci": None}
    if len(models) < 3:
        return out
    prompts = e58.PROMPT_ORDER

    def flat(xmodels, ymodels):
        xs = [blocks[a][p][0] for a in xmodels for p in prompts]
        ys = [blocks[b][p][1] for b in ymodels for p in prompts]
        return xs, ys

    x0, y0 = flat(models, models)
    obs = A.spearman(x0, y0)
    out["spearman"] = obs
    if obs is None:
        return out
    rng = random.Random(seed)
    k = 0
    for _ in range(draws):
        perm = models[:]
        rng.shuffle(perm)
        xs, ys = flat(models, perm)
        v = A.spearman(xs, ys)
        if v is not None and v >= obs - 1e-12:
            k += 1
    out["permutation_p"] = (k + 1) / (draws + 1)
    vals = []
    for _ in range(draws):
        pick = [rng.choice(models) for _ in models]
        xs = [blocks[a][p][0] for a in pick for p in prompts]
        ys = [blocks[a][p][1] for a in pick for p in prompts]
        v = A.spearman(xs, ys)
        if v is not None:
            vals.append(v)
    vals.sort()
    if vals:
        out["ci"] = {"lo": vals[int(0.025 * (len(vals) - 1))], "hi": vals[int(0.975 * (len(vals) - 1))], "valid_draws": len(vals)}
    return out


def tvd_mi(sc, harvest: dict, probes: dict) -> dict:
    """Both TVD-MI variants for one unit (exploratory). Repeat TVD: per task over criterion-item candidates with all three
    repeats. Deletion TVD: per gold-deletion ladder, identity as level 0."""
    from cert_judge import information_properties as IP        # imported by analysis_lib's path setup
    by_task: dict[str, dict[str, dict[int, float]]] = {}
    tasks = set()
    for c in harvest["cells"]:
        if c["kind"] == "crit":
            tasks.add(c["task"])
            if c["status"] in ("measured", "deterministic") and c.get("score") is not None:
                by_task.setdefault(c["task"], {}).setdefault(c["item"], {})[int(c["repeat"])] = float(c["score"])
    rep = []
    for t in sorted(by_task):
        complete, _ = IP.complete_repeat_candidates(by_task[t])
        if len(complete) >= 2:
            rep.append(IP.repeat_tvd_task(complete))
    repeat_val = mean(rep) if tasks and len(rep) / len(tasks) + 1e-9 >= MIN_TASK_COVERAGE else None
    ladders: dict[str, list[int]] = {}
    for r in probes.get("bm_gold", []):
        ladders.setdefault(r["key"], []).append(r["level"])
    dele = []
    for key, levels in ladders.items():
        reps = {0: sc.repeats("ident", key, 0)}
        reps.update({lv: sc.repeats("bm_gold", key, lv) for lv in sorted(levels)})
        reps = {lv: r for lv, r in reps.items() if len(r) >= 2}
        if len(reps) >= 2:
            dele.append(IP.deletion_tvd_task(reps))
    ok = ladders and len(dele) / len(ladders) + 1e-9 >= MIN_TASK_COVERAGE
    return {"repeat_tvd": repeat_val, "n_repeat_tasks": len(rep), "n_tasks": len(tasks),
            "deletion_tvd_value": mean([d["value"] for d in dele]) if ok else None,
            "deletion_tvd_information": mean([d["information"] for d in dele]) if ok else None,
            "n_ladders": len(dele), "n_declared_ladders": len(ladders)}


def build_units(A, run: Path, items: list[dict], manifest: dict, draws: int = 10000) -> tuple[list[dict], dict]:
    """draws: bootstrap draws of the held-out criterion's interval (the gated figure); the val-only and test-only criteria are
    descriptive and use 500 draws (their intervals are not reported)."""
    probes = A.valid_probes(manifest)
    units = []
    for path in sorted((run / "harvest" / "e39").glob("*.json")):
        h = e58.read_json(path)
        sc = A.Scores(h)
        crit = {"heldout": A.criterion(sc, items, ("val", "test"), draws=draws), "test_items": A.criterion(sc, items, ("test",), draws=500),
                "val_items": A.criterion(sc, items, ("val",), draws=500)}
        comps = A.components(sc, probes)
        pti = A.pti_v0_frozen(sc, probes)
        raw = A.ti_var_raw(sc, probes)
        norm = e58.read_json(e58.E39_DIR / "results/SELECTION.json")["ti_var_norm"]
        indices = {"PTI_v0_frozen": pti["value"],
                   "TI_var_trainnorm": A.ti_var(raw, {k: tuple(v) if isinstance(v, list) else v for k, v in norm.items()}) if raw else None}
        for name in A.CANDIDATES:
            if A.CANDIDATES[name][0] != "frozen":
                indices[name] = A.candidate_value(name, comps, indices)
        units.append({"config": h["config"], "model_key": h["family"], "prompt_key": h["config"].split("|")[1], "model_family": h.get("model_family"),
                      "params_b": h.get("params_b"), "status_counts": h["status_counts"], "criteria": crit,
                      "components": {k: v["value"] for k, v in comps.items()}, "pti_v0": {"status": pti["status"], "value": pti["value"]},
                      "ti_var_raw": raw, "indices": indices, "tvd_mi": tvd_mi(sc, h, probes)})
    return units, {"ti_var_norm": e58.read_json(e58.E39_DIR / "results/SELECTION.json")["ti_var_norm"]}


def gate_block(A, units: list[dict], draws: int) -> dict:
    plain = A.association(units, SELECTED, "heldout", draws=draws, seed=39)
    clus = clustered_stats(A, units, SELECTED, draws)
    rho, p = plain["spearman"], plain["permutation_p"]
    plain_pass = bool(rho is not None and p is not None and rho >= GATE_RHO and p < GATE_P)
    cl_pass = bool(clus["spearman"] is not None and clus["permutation_p"] is not None and clus["spearman"] >= GATE_RHO
                   and clus["permutation_p"] < GATE_P)
    return {"index": SELECTED, "gate": {"spearman": GATE_RHO, "permutation_p": GATE_P}, "plain": plain, "plain_PASS": plain_pass,
            "model_clustered": clus, "model_clustered_PASS": cl_pass,
            "verdict": f"plain {'PASS' if plain_pass else 'FAIL'}; model-clustered {'PASS' if cl_pass else 'FAIL'}"}


def secondary_block(A, units: list[dict], draws: int) -> dict:
    out = {"all_candidates_test_only": {n: A.association(units, n, "heldout", with_uncertainty=False) for n in A.CANDIDATES},
           "always_reported": {n: A.association(units, n, "heldout", draws=draws, seed=39) for n in ("PTI_v0_frozen", "TI_var_trainnorm")}}
    out["pti_v0_status_counts"] = {}
    for u in units:
        s = u["pti_v0"]["status"]
        out["pti_v0_status_counts"][s] = out["pti_v0_status_counts"].get(s, 0) + 1
    out["by_prompt_C_ms_gold"] = {p: A.association([u for u in units if u["prompt_key"] == p], SELECTED, "heldout", with_uncertainty=False)
                                  for p in e58.PROMPT_ORDER}
    out["by_model_family_C_ms_gold"] = {f: A.association([u for u in units if u["model_family"] == f], SELECTED, "heldout", with_uncertainty=False)
                                        for f in sorted({u["model_family"] for u in units if u["model_family"]})}
    return out


def scale_curves(units: list[dict]) -> dict:
    """Descriptive: per model family, each model's criterion and C_ms_gold per prompt and averaged over prompts."""
    fam: dict[str, dict] = {}
    for u in units:
        m = fam.setdefault(u["model_family"], {}).setdefault(u["model_key"], {"params_b": u["params_b"], "criterion": {}, "C_ms_gold": {}})
        m["criterion"][u["prompt_key"]] = (u["criteria"]["heldout"] or {}).get("spearman")
        m["C_ms_gold"][u["prompt_key"]] = u["indices"].get(SELECTED)
    for f, models in fam.items():
        for m in models.values():
            m["criterion_mean"] = mean(m["criterion"].values())
            m["C_ms_gold_mean"] = mean(m["C_ms_gold"].values())
            m["n_prompts_with_criterion"] = sum(v is not None for v in m["criterion"].values())
        fam[f] = dict(sorted(models.items(), key=lambda kv: kv[1]["params_b"]))
    return fam


def tvd_block(A, units: list[dict]) -> dict:
    out = {"note": "exploratory, not gated; does not freeze experiment 49 (W-365 is Brando's decision)"}
    for name, getter in (("repeat_tvd", lambda u: u["tvd_mi"]["repeat_tvd"]), ("deletion_tvd_value", lambda u: u["tvd_mi"]["deletion_tvd_value"]),
                         ("deletion_tvd_information", lambda u: u["tvd_mi"]["deletion_tvd_information"])):
        pairs = [(getter(u), (u["criteria"]["heldout"] or {}).get("spearman")) for u in units]
        pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
        out[name] = {"n_units": len(pairs), "spearman": A.spearman([a for a, _ in pairs], [b for _, b in pairs]) if len(pairs) >= A.MIN_UNITS else None}
    return out


def e42_block(run: Path, A, units: list[dict], draws: int) -> dict:
    d = run / "harvest" / "e42"
    if not d.exists():
        return {"status": "no E42 harvests"}
    e42, _, _ = e58.e42_modules()
    sys.path.insert(0, str(e58.E42_DIR / "scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("e42_analyze", e58.E42_DIR / "scripts/analyze.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rows = mod.valid_rows(e58.read_json(e58.E42_DIR / "results/semantic_probe_manifest.json"))
    labels = mod.audit_labels()
    per = [mod.screen_one(e58.read_json(p), rows, draws, labels) for p in sorted(d.glob("*.json"))]
    crit = {u["config"]: (u["criteria"]["heldout"] or {}).get("spearman") for u in units}
    verdicts = {v: sum(u["verdict"] == v for u in per) for v in ("PASS", "FAIL", "NOT_COMPUTABLE")}
    assoc = {}
    for fam in ("vacuity", "weakening", "overconstraint", "formatting"):
        pairs = [(u["metrics"][fam]["value"], crit.get(u["config"])) for u in per if u["metrics"].get(fam, {}).get("value") is not None]
        pairs = [(a, b) for a, b in pairs if b is not None]
        assoc[fam] = {"n_units": len(pairs), "spearman_with_criterion": A.spearman([a for a, _ in pairs], [b for _, b in pairs]) if len(pairs) >= A.MIN_UNITS else None}
    return {"rule": e42.PASS_DIRECTIONAL, "verdicts": verdicts, "n_units": len(per), "descriptive_association": assoc, "units": per}


def bridge_block(A, run: Path, units: list[dict]) -> dict:
    out = {"local": "qwen36_27b", "hosted": "qwen36 (alibaba/qwen3.6-27b, experiment 39)", "gated": False, "prompts": {}}
    by_cfg = {u["config"]: u for u in units}
    for p in e58.PROMPT_ORDER:
        local_p = run / "harvest" / "e39" / f"{e58.fs(e58.config_id('qwen36_27b', p))}.json"
        host_p = e58.E39_DIR / f"results/harvest/qwen36__{p}.json"
        if not local_p.exists() or not host_p.exists():
            out["prompts"][p] = {"status": "missing"}
            continue
        lh, hh = e58.read_json(local_p), e58.read_json(host_p)
        ls = {c["cell"]: c["score"] for c in lh["cells"] if c["status"] == "measured" and c.get("score") is not None}
        hs = {c["cell"]: c["score"] for c in hh["cells"] if c["status"] == "measured" and c.get("score") is not None}
        shared = sorted(set(ls) & set(hs))
        a, b = [ls[c] for c in shared], [hs[c] for c in shared]
        hosted = A.Scores(hh)
        manifest = e58.read_json(e58.E39_DIR / "results/probe_manifest.json")
        hosted_crit = A.criterion(hosted, load_items(), ("val", "test"))
        hosted_cms = A.components(hosted, A.valid_probes(manifest))["ms_gold"]["value"]
        u = by_cfg.get(e58.config_id("qwen36_27b", p))
        out["prompts"][p] = {"n_shared_measured_cells": len(shared),
                             "cell_spearman": A.spearman(a, b) if len(shared) >= 3 else None,
                             "exact_agreement": (sum(abs(x - y) < 1e-9 for x, y in zip(a, b)) / len(shared)) if shared else None,
                             "mean_abs_diff": (sum(abs(x - y) for x, y in zip(a, b)) / len(shared)) if shared else None,
                             "criterion_local": (u["criteria"]["heldout"] or {}).get("spearman") if u else None,
                             "criterion_hosted": hosted_crit["spearman"],
                             "C_ms_gold_local": u["indices"].get(SELECTED) if u else None, "C_ms_gold_hosted": hosted_cms,
                             "status_counts_local": lh["status_counts"], "status_counts_hosted": hh["status_counts"]}
    return out


def ci_str(ci) -> str:
    return "n/a" if not ci or ci.get("lo") is None else f"{ci['lo']:.3f} to {ci['hi']:.3f}"


def fmt(v, nd=3):
    return "n/a" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def write_report(path: Path, res: dict) -> None:
    g = res["gate"]
    pl, cl = g["plain"], g["model_clustered"]
    lines = ["# Experiment 58 results: open-weight judges on experiment 39's frozen probes", "",
             f"**TLDR:** {g['verdict']}. `C_ms_gold` vs the held-out criterion over {pl['n_units']} units: Spearman {fmt(pl['spearman'])} "
             f"(permutation p {fmt(pl['permutation_p'], 4)}); model-clustered p {fmt(cl['permutation_p'], 4)} over {cl['n_models']} models.", "",
             "## Gate (E39's: rho >= 0.45 and p < 0.05)", "",
             "| Test | n | Spearman | p | 95% CI | Gate |", "|---|---:|---:|---:|---|---|",
             f"| plain permutation | {pl['n_units']} | {fmt(pl['spearman'])} | {fmt(pl['permutation_p'], 4)} | {ci_str(pl['ci'])} | {'PASS' if g['plain_PASS'] else 'FAIL'} |",
             f"| model-clustered | {cl['n_models']} models | {fmt(cl['spearman'])} | {fmt(cl['permutation_p'], 4)} | {ci_str(cl['ci'])} | {'PASS' if g['model_clustered_PASS'] else 'FAIL'} |", "",
             "## Always reported", "", "| Index | n | Spearman | p |", "|---|---:|---:|---:|"]
    for n, a in res["secondary"]["always_reported"].items():
        lines.append(f"| {n} | {a['n_units']} | {fmt(a['spearman'])} | {fmt(a['permutation_p'], 4)} |")
    lines += ["", f"PTI_v0 status counts: {res['secondary']['pti_v0_status_counts']}", "", "## Scale within family (descriptive)", "",
              "| Family | Model | Params (B) | Criterion (mean over prompts) | C_ms_gold (mean) |", "|---|---|---:|---:|---:|"]
    for f, models in res["scale_curves"].items():
        for m, v in models.items():
            lines.append(f"| {f} | {m} | {v['params_b']} | {fmt(v['criterion_mean'])} | {fmt(v['C_ms_gold_mean'])} |")
    lines += ["", "## E42 semantic screen", "", f"Verdicts: {res['e42'].get('verdicts')}; descriptive association with the criterion: {res['e42'].get('descriptive_association')}",
              "", "## TVD-MI (exploratory; does not freeze E49, W-365 is Brando's call)", "", "| Variant | n | Spearman with criterion |", "|---|---:|---:|"]
    for k, v in res["tvd_mi"].items():
        if isinstance(v, dict):
            lines.append(f"| {k} | {v['n_units']} | {fmt(v['spearman'])} |")
    lines += ["", "## Bridge: local Qwen3.6-27B vs hosted (E39)", "", "| Prompt | shared cells | cell Spearman | exact agree | crit local | crit hosted | C_ms_gold local | hosted |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for p, v in res["bridge"]["prompts"].items():
        if "n_shared_measured_cells" in v:
            lines.append(f"| {p} | {v['n_shared_measured_cells']} | {fmt(v['cell_spearman'])} | {fmt(v['exact_agreement'])} | {fmt(v['criterion_local'])} | {fmt(v['criterion_hosted'])} | {fmt(v['C_ms_gold_local'])} | {fmt(v['C_ms_gold_hosted'])} |")
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=e58.RESULTS)
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--e42-draws", type=int, default=10000)
    args = ap.parse_args()
    if e58.sha_file(e58.E39_DIR / "results/SELECTION.json") != E39_SELECTION_SHA:
        raise SystemExit("STOP: experiment 39's SELECTION.json is not the frozen file named in PROTOCOL.md")
    A = e58.analysis_lib()
    manifest = e58.read_json(e58.E39_DIR / "results/probe_manifest.json")
    items = load_items()
    units, meta = build_units(A, args.run, items, manifest, args.draws)
    res = {"written_utc": e58.stamp(), "experiment": e58.EXPERIMENT, "run": str(args.run), "n_units": len(units), **meta,
           "gate": gate_block(A, units, args.draws), "secondary": secondary_block(A, units, args.draws), "scale_curves": scale_curves(units),
           "tvd_mi": tvd_block(A, units), "e42": e42_block(args.run, A, units, args.e42_draws), "bridge": bridge_block(A, args.run, units),
           "units": units}
    e58.write_json(args.out / "ANALYSIS.json", res)
    write_report(args.out / "RESULTS_open_weight_judges.md", res)
    print(json.dumps({"n_units": len(units), "verdict": res["gate"]["verdict"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
