#!/usr/bin/env python3
"""TLDR: Partial freeze for the cert-judge rating pool. Locks the 25-task wave and the accept
threshold from experiment 39's train and validation judges. No model calls. Does not pin candidate
bytes or the 51 judge selectors, so it is not permission to send packets.

Run from the cert-judge repository root:
    python3 experiments/ideas/cj_human_rating_pool_prospective_screen/freeze/freeze_wave1_and_threshold.py
"""
from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path

SEED = 20261014
PER_SPLIT = 5
DROP_STEMS = ("heapsort_build_heap", "heapsort_max_heapify")
GATE = 0.45  # experiment 39 PROTOCOL.md, also the pool's "meets the human gate" cut
HERE = Path(__file__).resolve().parent
REPO = next(q for q in HERE.parents if (q / "py_src" / "cert_judge").is_dir())
MANIFEST = Path("/Users/brandomiranda/veribench/experiments/106_simulated_expert_raters_icl_from_human_labels_leave_one_agent_out_fsc_judge/expt_v5/manifest.json")
UNITS = REPO / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results/units_train_val.json"
ANALYSIS_LIB = REPO / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families/scripts/analysis_lib.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stem(task: str) -> str:
    return task.split("/")[-1]


def draw(tasks: list[dict]) -> dict:
    """One random.Random(20261014), splits in manifest order, sample 5 from each split's eligible
    list in that same order. N17's two imported references are dropped before the draw."""
    order = []
    for task in tasks:
        if task["split"] not in order:
            order.append(task["split"])
    rng = random.Random(SEED)
    chosen = []
    eligible_counts = {}
    for split in order:
        pool = [t for t in tasks if t["split"] == split and stem(t["task"]) not in DROP_STEMS]
        eligible_counts[split] = len(pool)
        if len(pool) < PER_SPLIT:
            raise SystemExit(f"{split}: only {len(pool)} eligible tasks")
        chosen.extend(rng.sample(pool, PER_SPLIT))
    return {"split_order": order, "eligible_counts": eligible_counts, "tasks": chosen}


def threshold(units: list[dict]) -> dict:
    """Largest C_ms_gold among the train+validation values that maximize balanced accuracy for
    criterion >= 0.45. Test units are not read. A missing screen or criterion drops that unit."""
    rows = []
    for unit in units:
        if unit.get("kind") != "llm" or unit.get("split") not in ("train", "val"):
            continue
        screen = unit["indices"].get("C_ms_gold")
        criterion = (unit["criteria"].get("heldout") or {}).get("spearman")
        if screen is None or criterion is None:
            continue
        rows.append((unit["config"], unit["split"], float(screen), float(criterion)))
    goods = [r for r in rows if r[3] >= GATE]
    bads = [r for r in rows if r[3] < GATE]
    best = None
    for tau in sorted({r[2] for r in rows}):
        accepted = [r for r in rows if r[2] >= tau]
        tp = sum(r[3] >= GATE for r in accepted)
        fp = sum(r[3] < GATE for r in accepted)
        tn = len(bads) - fp
        fn = len(goods) - tp
        tpr = tp / len(goods)
        tnr = tn / len(bads)
        balanced = 0.5 * (tpr + tnr)
        if best is None or balanced > best["balanced_accuracy"] + 1e-12 or (
            abs(balanced - best["balanced_accuracy"]) <= 1e-12 and tau > best["tau"]
        ):
            best = {"tau": tau, "balanced_accuracy": balanced, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
                    "tpr": tpr, "tnr": tnr}
    best.update(n_units=len(rows), n_good=len(goods), n_bad=len(bads),
                tie_break="largest tau among thresholds with the maximum balanced accuracy",
                good_definition=f"held-out Spearman >= {GATE}")
    return best


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    drawn = draw(manifest["tasks"])
    units = json.loads(UNITS.read_text())["units"]
    tau = threshold(units)
    payload = {
        "written_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PARTIAL — wave-1 tasks and the accept threshold only. Candidate bytes and the 51 judge selectors are not pinned. Do not send packets.",
        "no_model_calls": True,
        "manifest_sha256": sha256(MANIFEST),
        "manifest_path": str(MANIFEST),
        "units_train_val_sha256": sha256(UNITS),
        "analysis_lib_sha256": sha256(ANALYSIS_LIB),
        "draw": {
            "seed": SEED,
            "generator": "random.Random, one stream, sample(5) per split",
            "dropped_stems": list(DROP_STEMS),
            "reason": "set N folder N17 shows raters the heapsort_build_heap and heapsort_max_heapify references",
            "split_order": drawn["split_order"],
            "eligible_counts": drawn["eligible_counts"],
            "n_tasks": len(drawn["tasks"]),
            "tasks": [{"task": t["task"], "split": t["split"], "reference_sha256": t["reference_sha256"],
                       "reference_path": t["reference_path"]} for t in drawn["tasks"]],
        },
        "accept_threshold": tau,
        "not_frozen": [
            "SHA-256 of the 125 candidate files from experiment 109",
            "the 51 new judge selectors, efforts and prompt fingerprints",
            "the set-N rubric file hash (the proposal cites b29e9caf; that file was not in the local human_round tree on 10-18-2026)",
        ],
    }
    out = HERE / "FREEZE_10-18-2026.json"
    out.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps({"n_tasks": payload["draw"]["n_tasks"], "tau": tau["tau"], "balanced_accuracy": tau["balanced_accuracy"],
                      "tp": tau["tp"], "fp": tau["fp"], "fn": tau["fn"], "tn": tau["tn"]}, indent=1))


if __name__ == "__main__":
    main()
