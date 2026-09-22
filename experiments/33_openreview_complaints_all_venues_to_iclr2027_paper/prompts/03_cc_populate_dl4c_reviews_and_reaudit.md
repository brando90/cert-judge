# Prompt 03 — Ingest the pasted ICML 2026 DL4C reviews and re-audit the paper

**TLDR:** Run this only after Brando has pasted the DL4C reviews (forum `gGR1gE7x3a`) into `experiments/33_openreview_complaints_all_venues_to_iclr2027_paper/reviews/icml2026_dl4c_gGR1gE7x3a.md`. Make the agent split the pasted text into one ledger row per complaint (`D26-<reviewer>-<n>`), audit each row against the current `paper_latex/ICLR_2027_submission/main.tex`, and apply any missing edits with the same artifact-tracing and concurrency rules as prompt 02. Success: no `Unknown` rows remain in the ledger, every new row has a status and evidence, and the paper builds. Deliverable: updated ledger, `results.md`, and (if edits were needed) one paper commit on `main`. Load-bearing constraint: the pasted text is the only source; do not infer complaints the reviewers did not write.

## Steps

1. Verify the paste: the file must contain at least one block starting with "Official Review" and a rating line; if the `[[PASTE …]]` placeholders are still present, stop and report "DL4C reviews not yet supplied".
2. Extract complaints: every sentence in Weaknesses, Open Questions, Recommendations, and the meta-review that asks for a change or doubts a claim becomes one row. Quote a short anchor phrase verbatim in the row.
3. Deduplicate against existing `A26-*`/`N25-*` rows: if a DL4C complaint repeats one, link it ("same as A26-c7ev-5") and inherit its status.
4. For rows with no prior match, audit `main.tex` and assign a status; for `Partial` rows, define new edit IDs `E10+` with the artifact that supplies any number (search `experiments/archive/` first; if no artifact exists, mark `Deferred` and say what run would be needed and its cost class).
5. Apply the new edits under the prompt-02 concurrency protocol (peer message, clean tree, scratch build, explicit staging).
6. Update `results.md` (phase table, counts of rows by status, `**TLDR-end:**`), commit, rebase, push.

TL;DR: Turns the pasted DL4C reviews into `D26-*` ledger rows, audits them against the ICLR manuscript, applies artifact-traced edits where evidence exists, and pushes the updated ledger, results, and paper; no model calls, no invented complaints.
