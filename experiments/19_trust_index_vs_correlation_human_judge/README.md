# Human Labels
**TLDR:** This experiment stores the human-label TSVs used for cert-judge validation and records the current LeanStral single-judge result. The only new interpretation here is scoped to `labs-leanstral-2603|P1_BASELINE`, not to other agents or judge-model families.

## Goal

Preserve the human-label datasets and keep a short, auditable note about the one LeanStral judge configuration that currently shows moderate human agreement.

## Structure

```text
experiments/18_human_labels/
├── README.md
├── results.md
├── expert_harsh_set_data.tsv
├── lenient_set_data.tsv
├── participant1_data_correct_prompt.tsv
├── participant2_data_pass_1.tsv
├── participant3_data_pass_1.tsv
├── participant4_data_pass_1.tsv
├── participant5_data_pass_1.tsv
└── old_prompt/
    ├── participant1_data_pass_1.tsv
    └── participant1_data_pass_2.tsv
```

## Method

1. Keep human-label TSVs in one numbered experiment folder.
2. Reuse cached judge-human analyses from `experiments/04_veribench_validation/`.
3. Document the LeanStral `P1_BASELINE` finding in `results.md` with source paths and exact metrics.

## Dependencies

- Human-label TSVs in this directory.
- Cached judge analyses under `experiments/04_veribench_validation/results_exp39_autometrics_autoti/`.
- Prompt definition in `experiments/02_reviewer_response_neurips_math_ai_2026/utils/sensitivity_sweep.py`.

## Status

| Step | Status | Notes |
| --- | --- | --- |
| Directory numbering | Done | Renamed from `experiments/human_labels` to `experiments/18_human_labels`. |
| Human-label files | Done | Existing TSVs preserved. |
| LeanStral result note | Done | See `results.md`. |
| New experiment run | N/A | This folder records labels and a result interpretation; no new judge calls were run. |
