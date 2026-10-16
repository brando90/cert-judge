#!/usr/bin/env python3
"""Seal the evaluator-only correction made after experiment-50 selection."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
E50 = ROOT / "experiments/50_semantic_effect_margin_cached_judge_selection_train_val_test"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    paths = [
        E50 / "PROTOCOL.md",
        E50 / "scripts/analyze_semantic_margin.py",
        E50 / "scripts/freeze_evaluation_sources.py",
        ROOT / "tests/test_semantic_margin.py",
        ROOT / "py_src/cert_judge/information_properties.py",
        ROOT / "experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation/scripts/analyze_information_properties.py",
        ROOT / "experiments/archive/45_five_rater_cached_selection_task_split_and_behavioral_audit/scripts/analyze.py",
        ROOT / "experiments/archive/45_five_rater_cached_selection_task_split_and_behavioral_audit/scripts/inventory.py",
        ROOT / "experiments/archive/44_cached_score_judge_selection_utility/scripts/analyze_selection_utility.py",
        ROOT / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families/scripts/analysis_lib.py",
    ]
    selection = ["configuration_overview.json", "per_probe_task_components.json", "selectors.json", "selection_receipt.json"]
    payload = {
        "status": "EVALUATOR_CORRECTION_FROZEN_AFTER_SELECTION",
        "correction_date": "2026-10-16",
        "scope": "Correct evaluate_split unpacking and add deterministic adapter fixtures; no selector rerun or formula change.",
        "initial_source_manifest_sha256": sha256(E50 / "results/input_manifest.json"),
        "selection_receipt_sha256": sha256(E50 / "results/selection_receipt.json"),
        "selection_artifact_sha256": {name: sha256(E50 / "results" / name) for name in selection},
        "files": {str(path.relative_to(ROOT)): sha256(path) for path in paths},
    }
    out = E50 / "results/evaluation_source_manifest.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"files": len(paths), "output": str(out.relative_to(ROOT))}))


if __name__ == "__main__":
    main()
