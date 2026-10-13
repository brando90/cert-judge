# Folder 42 — PROTOCOL (LOCKED before any expensive run)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/PROTOCOL.md>

**TLDR:** Locked contract for experiment 42: 194 Lean-validated probes (identity anchors plus vacuity, weakening, over-constraint and formatting-only probes built from the 25 annotation-era VeriBench references) scored by all 56 LLM judge configurations of experiment 39 (plus its 4 deterministic controls) through Valkyrie, 3 repeats per cell (32,592 judge calls), with per-judge directional accuracy, Kendall τ with weakening level, the formatting gap, a fixed pass rule, and the association with experiment 39's expert criterion on its train and val units.

This file freezes the protocol before any LLM-budget-spending run begins.
It is written PRIOR to seeing any results. Any deviation observed during
execution is documented in REPORT.md → "Open questions for Brando" (and in `results.md` → "Deviations"),
not by editing this file. Amendments, if unavoidable, are numbered, appended at the end and apply prospectively.

## Scientific question (locked)

Do LLM judges of Lean formal specifications lower their score when a specification looks right but guarantees less (vacuous, weakened or over-constrained statements), while keeping it unchanged under formatting-only edits, and do these behaviours add to a label-free index's agreement with expert judgment?

Operationally, per judge configuration (experiment 39's 56 LLM configurations and 4 controls):

- **Directional accuracy** on each semantic family F ∈ {vacuity, weakening, over-constraint}: the share of that family's valid probes whose score is strictly below the same task's identity score (the reference judged against itself). A tie counts as a miss.
- **Kendall τ-b with weakening level**: per task, between level (0 = identity, 1–3) and score; the judge value is the mean over tasks (all-tied tasks count as τ = 0). The required direction is τ < 0.
- **Formatting gap**: mean |score(formatting probe) − score(identity)| over formatting probes.
- **Decision rule:** a configuration **passes the semantic screen** iff its directional accuracy is ≥ 0.8 on each of vacuity, weakening and over-constraint **and** its formatting gap is ≤ 0.05 (point estimates). A configuration with any of the four metrics below 80% coverage of its valid probes is `NOT_COMPUTABLE`.
- **Index analysis (secondary):** Spearman association of each component (the three directional accuracies, 1 − formatting gap, −τ, and S = the geometric mean of the three accuracies and 1 − gap) with experiment 39's criterion (`criteria.heldout.spearman`, agreement with the expert coverage ratings on 45 held-out items) over experiment 39's train and val LLM units; and whether the geometric mean of experiment 39's selected index (and of `PTI_v0_frozen`, `TI_var_trainnorm`) with S has a higher Spearman with the criterion than the index alone (paired bootstrap over units for the difference). Experiment 39's test units are read only after its `results/TEST_RECEIPT.json` exists, and that analysis is labelled post hoc.

## Locked parameters

| Parameter | Value |
|---|---|
| References | experiment 100 `inputs/references/annotation/*.lean` (25 tasks; items file sha256 ad9ed552fc2ffac6…) |
| Probe families (declared per task) | `ident` L1; vacuity: `vac_true` L1 (every theorem statement → `True`), `vac_hyp` L1 (binders and premises kept, conclusion `True`); weakening: `weak` L1–L3 (cumulative, from `probe_edits/<task>.json`); over-constraint: `overc` L1 (main theorem + unsatisfiable hypothesis), L2 (every eligible theorem); formatting: `fmt_comments` L1, `fmt_layout` L1. 10 declared probes per task, 250 in all. Implementation-support lemmas used by definitions (for example a `decreasing_by` helper) are left unchanged by the vacuity probes. |
| Valid probes (Lean) | `ident` 24/25; `vac_true` 19/25; `vac_hyp` 19/25; `weak` 57/75; `overc` 37/50; `fmt_comments` 19/25; `fmt_layout` 19/25 (valid/declared; 194 valid probes of 250 declared, over 24 tasks). Invalid reasons: reference `1_MyAdd` does not elaborate (all its probes); the five `*_safe` references are already trivially true (`Post := True`), so their vacuity probes are proved equivalent and no weakening exists; over-constraint needs an explicit Nat/List/Array/String/Int binder on a theorem no other declaration uses; formatting probes need a comment or multi-line theorem head to change |
| Probe validity (fail-closed, `scripts/semantic_probes.py`) | the probe elaborates (`lake env lean`, Lean 4.22 + Mathlib project `/lfs/skampere1/0/brando9/vb90_grading/lean_project`, exit 0, `sorry` warnings allowed); semantic probes: in a check file where every data-valued implementation definition is an `axiom` of the same signature, theorem proofs are `sorry` without attributes and unit tests are dropped, Lean proves without `sorryAx`, for every theorem whose statement changed or that mentions an edited definition, `(∀ binders, reference statement) → (∀ binders, probe statement)`, and for every edited `Prop` definition `∀ binders, D_orig args → D args`; over-constraint hypotheses are proved unsatisfiable; the reverse implication is attempted with fixed automation and a probe whose every reverse implication is proved is excluded as proved-equivalent; formatting probes must `#print` exactly the same declarations with identical messages. Weakening edits may touch only theorem statements, `Prop`-valued definitions and (when needed to elaborate) theorem proofs, and may not add, remove or rename declarations. |
| Weakening proposals | written by Claude Code (claude-opus-5-5, subscription) under `probe_edits/PROPOSER_BRIEF.md`; enter the set only through the Lean checks above |
| Judge configurations | the 56 LLM units of experiment 39 (`results/panel.json`, imported from its frozen `scripts/e39.py`, prompt fingerprints identical to its receipt) + its 4 deterministic controls (edit distance, seeded random, theorem-count ratio, theorem-name Jaccard) |
| Selectors | experiment 39's pre-registered first selector per model, except the overrides it recorded from gateway-registry evidence (`results/selectors.json`: `gem31h` google/gemini-3.1-pro-preview, `qwen36` and `t2_qwen` alibaba/qwen3.6-27b); a missing selector falls back only to experiment 39's pre-registered list, recorded before that model's first admission |
| Rendering | experiment 100's frozen `prompts.render` (D0, R4, H0, H1, H2) and experiment 39's `legacy.render` (P1, P4, P8, LEX: reference = the reference's last theorem block); rendering context = the task's first item; candidate name `<task>__agent3.lean` (never reveals the probe) |
| JUDGE_REPEATS | 3 for every probe, including the identity anchor |
| Probe score | median of the scored repeats (measured or deterministic); needs ≥ 2 of 3, else the probe is unscored |
| Cells and calls | 194 valid probes × 3 repeats = 582 cells per configuration; 56 configurations → 32,592 Valkyrie judge calls (every cell rendered; no deterministic or unmeasured-extraction cells); plus one spare smoke cell per configuration (56 calls) and at most one `recovery_1` call per cell without a verdict |
| Intervals | task-clustered percentile bootstrap (tasks resampled with replacement), 10,000 draws, seed 42, 95%; index association: bootstrap over units and one-sided permutation p (10,000, seed 42) |
| File-level audit (sensitivity) | Lean proves theorem-level weakening (each changed statement is implied by the reference's). A theorem-level weakening can leave the file's overall guarantee unchanged when another unchanged theorem restates what was dropped. Before any call, Claude Code auditors (claude-opus-5-5, subscription; `probe_edits/FILE_LEVEL_AUDIT_BRIEF.md`) labelled every valid weakening and over-constraint probe strict / redundant / unclear at the file level (`probe_edits/audit/<task>.json`: overc redundant 16; overc strict 20; overc unclear 1; weak redundant 31; weak strict 25; weak unclear 1). Primary metrics use every Lean-valid probe; the pre-registered sensitivity view recomputes weakening and over-constraint directional accuracy on `strict` probes only; the pass rule uses the primary metrics |
| Thresholds | directional accuracy ≥ 0.8 per semantic family; formatting gap ≤ 0.05; metric coverage ≥ 80% |
| Transport | Valkyrie only (`VALKYRIE_ENV=bench`); single-call units through `vb103_judge` byte-identical to experiment 103's validated bundle (`results/agent_bundle_check.json` PASS); agent units through `brando_terminus_gateway` (`results/agent_harness.json` PASS; kwargs `max_turns` 20, `reasoning_effort` high; python3 sandbox image `python@sha256:1aaa65a8…` as in experiment 39); one served benchmark per judge key `certjudge42-<key>` on ports 9460–9468; one run per (configuration, part); exactly one call or agent episode per cell in `main`, one labelled `recovery_1` pass over cells without a verdict, no other retries |
| Spend | no automatic cap (repository `CLAUDE.md`, "Valkyrie runs have no automatic caps"); Vals-reported charges recorded per configuration after every merge |
| Seeds | admission permutation `random.Random("42|<config>")`; statistics seed 42 |

The judge prompts are experiment 39's frozen rubric bytes; a judge is not a solver, so the solver completion reminder is not added (adding it would change the configurations this experiment is meant to share with experiment 39).

## Scale verification (no further normalization)

Scores are normalized to [0, 1] at parse time (H0/H1/H2/R4: 0–5 ÷ 5; D0: 0–10 ÷ 10; legacy prompts already in [0, 1]); controls are in [0, 1] by construction. Nothing downstream divides again. Experiment 39's criterion is a Spearman correlation in [−1, 1] and is used as is.

## Verified data layout

- `results/semantic_probe_manifest.json` → `rows[]`: `probe_id` (`<kind>__<task>__L<level>`), `kind`, `family`, `task`, `level`, `path`, `sha256`, `source_sha256`, `valid`, `reason`, `reverse` (proved / unproved / not_applicable), `checks[]` (kind forward / reverse / unsat / same_declarations, theorem, status, axioms), `extra` (axiomatized definitions, closure, added hypotheses), `proposer`.
- `results/cells/<config>.json` → `cells[]`: `cell` = `<kind>__<task>__L<level>__r<repeat>`, `status` (render / deterministic / unmeasured_extraction), `prompt_sha256`.
- `results/harvest/<config>.json` → `cells[]` with `status` (measured / deterministic / parse_error / model_error / incomplete / unmeasured_infra / unmeasured_extraction), `score`, `score_raw`, `cost_usd`; `charges_usd`, `run_ids`, `selector`.
- Experiment 39 (read from its committed files at a named git ref, never from its checkout or `private/`): `results/units_train_val.json` → `units[]` with `config`, `split`, `kind`, `criteria.heldout.spearman`, `indices`; `results/SELECTION.json` → `selected`; `results/TEST_RECEIPT.json` (existence unlocks the post hoc test view).

## Pre-conditions for run

- Clone `/lfs/skampere1/0/brando9/cert-judge_e42` (branch `e42-semantic-probes`), VeriBench `/lfs/skampere1/0/brando9/veribench_e42` (read-only).
- `/lfs/skampere1/0/brando9/vb103_venv/bin/python` (PyYAML), `valk`, cloudflared, `~/.config/valkyrie/valkyrie.yaml` (copied mode 600 to `private/valkyrie.yaml`, never printed), ports 9460–9468 free.
- `$PY -m pytest scripts/test_e42.py -q` passes; `results/agent_bundle_check.json` and `results/agent_harness.json` PASS; `results/packs.json` PASS.
- **Wait gate:** experiment 39's committed `results.md` (on `origin/e39-proxy-index-search` or `main`) reports measured smoke verdicts through both of its transports (single-call `vb103_judge` and the Terminus2 agent). Satisfied at `origin/e39-proxy-index-search` 9823689 ("all 56 smoke cells are measured on the first re-attempt for Gemini 3.1 Pro …, Qwen3.6-27B … and the Terminus2 agent judges on GPT-6 Luna … and Claude Sonnet 5"; its train main runs admitted). `private/GATE_OPEN` is written only after this file is committed.

## Estimated wall-clock

Probe build: about 5 minutes at 12 jobs. Rendering and packs: minutes. Judging: 32,592 calls over nine served benchmarks at concurrency 20 per run, several runs in flight: single-call runs about 1–2 h each (Opus longer), agent-judge runs a few hours; about half a day to a day end to end with the recovery pass. Analysis: minutes. The index analysis waits for experiment 39's `results/units_train_val.json`.

## Pass/fail / abort rules

- **Smoke gate (per configuration):** its spare smoke cell (the first identity cell) returns a parsable verdict before its main pack is admitted. A configuration whose smoke fails on the recorded selector and on experiment 39's remaining pre-registered options is `NOT_RUN_ROUTE`; its cells stay in the denominator as missing.
- **Bundle / harness / pack gates:** PASS receipts required before any admission of the respective flavor.
- **STOP rules:** a delivered or served prompt hash differs from the frozen hash (that cell is `unmeasured_infra`; more than 1% of a run → hold admissions with `private/HOLD_JUDGE_ADMISSIONS` and report). HTTP 429 and other transport failures are infrastructure failures: the cell stays without a verdict until the single `recovery_1` pass; no retry loops. Charges never stop the run.
- **Completion:** every rendered cell of every configuration has a verdict or a labelled failure; one-to-one reconciliation of pack task ids against harvested cells; missing cells stay missing in the denominators; the probe score rule above decides which probes are scored.

## Identity / contact crib (verified)

- GitHub: `brando90` (repository `brando90/cert-judge`; `GH_TOKEN` from `~/keys/.brando90_github_token.txt`).
- Notification email: `brando.science@gmail.com`, no CC, via `uutils.emailing.send_email_smtp()` with `~/keys/gmail_app_password.txt`.
- Valkyrie configuration `~/.config/valkyrie/valkyrie.yaml` (never printed or committed); Vals-funded gateway; no personal provider keys.

## Amendments

- **Amendment 1 (09-30-2026, after the 56 smoke cells and before any main-run verdict was harvested; secondary metric only, the pass rule is unchanged).** Running the analysis on the four deterministic controls (zero calls) showed that the edit-distance control passes the locked screen (directional accuracy 1.00 on vacuity, weakening and over-constraint; formatting gap 0.044 ≤ 0.05): any change detector lowers its score for every edit, and formatting edits are small. So the screen is necessary but not sufficient evidence of semantic sensitivity. Added per configuration: the **formatting false-alarm rate** (share of formatting probes scored strictly below the identity score, task-clustered bootstrap interval) and **discrimination** = mean of the three semantic directional accuracies − false-alarm rate (a pure change detector scores about 0). Both are reported beside the locked verdict and do not change it.
