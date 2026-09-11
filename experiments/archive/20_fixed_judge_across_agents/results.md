# Fixed Judge Across Agents Results
**TLDR:** For the fixed judge `labs-leanstral-2603|P1_BASELINE`, the best full-panel calibrated item-rank result is five-human mean per-task calibration: item Spearman `0.840`, Kendall `0.721`, Pearson `0.857`, and task Spearman `0.914`. The best reportable full-panel family rows are LeanStral `labs-leanstral-2603|P1_BASELINE`, GPT-4o-mini `gpt-4o-mini|P1_BASELINE`, Codex `gpt-5.3-codex|P14_HUMAN_ALIGN_V2`, and Claude `claude-opus-4-7|P1_BASELINE`; Qwen is not comparable yet because there is no item-level five-human cache. The best raw no-calibration LeanStral result is much lower: item Spearman `0.426`, Kendall `0.325`, Pearson `0.417`, and task Spearman `0.544`.

## Sign-Off Summary

Brando wants a TMLR-ready result where one fixed judge works across as many agent families as possible. "Works" means two things:

1. For each agent row, the fixed judge's scores correlate strongly with human judgments.
2. If an agent-conditioned trust index is defined, that trust-index value correlates strongly with the fixed judge's human agreement across agent rows.

The target threshold is approximately `0.6` for each correlation metric: Pearson `r`, Spearman `rho`, and Kendall `tau`. Higher is better, and more agent rows are better. Treat 3 agent rows as a smoke panel; use 5 or more rows with uncertainty estimates for a paper-facing cross-agent trend claim.

Current state: existing completed runs support a strong *judge-calibration* result, not yet the requested cross-agent agent-row result. The current best tables below should be used as the starting evidence for Brando; the agent CLI/model rows remain to be generated and joined.

## Best Judge Rows To Report

Use this table for the short sign-off version: one best currently reportable judge row for the LeanStral judge being discussed, plus the best full-panel calibrated rows for GPT-4o-mini, Codex, and Claude. Qwen is listed honestly as unavailable for this same five-human human-alignment comparison.

| Family | Judge to report | Regime | Human target | n tasks/items | Spearman rho | Kendall tau | Pearson r | Task rho | Source |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| LeanStral | `labs-leanstral-2603|P1_BASELINE` | Best fixed LeanStral candidate, per-task calibrated | five-human `mean` | 20 / 60 | 0.840 | 0.721 | 0.857 | 0.914 | EXP38; EXP41 sweep |
| GPT-4o-mini | `gpt-4o-mini|P1_BASELINE` | Best full-panel calibrated GPT-4o-mini row | five-human `zscore_mean` | 20 / 60 | 0.843 | 0.703 | 0.873 | 0.910 | EXP41 Table 3 |
| Codex | `gpt-5.3-codex|P14_HUMAN_ALIGN_V2` | Best full-panel calibrated Codex row | five-human `zscore_mean` | 20 / 60 | 0.884 | 0.731 | 0.896 | 0.967 | EXP41 Table 3 |
| Claude | `claude-opus-4-7|P1_BASELINE` | Best full-panel calibrated Claude row | five-human `zscore_mean` | 20 / 60 | 0.870 | 0.728 | 0.892 | 0.934 | EXP41 Table 3 |
| Qwen | N/A | Not comparable yet | N/A | N/A | N/A | N/A | N/A | N/A | EXP41/EXP42 exclude Qwen: no item-level five-human judge cache |

Note: the best EXP41 full-panel calibrated LeanStral family row on the five-human `zscore_mean` target is `labs-leanstral-2603|P8_STRICT_B` with Spearman `0.806`, Kendall `0.664`, Pearson `0.856`, and task rho `0.851`. The table above keeps `labs-leanstral-2603|P1_BASELINE` because that is the fixed LeanStral judge candidate already selected for the cross-agent run and it has the strongest calibrated five-human mean item-rank result among the fixed-candidate summaries.

## Current Best Results For The Fixed Judge

This section is the answer for the single judge currently proposed for the next cross-agent run:

```text
labs-leanstral-2603|P1_BASELINE
```

The judge performs best when per-task human calibration is allowed. Without human calibration, it is the best raw fixed-judge candidate, but it does not clear the desired `>= 0.6` item-level target.

| Regime | Human target | Split | Uses evaluation-task human labels? | n tasks/items | Item Spearman rho | Kendall tau | Pearson r | Task rho | Source |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Best raw no-calibration | five-human `zscore_mean` | full | No | 20 / 60 | 0.426 | 0.325 | 0.417 | 0.544 | EXP41 Table 4; EXP39 z-score |
| Raw no-calibration | five-human `mean` | full | No | 20 / 60 | 0.422 | 0.325 | 0.433 | 0.541 | EXP39 mean; EXP41 sweep |
| Best full-panel calibrated | five-human `mean` | full | Yes, per-task | 20 / 60 | 0.840 | 0.721 | 0.857 | 0.914 | EXP38; EXP41 sweep |
| Best full-panel calibrated Pearson/task rho | five-human `trimmed_mean` | full | Yes, per-task | 20 / 60 | 0.830 | 0.687 | 0.862 | 0.934 | EXP41 sweep |
| Full-panel calibrated | five-human `zscore_mean` | full | Yes, per-task | 20 / 60 | 0.675 | 0.558 | 0.700 | 0.759 | EXP42 oracle; EXP41 sweep |
| Best held-out-task calibrated | five-human `mean` | test | Yes, per-task test labels | 6 / 18 | 0.619 | 0.469 | 0.711 | 0.754 | EXP41 sweep |
| Held-out-task calibrated | five-human `trimmed_mean` | test | Yes, per-task test labels | 6 / 18 | 0.572 | 0.430 | 0.676 | 0.600 | EXP41 sweep |
| Held-out-task calibrated | five-human `zscore_mean` | test | Yes, per-task test labels | 6 / 18 | 0.344 | 0.279 | 0.330 | 0.429 | EXP41 sweep; EXP42 oracle |
| LOO global calibration | five-human `zscore_mean` | leave-one-task-out | No task-specific labels | 20 / 60 | 0.170 | 0.100 | 0.352 | 0.533 | EXP41 Table 5 |
| Global train-to-test transfer | five-human `zscore_mean` | test | No test-task labels | 6 / 18 | -0.084 | -0.084 | -0.102 | -0.174 | EXP42 primary table |
| Legacy pooled human-label regime | pass1/pass2/avg labels | pooled | No new calibration | 72 rows | 0.041 avg Spearman | N/A | N/A | N/A | EXP16 cached row |

Source key for this fixed-judge table:

- EXP16 cached row: `experiments/04_veribench_validation/results_exp16_leanstral_r3_median/judge_rows.csv`
- EXP38: `experiments/04_veribench_validation/results_exp38_five_human_per_task_isotonic/per_judge_metrics.csv`
- EXP39 mean: `experiments/04_veribench_validation/results_exp39_autometrics_autoti/REPORT.md`
- EXP39 z-score: `experiments/04_veribench_validation/results_exp39_autometrics_autoti_zscore_mean/REPORT.md`
- EXP41 Table 4: `experiments/04_veribench_validation/results_exp41_honest_train_test/HONEST_TABLE.md`
- EXP41 sweep: `experiments/04_veribench_validation/results_exp41_honest_train_test/sweep_results.csv`
- EXP42 oracle / primary table: `experiments/04_veribench_validation/results_exp42_proper_transfer/PAPER_TABLE.md`
- EXP42 sweep: `experiments/04_veribench_validation/results_exp42_proper_transfer/sweep_results.csv`

Bottom line for this judge: the strongest honest item-rank number is `0.840` item Spearman / `0.721` Kendall under five-human mean per-task calibration. The strongest full-panel Pearson/task-rho numbers are `0.862` / `0.934` under five-human trimmed-mean per-task calibration. The strongest raw no-calibration number is `0.426` item Spearman / `0.544` task Spearman, so the raw fixed-judge claim still needs either a better construction or a clearly labeled limitation.

## Current Best Across Judge Families (Context)

### Best Positive Result: Per-Task Human-Calibrated Judges

Source: `experiments/04_veribench_validation/results_exp41_honest_train_test/HONEST_TABLE.md`.

Human target is the five-rater `zscore_mean`. Calibration is per-task isotonic using human labels for the task partition being evaluated. This is the strongest current result, but it is a human-calibrated result, not a raw/no-label judge result.

| Split | Model family | Best judge | n tasks/items | Spearman rho | Kendall tau | Pearson r | Task rho | Source table |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Test tasks | LeanStral | `labs-leanstral-2603|P8_STRICT_B` | 6 / 18 | 0.767 | 0.615 | 0.743 | 0.886 | EXP41 Table 2 |
| Test tasks | GPT-4o-mini | `gpt-4o-mini|P1_BASELINE` | 6 / 18 | 0.923 | 0.810 | 0.941 | 1.000 | EXP41 Table 2 |
| Test tasks | GPT-5.3 Codex | `gpt-5.3-codex|P1_BASELINE` | 6 / 18 | 0.933 | 0.830 | 0.943 | 1.000 | EXP41 Table 2 |
| Test tasks | Claude Opus 4.7 | `claude-opus-4-7|P4_CHECKLIST` | 6 / 18 | 0.930 | 0.824 | 0.936 | 1.000 | EXP41 Table 2 |
| Full panel | LeanStral | `labs-leanstral-2603|P8_STRICT_B` | 20 / 60 | 0.806 | 0.664 | 0.856 | 0.851 | EXP41 Table 3 |
| Full panel | GPT-4o-mini | `gpt-4o-mini|P1_BASELINE` | 20 / 60 | 0.843 | 0.703 | 0.873 | 0.910 | EXP41 Table 3 |
| Full panel | GPT-5.3 Codex | `gpt-5.3-codex|P14_HUMAN_ALIGN_V2` | 20 / 60 | 0.884 | 0.731 | 0.896 | 0.967 | EXP41 Table 3 |
| Full panel | Claude Opus 4.7 | `claude-opus-4-7|P1_BASELINE` | 20 / 60 | 0.870 | 0.728 | 0.892 | 0.934 | EXP41 Table 3 |

Interpretation: all four evaluated judge families clear Spearman `>= 0.70` after per-task human calibration. For the requested `>= 0.6` criterion, the weakest current positive number is LeanStral test Kendall `0.615`, which still clears the target.

### Raw No-Calibration Baseline

Source: `experiments/04_veribench_validation/results_exp41_honest_train_test/HONEST_TABLE.md`, Table 4.

These are the numbers to use when asking whether one fixed judge works without human calibration. They do not clear the desired `>= 0.6` item-level target.

| Model family | Best raw judge | n tasks/items | Spearman rho | Kendall tau | Pearson r | Task rho | Use |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| LeanStral | `labs-leanstral-2603|P1_BASELINE` | 20 / 60 | 0.426 | 0.325 | 0.417 | 0.544 | Best current raw fixed-judge candidate |
| GPT-4o-mini | `gpt-4o-mini|P1_BASELINE` | 20 / 60 | 0.266 | 0.212 | 0.285 | 0.345 | Raw baseline only |
| GPT-5.3 Codex | `gpt-5.3-codex|P20_TC_RATER_CARD` | 20 / 60 | -0.052 | -0.038 | -0.031 | -0.012 | Raw baseline only |
| Claude Opus 4.7 | `claude-opus-4-7|P1_BASELINE` | 20 / 60 | 0.203 | 0.140 | 0.244 | 0.324 | Raw baseline only |

### Transfer And Trust-Index Checks

These are the current best honesty checks for claims beyond per-task calibration.

| Check | Best current result | Source | Claim status |
| --- | --- | --- | --- |
| Global isotonic transfer with no test-task labels | Best test item rho is `0.295` for `gpt-4o-mini|P1_BASELINE`; LeanStral is `-0.084` | `experiments/04_veribench_validation/results_exp42_proper_transfer/PAPER_TABLE.md` | Does not support a `>= 0.6` held-out global-calibration claim |
| Raw five-human mean single metric | Best raw item/task rho is `0.422` / `0.541` for `labs-leanstral-2603|P1_BASELINE` | `experiments/04_veribench_validation/results_exp39_autometrics_autoti/REPORT.md` | Useful context; below the item-level target |
| Raw five-human z-score single metric | Best raw item/task rho is `0.426` / `0.544` for `labs-leanstral-2603|P1_BASELINE` | `experiments/04_veribench_validation/results_exp39_autometrics_autoti_zscore_mean/REPORT.md` | Best raw fixed-judge candidate; below the item-level target |
| Frozen TIvar held-out validation | Held-out rho ranges from `-0.333` to `0.119` across judge families | `experiments/04_veribench_validation/results_exp43_frozen_tivar_heldout/HELD_OUT_PAPER_TABLE.md` | Does not support a held-out trust-index trend claim |

### Bottom Line For Brando

The paper-positive current result is: per-task human-calibrated judge scores align strongly with five-human judgments across LeanStral, GPT-4o-mini, GPT-5.3 Codex, and Claude Opus 4.7. The honest limitation is: raw fixed judges and global held-out calibration do not yet reach the `>= 0.6` item-level target, so the requested one-fixed-judge-across-agent-CLIs result still needs a new per-agent run.

## Fixed Judge Candidate For Next Cross-Agent Run

Current candidate to freeze:

| Field | Value |
| --- | --- |
| Fixed judge ID | `labs-leanstral-2603|P1_BASELINE` |
| Judge model | `labs-leanstral-2603` |
| Prompt key | `P1_BASELINE` |
| Prompt path | `experiments/02_reviewer_response_neurips_math_ai_2026/utils/sensitivity_sweep.py` |
| Cached-score source / starting scorer | `experiments/04_veribench_validation/exp16_multi_judge_human_sets.py` |
| LLM caller | `experiments/02_reviewer_response_neurips_math_ai_2026/utils/judge_caller.py` |
| Existing cached run | `experiments/04_veribench_validation/results_exp16_leanstral_r3_median` |

Why this is still the next no-calibration candidate: it is the best raw single metric on both the five-human mean and five-human z-score targets (`0.422`-`0.426` item Spearman, `0.541`-`0.544` task Spearman). It does not yet clear the desired `0.6` item-level threshold.

Important implementation note: `experiments/04_veribench_validation/exp16_multi_judge_human_sets.py` is a useful cached-score/provenance source, but it does not produce this table as-is. It pools all candidate files into one row per judge and reports Spearman only. The real run needs a per-agent grouping/join script that uses manifests or candidate filenames, joins human labels, and computes Pearson/Spearman/Kendall per agent row.

## Future Cross-Agent Primary Result Table

Fill this table after real runs. Each row is one VeriBench-solving agent CLI/model pair.

| Agent row | Agent CLI | CLI version | Requested model | Observed model | n tasks | n items | Human target | Judge Pearson r | Judge Spearman rho | Judge Kendall tau | Row passes? | Artifact path |
| --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | --- | --- |
| `codex` | `codex` | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| `claude_code` | `claude` / `clauded` | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| `vibe_leanstral` | Mistral Vibe / LeanStral CLI | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| `gemini_cli` | `gemini` | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | Optional | TODO |
| `qwen_agent` | Qwen/Coder stack | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | Optional | TODO |

Per-row pass rule:

```text
Judge Pearson r >= 0.6
Judge Spearman rho >= 0.6
Judge Kendall tau >= 0.6
```

## Trust-Index Cross-Agent Table

Status: blocked until the experiment defines an agent-conditioned trust-index value. The existing `cert_index` / `cert_index_v2` in the legacy scorer are properties of the judge/prompt, not of an agent row. With one fixed judge, those values are constant across agent rows and cannot produce a meaningful Pearson/Spearman/Kendall trend.

Fill this only after the primary table exists and the trust-index definition is non-constant across agent rows. The vector being correlated should then be:

```text
x = agent-conditioned trust index per agent row
y = fixed-judge human-alignment score per agent row
```

Use the same `y` definition consistently, preferably agent-row Spearman or the mean of Pearson/Spearman/Kendall after verifying all three are reported.

| Human-alignment target | Pearson r(agent-TI, alignment) | Spearman rho(agent-TI, alignment) | Kendall tau(agent-TI, alignment) | n agent rows | Passes? |
| --- | ---: | ---: | ---: | ---: | --- |
| Judge Pearson by row | TODO | TODO | TODO | TODO | TODO |
| Judge Spearman by row | TODO | TODO | TODO | TODO | TODO |
| Judge Kendall by row | TODO | TODO | TODO | TODO | TODO |

Once a valid agent-conditioned trust-index definition exists, the cross-agent pass rule is:

```text
Pearson r(agent-TI, alignment) >= 0.6
Spearman rho(agent-TI, alignment) >= 0.6
Kendall tau(agent-TI, alignment) >= 0.6
```

## Paths Brando Needs

Core judge prompt/code:

- `experiments/02_reviewer_response_neurips_math_ai_2026/utils/sensitivity_sweep.py`
- `experiments/04_veribench_validation/exp16_multi_judge_human_sets.py`
- `experiments/02_reviewer_response_neurips_math_ai_2026/utils/judge_caller.py`

VeriBench agent/gold/human inputs:

- `data/generated_agents/`
- `data/veribench_dataset/lean_src/veribench/`
- `experiments/ethan_hand_labels/`
- `experiments/human_labels/`
- `experiments/04_veribench_validation/data/`
- `experiments/04_veribench_validation/run_veribench_validation.py`

Trust-index and calibration references:

- `experiments/04_veribench_validation/results_exp16_leanstral_r3_median/judge_rows.csv`
- `experiments/04_veribench_validation/results_exp38_five_human_per_task_isotonic/per_judge_metrics.csv`
- `experiments/04_veribench_validation/results_exp39_autometrics_autoti/REPORT.md`
- `experiments/04_veribench_validation/results_exp39_autometrics_autoti_zscore_mean/REPORT.md`
- `experiments/04_veribench_validation/results_exp41_honest_train_test/sweep_results.csv`
- `experiments/04_veribench_validation/exp28_variance_aware_trust_index.py`
- `experiments/04_veribench_validation/exp30_specialist_judge_task_split.py`
- `experiments/04_veribench_validation/exp40_train_test_calibration_sweep.py`
- `experiments/04_veribench_validation/exp43_frozen_tivar_heldout.py`
- `experiments/04_veribench_validation/results_exp41_honest_train_test/HONEST_TABLE.md`
- `experiments/04_veribench_validation/results_exp42_proper_transfer/PAPER_TABLE.md`
- `experiments/04_veribench_validation/results_exp42_proper_transfer/sweep_results.csv`
- `experiments/04_veribench_validation/results_exp43_frozen_tivar_heldout/HELD_OUT_PAPER_TABLE.md`

## Paper-Claim Guardrail

Do not write the cross-agent agent-CLI claim as solved until the TODO agent-row table above is filled from real runs. The completed positive result is per-task human-calibrated judge-human alignment; do not describe it as raw fixed-judge performance or held-out global generalization. If raw fixed-judge scores remain near the current `0.42` item / `0.54` task Spearman, report that as the limitation rather than upgrading it rhetorically.
