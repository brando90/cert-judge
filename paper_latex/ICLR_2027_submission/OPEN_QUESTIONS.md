# Submission decisions and remaining scientific limitations

The core rewrite is integrated into `main`. See `experiments/34_iclr_mega_rewrite_astra/REPORT.md` for the evidence audit and verification, and `experiments/34_iclr_mega_rewrite_astra/submission/SUBMISSION_STATUS.md` for the current upload state. The previous question sheet is preserved in `archive/OPEN_QUESTIONS.md`.

1. **Large language model usage:** the statement now describes candidate generation, judging, experimental implementation, analysis, figures, methodological feedback, literature retrieval, drafting, and editing. The final author attestations and license remain part of the submission confirmation.
2. **Title:** “Checking the Checks: Behavioral Screens for LLM Judges of Formal Specifications” is the current manuscript title and the prepared OpenReview revision title.
3. **Original human rubric:** the audit did not recover its text. Confirm the stricter/lenient pass descriptions and whether the original instructions can be recovered. A matched-rubric test requires that recovery or validation of a reconstructed criterion.
4. **Scientific readiness:** the main comparison has no missing-specification measurements; historical alpha probes can be malformed; the scalar gives lexical judges high values. The rewrite discloses these issues. Repairs and new inference require a separate authorized study; this task did not perform them.
5. **Leanstral:** retained as a short negative-control paragraph, with its full inherited discussion archived. No additional decision is required unless the authors want to change this treatment.
6. **Anonymous supplement:** prepared as `experiments/34_iclr_mega_rewrite_astra/submission/anonymous_supplement.zip` on 09-24-2026. It contains 28 frozen score-level inputs and reconstructs eight numerical tables and five figures. Its README states the exclusions; it is not a complete inference or human-annotation reproduction. The source worktree and internal packaging receipts must not be uploaded as supplementary material.

The 343-label pool is analyzed and disclosed as a different criterion, not proposed as an untouched test set. Statements and page-budget issues from the previous question sheet have been addressed.
