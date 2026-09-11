# AutoMetrics Literature Contrast Prompt
**TLDR:** This prompt asks an agent to verify the AutoMetrics related-work contrast against the arXiv paper and the cert-judge NeurIPS 2026 draft. Success means the agent finds no unsupported claims, keeps the contrast focused on similarities and differences, and updates only the literature artifact or appendix paragraph if corrections are needed.

Load `~/agents-config/INDEX_RULES.md` before acting.

## Task

1. Read `experiments/15_autometrics_related_work/paper_summary_and_contrast.md`.
2. Check the AutoMetrics paper at `https://arxiv.org/abs/2512.17267`.
3. Read the related-work appendix area in `paper_latex/NeurIPS_2026/paper/neurips_2026.tex`.
4. Verify that the contrast paragraph is accurate, concise, and appropriate for related work.
5. If needed, patch the summary, `writing.tex`, and the paper paragraph; otherwise report that no edits are needed.

## Guardrails

- Do not run paid LLM API calls.
- Do not run a GPU job.
- Do not introduce new claims without a source in the AutoMetrics paper or the cert-judge draft.
- Keep the paragraph focused on contrast, not a full AutoMetrics summary.
