# Independent Fable 5 review — PTI-v0 v4 first pass

**TLDR:** A fresh read-only Claude Fable 5 maximum-effort review returned `REQUEST CHANGES`. It independently reproduced the numerical core, requests, controls, panel, costs, fingerprints, and zero-spend bridge gate, then found one high-severity criterion-lineage defect and two medium design/reproducibility gaps. This file records that first-pass verdict before the builder's repair and targeted rereview.

- Review date: 2026-08-21 (America/Los_Angeles)
- Baseline: `cbd31f2ca0dbd4fe68ef7fbf632dfce4d160ab47`
- Reviewer: Claude Fable 5, fresh non-persistent CLI session, effort `max`
- Mode: read-only; `Write`, `Edit`, and `NotebookEdit` disabled
- Verdict: **REQUEST CHANGES**

## Independently verified

- The branch preserves Exp27, does not touch `main`, and does not alter the active manuscript or legacy result trees.
- The no-API CLI has no provider client or credential loader. Quotes remain unapproved, primary properties and the bridge remain `NOT_COMPUTABLE`, and `bridge_statistic_computed=false`.
- PTI numerical vectors and adversarial randomized checks match SciPy/NumPy to floating-point precision: tie-aware Spearman and Kendall tau-b, exact-zero geometric means, local medians, `2*sd(ddof=0)`, `K=1 => factor=C`, coverage failure, and endpoint snapping.
- Local-control properties recompute from raw scores, including exact-zero behavior.
- All frozen hashes/fingerprints and quote arithmetic recompute. The request totals are 780 points per judge, 6,240 conceptual cells, 4,176 unique cells, and 9,396 paid calls at three repeats.
- All 780 request content pairs replay to their recorded hashes. Spot Lean recompiles passed for valid bug, missing-spec, and alpha artifacts; a recorded-invalid base failed as recorded.
- The 72-row panel and unsafeMultiply exclusion reproduce from source evidence.
- All original criterion numbers recompute from `detail_rows.csv`; this exposed the lineage defect below.

## Findings

### H1 — High: one historical criterion contains eight silent API-error fallbacks

`command_compute_criterion` accepted `repeat_scores` without joining them to their legacy cache provenance. Eight of 72 rows for `gpt-5.3-codex|P8_STRICT_B` were `[0.5,0.5,0.5]` values produced by an HTTP-401 fallback rather than judge output:

- `0_bisect_right`, agents 0–2;
- `0_unsafeCopy_safe`, agents 0–2;
- `13_MyUppercase`, agents 0–1.

The contaminated average-view value was `0.3652094534256896`; the 64 clean rows give approximately `0.404138`, but the frozen 100% criterion-coverage rule means the correct status is `NOT_COMPUTABLE`, not a 64-row replacement estimate. The reviewer required exact cache-key lineage, fallback exclusion, row-level audit counts, and a regression test.

### M1 — Medium: SESOI omitted power of the frozen decision rule

The simulation reported median-gate diagnostics but not the probability that the actual positive rule fires: point Spearman at least 0.5 and a 95% judge-bootstrap interval excluding zero. Two columns labeled `analytic` were not analytic for the implemented Gaussian-copula DGP. The reviewer required frozen-rule power, correctly named Gaussian reference quantities, and tests at null/near-perfect target correlations.

### M2 — Medium: structural reasons conflate unresolved imports with elaboration failures

The original manifest labeled all 384 base failures as candidate/gold elaboration failures. The reviewer found 126 unresolved-object/import failures and noted that local `VeriBench.Common`/`Prelude` modules had not been built. The manifest also did not fingerprint `lake-manifest.json` or the available olean inventory, and rejected ladder-candidate timeout classes were discarded. The reviewer required error classes, build-state provenance, explicit local-module preparation policy, and timeout tests.

### L1 — Low: cache rationale was inaccurate

Legacy keys do carry namespace, model, prompt hash, and content hashes in their extended form. Failing closed remains correct because the entries lack the PTI schema/scorer/decoding success contract and may be error fallbacks. The reviewer requested explicit counts for prompt/content/repeat matches and fallbacks.

### L2 — Low: Route-B prose overstates semantic validation

Compilation and a declared syntactic mutation do not prove semantic worsening. The reviewer required the docs to call these intended, compile-valid cumulative faults under an explicit Route-B metamorphic-validity assumption.

### L3 — Low: exact-constant discontinuity was undocumented

An exactly constant ladder receives `C=0`, while any representable nonzero difference is nonconstant. The reviewer requested an explicit no-tolerance statement and deterministic score parsing requirement.

### L4 — Low: package/status QA was incomplete

The wheel-package fix was correct, but the first-pass status still said final tests and packaging were pending. The reviewer requested an editable-environment import, wheel build/content check, and final recorded test count.

### L5 — Low: pipeline source hash over-invalidated score bindings

The config fingerprint included the pipeline file SHA, so a comment-only edit changed every downstream score binding. The reviewer requested a versioned semantic pipeline identity or documented re-freeze policy, with the raw source SHA retained only as integrity provenance.

## Required proof after repair

1. Real artifact reports eight fallback rows and 64/72 coverage for `gpt-5.3-codex|P8_STRICT_B`, with its criterion `NOT_COMPUTABLE`; the other seven judges report zero fallback rows and 72/72 coverage.
2. SESOI reports actual decision-rule power and correctly named Gaussian reference quantities.
3. The structural manifest classifies unresolved imports/timeouts, records prepared local modules, and binds the Lake manifest and sorted olean inventory.
4. Cache inventory distinguishes potential, prompt/content, repeat, and fallback matches while retaining zero admissible PTI calls.
5. Focused tests, Lean build, editable import, wheel contents, deterministic regeneration, and secret/diff checks pass.

The first-pass reviewer explicitly asked for a targeted rereview of the regenerated criterion and SESOI outputs after these corrections.
