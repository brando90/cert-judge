# Experiment 48: cluster-aware intervals and criterion sensitivity of the held-out judge association of `C_ms_gold`

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/48_c_ms_gold_heldout_judge_association_cluster_bootstrap_and_criterion_sensitivity/README.md>

**TLDR:** Experiment 39 found that the gold deletion-monotonicity screen `C_ms_gold`, chosen on the train and validation judge models, predicts judge–human agreement on the held-out judge models (test Spearman 0.558 [0.078, 0.762], one-sided permutation p-val=0.0127, 16 of 18 units). That interval treats the 16 configurations as independent although they come from four judge models and nine prompts, and its criterion is an estimate from 45 items and three raters. This zero-inference study recomputes the association under pre-registered cluster bootstraps, within-model and within-prompt-family permutation tests, task-level criterion resampling, single-rater and leave-one-rater-out targets, and the reference-quality views of experiment 44, all from experiment 39's committed receipts and VeriBench experiment 100's pinned ratings. Decision rule: each view is ROBUST (Spearman ≥ 0.45, p-val < 0.05), WEAKENED or REVERSED under the thresholds experiment 39 pre-registered; the registered PASS is scoped, not re-litigated ([PROTOCOL.md](PROTOCOL.md)).

## Goal, hypothesis and decision criterion

**Central uncertainty (Trigger Rule 50).** Is the pooled held-out association carried by between-model or between-prompt-family differences, by particular raters, or by the placeholder- and ambiguous-reference criterion tasks? If so, the paper's transfer claim must be narrowed before the next human rating round is designed around it.

**Hypothesis.** The association is present within judge models (within-model permutation p-val < 0.05) and stays at or above the 0.45 gate when placeholder- and ambiguous-reference tasks are removed from the criterion; the two-level (task then configuration) interval keeps a positive lower bound.

**Decision.** Pre-declared per-view readings in [PROTOCOL.md](PROTOCOL.md) § Pre-declared readings. The headline triple is (within-model p-val; minimum Spearman over the reference-quality views; two-level interval lower bound). Whatever the outcome, experiment 39's registered verdict stands; this experiment supplies the scope statement and the limitation numbers for the paper and for the design of the human rating round.

## Structure

```
48_c_ms_gold_heldout_judge_association_cluster_bootstrap_and_criterion_sensitivity/
├── README.md                                   # this design document
├── PROTOCOL.md                                 # locked contract (before any number)
├── results.md                                  # live ledger (Trigger Rule 37)
├── CKPT_heldout_association_sensitivity.md     # resumable checkpoint (Trigger Rule 44)
├── RESULTS_heldout_association_sensitivity.md  # reader-facing report (written by the analysis)
├── scripts/analyze_e48.py                      # the analysis (zero inference)
├── scripts/test_e48.py                         # offline tests
└── results/                                    # input_manifest.json, g0_reproduction.json, a1_cluster.json, a2_stratified_permutation.json,
                                                #   a3_criterion_noise.json, a4_rater_views.json, a5_reference_quality.json, a6_attenuation.json, summary.json
```

## Method

1. Hash and load the frozen inputs (experiment 39's `units_test.json`, `units_train_val.json`, `harvest/*.json`, `probe_manifest.json`, `TEST_RECEIPT.json`; VeriBench experiment 100's `items.jsonl`, SHA-256 `ad9ed552…`).
2. Gate G0: reproduce the registered test association, every test unit's criterion and `C_ms_gold`, and the 0.928 criterion reproducibility, through experiment 39's own `analysis_lib`.
3. Run analyses A1–A6 exactly as pre-registered (seed 48, 10,000 draws), write one JSON per analysis and the report.
4. Read each view against the pre-declared rule and record the headline triple in `results.md`.

## Dependencies

- Experiment 39's committed receipts (read-only; path resolved under `experiments/` or `experiments/archive/`).
- VeriBench checkout with experiment 100's `inputs/items.jsonl` (`CJ_VERIBENCH_REPO`, default `/Users/brandomiranda/veribench`).
- `py_src/cert_judge/pti_v0.py` (tie-aware statistics) through experiment 39's `scripts/analysis_lib.py`.
- No model calls, no credentials, $0.

## Status

| Step | Status | Notes |
|---|---|---|
| Protocol locked | Done (10-14-2026 12:50 PDT) | [PROTOCOL.md](PROTOCOL.md) |
| Analysis code and tests | Pending | |
| G0 reproduction | Pending | |
| A1–A6 | Pending | |
| Report and ledger | Pending | |
