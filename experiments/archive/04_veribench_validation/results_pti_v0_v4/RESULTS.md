# PTI-v0 v4 zero-spend results

**TLDR:** The frozen zero-spend run validated 470 typed candidate artifacts, computed both deterministic controls, and reconstructed the 72-pair human criterion. No admissible primary-judge scores exist, so primary `PTI_v0` and the judge-level bridge are honestly `NOT_COMPUTABLE`; actual provider/API spend was `$0`.

## Run boundary

- Date: 2026-08-21 (America/Los_Angeles).
- Metric: `PTI_v0`.
- Mode: deterministic local work only; no credentials, inference client, or provider request.
- Candidate pool: 470 observed artifacts from 157 items; nominal grid 471; one missing artifact, `24_matrix_multiply|agent1|q0`.
- Human panel: 72 evidence-supported aligned pairs. Three stale unsafeMultiply rows remain excluded because their historical gold is the vulnerable artifact, not the intended safe gold.
- Frozen judges: five primaries and three controls; the two non-LLM controls were materialized locally.

## Structural validity

Validity was decided from construction, byte identity, and pinned Lean 4.22 elaboration, without consulting judge scores.

| Property | Structurally valid | Invalid | Contract |
|---|---:|---:|---|
| `P_eq` | 86 | 384 | Candidate and full gold elaborate; candidate is scored against itself. |
| `P_bm` | 49 | 421 | Original plus four distinct cumulative compile-valid fault mutations. |
| `P_ms` | 63 | 407 | Original plus four distinct cumulative compile-valid specification removals. |
| `P_eqalpha` | 67 | 403 | Conservative non-no-op binder rename and transformed artifact elaborate. |

All 470 selected gold artifacts elaborate. Only 86/470 generated candidates elaborate in the pinned project, accounting for the shared 384 base failures: 118 unresolved imports, 135 parse failures, 59 type/elaboration failures, 21 termination failures, and 51 other elaboration failures. The audit first compiles `VeriBench`, `VeriBench.Common`, and `VeriBench.Prelude`, then binds the host platform, measured filesystem case behavior, resolved Lake manifest, and 7,075-module olean inventory. This measured macOS run is case-insensitive: lowercase on-disk `veribench` modules coexist with uppercase `VeriBench` imports, so a case-sensitive Linux regeneration may produce a different structural set and must not reuse this manifest. Four rejected bug-mutation attempts timed out; none was accepted or hidden.

The valid structural set contains 196 cumulative bug-mutation steps and 252 cumulative missing-spec steps (157 theorem, 56 example, 34 `#eval`, and five spec-named `def` removals). These are intended, compile-valid cumulative faults under Route B; compilation does not prove semantic worsening. The exact row-level evidence and sanitized compiler diagnostics are in `probe_validity_manifest.json`.

## Request and cache inventory

- 780 conceptual probe points per judge: 86 equality, 245 bug-ladder, 315 missing-spec-ladder, and 134 alpha-pair points.
- 6,240 conceptual judge/probe cells across eight frozen judges.
- 4,176 content-deduplicated score cells; 3,132 are paid-judge cells, or 9,396 calls at three repeats.
- Legacy cache: 27,102 entries, including 148 potential model/content matches, 94 exact prompt/content/model matches, 80 that also contain three scores, and two matching error fallbacks. Zero calls are admissible because the entries lack the PTI schema and versioned scorer/decoding success contract.

## Local-control properties

The controls are diagnostic only and do not substitute for primary judges.

| Judge | `P_eq` | `P_bm` | `P_ms` | `P_eqalpha` | `PTI_eq_bm_ms` | `PTI_v0` |
|---|---:|---:|---:|---:|---:|---:|
| `editdist_e1` | 1.000000000000 | 0 | 0 | 0.999217767534 | 0 | 0 |
| `random_r1` | 0.424064239771 | 0 | 0 | 1.000000000000 | 0 | 0 |

Each displayed control property has 100% coverage of its corresponding structural set. Exact-zero geometric-mean semantics are preserved. For `editdist_e1`, all 49 valid bug ladders are constant-score behavioral failures; for `random_r1`, 46/49 bug ladders and 62/63 missing-spec ladders are constant-score failures.

## Human criterion

`TI_m1` is the paired Spearman correlation between the median of three historical judge repeats and the frozen average human view. LLM rows must match an exact non-fallback legacy-cache entry, while deterministic controls are recomputed from source. The legacy cache stores only the first repeat's reasoning, so “non-fallback” is verified on that stored reasoning plus exact three-score agreement; a later-repeat parse recovery is not independently visible. Seven judges pass at 72/72 coverage. Eight HTTP-401 fallback rows are excluded for `gpt-5.3-codex|P8_STRICT_B`, so its 64/72 coverage fails the frozen 100% rule and its criterion is `NOT_COMPUTABLE`. Intervals below are 10,000-replicate paired percentile-bootstrap intervals.

| Judge | Role | Coverage | `TI_m1` | Kendall tau-b | 95% CI for Spearman |
|---|---|---:|---:|---:|---|
| `editdist_e1` | control | 72/72 | 0.198674669969 | 0.148361254391 | [-0.079266953389, 0.456175404748] |
| `gpt-4o-mini\|P4_CHECKLIST` | primary | 72/72 | 0.091615386195 | 0.078856041498 | [-0.146925690075, 0.320159612198] |
| `gpt-4o-mini\|P8_STRICT_B` | primary | 72/72 | -0.014160512186 | -0.013920653937 | [-0.255756617928, 0.226709347833] |
| `gpt-5.3-codex\|BAD_STRINGY` | control | 72/72 | 0.434808914250 | 0.351337119535 | [0.206088737850, 0.631852057687] |
| `gpt-5.3-codex\|P1_BASELINE` | primary | 72/72 | 0.466422249291 | 0.388459428908 | [0.250846926623, 0.646195489315] |
| `gpt-5.3-codex\|P4_CHECKLIST` | primary | 72/72 | 0.419298135448 | 0.358521621430 | [0.195897459336, 0.601472509203] |
| `gpt-5.3-codex\|P8_STRICT_B` | primary | 64/72 | `NOT_COMPUTABLE` | N/A | N/A |
| `random_r1` | control | 72/72 | -0.000817659905 | -0.003118705047 | [-0.235112496732, 0.225373653928] |

These historical criterion values are not PTI values and are not a bridge result.

## Frozen SESOI simulation

The predeclared Gaussian-copula simulation uses the four primary judges with valid criterion lineage, seed 0, 10,000 draws per target correlation, and a 10,000-replicate judge bootstrap for each possible proxy order. At the frozen target Spearman `rho=0.5`, it produced:

- mean realized Spearman: 0.46708;
- empirical false-pass rate under the median diagnostic gate: 0.31635;
- empirical top-one benefit retention: 0.536750106084;
- probability that the point estimate reaches the SESOI: 0.5132;
- probability that the complete positive rule fires (`rho>=0.5` and CI low `>0`): **0.1492**.

This is a design simulation, not evidence about the uncomputed PTI bridge. It pre-registers that the available four-primary design is underpowered at its own SESOI. With four judges, the bootstrap interval excludes zero only for the perfect rank order, so `0.1492` is the simulated probability of that discrete event, not a smooth large-sample power curve.

## Spend quotes and actual spend

Quotes use the conservative frozen bound of one input token per UTF-8 byte plus 128 protocol tokens per request, at most 256 output tokens, and all input billed uncached.

| Scope | Missing calls | Conservative upper bound | Status |
|---|---:|---:|---|
| Alpha transformed side only | 918 | `$7.6127427` | Quoted; not approved or run |
| Uncached original plus alpha pair | 1,836 | `$15.2020962` | Quoted; not approved or run |
| Full frozen paid-judge request set | 9,396 | `$85.0848855` | Quoted; not approved or run |
| Optional RENAME/REORDER/STYLE | 0 quoted | N/A | Unvalidated transforms; not quotable |

Actual provider/API spend: **`$0`**.

## Gate result

- Primary `P_eq`, `P_bm`, `P_ms`, and `P_eqalpha`: `NOT_COMPUTABLE`, coverage 0%, because no admissible `PTI_v0_scores_v1` records exist.
- Primary `PTI_eq_bm_ms`: `NOT_COMPUTABLE`.
- Primary four-property `PTI_v0`: `NOT_COMPUTABLE`.
- Screen: `DEFER`.
- Outer bridge: `NOT_COMPUTABLE`; `bridge_statistic_computed=false`.
- Human criterion: seven judges computed; `gpt-5.3-codex|P8_STRICT_B` is `NOT_COMPUTABLE` after eight fallback rows were quarantined.
- Outer figure and active-manuscript result edits: not created, as required by the frozen hard gate.
- W&B Report: N/A for this blocked zero-spend preparation; no completed paid experiment exists.

## Reproduction

The command sequence is checked into `../pti_v0_v4/README.md`. Machine-readable authority resides in this directory and in the frozen configuration directory; no number in this report overrides those files.
