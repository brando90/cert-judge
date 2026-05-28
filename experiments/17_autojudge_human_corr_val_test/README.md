# Autojudge Human Correlation Val/Test Experiment
**TLDR:** This folder implements a validation-only autojudge prompt-selection experiment over saved Codex, Opus, and Leanstral judge outputs. It aggregates five participant label files plus Ethan pass1/pass2, freezes a task-level train/test split before selection, and reports held-out test correlations without new LLM calls.

## Goal

Evaluate whether an autojudge metric-selection procedure can produce a stronger Lean theorem judge while using all available human judgments fairly. The core scientific constraint is that any judge selection or hyperparameter choice must happen before the held-out test correlation is reported.

## Structure

```text
experiments/17_autojudge_human_corr_val_test/
├── README.md
├── PROTOCOL.md
├── REPORT.md
├── run_autojudge_val_test.py
├── scratch_notes.md
└── results/
    ├── all_candidate_correlations.csv
    ├── frozen_split.csv
    ├── missing_pairs.csv
    ├── pair_label_aggregates.csv
    ├── selection_table.csv
    └── summary.json
```

## Method Sketch

1. Load all five participant label files plus Ethan pass 1 and Ethan pass 2.
2. Aggregate labels by exact `gold_file::candidate_file` key.
3. Keep exact pairs scored by all primary Codex, Opus, and Leanstral candidates.
4. Freeze a task-level hash split before selection.
5. Select one prompt per family on validation/train Spearman only.
6. Report the selected prompt's held-out test Spearman correlation.

## Dependencies

- Existing human-label data under `experiments/human_labels/`.
- Ethan pass labels under `experiments/04_veribench_validation/data/`.
- Saved Exp16-style judge rows for Codex, Opus, and Leanstral under `experiments/04_veribench_validation/`.
- The AutoMetrics paper/procedure referenced in `scratch_notes.md` for motivation; this implementation is a no-new-LLM selector over an existing prompt bank.

## Status

| Step | Status | Notes |
|------|--------|-------|
| Scratch note captured | Done | See `scratch_notes.md`. |
| Val/test split frozen | Done | See `PROTOCOL.md` and `results/frozen_split.csv`. |
| Autojudge algorithm implemented | Done | See `run_autojudge_val_test.py`. |
| Held-out test result reported | Done | See `REPORT.md` and `results/selection_table.csv`. |

## Reproduce

```bash
cd /Users/brandomiranda/cert-judge-autojudge-human-corr-val-test
python experiments/17_autojudge_human_corr_val_test/run_autojudge_val_test.py \
  --out-dir experiments/17_autojudge_human_corr_val_test/results
```
