#!/usr/bin/env python3
"""Freeze experiment-50's resolved, allowlisted cached-data inputs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
E50 = Path(__file__).resolve().parents[1]
E46 = ROOT / "experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation"

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    old = json.loads((E46 / "results/input_manifest.json").read_text())["files"]
    paths = {Path(name) for name in old} | {Path("experiments/50_semantic_effect_margin_cached_judge_selection_train_val_test/PROTOCOL.md"), Path("experiments/50_semantic_effect_margin_cached_judge_selection_train_val_test/scripts/analyze_semantic_margin.py"), Path("experiments/50_semantic_effect_margin_cached_judge_selection_train_val_test/scripts/freeze_inputs.py"), Path("experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation/scripts/analyze_information_properties.py"), Path("experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation/results/selectors.json"), Path("experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation/results/selector_utility.json"), Path("experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation/results/property_rows.json"), Path("experiments/archive/45_five_rater_cached_selection_task_split_and_behavioral_audit/scripts/inventory.py"), Path("tests/test_information_properties.py"), Path("tests/test_semantic_margin.py")}
    files = {str(p): digest(ROOT / p) for p in sorted(paths)}
    payload = {"status": "FROZEN_BEFORE_CALCULATION", "scope": "protocol allowlist; E46 archive path resolved from historical experiments/46_", "path_resolution": {"historical_prefix": "experiments/46_", "resolved_prefix": "experiments/archive/46_", "meaning": "archive-only relocation; numerical input bytes are verified by SHA-256"}, "files": files}
    out = E50 / "results/input_manifest.json"; out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"files": len(files), "output": str(out.relative_to(ROOT))}))
if __name__ == "__main__": main()
