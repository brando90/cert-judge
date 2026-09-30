# CKPT: semantic weakening, over-constraint and vacuity probes (experiment 42)

**TLDR:** Resumable checkpoint for the skampere1 worker running experiment 42 (Lean-validated semantic probes scored by experiment 39's judges through Valkyrie).

Created: 09-30-2026 14:06 PDT
Last updated: 09-30-2026 14:06 PDT

Task: run experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges end to end on SNAP skampere1 per cc.md.

State:
- Phase: cc.md step 1 (checkpoint + ledger RUNNING).
- Worker: tmux `cj-e42-semantic-probes` on skampere1; clauded (personal profile, --dangerously-skip-permissions), model claude-opus-5-5, effort high. Model switches: none so far.
- Clone: /lfs/skampere1/0/brando9/cert-judge_e42, branch `e42-semantic-probes` cut from origin/main 7b10d95.
- Read-only worktree of experiment 39's live branch (never written): /lfs/skampere1/0/brando9/cert-judge_e42_e39ro at origin/e39-proxy-index-search b0f3488.
- VeriBench read-only clone: /lfs/skampere1/0/brando9/veribench_e42 at c6d9ed180.
- Health: `snap_health.sh --node skampere1` -> one FAIL (shared DFS 96% used, 3088 GiB free), not relevant: all files on node-local /lfs; WARN rows are dirty shared DFS checkouts this task does not touch.
- Experiment 39 status at 14:03 PDT: smoke stage in progress (its results.md: no transport-smoke PASS yet) -> wait gate closed.

Next: step 2 (probe construction, zero judge calls).

Blockers: none.
