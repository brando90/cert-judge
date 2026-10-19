#!/usr/bin/env python3
"""Create an auditable train-only projection before any numerical analysis."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXP = Path(__file__).resolve().parents[1]
OUT = EXP / "results" / "train_only_inputs"
E39 = ROOT / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families"
E42 = ROOT / "experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges"
E44 = ROOT / "experiments/archive/44_cached_score_judge_selection_utility"
E45 = ROOT / "experiments/archive/45_five_rater_cached_selection_task_split_and_behavioral_audit"
PROMPTS = {"D0", "H0", "H1", "H2", "R4"}
ACCEPTED = {"measured", "deterministic"}


def semantic_cell_allowed(cell: dict, item_task: dict, train_tasks: set) -> bool:
    """Keep a semantic cell only when its identifier is an original training row."""
    kind, task, key = cell.get("kind"), cell.get("task"), cell.get("key")
    if kind == "crit":
        return key in item_task and task == item_task[key]
    return task in train_tasks


def criterion_cell_allowed(cell: dict, item_task: dict, train_tasks: set) -> bool:
    """Keep criterion cells used by the training diagnosis and drop every other split."""
    kind, task, key = cell.get("kind"), cell.get("task"), cell.get("key")
    level = int(cell.get("level", 0))
    if kind == "crit":
        return level == 0 and key in item_task and task == item_task[key]
    return kind in {"ident", "ms_gold"} and task in train_tasks


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def source_paths(primary: list[str]) -> list[Path]:
    return [
        E39 / "results/panel.json",
        E39 / "results/probe_manifest.json",
        *(E39 / "results/harvest" / f"{config.replace('|', '__')}.json" for config in primary),
        E42 / "results/semantic_probe_manifest.json",
        *(sorted((E42 / "probe_edits/audit").glob("*.json"))),
        *(sorted((E42 / "results/harvest").glob("*.json"))),
        E44 / "inputs/items.jsonl",
        E45 / "results/individual_current_ratings.json",
    ]


def freeze() -> dict:
    """Hash sources and inspect identifiers/declarations, never numerical outcomes."""
    items = []
    for line in (E44 / "inputs/items.jsonl").read_text().splitlines():
        raw = json.loads(line)
        items.append({key: raw[key] for key in ("item", "task", "split")})
    train = [row for row in items if row["split"] == "train"]
    if len({row["item"] for row in train}) != len(train):
        raise ValueError("duplicate training item identifier")
    panel = json.loads((E39 / "results/panel.json").read_text())
    # The historical original-12 pool is declared in panel metadata as the
    # configuration split named "test"; this is pool provenance, not an item
    # outcome read.  All item-level numerical work below remains train-only.
    configs = [row for row in panel["units"] if row.get("kind") == "llm" and row.get("split") == "test" and row.get("prompt_key") in PROMPTS]
    primary = sorted(row["config"] for row in configs)
    h2 = sorted(row["config"] for row in configs if row.get("prompt_key") == "H2")
    if len(primary) != 12 or len(h2) != 4:
        raise ValueError("original 12-configuration/H2 pool declaration mismatch")
    audit_labels: dict[str, str] = {}
    for path in sorted((E42 / "probe_edits/audit").glob("*.json")):
        for probe_id, row in json.loads(path.read_text()).get("labels", {}).items():
            audit_labels[probe_id] = row.get("label")
    train_tasks = {row["task"] for row in train}
    manifest = json.loads((E42 / "results/semantic_probe_manifest.json").read_text())
    declarations = [
        {key: row.get(key) for key in ("probe_id", "task", "kind", "level", "family", "valid")}
        | {"audit_label": audit_labels.get(row.get("probe_id"))}
        for row in manifest["rows"]
        if row.get("task") in train_tasks
    ]
    audit_evidence: dict[str, dict] = {}
    for path in sorted((E42 / "probe_edits/audit").glob("*.json")):
        for probe_id, row in json.loads(path.read_text()).get("labels", {}).items():
            audit_evidence[probe_id] = row
    preserving = [
        row | {"restated_by": audit_evidence[row["probe_id"]].get("restated_by"), "why": audit_evidence[row["probe_id"]].get("why")}
        for row in declarations
        if row["valid"] is True
        and row["family"] == "weakening"
        and row["audit_label"] == "redundant"
        and bool(audit_evidence.get(row["probe_id"], {}).get("restated_by"))
        and bool(audit_evidence.get(row["probe_id"], {}).get("why"))
    ]
    payload = {
        "status": "FROZEN_BEFORE_NUMERICAL_READ",
        "source_hashes": {str(path.relative_to(ROOT)): digest(path) for path in source_paths(primary)},
        "train_items": train,
        "primary_configs": primary,
        "h2_configs": h2,
        "primary_config_metadata": [{key: row.get(key) for key in ("config", "model_key", "harness", "prompt_key")} for row in sorted(configs, key=lambda row: row["config"])],
        "train_probe_declarations": declarations,
        "preservation_controls": {"status": "AUDIT_CONFIRMED_REDUNDANT_WEAKENING", "declared_count": len(preserving), "rows": preserving},
    }
    write(OUT / "input_manifest.json", payload)
    return payload


def project() -> dict:
    manifest = json.loads((OUT / "input_manifest.json").read_text())
    observed = {name: digest(ROOT / name) for name in manifest["source_hashes"]}
    if observed != manifest["source_hashes"]:
        raise RuntimeError("frozen source hash mismatch")
    train_items = manifest["train_items"]
    item_task = {row["item"]: row["task"] for row in train_items}
    train_tasks = set(item_task.values())
    primary = set(manifest["primary_configs"])
    ratings, rejected_ratings = [], Counter()
    for raw in json.loads((E45 / "results/individual_current_ratings.json").read_text()):
        item = raw.get("item")
        if item not in item_task:
            rejected_ratings["non_train_identifier"] += 1
            continue
        ratings.append({"item": item, "current5_mean_0_to_1": raw["current5_mean_0_to_1"], "current3_mean_0_to_1": raw["current3_mean_0_to_1"]})
    if {row["item"] for row in ratings} != set(item_task):
        raise ValueError("training ratings do not match training identifiers")
    semantic_harvests, rejected_semantic = {}, Counter()
    for path in sorted((E42 / "results/harvest").glob("*.json")):
        raw = json.loads(path.read_text())
        config = raw.get("config")
        if config not in primary:
            continue
        kept = []
        for cell in raw.get("cells", []):
            if not semantic_cell_allowed(cell, item_task, train_tasks):
                rejected_semantic["non_train_identifier"] += 1
                continue
            kept.append({field: cell.get(field) for field in ("cell", "kind", "key", "task", "level", "repeat", "status", "score")})
        semantic_harvests[config] = {"config": config, "cells": kept}
    if set(semantic_harvests) != primary:
        raise ValueError("missing primary configuration harvest")
    criterion_harvests, rejected_criterion = {}, Counter()
    for config in sorted(primary):
        raw = json.loads((E39 / "results/harvest" / f"{config.replace('|', '__')}.json").read_text())
        if raw.get("config") != config: raise ValueError("criterion harvest configuration mismatch")
        kept = []
        for cell in raw.get("cells", []):
            if not criterion_cell_allowed(cell, item_task, train_tasks):
                rejected_criterion["non_train_identifier_or_unused_kind"] += 1
                continue
            kept.append({field: cell.get(field) for field in ("cell", "kind", "key", "task", "level", "repeat", "status", "score")})
        criterion_harvests[config] = {"config": config, "cells": kept}
    e39_manifest = json.loads((E39 / "results/probe_manifest.json").read_text())
    e39_probes = [{key: row.get(key) for key in ("task", "key", "kind", "level", "valid")} for row in e39_manifest["rows"] if row.get("task") in train_tasks and row.get("valid") is True]
    write(OUT / "ratings.json", ratings)
    write(OUT / "semantic_harvests.json", semantic_harvests)
    write(OUT / "criterion_harvests.json", criterion_harvests)
    write(OUT / "e39_train_probes.json", e39_probes)
    receipt = {"status": "COMPLETE_TRAIN_ONLY", "train_items": len(train_items), "train_tasks": len(train_tasks), "ratings_written": len(ratings), "semantic_harvest_configs": len(semantic_harvests), "criterion_harvest_configs": len(criterion_harvests), "semantic_cells_excluded_before_numeric_extraction": dict(rejected_semantic), "criterion_cells_excluded_before_numeric_extraction": dict(rejected_criterion), "ratings_excluded_before_target_extraction": dict(rejected_ratings)}
    write(OUT / "projection_receipt.json", receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--project", action="store_true")
    args = parser.parse_args()
    if args.freeze == args.project:
        raise SystemExit("choose exactly one of --freeze or --project")
    payload = freeze() if args.freeze else project()
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
