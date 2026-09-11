# Handwritten Judge Metric Notes
**TLDR:** This folder preserves three handwritten photos about using certified LLM judges as scalable proxies for human benchmark scores. The notes are exploratory: they transcribe the images, separate uncertain handwriting from inferred meaning, and sketch paper-facing ideas without turning them into unsupported claims.

## Goal

Capture the handwritten notes from the Telegram images and turn them into a durable experiment artifact for the `cert-judge` paper work. The main idea in the notes is that the reported benchmark score should be an aggregate judge score whose relationship to an aggregate human score is validated by correlation, variance, and ranking-stability checks.

## Structure

```text
experiments/14_handwritten_judge_metric_notes/
+-- README.md
+-- handwritten_transcription_and_paper_notes.md
+-- images/
    +-- image_1_single_file_judge_dataset.jpg
    +-- image_2_benchmark_human_estimator.jpg
    +-- image_3_corr_variance_target.jpg
```

## Method

1. Checked the existing `experiments/` tree for prior transcriptions or matching Telegram image names.
2. Copied the three source photos into this folder under stable filenames.
3. Transcribed each photo with explicit `[unclear]` markers where the handwriting is ambiguous.
4. Drafted paper-facing notes that distinguish defensible claims from ideas that still need experimental support.

## Dependencies

- Related existing artifacts:
  - `experiments/03_human_validation/`
  - `experiments/04_mutual_evalutation/plan_mutual_evaluation_integration.md`
  - `experiments/06_/trust_index_formulation.md`
  - `experiments/06_cert_index_vs_human_judge_corr_and_low_var/`
  - `experiments/07_property_vs_expected_behavior_corr/`
  - `experiments/10_cert_vs_ensemble_meta_corr/`
- No LLM-budget-spending run was launched for this folder.

## Status

| Step | Status | Notes |
|------|--------|-------|
| Existing experiment check | Done | No exact prior transcription found. |
| Image archival | Done | Three unique Telegram images copied; the fourth inline image was a duplicate of image 3. |
| Transcription | Done | Ambiguous handwriting is marked explicitly. |
| Paper notes | Done | Notes are framed as hypotheses and candidate prose, not validated results. |
