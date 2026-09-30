# Experiment 39 results: label-free proxy index, train / val / test over judge models

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results.md>

**Status:** RUNNING (started 09-30-2026 12:09 PDT; worker tmux `cj-e39-proxy-index-search` on skampere1, branch `e39-proxy-index-search`; no judge call made yet)
**Last updated:** 09-30-2026 12:32 PDT

Experiment 39: 56 judge configurations (50 single-call: six judge models × the VeriBench and cert-judge prompt families; 6 agent judges: Terminus2 + GPT-6 Luna / Claude Sonnet 5 / Qwen3.6-27B on the H2 and D0 rubrics) plus 4 controls, judged on Lean-validated probes through Valkyrie; a label-free index is selected on the train judge models (GPT-6 Sol, Claude Sonnet 5), checked on val (GPT-6 Luna, Gemini 3.1 Pro, Terminus2 + Luna) and tested once on held-out judges (Claude Opus 5.5, Qwen3.6-27B, Terminus2 + Sonnet 5, Terminus2 + Qwen) against agreement with the expert coverage ratings on 45 held-out VeriBench items; results pending.

Contract: [PROTOCOL.md](PROTOCOL.md). Design: [README.md](README.md). Runbook: [cc.md](cc.md). Quote: [COST_QUOTE.md](COST_QUOTE.md). Readable report (written by `scripts/analyze.py report` once results exist): `results/RESULTS_proxy_index_train_val_test.md`.

## Phases

| Phase | Status | Evidence |
|---|---|---|
| Design, code, 19 offline tests, dry run (56 configurations rendered, 51,500 calls, $1,421 expected) | DONE 09-30-2026 | `scripts/`, `results/panel.json`, `results/planning_dryrun/` |
| Protocol locked | DONE 09-30-2026 | `PROTOCOL.md` |
| Dispatch on SNAP skampere1 (tmux `cj-e39-proxy-index-search`) | DONE 09-30-2026 (19 offline tests pass on the node; panel receipt rebuilt) | `CKPT_proxy_index_search.md`, `results/panel.json` |
| Probes elaborated with Lean 4.22 + Mathlib | IN PROGRESS: first build (12:11–12:24 PDT) superseded, see deviation 2; rebuild against the mirror project started 12:31 PDT | `results/probe_manifest.json` |
| Exact quote within cap | PENDING | `results/QUOTE.json` |
| Bundle, agent-harness and pack checks | bundle PASS (served `vb103_judge` byte-identical to experiment 103's validated bundle); harness PASS (`brando_terminus_gateway`: kwargs `max_turns` 20, `reasoning_effort` high; its contract maps the gateway secret itself); packs PENDING | `results/agent_bundle_check.json`, `results/agent_harness.json`, `results/packs.json` |
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
- 09-30-2026, before any call (skampere1 worker): the first Lean-validated probe build found that **72 of the 75 rated candidates do not elaborate under Lean 4.22 + Mathlib v4.22** (3 elaborate: `0_unsafeCopy_safe__agent1`, `13_MyUppercase__agent1`, `33_MyMinimum__agent2`) and that the gold `1_MyAdd` does not elaborate (unsolved goals), so 24/25 golds carry ladders. First-error classes over the 72 candidates: 9 stop at `import VeriBench`/`VeriBench.Prelude`/`VeriBench.Common` (a prelude the grading project does not provide), ~25 import modules that no longer exist in this toolchain (`Std.Data.List.Basic`, `Lean.Data.HashMap`, `Mathlib.Data.List.Perm`, `Mathlib.Tactic.LibrarySearch`, ...), 14 contain literal markdown fences (parse error), and the rest fail type-checking, termination or proofs. cert-judge's frozen PTI-v0 run on the same Claude 3.7 sample population (`experiments/archive/04_veribench_validation/results_pti_v0_v4/probe_validity_manifest.json`) elaborated only 86 of 470 candidates (18%), so a low rate is a known property of these samples, not of this run. **Environment preparation, as in the frozen PTI-v0 pipeline (`run_pti_v0.py` `_LOCAL_LEAN_MODULES`):** the empty prelude modules `VeriBench`, `VeriBench.Common` and `VeriBench.Prelude` were compiled with `cert_judge.probe_validation.LeanCompiler.compile_module` from cert-judge's own sources (`data/veribench_dataset/lean_src/veribench.lean` sha256 d0d1fda6…, `veribench/Common.lean` and `veribench/Prelude.lean` sha256 6a3ad70c…, byte-identical to the archived run's records) into a private mirror of the grading project (`private/lean_mirror`: the same `lakefile.toml`, `lake-manifest.json`, `lean-toolchain` and a symlink to the same built packages; the shared project `/lfs/skampere1/0/brando9/vb90_grading/lean_project` was not modified). The probes were then rebuilt against the mirror. `PROTOCOL.md` is unchanged: a candidate that does not elaborate keeps only its criterion cell, invalid probes are excluded before any call, and every count is in `results/probe_manifest.json`. **Consequence for Brando:** the candidate-side components (`ms_cand`, `alpha`, `reorder`, `sorry`, `spam`) rest on very few candidates, so every pre-registered candidate index that contains `reorder` (GM_cov5/6/7, AM_cov7, MIN_cov7, GM_inv3, GM_bm_ms_inv, C_reorder) is expected to be NOT_COMPUTABLE and the family effectively reduces to the gold-side indices, `PTI_v0_frozen`, `TI_var_trainnorm`, `GM_mono2` and the single components; the report states the exact denominators.
- Every later amendment, substitute selector and missing-cell class will be listed here with counts.

**TLDR-end:** [cert-judge: e39-proxy-index] The experiment is designed, coded, tested and quoted ($1,421 expected for 51,500 Valkyrie calls including six Terminus2 agent-judge configurations, cap $2,000) and the SNAP worker has started on skampere1 (nothing judged yet); the test-model rows stay sealed until the selection is committed.
