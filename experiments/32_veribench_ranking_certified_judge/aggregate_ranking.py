#!/usr/bin/env python3
"""Aggregate Experiment 32 raw judge cells into the agent-ranking table with item-bootstrap CIs.

Reads results/raw/*.json (status ok), writes results/ranking.json and results/ranking_table.md.
Normalization matches the Claude 3.7 table: per (item, agent) mean over repeats, then mean over
items within a split; the judge here already emits scores in [0,1] (the Claude 3.7 judge emitted
integers in {0..10} divided by 10). No inference, no credentials.
"""
from __future__ import annotations

import json
import statistics as st
from itertools import combinations
from pathlib import Path

import numpy as np

EXP_DIR = Path(__file__).resolve().parent
RAW_DIR = EXP_DIR / "results" / "raw"
OUT_JSON = EXP_DIR / "results" / "ranking.json"
OUT_MD = EXP_DIR / "results" / "ranking_table.md"
CFG = json.loads((EXP_DIR / "judge_config.json").read_text())
MANIFEST = json.loads((EXP_DIR / "inputs_manifest.json").read_text())
AGENTS = ["baseline", "dspy_react", "trace_plus", "trace_plusplus"]
AGENT_NAMES = {"baseline": "Baseline", "dspy_react": "DSPy ReAct", "trace_plus": "Trace+", "trace_plusplus": "Trace++"}
TABLE_SPLITS = [("easy_set", "Easy"), ("cs_set", "CS"), ("real_code", "Real"), ("humaneval_set", "HE"), ("security_6858", "Sec")]
ALL_SPLITS = MANIFEST["splits"]
# Claude 3.7 table (paper_latex/ICLR_2027_submission/main.tex, tab:theorem_quality_table_split)
CLAUDE37 = {
    "baseline":       {"Easy": 0.580, "CS": 0.690, "Real": 0.472, "HE": 0.410, "Sec": 0.347, "Avg": 0.470},
    "dspy_react":     {"Easy": 0.659, "CS": 0.754, "Real": 0.580, "HE": 0.650, "Sec": 0.454, "Avg": 0.615},
    "trace_plus":     {"Easy": 0.342, "CS": 0.680, "Real": 0.592, "HE": 0.573, "Sec": 0.411, "Avg": 0.477},
    "trace_plusplus": {"Easy": 0.620, "CS": 0.756, "Real": 0.504, "HE": 0.645, "Sec": 0.432, "Avg": 0.588},
}
N_BOOT = CFG["bootstrap"]["iterations"]
SEED = CFG["bootstrap"]["seed"]


def load_cells() -> tuple[dict, dict]:
    cells: dict[tuple[str, str], dict[int, float]] = {}
    meta = {"n_ok": 0, "models_requested": set(), "models_observed_header": set(), "attempts": [], "elapsed": [], "tokens_in": 0, "tokens_out": 0,
            "benign_warnings": 0, "reasoning_efforts": set(), "n_failed_files": 0}
    for p in sorted(RAW_DIR.glob("*.json")):
        if p.name.endswith(".failed.json"):
            meta["n_failed_files"] += 1
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("status") != "ok":
            continue
        meta["n_ok"] += 1
        meta["models_requested"].add(d["model_requested"])
        meta["models_observed_header"].add(str(d.get("model_observed_header")))
        meta["reasoning_efforts"].add(d.get("reasoning_effort"))
        meta["attempts"].append(int(d.get("attempt", 1)))
        meta["elapsed"].append(float(d.get("elapsed_seconds", 0)))
        meta["benign_warnings"] += 1 if d.get("benign_warnings") else 0
        u = d.get("usage") or {}
        meta["tokens_in"] += int(u.get("input_tokens", 0)); meta["tokens_out"] += int(u.get("output_tokens", 0))
        cells.setdefault((d["item"], d["agent"]), {})[int(d["repeat"])] = float(d["score"])
    return cells, meta


def per_item_scores(cells, agg: str) -> dict[str, dict[str, float]]:
    """{agent: {item: aggregated score}} using only (item, agent) pairs with all repeats present."""
    out: dict[str, dict[str, float]] = {a: {} for a in AGENTS}
    for (item, agent), reps in cells.items():
        if len(reps) < CFG["n_repeats"]:
            continue
        vals = [reps[k] for k in sorted(reps)]
        out[agent][item] = float(np.mean(vals)) if agg == "mean" else float(np.median(vals))
    return out


def split_of(item: str) -> str:
    return item.split("/", 1)[0]


def complete_items(scores: dict[str, dict[str, float]]) -> list[str]:
    """Items scored for all four agents (paired design)."""
    sets = [set(scores[a]) for a in AGENTS]
    return sorted(set.intersection(*sets)) if all(sets) else []


def table_from_items(scores, items_by_split: dict[str, list[str]], sec_splits: list[str]) -> dict[str, dict[str, float]]:
    tab = {}
    for a in AGENTS:
        row = {}
        for s, label in TABLE_SPLITS:
            its = items_by_split[s] if label != "Sec" else [i for sp in sec_splits for i in items_by_split[sp]]
            row[label] = float(np.mean([scores[a][i] for i in its])) if its else float("nan")
        row["Avg"] = float(np.mean([row[l] for _, l in TABLE_SPLITS]))
        all_items = [i for s in ALL_SPLITS for i in items_by_split[s]]
        row["ItemMean"] = float(np.mean([scores[a][i] for i in all_items]))
        tab[a] = row
    return tab


def ordering(tab: dict[str, dict[str, float]], col: str) -> list[str]:
    return sorted(AGENTS, key=lambda a: -tab[a][col])


def spearman(x, y):
    from scipy.stats import spearmanr
    return float(spearmanr(x, y).correlation)


def kendall(x, y):
    from scipy.stats import kendalltau
    return float(kendalltau(x, y).correlation)


def bootstrap(scores, items, sec_splits, rng) -> dict:
    items_by_split = {s: [i for i in items if split_of(i) == s] for s in ALL_SPLITS}
    point = table_from_items(scores, items_by_split, sec_splits)
    cols = [l for _, l in TABLE_SPLITS] + ["Avg", "ItemMean"]
    samples = {a: {c: [] for c in cols} for a in AGENTS}
    diffs = {(a, b): {c: [] for c in cols} for a, b in combinations(AGENTS, 2)}
    order_counts = {c: {} for c in ["Avg", "ItemMean"]}
    for _ in range(N_BOOT):
        boot = {s: list(rng.choice(its, size=len(its), replace=True)) if its else [] for s, its in items_by_split.items()}
        t = table_from_items(scores, boot, sec_splits)
        for a in AGENTS:
            for c in cols:
                samples[a][c].append(t[a][c])
        for (a, b) in diffs:
            for c in cols:
                diffs[(a, b)][c].append(t[a][c] - t[b][c])
        for c in order_counts:
            key = " > ".join(AGENT_NAMES[a] for a in ordering(t, c))
            order_counts[c][key] = order_counts[c].get(key, 0) + 1
    def ci(v):
        v = np.asarray(v, dtype=float); v = v[np.isfinite(v)]
        return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) else [float("nan")] * 2
    out = {
        "point": point,
        "ci": {a: {c: ci(samples[a][c]) for c in cols} for a in AGENTS},
        "pairwise_diff": {f"{a}-{b}": {c: {"point": point[a][c] - point[b][c], "ci": ci(diffs[(a, b)][c]),
                                          "p_boot_two_sided": float(2 * min(np.mean(np.asarray(diffs[(a, b)][c]) <= 0), np.mean(np.asarray(diffs[(a, b)][c]) >= 0)))}
                                      for c in cols} for (a, b) in diffs},
        "ordering_bootstrap_frequency": {c: dict(sorted(order_counts[c].items(), key=lambda kv: -kv[1])) for c in order_counts},
        "n_items_by_split": {s: len(v) for s, v in items_by_split.items()},
    }
    return out


def main() -> None:
    cells, meta = load_cells()
    rng = np.random.default_rng(SEED)
    result = {
        "schema_version": "exp32_ranking_v1",
        "judge": {"prompt_name": CFG["prompt_name"], "model_requested_by_cli_flag": CFG["model_requested_by_cli_flag"],
                  "models_requested_observed_in_records": sorted(meta["models_requested"]),
                  "model_observed_header_values": sorted(meta["models_observed_header"]),
                  "reasoning_effort": sorted(str(x) for x in meta["reasoning_efforts"]),
                  "certified_configuration_requested": CFG["certified_configuration_requested"],
                  "model_fallback_reason": CFG["model_fallback_reason"]},
        "calls": {"ok_cells": meta["n_ok"], "expected_cells": MANIFEST["n_candidate_rows"] * CFG["n_repeats"],
                  "failed_cell_files": meta["n_failed_files"],
                  "total_cli_invocations_including_retries": int(sum(meta["attempts"])),
                  "cells_needing_retry": int(sum(1 for a in meta["attempts"] if a > 1)),
                  "cells_with_benign_skills_warning": meta["benign_warnings"],
                  "mean_elapsed_seconds_per_ok_call": float(st.mean(meta["elapsed"])) if meta["elapsed"] else None,
                  "input_tokens_total": meta["tokens_in"], "output_tokens_total": meta["tokens_out"],
                  "provider_api_spend_usd": 0.0},
        "normalization": "score in [0,1] as emitted; mean over 3 repeats per (item, agent); mean over items per split; Avg = macro-average over the five table splits; ItemMean = mean over all scored items (six splits)",
        "claude37_table": CLAUDE37,
        "analyses": {},
    }
    for agg in ("mean", "median"):
        scores = per_item_scores(cells, agg)
        items = complete_items(scores)
        if not items:
            result["analyses"][agg] = {"status": "no complete items yet"}
            continue
        for sec_name, sec_splits in (("sec_6858_only", ["security_6858"]), ("sec_6858_plus_python", ["security_6858", "security_python"])):
            b = bootstrap(scores, items, sec_splits, np.random.default_rng(SEED))
            ords = {c: [AGENT_NAMES[a] for a in ordering(b["point"], c)] for c in ["Avg", "ItemMean"] + [l for _, l in TABLE_SPLITS]}
            c37_order = [AGENT_NAMES[a] for a in sorted(AGENTS, key=lambda a: -CLAUDE37[a]["Avg"])]
            new_avg = [b["point"][a]["Avg"] for a in AGENTS]; old_avg = [CLAUDE37[a]["Avg"] for a in AGENTS]
            agreement = {
                "claude37_avg_order": c37_order,
                "new_avg_order": ords["Avg"],
                "identical_avg_order": ords["Avg"] == c37_order,
                "spearman_avg_4_agents": spearman(new_avg, old_avg),
                "kendall_avg_4_agents": kendall(new_avg, old_avg),
                "per_split_identical_order": {l: ords[l] == [AGENT_NAMES[a] for a in sorted(AGENTS, key=lambda a: -CLAUDE37[a][l])] for _, l in TABLE_SPLITS},
                "per_split_spearman": {l: spearman([b["point"][a][l] for a in AGENTS], [CLAUDE37[a][l] for a in AGENTS]) for _, l in TABLE_SPLITS},
                "cell_spearman_20": spearman([b["point"][a][l] for a in AGENTS for _, l in TABLE_SPLITS], [CLAUDE37[a][l] for a in AGENTS for _, l in TABLE_SPLITS]),
            }
            result["analyses"][f"{agg}__{sec_name}"] = {"n_paired_items": len(items), **b, "orderings": ords, "agreement_with_claude37": agreement}
    OUT_JSON.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")

    # Markdown table (primary: mean over repeats, Sec = security_6858 only)
    key = "mean__sec_6858_only"
    lines = [f"# Experiment 32 ranking table — judge {CFG['prompt_name']} on `{CFG['model_requested_by_cli_flag']}` (effort {CFG['reasoning_effort']}), 3 repeats", ""]
    lines.append(f"Cells: {meta['n_ok']}/{MANIFEST['n_candidate_rows'] * CFG['n_repeats']} ok; CLI invocations incl. retries: {int(sum(meta['attempts']))}; provider API spend: $0.")
    if key in result["analyses"] and "point" in result["analyses"][key]:
        A = result["analyses"][key]
        lines += ["", f"Paired items: {A['n_paired_items']} (per split: {A['n_items_by_split']}). 95% percentile bootstrap over items within split, {N_BOOT} draws, seed {SEED}.", "",
                  "| Agent | Easy | CS | Real | HE | Sec | **Avg** (95% CI) | ItemMean (95% CI) |", "|---|---|---|---|---|---|---|---|"]
        for a in AGENTS:
            p = A["point"][a]; c = A["ci"][a]
            cellf = lambda l: f"{p[l]:.3f} [{c[l][0]:.3f}, {c[l][1]:.3f}]"
            lines.append(f"| {AGENT_NAMES[a]} | " + " | ".join(f"{p[l]:.3f}" for _, l in TABLE_SPLITS) + f" | **{p['Avg']:.3f}** [{c['Avg'][0]:.3f}, {c['Avg'][1]:.3f}] | {cellf('ItemMean')} |")
        lines += ["", "Per-split 95% CIs:", "", "| Agent | " + " | ".join(l for _, l in TABLE_SPLITS) + " |", "|---|" + "---|" * len(TABLE_SPLITS)]
        for a in AGENTS:
            c = A["ci"][a]
            lines.append(f"| {AGENT_NAMES[a]} | " + " | ".join(f"[{c[l][0]:.3f}, {c[l][1]:.3f}]" for _, l in TABLE_SPLITS) + " |")
        ag = A["agreement_with_claude37"]
        lines += ["", f"Ordering by Avg: {' > '.join(ag['new_avg_order'])}; Claude 3.7 table: {' > '.join(ag['claude37_avg_order'])}; identical: {ag['identical_avg_order']}; Spearman over the four Avg values: {ag['spearman_avg_4_agents']:.3f}; Spearman over the 20 split cells: {ag['cell_spearman_20']:.3f}.",
                  "", "Bootstrap frequency of each full Avg ordering:", ""]
        for k, v in list(A["ordering_bootstrap_frequency"]["Avg"].items())[:6]:
            lines.append(f"- {k}: {v / N_BOOT:.3f}")
        lines += ["", "Pairwise Avg differences (point, 95% CI, two-sided bootstrap p):", ""]
        for k, v in A["pairwise_diff"].items():
            d = v["Avg"]; lines.append(f"- {k}: {d['point']:+.3f} [{d['ci'][0]:+.3f}, {d['ci'][1]:+.3f}], p={d['p_boot_two_sided']:.3f}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_MD.read_text())


if __name__ == "__main__":
    main()
