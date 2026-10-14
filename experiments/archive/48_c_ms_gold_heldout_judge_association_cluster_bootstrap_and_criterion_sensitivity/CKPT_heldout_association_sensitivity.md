# CKPT — experiment 48 held-out association sensitivity

Created: 10-14-2026 12:50 PDT
Last updated: 10-14-2026 13:19 PDT

1. **Goal** — is experiment 39's held-out `C_ms_gold` association robust to model/prompt clustering, criterion noise, rater choice and reference quality (zero inference)?
2. **What ran** — 10-14-2026: protocol locked (commit c16120b); `scripts/analyze_e48.py` run end to end on Brando's MacBook Pro (53.5 s, seed 48, 10,000 draws; worktree `~/.worktrees/cert-judge/e48-e49-cached-analyses`, branch `claude/cj-e48-e49-cached-analyses`); `scripts/test_e48.py` 10 passed.
3. **Results** — G0 PASS. Headline triple: within-model permutation p-val=0.0701 (not shown within models); minimum reference-quality view 0.530 [0.084, 0.781] p-val=0.0207 (27 items, 9 tasks, ROBUST); two-level interval [0.073, 0.871] (lower bound above 0, below 0.45). Within-prompt-family p-val=0.9136; model-cluster interval [−0.842, 0.656]; leave-out `qwen36` 0.377 (WEAKENED), leave-out `LEX` 0.453 (WEAKENED); all 12 rater views ROBUST (0.500–0.684); all 5 reference views ROBUST (0.528–0.558). Full numbers: [results.md](results.md), [RESULTS_heldout_association_sensitivity.md](RESULTS_heldout_association_sensitivity.md).
4. **Stuck / blocked** — nothing.
5. **Next steps** — (1) archived to `experiments/archive/48_c_ms_gold_heldout_judge_association_cluster_bootstrap_and_criterion_sensitivity` in the verdict commit (10-14-2026 13:08 PDT); land the branch by PR and merge; (2) feed the scope statement (within-model p, within-family p, cluster intervals) to the paper's limitations and to experiment 49's design table.
6. **Brando to-do** — none.

## Log
- 10-14-2026 12:50 PDT -- folder created, protocol locked, no numbers yet.
- 10-14-2026 13:03 PDT -- analysis run (G0 PASS, A1–A6 written, 10 tests pass), ledger and report written; status DONE.
- 10-14-2026 13:08 PDT -- verdict recorded; folder archived to experiments/archive/48_c_ms_gold_heldout_judge_association_cluster_bootstrap_and_criterion_sensitivity (repo-root resolution fixed for the new depth, analysis re-run from the archived location, 10 tests pass).
- 10-14-2026 13:19 PDT -- LANDED bd43beb65d2999490ac920c23999e309860838ea https://github.com/brando90/cert-judge/pull/66 10-14-2026 13:19 PDT (rebase-merged; experiment landed on main in its archived home)
