# Experiment 58 frozen-analysis audit checkpoint

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex/e58-frozen-analysis-fixes/experiments/58_open_weight_judges_on_e39_e42_probes/CKPT_analysis_audit.md>

**TLDR:** E58 fixes verified; saved E60 primary statistic exactly reproduced. Complete E60 output exactly reproduced; recording the newer four-judge FarmShare partial and final cleanup.
Created: 10-26-2026 12:29 PDT
Last updated: 10-26-2026 13:10 PDT

## Goal
- Audit frozen E58 implementation, reconcile project status with coworker, preserve scientific choices and spending pause.
## What ran
- Owned branch `codex/e58-frozen-analysis-fixes`; merged latest main `523ef0e` (PRs 78–81); canonical checkout untouched.
- 40 combined E58/E60 tests pass, no skips; 9,927 prompt hashes match. Complete E60 saved output matches all 2,567 scalar values exactly.
- SNAP work root: `/lfs/skampere1/0/brando9/.agent-tasks/cj-e58-analysis-01a179a8`; no GPU/model calls.
- Completed sessions: `cj-e58-analysis-01a179a8`, `cj-e58-analysis-final-01a179a8`; both exit 0.
- Full E60 core and extra sensitivity both exit 0. PRs #82 (E58 repairs) and #84 (E60 input boundary) are open; zero inference.
## Results
- [Audit](RESULTS_analysis_audit.md), [receipt](results/audit_10-26-2026/REPRODUCTION.json), [live log](results/audit_10-26-2026/results.md).
## Stuck / blocked
- Mercury1 smoke dry-run complete. New PR #83 reports four FarmShare judges; raw archive requested from coworker after Mac authentication failed.
- Protocol/code gaps preserved and documented; main layout checker already fails on unregistered E59/E60 directories.
## Next steps
- [p 9/10] Finish source-unit gate check for PR #83, publish receipts, send completion and clean owned scratch/worktrees. Coworker owns E61 mercury2 GPUs 0–7.
- Inspect: `ssh skampere1 'tail -n 20 /lfs/skampere1/0/brando9/snap_jobs/cj-e58-farmshare-gate-01a179a8_latest.log'`.
- Test: `E58_VERIBENCH_REPO=/Users/brandomiranda/veribench /Users/brandomiranda/uv_envs/cert-judge/bin/python -m pytest -q experiments/58_open_weight_judges_on_e39_e42_probes/tests`.
## Brando to-do
- None; user requested at least one hour of work, through approximately 13:20 PDT.

## Log
- 10-26-2026 12:29 PDT -- Initial audit and cluster observations recorded; Codex owns fixes and cleanup of its managed checkout.
- 10-26-2026 12:46 PDT -- Final E58 suite and exact saved-data primary reproduction passed; checking E60 report fidelity and preparing publication.
- 10-26-2026 12:54 PDT -- PR #82 published; coworker confirmed E61 ownership. Retrieved and verified mercury1 smoke hash; corrected nested E60 archive paths and asserted all four input counts before restarting saved-data reproduction.
- 10-26-2026 13:10 PDT -- E60 full output and extra sensitivity exactly reproduce (2,567 values); PR #84 published. Found PR #83 FarmShare partial; checking its processed-unit gate and requested collected archive for raw verification.
