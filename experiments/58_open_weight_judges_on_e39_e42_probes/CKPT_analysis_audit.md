# Experiment 58 frozen-analysis audit checkpoint

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex/e58-frozen-analysis-fixes/experiments/58_open_weight_judges_on_e39_e42_probes/CKPT_analysis_audit.md>

**TLDR:** E58 fixes verified; saved E60 primary statistic exactly reproduced. Completing publication and a separate saved-data E60 reproduction without new judge calls.
Created: 10-26-2026 12:29 PDT
Last updated: 10-26-2026 12:46 PDT

## Goal
- Audit frozen E58 implementation, reconcile project status with coworker, preserve scientific choices and spending pause.
## What ran
- Owned branch `codex/e58-frozen-analysis-fixes`; base `0c21bf1` (main already contains PRs 78–80); canonical checkout untouched.
- 32 tests pass, no skips; 9,927 prompt hashes match. E60 compatibility primary object exactly matches saved output at 10,000 draws.
- SNAP work root: `/lfs/skampere1/0/brando9/.agent-tasks/cj-e58-analysis-01a179a8`; no GPU/model calls.
- Completed sessions: `cj-e58-analysis-01a179a8`, `cj-e58-analysis-final-01a179a8`; both exit 0.
- Full E60 cached-data reproduction: `cj-e60-reproduction-01a179a8`, one CPU/3 GiB/1,800-second cap; source archives copied, originals untouched.
## Results
- [Audit](RESULTS_analysis_audit.md), [receipt](results/audit_10-26-2026/REPRODUCTION.json), [live log](results/audit_10-26-2026/results.md).
## Stuck / blocked
- Original E58 harvest/job receipt not found in named inspected locations. Coworker inbox messages sent; no reply yet.
- Protocol/code gaps preserved and documented; main layout checker already fails on unregistered E59/E60 directories.
## Next steps
- [p 9/10] Publish fixes-only PR and Google companion; verify full E60 reproduction; send completion and cleanup owned scratch/worktree.
- Inspect: `ssh skampere1 'tail -n 20 /lfs/skampere1/0/brando9/snap_jobs/cj-e60-reproduction-01a179a8_latest.log'`.
- Test: `E58_VERIBENCH_REPO=/Users/brandomiranda/veribench /Users/brandomiranda/uv_envs/cert-judge/bin/python -m pytest -q experiments/58_open_weight_judges_on_e39_e42_probes/tests`.
## Brando to-do
- None; user requested at least one hour of work, through approximately 13:20 PDT.

## Log
- 10-26-2026 12:29 PDT -- Initial audit and cluster observations recorded; Codex owns fixes and cleanup of its managed checkout.
- 10-26-2026 12:46 PDT -- Final E58 suite and exact saved-data primary reproduction passed; checking E60 report fidelity and preparing publication.
