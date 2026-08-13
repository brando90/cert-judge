# AGENT PROMPT — Port the CertJudge TMLR draft to ICLR 2027 format and content

## Role and goal

You are working in the `cert-judge` repository (github.com/brando90/cert-judge). Your job is to
produce an ICLR 2027 submission draft by porting `TMLR_2026_resubmission/main.tex` into the
official ICLR 2027 template and implementing every content change specified in
`docs/certjudge-revision-memo.md` (the memo is the source of truth; if it conflicts with this
prompt, the memo wins; if it conflicts with repository facts, stop and report).

## Ground rules

1. Work on a new branch `iclr2027-port`. Never edit `TMLR_2026_resubmission/` in place — copy
   into a new `ICLR_2027_submission/` directory. Open a PR at the end; do not merge, do not
   push to `main`.
2. No API-key-loading runs of any kind without first surfacing the exact script and its cost
   and receiving explicit approval. LaTeX compilation, git, and pure-stdlib Python are free to
   run.
3. Any number you insert or change in the manuscript must be labeled in your change log as
   DOCUMENTED (traced to a repo artifact, cite the path), DERIVED (computed by you, show the
   command), or UNKNOWN (insert `\todo{}` and flag). Never guess a number.
4. Verify before you trust: re-run `experiments/26_human_label_dataset_audit/audit_human_labels.py`
   and `reconcile_paper_numbers.py` (pure stdlib) and confirm their outputs match the memo's §4
   table before propagating any data facts into the text. If they disagree with the memo,
   stop and report the discrepancy instead of choosing a side.

## Step 0 — Template setup

- Download the official style files:
  `https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip`. Unzip into
  `ICLR_2027_submission/`, and build the provided template once to confirm the toolchain
  compiles before touching content.
- Port `main.tex`, `refs.bib`, figures, and any input files from `TMLR_2026_resubmission/`
  into the ICLR template structure. Preserve the TMLR version untouched.

## Step 1 — Rename pass (memo §1 ledger)

Apply the rename ledger in one sweep across text, math macros, figure captions, axis labels,
table headers, and code identifiers referenced in the paper:

- `TI_var` / "trust index" / "cert index" → `\mathrm{PTI}_p` (define once; `p` is an index set,
  default bridge aggregate `PTI_{\{1,2,3\}}` with `P_4` reported standalone).
- Per-judge "human alignment"/"human Spearman"/`Align` → `\mathrm{TI}_{m_1}`.
- "certification protocol" → "amortized judge validation"; algorithm CERTIFY → SCREEN;
  "certificate extends" → "screen result extends". The repo slug `cert-judge` stays.
- pass1/pass2 → strict/lenient (note: the old names are inverted vs. chronology; sha evidence
  is in the audit README — never reintroduce temporal language).
- "reflexivity" in prose → "identity" (keep the formal statement unchanged).
- The words "Trust Index" must not appear in the title, abstract, or section headings.
- Figures whose embedded labels contain old names: do NOT silently regenerate. List them in
  `CHANGES.md` under "figures needing regeneration" with the generating script path.

## Step 2 — Claims surgery (memo §2)

- Rewrite the abstract to screen semantics: properties are a cheap screen whose acceptance is
  licensed only by a demonstrated bridge; no sentence may claim prediction that the results
  section does not report. Cross-check every abstract claim against the results by grep before
  finishing.
- Remove every instance of "sound rejection by construction" and equivalents. Insert the Route
  A / Route B treatment (memo §2.1) — Route B's lemma goes to the appendix with its one-line
  proof; the main text states the conditional-falsification sentence only.
- Correct GM language to soft-AND (memo §2.3); the hard screen is per-property UCB thresholds;
  the reported object is the property vector/profile.
- Replace any "half of trustworthiness is free" phrasing with the one-conjunct statement
  (memo §2.4) and make the headline bridge `PTI_{\{1,2,3\}}` vs `TI_{m_1}` — stability never on
  both sides.
- Cost claims use "de-indexed, not eliminated" phrasing and the C_amortized decomposition
  (memo §2.5).
- Every correlation currently reported from the calibration labels is explicitly labeled a
  validation-set number.

## Step 3 — Data-facts corrections (memo §4)

- Panel description per the audit: 75 rated pairs = 25 problems × 3 generations; 72 analyzed.
  Default to Option A wording ("75 rated from 25 problems; 72 analyzed — one problem's gold is
  indexed under a pre-renumbering filename"). Option B (rename the 3 stale rows and regenerate
  EXP16/EXP18) requires explicit human approval because it changes headline numbers; if
  approved separately, implement and update all dependent values.
- One-rater disclosure: two rubric-strictness rounds by a single annotator; 150 rated / 144
  analyzed labels; inter-round agreement (0.249 Spearman) framed as rubric stability, not
  inter-rater agreement.
- Selection disclosure: stratified 5-per-split, hand-picked, frozen 2026-04-07, no seed;
  estimand = alignment on a fixed curated panel; cite the seeded study-41 template as the
  upgrade path.
- Add the criterion-drift paragraph: the 5-rater 343-label pool is a separate population under
  a revised rubric, ρ ≈ 0.13 with the calibration criterion; held-out claims must use one
  rubric and one pool per claim ("criterion drift first, power second").
- Add the b′→b item-level extrapolation sentence (validated on 72 items; used on 157 × 3).
- MAE/MSE: adopt mean-of-duplicates, recompute via the audit scripts, and make the table
  self-consistent.
- Resolve the "~72–75" hedge to 72 wherever the analyzed set is meant.

## Step 4 — ICLR compliance

- Main text ≤ 9 pages (strict; references uncounted; appendix after references, unlimited).
  Use the memo §5 allocation table to move content; reviewers are not obliged to read the
  appendix, so every load-bearing claim and its evidence stays in the main text.
- Double-blind: strip author names, acknowledgments, grant numbers, and identifying links;
  cite the workshop version and VeriBench in third person; repo links become an anonymized
  repository or supplementary zip. Grep for author names, lab name, university, and GitHub
  handles before finishing — an identity leak is a desk reject.
- Add the required AI-use statement (uncounted) and a reproducibility statement pointing to
  the appendix and supplementary code; ethics statement only if the humans decide it is
  warranted (leave a commented stub).
- Title from the memo §5 shortlist: use option 1 as the working title unless told otherwise.

## Step 5 — Outputs

Produce, on the branch:

1. `ICLR_2027_submission/main.tex` (+ inputs) compiling cleanly to ≤ 9 main pages.
2. `ICLR_2027_submission/CHANGES.md`: every edit with rationale, memo-section pointer, and
   DOCUMENTED/DERIVED/UNKNOWN label; the figures-needing-regeneration list; the anonymization
   checklist results.
3. `ICLR_2027_submission/OPEN_QUESTIONS.md`: anything requiring a human decision (Option B
   approval, title choice, ethics statement, figure regeneration).
4. A PR from `iclr2027-port` with a summary that includes final page count and the audit-script
   verification output.

Do not submit anything to OpenReview; submission is a human action.

---
END OF AGENT INSTRUCTIONS

```
TL;DR (for the human reader; the agent should ignore this block):
This prompt has Claude Code copy the TMLR draft into the official ICLR 2027 template
(style files URL baked in), apply the full rename ledger (PTI_p / TI_m1 / SCREEN /
strict-lenient), execute the claims surgery from the revision memo (screen-semantics
abstract, Route A/B, soft-AND GM, one-conjunct, validation-set labeling), write the
audited data facts into the paper (75/72, one rater, criterion drift ρ≈0.13, selection
provenance), enforce ICLR compliance (9 pages, double-blind grep, AI-use statement),
and deliver a PR with a labeled change log and an open-questions file — with hard rules:
new branch only, no number without provenance, re-run the audit scripts first, and no
API spend without surfacing script + cost. Deadlines: abstract Sep 18, paper Sep 25
(AoE).
```
