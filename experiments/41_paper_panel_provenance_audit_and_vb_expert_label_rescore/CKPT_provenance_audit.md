# Checkpoint: experiment 41 provenance audit

**Last updated:** 09-30-2026 14:02 PDT
**Worker:** Claude Sonnet 5, effort high, tmux `cj-e41-provenance-audit`, skampere1
**Branch:** `e41-provenance-audit` (clone: `/lfs/skampere1/0/brando9/cert-judge_e41`)
**Model calls so far:** 0 (zero-call analysis; this is a text/data audit)

## Environment
- Python: created `uv venv /lfs/skampere1/0/brando9/venvs/cj_e41` (vb103_venv lacked numpy/scipy/pandas) and
  `uv pip install --python /lfs/skampere1/0/brando9/venvs/cj_e41/bin/python numpy scipy pandas` (numpy 2.4.6,
  scipy 1.17.1, pandas 3.1.0rc0).
- Read-only VeriBench clone: `/lfs/skampere1/0/brando9/veribench_e41` (never commit there).
- Did not touch experiment 39's folder, checkout (`cert-judge_e39`), Valkyrie benchmark, or ports 8990-8998.

## Progress
- [x] Step 0: snap_health.sh run (WARNs are pre-existing on unrelated shared-dfs repos, not this task).
- [x] Step 1: branch `e41-provenance-audit` created off `origin/main`; this checkpoint created; `results.md` set to RUNNING.
- [ ] Step 2: label identity matching (`results/label_identity.json`)
- [ ] Step 3: rating dates / rater-seen references
- [ ] Step 4: judge-seen references (`results/provenance_by_task.csv`)
- [ ] Step 5: Gate G0 (`results/G0_reproduction.json`)
- [ ] Step 6: Views V1-V5, S1-S4 (`scripts/rescore.py`, `scripts/test_rescore.py`)
- [ ] Step 7: REPORT.md
- [ ] Step 8: land (PR, merge, email receipt, `private/DONE`)

## Notes / deviations
(none yet)

## Resume instructions
If interrupted, re-read this file and `results.md`, then continue from the first unchecked step above.
