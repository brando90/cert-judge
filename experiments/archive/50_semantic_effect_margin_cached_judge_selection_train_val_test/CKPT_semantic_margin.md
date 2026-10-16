# Semantic-margin checkpoint
Created: 10-16-2026 12:45 PDT
Last updated: 10-16-2026 14:28 PDT

## Goal
- Test one frozen semantic-margin selector against cached properties and human-rubric baseline.
## What ran
- Committed/pushed source and 163-file resolved manifest before calculation (`b34a633`).
- Ran selection only: 56 configuration overview and per-probe/task components written; receipt records `human_outcomes_read=false` and selector SHA-256 `5cce7bd559bfae1ddd3fb531ef268aeb0cafaf5f5fc5b79b31b24254523bd858`.
- Parent inspection stopped the worker before evaluation: `evaluate_split` mis-unpacked the adapter return.  Correcting evaluator/test code only; selector bytes are preserved and will be committed before outcomes are read.
- Corrected evaluator was sealed in `52e8e1f`, then evaluated once: validation unavailable at 13/15 common files (14 required); test computed on 29/30 files across 10 tasks.  Margin Spearman 0.815 [0.414, 0.950] vs H2 0.826 [0.507, 0.934]; paired difference -0.012 [-0.197, +0.183].
- Reproduction against experiment 46 PASS: 550 comparable cells at absolute tolerance 1e-12; 15 deterministic tests passed.
- Archive integrity follow-up: original evaluator blob hashes and current archive-only source hashes are separately pinned; 17 deterministic tests now validate both source layers and reject tampered declared source/data.
## Results
- None yet; new judge calls 0.
## Stuck / blocked
- None; follow-up archive-integrity PR/landing receipt remain.
## Next steps
- Merge archive-integrity follow-up without rerunning scientific phases.
## Brando to-do
- None.

## Log
10-16-2026 12:45 PDT -- Registered the authorized cached-data experiment; no new property computed.
10-16-2026 13:12 PDT -- Inspected archived parsers/helpers and prepared isolated experiment-50 implementation; no human outcome artifact loaded by selection code.
10-16-2026 13:20 PDT -- Selection completed from cached probes: maximum semantic margin selects t2_sonnet5|D0; deletion TVD remains unavailable by frozen repeat coverage.
10-16-2026 13:34 PDT -- Parent inspection identified evaluator return-value unpacking before numerical acceptance; no evaluation result was produced or read.  Added correction record and adapter-level fixtures; selection artifacts remain byte-preserved.
10-16-2026 14:02 PDT -- Corrected evaluator completed one outcome pass and baseline reproduction; report records an inconclusive primary paired interval and validation support failure.
10-16-2026 14:28 PDT -- Parent archive inspection found evaluator-source manifest/archive path mismatch; added separate provenance receipt and non-mutating integrity verification.  Parent independently checked corrected-source strict coverage: 4/5 computed and 3/5 not computable in the declared checks.
