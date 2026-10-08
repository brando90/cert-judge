# Frozen v5 probes checkpoint

**Doc link:** [Runbook](cc.md)
Created: 10-08-2026 10:51 PDT
Last updated: 10-08-2026 10:51 PDT

- Scope: only frozen probe construction/compilation; zero judge calls.
- Status: prepared, launch not yet verified.
- Owner: named session codex-cj-e47-v5-probes; branch codex/cj-e47-v5-probes.
- Main integrator: /dfs/scratch0/brando9/cert-judge-e47-v5-sandbox.
- Inputs: pinned metadata at 79bbfa3; frozen E39 source; v5 source ccd86d467fd7577826c4b549df2c532bf43b1892.
- Expected scope: 50 references and 750 declared candidates, including 691 nonblank; verify manifest counts.
- Next: read runbook; verify copied input hashes/toolchain; build and compile full required ladders.
- Runtime: expt_v1/probes/runtime, run cj-e47-probes-10-08-2026-a1.
- Remote usage receipt 10:46 PDT: weekly 5% used, 95% remaining; included subscription. Next-phase estimate up to 10 percentage points, 25% finishing reserve; two execution coordinators shared. Purchased-credit spillover unverified/ineligible.
- Health preflight PASS relevant checks; shared storage 4735 GiB / local storage 9322 GiB free; warnings only. No graphics processors, 2 compile workers initially.
- Watchdog: /lfs/skampere1/0/brando9/snap_jobs/cj-e47-probes-watch.py; five-minute cron. Classification self-test passed locally; remote installation/first check pending. Root app heartbeat already covers main experiment, with this checkpoint linked.
