# Experiment 49: how many tasks, raters and held-out judges the cert-judge human rating pool needs, measured by resampling cached judge scores and five raters

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/49_human_rating_round_design_precision_and_power_from_cached_judge_scores_and_five_raters/README.md>

**TLDR:** The plan of record is more human data: VeriBench's set-N round (25 task folders, two ratings per file, closes 11-06-2026) is evaluation-only, and judge screening is to come from a separate cert-judge pool on other tasks. This zero-inference study tells that pool's designers what they buy with each rated task, each extra rater and each held-out judge configuration, by resampling experiment 39's cached scores (56 judge configurations × 75 items × 3 repeats) and VeriBench experiment 100's five current raters: criterion precision and ranking reliability over a tasks × raters grid, power of the pre-registered held-out test (Spearman ≥ 0.45, p-val < 0.05) versus the number of held-out judge configurations (independent and model-clustered), the equal-budget allocation, and a labelled model-based extrapolation beyond 75 items. Decision rule: the smallest design meeting agent-suggested targets (ranking reliability 0.90, gate agreement 0.90, power 0.80), or "unmet" with the best value achieved ([PROTOCOL.md](PROTOCOL.md)).

## Goal, hypothesis and decision criterion

**Central uncertainty (Trigger Rule 50).** Whether a pool the team can rate can produce a criterion precise enough to separate judge configurations and to test a label-free screen on held-out judges, or whether the binding constraint is the number of held-out judge configurations rather than ratings.

**Hypothesis.** At 15 tasks and three raters (the registered design) the criterion already ranks configurations with reliability above 0.90 against the 25-task five-rater reference, so additional ratings buy little; the held-out test's power at 16 configurations is below 0.80 at the pooled effect size and far below it on fuller-context prompts, so the decisive lever is more held-out judge models, not more items.

**Decision.** [PROTOCOL.md](PROTOCOL.md) § Pre-declared readings: a measured (T, R, K, M) recommendation feeding the rating-pool lane (`experiments/ideas/cj_human_rating_pool_prospective_screen/`) and the paper's limitations; no change to experiment 39's verdict or to set N.

## Structure

```
49_human_rating_round_design_precision_and_power_from_cached_judge_scores_and_five_raters/
├── README.md                         # this design document
├── PROTOCOL.md                       # locked contract (before any number)
├── results.md                        # live ledger (Trigger Rule 37)
├── CKPT_rating_round_design.md       # resumable checkpoint (Trigger Rule 44)
├── RESULTS_rating_round_design.md    # reader-facing report (written by the analysis)
├── scripts/analyze_e49.py            # the analysis (zero inference)
├── scripts/test_e49.py               # offline tests
└── results/                          # input_manifest.json, g0_reproduction.json, q1_precision_grid.json, q2_power.json,
                                      #   q3_allocation.json, q4_extrapolation.json, summary.json
```

## Method

1. Hash and load experiment 39's harvest, unit files and manifest and VeriBench experiment 100's pinned `items.jsonl`.
2. Gate G0: reproduce every configuration's registered criterion and the registered `C_ms_gold` test association through experiment 39's `analysis_lib`; parity-test the NumPy Spearman against it.
3. Q1 subsampling grid (1,000 draws per cell, seed 49); Q2 power curves (empirical, parametric, model-clustered); Q3 equal-budget comparison from the grid; Q4 labelled extrapolation.
4. Read the grid against the pre-declared targets and record the headline triple in `results.md`.

## Dependencies

- Experiment 39's committed receipts (read-only; path resolved under `experiments/` or `experiments/archive/`).
- VeriBench checkout with experiment 100's `inputs/items.jsonl` (`CJ_VERIBENCH_REPO`, default `/Users/brandomiranda/veribench`).
- `py_src/cert_judge/pti_v0.py` through experiment 39's `scripts/analysis_lib.py`; NumPy for the permutation loops after a parity test.
- No model calls, no credentials, $0.

## Status

| Step | Status | Notes |
|---|---|---|
| Protocol locked | Done (10-14-2026 12:52 PDT) | [PROTOCOL.md](PROTOCOL.md) |
| Analysis code and tests | Pending | |
| G0 reproduction | Pending | |
| Q1–Q4 | Pending | |
| Report and ledger | Pending | |
