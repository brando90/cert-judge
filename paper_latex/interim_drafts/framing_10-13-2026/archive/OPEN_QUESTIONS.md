# OPEN QUESTIONS — human decisions needed for the ICLR 2027 submission

**TLDR:** The ICLR 2027 paper is now the accepted ICML 2026 DL4C paper in ICLR format (see
`CHANGES.md`). Four author decisions remain: the ~2-page main-text overflow, whether to write the
ICLR statements, the title, and whether to fold in the newer 343-label annotation pool. The prior
question list — which concerned the superseded *Surrogate Gap* / PTI-v0 draft — is preserved at
`paper_latex/archive/ICLR_2027_submission_old_09162026/OPEN_QUESTIONS.md`.

> **Status 2026-09-22:** item 1 (page budget) is resolved — the main text is now ~7 pages after the rewrite and the
> removal of §5.4/Table 5 (the carried-over VeriBench agent ranking). The paper is no longer a verbatim port; see git log
> and `experiments/31_final_iclr_paper_writing/notes.md`. Items 2–5 remain open.

1. **Main-text page budget (blocking for submission).** Main text runs pages 1–11; ICLR counts main
   text only and allows 9. Two pages must come out, and that is a content call. Cheapest candidates,
   in order of least scientific loss:
   - §2 Related Work is ~1 page in the main text while Appendix A already holds an extended version;
     compress the main-text version to a short paragraph and lean on the appendix.
   - §6 Limitations repeats the `n=75` / 343-label held-out plan twice (once under "Validation vs.
     test protocol", once under "Limitations"); merging removes ~0.4 page.
   - Move Table 6 (threshold sweep) and/or Table 7 (VeriBench agent ranking) to the appendix.
   **Decide: which cuts, or request a different target length.**

2. **ICLR statements (Ethics / Reproducibility / LLM usage).** None are present — the ICML paper had
   none, and nothing was invented. The reproducibility statement can be drafted from repository
   facts; the LLM-usage statement needs the authors' own account of how LLMs were used in writing.
   **Decide: draft them (and supply the LLM-usage facts), or submit without.**

3. **Title.** Currently the accepted ICML title verbatim: *"Certifying the Judge: Falsifiable
   Properties for LLM-Based Evaluation of Formal Code"*. It is the right title for a resubmission of
   the accepted work. **Decide: keep, or retitle for the main-conference audience.**

4. **The newer annotation pool.** §6 announces, but does not use, the 5-reviewer / 343-label / 78-pair
   corpus in `experiments/human_labels`, framing the locked held-out test as future work. A main
   conference submission is a natural place to actually run it. **Decide: keep as announced future
   work (zero new spend), or register an active experiment and run the locked held-out analysis
   before the deadline.** Any judge re-runs need an explicit call/cost quote first.

5. **Supplement bundle.** `ANONYMIZED_SUPPLEMENT_ALLOWLIST.md` still enumerates Experiment-29 /
   PTI-v0 artifacts, which this paper no longer reports. Its double-blind hygiene rules still apply;
   its artifact list must be re-derived against the `TI_var` / EXP16–EXP19 outputs this paper cites.
   **Decide: whether a supplement is being submitted at all.**

## Inherited nits (flagged, not changed)

- Appendix E says "Figures A.1–A.3"; under ICLR numbering those are Appendix F figures. Present in
  the accepted ICML paper too; fixing it means choosing the right `\ref` targets.
- The `TI_var` display equation keeps the two-line `aligned` break tuned for the narrow ICML column.
