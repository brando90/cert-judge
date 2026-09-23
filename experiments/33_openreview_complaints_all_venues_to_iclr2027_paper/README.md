# 33 — OpenReview complaints from every venue, addressed one by one in the ICLR 2027 paper

**TLDR:** This paper has been reviewed on OpenReview four times under three titles (NeurIPS 2025 MATH-AI, ICML 2026 AI4Math, ICML 2026 DL4C, and a TMLR 2026 desk reject). This experiment collects every review verbatim (`reviews/`), turns each complaint into one ledger row with a status against `paper_latex/ICLR_2027_submission/main.tex` (`complaints_ledger.md`), ships the prompts that execute the collection, the paper edits, the DL4C ingestion, and an opt-in QA pass (`prompts/`), and applies the nine artifact-traced edits E1–E9 to the manuscript. The DL4C reviews could not be fetched without an OpenReview login (`reviews/fetch_attempts.md`); their file is an explicitly empty skeleton for Brando to paste into. Started 09-22-2026.

## Goal, hypothesis, decision criterion

**Uncertainty.** The ICLR 2027 manuscript descends from three reviewed drafts; nobody had checked, complaint by complaint, whether each reviewer ask is now addressed, disclosed as a limitation, or silently dropped. A dropped ask that a returning reviewer recognizes is the cheapest way to lose the submission.

**Cheapest sufficient test.** Enumerate every complaint from every OpenReview round and audit the current `main.tex` against each one. No new experiments are needed: every number the edits introduce already exists in `experiments/archive/`.

**Decision criterion.** The pass is done when every ledger row is `Addressed`, `Disclosed`, `Deferred (named owner)`, or `Superseded`; a row may stay `Partial` only while its edit is in flight, and `Unknown` only for the DL4C reviews until Brando supplies them. Numbers enter the paper only with an artifact path in the ledger.

## Structure

```
33_openreview_complaints_all_venues_to_iclr2027_paper/
├── README.md                                   ← this file
├── results.md                                  ← live status (phase table, counts, TLDR-end)
├── complaints_ledger.md                        ← one row per complaint; edit list E1–E9 with number sources
├── openreview_form_abstract.txt                ← plain-text abstract for the ICLR OpenReview form (TMLR lesson)
├── make_openreview_form_abstract.py            ← regenerates the file above from main.tex; warns on leftover LaTeX / internal refs
├── reviews/
│   ├── neurips2025_mathai_9WAWDdwqpC.md        ← verbatim (ivJs 6/10, 36Hd 3/10)
│   ├── icml2026_ai4math_xmHP3UhGQ8.md          ← verbatim copy of experiments/18_icml_2026_reviews/pre_prompt.md (accept, poster)
│   ├── icml2026_dl4c_gGR1gE7x3a.md             ← SKELETON, empty until Brando pastes the reviews (accept, poster)
│   ├── tmlr2026_desk_reject_WKVtlskjeQ.md      ← desk-reject record and self-diagnosed causes
│   └── fetch_attempts.md                       ← every fetch attempt and its failure mode
└── prompts/
    ├── 01_cc_collect_openreview_complaints.md  ← the collection pass (what produced reviews/ and the ledger)
    ├── 02_cc_address_complaints_in_iclr_main_tex.md ← applies E1–E9 under the concurrent-editing protocol
    ├── 03_cc_populate_dl4c_reviews_and_reaudit.md   ← run after the DL4C paste
    └── 04_cc_qa_reviewer_coverage.md           ← opt-in QA (only when Brando asks for QA)
```

## Method

1. Locate every OpenReview forum for the paper with the public search API (`notes/search`); record forum ids, venue tags, submission numbers.
2. Copy reviews already captured in the repo verbatim; attempt to fetch the rest; log every attempt; leave marked skeletons where fetches fail.
3. Read `main.tex` end to end and write one ledger row per complaint with status, evidence, and action.
4. Define the edit list E1–E9, each with the artifact that supplies its numbers.
5. Apply the edits under the concurrent-editing protocol (peer message, clean tree, scratch build, explicit staging), rebuild the PDF, commit and push.
6. Keep `results.md` live; after the DL4C paste, run prompt 03; run prompt 04 only on request.

## Dependencies

- `experiments/18_icml_2026_reviews/pre_prompt.md` (AI4Math capture; source of truth for `A26-*`).
- `experiments/archive/02_neurips_reviews/or_neurips_2025_math_ai_workshop/or_reviews.md` (MATH-AI capture).
- `experiments/archive/21_tmlr_submission/` (desk-reject record, headline CI provenance).
- Artifacts for the edits: `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/`, `…/results_exp24_alpha_canonicalized_identity/`, `…/results_final_stat_reliability_suite/exp18_human_label_reliability/`, `experiments/archive/23_reanchored_calibration/`, `experiments/archive/24_expanded_panel_cli/results/pass2_full_screen_results.json`.
- Concurrent owners: experiment 31 (main-text prose). Experiment 32 (§5.4 VeriBench re-scoring) was stopped on 09-22-2026 when Brando removed §5.4 / Table 5 from the paper. This experiment stays off the abstract and intro.
- No LLM calls, no credentials.

## Status

| Step | Status | Notes |
|---|---|---|
| Locate forums | Done | 4 forums: `9WAWDdwqpC`, `xmHP3UhGQ8`, `gGR1gE7x3a`, `WKVtlskjeQ`; no NeurIPS 2026 / ICLR 2026 submission found (09-22-2026) |
| Capture reviews | Partial | 3 of 4 captured; DL4C blocked by the OpenReview login wall (`reviews/fetch_attempts.md`) |
| Ledger | Done (v1) | 46 rows + DL4C placeholders; 3 open non-reviewer items O1–O3 |
| Prompts 01–04 | Done | Recommended model/effort is stated in the chat handoff, not in the files (Trigger Rule 36) |
| Paper edits E1–E9 | see `results.md` | applied by the same session that wrote this folder, 09-22-2026 |
| DL4C ingestion (prompt 03) | Blocked | needs Brando's paste |
| QA (prompt 04) | Not requested | opt-in |
