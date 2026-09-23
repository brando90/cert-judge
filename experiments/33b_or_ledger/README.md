# 33b — OpenReview complaints hub: edits ledger, prompts, and form abstract

**TLDR:** The paper has been reviewed on OpenReview four times under three titles. Each round now has its own folder with the verbatim reviews and a per-venue complaint ledger (`33a_ai4math_reviews`, `33c_dl4c_reviews`, `33d_mathai_reviews`, `33e_tmlr_desk_reject`); this hub holds what is shared across venues: the edits ledger (E1–E9 with artifact sources and landed commits), the live `results.md`, the four executable prompts, the fetch log, and the plain-text OpenReview form abstract. The DL4C reviews are still missing from `33c` (login-walled forum). Started 09-22-2026 as `33_openreview_complaints_all_venues_to_iclr2027_paper`; split into 33a–33e the same day at Brando's request.

## Goal, hypothesis, decision criterion

**Uncertainty.** The ICLR 2027 manuscript descends from three reviewed drafts; nobody had checked, complaint by complaint, whether each reviewer ask is addressed, disclosed as a limitation, or silently dropped.

**Cheapest sufficient test.** Enumerate every complaint from every OpenReview round and audit the current section files against each one. No new experiments: every number the edits introduce already exists in `experiments/archive/`.

**Decision criterion.** Done when every row in the per-venue ledgers is `Addressed`, `Disclosed`, `Deferred (named owner)`, or `Superseded`; `Unknown` is allowed only for DL4C until Brando supplies the text. Numbers enter the paper only with an artifact path in `edits_ledger.md`.

## Structure

```
33a_ai4math_reviews/       pre_prompt.md (verbatim capture), agent_prompt.md (original action plan), complaints.md (A26-*)
33b_or_ledger/             this hub
├── README.md
├── results.md             live status (phase table, counts, TLDR-end)
├── edits_ledger.md        E1–E9 with number sources and landed commits; open items O1–O3; index of venue ledgers
├── fetch_attempts.md      every OpenReview fetch attempt and its failure mode
├── openreview_form_abstract.txt / make_openreview_form_abstract.py   plain-text form abstract from 00_abstract.tex
└── prompts/               01 collect · 02 apply edits · 03 ingest DL4C · 04 opt-in QA
33c_dl4c_reviews/          reviews_gGR1gE7x3a.md (SKELETON, empty until pasted), complaints.md (D26-* placeholders)
33d_mathai_reviews/        reviews_9WAWDdwqpC.md (verbatim), complaints.md (N25-*)
33e_tmlr_desk_reject/      desk_reject_WKVtlskjeQ.md (record), complaints.md (T26-*)
```

## Method

1. Locate every OpenReview forum with the public search API; record ids, venue tags, submission numbers.
2. Store each round's reviews verbatim in its own folder; log failed fetches; leave marked skeletons.
3. Write one complaint row per reviewer ask in that folder's `complaints.md` with status, evidence, action.
4. Define the edit list in `edits_ledger.md`, each with the artifact that supplies its numbers.
5. Apply the edits under the shared-checkout protocol (peer message, clean section files, scratch build, pathspec commits).
6. Keep `results.md` live; after the DL4C paste, run prompt 03; run prompt 04 only on request.

## Dependencies

- Verbatim sources: `33a_ai4math_reviews/pre_prompt.md`; `experiments/archive/02_neurips_reviews/or_neurips_2025_math_ai_workshop/or_reviews.md` (copied to 33d); `experiments/archive/21_tmlr_submission/` (33e record, headline CI provenance).
- Artifacts behind the edits: `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/`, `…/results_exp24_alpha_canonicalized_identity/`, `…/results_final_stat_reliability_suite/exp18_human_label_reliability/`, `experiments/archive/23_reanchored_calibration/`, `experiments/archive/24_expanded_panel_cli/results/pass2_full_screen_results.json`, `experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json`.
- Concurrent owner of the prose: experiment 31. No LLM calls, no credentials.

## Status

| Step | Status | Notes |
|---|---|---|
| Locate forums | Done | 4 forums; no NeurIPS 2026 / ICLR 2026 submission found (09-22-2026) |
| Capture reviews | 3 of 4 | DL4C blocked by the OpenReview login wall (`fetch_attempts.md`) |
| Per-venue ledgers | Done | 33a 29 rows · 33d 14 rows · 33e 3 rows · 33c placeholders |
| Paper edits E1–E9 | Done | commit `e0631b6`; six VeriBench-judge rows later superseded by the §5.4 cut |
| DL4C ingestion (prompt 03) | Blocked | needs the pasted text in `33c_dl4c_reviews/reviews_gGR1gE7x3a.md` |
| QA (prompt 04) | Not requested | opt-in |
