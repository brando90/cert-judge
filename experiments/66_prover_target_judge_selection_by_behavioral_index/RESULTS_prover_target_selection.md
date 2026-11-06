# Experiment 66 results: behavioral-index selection of prover-agreeing judges

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/66_prover_target_judge_selection_by_behavioral_index/RESULTS_prover_target_selection.md>

**TLDR:** On a constructed target, experiment 42's fixed Lean reverse-implication procedure, the label-free index `C_ms_gold` tracks judge–prover agreement across 16 held-out language-model judge configurations: Spearman 0.705 [0.593, 0.880], one-sided permutation p 0.0016. Index selection lands within 0.0025 of the best configuration. The signal comes mostly from separating legacy and lexical prompts from VeriBench rubric prompts: within the 10 rubric-prompt configurations it is weak (0.170 [−0.327, 0.842]). Deterministic theorem-count controls reach the maximal index with only constant-level agreement. On 99 natural outputs with historical Lean outcomes, the index could not be tested across judges, a consensus signal did not select, and two provers rank the judges differently. Everything is retrospective; 0 model calls.

Protocol frozen at `e13b133` before any association was computed ([PROTOCOL.md](PROTOCOL.md)). Aggregates: [`results/r1_e42_target.json`](results/r1_e42_target.json), [`results/r2_natural_target.json`](results/r2_natural_target.json). Audit: [SOURCE_AUDIT.md](SOURCE_AUDIT.md).

## Definitions used below

- **Artifact:** one candidate file paired with its gold reference and original Python source.
- **`Y_P`:** the recorded binary outcome of the fixed proving procedure.
- **`G_P`:** 1 minus the Brier loss of a configuration's forecast against `Y_P`; higher is better. A constant forecast at the training rate is the floor that any useful judge must beat.
- **Fitted condition:** a logistic map from median judge score to probability, fitted on training tasks (R1) or by two-fold task cross-fitting (R2).
- **Raw condition:** the normalized score itself. It is shown separately because it is not an elicited probability.
- **Rank criterion:** area under the receiver operating characteristic curve (AUC) of score against `Y_P`.

## R1: constructed target (experiment 42's fixed Lean procedure)

**Scope.**
- 194 Lean-valid probes from 24 VeriBench references: identity 24 and formatting 38, all covered; weakening 57, over-constraint 37 and vacuity 38, all unproved.
- The score map is fitted on the 10 training tasks; `G_P` is computed on the 14 validation and test tasks, with 100% criterion coverage for every configuration.
- Judge families are judge models, following experiment 39's split.

| Pool and index (criterion `G_P`, fitted) | Configurations / models | Spearman [two-level 95%] | Pearson | Kendall | One-sided permutation p | Within-model p |
|---|---:|---:|---:|---:|---:|---:|
| **Test, `C_ms_gold` (primary)** | 16 / 4 | **0.705 [0.593, 0.880]** | 0.801 | 0.477 | **0.0016** | 0.0038 |
| Test, `C_ms_gold` from training-task ladders only | 17 / 4 | 0.731 [0.669, 0.960] | 0.824 | 0.526 | 0.0010 | 0.0040 |
| Test, `TI_var_trainnorm` | 18 / 4 | −0.148 [−0.737, 0.585] | 0.101 | −0.172 | 0.723 | 0.524 |
| Test, `PTI_v0_frozen` | 9 / 4 | 0.274 [0.085, 0.688] | 0.238 | 0.236 | 0.338 | 0.194 |
| Train + validation, `C_ms_gold` (descriptive) | 38 / 5 | 0.856 [0.654, 0.920] | 0.682 | 0.652 | <0.001 | <0.001 |
| All language-model configurations, `C_ms_gold` (descriptive) | 54 / 9 | 0.855 [0.716, 0.916] | 0.709 | 0.644 | <0.001 | <0.001 |

Two-level intervals resample judge models, then evaluation tasks, with 10,000 draws and the fitted maps held fixed. Permutation tests use 10,000 draws. `C_ms_gold` is missing for 2 test configurations (below experiment 39's coverage rule), and `PTI_v0_frozen` is missing for 9 because its candidate-side probes were too sparse.

**Selection on the test pool (16 configurations):**

| Rule | `G_P` |
|---|---:|
| Pick the highest `C_ms_gold` (`t2_sonnet5|D0`) | **0.904**, two-level 95% [0.886, 0.915] |
| Best configuration in the pool, a diagnostic oracle (`qwen36|H0`) | 0.907 |
| Regret, oracle minus pick | **0.0025** [0.000, 0.018] |
| Fixed H2 rubric, mean of its 3 configurations | 0.876 |
| Random configuration, pool mean | 0.859 |
| Constant forecast | 0.782 |
| Within-model regret, mean over 4 models | 0.0012 |

**Separately named and secondary analyses:**
- **Raw scores:** `C_ms_gold` versus raw-score `G_P`, Spearman 0.806 [0.665, 0.893]. The raw score beats the constant (0.782) for only 7 of 56 language-model configurations (picked 0.813). That is expected, because a raw 0–1 coverage score is not a calibrated probability.
- **Rank criterion:** Spearman 0.586, permutation p 0.011, two-level interval [−0.842, 0.764]. Eleven of 18 test configurations have AUC above 0.95, so the rank criterion has little room to vary at the top.
- **Prover agreement versus human agreement:** across all 56 language-model configurations, `G_P` and experiment 39's held-out human criterion correlate at Spearman 0.779 (Pearson 0.754, Kendall 0.565).

**Post hoc diagnostics (declared after seeing the primary result):**

| Pool | Configurations / models | Spearman [two-level 95%] | Permutation p | Within-model p | Selection |
|---|---:|---:|---:|---:|---|
| Test, VeriBench rubric prompts only (D0, H0, H1, H2, R4) | 10 / 4 | 0.170 [−0.327, 0.842] | 0.319 | 0.162 | pick 0.904, oracle 0.907, random 0.888 |
| All language-model configurations, rubric prompts only | 32 / 9 | 0.662 [0.068, 0.850] | <0.001 | 0.376 | regret 0.007 |
| All configurations including the 4 deterministic controls | 58 / 10 | 0.588 [0.032, 0.896] | <0.001 | <0.001 | **picks the theorem-count control: `G_P` 0.782 (constant level), regret 0.129** |

Reading:
- **Where the association comes from:** on held-out models it mostly separates legacy (P1, P4, P8) and lexical prompts, which score low on both index and agreement, from rubric prompts. Among rubric prompts, the remaining association is between models, not within them.
- **Why selection still works:** every held-out rubric configuration has `G_P` between 0.868 and 0.907. Avoiding legacy prompts is enough to pick near the top.
- **Where the index fails:** the theorem-count, name-overlap and edit-distance controls score `C_ms_gold = 1.0`, because deleting statements lowers their scores monotonically. Yet they cannot tell a weakened theorem from the original, so their prover agreement equals the constant's. The index therefore selects well only within a pool of language-model judges.

**Secondary file-level audit target:** with redundant weakenings and over-constraints counted as covered, the same fitted forecasts score 0.71 to 0.82 across language-model configurations, against 0.69 for the controls. The theorem-level procedure and the file-level reading disagree on 47 probes.

## R2: natural outputs with historical Lean entailment outcomes

**Scope.**
- 99 VeriBench experiment 106 v5 artifacts (Claude Code + Opus 5: 50; Codex + GPT-5.6 Sol: 49; 50 tasks), joined by exact candidate sha256.
- 95 have a first-pass outcome and 60 of those are accepted (Tiny-256 36/20, Core-614 59/40).
- 26 of 32 configurations meet the 90% coverage rule; the 6 Grok and Qwen frames below it are reported as not computable.
- The constant forecast gives `G_P` 0.743.

| Configuration (selected rows; all 26 in the JSON) | Family | `G_P` cross-fitted | AUC vs main prover | AUC vs Gemini prover (36 Tiny-256) | Consensus signal |
|---|---|---:|---:|---:|---:|
| Frozen H0 judge, GPT-6 Sol high | OpenAI | **0.819** | 0.820 | 0.760 | 0.644 |
| Simulated rater GPT-6 Astra, frame P3 | OpenAI | 0.802 | 0.797 | 0.760 | 0.707 |
| Frozen H2 judge, GPT-6 Sol high | OpenAI | 0.790 | 0.762 | 0.780 | 0.770 |
| Frozen H2 judge, Claude Opus 5.5 max | Anthropic | 0.781 | 0.753 | 0.780 | 0.807 |
| Frozen H0 judge, Claude Opus 5.5 max | Anthropic | 0.776 | 0.725 | **0.860** | **0.871** |
| Simulated rater Kimi K3, frame C0 | Moonshot | 0.752 | 0.626 | 0.760 | 0.696 |

- **Artifact level:** every computable configuration beats the constant, but only by 0.009 to 0.076.
- **Label-free selection, consensus signal:** agreement with judges from other model families. Spearman with `G_P` is −0.213 [−0.718, 0.875] (Pearson −0.427, Kendall −0.089, one-sided permutation p 0.85). It picks the Opus H0 judge (`G_P` 0.776), against 0.819 for the best, 0.779 for a random pick and 0.785 for the fixed H2 rubric; regret 0.043 [0.000, 0.061].
- **`C_ms_gold` on the 4 configurations that share model, effort and prompt with experiment 39 units** (descriptive; fewer than 8 units, so no correlation):

| Configuration | `C_ms_gold` | `G_P` |
|---|---:|---:|
| GPT-6 Sol high, H0 | 0.961 | 0.819 |
| GPT-6 Sol high, H2 | 0.978 | 0.790 |
| Claude Opus 5.5 max, H2 | 0.994 | 0.781 |
| Claude Opus 5.5 max, H0 | 0.991 | 0.776 |

  In this small set the order is reversed.
- **Prover dependence (post hoc):** on the same 36 Tiny-256 outputs, judge rankings by AUC against the main prover and against the Gemini prover correlate at Spearman −0.126. Mean AUC is 0.689 against the main prover and 0.782 against the Gemini prover, and the two provers disagree on 15 of 36 outcomes. Which prover is "fixed" changes which judge looks best.

## Predictions versus observations

| Prediction (protocol `e13b133`) | Observed |
|---|---|
| R1 constant `G_P` about 0.78 | 0.782 |
| R1 best configurations above 0.9 | 0.904–0.911 for the best five |
| R1 primary Spearman 0.3–0.7, wide interval | 0.705 [0.593, 0.880], at the top of the range |
| R1 within-family association weaker | Within-model permutation p 0.0038 (strong); but within rubric prompts the association is weak (post hoc) |
| R1 regret under 0.05, pick above fixed H2 | 0.0025; pick 0.904 versus H2 0.876 |
| R1 theorem-count control near or below constant | Equal to constant (0.782), with maximal `C_ms_gold` |
| R1 `PTI_v0`, `TI_var` weaker | `TI_var` −0.148, `PTI_v0` 0.274 (n 9) |
| R2 H2/H0 judges 0.80–0.88 versus constant about 0.77 | 0.776–0.819 versus 0.743; slightly below the predicted band |
| R2 consensus signal positive, 0.2–0.6 | −0.213; prediction failed |
| R2 provers disagree substantially | 15/36 disagreements; judge rankings unrelated across provers |

## Deviations

1. **Rank-criterion bootstrap (R1, code fix after the first run).** The first run's bootstrap for the rank criterion recomputed Brier-based `G_P` instead of AUC. It was fixed and rerun; Brier-based results are unchanged.
2. **Post hoc pools (R1).** Rubric-only pools and a pool including the controls were added after the primary result and are labeled as diagnostics.
3. **Coverage guard (R2, code).** Configurations below the coverage rule now return not computable instead of dividing by zero; no definition changed.
4. **Cross-prover comparison (R2, post hoc).**

## What is supported

- **Supported, retrospectively:**
  - On a constructed, theorem-level fixed-procedure target, cert-judge's frozen `C_ms_gold` predicts which held-out language-model judge configurations agree with the prover, and selecting by it gives near-oracle prover agreement.
  - The evidence that it ranks judges *within* the competitive rubric prompts is weak.
  - It does not hold once deterministic controls are in the pool.
- **Not supported or not tested:** natural-output validity of index selection (not testable across these judges); a fresh, validated target (none exists); semantic file-level coverage; human agreement (a separate criterion, though prover and human agreement correlate at 0.78 across these judges).
- **Next:** the prepared [P1](PROSPECTIVE_P1.md) run of 117 open-weight configurations, which already have frozen `C_ms_gold` values, on a validated fresh target. That is the test R2 could not perform.

**TLDR-end:** [cj: experiments/66_prover_target_judge_selection_by_behavioral_index] `C_ms_gold` selects prover-agreeing judges on a constructed fixed-procedure target (Spearman 0.705, regret 0.0025), mainly by screening out weak prompts, and is fooled by deterministic controls. On natural outputs the index could not be tested and the prover choice reorders judges.
