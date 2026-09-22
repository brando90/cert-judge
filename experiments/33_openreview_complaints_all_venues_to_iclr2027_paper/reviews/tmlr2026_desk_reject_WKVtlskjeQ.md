# TMLR 2026 — desk rejection of submission 10994 (record, no reviewer reviews)

**TLDR:** The TMLR submission (OpenReview forum `WKVtlskjeQ`, submission 10994, 07-29-2026) was desk-rejected on 07-31-2026 by Editors-in-Chief discretionary triage; no reviewer or action-editor reviews exist. The complaint is therefore the triage judgment itself plus the two self-diagnosed causes recorded at the time. Source files: `experiments/archive/21_tmlr_submission/{desk_reject_response_comment.md,resubmission_kit.md,TMLR_REVISION_BACKLOG.md}`.

## What the venue said (as recorded on 08-01-2026 in `resubmission_kit.md`)

> EiC discretionary triage ("unlikely to meet TMLR acceptance criteria... extremely limited reviewer capacity"), 31 Jul 2026. NOT anonymity / stylefile / length / overlap / quota (all verified compliant).

The verbatim EiC note was never captured into the repo; the fragments above are the only quoted text. The forum itself is behind OpenReview's login wall (see `fetch_attempts.md`).

## Self-diagnosed causes (authors, 08-01-2026)

1. **Form-field abstract rendering fault.** The OpenReview form abstract used `\(\mathrm{TI}_{\mathrm{var}}\)`, which OpenReview strips, so the landing page read "a variance-aware trust index, ," and included internal references such as "(Appendix G)". The PDF was intact.
2. **Triage-bait abstract structure.** The abstract skim-read as "n=8 correlations + held-out test failed" because the negative disclosure was appended to a workshop-poster framing instead of positioned as the contribution.

## Carry-over for ICLR 2027

- The ICLR 2027 OpenReview form abstract must be plain text with `$...$` math only and no internal section or appendix references; a ready-to-paste version is `../openreview_form_abstract.txt` (regenerate it from the final `main.tex` abstract before submission).
- Deferred reviewer asks from the ICML 2026 AI4Math round that the TMLR packet listed as revision material are folded into `../complaints_ledger.md` (they carry `A26-*` IDs), so nothing in `TMLR_REVISION_BACKLOG.md` is lost.
