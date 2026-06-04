# Fixed Judge Across Agents Results
**TLDR:** No new cross-agent result has been generated yet. This file states the sign-off target Brando wants: one frozen judge, applied to multiple VeriBench-solving agent CLI/model rows, with per-agent judge-human agreement clearing approximately `0.6` under Pearson, Spearman, and Kendall. The requested trust-index correlation remains a definition gap until the experiment adds an agent-conditioned trust-index value; the existing cert index is per judge and would be constant for one fixed judge.

## Sign-Off Summary

Brando wants a TMLR-ready result where one fixed judge works across as many agent families as possible. "Works" means two things:

1. For each agent row, the fixed judge's scores correlate strongly with human judgments.
2. If an agent-conditioned trust index is defined, that trust-index value correlates strongly with the fixed judge's human agreement across agent rows.

The target threshold is approximately `0.6` for each correlation metric: Pearson `r`, Spearman `rho`, and Kendall `tau`. Higher is better, and more agent rows are better. Treat 3 agent rows as a smoke panel; use 5 or more rows with uncertainty estimates for a paper-facing cross-agent trend claim.

## Fixed Judge

Current candidate to freeze:

| Field | Value |
| --- | --- |
| Fixed judge ID | `labs-leanstral-2603|P1_BASELINE` |
| Judge model | `labs-leanstral-2603` |
| Prompt key | `P1_BASELINE` |
| Prompt path | `experiments/02_reviewer_response_neurips_math_ai_2026/utils/sensitivity_sweep.py` |
| Scoring code | `experiments/04_veribench_validation/exp16_multi_judge_human_sets.py` |
| LLM caller | `experiments/02_reviewer_response_neurips_math_ai_2026/utils/judge_caller.py` |
| Existing cached run | `experiments/04_veribench_validation/results_exp16_leanstral_r3_median` |

Existing reference numbers for this judge are useful context, not the final cross-agent result:

| Existing analysis | Target/regime | n items | Item Spearman | Task Spearman | Source |
| --- | --- | ---: | ---: | ---: | --- |
| Exp39 raw single metric | five-human `mean` target | `60` | `0.422` | `0.541` | `experiments/04_veribench_validation/results_exp39_autometrics_autoti/REPORT.md` |
| Exp39 z-score raw single metric | five-human z-score target | `60` | `0.426` | `0.544` | `experiments/04_veribench_validation/results_exp39_autometrics_autoti_zscore_mean/REPORT.md` |
| Exp41 raw full-panel baseline | raw table copied from z-score/held-out sweep | `60` | `0.426` | `0.544` | `experiments/04_veribench_validation/results_exp41_honest_train_test/HONEST_TABLE.md` |
| Exp16 cached row | pass1/pass2/avg label sets, pooled candidate rows | `72` | `0.0405` avg human Spearman | N/A | `experiments/04_veribench_validation/results_exp16_leanstral_r3_median/summary.json` |

These are below the desired `0.6` item-level threshold, so the final experiment should either improve the target construction/agent panel honestly or report the limitation.

Important implementation note: `experiments/04_veribench_validation/exp16_multi_judge_human_sets.py` is a useful cached-score/provenance source, but it does not produce this table as-is. It pools all candidate files into one row per judge and reports Spearman only. The real run needs a per-agent grouping/join script that uses manifests or candidate filenames, joins human labels, and computes Pearson/Spearman/Kendall per agent row.

## Primary Result Table

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

- `experiments/04_veribench_validation/exp28_variance_aware_trust_index.py`
- `experiments/04_veribench_validation/exp30_specialist_judge_task_split.py`
- `experiments/04_veribench_validation/exp40_train_test_calibration_sweep.py`
- `experiments/04_veribench_validation/exp43_frozen_tivar_heldout.py`
- `experiments/04_veribench_validation/results_exp41_honest_train_test/HONEST_TABLE.md`
- `experiments/04_veribench_validation/results_exp42_proper_transfer/PAPER_TABLE.md`
- `experiments/04_veribench_validation/results_exp43_frozen_tivar_heldout/HELD_OUT_PAPER_TABLE.md`

## Paper-Claim Guardrail

Do not write the TMLR claim as solved until the TODO tables above are filled from real runs. If only the per-task calibrated/oracle results clear `0.6`, label them as calibrated capacity, not held-out generalization. If raw fixed-judge scores remain near the current `0.42` item / `0.54` task Spearman, report that as the limitation rather than upgrading it rhetorically.
