# Complaints — TMLR 2026 desk reject (forum `WKVtlskjeQ`, submission 10994)

**TLDR:** 3 rows (`T26-*`): the Editors-in-Chief triage judgment and the two self-diagnosed causes (form-abstract rendering, triage-bait abstract); record in `desk_reject_WKVtlskjeQ.md`. All three are addressed for ICLR (plain-text form abstract in `../33b_or_ledger/openreview_form_abstract.txt`).

Status vocabulary: **Addressed** (paper already handles it), **Disclosed** (stated as a limitation, no new evidence), **Partial → E#** (edit in flight), **Deferred (owner)**, **Superseded** (the criticized artifact no longer exists), **Unknown** (review text missing). Edit IDs `E#` are defined, with their artifact sources and landed commits, in `../33b_or_ledger/edits_ledger.md`. Line numbers (`:NNN`) refer to the monolithic `main.tex` at HEAD `35df712`; since commit `710dda9` the prose lives in per-section files under `paper_latex/ICLR_2027_submission/`, so locate text by section name.

| ID | Source | Complaint | Status | Evidence | Action |
|---|---|---|---|---|---|
| T26-EiC-1 | Editors-in-Chief | "Unlikely to meet TMLR acceptance criteria" under "extremely limited reviewer capacity" (discretionary triage; no reviews) | Addressed in principle | Claims are scoped as validation-set associations (abstract, §5.1, §6); ICLR has no discretionary triage | none (venue-specific) |
| T26-self-1 | authors' postmortem | OpenReview form abstract rendered "trust index, ," (`\(...\)` stripped) and carried internal appendix references | Addressed (form abstract file) | ICLR form abstract not yet prepared | `openreview_form_abstract.txt` written (plain text, `$…$` only, no internal refs); regenerate from the final abstract before submission |
| T26-self-2 | authors' postmortem | Abstract skim-read as "n=8 correlations + held-out test failed" | Addressed | Current abstract leads with the protocol and its evidence; the held-out caveat sits in §6 | none |
