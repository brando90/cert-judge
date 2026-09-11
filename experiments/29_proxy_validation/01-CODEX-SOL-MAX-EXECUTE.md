# CertJudge PTI-v0 v4 — GPT-5.6 Sol `max` execution prompt

Work in `brando90/cert-judge`. Load the current global `agents-config` rules first. Read `PREFLIGHT_PTI_V0_V4.md` and every file in this handoff.

Proceed only if the preflight verdict is `READY`, or `READY AFTER FIXES` and every required fix is recorded as resolved. If a HARD blocker remains, write/update `BLOCKED.md`, complete independent no-risk work, and do not manufacture a workaround.

## Authority

1. `03-SPEC-OVERRIDES-R41-R49.md`.
2. The current repository's audited facts and merged revision memo.
3. `PTI_V0_CANONICAL_SPEC.md` and test vectors, except where overridden.
4. Task prompts and historical comments.

No post-result metric redesign is allowed.

## Git topology

Do not push to `main` and do not auto-merge.

- PR A branch: `codex/pti-v0-final` from updated `main` after dependency state is resolved.
- PR B branch: `codex/iclr2027-final` stacked on PR A.
- PR #38 remains the Exp27 dependency; do not duplicate it.

Before edits, record current branch/HEAD/dirty state. Stage only intended paths.

## Phase 1 — specification and guidance

On PR A:

1. Commit the v4 overrides and a concise PTI-v0 spec under `docs/spec/`.
2. Update stale project descriptions in `AGENTS.md` and `CLAUDE.md` while preserving valid environment and safety guidance.
3. Add a machine-readable metric version: `PTI_v0`.
4. Add the reference vectors/tests to the canonical test tree.

## Phase 2 — conformance implementation

Integrate PTI-v0 into the canonical scoring package; do not create a disconnected script if reusable scoring code already exists.

Implement and test:

- stable zero-first log geometric mean;
- tie-aware Spearman and endpoint snapping;
- local median over repeats;
- ladder `C=(1-rho)/2`;
- repeat instability using `2*sd(ddof=0)` averaged over levels;
- `K_aj=1 => factor=C`;
- equality and alpha paired-difference factors;
- property and PTI aggregation;
- structural-invalid exclusion versus behavioral constant `C=0`;
- missing/coverage `NOT_COMPUTABLE/DEFER`;
- long-form diagnostics.

Pass the complete numerical vector suite at `1e-12` before running real data. Cross-check against the supplied reference implementation and randomized tie-heavy cases.

## Phase 3 — evidence-backed panel repair

Apply the Option-B repair only if preflight verified it. Preserve raw source labels, create an audit manifest, generate canonical repaired derivatives, and rerun all label-lineage checks. Never edit a value merely to recover the count 75.

Freeze and commit the judge manifest, role labels, item panel, property definitions, aggregation, bootstrap, SESOI, and output schema **before any bridge statistic is computed**.

## Phase 4 — cached properties and alpha gate

Compute all zero-spend cached properties first.

For alpha:

- use only a preflight-validated Lean-safe transform;
- present the exact alpha-only command, missing call count, model list, repeats, and cost;
- require explicit recorded approval before loading a key;
- optional RENAME/REORDER/STYLE calls are a separate approval and never required for the headline.

If alpha is declined or blocked, run the pre-declared labeled three-property headline and mark four-property PTI-v0 `NOT RUN/NOT COMPUTABLE`; do not silently rename it.

## Phase 5 — PTI-v0 experiment

For every judge, output:

- `P_eq`, `P_bm`, `P_ms`, `P_eqalpha` or explicit status;
- PTI variant label and metric version;
- per-ladder median scores, rho, C, sigma, factor, ties, adjacent reversals, structural-validity flag, constant-score flag;
- coverage and parse failures;
- clustered CIs over `f=(i,a,q)`;
- primary/control and model-family roles.

Exact zeros remain zeros. Missing data are not zeros. All outputs are deterministic and saved under a new result directory; never overwrite legacy runs.

## Phase 6 — human criterion and outer bridge

For each judge, compute `TI_m1` from paired items using median judge repeats and the frozen human view; averaged labels are primary, strict/lenient secondary.

Then compute the outer judge-level bridge:

- primaries-only primary analysis;
- pooled analysis including controls, clearly secondary;
- Spearman primary, Kendall tau-b robustness;
- bootstrap CI over judges with valid-replicate count;
- model-family leave-one-family-out sensitivity when feasible;
- three-vs-four-property analysis pre-labeled, not selected by best result;
- exploratory per-property associations labeled exploratory.

No `y=x`, no PTI/TI level MAE, no causal interpretation, and no tuning after seeing results.

Run the frozen SESOI simulation and distinguish positive, negative, and inconclusive outcomes.

## Phase 7 — figures

Create the outer bridge figure inside the canonical experiment tree. Reuse Exp27/PR #38 for the inner item-level criterion diagnostic. Generate source-data CSV/JSON for every paper figure and record exact commands.

Run visual and statistical QA: tie handling, ranges, labels, legends, uncertainty, role encodings, and no misleading density/identity channels.

## Phase 8 — PR A QA

Follow the repository's independent QA rule. Use a fresh reviewer/model to recompute headline values from raw outputs and review the complete diff. Fix findings, rerun tests, compile relevant packages, scan for secrets, then commit/push and open a draft PR with a concise evidence-backed description.

## Phase 9 — manuscript on stacked PR B

Edit `paper_latex/ICLR_2027_submission/main.tex` in place. Do not port TMLR.

Apply `05-ICLR2027-FINALIZATION-CHECKLIST.md`. Populate PTI-v0 results only from committed machine-readable outputs. Keep legacy TIvar numbers explicitly historical or remove them. Preserve criterion-drift and registered-negative disclosures.

Build the paper, verify page limit and anonymity, run stale-term/TODO/reference/citation greps, render and inspect the PDF, and create a result-status table mapping every manuscript number to a file and command.

Run an independent paper QA before commit/push and open PR B as a draft stacked on PR A.

## Final status

Write `STATUS_PTI_V0_V4.md` containing:

- dependency SHAs;
- preflight verdict and resolved blockers;
- alpha approval/status and actual spend;
- conformance tests;
- panel counts;
- metric variants actually run;
- headline bridge with uncertainty or an honest `NOT COMPUTED`;
- all sensitivity analyses;
- PR URLs;
- manuscript build/page/anonymity status;
- remaining human decisions and submission actions.
