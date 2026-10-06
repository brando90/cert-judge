# Cached score judge selection utility

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/44_cached_score_judge_selection_utility/README.md>

**TLDR:** Compare the frozen deletion-monotonicity proxy with practical judge selectors using existing scores. The goal is a measured decision about prospective validation, not another pooled correlation headline.

Completed: 10-05-2026. [Protocol](PROTOCOL.md), [results](RESULTS_selection_utility.md), [live ledger](results.md), [checkpoint](CKPT_selection_utility.md), [worker instructions](cc.md).

## Structure

```text
PROTOCOL.md                 exploratory analysis contract
cc.md                       execution instructions
CKPT_selection_utility.md  resumable state
results.md                  live ledger
scripts/                    deterministic analysis and tests
results/                    source manifest, tables and receipt
RESULTS_selection_utility.md final verified report
```

## Method

1. Verify frozen inputs and reconstruct original criterion values.
2. Fix selectors using the protocol's rules and existing train/validation judges.
3. Compare selection utility on declared test pools and reference-quality views.
4. Report paired task uncertainty, model sensitivities, missingness and decision.

## Dependencies

Existing experiment39 harvests and frozen units; fingerprint-matched VeriBench item labels; Python, NumPy and SciPy. No provider credentials or inference calls.

| Phase | Status |
|---|---|
| Protocol and source inventory | Done |
| Deterministic implementation | Done — cached scores only; no inference |
| Verified analysis and report | Done — 9 tests, all-source reconstruction, 10,000 task-cluster draws |
| Archive | Done — retired to this canonical archive home; publication receipt pending landing |
