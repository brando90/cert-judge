# Experiment 39 results: label-free proxy index, train / val / test over judge models

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results.md>

**Status:** DISPATCH-READY (designed 09-30-2026; no judge call made yet)
**Last updated:** 09-30-2026 16:35 UTC

Experiment 39: 50 judge configurations (six judge models × the VeriBench and cert-judge prompt families) plus 4 controls, judged on Lean-validated probes through Valkyrie; a label-free index is selected on the train judge models (GPT-6 Sol, Claude Sonnet 5), checked on val (GPT-6 Luna, Gemini 3.1 Pro) and tested once on held-out judge models (Claude Opus 5.5, Qwen3.6-27B) against agreement with the expert coverage ratings on 45 held-out VeriBench items; results pending.

Contract: [PROTOCOL.md](PROTOCOL.md). Design: [README.md](README.md). Runbook: [cc.md](cc.md). Quote: [COST_QUOTE.md](COST_QUOTE.md). Readable report (written by `scripts/analyze.py report` once results exist): `results/RESULTS_proxy_index_train_val_test.md`.

## Phases

| Phase | Status | Evidence |
|---|---|---|
| Design, code, 16 offline tests, dry run (50 configurations rendered, 45,136 calls, $1,084 expected) | DONE 09-30-2026 | `scripts/`, `results/panel.json`, `results/planning_dryrun/` |
| Protocol locked | DONE 09-30-2026 | `PROTOCOL.md` |
| Dispatch on SNAP skampere1 (tmux `cj-e39-proxy-index-search`) | PENDING | — |
| Probes elaborated with Lean 4.22 + Mathlib | PENDING | `results/probe_manifest.json` |
| Exact quote within cap | PENDING | `results/QUOTE.json` |
| Bundle and pack checks | PENDING | `results/agent_bundle_check.json`, `results/packs.json` |
| Smoke per configuration; main admission train → val → test; recovery pass; merge | PENDING | `results/judge_progress.json`, `results/harvest/` |
| Criterion, components, indices (train + val rows open; test rows sealed) | PENDING | `results/units_train_val.json` |
| Selection committed | PENDING | `results/FINALISTS.json`, `results/SELECTION.json` |
| One-shot test | PENDING | `results/TEST_RECEIPT.json` |
| Report and landing | PENDING | `results/RESULTS_proxy_index_train_val_test.md`, PR |

## Numbers so far

| Quantity | Value | Source |
|---|---|---|
| Units | 54 (train 18 LLM + 4 controls; val 18; test 14) | `results/panel.json` |
| Calls per configuration (upper bound, before Lean exclusions) | 920 (D0: 776 + 112 deterministic + 32 unmeasured) | `results/planning_dryrun/cells_summary.json` |
| Total calls (upper bound) | 45,136 | `results/planning_dryrun/QUOTE.json` |
| Expected charges | $1,084 (train $228, val $215, test $641); cap $1,600 | same |
| Human ceiling on the criterion items | 0.747 (mean leave-one-expert-out Spearman, 45 items) | VeriBench experiment 100 |
| Criterion correlations, component values, index correlations | not measured | — |

## Deviations and open questions for Brando

- None yet. Every amendment, substitute selector and missing-cell class will be listed here with counts.

**TLDR-end:** [cert-judge: e39-proxy-index] The experiment is designed, coded, tested and quoted ($1,084 expected for 45,136 Valkyrie calls, cap $1,600) but nothing has been judged; the worker runbook `cc.md` runs it end to end on SNAP and the test-model rows stay sealed until the selection is committed.
