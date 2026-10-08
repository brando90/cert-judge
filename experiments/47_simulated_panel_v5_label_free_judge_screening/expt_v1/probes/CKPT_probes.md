# Frozen v5 probes checkpoint

**Doc link:** [Runbook](cc.md)
Created: 10-08-2026 10:51 PDT
Last updated: 10-08-2026 11:33 PDT

- Scope: only frozen probe construction/compilation; zero judge calls.
- Status: RUNNING. The previous foreground driver (process 325184) exited without terminal manifests after retaining 55 hash-bound receipts (18 successful, 37 failed); its cache is preserved. Resumed sole driver is process 689488 in tmux `codex-cj-e47-v5-probes:probe-build-resume`, with exactly two compile workers and the same cache/environment; it has 99 receipts (40 successful, 59 failed), zero timeouts, and two live Lean children at this checkpoint.
- Owner: named session codex-cj-e47-v5-probes; branch codex/cj-e47-v5-probes.
- Main integrator: /dfs/scratch0/brando9/cert-judge-e47-v5-sandbox.
- Inputs: pinned metadata at 79bbfa3; frozen E39 source; v5 source ccd86d467fd7577826c4b549df2c532bf43b1892.
- Expected scope: 50 references and 750 declared candidates, including 691 nonblank; verify manifest counts.
- Input preflight: 750 declared fresh rows, 691 nonblank and 59 blank from the frozen main plus late manifests; exactly 50 unique reference hashes are being copied and verified. The permitted source copy presently has no G01 candidate bytes despite 50 nonblank G01 declarations; main owner is recovering only exact pinned, manifest-hash-matched bytes. Do not finalize G01 as unavailable.
- Lean preflight: `/lfs/skampere1/0/brando9/vb90_grading/lean_project` declares `leanprover/lean4:v4.22.0`; `~/.elan/bin/lake --version` reports Lean 4.22.0. Its toolchain and lake-manifest hashes are recorded by the driver.
- G01 recovery: main delivered all 50 allowed G01 blobs into its input copy at 10-08-2026 11:20 PDT. Local verification found 50 files and 50/50 `cand_sha256` matches against the frozen manifest; the current pass has copied and hash-verified all G01 bytes, and its cache will be reused for any later resumable pass.
- Runtime liveness: `runtime/active_jobs.json` now carries the live compiler in its nonempty `jobs` list as well as its detailed driver receipt, so the serial supervisor will adopt it rather than launch a competing writer. The tmux-owned compiler and host monitor are healthy.
- Duration decision: retain the two-worker bound under the observed host load. The frozen bug-mutation search has variable attempts; 741 distinct base sources and up to 3,014 original/deletion proposals precede those searches, so terminal compilation is expected to require hours rather than a short coordinator turn. Preserve receipts and continue rather than cut scope.
- Next: observe process 689488 through all available declared source/probe hashes, then validate and publish terminal manifests. If it exits before terminal manifests, start only the exact hash-resumable continuation from the preserved cache under the existing three-attempt limit.
- Runtime: expt_v1/probes/runtime, run cj-e47-probes-10-08-2026-a1.
- Remote usage receipt 10:46 PDT: weekly 5% used, 95% remaining; included subscription. Next-phase estimate up to 10 percentage points, 25% finishing reserve; two execution coordinators shared. Purchased-credit spillover unverified/ineligible.
- Health preflight PASS relevant checks; shared storage 4735 GiB / local storage 9322 GiB free; warnings only. No graphics processors, 2 compile workers initially.
- Watchdog: /lfs/skampere1/0/brando9/snap_jobs/cj-e47-probes-watch.py; five-minute cron. Classification self-test passed locally; remote installation/first check pending. Root app heartbeat already covers main experiment, with this checkpoint linked.
