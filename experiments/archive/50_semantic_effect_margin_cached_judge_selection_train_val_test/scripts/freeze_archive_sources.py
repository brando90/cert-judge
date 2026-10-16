#!/usr/bin/env python3
"""Create post-run archive-only source provenance; never runs scientific phases."""
from __future__ import annotations
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
E50 = Path(__file__).resolve().parents[1]
ACTIVE = "experiments/50_semantic_effect_margin_cached_judge_selection_train_val_test/"
ARCHIVE = "experiments/archive/50_semantic_effect_margin_cached_judge_selection_train_val_test/"
SELECT_COMMIT = "2bcebd51d364bacbf4fc95bdae0d5eb99679e8df"
EVALUATION_COMMIT = "683efe98cc57b5bcb484c14fb338d0e617ff71fc"
PUBLISHED_COMMIT = "8b721efeaec1ed0800825e9bf668b900c819d7db"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def blob(commit, name): return hashlib.sha256(subprocess.run(["git", "show", f"{commit}:{name}"], cwd=ROOT, check=True, capture_output=True).stdout).hexdigest()
def main():
    input_manifest = json.loads((E50 / "results/input_manifest.json").read_text())
    eval_manifest = json.loads((E50 / "results/evaluation_source_manifest.json").read_text())
    adapted = ["scripts/analyze_semantic_margin.py", "scripts/freeze_evaluation_sources.py"]
    test = "tests/test_semantic_margin.py"
    records = []
    for suffix in adapted:
        old, new = ACTIVE + suffix, ARCHIVE + suffix
        records.append({"original_path": old, "archive_path": new, "evaluation_source_commit": EVALUATION_COMMIT, "evaluation_sha256": eval_manifest["files"][old], "archive_sha256": sha(ROOT / new), "reason": "archive-root discovery/path resolution only; no scientific computation rerun"})
    records.append({"original_path": test, "archive_path": test, "evaluation_source_commit": EVALUATION_COMMIT, "evaluation_sha256": eval_manifest["files"][test], "archive_sha256": sha(ROOT / test), "reason": "test importer changed from active to archived experiment path"})
    pre = []
    for name in (ACTIVE + "scripts/analyze_semantic_margin.py", ACTIVE + "scripts/freeze_inputs.py", test):
        pre.append({"path": name, "selection_source_commit": SELECT_COMMIT, "sha256": input_manifest["files"][name]})
    bodies = ["results/configuration_overview.json", "results/per_probe_task_components.json", "results/selectors.json", "results/selection_receipt.json", "results/evaluation.json", "results/association.json", "results/robustness.json", "results/runtime.json"]
    payload = {"status": "ARCHIVE_SOURCE_PROVENANCE_FROZEN", "scope": "Post-run archival integration only; original protocol, manifests, selectors, and numerical bodies remain frozen.", "original_evaluation_source_manifest_sha256": sha(E50 / "results/evaluation_source_manifest.json"), "archive_adaptations": records, "preselection_source_blobs": pre, "frozen_numerical_bodies": [{"relative_path": n, "published_results_commit": PUBLISHED_COMMIT, "sha256": sha(E50 / n)} for n in bodies]}
    out = E50 / "results/archive_source_provenance.json"; out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"archive_adaptations": len(records), "numerical_bodies": len(bodies), "output": str(out.relative_to(ROOT))}))
if __name__ == "__main__": main()
