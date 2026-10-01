# CKPT: semantic weakening, over-constraint and vacuity probes (experiment 42)

**TLDR:** Resumable checkpoint for the skampere1 worker running experiment 42 (Lean-validated semantic probes scored by experiment 39's judges through Valkyrie).

Created: 09-30-2026 14:06 PDT
Last updated: 09-30-2026 19:58 PDT

Task: run experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges end to end on SNAP skampere1 per cc.md.

State:
- Phase: cc.md step 7 (landing). Analysis DONE: results/semantic_screen.json, results/index_association.json (experiment 39 criterion from origin/main 99e3496; test view post hoc after its TEST_RECEIPT.json), results/RESULTS_semantic_screen.md, REPORT.md; results.md DONE; README + experiments/README.md row + layout.json updated; tests 14 passed; experiment_layout --check OK. Judging totals: 32,592/32,592 reconciled, $656.15 Vals-reported. Next: PR, rebase on origin/main, merge, email, private/DONE.
- Services: nine pack services certjudge42-<key> on ports 9460-9468 behind cloudflared (receipts results/deployment_<key>.json; tunnel URLs private only). `$PY scripts/deploy_service.py --model <key> --status` re-checks. Never redeploy a model with a live run.
- Probes (final build): 194 valid of 250 declared -> 582 cells per config, 32,592 calls over 56 configs (+56 smoke). File-level audit labels in probe_edits/audit/ (weak 25 strict/31 redundant/1 unclear; overc 20/16/1).
- Receipts: agent_bundle_check PASS, agent_harness PASS (brando_terminus_gateway), packs PASS, controls written (results/harvest/ctl__*.json).
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

Progress 09-30-2026 18:38 PDT: 53/56 main runs terminal; 13 merged ($91.38). Harvest helper: nohup private/harvest_loop.sh (scripts/parallel_harvest.py, 6 workers) beside the driver. Next: watch main runs; update results.md charges after every merge; then analyze.py screen, wait for experiment 39 units_train_val.json, analyze.py index, REPORT.md, landing.

Blockers: none.
