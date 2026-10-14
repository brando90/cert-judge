# Experiment 48 — live results ledger

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/48_c_ms_gold_heldout_judge_association_cluster_bootstrap_and_criterion_sensitivity/results.md>

**Status:** DONE (started 10-14-2026 12:50 PDT, finished 10-14-2026 13:03 PDT; zero inference, 53.5 s of CPU on Brando's MacBook Pro)
**Last updated:** 10-14-2026 13:08 PDT (archived to `experiments/archive/48_c_ms_gold_heldout_judge_association_cluster_bootstrap_and_criterion_sensitivity` in the verdict commit; analysis re-run from there, numbers unchanged)

Full report: [RESULTS_heldout_association_sensitivity.md](RESULTS_heldout_association_sensitivity.md); receipts in `results/` (inputs hashed in `results/input_manifest.json`). Unless stated, numbers are tie-aware Spearman correlations between `C_ms_gold` and the judge–human criterion over the 16 computable held-out judge configurations, with 95% percentile bootstrap intervals (10,000 draws, resampled unit named) and one-sided configuration-permutation p-values; thresholds 0.45 and p-val < 0.05 are experiment 39's pre-registered gate.

| Phase | Status | Result |
|---|---|---|
| Protocol locked | DONE | [PROTOCOL.md](PROTOCOL.md), sealed at commit c16120b before any number |
| Inputs hashed | DONE | 56 harvest files, 4 receipt files, VeriBench items.jsonl (SHA-256 ad9ed552…) |
| G0 reproduction | DONE — PASS | registered test association 0.558 [0.078, 0.762] p-val=0.0127 reproduced to 1e-9 (seed 39); every test unit's criterion (max diff 0) and `C_ms_gold` (max diff 3.3e-16) reproduced; criterion ranking reproducibility 0.928 (47 configurations with both halves) |
| A1 cluster bootstraps | DONE | judge-model cluster interval [−0.842, 0.656] (4 clusters, 35 distinct multisets, p-val=n/a); prompt cluster interval [−0.123, 0.850] (8 clusters); leave-one-model-out min 0.377 (drop `qwen36`, p-val=0.1575, WEAKENED), median 0.564, max 0.591; leave-one-prompt-out min 0.453 (drop `LEX`, p-val=0.0534, WEAKENED), median 0.520, max 0.741 (drop `D0`); every other deletion ROBUST |
| A2 stratified permutations | DONE | within judge model p-val=0.0701 (not shown to hold within models at 0.05); within prompt-rendering family p-val=0.9136 (the pooled association is carried by the legacy-vs-fuller-context difference); descriptive within-model Spearman: Claude Opus 5.5 0.600 (5 units), Qwen3.6-27B 0.643 (7 units) |
| A3 criterion-noise intervals | DONE | task-only [0.412, 0.783]; two-level (task, then configuration) [0.073, 0.871], lower bound above 0 but below 0.45; p-val=n/a; per-unit criterion SD over task draws 0.07–0.24 |
| A4 rater views | DONE | all 12 targets ROBUST: min 0.500 [−0.076, 0.890] p-val=0.0250 (rater 4 alone), max 0.684 [0.265, 0.903] p-val=0.0021 (leave rater 2 out); five-rater mean 0.555 [0.103, 0.788] p-val=0.0154 |
| A5 reference-quality views | DONE | all ROBUST: no placeholder tasks 0.545 [0.039, 0.769] p-val=0.0175 (36 items); no ambiguous tasks 0.543 [0.087, 0.777] p-val=0.0177 (36); neither 0.530 [0.084, 0.781] p-val=0.0207 (27 items, 9 tasks); test tasks only 0.528 [0.075, 0.758] p-val=0.0199 (30) |
| A6 attenuation bound | DONE | criterion split-half 0.928 (Spearman–Brown 0.963, 47 configurations); `C_ms_gold` split-half 0.888 (Spearman–Brown 0.941, 54 configurations); disattenuated test Spearman 0.586 (bound, not an estimate) |
| Report | DONE | [RESULTS_heldout_association_sensitivity.md](RESULTS_heldout_association_sensitivity.md); 10 offline tests pass (`scripts/test_e48.py`) |

## Headline triple (pre-declared)

1. Within-judge-model permutation p-val=0.0701 → the pooled association is **not shown to hold within judge models** at the 0.05 level (the within-model point estimates are positive: 0.600 and 0.643 on the two models with ≥ 5 units).
2. Minimum Spearman over the four reference-quality views: 0.530 [0.084, 0.781] p-val=0.0207 (27 items, 9 tasks) → **ROBUST** to placeholder and ambiguous references.
3. Two-level interval (task, then configuration): [0.073, 0.871] → lower bound **above 0, below 0.45**.

Reading for the paper: the held-out association survives every rater and reference-quality view and every single-prompt deletion except the lexical control, but it is not resolved within judge models, it disappears when the criterion is permuted within prompt-rendering families (p-val=0.9136), and the cluster intervals over four judge models reach −0.84. Experiment 39's registered PASS stands; its scope is a pooled claim over prompt families and judge models, not a within-model ranking claim.

## Deviations

- Prompt clusters: the 16 computable units span 8 prompt keys, not the 9 of the 18 declared test units (`R4` appears only in `qwen36|R4`, which has no `C_ms_gold`); A1(c) and A1(d) use the 8.
- Criterion ranking reproducibility (G0 item 4 and A6) is over the 47 LLM configurations whose validation-item and test-item criteria are both COMPUTED (experiment 39 stored the same 47-unit value, 0.928); the nine D0/LEX-type units with validation-item coverage below 90% are excluded by the frozen rule.
- A3: the four D0 units are NOT_COMPUTABLE in 1,608 of 10,000 task draws (their three unscored items' tasks over-drawn below the 90% coverage rule) and `qwen36|LEX` in 18; those draws proceed with the remaining units (never fewer than 8), as the protocol prescribes.
- A4: the rater-3-alone view declares 27 items and leaves 12 of 16 units computable (the four D0 units fall below 90% coverage on those items); reported with that denominator.
- A6: the `C_ms_gold` split-half uses the 54 LLM configurations with both halves defined.

**TLDR-end:** [cert-judge: experiment 48 held-out association sensitivity] Experiment 39's held-out `C_ms_gold` association (0.558) is robust to raters and reference quality (every view ≥ 0.50, p-val ≤ 0.025) but not resolved within judge models (within-model p-val=0.0701, within-prompt-family p-val=0.9136, model-cluster interval [−0.842, 0.656]); the two-level interval is [0.073, 0.871].
