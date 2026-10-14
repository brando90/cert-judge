# CKPT — experiment 49 rating-round design

Created: 10-14-2026 12:52 PDT
Last updated: 10-14-2026 13:15 PDT

1. **Goal** — how many rated tasks, raters per item and held-out judge configurations the cert-judge screening pool needs, measured by resampling cached judge scores and five raters (zero inference).
2. **What ran** — 10-14-2026 13:12 PDT: `scripts/analyze_e49.py` full run (82 s, seed 49; G0 PASS), `scripts/test_e49.py` 9 passed; report `RESULTS_rating_round_design.md`, receipts `results/*.json`, ledger `results.md` DONE. Branch `claude/cj-e48-e49-cached-analyses`, worktree `~/.worktrees/cert-judge/e48-e49-cached-analyses`.
3. **Results** — smallest adequate design 20 tasks × 2 raters (ranking reliability 0.950, gate agreement 0.915 vs the 25-task five-rater reference; 1,000 draws); registered 15 × 3 cell 0.951 / 0.926. Held-out test power (Spearman ≥ 0.45, perm p < 0.05; 1,000 draws × 1,000 perms): mixed-family pool 0.915 at K = 12, test-16 pool 0.789 at K = 16, fuller-context pool never above 0.286 (pool Spearman 0.302), legacy 0; model-clustered M = 2 → 0.809. Reference held-out association 0.596 [0.134, 0.780] p-val=0.0093 (16 units). Single-rater ICC(C,1) 0.517; task design effect 2.64.
4. **Stuck / blocked** — nothing.
5. **Next steps** — (1) archived to `experiments/archive/49_human_rating_round_design_precision_and_power_from_cached_judge_scores_and_five_raters` in the verdict commit (10-14-2026 13:15 PDT); land the branch by PR and merge; (2) feed the readings to `experiments/ideas/cj_human_rating_pool_prospective_screen/` (next pool: fix the within-family effect size or gate before adding judges or ratings).
6. **Brando to-do** — none.

## Log
- 10-14-2026 12:52 PDT -- folder created, protocol locked, no numbers yet.
- 10-14-2026 13:12 PDT -- full analysis run, tests 9 passed, report and ledger DONE; one deviation (Q4(b) design effect via task bootstrap).
- 10-14-2026 13:15 PDT -- verdict recorded; folder archived to experiments/archive/49_human_rating_round_design_precision_and_power_from_cached_judge_scores_and_five_raters (repo-root resolution fixed for the new depth, selection-split caveat added to the power reading, analysis re-run from the archived location, 9 tests pass).
