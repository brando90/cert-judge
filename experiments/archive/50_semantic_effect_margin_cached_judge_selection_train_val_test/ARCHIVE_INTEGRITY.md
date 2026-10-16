# Archive integrity provenance

**Scope:** This receipt documents post-run archival integration only.  It does not alter or rerun the frozen selector, outcome evaluation, protocol, or numerical tables.

`results/evaluation_source_manifest.json` retains the exact evaluator-source hashes used before measurement at commit `683efe98cc57b5bcb484c14fb338d0e617ff71fc`.
`results/archive_source_provenance.json` separately records the current SHA-256 hashes of the archive-only path-resolution adaptations, verifies the original source blobs from Git, and pins every numerical body to published-results commit `8b721efeaec1ed0800825e9bf668b900c819d7db`.

The only archive adaptations are root/path resolution in `analyze_semantic_margin.py` and `freeze_evaluation_sources.py`, plus the test import’s archived path.
They did not execute selection or outcome evaluation.

Parent independently checked strict-probe coverage against corrected evaluator hash `52c31de97eee6a854d8ecf9f9bdebd9a55c6cd33c7214ea18d871e2ed981d14c`: four of five accepted strict-weakening probes passed the task coverage requirement; three of five failed it.

Run this non-mutating verification command from the repository root:

```bash
PYTHONPATH=py_src python3 - <<'PY'
import importlib.util
from pathlib import Path
p = Path('experiments/archive/50_semantic_effect_margin_cached_judge_selection_train_val_test/scripts/analyze_semantic_margin.py')
s = importlib.util.spec_from_file_location('e50_integrity', p)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
m.assert_freeze()
m.assert_evaluation_source_freeze()
print('archived integrity: PASS')
PY
```
