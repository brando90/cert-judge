# Experiment 39: a label-free proxy index searched on train judge models, checked on val, tested once on held-out judge models

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/39_label_free_proxy_index_train_val_test_over_judge_families/README.md>

**TLDR:** The paper's index (`TI_var`) was designed and evaluated on the same 72-pair panel, and its one held-out attempt (experiment 43) had a criterion with no signal, so nothing in cert-judge shows that a label-free property index predicts judge–human agreement on judges it was not tuned on. This experiment fixes both problems: the criterion is each judge configuration's Spearman agreement with VeriBench's three-expert coverage ratings on the 45 held-out items (the labels and inputs experiment 100 validated a judge against, human ceiling 0.747), and the proxy is searched over a pre-registered family of property indices on the train judge models (GPT-6 Sol, Claude Sonnet 5, plus non-LLM controls), checked on the val judge models (GPT-6 Luna, Gemini 3.1 Pro) and tested once on the test judges (Claude Opus 5.5, Qwen3.6-27B, and two Terminus2 agent judges). Agent judges are in the panel so that the proxy is tested across harnesses, not only across models: the claim is that the same label-free screen works for any new judge, single call or agent. 60 units (50 single-call model × prompt configurations, 6 agent-judge configurations in which the Terminus2 agent harness judges with the same rubric bytes, 4 controls), about 51,500 Valkyrie judge calls (planning estimate about $1,420; no automatic spend cap, PROTOCOL.md Amendment 1), Lean-validated probes, no new human labels. Every model and agent call goes through Valkyrie. Decision: the selected index passes if its test Spearman is at least 0.45 with permutation p below 0.05; the paper's frozen `PTI_v0` and `TI_var` are reported on every split regardless.

## Goal, hypothesis and decision criterion

**Central uncertainty (Trigger Rule 50).** Does a label-free index computed from scripted edits of gold and candidate Lean files rank judge configurations the way their agreement with expert human ratings ranks them, *for judge models the index was not chosen on*? If not, the protocol in the ICLR paper cannot replace per-judge human validation, and the paper must say so.

**Hypothesis.** At least one pre-registered index (the coverage-matched candidates built from missing-statement monotonicity, rewrite invariance, spam non-increase and repeat stability) reaches Spearman ≥ 0.45 with the criterion on the test judge models, and its train, val and test correlations lie within 0.30 of each other. Secondary hypothesis: the paper's `TI_var` (bug-ladder only, panel-normalized) does worse than the coverage-matched candidates on the coverage criterion.

**Decision.** PASS → the paper's claim is re-stated with the held-out numbers and the selected index; FAIL (test ρ < 0.45 or p ≥ 0.05) → the paper's protocol section is rewritten as a negative result with these numbers, and any future proxy must be tested this way before it is claimed. Inconclusive is possible (wide intervals at n = 14 test units) and is reported as such; no threshold is moved after the fact ([PROTOCOL.md](PROTOCOL.md)).

**Why this and not more human labels.** Experiment 100 (VeriBench) already spent the labels well: 75 items, three experts, task split 10/5/10, annotation-era inputs. What was missing on the cert-judge side was never labels; it was a criterion with signal and judges spread across it. Experiment 100's held-out ablations gave eight configurations spanning 0.10–0.85; this experiment extends that to 50 configurations across six judge models so that a proxy can be selected on some and tested on others.

## Structure

```
39_label_free_proxy_index_train_val_test_over_judge_families/
├── README.md                    # this design doc
├── PROTOCOL.md                  # locked contract (before any judge call)
├── COST_QUOTE.md                # planning estimate from the dry run; the exact quote is results/QUOTE.json on SNAP
├── cc.md                        # the SNAP worker runbook (paste into Claude Code / Codex)
├── results.md                   # live ledger (Trigger Rule 37)
├── CKPT_proxy_index_search.md   # resumable checkpoint (Trigger Rule 44)
├── prompts/                     # the paper's legacy judge prompts, ported verbatim (P1_BASELINE, P4_CHECKLIST, P8_STRICT_B, BAD_STRINGY)
├── scripts/
│   ├── e39.py                   # frozen constants: panel, split, cell kinds, paths, VeriBench imports
│   ├── probes.py                # probe constructors (fail-closed Lean validation)
│   ├── legacy.py                # legacy prompt renderer/parser (reference = gold's last theorem block, as in the paper)
│   ├── build_panel.py           # results/panel.json (units, families, splits, prompt fingerprints)
│   ├── build_probes.py          # results/probe_manifest.json + private/probes/ (Lean-validated artifacts)
│   ├── render_cells.py          # private/cells/<config>/<cell>.json + results/cells/<config>.json (hashes only)
│   ├── quote.py                 # results/QUOTE.json: exact call count, expected and worst-case cost vs cap
│   ├── pack.py                  # private/packs/<model>/ Valkyrie task packs (experiment 103's format) + round-trip check
│   ├── deploy_service.py        # one collect-only pack service per judge model (experiment 103's service, read-only)
│   ├── verify_bundle.py         # the served vb103_judge agent is byte-identical to the validated bundle
│   ├── verify_agent_harness.py  # records the Terminus2 bundle (contract kwargs, secret mapping) used by the agent judges
│   ├── judge_controller.py      # admit / poll / harvest / recover / merge through `valk`
│   ├── local_controls.py        # the four deterministic non-LLM controls
│   ├── analysis_lib.py          # statistics, criterion, components, frozen indices, candidate family
│   ├── analyze.py               # units -> select (train->val) -> sealed test unlock -> report
│   ├── driver.py, worker_loop.sh  # durable stage driver for the tmux worker
│   └── test_e39.py              # offline unit tests (19)
├── results/                     # committed receipts: panel.json, probe_manifest.json, QUOTE.json, packs.json, harvest/,
│                                #   units_train_val.json, FINALISTS.json, SELECTION.json, TEST_RECEIPT.json, units_test.json,
│                                #   RESULTS_proxy_index_train_val_test.md; planning_dryrun/ holds the unvalidated dry run
└── private/                     # git-ignored: prompt bytes, probe Lean files, packs, raw verdicts, Valkyrie config, logs
```

## Method

1. **Units and split (frozen in `scripts/e39.py`, receipt `results/panel.json`).** A unit is one judge configuration = judge model × prompt. Prompts: VeriBench's D0 (deployed scoreboard rubric), R4 (experiment 75), H0/H1/H2 (experiment 100's human-mirror family, H2 being the validated judge prompt) and the cert-judge paper's P1_BASELINE, P4_CHECKLIST, P8_STRICT_B and BAD_STRINGY (the deliberately lexical judge). Judge models and their split: **train** GPT-6 Sol (high) and Claude Sonnet 5 (medium); **val** GPT-6 Luna (high), Gemini 3.1 Pro (high) and the agent judge Terminus2 + GPT-6 Luna; **test** Claude Opus 5.5 (max; five prompts H2, H0, D0, P4, LEX), Qwen3.6-27B (thinking), and the agent judges Terminus2 + Claude Sonnet 5 (a held-out harness on a train model) and Terminus2 + Qwen3.6-27B (held-out harness and model). Agent judges run the H2 and D0 prompts: the frozen prompt bytes are delivered as the agent's task with one instruction to write the verdict file, so rubric and inputs are identical to the single-call units and only the harness differs. Four deterministic controls (edit distance, seeded random, theorem-count ratio, theorem-name Jaccard) sit in train only. 18 / 20 / 18 LLM units (single-call 18 / 18 / 14, agent 0 / 2 / 4).
2. **Criterion (labels used here and nowhere else).** For each unit, Spearman between its median-of-3 score and the expert mean (participants 1–3, divided by 5) over the 45 items of experiment 75's val and test tasks, with the annotation-era references and Python the raters saw (experiment 100's `inputs/`). Task-clustered bootstrap intervals; secondary views on the 30 test items and all 75 items.
3. **Probes (label-free, Lean-validated, `scripts/build_probes.py`).** Per task: identity (gold as candidate, 3 repeats), blank candidate, cumulative theorem-statement deletion from the gold (≤ 4 levels), cert-judge's cumulative implementation-bug ladder on the gold (4 levels, 3 repeats). Per rated candidate: 3 repeats of the criterion cell, cumulative statement deletion (≤ 3 levels), alpha-renaming, adjacent-theorem reorder, proofs → `sorry`, three irrelevant true theorems appended. Every transformed file must elaborate under Lean 4.22 + Mathlib; otherwise it is excluded before any call. The probe theorem finder accepts same-line `@[attr] theorem` and `private`/`protected` heads (the core cert-judge finder saw 60 of the 181 gold theorems; the widened one sees 181/181 and 137/137 candidate theorems, checked against experiment 100's counts). A candidate that does not elaborate keeps only its criterion cell.
4. **Judge calls (Valkyrie only).** Prompts rendered with experiment 100's frozen `prompts.render` (H*, R4, D0) or the paper's templates (`scripts/legacy.py`); packed in experiment 103's task-file format; served through experiment 103's collect-only service; delivered by the validated `vb103_judge` agent, one `/query` per cell (single-call judges), or by the Terminus2 bundle recorded by `scripts/verify_agent_harness.py` for the agent judges (the agent writes the verdict file, the service collects it); verdicts parsed on the host with each rubric's parser. The paper's legacy prompts show a judge only the gold's last theorem block, exactly as in the paper, so for those configurations a gold-deletion ladder is informative only at its first level; that is a property of the configuration under test and is reported, not corrected. Admission order train → val → test, one spare smoke cell per configuration first, one labelled recovery pass for cells with no verdict, charges recorded.
5. **Components and indices (`scripts/analysis_lib.py`).** Ten components in [0, 1]: identity, blank, missing-statement monotonicity on gold and on candidates, bug monotonicity, alpha / reorder / sorry invariance, spam non-increase, repeat stability. Frozen paper indices: `PTI_v0` exactly as `docs/spec/PTI_V0.md`, and `TI_var` with its min–max normalization frozen from the train units. Candidate family: 22 pre-registered forms (geometric, arithmetic and minimum aggregations of component subsets, and every single component).
6. **Selection and test (`scripts/analyze.py`).** Rank the candidates by Spearman with the criterion over the train units; keep three; select by val. The test-unit rows are written to `private/` and unlocked only by `analyze.py test --finalists-commit <sha>` after `results/FINALISTS.json` is committed. Report Spearman, Kendall, Pearson, bootstrap intervals over units and a one-sided permutation p; the frozen paper indices on every split; and the criterion's own split-half reliability as the attenuation bound.

## Dependencies

- VeriBench checkout with experiments 75, 95 (`tc_gateway/canonical`), 100, 103 and 105 (read-only); the worker clones its own copy on SNAP.
- Lean 4.22 + Mathlib project `/lfs/skampere1/0/brando9/vb90_grading/lean_project` (experiment 105's), `lake env lean`.
- Valkyrie (`valk`, `VALKYRIE_ENV=bench`) with the Vals configuration on the host; experiment 103's `vb103_judge` agent as published; experiment 103's `vb_service_single_call` service code; cloudflared; the `vb103_venv` Python.
- Funding: Vals (Valkyrie); no personal or provider key; no automatic spend cap (PROTOCOL.md Amendment 1), Vals-reported charges recorded.
- cert-judge `py_src/cert_judge/{probe_validation,pti_v0}.py` for probe construction and the frozen numerics.

## Status

| Step | Status | Notes |
|---|---|---|
| Design, code, offline tests | Done (09-30-2026) | 19 tests pass; dry run renders 56 configurations, 51,500 calls, $1,421 expected ([COST_QUOTE.md](COST_QUOTE.md)) |
| Protocol locked | Done (09-30-2026) | [PROTOCOL.md](PROTOCOL.md) |
| Dispatch to SNAP | Done (09-30-2026) | tmux `cj-e39-proxy-index-search` on skampere1, branch `e39-proxy-index-search` |
| Probes elaborated (Lean) | Done (09-30-2026) | 24/25 golds, 3/75 candidates elaborate under Lean 4.22 + Mathlib (`results/probe_manifest.json`); see `results.md` deviations |
| Agent harness check + smoke + main admission (train → val → test) | Done (09-30-2026) | 56 smoke + 56 main runs; `brando_terminus_gateway` on a python3 sandbox image; `results/agent_harness.json`, `results/selectors.json` |
| Harvest, recovery pass, merge | Done (10-01-2026) | 28,591 cells reconciled one-to-one; 31 recovery runs; $574 Vals-reported |
| Selection (train → val) | Done (10-01-2026) | selected `C_ms_gold` (train ρ 0.761, val ρ 0.762); seal commit `86ae479` |
| One-shot test | Done (10-01-2026) | **PASS**: test ρ 0.558 [0.08, 0.76], permutation p 0.0127; `PTI_v0` -0.274, `TI_var` -0.332 on test |
| Report | Done (10-01-2026) | [results.md](results.md), [results/RESULTS_proxy_index_train_val_test.md](results/RESULTS_proxy_index_train_val_test.md) |
