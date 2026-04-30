#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import spearmanr


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Folder 09: single certified judge vs ensemble")
    p.add_argument("--detail-csv", type=Path, required=True)
    p.add_argument("--exp06-summary", type=Path, required=True)
    p.add_argument("--exp07-summary", type=Path, required=True)
    p.add_argument("--human-tsv", type=Path, default=None,
                   help="Optional TSV with columns gold_file,candidate_file,human_score_0_5")
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--label", type=str, default="median")
    p.add_argument("--bootstrap-iters", type=int, default=10000)
    p.add_argument("--perm-iters", type=int, default=0)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_detail(path: Path) -> List[dict]:
    rows: List[dict] = []
    with path.open("r", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def load_human_tsv(path: Path | None) -> Dict[str, float]:
    if path is None:
        return {}
    out: Dict[str, float] = {}
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            gold = r.get("gold_file")
            cand = r.get("candidate_file")
            hs = r.get("human_score_0_5")
            if not gold or not cand or hs in (None, ""):
                continue
            # Convert 0..5 to 0..1 (monotonic scale; Spearman unchanged either way).
            out[f"{gold}::{cand}"] = float(hs) / 5.0
    return out


def extract_cert_scores(exp06: dict) -> Dict[str, Tuple[float, float]]:
    out: Dict[str, Tuple[float, float]] = {}
    for jr in exp06.get("judge_rows", []):
        out[jr["judge_id"]] = (float(jr.get("cert_index", float("nan"))), float(jr.get("cert_index_v2", float("nan"))))
    return out


def certified_pass_set(exp07: dict) -> set[str]:
    s = set()
    for jr in exp07.get("per_judge", []):
        if bool(jr.get("all_pass_p1_p2_p4", False)):
            s.add(jr["judge_id"])
    return s


def select_single_best(cert_scores: Dict[str, Tuple[float, float]], certified_set: set[str]) -> str:
    candidates = [j for j in cert_scores if j in certified_set]
    if not candidates:
        raise ValueError("No certified-pass judges found.")
    # sort by cert v2, tie-break by cert v1
    candidates.sort(key=lambda j: (cert_scores[j][1], cert_scores[j][0]), reverse=True)
    return candidates[0]


def is_llm(judge_id: str) -> bool:
    return ("|" in judge_id) and (not judge_id.startswith("editdist_")) and (not judge_id.startswith("random_"))


def build_item_table(detail_rows: List[dict]) -> Dict[str, dict]:
    items: Dict[str, dict] = {}
    for r in detail_rows:
        item_key = r["item_key"]
        row_type = r["row_type"]
        judge = r["judge_id"]
        score_mean = r.get("score_mean", "")
        if item_key not in items:
            items[item_key] = {"judges": {}, "human": {}}
        if score_mean in ("", None):
            continue
        s = float(score_mean)
        if row_type == "human_eval_union":
            # In exp16/06 artifacts this row type is the judge score on the
            # human-eval union item set (gold::candidate), not the human label.
            items[item_key]["judges"][judge] = s
        elif row_type.startswith("human_label_"):
            label = row_type.replace("human_label_", "")
            items[item_key]["human"][label] = s
        else:
            items[item_key]["judges"][judge] = s
    return items


def spearman_safe(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3:
        return float("nan")
    v = spearmanr(x, y).statistic
    return float(v) if v is not None else float("nan")


def bootstrap_ci(x: np.ndarray, y: np.ndarray, iters: int, seed: int) -> Tuple[float, float]:
    if len(x) < 3:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    n = len(x)
    vals: List[float] = []
    for _ in range(iters):
        idx = rng.integers(0, n, n)
        v = spearman_safe(x[idx], y[idx])
        if math.isfinite(v):
            vals.append(v)
    if not vals:
        return (float("nan"), float("nan"))
    arr = np.sort(np.array(vals))
    return (float(arr[int(0.025 * (len(arr) - 1))]), float(arr[int(0.975 * (len(arr) - 1))]))


def bootstrap_delta_ci(pred_a: np.ndarray, pred_b: np.ndarray, human: np.ndarray, iters: int, seed: int) -> Tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    n = len(human)
    vals: List[float] = []
    for _ in range(iters):
        idx = rng.integers(0, n, n)
        ra = spearman_safe(pred_a[idx], human[idx])
        rb = spearman_safe(pred_b[idx], human[idx])
        if math.isfinite(ra) and math.isfinite(rb):
            vals.append(ra - rb)
    if not vals:
        return (float("nan"), float("nan"), float("nan"))
    arr = np.sort(np.array(vals))
    lo = float(arr[int(0.025 * (len(arr) - 1))])
    hi = float(arr[int(0.975 * (len(arr) - 1))])
    obs = float(np.median(arr))
    return (obs, lo, hi)


def weighted_mean(values: List[float], weights: List[float]) -> float:
    w = np.array(weights, dtype=float)
    v = np.array(values, dtype=float)
    sw = w.sum()
    if sw <= 0:
        return float(np.mean(v))
    return float(np.dot(v, w) / sw)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    exp06 = load_json(args.exp06_summary)
    exp07 = load_json(args.exp07_summary)
    detail_rows = load_detail(args.detail_csv)

    cert_scores = extract_cert_scores(exp06)
    pass_set = certified_pass_set(exp07)
    items = build_item_table(detail_rows)
    judges_present = set()
    for rec in items.values():
        judges_present.update(rec["judges"].keys())

    cert_scores = {j: v for j, v in cert_scores.items() if j in judges_present}
    pass_set = {j for j in pass_set if j in judges_present}
    single_best = select_single_best(cert_scores, pass_set)

    all_llm = sorted([j for j in cert_scores if is_llm(j)])
    certified_llm = sorted([j for j in all_llm if j in pass_set])
    if single_best not in certified_llm:
        raise ValueError("Selected single best judge is not in certified LLM pool.")
    human_tsv = load_human_tsv(args.human_tsv)
    if human_tsv:
        # Override with external human labels for union items.
        for k, rec in items.items():
            if k in human_tsv:
                rec["human"]["union_avg"] = human_tsv[k]

    available_labels = sorted({k for rec in items.values() for k in rec["human"].keys()})
    if not available_labels:
        raise ValueError("No human labels found (detail CSV and --human-tsv empty).")
    label_sets = available_labels

    methods = [
        "single_best_certified",
        "ens_all_llm_uniform",
        "ens_certified_uniform",
        "ens_all_llm_certv2_weighted",
        "ens_certified_certv2_weighted",
    ]

    preds_by_label: Dict[str, Dict[str, List[float]]] = {ls: {m: [] for m in methods} for ls in label_sets}
    humans_by_label: Dict[str, List[float]] = {ls: [] for ls in label_sets}

    w_all = [max(cert_scores[j][1], 0.0) for j in all_llm]
    w_cert = [max(cert_scores[j][1], 0.0) for j in certified_llm]

    used_items = 0
    for _, rec in items.items():
        judges = rec["judges"]
        human = rec["human"]
        if single_best not in judges:
            continue
        if not all(j in judges for j in all_llm):
            continue
        if not all(j in judges for j in certified_llm):
            continue
        if not all(ls in human for ls in label_sets):
            continue

        s_single = float(judges[single_best])
        s_all_uniform = float(np.mean([float(judges[j]) for j in all_llm]))
        s_cert_uniform = float(np.mean([float(judges[j]) for j in certified_llm]))
        s_all_w = weighted_mean([float(judges[j]) for j in all_llm], w_all)
        s_cert_w = weighted_mean([float(judges[j]) for j in certified_llm], w_cert)

        for ls in label_sets:
            humans_by_label[ls].append(float(human[ls]))
            preds_by_label[ls]["single_best_certified"].append(s_single)
            preds_by_label[ls]["ens_all_llm_uniform"].append(s_all_uniform)
            preds_by_label[ls]["ens_certified_uniform"].append(s_cert_uniform)
            preds_by_label[ls]["ens_all_llm_certv2_weighted"].append(s_all_w)
            preds_by_label[ls]["ens_certified_certv2_weighted"].append(s_cert_w)

        used_items += 1

    comparison_rows: List[dict] = []
    pairwise_rows: List[dict] = []

    for ls in label_sets:
        h = np.array(humans_by_label[ls], dtype=float)
        for m in methods:
            p = np.array(preds_by_label[ls][m], dtype=float)
            rho = spearman_safe(p, h)
            ci_lo, ci_hi = bootstrap_ci(p, h, args.bootstrap_iters, args.seed)
            comparison_rows.append({
                "label_set": ls,
                "method": m,
                "n_items": len(h),
                "spearman_r": rho,
                "spearman_ci_lo": ci_lo,
                "spearman_ci_hi": ci_hi,
            })

        base = np.array(preds_by_label[ls]["single_best_certified"], dtype=float)
        for m in methods:
            if m == "single_best_certified":
                continue
            other = np.array(preds_by_label[ls][m], dtype=float)
            obs, d_lo, d_hi = bootstrap_delta_ci(base, other, h, args.bootstrap_iters, args.seed)
            pairwise_rows.append({
                "label_set": ls,
                "comparison": f"single_best_certified - {m}",
                "delta_spearman_median_boot": obs,
                "delta_ci_lo": d_lo,
                "delta_ci_hi": d_hi,
            })

    summary = {
        "experiment": "09_single_certified_judge_vs_ensemble",
        "label": args.label,
        "inputs": {
            "detail_csv": str(args.detail_csv),
            "exp06_summary": str(args.exp06_summary),
            "exp07_summary": str(args.exp07_summary),
        },
        "selection": {
            "single_best_certified": single_best,
            "certified_pass_judges": sorted(list(pass_set)),
            "all_llm_judges": all_llm,
            "certified_llm_judges": certified_llm,
        },
        "n_items_used": used_items,
        "comparison_rows": comparison_rows,
        "pairwise_delta_rows": pairwise_rows,
        "bootstrap_iters": args.bootstrap_iters,
        "perm_iters": args.perm_iters,
        "seed": args.seed,
    }

    with (args.out_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with (args.out_dir / "comparison_table.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["label_set", "method", "n_items", "spearman_r", "spearman_ci_lo", "spearman_ci_hi"])
        w.writeheader()
        w.writerows(comparison_rows)

    with (args.out_dir / "pairwise_delta_table.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["label_set", "comparison", "delta_spearman_median_boot", "delta_ci_lo", "delta_ci_hi"])
        w.writeheader()
        w.writerows(pairwise_rows)

    lines = []
    lines.append(f"# Folder 09 Auto Report ({args.label})")
    lines.append("")
    lines.append(f"- n_items used: {used_items}")
    lines.append(f"- single_best_certified: `{single_best}`")
    lines.append(f"- certified_llm_judges: {len(certified_llm)}")
    lines.append("")
    lines.append("## Spearman with human labels")
    lines.append("")
    lines.append("| label_set | method | rho | 95% bootstrap CI |")
    lines.append("|---|---|---:|---|")
    for r in comparison_rows:
        lines.append(
            f"| {r['label_set']} | `{r['method']}` | {r['spearman_r']:.3f} | [{r['spearman_ci_lo']:.3f}, {r['spearman_ci_hi']:.3f}] |"
        )
    lines.append("")
    lines.append("## Pairwise delta (single - ensemble)")
    lines.append("")
    lines.append("| label_set | comparison | delta rho | 95% bootstrap CI |")
    lines.append("|---|---|---:|---|")
    for r in pairwise_rows:
        lines.append(
            f"| {r['label_set']} | `{r['comparison']}` | {r['delta_spearman_median_boot']:.3f} | [{r['delta_ci_lo']:.3f}, {r['delta_ci_hi']:.3f}] |"
        )

    with (args.out_dir / "REPORT_AUTO.md").open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"done: {args.out_dir}")


if __name__ == "__main__":
    main()
