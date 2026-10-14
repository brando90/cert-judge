# Experiment 49 — live results ledger

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/49_human_rating_round_design_precision_and_power_from_cached_judge_scores_and_five_raters/results.md>

**Status:** DONE (started 10-14-2026 12:52 PDT, finished 10-14-2026 13:12 PDT; zero inference, $0, local MacBook Pro worktree)
**Last updated:** 10-14-2026 13:15 PDT (archived to `experiments/archive/49_human_rating_round_design_precision_and_power_from_cached_judge_scores_and_five_raters` in the verdict commit; analysis re-run from there, numbers unchanged)

Report: [RESULTS_rating_round_design.md](RESULTS_rating_round_design.md). Receipts: `results/*.json` (inputs hashed in `results/input_manifest.json`; seed 49, gate G0 seed 39). Tests: `scripts/test_e49.py`, 9 passed.

| Phase | Status | Result |
|---|---|---|
| Protocol locked | DONE | [PROTOCOL.md](PROTOCOL.md), sealed at commit `c16120b` |
| Inputs hashed | DONE | 65 files: experiment 39's 60 harvest files, 2 unit files, probe manifest, test receipt; VeriBench experiment 100 `items.jsonl` SHA-256 `ad9ed552…` |
| G0 reproduction and NumPy parity | DONE | PASS: every configuration's criterion reproduced (max abs. diff. 0 over 56); registered `C_ms_gold` test association 0.558 [0.078, 0.762] p-val=0.0127 (16 units, seed 39) reproduced to 1.1e-16; vectorized Spearman parity 0 |
| Reference criterion (25 tasks, all available raters, 345 ratings) | DONE | held-out association of `C_ms_gold` 0.596 [0.134, 0.780] p-val=0.0093 (one-sided permutation; 95% configuration bootstrap, 10,000 draws; 16 units); Kendall 0.377, Pearson 0.696. Registered design versus reference: ranking reliability 0.961, gate agreement 0.929 |
| Q1 precision grid (24 cells × 1,000 draws) | DONE | ranking reliability (mean) rises from 0.595 (5 tasks × 1 rater) to 0.985 (20 × 5); the registered 15 × 3 cell gives 0.951 [5th pct 0.913] with gate agreement 0.926; held-out association mean 0.55–0.62 and flat in T and R once reliable |
| Q2 power curves (1,000 draws × 1,000 permutations) | DONE | power ≥ 0.80 at K = 12 for the mixed-family pool (0.915; pool Spearman 0.763), at K = 24 for the test-16 pool (0.865; K = 16: 0.789), never for the fuller-context pool (best 0.286 at K = 16; pool Spearman 0.302), 0 for legacy (−0.357); model-clustered M = 2 → 0.809 (187/1,000 draws below 8 units counted as failures), M = 4 → 0.962 |
| Q3 allocation | DONE | more tasks with fewer raters wins 7 of 8 equal-budget comparisons |
| Q4 extrapolation (model-based) | DONE | single-rater ICC(C,1) 0.517, three-rater 0.763 (ρ_max 0.873), five-rater 0.843 (ρ_max 0.918); task design effect median 2.64 (criterion SD 0.130 at 75 items), extrapolated Fisher-z SD 0.134 at 150 items |
| Report | DONE | [RESULTS_rating_round_design.md](RESULTS_rating_round_design.md) |

## Pre-declared readings (agent-suggested targets 0.90 / 0.90 / 0.80, PROTOCOL.md)

- Smallest adequate (T, R): 20 tasks × 2 raters (120 nominal ratings; reliability 0.950, gate agreement 0.915). The registered 15 × 3 design (135) also meets both targets.
- Smallest adequate K, mixed-family pool: 12 (power 0.915). Fuller-context pool: unmet at every K ≤ 48 (best 0.286). Model-clustered: M = 2 (0.809).
- Headline triple: (20 × 2; K = 12; fuller-context power at K = 16 = 0.29).
- Reading: the pooled power is carried by the between-prompt-family contrast (legacy prompts score low on both axes); within the deployable fuller-context family the association (0.30) sits below the 0.45 gate, so neither more held-out judges nor more ratings rescue the pre-registered test there. The decisive lever for the next pool is the within-family effect size (a better screen or a family-specific gate), not the number of ratings.

## Deviations

- Q4(b) design effect: PROTOCOL.md names "Q1's empirical criterion SD at T = 25, R = 5", but that cell is the full data and has no variation. The design effect uses a 1,000-draw task bootstrap at 25 tasks with all available raters instead (recorded in `results/q4_extrapolation.json`); everything else follows the protocol's grid, draw counts and seeds.
- The analysis ran locally (seconds to minutes of CPU on cached receipts) rather than on SNAP; every artifact is committed with the branch.

**TLDR-end:** [cert-judge: experiment 49 rating-round design from cached scores] DONE: 20 tasks × 2 raters already rank judge configurations reliably (0.95) and the registered held-out test is powered (0.92 at 12 judges) only across prompt families; within fuller-context judges the association (0.30) is below the 0.45 gate and no number of judges or ratings fixes that.
