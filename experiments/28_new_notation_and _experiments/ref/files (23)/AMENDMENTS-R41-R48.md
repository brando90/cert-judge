# AMENDMENTS R41–R48 — folding in the repo-grounded review (20 Aug 2026)

**Status.** Ratified. Part of the specification. Authority: R41–R48 supersede earlier rulings
and prompt text wherever they conflict (specifically amending R25/R26/R33/R35/R37 and the
bridge/port prompts as stated). Source: an external repository-grounded review; each finding
was independently adjudicated. Everything not amended here stands.

## R41 — α-probe validity gate (amends R25/R37; adopts the review's finding 1)

The repository's current `variant_generator.py` α transform is reported invalid: string-level
regex renaming of signature identifiers only (bound occurrences in the proof body untouched),
a `:=:=` emission defect, a comment-append fallback that is a no-op, and `compiled=None`
throughout. Therefore:

1. **No α inference may be funded until probe validity is established.** For every proposed
   probe, a manifest row `(original, transformed, changed?, compiles?, error)` is required;
   every transformed artifact must compile/elaborate under the same toolchain as its
   original; the transform must rename each binder together with **all** bound occurrences;
   no-op and failed rows are excluded before any scoring and their counts reported.
   Implementation via Lean syntax/elaboration is preferred over regex; if regex is retained,
   the compile gate is the arbiter.
2. **Interim ruling: `ALPHA_RUN: declined (probe invalid)`** — recorded before any bridge
   number, so the pre-declared PTI_{eq,bm,ms} headline applies unless a validated probe set
   and a fresh funding decision both exist before Phase 3.
3. **Audit-trail flag for the paper:** the workshop-era ALPHA self-pair result (mean 0.399,
   the standing "failure mode") may be partially an artifact of this invalid transform
   (malformed Lean scored against originals). Phase 0 must determine which generator version
   produced those cached variants; the manuscript's ALPHA discussion is conditioned on that
   determination and must not present the 0.399 finding as a clean judge failure if the
   probes were malformed.
4. The same validity manifest (diff-nonempty, compiles, real cumulative degradation) is
   required for **bug and spec ladders** before properties are computed — see R47.4.

## R42 — Complete 75-item label repair (amends R35's mechanism; keeps its goal)

Option B's rename alone leaves the primary averaged view wrong (audit: avg TSV matches
(strict+lenient)/2 on only 73/75; stale unsafeMultiply avg rows carry 5.0 where the mean of
(4,5) is 4.5; the runner reads the precomputed avg TSV). Binding repair, in order:
(1) canonicalize the stale keys in the **strict and lenient** views; (2) collapse lenient
duplicates under the frozen mean-of-duplicates rule; (3) **regenerate the average view from
the repaired strict and lenient frames** — never text-edit the avg TSV; (4) verify
avg = (strict+lenient)/2 numerically on 75/75 pairs; (5) recompute all human-label
diagnostics (inter-round Spearman/QWK, MAE/MSE, dispersion figure) from the repaired frames
and record every changed value with before/after. The experiment runner is pointed at the
regenerated view.

## R43 — Repository-state facts (confirms R39; adds two fixes)

- The active manuscript **exists** at `paper_latex/ICLR_2027_submission/main.tex`: revise in
  place per R39; never re-port from `TMLR_2026_resubmission/`.
- **Branch renames** (remote `iclr2027-port` already exists): use `pti-v0-run`,
  `pti-v0-bridge-figure`, `iclr2027-pti-v0-refresh`. These names supersede every branch name
  in the prompts and masters.
- **SYNC.md does not exist in-repo:** Task 0 creates it, headed by a note that revision
  entries R1–R22 predate the in-repo log (they live in session records); the in-repo log
  begins at R23. This is not a blocker once so ruled.

## R44 — Linear branch stack and PR sequencing (amends the masters' git plan)

```
main └── pti-v0-run └── pti-v0-bridge-figure └── iclr2027-pti-v0-refresh
PR bases: pti-v0-run → main; pti-v0-bridge-figure → pti-v0-run;
          iclr2027-pti-v0-refresh → pti-v0-bridge-figure
```

Open **one draft PR at a time**, in that order; the figure and manuscript branches are
created only after the upstream PR's content is reviewed (see R48 phases). The manuscript
branch thereby contains the figure by descent, not by copying.

## R45 — Bridge-figure corrections (amends the bridge prompt)

Remove the y = x diagonal and the mean|PTI − TI| level-gap statistic: PTI is a [0,1]
conformance aggregate and TI_m1 is a Spearman in [−1,1]; they share no units, calibration, or
identity relation, so level comparison is meaningless on these axes. (The diagonal was a
carryover from the memo's Figure-1 spec, written when the y-axis was TI_2'; R23's axis change
invalidated its rationale.) Retain: Spearman + Kendall τ_b with CIs, primaries-only vs
pooled, family/role encodings, anchors, error bars, NOT-COMPUTABLE gutter. An OLS line may
remain only as a clearly labeled visual guide; with ~8 primaries, prefer the raw scatter and
rank statistics to carry the result. The item-level diagnostic figure is unaffected.

## R46 — Abstract and prose corrections (amends the ratified abstract skeleton)

1. Replace "— each combining a validity term with a repeat-stability term, aggregated by a
   two-level geometric mean." with: "— with the two degradation properties scored per item as
   validity × repeat-stability, all aggregated by a two-level geometric mean." (Only the
   ladder properties carry σ; eq and eqα are level/paired-difference factors by design.)
2. Replace "The properties are necessary conditions, not sufficient ones:" with: "The
   properties are a priori behavioral constraints — candidate necessary conditions under
   stated metamorphic-validity assumptions —" keeping the rest of the sentence. The full
   Route A / Route B treatment stays in-body (memo §2.1).
3. In `pti-methods-section.tex`, soften "four behaviours that any trustworthy evaluator of
   formal artifacts must exhibit" to "four behaviours we posit as a priori requirements for a
   trustworthy evaluator of formal artifacts, in the sense made precise in
   Section~\ref{sec:bridge}". Applied by the manuscript phase, logged in CHANGES.md.
4. Remove the optional decision-utility sentence from the abstract entirely (see R47.3).

## R47 — Statistical and protocol pinning (closes the review's finding 7)

1. **Bootstrap:** percentile intervals (BCa and basic are fragile at n = 8 with ties);
   resamples with fewer than 3 distinct judges (bridge) or undefined/constant correlations
   are recorded as invalid, excluded, and **counted**; report n_valid alongside every CI;
   flag any CI with < 95% valid replicates. Same policy for item-cluster bootstraps.
2. **SESOI simulation DGP:** Gaussian-copula rank coupling calibrated to the target Spearman
   as primary; independent rank-permutation mixing as a labeled sensitivity; seeds fixed;
   both curves reported.
3. **Screen thresholds τ_k:** not invented now. Selecting τ_k from the same validation data
   would re-open the circularity; the submission therefore claims the **surrogate/ranking**
   relationship plus reported property profiles, and specifies the operational PASS/FAIL
   screen (per-property UCB vs pre-registered τ_k on held-out judges) as pre-registered
   future work. All "human validations avoided at tolerance α" claims are removed or
   conditioned accordingly. θ = 0.20 (R26) is a computability rule, not a pass threshold —
   the paper says so.
4. **Panel cleaning (amends R26.1):** items are removed from D_T only for **objective
   construction defects** — byte-identical adjacent rungs, non-compiling variants, no actual
   cumulative degradation — established by a judge-free audit (the R41 manifest machinery).
   Unanimous judge-insensitivity is reported as a diagnostic but does **not** remove items
   (a hard probe every current judge saturates on is information, and removal would inflate
   conformance for future screened judges). Note: under per-judge exclusion, this change
   alters no current judge's score; it protects the amortization use-case. θ and
   NOT-COMPUTABLE semantics unchanged.

## R48 — Phased execution (supersedes R33's auto-continue and both masters' task ordering)

- **Phase 0 — no-spend preflight** (`PREFLIGHT-PROMPT.md`): one report, then stop. No API
  calls, no bridge numbers, no paper edits, no PRs.
- **Phase 1 — metric from cache** on `pti-v0-run`: spec commits (incl. SYNC.md creation per
  R43), R42 label repair, conformance gate, manifests, cached properties, Step-3
  property-table + gates commit, α validity manifest + split cost sheet. One draft PR. **Stop
  for human scientific review** — mechanical gates passing does not authorize continuing.
- **Phase 2 — α decision:** fund only if R41's validity conditions hold and the α-only cost
  (missing transformed-vs-gold calls only; rename/reorder/style diagnostics priced
  separately, R48.1: split approvals) is approved; else the declined record stands.
- **Phase 3 — the single bridge computation** + SESOI, after freezing roles, repair,
  bootstrap policy, and DGP; primaries-only and pooled reported separately.
- **Phase 4 — figure (R45) then manuscript** (R39/R43/R46; no literal `\todo{}` survives
  into anything submitted — unresolved placeholders become coherent number-free prose or the
  claim is cut).
- Commit-ordering discipline from R33 (property table strictly before any bridge; git
  history as pre-registration evidence) survives; the auto-continue does not.

---

```
TL;DR (for the human reader; the agent should ignore this block):
This folds the repo-grounded review into binding rulings: α funding is declined until
the transform provably compiles and renames binders with their occurrences (and the
workshop ALPHA-0.399 result gets audited for contamination by the same bug); the 75-item
fix now regenerates the average labels from repaired strict/lenient instead of trusting
the checked-in TSV; branches become a true linear stack with new non-colliding names and
SYNC.md is created rather than assumed; the bridge figure drops the meaningless y=x and
level-gap; the abstract's two overclaims are corrected verbatim; bootstrap type, SESOI
DGP, and the τ_k question are pinned (screen claim demoted to pre-registered future
work); panel cleaning switches to objective construction defects only; and execution
becomes preflight → cached metric → human review → α decision → bridge → figure → paper
instead of one unattended run.
```
