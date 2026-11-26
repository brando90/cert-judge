#!/usr/bin/env python3
"""Formulation ③ versus ④ on sealed task folds. Needs 69B forecasts. Dry-run stays unlabeled as a result."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "69b/scripts"))
sys.path.insert(0, str(HERE.parents[3] / "experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026/scripts"))
from common import SPLIT, items_from_ratings  # noqa: E402
import metrics as M  # noqa: E402

B = 2000
SEED = 69


def boot_diff(a: np.ndarray, b: np.ndarray, seed: int) -> dict:
    diff = np.asarray(a, float) - np.asarray(b, float)
    rng = np.random.default_rng(seed)
    draws = diff[rng.integers(0, len(diff), size=(B, len(diff)))].mean(1)
    return {"diff": float(diff.mean()), "lo": float(np.percentile(draws, 2.5)), "hi": float(np.percentile(draws, 97.5))}


def wins(block: dict) -> bool:
    return block["diff"] < 0 and block["hi"] < 0


def task_mean(loss: np.ndarray, tasks: list[str], wanted: set[str]) -> float:
    vals = [float(loss[np.array([t == w for t in tasks])].mean()) for w in sorted(wanted)]
    return float(np.mean(vals))


def per_task(loss: np.ndarray, tasks: list[str], wanted: list[str]) -> np.ndarray:
    return np.asarray([float(loss[np.array([t == w for t in tasks])].mean()) for w in wanted])


def candidates_for_judge(probs: np.ndarray, ratings: list[list[int]], tasks: list[str], fit_split: str) -> dict[str, np.ndarray]:
    """Return item-aligned forecast matrices. Maps are fit on fit_split only."""
    ev = probs @ np.arange(6)
    idx = [i for i, t in enumerate(tasks) if SPLIT[t] == fit_split]
    ce_map = M.fit_ce_ordinal(ev[idx], [ratings[i] for i in idx])
    pe_map = M.fit_pearson_gauss(ev[idx], [ratings[i] for i in idx])
    const = M.fit_const([ratings[i] for i in idx])(np.zeros(len(tasks)))
    return {
        "native": probs,
        "ce_map": ce_map(ev),
        "pearson_map": pe_map(ev),
        "const": const,
    }


def loss_vector(mat: np.ndarray, ratings: list[list[int]], kind: str) -> np.ndarray:
    out = np.empty(len(ratings))
    for i, rats in enumerate(ratings):
        if kind == "rps":
            out[i] = M.rps_item(mat[i], rats)
        elif kind == "ce":
            out[i] = M.ce_item(mat[i], rats)
        else:
            out[i] = M.tvd_item(mat[i], rats)
    return out


def select(cands: dict[str, np.ndarray], ratings, tasks, objective: str, select_split: str) -> str:
    names = list(cands)
    if objective == "pearson":
        idx = [i for i, t in enumerate(tasks) if SPLIT[t] == select_split]
        scores = []
        for name in names:
            ev = cands[name] @ np.arange(6)
            human = np.asarray([float(np.mean(ratings[i])) for i in idx])
            rho = M.pearson_corr(ev[idx], human)
            scores.append((-999.0 if np.isnan(rho) else rho, name))
        return max(scores)[1]
    kind = objective
    best_name, best_val = None, 1e9
    for name in names:
        loss = loss_vector(cands[name], ratings, kind)
        val = task_mean(loss, tasks, {t for t in tasks if SPLIT[t] == select_split})
        if val < best_val or (val == best_val and (best_name is None or name < best_name)):
            best_name, best_val = name, val
    return best_name


def run(forecast_rows: list[dict], items: list[dict]) -> dict:
    by_judge = {}
    sources = set()
    item_index = {it["item_id"]: it for it in items}
    order = sorted(items, key=lambda it: it["item_id"])
    for row in forecast_rows:
        sources.add(row.get("source"))
        if row.get("probs") is None:
            continue
        by_judge.setdefault(row["judge"], {})[row["item_id"]] = row["probs"]
    dry = sources == {"dry_run"}
    ratings = [it["ratings"] for it in order]
    tasks = [it["task"] for it in order]
    test_tasks = [t for t in tasks if SPLIT[t] == "test"]
    # unique test task order
    test_unique = [t for t in dict.fromkeys(test_tasks)]
    arms = {}
    for judge, scored in sorted(by_judge.items()):
        if any(it["item_id"] not in scored for it in order):
            arms[judge] = {"status": "NOT_COMPUTABLE"}
            continue
        probs = np.vstack([np.asarray(scored[it["item_id"]], float) for it in order])
        # ④ fits and selects on train. ③ fits on train and selects on val.
        fit4 = candidates_for_judge(probs, ratings, tasks, "train")
        fit3 = fit4  # same train fit; selection split differs
        chosen = {
            "rps_4": select(fit4, ratings, tasks, "rps", "train"),
            "ce_4": select(fit4, ratings, tasks, "ce", "train"),
            "pearson_4": select(fit4, ratings, tasks, "pearson", "train"),
            "rps_3": select(fit3, ratings, tasks, "rps", "val"),
            "ce_3": select(fit3, ratings, tasks, "ce", "val"),
            "pearson_3": select(fit3, ratings, tasks, "pearson", "val"),
        }
        test_rps = {}
        for arm, name in chosen.items():
            loss = loss_vector(fit4[name], ratings, "rps")
            test_rps[arm] = per_task(loss, tasks, test_unique)
        def cmp(a: str, b: str, seed: int) -> dict:
            block = boot_diff(test_rps[a], test_rps[b], seed)
            block["wins"] = (not dry) and wins(block)
            block["selected_a"] = chosen[a]
            block["selected_b"] = chosen[b]
            block["test_rps_a"] = float(test_rps[a].mean())
            block["test_rps_b"] = float(test_rps[b].mean())
            return block
        arms[judge] = {
            "status": "DRY_RUN" if dry else "MEASURED",
            "chosen": chosen,
            "rps3_minus_rps4": cmp("rps_3", "rps_4", SEED),
            "ce3_minus_ce4": cmp("ce_3", "ce_4", SEED + 1),
            "rps3_minus_pearson3": cmp("rps_3", "pearson_3", SEED + 2),
            "rps4_minus_pearson4": cmp("rps_4", "pearson_4", SEED + 3),
        }
    return {"dry_run": dry, "arms": arms}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecasts", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rows = [json.loads(line) for line in Path(args.forecasts).read_text().splitlines() if line.strip()]
    payload = run(rows, items_from_ratings())
    Path(args.out).write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"dry_run": payload["dry_run"], "judges": list(payload["arms"])}))


if __name__ == "__main__":
    main()
