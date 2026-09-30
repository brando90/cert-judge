# CKPT: semantic weakening, over-constraint and vacuity probes (experiment 42)

**TLDR:** Resumable checkpoint for the skampere1 worker running experiment 42 (Lean-validated semantic probes scored by experiment 39's judges through Valkyrie).

Created: 09-30-2026 14:06 PDT
Last updated: 09-30-2026 14:51 PDT

Task: run experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges end to end on SNAP skampere1 per cc.md.

State:
- Phase: cc.md step 2 (probe construction, zero judge calls). Code written: scripts/{e42,lean_text,semantic_probes,build_semantic_probes,build_panel,analyze,test_e42}.py; transport vendored from experiment 39 @9823689 (deploy_service, judge_controller, driver, worker_loop.sh, pack, render_cells, local_controls, legacy, verify_bundle, verify_agent_harness) with certjudge42-<key> benchmarks, ports 9460-9468, run labels cj42-*; driver admits nothing until private/GATE_OPEN exists and writes private/JUDGING_DONE (never private/DONE).
- Tests: `$PY -m pytest scripts/test_e42.py -q` -> 14 passed (incl. Lean-backed harness test: strengthening and equivalent edits rejected, weakening accepted).
- Lean: shared project /lfs/skampere1/0/brando9/vb90_grading/lean_project used read-only (no reference imports VeriBench, so experiment 39's prelude mirror is not needed). 24/25 references elaborate; 1_MyAdd fails (unsolved goals line 195, same as experiment 39) -> task excluded fail-closed.
- Check design: each semantic probe's check file axiomatizes every data-valued implementation def (and where-helpers), sets theorem proofs to sorry, drops tests; forward reference=>probe per changed theorem and per edited Prop def must be proved without sorryAx; reverse auto-attempted, all-proved = excluded as equivalent; overc hypotheses proved unsatisfiable; formatting probes must #print identical declarations.
- Trial build (auto families, 09-30 ~15:00): ident 24/25, vac_true 19, vac_hyp 19, overc 33/50 (before heap fix), fmt_comments 19, fmt_layout 19 valid.
- Weakening edits: probe_edits/<task>.json; 0_bisect_right written by the worker (3/3 valid); 5 *_safe tasks have no levels (Post := True); 18 tasks being proposed by 6 Claude Code subagents (claude-opus-5-5, subscription) under probe_edits/PROPOSER_BRIEF.md.
- results/panel.json (56 LLM + 4 controls, prompt fingerprints identical to experiment 39's) and results/selectors.json (experiment 39's recorded selectors: gem31h google/gemini-3.1-pro-preview, qwen36/t2_qwen alibaba/qwen3.6-27b).
- Worker: tmux `cj-e42-semantic-probes` on skampere1; clauded (personal profile, --dangerously-skip-permissions), model claude-opus-5-5, effort high. Model switches: none so far.
- Clone: /lfs/skampere1/0/brando9/cert-judge_e42, branch `e42-semantic-probes` cut from origin/main 7b10d95.
- Read-only worktree of experiment 39's live branch (never written): /lfs/skampere1/0/brando9/cert-judge_e42_e39ro at origin/e39-proxy-index-search b0f3488.
- VeriBench read-only clone: /lfs/skampere1/0/brando9/veribench_e42 at c6d9ed180.
- Health: `snap_health.sh --node skampere1` -> one FAIL (shared DFS 96% used, 3088 GiB free), not relevant: all files on node-local /lfs; WARN rows are dirty shared DFS checkouts this task does not touch.
- Experiment 39 status at 14:03 PDT: smoke stage in progress (its results.md: no transport-smoke PASS yet) -> wait gate closed.

Next: step 2 (probe construction, zero judge calls).

Blockers: none.
