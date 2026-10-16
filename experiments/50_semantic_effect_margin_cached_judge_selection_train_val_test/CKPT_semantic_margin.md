# Semantic-margin checkpoint
Created: 10-16-2026 12:45 PDT
Last updated: 10-16-2026 13:34 PDT

## Goal
- Test one frozen semantic-margin selector against cached properties and human-rubric baseline.
## What ran
- Committed/pushed source and 163-file resolved manifest before calculation (`b34a633`).
- Ran selection only: 56 configuration overview and per-probe/task components written; receipt records `human_outcomes_read=false` and selector SHA-256 `5cce7bd559bfae1ddd3fb531ef268aeb0cafaf5f5fc5b79b31b24254523bd858`.
- Parent inspection stopped the worker before evaluation: `evaluate_split` mis-unpacked the adapter return.  Correcting evaluator/test code only; selector bytes are preserved and will be committed before outcomes are read.
## Results
- None yet; new judge calls 0.
## Stuck / blocked
- None.
## Next steps
- Commit/push frozen selectors plus the dated evaluator-correction receipt, then run the outcome evaluation exactly once.
## Brando to-do
- None.

## Log
10-16-2026 12:45 PDT -- Registered the authorized cached-data experiment; no new property computed.
10-16-2026 13:12 PDT -- Inspected archived parsers/helpers and prepared isolated experiment-50 implementation; no human outcome artifact loaded by selection code.
10-16-2026 13:20 PDT -- Selection completed from cached probes: maximum semantic margin selects t2_sonnet5|D0; deletion TVD remains unavailable by frozen repeat coverage.
10-16-2026 13:34 PDT -- Parent inspection identified evaluator return-value unpacking before numerical acceptance; no evaluation result was produced or read.  Added correction record and adapter-level fixtures; selection artifacts remain byte-preserved.
