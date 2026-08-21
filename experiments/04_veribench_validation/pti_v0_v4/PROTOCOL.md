# Folder 04 — PTI-v0 v4 PROTOCOL (LOCKED before any expensive run)

**TLDR:** This protocol freezes PTI-v0 before any LLM-budget-spending run. It asks whether the label-free proxy ranks judge configurations like the paired human criterion, while treating structural failures, score missingness, and behavioral failures as distinct outcomes.

This file freezes the protocol before any LLM-budget-spending run begins. It is written prior to seeing PTI-v0 judge results. Any execution deviation belongs in the result report, not in this locked protocol.

Independent-QA amendment (2026-08-21, still before any paid run or bridge statistic): historical criterion error fallbacks are now explicit missingness under 100% coverage; the Lean environment is bound to its resolved manifest/module inventory; and the SESOI simulation includes the complete frozen decision-rule power. These fail-closed corrections were made without observing a primary PTI or bridge result.

## Scientific question (locked)

Does `PTI_v0`, computed without human labels from four pre-specified behavioral diagnostics, rank judge configurations similarly to the paired human-grounded `TI_m1` criterion?

The primary bridge analysis is Spearman rank association across primary judge configurations. A positive, decision-relevant outcome requires a point estimate of at least the frozen SESOI `rho=0.5` and a 95% bootstrap interval excluding zero. Other outcomes are labeled negative, below-SESOI, or inconclusive by the pre-frozen decision rule; none establishes that a judge is trustworthy.

## Locked metrics and parameters

- Metric version: `PTI_v0`.
- Typed artifact: `f=(item_id,agent_id,generation_id)`; repeats use `r`; ladder levels use `ell`.
- Properties: `P_eq`, `P_bm`, `P_ms`, and alpha-only `P_eqalpha`.
- Judge repeats: three; local aggregation: median.
- Ladder direction: larger `ell` means greater degradation; `C=(1-rho)/2`.
- Stability: mean over levels of `2*sd(ddof=0)`; with one repeat, the ladder factor equals `C`.
- Structural-invalid probes are excluded independently of scores. Structurally valid constant score ladders remain included with `C=0`.
- Property and PTI aggregation: exact-zero-first geometric means in log space, with no headline epsilon floor.
- Required score coverage: 100% of each judge/property’s frozen structural set.
- Human panel: evidence-supported 72-row intersection; primary view is the arithmetic mean of duplicate-collapsed strict and lenient passes.
- Bootstrap: 10,000 percentile replicates, seed 0; base artifact is the property/PTI unit and judge configuration is the bridge unit.
- Primary bridge: primaries-only Spearman. Kendall tau-b, pooled controls, family leave-one-out, three-property, and per-property analyses are pre-labeled robustness or exploratory analyses.
- SESOI: bridge Spearman `rho=0.5`.
- No per-property deployment thresholds are frozen; no `PASS-SCREEN` or human-validations-saved claim is permitted.

The machine-readable authority is `frozen_config.json`. The numerical authority is `tests/data/PTI_V0_TEST_VECTORS_v4.json` plus `py_src/cert_judge/pti_v0.py`.

## Scale verification (no further normalization)

All judge scores and PTI factors are already normalized to `[0,1]`. Raw human panel scores remain on `[0,5]` because rank correlation is scale-invariant. `TI_m1` is a Spearman coefficient in `[-1,1]`; `PTI_v0` is in `[0,1]`. The outer bridge therefore has no identity line and no PTI-versus-TI level error.

## Verified data schema

- Base candidates: `data/generated_agents/<item>__agent<id>.lean`.
- Gold precedence: the legacy VeriBench root first, then the newest root only when absent from the legacy root.
- Pool manifest: `base_pool_manifest.json`, including candidate/gold hashes, missing nominal rows, and duplicate-content groups.
- Structural manifest: `../results_pti_v0_v4/probe_validity_manifest.json`, created only after pinned Lean 4.22 elaboration.
- Score requests: `../results_pti_v0_v4/score_requests.json`; every cell binds metric/schema, judge, prompt provenance, content hashes, and repeat count through the full request-manifest fingerprint. Non-self references use the final theorem/lemma block selected by the frozen Exp16 regex, with full-gold fallback; each request retains both the full gold-source hash and actual reference hash.
- Accepted scores: `PTI_v0_scores_v1`, formally described by `score_schema.json` and runtime-validated for exact repeat cardinality, uniqueness, finiteness, range, and manifest binding.
- Human criterion source: `../results_exp16_final_robust/detail_rows.csv`, joined one-to-one to the frozen panel and aggregated by the median of exactly three judge repeats. Every LLM row must match its exact historical cache key and a non-fallback entry; deterministic controls are recomputed from source. The legacy entry retains only first-repeat reasoning, so the non-fallback classification is limited to that reasoning plus exact three-score agreement. Coverage is 100%, so an error fallback is missingness and makes that judge's criterion `NOT_COMPUTABLE`.

## Pre-conditions for run

- Work from the `codex/pti-v0-final` feature branch; do not push to or merge `main`.
- Resolve or explicitly stack dependency review in order: `brando90/ultimate-utils#44`, then `brando90/cert-judge#38`.
- Use the checked Lean project with `leanprover/lean4:v4.22.0` and a resolved Lake dependency tree. The audit compiles the local `VeriBench`, `VeriBench.Common`, and `VeriBench.Prelude` support modules first, classifies unresolved imports separately, and fingerprints the host platform, measured filesystem case behavior, Lake manifest, and available olean-module inventory. Lowercase on-disk `veribench` modules and uppercase `VeriBench` imports make the observed structural set platform-dependent; regeneration on a case-sensitive filesystem may validly diverge and must not reuse this manifest.
- Pass the numerical vectors, randomized tie-heavy cross-checks, Lean transformation tests, and package build.
- Produce an admissible-cache inventory and an exact alpha-only quote.
- Obtain explicit human approval for the exact LLM call count and cost before any credential-capable scorer is used. The canonical CLI cannot load credentials or perform inference.

## Estimated wall-clock

- Config, pool, panel, cache, and quote regeneration: under two minutes on the audited Mac.
- Full original/transformed Lean audit: approximately 20–45 CPU minutes with eight workers; no GPU.
- Deterministic local controls, criterion, SESOI, and gated status outputs: under five minutes.
- LLM judge scoring: not estimated here; the exact call/token/cost quote is a required precondition and the execution mechanism is intentionally absent.
- Bridge and figure generation after admissible scores and a pre-bridge commit: under five minutes.

## Pass/fail and abort rules

- Abort a probe globally on missing/no-op/duplicate content, an incorrect declared syntactic relation, malformed source, or failed required elaboration. Compile-valid cumulative fault injection is a Route-B assumption rather than proof of semantic worsening. Never consult judge score constancy for structural validity.
- Abort property computation for a judge when any required score cell is absent, incomplete, duplicated, non-finite, or outside `[0,1]`; emit `NOT_COMPUTABLE/DEFER`, not zero.
- A constant valid ladder is a behavioral zero and remains in the geometric mean.
- Abort all paid inference if the quote, model list, repeats, prompts, or request fingerprint changes after approval.
- Forbid the bridge when more than half of primary judges are `NOT_COMPUTABLE` for any property.
- Before any computed bridge, commit the byte-identical property file and supply that commit’s full SHA. Never compute a bridge from an uncommitted or subsequently modified property table.
- Do not edit the active manuscript or generate a result figure until committed machine-readable bridge evidence exists.

## Identity and contact crib (verified)

- GitHub owner/login: `brando90`, verified with the authenticated GitHub CLI on 2026-08-21.
- Local Git author: Brando Miranda (`brandojazz@gmail.com`), verified from repository Git configuration.
- LLM credentials: not applicable to this CLI and must not be loaded. Independent QA uses the locally authenticated `clauded` subscription CLI.

## Result boundary

The four-property headline is named `PTI_v0` only when all four properties are computed. If alpha is unavailable but the other properties are complete, the only permitted fallback is `PTI_eq_bm_ms`. Legacy JTI/TIvar values are never reused as either result.

Metric and transformer source hashes remain inside the config fingerprint as strict integrity gates. Any byte change to those files requires a deterministic re-freeze and downstream regeneration. The raw pipeline source hash is retained as provenance but excluded from the semantic config fingerprint; a semantic pipeline change requires a `PIPELINE_VERSION` bump.
