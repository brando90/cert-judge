# Experiment 39 results: label-free proxy index, train / val / test over judge models

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results.md>

**Status:** RUNNING (started 09-30-2026 12:09 PDT; worker tmux `cj-e39-proxy-index-search` on skampere1, branch `e39-proxy-index-search`; no judge call made yet)
**Last updated:** 09-30-2026 15:02 PDT

Experiment 39: 56 judge configurations (50 single-call: six judge models × the VeriBench and cert-judge prompt families; 6 agent judges: Terminus2 + GPT-6 Luna / Claude Sonnet 5 / Qwen3.6-27B on the H2 and D0 rubrics) plus 4 controls, judged on Lean-validated probes through Valkyrie; a label-free index is selected on the train judge models (GPT-6 Sol, Claude Sonnet 5), checked on val (GPT-6 Luna, Gemini 3.1 Pro, Terminus2 + Luna) and tested once on held-out judges (Claude Opus 5.5, Qwen3.6-27B, Terminus2 + Sonnet 5, Terminus2 + Qwen) against agreement with the expert coverage ratings on 45 held-out VeriBench items; results pending.

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
| Smoke per configuration; main admission train → val → test; recovery pass; merge | IN PROGRESS since 09-30-2026 13:27 PDT: 56 smoke runs admitted, 32 measured on the first attempt (GPT-6 Sol 9/9, Claude Sonnet 5 9/9, GPT-6 Luna 9/9, Claude Opus 5.5 5/5; $0.76 in smoke charges), 24 retired at $0 and re-admitted after two fixes (see deviations); all 56 main runs admitted by 21:23Z (concurrency 20 each; every smoke measured, including the six Terminus2 agent judges); train configurations are being harvested, recovered and merged, see the live table below | `results/judge_progress.json`, `results/harvest/` |
| Criterion, components, indices (train + val rows open; test rows sealed) | PENDING | `results/units_train_val.json` |
| Selection committed | PENDING | `results/FINALISTS.json`, `results/SELECTION.json` |
| One-shot test | PENDING | `results/TEST_RECEIPT.json` |
| Report and landing | PENDING | `results/RESULTS_proxy_index_train_val_test.md`, PR |

## Numbers so far

| Quantity | Value | Source |
|---|---|---|
| Units | 60 (train 18 LLM + 4 controls; val 20 incl. 2 agent judges; test 18 incl. 4 agent judges) | `results/panel.json` |
| Calls per configuration (after Lean exclusions) | 521 (D0 configurations: 456 + 56 deterministic + 9 unmeasured extraction) | `results/cells_summary.json` |
| Total calls (exact, after Lean exclusions) | 28,591 (single-call 25,660 + agent-judge 2,931; dry-run upper bound was 51,500) | `results/QUOTE.json` |
| Expected charges | $790.59 (train $129.49, val $127.01, test $534.13); no automatic cap (PROTOCOL.md Amendment 1); dry-run estimate was $1,421 | same |
| Valid probes (Lean 4.22 + Mathlib) | golds with ladders 24/25; candidates elaborating 3/75 (ms_cand 3, alpha 3, reorder 0, sorry 3, spam 3 valid probes) | `results/probe_manifest.json` |
| Human ceiling on the criterion items | 0.747 (mean leave-one-expert-out Spearman, 45 items) | VeriBench experiment 100 |
| Criterion correlations, component values, index correlations | not measured | — |

## Judge campaign (live, per configuration)

<!-- campaign-table:begin -->
_Merged configurations as of 09-30-2026 22:02 UTC: 6/56; measured cells 3,061 of 3,126 merged cells; Vals-reported charges $23.32 on merged main + recovery runs, plus $1.21 on the 56 smoke cells._

| Configuration | Split | Selector | Cells | Measured | Deterministic | Missing (class) | Recovered | Charges (USD) |
|---|---|---|---:|---:|---:|---|---:|---:|
| `sol6h|D0` | train | `openai/gpt-6-sol-high` | 521 | 456 | 56 | unmeasured_extraction 9 | 0 | 4.35 |
| `sol6h|H0` | train | — | — | — | — | not merged yet | — | — |
| `sol6h|H1` | train | `openai/gpt-6-sol-high` | 521 | 521 | 0 | 0 | 0 | 6.24 |
| `sol6h|H2` | train | `openai/gpt-6-sol-high` | 521 | 521 | 0 | 0 | 0 | 6.04 |
| `sol6h|LEX` | train | `openai/gpt-6-sol-high` | 521 | 521 | 0 | 0 | 0 | 2.14 |
| `sol6h|P1` | train | `openai/gpt-6-sol-high` | 521 | 521 | 0 | 0 | 0 | 2.38 |
| `sol6h|P4` | train | — | — | — | — | not merged yet | — | — |
| `sol6h|P8` | train | `openai/gpt-6-sol-high` | 521 | 521 | 0 | 0 | 0 | 2.18 |
| `sol6h|R4` | train | — | — | — | — | not merged yet | — | — |
| `sonnet5m|D0` | train | — | — | — | — | not merged yet | — | — |
| `sonnet5m|H0` | train | — | — | — | — | not merged yet | — | — |
| `sonnet5m|H1` | train | — | — | — | — | not merged yet | — | — |
| `sonnet5m|H2` | train | — | — | — | — | not merged yet | — | — |
| `sonnet5m|LEX` | train | — | — | — | — | not merged yet | — | — |
| `sonnet5m|P1` | train | — | — | — | — | not merged yet | — | — |
| `sonnet5m|P4` | train | — | — | — | — | not merged yet | — | — |
| `sonnet5m|P8` | train | — | — | — | — | not merged yet | — | — |
| `sonnet5m|R4` | train | — | — | — | — | not merged yet | — | — |
| `gem31h|D0` | val | — | — | — | — | not merged yet | — | — |
| `gem31h|H0` | val | — | — | — | — | not merged yet | — | — |
| `gem31h|H1` | val | — | — | — | — | not merged yet | — | — |
| `gem31h|H2` | val | — | — | — | — | not merged yet | — | — |
| `gem31h|LEX` | val | — | — | — | — | not merged yet | — | — |
| `gem31h|P1` | val | — | — | — | — | not merged yet | — | — |
| `gem31h|P4` | val | — | — | — | — | not merged yet | — | — |
| `gem31h|P8` | val | — | — | — | — | not merged yet | — | — |
| `gem31h|R4` | val | — | — | — | — | not merged yet | — | — |
| `luna6h|D0` | val | — | — | — | — | not merged yet | — | — |
| `luna6h|H0` | val | — | — | — | — | not merged yet | — | — |
| `luna6h|H1` | val | — | — | — | — | not merged yet | — | — |
| `luna6h|H2` | val | — | — | — | — | not merged yet | — | — |
| `luna6h|LEX` | val | — | — | — | — | not merged yet | — | — |
| `luna6h|P1` | val | — | — | — | — | not merged yet | — | — |
| `luna6h|P4` | val | — | — | — | — | not merged yet | — | — |
| `luna6h|P8` | val | — | — | — | — | not merged yet | — | — |
| `luna6h|R4` | val | — | — | — | — | not merged yet | — | — |
| `t2_luna|D0` | val | — | — | — | — | not merged yet | — | — |
| `t2_luna|H2` | val | — | — | — | — | not merged yet | — | — |
| `opus55x|D0` | test | — | — | — | — | not merged yet | — | — |
| `opus55x|H0` | test | — | — | — | — | not merged yet | — | — |
| `opus55x|H2` | test | — | — | — | — | not merged yet | — | — |
| `opus55x|LEX` | test | — | — | — | — | not merged yet | — | — |
| `opus55x|P4` | test | — | — | — | — | not merged yet | — | — |
| `qwen36|D0` | test | — | — | — | — | not merged yet | — | — |
| `qwen36|H0` | test | — | — | — | — | not merged yet | — | — |
| `qwen36|H1` | test | — | — | — | — | not merged yet | — | — |
| `qwen36|H2` | test | — | — | — | — | not merged yet | — | — |
| `qwen36|LEX` | test | — | — | — | — | not merged yet | — | — |
| `qwen36|P1` | test | — | — | — | — | not merged yet | — | — |
| `qwen36|P4` | test | — | — | — | — | not merged yet | — | — |
| `qwen36|P8` | test | — | — | — | — | not merged yet | — | — |
| `qwen36|R4` | test | — | — | — | — | not merged yet | — | — |
| `t2_qwen|D0` | test | — | — | — | — | not merged yet | — | — |
| `t2_qwen|H2` | test | — | — | — | — | not merged yet | — | — |
| `t2_sonnet5|D0` | test | — | — | — | — | not merged yet | — | — |
| `t2_sonnet5|H2` | test | — | — | — | — | not merged yet | — | — |
<!-- campaign-table:end -->

## Deviations and open questions for Brando

- 09-30-2026, before any call (PR #48 review by the sibling session): the probe theorem finder missed same-line `@[attr] theorem` heads (60 of 181 gold theorems found); widened to 181/181, `ms_gold` levels 57 → 83, quote 50,224 → 51,500 calls. Core `declarations()` (PTI-v0 numerics, bug-ladder targets) unchanged.
- 09-30-2026, before any call (Brando, PR #49 merged to main as c97be81): PROTOCOL.md Amendment 1 removes the automatic $2,000 spend cap; Valkyrie runs are not auto-capped, and charges are recorded after every merge, never used to hold admissions. Merged into this branch during the smoke stage, before any main admission.
- 09-30-2026, before any call (skampere1 worker): the first Lean-validated probe build found that **72 of the 75 rated candidates do not elaborate under Lean 4.22 + Mathlib v4.22** (3 elaborate: `0_unsafeCopy_safe__agent1`, `13_MyUppercase__agent1`, `33_MyMinimum__agent2`) and that the gold `1_MyAdd` does not elaborate (unsolved goals), so 24/25 golds carry ladders. First-error classes over the 72 candidates: 9 stop at `import VeriBench`/`VeriBench.Prelude`/`VeriBench.Common` (a prelude the grading project does not provide), ~25 import modules that no longer exist in this toolchain (`Std.Data.List.Basic`, `Lean.Data.HashMap`, `Mathlib.Data.List.Perm`, `Mathlib.Tactic.LibrarySearch`, ...), 14 contain literal markdown fences (parse error), and the rest fail type-checking, termination or proofs. cert-judge's frozen PTI-v0 run on the same Claude 3.7 sample population (`experiments/archive/04_veribench_validation/results_pti_v0_v4/probe_validity_manifest.json`) elaborated only 86 of 470 candidates (18%), so a low rate is a known property of these samples, not of this run. **Environment preparation, as in the frozen PTI-v0 pipeline (`run_pti_v0.py` `_LOCAL_LEAN_MODULES`):** the empty prelude modules `VeriBench`, `VeriBench.Common` and `VeriBench.Prelude` were compiled with `cert_judge.probe_validation.LeanCompiler.compile_module` from cert-judge's own sources (`data/veribench_dataset/lean_src/veribench.lean` sha256 d0d1fda6…, `veribench/Common.lean` and `veribench/Prelude.lean` sha256 6a3ad70c…, byte-identical to the archived run's records) into a private mirror of the grading project (`private/lean_mirror`: the same `lakefile.toml`, `lake-manifest.json`, `lean-toolchain` and a symlink to the same built packages; the shared project `/lfs/skampere1/0/brando9/vb90_grading/lean_project` was not modified). The probes were then rebuilt against the mirror. `PROTOCOL.md` is unchanged: a candidate that does not elaborate keeps only its criterion cell, invalid probes are excluded before any call, and every count is in `results/probe_manifest.json`. **Consequence for Brando:** the candidate-side components (`ms_cand`, `alpha`, `reorder`, `sorry`, `spam`) rest on very few candidates, so every pre-registered candidate index that contains `reorder` (GM_cov5/6/7, AM_cov7, MIN_cov7, GM_inv3, GM_bm_ms_inv, C_reorder) is expected to be NOT_COMPUTABLE and the family effectively reduces to the gold-side indices, `PTI_v0_frozen`, `TI_var_trainnorm`, `GM_mono2` and the single components; the report states the exact denominators.
- 09-30-2026, before any call (skampere1 worker): Valkyrie rejects benchmark names containing an underscore (`Invalid benchmark name` for `certjudge39-t2_luna`), so the three agent-judge services were stopped and redeployed as `certjudge39-t2-luna`, `certjudge39-t2-sonnet5` and `certjudge39-t2-qwen` (`scripts/deploy_service.py` folds the key's underscore to a hyphen; `scripts/pack.py` and `results/packs.json` carry the same informational name; packs, ports, bearer and prompt bytes unchanged). All nine benchmarks list their tasks through Valkyrie: 4,633 for each nine-prompt model, 2,545 for Claude Opus 5.5, 979 per agent judge.
- 09-30-2026, smoke stage (skampere1 worker): (a) all six Terminus2 agent-judge smokes failed in the benchmark service's sandbox provisioning (`verify` phase: `python3 missing`) before the agent ran: the service's default sandbox image is a bare Ubuntu 24.04 digest without a system `python3`; the `vb103_judge` bundle's setup installs one with apt before that phase, the Terminus2 bundle's setup does not (it installs `uv` and a private CPython venv). Fix: the three agent-judge services (only) run on the digest-pinned public image `python@sha256:1aaa65a8…` (python:3.12-slim-bookworm, linux/amd64), set through the service's documented `VB_BASE_IMAGE` knob by `scripts/deploy_service.py` (`E39_AGENT_BASE_IMAGE`); the harness bundle, kwargs, prompt bytes and packs are unchanged; recorded in `results/deployment_t2_*.json`. (b) The gateway registry (read inside Valkyrie) has no `google/gemini-3.1-pro-preview-high` and no `alibaba/qwen3.6-27b-thinking` (the `vb103_judge` agent raised KeyError before any request, `requests_sent` 0): per cc.md step 7, `results/selectors.json` records the next pre-registered selector of the same model, `google/gemini-3.1-pro-preview` for `gem31h` and `alibaba/qwen3.6-27b` for `qwen36` and `t2_qwen`, before any admission of those models that reaches a model; the pre-registered substitutes (`openai/gpt-5.6-luna-high`, then `anthropic/claude-opus-5-no-fallback` for Qwen) remain the next options. The 24 affected smoke admissions (all $0, no model call) are retired in `private/judge/state.json` (`retired_admissions`) and re-admitted.
- 09-30-2026, smoke stage (skampere1 worker): after the two fixes all 56 smoke cells are measured on the first re-attempt for Gemini 3.1 Pro (`google/gemini-3.1-pro-preview`, $0.008–0.051 per call), Qwen3.6-27B (`alibaba/qwen3.6-27b`, $0.006–0.014) and the Terminus2 agent judges on GPT-6 Luna (0.8 on H2, 4 turns) and Claude Sonnet 5 (0.3 on D0); the Terminus2+Qwen smokes are still running. The Terminus2 bundle exports no `receipt.json`, so `scripts/judge_controller.py` now reads each agent episode's Vals-reported cost and token usage from its ATIF trajectory (`final_metrics.total_cost_usd`; Luna $0.002–0.003, Sonnet 5 $0.057–0.065 per episode) and checks the service-recorded `instruction_sha256` of every served cell (both flavors) against the pack's bytes, marking a mismatch `unmeasured_infra` (the prompt-hash STOP rule for episodes without a receipt); no hash mismatch so far.
- Every later amendment, substitute selector and missing-cell class will be listed here with counts.

**TLDR-end:** [cert-judge: e39-proxy-index] The experiment is quoted at 28,591 Valkyrie calls / $790.59 expected (no automatic spend cap, PROTOCOL.md Amendment 1) after Lean validation kept 24 golds and only 3 elaborating candidates; the SNAP worker on skampere1 has passed the transport gates and is judging (smoke stage), and the test-model rows stay sealed until the selection is committed.
