# Frozen v5 probes checkpoint

**Doc link:** [Runbook](cc.md)
Created: 10-08-2026 10:51 PDT
Last updated: 10-08-2026 11:13 PDT

- Scope: only frozen probe construction/compilation; zero judge calls.
- Status: RUNNING. A detached shell launch (process 309635) did not retain the driver and produced no receipt. The bounded foreground handoff is verified live as process 325184 with two Lean children; the persistent hash cache has 48 source-hash receipts at 10-08-2026 11:13 PDT. `runtime/active_jobs.json` and `runtime/driver.lock` identify the healthy sole coordinator for the supervisor.
- Owner: named session codex-cj-e47-v5-probes; branch codex/cj-e47-v5-probes.
- Main integrator: /dfs/scratch0/brando9/cert-judge-e47-v5-sandbox.
- Inputs: pinned metadata at 79bbfa3; frozen E39 source; v5 source ccd86d467fd7577826c4b549df2c532bf43b1892.
- Expected scope: 50 references and 750 declared candidates, including 691 nonblank; verify manifest counts.
- Input preflight: 750 declared fresh rows, 691 nonblank and 59 blank from the frozen main plus late manifests; exactly 50 unique reference hashes are being copied and verified. The permitted source copy has no G01 candidate bytes despite 50 nonblank G01 declarations, so those criterion rows will be retained as `missing_source` rather than searched outside the allowlist.
- Lean preflight: `/lfs/skampere1/0/brando9/vb90_grading/lean_project` declares `leanprover/lean4:v4.22.0`; `~/.elan/bin/lake --version` reports Lean 4.22.0. Its toolchain and lake-manifest hashes are recorded by the driver.
- G01 recovery: the master verified that all 50 allowed G01 candidate blobs exist in the exact pinned v5 tree and will deliver hash-verified bytes into the allowed input copy. This run retains provisional missing-source G01 rows only; do not finalize them. The next resumable pass will consume the delivered bytes and reuse every unaffected hash receipt.
- Next: keep the verified driver alive through all declared source/probe hashes, then validate and publish its terminal manifests.
- Runtime: expt_v1/probes/runtime, run cj-e47-probes-10-08-2026-a1.
- Remote usage receipt 10:46 PDT: weekly 5% used, 95% remaining; included subscription. Next-phase estimate up to 10 percentage points, 25% finishing reserve; two execution coordinators shared. Purchased-credit spillover unverified/ineligible.
- Health preflight PASS relevant checks; shared storage 4735 GiB / local storage 9322 GiB free; warnings only. No graphics processors, 2 compile workers initially.
- Watchdog: /lfs/skampere1/0/brando9/snap_jobs/cj-e47-probes-watch.py; five-minute cron. Classification self-test passed locally; remote installation/first check pending. Root app heartbeat already covers main experiment, with this checkpoint linked.
