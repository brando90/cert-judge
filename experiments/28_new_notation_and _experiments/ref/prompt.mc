# CertJudge — master execution prompt v3 (paste this into Claude Code)

ref: /Users/brandomiranda/cert-judge/experiments/28_new_notation_and _experiments/files (22).zip (all the info from the ai bot to finish this task, you likely need to unzip it)
ref: /Users/brandomiranda/cert-judge/experiments/28_new_notation_and _experiments/prompt.mc 

You are Claude Code working in `github.com/brando90/cert-judge`, executing the ICLR 2027
revision of *Certifying the Judge* end-to-end: commit the ratified specification, implement
PTI-v0 against the numerical oracle, run the experiments, build the bridge figure, and revise
the active manuscript. The design phase is complete; two independently produced finalization
packages have been merged and every conflict between them is adjudicated. Your job is
execution with **zero design decisions**. Supersedes master prompt v2.

## Required inputs

**Package A (protocol & execution):**
`certjudge-memo-addendum-R23-R35.md` · `RECONCILIATION-R36-R40.md` ·
`certjudge-revision-memo.md` · `pti-methods-section.tex` ·
`agent-prompt-pti-v0-run-v2.md` · `agent-prompt-bridge-plot-v2.md` ·
`agent-prompt-iclr2027-port-v2.md`

**Package B (numerics & manuscript migration):**
`PTI_V0_CANONICAL_SPEC.md` · `MANUSCRIPT_REVISION_MAP.md` ·
`CODEX_AGENT_PROMPT_CERT_JUDGE.md` · `PTI_V0_TEST_VECTORS_v2.json` (patched; supersedes
`PTI_V0_TEST_VECTORS.json`) · `test_pti_v0_reference_final.py` · `README_FOR_CODING_AGENT.md`
· `REFERENCE_TEST_OUTPUT.txt` · plus, **if provided**: `pti_v0_reference_final.py`,
`DECISION_LOG.md`, `PTI_V0_IMPLEMENTATION_MEMO.md`, `SOURCE_PROVENANCE.md`,
`PTI_V0_PAPER_READY_NARRATIVE.tex`, `PTI_V0_PAPER_READY_METHOD.tex`,
`PTI_V0_NUMERICAL_STABILITY_APPENDIX.tex`.

Missing-file handling: if `pti_v0_reference_final.py` is absent, implement the oracle from
`PTI_V0_CANONICAL_SPEC.md` + the patched vectors (the tests define compliance). If
`DECISION_LOG.md` is absent, note it in `STATUS.md` and treat any question it would answer as
governed by the merged authority order below; if that fails to settle something, `BLOCKED.md`.

## Authority order (from RECONCILIATION R38)

1. Addendum R23–R35 + Reconciliation R36–R40
2. `certjudge-revision-memo.md`
3. `PTI_V0_CANONICAL_SPEC.md` + `DECISION_LOG.md` (binding numerics/notation where not
   superseded — the enumerated supersessions are: constant ladders → R36 exclusion machinery;
   absolute no-spend → R37 single α gate; B's source-of-truth inversion; "necessary
   condition" blanket ban not adopted; P_eq scope per R31; commit policy per this prompt)
4. Task prompts, then code comments

Any unenumerated conflict: stop that thread, write `BLOCKED.md` (what is wrong, what it
affects, what you propose, what evidence settles it), continue everything independent of it.

## Standing rules

1. **Hard Rule 9 / R37.** Exactly one paid-inference gate exists in this pipeline: the α
   paired-difference (variant-vs-gold) run. Surface script + call count + cost and wait for
   approval; record `ALPHA_RUN: funded | declined` in `RESULTS.md` **before any bridge number
   exists**; declined ⇒ pre-declared labeled headline PTI_{eq,bm,ms}. Any other spend that
   seems necessary is a stop-and-ask, never an inferred approval. No secrets printed.
2. **No fabricated results.** Missing numbers are `TBD`, `NOT RECOMPUTED`, or
   `LEGACY TIvar RESULT — NOT PTI-v0`. TI_var-era numbers never appear as PTI-v0 results
   (R34). Every number is DOCUMENTED (path) / DERIVED (command) / UNKNOWN.
3. **Freeze.** PTI-v0 changes for no reason after any bridge number exists; properties are
   never reselected or reweighted on results.
4. **Git.** Stacked branches: `pti-v0` off `main`; `bridge-plot` and `iclr2027-port` off the
   head of `pti-v0`. One PR per branch. No merges, no pushes to `main`, no OpenReview
   submission. Legacy outputs are never overwritten; new outputs carry
   `metric_version = "PTI_v0"`.
5. **Determinism.** Seeds fixed (0); 10,000 bootstrap iterations; iteration sorted by item
   id; log-domain zero-first GMs; endpoint snapping and unit-interval validation per the
   canonical spec.

## Execution order

**Task 0 — Spec commit (on `pti-v0`).** Create the branch. Commit to `docs/spec/`: the
addendum, the reconciliation, `PTI_V0_CANONICAL_SPEC.md` (annotated at §4.2 and the two
superseded checklist lines per R36 — annotate, don't delete), `PTI_V0_TEST_VECTORS_v2.json`,
and the amended test file. Append SYNC.md entries R23–R40 (append-only; if the latest entry
is not R22, renumber from the actual latest — content unchanged). Verify
`docs/certjudge-revision-memo.md` and `pti-methods-section.tex` exist in-repo; commit the
provided copies if not.

**Task A — PTI-v0 implementation + run** per `agent-prompt-pti-v0-run-v2.md` **as amended by
R40**. Internal order: (a) package B's read-only git/rg repository audit → record canonical
schema, cached tensors, legacy metric, figure/table generators, manuscript build command in
`CACHE_INVENTORY.md`; (b) audit scripts + Option B rename (R35) → panel = 75 = 25×3 confirmed;
(c) judge manifest frozen; (d) **conformance gate**: adapt the oracle into the canonical
pipeline (integrate, don't fork) and pass the full patched vector suite + amended unit tests
at 1e-12 **before any real property is computed**; (e) the α spend gate (the one pause) —
everything up to the Step-3 commit proceeds while awaiting the answer; (f) probes, panel
cleaning, properties with all mandated diagnostics and sensitivity columns; (g) **Step-3
commit** (property table + GATES.md) strictly before (h) the bridge (PTI-v0 vs TI_m1, avg
primary, primaries-only lead + pooled, cluster/judge bootstraps per R40.3, τ_b, per-property
exploratory, secondary 13-judge panel if cached); (i) SESOI simulation; (j) PR.

**Task B — Bridge figure** per `agent-prompt-bridge-plot-v2.md`, branching from `pti-v0`'s
head after Task A's CSVs exist; anchored to the existing
`experiments/27_ti_plot_like_scatter_plots` (its item-level figures are revised in place; the
new outer bridge figure follows the repo's experiment convention, never an orphan module); synthetic generator + explicit statement if Task A is
HARD-blocked.

**Task C — Manuscript** per `agent-prompt-iclr2027-port-v2.md` **as amended by R39**: first
detect whether `paper_latex/ICLR_2027_submission/main.tex` exists. If yes — revise it in
place, keep its title, skip the template/TMLR-copy step, and apply the union of the v2
prompt's content requirements and `MANUSCRIPT_REVISION_MAP.md` (its stale-term audit,
result-status table with `LEGACY TIvar RESULT — NOT PTI-v0` markers, and acceptance checklist
are mandatory deliverables). If no — follow the v2 prompt's Step 0, then apply the same
union. Either way: `pti-methods-section.tex` is the metric-section base (its exclusion
paragraph is the manuscript's degeneracy text; package B's "C = 0 by policy" sentence must
not appear), augmented with the σ̃, θ/NOT-COMPUTABLE, typed-index, endpoint-snapping, and
coverage-failure paragraphs; the numerical-stability appendix may start from
`PTI_V0_NUMERICAL_STABILITY_APPENDIX.tex` if provided, amended to exclusion semantics. The
ratified abstract skeleton fills only from `RESULTS.md`; the ≤ 9-page limit, anonymization
grep, AI-use and reciprocal-reviewing statements from the live CFP, criterion-drift and
one-rater disclosures, and the claim-by-claim abstract audit all remain mandatory. Build the
manuscript (latexmk or the repo's documented command) and record the result.

## Definition of done

Three open PRs plus `STATUS.md` on `iclr2027-port`: bridge headline (or its `TBD` state),
`ALPHA_RUN` record, conformance-test and manuscript-build results, HARD/SOFT gate outcomes,
page count, anonymization grep, result-status table summary, every remaining
`TBD`/`\todo{}`, every `BLOCKED.md` item, and the outstanding human actions (α approval if
still pending; PR review/merge; OpenReview submission — abstract Sep 18, paper Sep 25, 2026
AoE; reciprocal-reviewer registration).

---
END OF AGENT INSTRUCTIONS

```
TL;DR (for the human reader; the agent should ignore this block):
v3 merges both AI packages into one pipeline: ChatGPT Pro's numerics layer (oracle API,
1e-12 test vectors, typed indices, cluster bootstrap, repo audit, manuscript revision
map) runs inside my protocol layer (ratified rulings, Option B, gated bridge with
pre-registration commits, SESOI, ICLR compliance), with the three conflicts adjudicated
in RECONCILIATION-R36-R40: constant ladders are excluded rather than zeroed (their C=0
policy + no-floor GM would let one saturated probe item wipe out every judge's PTI),
their absolute no-spend rule gains the single α gate so P_eqα can actually be computed,
and the manuscript task auto-detects whether paper_latex/ICLR_2027_submission already
exists (as ChatGPT observed) and revises in place instead of re-porting. Still exactly
one approval on your desk: the α inference cost.
```