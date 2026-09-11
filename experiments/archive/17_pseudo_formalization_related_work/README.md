# Pseudo-Formalization Related Work Contrast
**TLDR:** This folder summarizes "Pseudo-Formalization for Automatic Proof Verification" (arXiv:2605.20531) and records the exact contrast with cert-judge. It is a literature-analysis artifact, not a model-budget experiment.

## Goal

Summarize PF+BV and decide whether it belongs in the related-work appendix for cert-judge, VeriBench, VeriBench-DT, and VeriBench-Deps.
The useful contrast is real: PF+BV verifies natural-language mathematical proofs by rewriting them into structured modules, whereas cert-judge certifies whether an LLM judge is reliable for Lean 4 theorem/specification scoring.

## Structure

```text
experiments/17_pseudo_formalization_related_work/
+-- README.md
+-- paper_summary_and_contrast.md
+-- writing.tex
```

## Method

1. Fetched the arXiv page and PDF for "Pseudo-Formalization for Automatic Proof Verification" ([arXiv:2605.20531](https://arxiv.org/abs/2605.20531)).
2. Checked the released code repository, [Slim205/pseudo-formalization](https://github.com/Slim205/pseudo-formalization).
3. Read the abstract, introduction, method, experiments, related work, and limitations from the PDF text.
4. Extracted similarities and differences against cert-judge before writing any paper-facing prose.

## Dependencies

- Main cert-judge paper draft: `paper_latex/NeurIPS_2026/paper/neurips_2026.tex`
- Bibliography file: `paper_latex/NeurIPS_2026/paper/refs.bib`
- No GPU jobs, W&B runs, or paid LLM API calls were launched.

## Status

| Step | Status | Notes |
|------|--------|-------|
| Source review | Done | Used arXiv page, PDF text, and released GitHub README. |
| Summary artifact | Done | See `paper_summary_and_contrast.md`. |
| Paper-facing prose | Done | See `writing.tex` and the related-work appendix edit. |
| LLM-budget experiment | N/A | Literature-only folder; no model calls were needed. |
