# Autojudge Human Correlation Val/Test Report
**TLDR:** A validation-only prompt-selection procedure selects Codex `P7_STRICT_A` test Spearman -0.237, Opus `P1_BASELINE` test Spearman 0.254, Leanstral `P1_BASELINE` test Spearman 0.268 under the frozen split. Codex does not generalize on this split; Opus and Leanstral are weakly positive with bootstrap intervals crossing zero.

## Result

| Family | Selected judge | Train Spearman | Test Spearman | Test 95% boot CI | n train | n test |
|:---|:---|---:|---:|:---|---:|---:|
| Codex | `gpt-5.3-codex|P7_STRICT_A` | 0.189 | -0.237 | [-0.548, 0.095] | 36 | 36 |
| Opus | `claude-opus-4-7|P1_BASELINE` | 0.280 | 0.254 | [-0.115, 0.559] | 36 | 36 |
| Leanstral | `labs-leanstral-2603|P1_BASELINE` | 0.346 | 0.268 | [-0.073, 0.556] | 36 | 36 |

## Protocol

- Human target: raw mean over five participant files plus Ethan pass1 and Ethan pass2, with Ethan's two passes intentionally counted as two label sources.
- Split: fixed SHA256 task split with salt `cert-judge-exp17-autojudge-val-test-v1`; all candidates for a `gold_file` stay in the same split.
- Train split: 12 tasks / 36 candidate pairs.
- Test split: 12 tasks / 36 candidate pairs.
- Selection rule: within each family, choose the eligible prompt with the highest train Spearman against the aggregate human target; break exact ties by lexicographic `judge_id`.
- Eligible primary candidates: saved `kind=llm` judges for the target family only. Explicit `llm_bad`, edit-distance, random, and other-family controls are excluded from primary selection.
- AutoMetrics relation: this is an AutoMetrics-style low-data selector over an existing metric/prompt bank, not a full reimplementation with new generated criteria or regression composition. AutoMetrics is the motivating paper: [https://arxiv.org/abs/2512.17267](https://arxiv.org/abs/2512.17267).

## Exact Commands

```bash
cd /Users/brandomiranda/cert-judge-autojudge-human-corr-val-test
python experiments/17_autojudge_human_corr_val_test/run_autojudge_val_test.py \
  --out-dir experiments/17_autojudge_human_corr_val_test/results
```

## Label And Coverage

- Label sources found: 7 files.
- Nonblank ratings loaded: 496.
- Unique labeled pairs before score coverage filtering: 90.
- Exact pairs scored by every primary candidate: 72.
- Human-labeled pairs excluded for missing saved judge scores: 18.

## Caveats

- The primary analysis uses exact gold_file::candidate_file matches only; 18 aggregated human-labeled pairs lack saved scores from every primary family and are excluded rather than newly judged.
- The split is held out by problem, but rows within a problem share the same gold file; bootstrap intervals over pair rows therefore understate uncertainty if task-level dependence dominates.
- This is prompt selection over saved judge outputs, not a full AutoMetrics implementation with newly generated evaluator criteria or regression-composed metrics.
- The candidate pool is not identical across families: Codex has 7 eligible prompts; Opus has 3 eligible prompts; Leanstral has 3 eligible prompts.
- The human target is an aggregate of ordinal 0-5 labels; Spearman uses rank information and does not model rater-specific reliability.

## Outputs

- `results/selection_table.csv`: selected family-level train/test table.
- `results/all_candidate_correlations.csv`: every eligible prompt correlation before selection.
- `results/frozen_split.csv`: task-level train/test assignment.
- `results/pair_label_aggregates.csv`: seven-source human label aggregate.
- `results/missing_pairs.csv`: human-labeled pairs excluded from primary exact-score analysis.
- `results/summary.json`: machine-readable run metadata and selected rows.

## Paper Patch Decision

No paper text was patched in this PR. The result is a new prompt-selection diagnostic over the existing saved judge panel, not a held-out test of the paper's variance-aware trust index. Current paper drafts already separate validation-set evidence from held-out generalization, and this result is too caveated for a clean main-text claim without reviewer discussion.
