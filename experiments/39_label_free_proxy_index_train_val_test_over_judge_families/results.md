# Experiment 39 results: label-free proxy index, train / val / test over judge models

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results.md>

**Status:** DONE (09-30-2026 17:27 PDT; every declared cell judged, sealed test unlocked at `86ae479201e5`, verdict PASS)
**Last updated:** 09-30-2026 17:27 PDT

Experiment 39: 56 judge configurations (six single-call models × the VeriBench and cert-judge prompt families, plus six Terminus2 agent judges) judged 28,591 Lean-validated probe cells through Valkyrie ($574); the label-free index selected on the train judges, `C_ms_gold` (gold missing-statement monotonicity; train ρ 0.76, val ρ 0.76), predicts judge–human agreement on the held-out test judges with Spearman 0.56 [0.08, 0.76], permutation p 0.013: pre-registered PASS; the paper's frozen `PTI_v0` (-0.27) and `TI_var` (-0.33) do not transfer.

Contract: [PROTOCOL.md](PROTOCOL.md). Design: [README.md](README.md). Runbook: [cc.md](cc.md). Quote: [COST_QUOTE.md](COST_QUOTE.md). Readable report (written by `scripts/analyze.py report` once results exist): `results/RESULTS_proxy_index_train_val_test.md`.

## Phases

| Phase | Status | Evidence |
|---|---|---|
| Design, code, 19 offline tests, dry run (56 configurations rendered, 51,500 calls, $1,421 expected) | DONE 09-30-2026 | `scripts/`, `results/panel.json`, `results/planning_dryrun/` |
| Protocol locked | DONE 09-30-2026 | `PROTOCOL.md` |
| Dispatch on SNAP skampere1 (tmux `cj-e39-proxy-index-search`) | DONE 09-30-2026 (19 offline tests pass on the node; panel receipt rebuilt) | `CKPT_proxy_index_search.md`, `results/panel.json` |
| Probes elaborated with Lean 4.22 + Mathlib | DONE 09-30-2026 12:41 PDT (mirror project with the VeriBench prelude; see deviations): valid/invalid per kind — ident 24/1, blank 25/0, ms_gold 76/4, bm_gold 37/60, crit 75/0, ms_cand 3/72, alpha 3/72, reorder 0/75, sorry 3/72, spam 3/72 | `results/probe_manifest.json` |
| Exact quote (no automatic cap, Amendment 1) | DONE 09-30-2026: 28,591 calls over 56 configurations, expected $790.59 (train $129.49, val $127.01, test $534.13), worst-case admission bound $11,945 (no automatic spend cap: PROTOCOL.md Amendment 1; regenerated under the amended `quote.py`) | `results/QUOTE.json`, `results/cells_summary.json` |
| Bundle, agent-harness and pack checks | bundle PASS (served `vb103_judge` byte-identical to experiment 103's validated bundle); harness PASS (`brando_terminus_gateway`: kwargs `max_turns` 20, `reasoning_effort` high; its contract maps the gateway secret itself); packs PASS (nine packs, 0 round-trip failures: 4,633 tasks per nine-prompt model, 2,545 for Claude Opus 5.5, 979 per agent judge, each including one smoke cell per configuration) | `results/agent_bundle_check.json`, `results/agent_harness.json`, `results/packs.json` |
| Smoke per configuration; main admission train → val → test; recovery pass; merge | DONE 10-01-2026 00:06 UTC (all 56 configurations merged; one recovery pass over 31 runs / 97 cells); history: 56 smoke runs admitted, 32 measured on the first attempt (GPT-6 Sol 9/9, Claude Sonnet 5 9/9, GPT-6 Luna 9/9, Claude Opus 5.5 5/5; $0.76 in smoke charges), 24 retired at $0 and re-admitted after two fixes (see deviations); all 56 main runs admitted by 21:23Z (concurrency 20 each; every smoke measured, including the six Terminus2 agent judges); train configurations are being harvested, recovered and merged, see the live table below | `results/judge_progress.json`, `results/harvest/` |
| Criterion, components, indices (train + val rows open; test rows sealed) | DONE 10-01-2026 00:13 UTC (38 open LLM/control units; test rows sealed under `private/`) | `results/units_train_val.json` |
| Selection committed | DONE 10-01-2026: selected `C_ms_gold` (train ρ 0.761, val ρ 0.762); finalists `C_ms_gold`, `C_ident`, `GM_mono2`; seal commit `86ae479201e5` | `results/FINALISTS.json`, `results/SELECTION.json` |
| One-shot test | DONE 10-01-2026 00:22 UTC: `C_ms_gold` test ρ 0.558 [0.08, 0.76], p 0.0127, PASS | `results/TEST_RECEIPT.json`, `results/units_test.json` |
| Report and landing | report DONE 10-01-2026; landing PR from `e39-proxy-index-search` (number and merge commit recorded in `CKPT_proxy_index_search.md`) | `results/RESULTS_proxy_index_train_val_test.md`, PR |

## Numbers so far

| Quantity | Value | Source |
|---|---|---|
| Units | 60 (train 18 LLM + 4 controls; val 20 incl. 2 agent judges; test 18 incl. 4 agent judges) | `results/panel.json` |
| Calls per configuration (after Lean exclusions) | 521 (D0 configurations: 456 + 56 deterministic + 9 unmeasured extraction) | `results/cells_summary.json` |
| Total calls (exact, after Lean exclusions) | 28,591 (single-call 25,660 + agent-judge 2,931; dry-run upper bound was 51,500) | `results/QUOTE.json` |
| Expected charges | $790.59 (train $129.49, val $127.01, test $534.13); no automatic cap (PROTOCOL.md Amendment 1); dry-run estimate was $1,421 | same |
| Valid probes (Lean 4.22 + Mathlib) | golds with ladders 24/25; candidates elaborating 3/75 (ms_cand 3, alpha 3, reorder 0, sorry 3, spam 3 valid probes) | `results/probe_manifest.json` |
| Human ceiling on the criterion items | 0.747 (mean leave-one-expert-out Spearman, 45 items) | VeriBench experiment 100 |
| Criterion correlations, component values, index correlations | measured for all 60 units; see the verdict section and `results/RESULTS_proxy_index_train_val_test.md` | `results/units_train_val.json`, `results/units_test.json` |
| Charges (Vals-reported) | $573.01 on main + recovery runs, $1.21 on 56 smoke cells, total $574.22 (quote $790.59) | `results/harvest/*.json` `charges_usd` |
| Cells by status (56 configurations, incl. deterministic) | measured 28,345, deterministic 504, unmeasured_extraction 81, parse_error 235, model_error 7, unmeasured_infra 4 | `results/harvest/*.json` |

## Verdict (pre-registered in PROTOCOL.md; sealed test unlocked at commit `86ae479201e5`)

**PASS.** The index selected on the train judge models and checked on val, `C_ms_gold` (the missing-statement monotonicity component on the 24 gold ladders), predicts judge–human agreement on the 18 held-out test judge configurations (Claude Opus 5.5 ×5, Qwen3.6-27B ×9, Terminus2 + Claude Sonnet 5 ×2, Terminus2 + Qwen3.6-27B ×2): test Spearman 0.558 (gate ≥ 0.45), one-sided permutation p 0.0127 (gate < 0.05), train−test gap 0.203 within the 0.30 match tolerance, so the train (0.761), val (0.762) and test correlations match. The criterion was computable for 18/18 test units (no INCONCLUSIVE condition: the bootstrap interval spans 0.68 < 1.2); the selected index was computable for 16/18 (`qwen36|H2`, `qwen36|R4` have `ms_gold` ladder coverage 19/24 < 80% after parse errors). The paper's frozen indices do not transfer: `PTI_v0_frozen` test ρ -0.274 (n=9; NOT_COMPUTABLE for 9 test units because the exact-zero geometric mean needs every ladder and the 3 alpha probes) and `TI_var_trainnorm` test ρ -0.332 (n=18).

| Index | Train ρ (n) | Val ρ (n) | Test ρ [95% CI] (n) | Test τ-b | Test Pearson | Permutation p (one-sided) |
|---|---|---|---|---|---|---|
| **C_ms_gold** | 0.761 (18) | 0.762 (20) | 0.558 [0.08, 0.76] (16) | 0.360 | 0.643 | 0.0127 |
| **PTI_v0_frozen** | 0.433 (15) | — (18) | -0.274 [-0.75, 0.11] (9) | -0.236 | -0.075 | 0.7793 |
| **TI_var_trainnorm** | -0.010 (18) | -0.177 (20) | -0.332 [-0.64, 0.13] (18) | -0.172 | -0.194 | 0.9135 |

Secondary single components on the test units (not pre-registered): `GM_mono2` 0.128 (n=14), `C_ident` 0.697 (n=18), `C_ms_cand` -0.054 (n=16), `C_bm_gold` 0.423 (n=18), `C_alpha` 0.143 (n=15), `C_sorry` 0.354 (n=18), `C_spam` 0.612 (n=17), `C_stab` 0.007 (n=18). Not computable on test (a component with `reorder`, or `blank` after the deterministic zero): `GM_cov5`, `GM_cov6`, `GM_cov7`, `GM_all10`, `AM_cov7`, `MIN_cov7`, `GM_inv3`, `GM_bm_ms_inv`, `C_blank`, `C_reorder`. Human ceiling on the criterion items: 0.747; criterion ranking reproducibility across configurations (val items vs test items, 47 LLM units): 0.928.

Harness view (descriptive): over the 14 single-call test units alone, `C_ms_gold` ρ 0.573, `TI_var_trainnorm` ρ -0.377, `PTI_v0_frozen` not computable; the four Terminus2 agent-judge units all sit at the top of both axes:

| Agent-judge unit | Criterion ρ | C_ms_gold | PTI_v0_frozen | TI_var_trainnorm |
|---|---|---|---|---|
| `t2_qwen|D0` | 0.818 | 0.995 | 0.000 | 0.220 |
| `t2_qwen|H2` | 0.870 | 0.993 | — | 0.008 |
| `t2_sonnet5|D0` | 0.768 | 0.996 | 0.000 | 0.007 |
| `t2_sonnet5|H2` | 0.864 | 0.992 | 0.000 | 0.007 |

Selection record: train ranking (Spearman with the criterion over the 18 train LLM units) `C_ms_gold` 0.761, `C_ident` 0.742, `GM_mono2` 0.646, `C_ms_cand` 0.486, `PTI_v0_frozen` 0.433 (n=15), …, `TI_var_trainnorm` -0.010; val check of the three finalists `C_ms_gold` 0.762, `C_ident` 0.723, `GM_mono2` 0.380 (n=20). Full tables: [results/RESULTS_proxy_index_train_val_test.md](results/RESULTS_proxy_index_train_val_test.md); receipts `results/SELECTION.json`, `results/TEST_RECEIPT.json`, `results/units_train_val.json`, `results/units_test.json`.

## Judge campaign (final, per configuration)

<!-- campaign-table:begin -->
_Merged configurations as of 10-01-2026 00:15 UTC: 56/56; measured cells 28,345 of 29,176 merged cells; Vals-reported charges $573.01 on merged main + recovery runs, plus $1.21 on the 56 smoke cells._

| Configuration | Split | Selector | Cells | Measured | Deterministic | Missing (class) | Recovered | Charges (USD) |
|---|---|---|---:|---:|---:|---|---:|---:|
| `sol6h|D0` | train | `openai/gpt-6-sol-high` | 521 | 456 | 56 | unmeasured_extraction 9 | 0 | 4.35 |
| `sol6h|H0` | train | `openai/gpt-6-sol-high` | 521 | 521 | 0 | 0 | 1 | 7.22 |
| `sol6h|H1` | train | `openai/gpt-6-sol-high` | 521 | 521 | 0 | 0 | 0 | 6.24 |
| `sol6h|H2` | train | `openai/gpt-6-sol-high` | 521 | 521 | 0 | 0 | 0 | 6.04 |
| `sol6h|LEX` | train | `openai/gpt-6-sol-high` | 521 | 521 | 0 | 0 | 0 | 2.14 |
| `sol6h|P1` | train | `openai/gpt-6-sol-high` | 521 | 521 | 0 | 0 | 0 | 2.38 |
| `sol6h|P4` | train | `openai/gpt-6-sol-high` | 521 | 521 | 0 | 0 | 1 | 2.59 |
| `sol6h|P8` | train | `openai/gpt-6-sol-high` | 521 | 521 | 0 | 0 | 0 | 2.18 |
| `sol6h|R4` | train | `openai/gpt-6-sol-high` | 521 | 521 | 0 | 0 | 0 | 7.34 |
| `sonnet5m|D0` | train | `anthropic/claude-sonnet-5-medium` | 521 | 456 | 56 | unmeasured_extraction 9 | 0 | 9.53 |
| `sonnet5m|H0` | train | `anthropic/claude-sonnet-5-medium` | 521 | 518 | 0 | parse_error 3 | 0 | 11.12 |
| `sonnet5m|H1` | train | `anthropic/claude-sonnet-5-medium` | 521 | 520 | 0 | parse_error 1 | 0 | 9.62 |
| `sonnet5m|H2` | train | `anthropic/claude-sonnet-5-medium` | 521 | 505 | 0 | parse_error 16 | 1 | 10.56 |
| `sonnet5m|LEX` | train | `anthropic/claude-sonnet-5-medium` | 521 | 520 | 0 | parse_error 1 | 0 | 3.23 |
| `sonnet5m|P1` | train | `anthropic/claude-sonnet-5-medium` | 521 | 519 | 0 | parse_error 2 | 1 | 3.26 |
| `sonnet5m|P4` | train | `anthropic/claude-sonnet-5-medium` | 521 | 521 | 0 | 0 | 0 | 3.45 |
| `sonnet5m|P8` | train | `anthropic/claude-sonnet-5-medium` | 521 | 521 | 0 | 0 | 0 | 3.22 |
| `sonnet5m|R4` | train | `anthropic/claude-sonnet-5-medium` | 521 | 520 | 0 | parse_error 1 | 0 | 10.96 |
| `gem31h|D0` | val | `google/gemini-3.1-pro-preview` | 521 | 456 | 56 | unmeasured_extraction 9 | 2 | 9.98 |
| `gem31h|H0` | val | `google/gemini-3.1-pro-preview` | 521 | 521 | 0 | 0 | 4 | 13.70 |
| `gem31h|H1` | val | `google/gemini-3.1-pro-preview` | 521 | 520 | 0 | parse_error 1 | 4 | 13.48 |
| `gem31h|H2` | val | `google/gemini-3.1-pro-preview` | 521 | 520 | 0 | parse_error 1 | 8 | 15.46 |
| `gem31h|LEX` | val | `google/gemini-3.1-pro-preview` | 521 | 521 | 0 | 0 | 4 | 4.26 |
| `gem31h|P1` | val | `google/gemini-3.1-pro-preview` | 521 | 521 | 0 | 0 | 7 | 4.19 |
| `gem31h|P4` | val | `google/gemini-3.1-pro-preview` | 521 | 521 | 0 | 0 | 9 | 4.26 |
| `gem31h|P8` | val | `google/gemini-3.1-pro-preview` | 521 | 521 | 0 | 0 | 6 | 3.64 |
| `gem31h|R4` | val | `google/gemini-3.1-pro-preview` | 521 | 520 | 0 | parse_error 1 | 2 | 12.72 |
| `luna6h|D0` | val | `openai/gpt-6-luna-high` | 521 | 455 | 56 | parse_error 1, unmeasured_extraction 9 | 2 | 0.35 |
| `luna6h|H0` | val | `openai/gpt-6-luna-high` | 521 | 521 | 0 | 0 | 0 | 0.50 |
| `luna6h|H1` | val | `openai/gpt-6-luna-high` | 521 | 521 | 0 | 0 | 0 | 0.40 |
| `luna6h|H2` | val | `openai/gpt-6-luna-high` | 521 | 521 | 0 | 0 | 2 | 0.40 |
| `luna6h|LEX` | val | `openai/gpt-6-luna-high` | 521 | 521 | 0 | 0 | 1 | 0.10 |
| `luna6h|P1` | val | `openai/gpt-6-luna-high` | 521 | 521 | 0 | 0 | 1 | 0.15 |
| `luna6h|P4` | val | `openai/gpt-6-luna-high` | 521 | 520 | 0 | parse_error 1 | 1 | 0.20 |
| `luna6h|P8` | val | `openai/gpt-6-luna-high` | 521 | 521 | 0 | 0 | 0 | 0.12 |
| `luna6h|R4` | val | `openai/gpt-6-luna-high` | 521 | 521 | 0 | 0 | 1 | 0.49 |
| `t2_luna|D0` | val | `openai/gpt-6-luna-high` | 521 | 454 | 56 | parse_error 2, unmeasured_extraction 9 | 1 | 0.69 |
| `t2_luna|H2` | val | `openai/gpt-6-luna-high` | 521 | 519 | 0 | parse_error 2 | 5 | 1.14 |
| `opus55x|D0` | test | `anthropic/claude-opus-5-5-no-fallback` | 521 | 456 | 56 | unmeasured_extraction 9 | 6 | 58.42 |
| `opus55x|H0` | test | `anthropic/claude-opus-5-5-no-fallback` | 521 | 520 | 0 | model_error 1 | 11 | 87.83 |
| `opus55x|H2` | test | `anthropic/claude-opus-5-5-no-fallback` | 521 | 521 | 0 | 0 | 1 | 65.38 |
| `opus55x|LEX` | test | `anthropic/claude-opus-5-5-no-fallback` | 521 | 521 | 0 | 0 | 0 | 12.96 |
| `opus55x|P4` | test | `anthropic/claude-opus-5-5-no-fallback` | 521 | 515 | 0 | model_error 6 | 3 | 44.12 |
| `qwen36|D0` | test | `alibaba/qwen3.6-27b` | 521 | 449 | 56 | parse_error 7, unmeasured_extraction 9 | 0 | 4.15 |
| `qwen36|H0` | test | `alibaba/qwen3.6-27b` | 521 | 501 | 0 | parse_error 20 | 0 | 4.66 |
| `qwen36|H1` | test | `alibaba/qwen3.6-27b` | 521 | 506 | 0 | parse_error 15 | 0 | 4.87 |
| `qwen36|H2` | test | `alibaba/qwen3.6-27b` | 521 | 489 | 0 | parse_error 31, unmeasured_infra 1 | 0 | 5.32 |
| `qwen36|LEX` | test | `alibaba/qwen3.6-27b` | 521 | 491 | 0 | parse_error 30 | 1 | 2.49 |
| `qwen36|P1` | test | `alibaba/qwen3.6-27b` | 521 | 500 | 0 | parse_error 21 | 0 | 2.98 |
| `qwen36|P4` | test | `alibaba/qwen3.6-27b` | 521 | 511 | 0 | parse_error 10 | 0 | 3.23 |
| `qwen36|P8` | test | `alibaba/qwen3.6-27b` | 521 | 497 | 0 | parse_error 24 | 2 | 2.61 |
| `qwen36|R4` | test | `alibaba/qwen3.6-27b` | 521 | 504 | 0 | parse_error 17 | 0 | 5.07 |
| `t2_qwen|D0` | test | `alibaba/qwen3.6-27b` | 521 | 447 | 56 | parse_error 6, unmeasured_extraction 9, unmeasured_infra 3 | 4 | 11.04 |
| `t2_qwen|H2` | test | `alibaba/qwen3.6-27b` | 521 | 500 | 0 | parse_error 21 | 6 | 17.79 |
| `t2_sonnet5|D0` | test | `anthropic/claude-sonnet-5-medium` | 521 | 456 | 56 | unmeasured_extraction 9 | 0 | 17.99 |
| `t2_sonnet5|H2` | test | `anthropic/claude-sonnet-5-medium` | 521 | 521 | 0 | 0 | 1 | 30.47 |
<!-- campaign-table:end -->

## Deviations and open questions for Brando

- 09-30-2026, before any call (PR #48 review by the sibling session): the probe theorem finder missed same-line `@[attr] theorem` heads (60 of 181 gold theorems found); widened to 181/181, `ms_gold` levels 57 → 83, quote 50,224 → 51,500 calls. Core `declarations()` (PTI-v0 numerics, bug-ladder targets) unchanged.
- 09-30-2026, before any call (Brando, PR #49 merged to main as c97be81): PROTOCOL.md Amendment 1 removes the automatic $2,000 spend cap; Valkyrie runs are not auto-capped, and charges are recorded after every merge, never used to hold admissions. Merged into this branch during the smoke stage, before any main admission.
- 09-30-2026, before any call (skampere1 worker): the first Lean-validated probe build found that **72 of the 75 rated candidates do not elaborate under Lean 4.22 + Mathlib v4.22** (3 elaborate: `0_unsafeCopy_safe__agent1`, `13_MyUppercase__agent1`, `33_MyMinimum__agent2`) and that the gold `1_MyAdd` does not elaborate (unsolved goals), so 24/25 golds carry ladders. First-error classes over the 72 candidates: 9 stop at `import VeriBench`/`VeriBench.Prelude`/`VeriBench.Common` (a prelude the grading project does not provide), ~25 import modules that no longer exist in this toolchain (`Std.Data.List.Basic`, `Lean.Data.HashMap`, `Mathlib.Data.List.Perm`, `Mathlib.Tactic.LibrarySearch`, ...), 14 contain literal markdown fences (parse error), and the rest fail type-checking, termination or proofs. cert-judge's frozen PTI-v0 run on the same Claude 3.7 sample population (`experiments/archive/04_veribench_validation/results_pti_v0_v4/probe_validity_manifest.json`) elaborated only 86 of 470 candidates (18%), so a low rate is a known property of these samples, not of this run. **Environment preparation, as in the frozen PTI-v0 pipeline (`run_pti_v0.py` `_LOCAL_LEAN_MODULES`):** the empty prelude modules `VeriBench`, `VeriBench.Common` and `VeriBench.Prelude` were compiled with `cert_judge.probe_validation.LeanCompiler.compile_module` from cert-judge's own sources (`data/veribench_dataset/lean_src/veribench.lean` sha256 d0d1fda6…, `veribench/Common.lean` and `veribench/Prelude.lean` sha256 6a3ad70c…, byte-identical to the archived run's records) into a private mirror of the grading project (`private/lean_mirror`: the same `lakefile.toml`, `lake-manifest.json`, `lean-toolchain` and a symlink to the same built packages; the shared project `/lfs/skampere1/0/brando9/vb90_grading/lean_project` was not modified). The probes were then rebuilt against the mirror. `PROTOCOL.md` is unchanged: a candidate that does not elaborate keeps only its criterion cell, invalid probes are excluded before any call, and every count is in `results/probe_manifest.json`. **Consequence for Brando:** the candidate-side components (`ms_cand`, `alpha`, `reorder`, `sorry`, `spam`) rest on very few candidates, so every pre-registered candidate index that contains `reorder` (GM_cov5/6/7, AM_cov7, MIN_cov7, GM_inv3, GM_bm_ms_inv, C_reorder) is expected to be NOT_COMPUTABLE and the family effectively reduces to the gold-side indices, `PTI_v0_frozen`, `TI_var_trainnorm`, `GM_mono2` and the single components; the report states the exact denominators.
- 09-30-2026, before any call (skampere1 worker): Valkyrie rejects benchmark names containing an underscore (`Invalid benchmark name` for `certjudge39-t2_luna`), so the three agent-judge services were stopped and redeployed as `certjudge39-t2-luna`, `certjudge39-t2-sonnet5` and `certjudge39-t2-qwen` (`scripts/deploy_service.py` folds the key's underscore to a hyphen; `scripts/pack.py` and `results/packs.json` carry the same informational name; packs, ports, bearer and prompt bytes unchanged). All nine benchmarks list their tasks through Valkyrie: 4,633 for each nine-prompt model, 2,545 for Claude Opus 5.5, 979 per agent judge.
- 09-30-2026, smoke stage (skampere1 worker): (a) all six Terminus2 agent-judge smokes failed in the benchmark service's sandbox provisioning (`verify` phase: `python3 missing`) before the agent ran: the service's default sandbox image is a bare Ubuntu 24.04 digest without a system `python3`; the `vb103_judge` bundle's setup installs one with apt before that phase, the Terminus2 bundle's setup does not (it installs `uv` and a private CPython venv). Fix: the three agent-judge services (only) run on the digest-pinned public image `python@sha256:1aaa65a8…` (python:3.12-slim-bookworm, linux/amd64), set through the service's documented `VB_BASE_IMAGE` knob by `scripts/deploy_service.py` (`E39_AGENT_BASE_IMAGE`); the harness bundle, kwargs, prompt bytes and packs are unchanged; recorded in `results/deployment_t2_*.json`. (b) The gateway registry (read inside Valkyrie) has no `google/gemini-3.1-pro-preview-high` and no `alibaba/qwen3.6-27b-thinking` (the `vb103_judge` agent raised KeyError before any request, `requests_sent` 0): per cc.md step 7, `results/selectors.json` records the next pre-registered selector of the same model, `google/gemini-3.1-pro-preview` for `gem31h` and `alibaba/qwen3.6-27b` for `qwen36` and `t2_qwen`, before any admission of those models that reaches a model; the pre-registered substitutes (`openai/gpt-5.6-luna-high`, then `anthropic/claude-opus-5-no-fallback` for Qwen) remain the next options. The 24 affected smoke admissions (all $0, no model call) are retired in `private/judge/state.json` (`retired_admissions`) and re-admitted.
- 09-30-2026, smoke stage (skampere1 worker): after the two fixes all 56 smoke cells are measured on the first re-attempt for Gemini 3.1 Pro (`google/gemini-3.1-pro-preview`, $0.008–0.051 per call), Qwen3.6-27B (`alibaba/qwen3.6-27b`, $0.006–0.014) and the Terminus2 agent judges on GPT-6 Luna (0.8 on H2, 4 turns) and Claude Sonnet 5 (0.3 on D0); the Terminus2+Qwen smokes are still running. The Terminus2 bundle exports no `receipt.json`, so `scripts/judge_controller.py` now reads each agent episode's Vals-reported cost and token usage from its ATIF trajectory (`final_metrics.total_cost_usd`; Luna $0.002–0.003, Sonnet 5 $0.057–0.065 per episode) and checks the service-recorded `instruction_sha256` of every served cell (both flavors) against the pack's bytes, marking a mismatch `unmeasured_infra` (the prompt-hash STOP rule for episodes without a receipt); no hash mismatch so far.
- **Final missing-cell classes (counts over the 56 configurations, every one reconciled one-to-one against its pack):** parse_error 235 (a verdict that the rubric's parser rejects; concentrated in Qwen3.6-27B: 7–31 per configuration, 182 in total, Claude Sonnet 5 H2 16, Terminus2 + Qwen 27, others ≤ 3), model_error 7 (Claude Opus 5.5: H0 1, P4 6), unmeasured_infra 4 (`qwen36|H2` 1, `t2_qwen|D0` 3, after the single recovery pass), unmeasured_extraction 81 (the deployed D0 rubric's extractor refuses 9 probe files; 9 per D0 configuration), deterministic 504 (D0's no-call rules, 56 per D0 configuration). Recovery pass: 31 runs over 97 cells; 33 main cells had ended in ERROR; no cell was admitted more than twice. Retired admissions (never reached a model, $0): 24 smoke cells, listed in `private/judge/state.json`.
- **Selectors actually used:** `openai/gpt-6-sol-high`, `anthropic/claude-sonnet-5-medium`, `openai/gpt-6-luna-high`, `google/gemini-3.1-pro-preview` (second pre-registered selector; `-high` absent from the registry), `anthropic/claude-opus-5-5-no-fallback`, `alibaba/qwen3.6-27b` (second pre-registered selector; `-thinking` absent), agent judges through `brando_terminus_gateway` (max_turns 20, reasoning_effort high) on `openai/gpt-6-luna-high`, `anthropic/claude-sonnet-5-medium`, `alibaba/qwen3.6-27b`. No substitute from the substitutes list was needed.
- **Amendments:** PROTOCOL.md Amendment 1 only (no automatic spend cap; Brando, before any judge call). PROTOCOL.md was not edited by the worker.
- **Operational deviations (zero effect on prompts, cells or scoring):** `scripts/parallel_harvest.py` harvested terminal runs in parallel because `valk run results` takes ~4.5 min per run; `scripts/driver.py` now skips the controls / unit re-analysis after the seal and restores the sealed `results/units_train_val.json` from git if a re-run rewrote its timestamp (the first post-seal pass hit that refusal); `scripts/judge_controller.py` reads agent-episode costs from the Terminus2 ATIF trajectory and checks the served instruction hash.
- **Open question for Brando:** with only 3 of 75 rated candidates elaborating under Lean 4.22, the candidate-side components are nearly empty, so the pre-registered family effectively reduced to the gold-side indices and single components; a follow-up with a candidate pool that compiles (or a protocol that validates candidate probes relative to the candidate's own elaboration state) is needed before claiming anything about `alpha`, `reorder`, `sorry`, `spam` or `ms_cand`.

**TLDR-end:** [cert-judge: e39-proxy-index] Experiment 39 is complete: all 28,591 declared judge cells were judged through Valkyrie ($574), the label-free index selected on the train judge models (`C_ms_gold`, gold missing-statement monotonicity) passes the pre-registered test on the held-out judge models (Spearman 0.56, permutation p 0.013, train/val/test correlations within 0.30), while the paper's frozen `PTI_v0` and `TI_var` do not transfer; the candidate-side probe family was too thin (3/75 candidates elaborate) to say anything about the rewrite-invariance components.
