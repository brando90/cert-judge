#!/usr/bin/env python3
"""Write the allowlisted, offline source-hash receipt for experiment 46."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "pyproject.toml").is_file())
E46 = Path(__file__).resolve().parents[1]
E39 = ROOT / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families"
E42 = ROOT / "experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges"
E44 = ROOT / "experiments/archive/44_cached_score_judge_selection_utility"
E45 = ROOT / "experiments/archive/45_five_rater_cached_selection_task_split_and_behavioral_audit"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs() -> list[Path]:
    paths = [
        E46 / "PROTOCOL.md",
        E39 / "results/panel.json",
        E39 / "results/probe_manifest.json",
        E39 / "results/units_train_val.json",
        E39 / "results/units_test.json",
        E42 / "results/semantic_probe_manifest.json",
        E44 / "inputs/items.jsonl",
        E45 / "results/individual_current_ratings.json",
        E45 / "results/inventory.json",
        E39 / "scripts/analysis_lib.py",
        E44 / "scripts/analyze_selection_utility.py",
        E45 / "scripts/analyze.py",
        E46 / "scripts/freeze_inputs.py",
        E46 / "scripts/analyze_information_properties.py",
        ROOT / "py_src/cert_judge/information_properties.py",
        ROOT / "tests/test_information_properties.py",
    ]
    paths += sorted((E39 / "results/harvest").glob("*.json"))
    paths += sorted((E42 / "results/harvest").glob("*.json"))
    paths += sorted((E42 / "probe_edits/audit").glob("*.json"))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=E46 / "results/input_manifest.json")
    args = parser.parse_args()
    source_paths = inputs()
    if not source_paths or any(not path.is_file() for path in source_paths):
        raise RuntimeError("allowlisted input inventory is incomplete")
    receipt = {
        "status": "FROZEN_BEFORE_CALCULATION",
        "scope": "PROTOCOL.md allowlist only; no private or external inputs",
        "files": {str(path.relative_to(ROOT)): sha256(path) for path in source_paths},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"files": len(source_paths), "output": str(args.output.relative_to(ROOT))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
