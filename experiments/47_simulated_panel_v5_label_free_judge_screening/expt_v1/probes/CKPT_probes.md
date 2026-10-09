# Frozen v5 probes checkpoint

**Doc link:** [Runbook](cc.md)
Created: 10-08-2026 10:51 PDT
Last updated: 10-08-2026 18:58 PDT

- Scope: only frozen probe construction/compilation; zero judge calls.
- Status: COMPLETE AND PUSHED. The compiler exited 0 with terminal manifests and no active compile jobs; attempt 4 was the one permitted postcompile finalizer, not a scoring-cell retry.
- Owner: named session codex-cj-e47-v5-probes; branch codex/cj-e47-v5-probes.
- Main integrator: /dfs/scratch0/brando9/cert-judge-e47-v5-sandbox.
- Inputs: pinned metadata at 79bbfa3; frozen E39 source; v5 source ccd86d467fd7577826c4b549df2c532bf43b1892.
- Expected scope: 50 references and 750 declared candidates, including 691 nonblank; verify manifest counts.
- Input terminal state: 750 declared fresh rows, 691 nonblank hash-verified candidates, 59 declared blanks, 50 unique reference hashes, and 50/50 verified G01 candidate hashes.
- Lean preflight: `/lfs/skampere1/0/brando9/vb90_grading/lean_project` declares `leanprover/lean4:v4.22.0`; `~/.elan/bin/lake --version` reports Lean 4.22.0. Its toolchain and lake-manifest hashes are recorded by the driver.
- Terminal manifests: source `c032ac46e92dfe2ed326b1372e21f8d69a6d2b719fffc1ca379ea33a507493aa`, probe `d41ceff706a47eebc6310935f983f4837c1e22b4a12091d0b15fc73abe4b743a`, summary `18771989748e56fc15ad9f1c5658ac259276482ecb006043c0c0b28a85eca62d`; independent audit PASS.
- Terminal compilation: 2,641 unique cache receipts, 1,711 success, 930 failure (421 elaboration, 392 type-or-elaboration, 110 parse, 4 unresolved-import, 3 timeout), one environment fingerprint.
- Published artifact commit: `aaed94c38cc67032acd58a90a4e669052de1b168` on `origin/codex/cj-e47-v5-probes`; commit-bound handoff/COMPLETE receipt is the final remaining scoped publication record.
- Next: main worker verifies and integrates this isolated probe commit; this worker must not run scoring or merge to main.
- Runtime: expt_v1/probes/runtime, run cj-e47-probes-10-08-2026-a1.
- Native usage read at postcompile finalization start: 10-08-2026 11:35 PDT receipt reports 7% used / 93% included weekly allowance remaining, with a 25% finishing reserve; this phase is capped at an estimated 3 percentage points, and prepaid spillover remains ineligible.
- Health preflight PASS relevant checks; shared storage 4735 GiB / local storage 9322 GiB free; warnings only. No graphics processors, 2 compile workers initially.
- Watchdog: /lfs/skampere1/0/brando9/snap_jobs/cj-e47-probes-watch.py; five-minute cron. Classification self-test passed locally; remote installation/first check pending. Root app heartbeat already covers main experiment, with this checkpoint linked.
