#!/usr/bin/env python3
"""TLDR: Compare the 124 pinned wave-1 candidates with the 75 May rated files on experiment 110's
file-side criteria C1-C13. No model calls.

    python3 experiments/54_wave1_pinned_candidates_vs_may_rated_pool_structural_screen/scripts/analyze_e54.py
"""
from __future__ import annotations

import base64
import importlib.util
import json
import random
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
E54 = HERE.parent
REPO = next(q for q in E54.parents if (q / "py_src" / "cert_judge").is_dir())
VB = Path("/Users/brandomiranda/veribench")
X100 = VB / "experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test"
EXTRACT = VB / "experiments/110_fsc_judge_transfer_frontier_outputs_vs_human_rated_pool/scripts/extract_criteria.py"
PIN = REPO / "experiments/ideas/cj_human_rating_pool_prospective_screen/freeze/CANDIDATE_PIN_10-18-2026.json"
FREEZE = REPO / "experiments/ideas/cj_human_rating_pool_prospective_screen/freeze/FREEZE_10-18-2026.json"
TEXTS = Path("/tmp/wave1_texts.jsonl")
CRITS = [f"C{i}" for i in range(1, 14)]
SEED = 54
DRAWS = 10000
COVERAGE = 0.70


def load_extractor():
    spec = importlib.util.spec_from_file_location("extract_criteria_110", EXTRACT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def percentile_interval(values):
    x = np.asarray(values, dtype=float)
    lo = float(np.percentile(x, 5))
    hi = float(np.percentile(x, 95))
    if lo == hi:
        lo, hi = float(np.min(x)), float(np.max(x))
        degenerate = True
    else:
        degenerate = False
    return lo, hi, degenerate


def in_distribution(pool, wave, coverage=COVERAGE):
    lo, hi, degenerate = percentile_interval(pool)
    med = float(np.median(wave))
    inside = (wave >= lo) & (wave <= hi)
    frac = float(np.mean(inside)) if len(wave) else 0.0
    return {"median": med, "pool_lo": lo, "pool_hi": hi, "degenerate": degenerate,
            "frac_inside": frac, "in_distribution": bool(lo <= med <= hi and frac + 1e-12 >= coverage)}


def task_of_id(task_id: str, by_lower: dict) -> str:
    return by_lower[task_id]


def main() -> None:
    ext = load_extractor()
    freeze = json.loads(FREEZE.read_text())
    by_lower = {t["task"].replace("/", "__").lower(): t["task"] for t in freeze["draw"]["tasks"]}
    items = [json.loads(l) for l in (X100 / "inputs/items.jsonl").read_text().splitlines() if l.strip()]
    pool_rows = []
    for it in items:
        cand = (X100 / "inputs/candidates" / it["candidate_file"]).read_text(errors="replace")
        ref = (X100 / it["ref_ann_path"]).read_text(errors="replace")
        py = (X100 / it["py_ann_path"]).read_text(errors="replace")
        feat = ext.features(cand, ref, py)
        pool_rows.append({"item": it["item"], "task": it["task"], **{c: feat[c] for c in CRITS}})
    texts = {}
    for line in TEXTS.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("matched"):
            texts[(rec["system"], rec["task_id"])] = base64.b64decode(rec["b64"]).decode("utf-8", "replace")
    wave_rows = []
    missing_text = []
    for row in json.loads(PIN.read_text())["rows"]:
        if not row["collected_sha256"]:
            continue
        key = (row["system"], row["task_id"])
        text = texts.get(key)
        if text is None:
            missing_text.append(key)
            continue
        task = task_of_id(row["task_id"], by_lower)
        ref_path = VB / "veribench_dataset/lean_src/veribench" / f"{task}.lean"
        # task is like easy_set/21_is_palindrome; python lives beside it under py_src
        py_path = VB / "veribench_dataset/py_src" / f"{task}.py"
        if not ref_path.exists() or not py_path.exists():
            missing_text.append({"task": task, "ref": ref_path.exists(), "py": py_path.exists()})
            continue
        feat = ext.features(text, ref_path.read_text(errors="replace"), py_path.read_text(errors="replace"))
        wave_rows.append({"system": row["system"], "task": task, "task_id": row["task_id"], **{c: feat[c] for c in CRITS}})
    if missing_text:
        raise SystemExit(f"missing texts or sources: {missing_text[:5]} n={len(missing_text)}")
    pool = {c: np.array([r[c] for r in pool_rows], dtype=float) for c in CRITS}
    wave = {c: np.array([r[c] for r in wave_rows], dtype=float) for c in CRITS}
    per = {}
    for c in CRITS:
        row = in_distribution(pool[c], wave[c])
        row["at_0.60"] = in_distribution(pool[c], wave[c], 0.60)["in_distribution"]
        row["at_0.80"] = in_distribution(pool[c], wave[c], 0.80)["in_distribution"]
        per[c] = row
    k = sum(1 for c in CRITS if per[c]["in_distribution"])
    # task bootstrap of the wave-1 side; pool fixed
    rng = np.random.default_rng(SEED)
    tasks = sorted({r["task"] for r in wave_rows})
    by_task = {t: [r for r in wave_rows if r["task"] == t] for t in tasks}
    ks = []
    for _ in range(DRAWS):
        drawn = rng.choice(tasks, size=len(tasks), replace=True)
        sample = [r for t in drawn for r in by_task[t]]
        kk = 0
        for c in CRITS:
            vals = np.array([r[c] for r in sample], dtype=float)
            if in_distribution(pool[c], vals)["in_distribution"]:
                kk += 1
        ks.append(kk)
    ks = np.array(ks)
    by_system = {}
    for system in sorted({r["system"] for r in wave_rows}):
        sub = [r for r in wave_rows if r["system"] == system]
        cnt = 0
        for c in CRITS:
            vals = np.array([r[c] for r in sub], dtype=float)
            if in_distribution(pool[c], vals)["in_distribution"]:
                cnt += 1
        by_system[system] = {"n": len(sub), "in_distribution": cnt}
    payload = {
        "written_utc": datetime.now(timezone.utc).isoformat(),
        "seed": SEED, "draws": DRAWS, "n_pool": len(pool_rows), "n_wave": len(wave_rows),
        "n_wave_tasks": len(tasks), "criteria_in_distribution": k, "criteria_declared": 13,
        "bootstrap": {"lo": float(np.percentile(ks, 2.5)), "hi": float(np.percentile(ks, 97.5)),
                      "mean": float(ks.mean()), "p_val": "n/a", "resampled": "wave-1 task, pool fixed"},
        "per_criterion": per, "per_system": by_system,
        "extractor": str(EXTRACT),
    }
    out = E54 / "results/summary.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps({"k": k, "ci": [payload["bootstrap"]["lo"], payload["bootstrap"]["hi"]], "n": len(wave_rows), "systems": by_system}, indent=1))


if __name__ == "__main__":
    main()
