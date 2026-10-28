# Experiment 58 frozen-analysis audit checkpoint

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/58_open_weight_judges_on_e39_e42_probes/CKPT_analysis_audit.md>

**TLDR:** E58 fixes verified; saved E60 primary statistic exactly reproduced. Complete E60 output and published FarmShare gate statistics exactly reproduced; fixes and receipts published.
Created: 10-26-2026 12:29 PDT
Last updated: 10-26-2026 14:56 PDT

## Goal
- Audit frozen E58 implementation, reconcile project status with coworker, preserve scientific choices and spending pause.
## What ran
- Owned branch `codex/e58-frozen-analysis-fixes`; synced main `19b0b9d` (through PR #86); canonical checkout untouched.
- 40 combined E58/E60 tests pass, no skips; 9,927 prompt hashes match. Complete E60 saved output matches all 2,567 scalar values exactly.
- Prior six SNAP sessions finished and were removed. New CPU package is prepared at `/lfs/skampere1/0/brando9/.agent-tasks/cj-e58-raw-01a179a8`; no analysis launched without the archive.
- Completed sessions: `cj-e58-analysis-01a179a8`, `cj-e58-analysis-final-01a179a8`; both exit 0.
- Full E60 core and extra sensitivity both exit 0. PRs #82 (E58 repairs) and #84 (E60 input boundary) are open; zero inference.
## Results
- [Audit](RESULTS_analysis_audit.md), [receipt](results/audit_10-26-2026/REPRODUCTION.json), [live log](results/audit_10-26-2026/results.md).
## Stuck / blocked
- Mercury1 smoke dry-run complete. New PR #83 reports four FarmShare judges; raw archive requested again at 14:38: [delivery request](https://github.com/brando90/agents-config/issues/68#issuecomment-6427967589); Mac and SNAP-to-FarmShare BatchMode authentication fail. No Duo attempted.
- Protocol/code gaps preserved and documented; main layout checker already fails on unregistered E59/E60 directories.
## Next steps
- [p 9/10, done] Repairs and reproductions published. E60 checkout archived; E58 checkout retained because the app protects its active primary checkout.
- [p 10/10, active] Heartbeat `certjudge-finish-farmshare-raw-verification` checks every 10 minutes. Once archive SHA `3fd6e86c...` arrives at `skampere1:/lfs/skampere1/0/brando9/e58-transfer/e58_results.tgz`, inspect prior execution state and run the prepared `run_farmshare_raw.sh` once via `SNAP_HOST=skampere1 bash ~/agents-config/scripts/snap_dispatch.sh run cj-e58-raw-01a179a8 'bash /lfs/skampere1/0/brando9/.agent-tasks/cj-e58-raw-01a179a8/run_farmshare_raw.sh'`.
- Test: `E58_VERIBENCH_REPO=/Users/brandomiranda/veribench /Users/brandomiranda/uv_envs/cert-judge/bin/python -m pytest -q experiments/58_open_weight_judges_on_e39_e42_probes/tests`.
## Brando to-do
- None. Coworker has the archive request, protocol-gap list, PR links and current hardware snapshot.

## Log
- 10-26-2026 12:29 PDT -- Initial audit and cluster observations recorded; Codex owns fixes and cleanup of its managed checkout.
- 10-26-2026 12:46 PDT -- Final E58 suite and exact saved-data primary reproduction passed; checking E60 report fidelity and preparing publication.
- 10-26-2026 12:54 PDT -- PR #82 published; coworker confirmed E61 ownership. Retrieved and verified mercury1 smoke hash; corrected nested E60 archive paths and asserted all four input counts before restarting saved-data reproduction.
- 10-26-2026 13:10 PDT -- E60 full output and extra sensitivity exactly reproduce (2,567 values); PR #84 published. Found PR #83 FarmShare partial; checking its processed-unit gate and requested collected archive for raw verification.
- 10-26-2026 13:18 PDT -- Four-judge processed-unit gates match exactly; all owned CPU jobs complete. Artifacts and logs preserved under canonical private audit path; temporary remote/local scratch removed and E60 worktree archived. E58 primary checkout retained by app constraint.
- 10-26-2026 14:46 PDT -- Resumed at Brando's request. Main log updates merged; expected raw-verification outcomes committed before acquisition. New read-only verifier passes 14 corruption controls; combined E58 suite 46 passed. Retrieved three mercury1 smoke source files with matching remote hashes and exactly replayed all 521 cells from 20 raw responses. FarmShare transfer pending; existing Chrome, Drive, mail and local Downloads searches found no archive.
- 10-26-2026 14:56 PDT -- PR #82 head dc70591 and Google companion updated and read back. Prepared remote package SHA d74074a3b216a08729eeef9bbf4033e423a6df6abb76d1dbaf3a13da14aabf58 verifies and imports; skampere1 has 2,294,290,206,720 bytes free despite percentage-based disk warnings, sufficient for this bounded CPU audit. The fixed-archive runner is syntax checked; no snapshot or EXIT_CODE exists. Heartbeat created ACTIVE and viewed; it owns continuation and eventual cleanup of prepared scratch/transfer. Canonical private copies are hash-verified. RUN START mail 1a17a28a33e66195 awaits matching DONE after verification. WhatsApp browser needs linking and desktop controls did not send; issue/email are the confirmed cowork channels.
