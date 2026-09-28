# Prompt 04 — QA: verify reviewer coverage and number provenance (opt-in, run only when Brando asks for QA)

**TLDR:** Make a fresh reviewer agent check, row by row, that the per-venue `complaints.md` files (`experiments/33a_ai4math_reviews`, `33c_dl4c_reviews`, `33d_mathai_reviews`, `33e_tmlr_desk_reject`) are faithful to the verbatim reviews beside them, that every status is justified by the cited section-file text (`paper_latex/ICLR_2027_submission/0*.tex`, `99*.tex`), and that every number introduced by edits E1–E9 matches its artifact. Success: PASS only if no row misstates a review, no `Addressed` row lacks supporting paper text, and every number reproduces from its artifact path; otherwise a blocking list with file:line and the concrete fix. Deliverable: `qa/qa_report_<MM-DD-YYYY>.md` in `experiments/33b_or_ledger/`. Load-bearing constraint: read-only on the paper; report, do not fix, unless Brando's dispatch says otherwise.

## Checks

1. **Faithfulness:** for each `complaints.md` row, find the sentence in the verbatim review file in the same folder that the row paraphrases; flag rows with no source sentence or with a stronger claim than the reviewer made.
2. **Coverage:** list any reviewer sentence that asks for a change and has no ledger row.
3. **Status justification:** for `Addressed`/`Disclosed`, open the cited section (grep the section files; the ledger's `:NNN` numbers predate the 710dda9 split) and confirm the text does what the row says; for `Partial → E#`, confirm the edit landed (`git log -p`) and the row was updated.
4. **Number provenance:** for E3, E4, E5, E7, E8, open the artifact path and recompute or read the field; report each value side by side with the paper text.
5. **Build:** in a scratch copy of `paper_latex/ICLR_2027_submission`, run `latexmk -pdf main.tex`; zero undefined citations/references; report page count.
6. **Writing rules:** one sentence per line (from the paper dir: `python3 ~/agents-config/scripts/latex_sentence_lines.py --check main.tex 0*.tex 99*.tex`), no "development set" wording, split names present for every reported number.

## Output format

`# QA report — experiment 33` / `**TLDR:** PASS|FAIL …` / blocking issues first (file:line, quote, fix) / non-blocking notes / a table of every number checked (paper value, artifact value, path, match).

TL;DR: A read-only audit of the ledger's faithfulness, the paper's coverage of every reviewer ask, and the provenance of every number E1–E9 introduced; produces a dated QA report and no paper edits.
