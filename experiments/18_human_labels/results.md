# LeanStral P1 Baseline Result
**TLDR:** The current single-judge result worth calling out is `labs-leanstral-2603|P1_BASELINE`: on the five-human mean target it reaches item Spearman `0.422` and task Spearman `0.541` over `60` items and `20` tasks. This is a LeanStral-only note; it deliberately does not explain the same prompt on other agents or judge-model families.

## Finding

`labs-leanstral-2603|P1_BASELINE` is the cleanest LeanStral single-judge story in the current cached analyses. The relevant result is raw judge-human agreement, not a learned ensemble, per-task isotonic oracle, or AutoTI composition.

| Target / analysis | Item Spearman | Task Spearman | Items | Tasks | Source |
| --- | ---: | ---: | ---: | ---: | --- |
| Five-human `mean` target | `0.422` | `0.541` | `60` | `20` | `experiments/04_veribench_validation/results_exp39_autometrics_autoti/REPORT.md` |
| Five-human `zscore_mean` target | `0.426` | `0.544` | `60` | `20` | `experiments/04_veribench_validation/results_exp39_autometrics_autoti_zscore_mean/REPORT.md` |
| All-human task aggregation | n/a | `0.510` | `72` | `24` | `experiments/04_veribench_validation/results_exp34_all_human_task_aggregation/REPORT.md` |

The `0.55ish` number is therefore best described as task-level Spearman, roughly `0.54`, with item-level agreement around `0.42`.

## What the Judge Is

The judge id combines the LeanStral model with the baseline semantic-alignment prompt:

- Model: `labs-leanstral-2603`
- Prompt: `P1_BASELINE`
- Cached score source: `experiments/04_veribench_validation/results_exp16_leanstral_r3_median`
- Prompt source: `experiments/02_reviewer_response_neurips_math_ai_2026/utils/sensitivity_sweep.py`

`P1_BASELINE` asks a Lean 4 semantic judge to score how well a generated theorem captures the correctness properties of a reference implementation on a `0.0` to `1.0` scale. Its rubric reserves `1.0` for semantic equivalence, gives high partial credit for minor omissions, midrange scores for meaningful gaps, and near-zero scores for trivial or incorrect theorems.

## Interpretation

For LeanStral, the simple semantic-alignment rubric appears to be better matched to the human target than more elaborate calibrated machinery is necessary for this specific headline. The stronger task-level correlation is also the more natural number to report: aggregating multiple generated items within the same task reduces per-item noise and better reflects whether the judge ranks task-level quality in the same direction as humans.

This is moderate agreement, not a solved judge. The item-level correlation remains about `0.42`, so individual examples still contain substantial noise. The result should be written as: LeanStral with `P1_BASELINE` gives a useful raw single-judge signal on the current human-label set, with task-level Spearman around `0.54`.

## Scope

This note does not make a cross-agent or cross-model claim. It is intentionally limited to the LeanStral `P1_BASELINE` result and should not be used to explain why the same prompt behaves differently elsewhere.
