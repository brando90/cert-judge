#!/usr/bin/env python3
"""Held-out RPS of 69B native forecasts against the 250 ratings. Dry-run files stay labeled DRY_RUN."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/scripts"))
from common import items_from_ratings  # noqa: E402
import metrics as M  # noqa: E402

B = 2000
SEED = 69


def boot_mean(values: np.ndarray, seed: int) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    draws = values[rng.integers(0, len(values), size=(B, len(values)))].mean(1)
    return float(values.mean()), float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def beats_const(diff: float, hi: float) -> bool:
    return diff < 0 and hi < 0


def evaluate(forecast_rows: list[dict], items: list[dict]) -> dict:
    judges = defaultdict(dict)
    sources = set()
    for row in forecast_rows:
        if row.get("probs") is None:
            continue
        judges[row["judge"]][row["item_id"]] = np.asarray(row["probs"], dtype=float)
        sources.add(row.get("source"))
    dry = sources == {"dry_run"}
    tasks = sorted({it["task"] for it in items})
    reports = []
    for judge, scored in sorted(judges.items()):
        covered = [it for it in items if it["item_id"] in scored]
        if len(covered) < len(items):
            reports.append({"judge": judge, "status": "NOT_COMPUTABLE", "n": len(covered)})
            continue
        order = sorted(covered, key=lambda it: it["item_id"])
        task_of = [it["task"] for it in order]
        ratings = [it["ratings"] for it in order]
        jloss = {"rps": [], "ce": [], "tvd": [], "ev": []}
        for it in order:
            q = scored[it["item_id"]]
            jloss["rps"].append(M.rps_item(q, it["ratings"]))
            jloss["ce"].append(M.ce_item(q, it["ratings"]))
            jloss["tvd"].append(M.tvd_item(q, it["ratings"]))
            jloss["ev"].append(float(np.dot(np.arange(6), q)))
        j_task, c_task = [], []
        ce_j, ce_c, tv_j, tv_c = [], [], [], []
        for task in tasks:
            idx = [i for i, t in enumerate(task_of) if t == task]
            train = [ratings[i] for i, t in enumerate(task_of) if t != task]
            q = M.fit_const(train)([0.0])[0]
            cr = [M.rps_item(q, ratings[i]) for i in idx]
            cc = [M.ce_item(q, ratings[i]) for i in idx]
            ct = [M.tvd_item(q, ratings[i]) for i in idx]
            j_task.append(float(np.mean([jloss["rps"][i] for i in idx])))
            c_task.append(float(np.mean(cr)))
            ce_j.append(float(np.mean([jloss["ce"][i] for i in idx])))
            ce_c.append(float(np.mean(cc)))
            tv_j.append(float(np.mean([jloss["tvd"][i] for i in idx])))
            tv_c.append(float(np.mean(ct)))
        d_rps = np.asarray(j_task) - np.asarray(c_task)
        mean, lo, hi = boot_mean(d_rps, SEED)
        d_ce = np.asarray(ce_j) - np.asarray(ce_c)
        d_tv = np.asarray(tv_j) - np.asarray(tv_c)
        ce_m, ce_lo, ce_hi = boot_mean(d_ce, SEED + 1)
        tv_m, tv_lo, tv_hi = boot_mean(d_tv, SEED + 2)
        human = np.asarray([float(np.mean(it["ratings"])) for it in order])
        reports.append({
            "judge": judge,
            "status": "DRY_RUN" if dry else "MEASURED",
            "n_items": len(order),
            "n_tasks": len(tasks),
            "rps": float(np.mean(j_task)),
            "const_rps": float(np.mean(c_task)),
            "vs_const_rps": {"diff": mean, "lo": lo, "hi": hi},
            "beats_const_rps": (not dry) and beats_const(mean, hi),
            "vs_const_ce": {"diff": ce_m, "lo": ce_lo, "hi": ce_hi},
            "vs_const_tvd": {"diff": tv_m, "lo": tv_lo, "hi": tv_hi},
            "spearman": M.spearman_corr(jloss["ev"], human),
            "pearson": M.pearson_corr(jloss["ev"], human),
        })
    return {"dry_run": dry, "judges": reports}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecasts", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rows = [json.loads(line) for line in Path(args.forecasts).read_text().splitlines() if line.strip()]
    payload = evaluate(rows, items_from_ratings())
    Path(args.out).write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"dry_run": payload["dry_run"], "judges": [j["judge"] for j in payload["judges"]]}))


if __name__ == "__main__":
    main()
