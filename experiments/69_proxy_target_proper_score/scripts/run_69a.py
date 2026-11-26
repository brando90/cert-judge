#!/usr/bin/env python3
"""Experiment 69A: zero-spend proper-score selection. See PREREG.md. No model calls."""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
sys.path.insert(0, str(ROOT / "experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/scripts"))
import metrics as M  # noqa: E402

B = 2000
SEED = 69
MIN_POOL = 8
EXPECTED = {"T05": 100, "T08": 100, "T12": 30, "T06": 16, "V04": 3, "V02": 1}

FAM = {
    "Codex": (
        ROOT / "experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/detail_rows.csv",
        ROOT / "experiments/archive/04_veribench_validation/results_exp28_varaware_codex_avg_newindex/judge_trust_vector.csv",
    ),
    "Claude Opus": (
        ROOT / "experiments/archive/04_veribench_validation/results_exp16_opus47_r3_median/detail_rows.csv",
        ROOT / "experiments/archive/04_veribench_validation/results_exp28_varaware_opus_avg_newindex/judge_trust_vector.csv",
    ),
    "Qwen3-Coder": (
        ROOT / "experiments/archive/13_qwen_replication_exp16_exp19/results/exp16_qwen_r3_median/detail_rows.csv",
        ROOT / "experiments/archive/04_veribench_validation/results_exp28_varaware_qwen_avg/judge_trust_vector.csv",
    ),
}
HL = ROOT / "experiments/human_labels"
E39 = ROOT / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results"
MARGIN = ROOT / "experiments/archive/50_semantic_effect_margin_cached_judge_selection_train_val_test/results/configuration_overview.json"
SNAP = EXP / "data/cert-judge-data/ttj-exp09-live-sync-2026-11-26/ratings"
E39_PROXIES = ("C_ms_gold", "TI_var_trainnorm", "PTI_v0_frozen", "C_bm_gold", "semantic_margin_train")


def success_rule(diff_const_mean, diff_const_lo, diff_const_hi, regret_lo, regret_hi) -> bool:
    """Literal PREREG rule. Lower RPS is better, so beating CONST needs a negative difference."""
    beats_const = diff_const_mean < 0 and diff_const_hi < 0
    regret_excludes_0 = regret_hi < 0 or regret_lo > 0
    return bool(beats_const and regret_excludes_0)


def boot_mean(values: np.ndarray, seed: int) -> tuple[float, float, float]:
    x = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    draws = x[rng.integers(0, len(x), size=(B, len(x)))].mean(axis=1)
    return float(x.mean()), float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def qwk(y1: list[int], y2: list[int], k: int = 6) -> float:
    obs = np.zeros((k, k), dtype=float)
    for a, b in zip(y1, y2):
        obs[int(a), int(b)] += 1.0
    obs /= obs.sum()
    r, c = obs.sum(1), obs.sum(0)
    exp = np.outer(r, c)
    w = np.array([[((i - j) / (k - 1)) ** 2 for j in range(k)] for i in range(k)], dtype=float)
    den = float((w * exp).sum())
    return float("nan") if den == 0 else float(1.0 - (w * obs).sum() / den)


def laplace_from_ratings(ratings: list[int], alpha: float = 0.5) -> np.ndarray:
    c = np.zeros(6, dtype=float)
    for y in ratings:
        c[int(y)] += 1.0
    q = c + alpha
    return q / q.sum()


def load_hvb() -> dict[tuple[str, str], list[int]]:
    paths = [
        HL / "participant1_data_correct_prompt.tsv",
        HL / "participant2_data_pass_1.tsv",
        HL / "participant3_data_pass_1.tsv",
        HL / "participant4_data_pass_1.tsv",
        HL / "participant5_data_pass_1.tsv",
    ]
    bags: dict[tuple[str, str], list[int]] = defaultdict(list)
    for path in paths:
        with path.open() as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                score = row["human_score_0_5"].strip()
                gold, cand = row["gold_file"].strip(), row["candidate_file"].strip()
                if gold and cand and score != "":
                    bags[(gold, cand)].append(int(round(float(score))))
    return {key: vals for key, vals in bags.items() if len(vals) >= 4}


def load_paper() -> dict[str, dict]:
    judges: dict[str, dict] = {}
    for family, (detail_path, ti_path) in FAM.items():
        ti = {row["judge_id"]: float(row["TI_variance_aware"]) for row in csv.DictReader(ti_path.open())}
        detail: dict[str, dict[tuple[str, str], list[float]]] = defaultdict(dict)
        with detail_path.open() as handle:
            for row in csv.DictReader(handle):
                if row["row_type"] != "human_eval_union":
                    continue
                gold, cand = row["item_key"].split("::", 1)
                detail[row["judge_id"]][(gold, cand)] = [float(x) for x in json.loads(row["repeat_scores"])]
        for judge_id, scores in detail.items():
            judges[judge_id] = {"family": family, "pool": "paper", "TI_var": ti.get(judge_id), "scores": scores}
    return judges


def load_e39_indices() -> dict[str, dict]:
    units = []
    for name in ("units_train_val.json", "units_test.json"):
        units.extend(json.loads((E39 / name).read_text())["units"])
    margin = json.loads(MARGIN.read_text())["configs"]
    out = {}
    for unit in units:
        cfg = unit["config"]
        idx = dict(unit["indices"])
        sm = margin.get(cfg, {}).get("properties", {}).get("train", {}).get("semantic_margin")
        idx["semantic_margin_train"] = float(sm["value"]) if sm and sm.get("status") == "COMPUTED" else None
        out[cfg] = {"split": unit["split"], "kind": unit["kind"], "family": unit["family"], "indices": idx}
    return out


def load_e39_scores(needed: set[str]) -> dict[str, dict[str, list[float]]]:
    out: dict[str, dict[str, list[float]]] = {}
    for path in sorted((E39 / "harvest").glob("*.json")):
        data = json.loads(path.read_text())
        buckets: dict[str, list[float]] = defaultdict(list)
        for cell in data["cells"]:
            if cell.get("kind") != "crit" or cell.get("score") is None:
                continue
            if cell.get("status") not in ("measured", "deterministic"):
                continue
            if cell["item"] in needed:
                buckets[cell["item"]].append(float(cell["score"]))
        out[data["config"]] = dict(buckets)
    return out


def artifact_losses(probs: np.ndarray, ratings: list[int]) -> tuple[float, float, float]:
    return M.rps_item(probs, ratings), M.ce_item(probs, ratings), M.tvd_item(probs, ratings)


def judge_probs(repeats: list[float]) -> np.ndarray:
    return M.binned_repeats_to_probs(repeats, alpha=0.5)


def build_panel(artifacts: list[tuple[str, str]], ratings: dict, score_map: dict[tuple[str, str], list[float]]) -> dict | None:
    covered = [key for key in artifacts if key in score_map and score_map[key]]
    if len(covered) < len(artifacts):
        return None
    probs = np.vstack([judge_probs(score_map[key]) for key in artifacts])
    rps, ce, tvd, means = [], [], [], []
    for i, key in enumerate(artifacts):
        a, b, c = artifact_losses(probs[i], ratings[key])
        rps.append(a)
        ce.append(b)
        tvd.append(c)
        means.append(5.0 * float(np.median(score_map[key])))
    return {
        "rps": np.asarray(rps),
        "ce": np.asarray(ce),
        "tvd": np.asarray(tvd),
        "judge_05": np.asarray(means),
        "human_mean": np.asarray([float(np.mean(ratings[key])) for key in artifacts]),
    }


def loto_selection(artifacts, tasks, ratings, judges: dict[str, dict], proxy_key: str) -> dict:
    """judges[name] = {proxy, rps, ce, tvd, judge_05, human_mean} arrays aligned to artifacts."""
    names = sorted(judges)
    task_ids = sorted(set(tasks))
    by_task = {t: np.array([i for i, task in enumerate(tasks) if task == t]) for t in task_ids}
    proxy_of = {name: judges[name]["proxy"] for name in names}
    proxy_name = max(names, key=lambda name: (proxy_of[name], name))

    const_rps, const_ce, const_tvd = [], [], []
    proxy_rps, proxy_ce, proxy_tvd = [], [], []
    best_rps, best_ce, best_tvd = [], [], []
    chosen_best = []
    for task in task_ids:
        hold = by_task[task]
        train = np.array([i for i, t in enumerate(tasks) if t != task])
        train_ratings = [y for i in train for y in ratings[artifacts[i]]]
        q = laplace_from_ratings(train_ratings)
        cr, cc, ct = [], [], []
        for i in hold:
            a, b, c = artifact_losses(q, ratings[artifacts[i]])
            cr.append(a)
            cc.append(b)
            ct.append(c)
        const_rps.append(float(np.mean(cr)))
        const_ce.append(float(np.mean(cc)))
        const_tvd.append(float(np.mean(ct)))
        best_name = min(names, key=lambda name: (float(judges[name]["rps"][train].mean()), name))
        chosen_best.append(best_name)
        for dest, src in (
            (proxy_rps, judges[proxy_name]["rps"]),
            (proxy_ce, judges[proxy_name]["ce"]),
            (proxy_tvd, judges[proxy_name]["tvd"]),
        ):
            dest.append(float(src[hold].mean()))
        best_rps.append(float(judges[best_name]["rps"][hold].mean()))
        best_ce.append(float(judges[best_name]["ce"][hold].mean()))
        best_tvd.append(float(judges[best_name]["tvd"][hold].mean()))

    def pack(proxy_vec, base_vec, seed):
        diff = np.asarray(proxy_vec) - np.asarray(base_vec)
        mean, lo, hi = boot_mean(diff, seed)
        return {"diff": mean, "lo": lo, "hi": hi}

    rows = []
    for name in names:
        rows.append({
            "judge": name,
            "proxy": proxy_of[name],
            "loto_rps": float(np.mean([judges[name]["rps"][by_task[t]].mean() for t in task_ids])),
            "loto_ce": float(np.mean([judges[name]["ce"][by_task[t]].mean() for t in task_ids])),
            "loto_tvd": float(np.mean([judges[name]["tvd"][by_task[t]].mean() for t in task_ids])),
            "spearman": M.spearman_corr(judges[name]["judge_05"], judges[name]["human_mean"]),
            "pearson": M.pearson_corr(judges[name]["judge_05"], judges[name]["human_mean"]),
        })
    rps_c = pack(proxy_rps, const_rps, SEED)
    rps_b = pack(proxy_rps, best_rps, SEED + 1)
    return {
        "n_judges": len(names),
        "proxy": proxy_key,
        "selected": proxy_name,
        "selected_proxy": proxy_of[proxy_name],
        "best_on_val_by_task": chosen_best,
        "rps_proxy": float(np.mean(proxy_rps)),
        "rps_const": float(np.mean(const_rps)),
        "rps_best": float(np.mean(best_rps)),
        "vs_const_rps": rps_c,
        "regret_rps": rps_b,
        "vs_const_ce": pack(proxy_ce, const_ce, SEED + 2),
        "regret_ce": pack(proxy_ce, best_ce, SEED + 3),
        "vs_const_tvd": pack(proxy_tvd, const_tvd, SEED + 4),
        "regret_tvd": pack(proxy_tvd, best_tvd, SEED + 5),
        "pass": success_rule(rps_c["diff"], rps_c["lo"], rps_c["hi"], rps_b["lo"], rps_b["hi"]),
        "judges": rows,
        "proxy_spearman_vs_neg_rps": M.spearman_corr([r["proxy"] for r in rows], [-r["loto_rps"] for r in rows]),
        "proxy_pearson_vs_neg_rps": M.pearson_corr([r["proxy"] for r in rows], [-r["loto_rps"] for r in rows]),
    }


def n250_block() -> dict:
    rows = []
    for path in sorted(SNAP.glob("*native_main*.csv")):
        with path.open() as handle:
            for row in csv.DictReader(handle):
                if row.get("source_label") != "main":
                    continue
                raw = (row.get("final_score_0_5") or "").strip()
                if raw == "":
                    continue
                rows.append(row)
    by_id = defaultdict(int)
    hist = defaultdict(int)
    attest = defaultdict(int)
    by_item = defaultdict(list)
    t05, t08 = {}, {}
    for row in rows:
        rid = row["rater_id"].strip()
        score = int(round(float(row["final_score_0_5"])))
        by_id[rid] += 1
        hist[score] += 1
        att = (row.get("ai_assisted_rating_attestation (AI help is allowed)") or "").strip()
        attest[att if att else "(blank)"] += 1
        by_item[(row["task_folder"], row["item_id"])].append(score)
        if rid == "T05":
            t05[row["item_id"]] = score
        elif rid == "T08":
            t08[row["item_id"]] = score
    counts_ok = dict(by_id) == EXPECTED and sum(by_id.values()) == 250
    shared = sorted(set(t05) & set(t08))
    y1 = [t05[i] for i in shared]
    y2 = [t08[i] for i in shared]
    # LOTO CONST on files that have at least one rating. Task = task_folder.
    artifacts = sorted(by_item)
    tasks = [task for task, _item in artifacts]
    ratings = {key: by_item[key] for key in artifacts}
    task_ids = sorted(set(tasks))
    const_rps, const_ce, const_tvd = [], [], []
    for task in task_ids:
        hold = [i for i, t in enumerate(tasks) if t == task]
        train_ratings = [y for i, t in enumerate(tasks) if t != task for y in ratings[artifacts[i]]]
        q = laplace_from_ratings(train_ratings)
        rs, cs, ts = [], [], []
        for i in hold:
            a, b, c = artifact_losses(q, ratings[artifacts[i]])
            rs.append(a)
            cs.append(b)
            ts.append(c)
        const_rps.append(float(np.mean(rs)))
        const_ce.append(float(np.mean(cs)))
        const_tvd.append(float(np.mean(ts)))
    rps_m, rps_lo, rps_hi = boot_mean(np.asarray(const_rps), SEED)
    ce_m, ce_lo, ce_hi = boot_mean(np.asarray(const_ce), SEED + 7)
    tvd_m, tvd_lo, tvd_hi = boot_mean(np.asarray(const_tvd), SEED + 8)
    return {
        "counts_ok": counts_ok,
        "n": len(rows),
        "by_rater": dict(by_id),
        "hist": {str(k): hist[k] for k in range(6)},
        "share_5": hist[5] / len(rows),
        "mean_score": float(np.mean([int(round(float(r["final_score_0_5"]))) for r in rows])),
        "attest": dict(attest),
        "t05_t08_n": len(shared),
        "t05_t08_spearman": M.spearman_corr(y1, y2),
        "t05_t08_pearson": M.pearson_corr(y1, y2),
        "t05_t08_qwk": qwk(y1, y2),
        "t05_t08_exact": int(sum(a == b for a, b in zip(y1, y2))),
        "t05_t08_within1": int(sum(abs(a - b) <= 1 for a, b in zip(y1, y2))),
        "n_files": len(artifacts),
        "n_tasks": len(task_ids),
        "const_loto_rps": {"val": rps_m, "lo": rps_lo, "hi": rps_hi},
        "const_loto_ce": {"val": ce_m, "lo": ce_lo, "hi": ce_hi},
        "const_loto_tvd": {"val": tvd_m, "lo": tvd_lo, "hi": tvd_hi},
    }


def fmt(block: dict) -> str:
    return f"{block['diff']:+.4f} [{block['lo']:+.4f}, {block['hi']:+.4f}]"


def write_results(payload: dict) -> None:
    out = EXP / "results"
    out.mkdir(exist_ok=True)
    (out / "summary.json").write_text(json.dumps(payload, indent=2) + "\n")
    lines = ["# Experiment 69A tables", "", "Generated by `scripts/run_69a.py` from `PREREG.md`. Lower RPS, CE, and TVD are better.", ""]
    n = payload["n250"]
    lines += [
        "## N250 human snapshot",
        "",
        f"- Count check: `{n['counts_ok']}` ({n['n']} main scores, by rater `{n['by_rater']}`).",
        f"- Histogram 0..5: `{n['hist']}`. Share at 5: {n['share_5']:.4f}. Mean score: {n['mean_score']:.4f}.",
        f"- Attestations: `{n['attest']}`.",
        f"- T05 vs T08 on {n['t05_t08_n']} files: Spearman {n['t05_t08_spearman']:.4f}, Pearson {n['t05_t08_pearson']:.4f}, quadratic weighted kappa {n['t05_t08_qwk']:.4f}, exact {n['t05_t08_exact']}, within 1 {n['t05_t08_within1']}.",
        f"- LOTO CONST on {n['n_files']} files / {n['n_tasks']} tasks: RPS {n['const_loto_rps']['val']:.4f} [{n['const_loto_rps']['lo']:.4f}, {n['const_loto_rps']['hi']:.4f}], CE {n['const_loto_ce']['val']:.4f} [{n['const_loto_ce']['lo']:.4f}, {n['const_loto_ce']['hi']:.4f}], TVD {n['const_loto_tvd']['val']:.4f} [{n['const_loto_tvd']['lo']:.4f}, {n['const_loto_tvd']['hi']:.4f}].",
        "",
        "## Selection",
        "",
    ]
    for block in payload["selections"]:
        lines.append(f"### {block['pool']} / {block.get('proxy', 'n/a')}")
        lines.append("")
        if block.get("status") == "NOT_COMPUTABLE":
            lines.append(f"NOT_COMPUTABLE: {block.get('reason')}")
            lines.append("")
            continue
        lines.append(
            f"Selected `{block['selected']}` (proxy {block['selected_proxy']:.4f}). "
            f"RPS proxy {block['rps_proxy']:.4f}, CONST {block['rps_const']:.4f}, best-on-val {block['rps_best']:.4f}. "
            f"vs CONST {fmt(block['vs_const_rps'])}. Regret {fmt(block['regret_rps'])}. Pass: `{block['pass']}`."
        )
        lines.append("")
        lines.append(f"CE vs CONST {fmt(block['vs_const_ce'])}; CE regret {fmt(block['regret_ce'])}.")
        lines.append(f"TVD vs CONST {fmt(block['vs_const_tvd'])}; TVD regret {fmt(block['regret_tvd'])}.")
        lines.append(
            f"Diagnostic Spearman(proxy, −RPS) {block['proxy_spearman_vs_neg_rps']}. "
            f"Pearson {block['proxy_pearson_vs_neg_rps']}."
        )
        lines.append("")
        lines.append("| Judge | Proxy | LOTO RPS | LOTO CE | LOTO TVD | Spearman | Pearson |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for row in sorted(block["judges"], key=lambda r: -r["proxy"]):
            lines.append(
                f"| `{row['judge']}` | {row['proxy']:.4f} | {row['loto_rps']:.4f} | {row['loto_ce']:.4f} | {row['loto_tvd']:.4f} | {row['spearman']:.4f} | {row['pearson']:.4f} |"
            )
        lines.append("")
    (out / "tables.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    hvb = load_hvb()
    artifacts = sorted(hvb)
    tasks = [gold for gold, _cand in artifacts]
    needed = {cand[:-5] if cand.endswith(".lean") else cand for _gold, cand in artifacts}
    paper = load_paper()
    e39_meta = load_e39_indices()
    e39_scores = load_e39_scores(needed)
    stem = {key: (key[1][:-5] if key[1].endswith(".lean") else key[1]) for key in artifacts}

    def paper_panel(names: list[str]) -> dict[str, dict]:
        panel = {}
        for name in names:
            smap = paper[name]["scores"]
            built = build_panel(artifacts, hvb, smap)
            if built is None or paper[name]["TI_var"] is None:
                continue
            built["proxy"] = paper[name]["TI_var"]
            panel[name] = built
        return panel

    def e39_panel(names: list[str], proxy_key: str) -> dict[str, dict]:
        panel = {}
        for name in names:
            meta = e39_meta[name]
            value = meta["indices"].get(proxy_key)
            if value is None:
                continue
            smap = {key: e39_scores.get(name, {}).get(stem[key], []) for key in artifacts}
            built = build_panel(artifacts, hvb, smap)
            if built is None:
                continue
            built["proxy"] = float(value)
            panel[name] = built
        return panel

    selections = []
    paper_names = sorted(paper)
    selections.append({"pool": "paper_all", **loto_selection(artifacts, tasks, hvb, paper_panel(paper_names), "TI_var")})
    for family in FAM:
        names = [name for name in paper_names if paper[name]["family"] == family]
        panel = paper_panel(names)
        if len(panel) < MIN_POOL:
            selections.append({"pool": f"paper_{family}", "proxy": "TI_var", "status": "NOT_COMPUTABLE", "reason": f"{len(panel)} judges"})
        else:
            selections.append({"pool": f"paper_{family}", **loto_selection(artifacts, tasks, hvb, panel, "TI_var")})

    test_llm = [cfg for cfg, meta in e39_meta.items() if meta["split"] == "test" and meta["kind"] == "llm"]
    all_llm = [cfg for cfg, meta in e39_meta.items() if meta["kind"] == "llm"]
    for pool_name, members in (("e39_test_llm", test_llm), ("e39_all_llm", all_llm)):
        for proxy_key in E39_PROXIES:
            panel = e39_panel(members, proxy_key)
            if len(panel) < MIN_POOL:
                selections.append({"pool": pool_name, "proxy": proxy_key, "status": "NOT_COMPUTABLE", "reason": f"{len(panel)} judges with full P59 coverage"})
            else:
                selections.append({"pool": pool_name, **loto_selection(artifacts, tasks, hvb, panel, proxy_key)})

    payload = {
        "n_artifacts": len(artifacts),
        "n_tasks": len(set(tasks)),
        "n250": n250_block(),
        "selections": selections,
        "spend_usd": 0,
    }
    write_results(payload)
    print(json.dumps({
        "n_artifacts": payload["n_artifacts"],
        "n_tasks": payload["n_tasks"],
        "n250_ok": payload["n250"]["counts_ok"],
        "share_5": payload["n250"]["share_5"],
        "passes": [(b["pool"], b.get("proxy"), b.get("pass"), b.get("status")) for b in selections],
    }, indent=2))


if __name__ == "__main__":
    main()
