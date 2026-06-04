# Trust Index vs Human-Judge Correlation
**TLDR:** The old table was raw judge-human agreement for one LeanStral prompt; it was not the requested trust-index validation. The direct 3-by-3 readout from EXP30 shows that Codex clears the `0.6` meta-correlation target on pass1, pass2, and avg; Claude Code/Opus clears only pass2; LeanStral does not clear any split.

## Primary 3-by-3 Table

Each cell is `Spearman(ti_var_v3, human_spearman)` over the corresponding 8-row judge panel. This is the correlation between the trust index and the judge-human correlation. The desired threshold is `rho >= 0.6`.

| Judge family | Pass 1 | Pass 2 | Avg |
| --- | ---: | ---: | ---: |
| Codex (`gpt-5.3-codex`) | `0.762` PASS | `0.810` PASS | `0.762` PASS |
| Claude Code/Opus (`claude-opus-4-7`) | `0.405` FAIL | `0.643` PASS | `0.429` FAIL |
| LeanStral (`labs-leanstral-2603`) | `-0.667` FAIL | `0.167` FAIL | `-0.333` FAIL |

## Interpretation

Codex is the only family in this cached result where the trust index clears the `0.6` threshold across all three pass splits. Claude Code/Opus has one encouraging split, pass2, but the averaged result is only `0.429`, below the desired `0.6`. LeanStral is a mismatch for this trust-index criterion in EXP30 even though one LeanStral raw prompt has the strongest standalone human correlation elsewhere.

The table above is the one to use for the question: "does the trust index correlate with judge-human correlation for Codex, Claude Code/Opus, and LeanStral?"

## Source And Definition

- Source summary: `experiments/04_veribench_validation/results_exp30_tivar_v3_all_models/summary.json`
- Source vectors: `experiments/04_veribench_validation/results_exp30_tivar_v3_all_models/judge_trust_vector_<family>_<split>.csv`
- Trust index column: `ti_var_v3`
- Human-agreement column: `human_spearman`
- Correlation: Spearman rho computed across each 8-row panel
- Panel size: `n_judges = 8` for every family and split

The 8-row panels include the family-specific prompt rows plus shared anchor baselines. Therefore this is the EXP30 panel-level trust-index correlation, not a same-family-prompts-only correlation.

## What The Old Table Was

The previous table answered a different question. It showed raw judge-human agreement for the single LeanStral judge `labs-leanstral-2603|P1_BASELINE`, not the correlation between trust index and human agreement across judges.

| Target / analysis | Item Spearman | Task Spearman | Items | Tasks | Source |
| --- | ---: | ---: | ---: | ---: | --- |
| Five-human `mean` target | `0.422` | `0.541` | `60` | `20` | `experiments/04_veribench_validation/results_exp39_autometrics_autoti/REPORT.md` |
| Five-human `zscore_mean` target | `0.426` | `0.544` | `60` | `20` | `experiments/04_veribench_validation/results_exp39_autometrics_autoti_zscore_mean/REPORT.md` |
| All-human task aggregation | n/a | `0.510` | `72` | `24` | `experiments/04_veribench_validation/results_exp34_all_human_task_aggregation/REPORT.md` |

That old table is still useful for reporting the best standalone LeanStral judge-human agreement, but it should not be used as evidence that the trust index ranks judges correctly.

## Related Cross-Check

EXP34 computes the global all-human meta-correlation for `cert_index_v2` across 24 cached judge rows, without splitting by Codex/Claude/LeanStral family. Those global values are modest:

| Level | `cert_index_v2` vs judge-human Spearman |
| --- | ---: |
| Item | `0.263` |
| Task | `0.169` |

This cross-check points in the same direction: raw judge-human agreement and trust-index validation are distinct claims, and the trust-index validation is not uniformly strong across model families.
