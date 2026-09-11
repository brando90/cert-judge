# Autojudge Human Correlation Val/Test Experiment
**TLDR:** This folder tracks the proposed experiment for using all available human judgments plus Ethan pass labels to select an autojudge without p-hacking. The locked direction is to split data into validation and test sets, tune or select only on validation, and report the held-out test correlation to human judgments.

## Goal

Evaluate whether an autojudge metric-selection procedure can produce a stronger Lean theorem judge while using all available human judgments fairly. The core scientific constraint is that any judge selection or hyperparameter choice must happen before the held-out test correlation is reported.

## Structure

```text
experiments/17_autojudge_human_corr_val_test/
├── README.md
└── scratch_notes.md
```

## Method Sketch

1. Use all five human annotators plus Ethan pass 1 and Ethan pass 2 where available.
2. Define a validation/test split before running judge selection.
3. Use the autojudge metric algorithm to select the judge or prompt on the validation split.
4. Report the final correlation against aggregated human judgments only on the held-out test split.

## Dependencies

- Existing human-label data under `experiments/human_labels/` and related validation artifacts.
- The autojudge metric paper/procedure referenced in `scratch_notes.md`.
- Existing judge-correlation scripts from the validation experiments.

## Status

| Step | Status | Notes |
|------|--------|-------|
| Scratch note captured | Done | See `scratch_notes.md`. |
| Val/test split frozen | TODO | Ethan/Brando need to choose or confirm the split. |
| Autojudge algorithm implemented | TODO | Implement from the referenced paper/procedure. |
| Held-out test result reported | TODO | Report only after validation selection is locked. |
