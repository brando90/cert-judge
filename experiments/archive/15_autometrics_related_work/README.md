# AutoMetrics Related Work Contrast
**TLDR:** This folder summarizes AutoMetrics (arXiv:2512.17267) as related work for cert-judge and extracts the precise similarity/difference claims needed for the paper appendix. It is a literature-analysis artifact, not an LLM-budget experiment.

## Goal

Summarize AutoMetrics and contrast it with cert-judge so the paper can cite it accurately in the related-work appendix.
The key question is how AutoMetrics' adaptive metric induction differs from cert-judge's property certification of Lean 4 theorem judges.

## Structure

```text
experiments/15_autometrics_related_work/
+-- README.md
+-- paper_summary_and_contrast.md
+-- writing.tex
+-- expt_v1/
    +-- cc.md
    +-- results/
        +-- results_summary_2026-05-26__16-17-05.md
```

## Method

1. Fetched the arXiv page and source for AutoMetrics, "AutoMetrics: Approximate Human Judgements with Automatically Generated Evaluators" ([arXiv:2512.17267](https://arxiv.org/abs/2512.17267)).
2. Read the introduction, method, experiments, case study, related work, MetricBank description, and limitations from the paper source.
3. Extracted claims that are directly relevant to cert-judge: low-data human calibration, generated LLM-judge criteria, metric regression, sensitivity/stability perturbations, and stated limitations.
4. Drafted appendix-ready contrast text that separates shared motivation from the main methodological difference.

## Dependencies

- Main cert-judge paper draft: `paper_latex/NeurIPS_2026/paper/neurips_2026.tex`
- Bibliography file: `paper_latex/NeurIPS_2026/paper/refs.bib`
- No GPU jobs, W&B runs, or paid LLM API calls were launched.

## Status

| Step | Status | Notes |
|------|--------|-------|
| Source review | Done | Used the arXiv abstract page and TeX source. |
| Summary artifact | Done | See `paper_summary_and_contrast.md`. |
| Paper-facing prose | Done | See `writing.tex` and the NeurIPS 2026 appendix edit. |
| LLM-budget experiment | N/A | Literature-only folder; no model calls were needed. |
