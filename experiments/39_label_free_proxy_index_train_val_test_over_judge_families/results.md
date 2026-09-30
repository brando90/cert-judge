# Experiment 39 results: label-free proxy index, train / val / test over judge models

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results.md>

**Status:** RUNNING (started 09-30-2026 12:09 PDT; worker tmux `cj-e39-proxy-index-search` on skampere1, branch `e39-proxy-index-search`; no judge call made yet)
**Last updated:** 09-30-2026 12:09 PDT

Experiment 39: 56 judge configurations (50 single-call: six judge models × the VeriBench and cert-judge prompt families; 6 agent judges: Terminus2 + GPT-6 Luna / Claude Sonnet 5 / Qwen3.6-27B on the H2 and D0 rubrics) plus 4 controls, judged on Lean-validated probes through Valkyrie; a label-free index is selected on the train judge models (GPT-6 Sol, Claude Sonnet 5), checked on val (GPT-6 Luna, Gemini 3.1 Pro, Terminus2 + Luna) and tested once on held-out judges (Claude Opus 5.5, Qwen3.6-27B, Terminus2 + Sonnet 5, Terminus2 + Qwen) against agreement with the expert coverage ratings on 45 held-out VeriBench items; results pending.

Contract: [PROTOCOL.md](PROTOCOL.md). Design: [README.md](README.md). Runbook: [cc.md](cc.md). Quote: [COST_QUOTE.md](COST_QUOTE.md). Readable report (written by `scripts/analyze.py report` once results exist): `results/RESULTS_proxy_index_train_val_test.md`.

## Phases

| Phase | Status | Evidence |
|---|---|---|
| Design, code, 19 offline tests, dry run (56 configurations rendered, 51,500 calls, $1,421 expected) | DONE 09-30-2026 | `scripts/`, `results/panel.json`, `results/planning_dryrun/` |
| Protocol locked | DONE 09-30-2026 | `PROTOCOL.md` |
| Dispatch on SNAP skampere1 (tmux `cj-e39-proxy-index-search`) | IN PROGRESS (worker started, clone + branch + checkpoint landed) | `CKPT_proxy_index_search.md` |
| Probes elaborated with Lean 4.22 + Mathlib | PENDING | `results/probe_manifest.json` |
| Exact quote within cap | PENDING | `results/QUOTE.json` |
| Bundle, agent-harness and pack checks | PENDING | `results/agent_bundle_check.json`, `results/agent_harness.json`, `results/packs.json` |
| Smoke per configuration; main admission train → val → test; recovery pass; merge | PENDING | `results/judge_progress.json`, `results/harvest/` |
| Criterion, components, indices (train + val rows open; test rows sealed) | PENDING | `results/units_train_val.json` |
| Selection committed | PENDING | `results/FINALISTS.json`, `results/SELECTION.json` |
| One-shot test | PENDING | `results/TEST_RECEIPT.json` |
| Report and landing | PENDING | `results/RESULTS_proxy_index_train_val_test.md`, PR |

## Numbers so far

| Quantity | Value | Source |
|---|---|---|
| Units | 60 (train 18 LLM + 4 controls; val 20 incl. 2 agent judges; test 18 incl. 4 agent judges) | `results/panel.json` |
| Calls per configuration (upper bound, before Lean exclusions) | 946 (D0: 782 + 132 deterministic + 32 unmeasured) | `results/planning_dryrun/cells_summary.json` |
| Total calls (upper bound) | 51,500 (46,316 single-call + 5,184 agent-judge cells) | `results/planning_dryrun/QUOTE.json` |
| Expected charges | $1,421 (train $234, val $229, test $958); cap $2,000 | same |
| Human ceiling on the criterion items | 0.747 (mean leave-one-expert-out Spearman, 45 items) | VeriBench experiment 100 |
| Criterion correlations, component values, index correlations | not measured | — |

## Deviations and open questions for Brando

- 09-30-2026, before any call (PR #48 review by the sibling session): the probe theorem finder missed same-line `@[attr] theorem` heads (60 of 181 gold theorems found); widened to 181/181, `ms_gold` levels 57 → 83, quote 50,224 → 51,500 calls. Core `declarations()` (PTI-v0 numerics, bug-ladder targets) unchanged.
- Every later amendment, substitute selector and missing-cell class will be listed here with counts.

**TLDR-end:** [cert-judge: e39-proxy-index] The experiment is designed, coded, tested and quoted ($1,421 expected for 51,500 Valkyrie calls including six Terminus2 agent-judge configurations, cap $2,000) and the SNAP worker has started on skampere1 (nothing judged yet); the test-model rows stay sealed until the selection is committed.
