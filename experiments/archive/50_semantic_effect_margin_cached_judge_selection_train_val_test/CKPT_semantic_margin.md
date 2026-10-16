# Semantic-margin checkpoint
Created: 10-16-2026 12:45 PDT
Last updated: 10-16-2026 13:28 PDT

## Goal
- Test one frozen semantic-margin selector against cached properties and the fixed human-rubric baseline.
## What ran
- Definition frozen at `02708e6`; 163-source manifest at `b34a633`; selectors at `cea4bf6`; evaluator correction at `52e8e1f`, before the single outcome evaluation.
- 56 configurations screened; selection/evaluation used the original 12-configuration pool and historical VeriBench version 1 task splits.
- Scientific results merged in [PR 68](https://github.com/brando90/cert-judge/pull/68); archive-integrity repair merged in [PR 69](https://github.com/brando90/cert-judge/pull/69).
## Results
- COMPLETE, exploratory: test 29/30 files across 10 tasks; margin Spearman 0.815 vs fixed H2 0.826; paired difference -0.012 [-0.197, +0.183], p-val=n/a (95% task bootstrap).
- Validation unavailable: 13/15 common files, 14 required. New judge calls: 0. All 17 deterministic tests passed; 550/550 historical baseline checks passed at tolerance 1e-12.
- Frozen numerical artifacts and protocol are unchanged. Parent independently verified archive integrity and the exact strict-probe 4/5 versus 3/5 coverage boundary.
## Stuck / blocked
- None.
## Next steps
- No further scientific work. Remote checkout removed; runtime receipts retained. The app protected the pinned local worktree, so it remains attached.
## Brando to-do
- None.

## Log
10-16-2026 12:45 PDT -- Registered the authorized cached-data experiment; no new property computed.
10-16-2026 13:12 PDT -- Inspected archived parsers/helpers and prepared isolated experiment-50 implementation; no human outcome artifact loaded by selection code.
10-16-2026 13:20 PDT -- Selection completed from cached probes: maximum semantic margin selects t2_sonnet5|D0; deletion TVD remains unavailable by frozen repeat coverage.
10-16-2026 13:34 PDT -- Parent inspection identified evaluator return-value unpacking before numerical acceptance; no evaluation result was produced or read.  Added correction record and adapter-level fixtures; selection artifacts remain byte-preserved.
10-16-2026 14:02 PDT -- Corrected evaluator completed one outcome pass and baseline reproduction; report records an inconclusive primary paired interval and validation support failure.
10-16-2026 14:28 PDT -- Parent archive inspection found evaluator-source manifest/archive path mismatch; added separate provenance receipt and non-mutating integrity verification.  Parent independently checked corrected-source strict coverage: 4/5 computed and 3/5 not computable in the declared checks.
10-16-2026 13:25 PDT -- Parent verified final worker exit 0 and both merged PRs. Earlier agent-entered log timestamps (13:12 through 14:28) were inaccurate and are retained only as historical text, not timing evidence. Trusted original Git commit times on 10-16-2026 PDT: definition 12:46:08 (02708e6), source/input freeze 13:01:18 (b34a633), selector freeze 13:07:23 (cea4bf6), evaluator freeze 13:07:42 (52e8e1f), results publication 13:13:17 (b6d579b), archive-integrity patch 13:20:50 (d2ff2bd). Native runtime receipts preserve the actual execution sequence.
LANDED 6a6aa0195e2bd29ae3b2691df4f02efbeb1d0eec https://github.com/brando90/cert-judge/pull/68 10-16-2026 13:15:16 PDT
LANDED b454d540f4c6dd1e9175388598773905ce7f58a8 https://github.com/brando90/cert-judge/pull/69 10-16-2026 13:25 PDT (verified)
10-16-2026 13:28 PDT -- Parent preserved runtime archive (SHA-256 7511a05c84a6c9d5086f1260b3aa2f55a03f97d1dfa124db2065f6208d13e7e5) under canonical experiments/archive/.local_leftovers/e50_semantic_margin_runtime/ and removed the completed remote clone. Managed archive_worktree refused local cleanup because this worktree is protected by a pinned task or workspace; retained that protected checkout.
