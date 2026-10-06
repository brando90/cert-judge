# Cached-score judge selection utility results

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/44_cached_score_judge_selection_utility/RESULTS_selection_utility.md>

**TLDR:** Proxy selection has not demonstrated a gain over the fixed human-rating rubric among comparable judges; the original registered association is preserved.

**Status:** COMPLETE — exploratory cached-score analysis, no inference or new labels.

H2 denotes the fixed prompt that mirrors the human-rating rubric, with conventions and demonstrations. The H2 selector chooses uniformly among four individual configurations; it is not an ensemble. The primary pool has 12 configurations from three underlying model families, with single-call and agent variants.

## Practical decision

On the primary 12-configuration, 42-file/15-task common-support comparison, the frozen deletion-monotonicity proxy did not demonstrate an advantage over fixed H2: proxy minus H2 Spearman was -0.086, with a paired 95% task-cluster percentile interval [-0.308, 0.058] across 10,000 draws (p-val=n/a). The proxy's point estimate was lower and the interval crossed zero. This exploratory follow-up therefore preserves the original registered result rather than replacing it; label-free deployment remains unproven.

## Primary full-context pool / original 45-item view

| Selector | Expected Spearman / Pearson / Kendall | Spearman 95% interval | Selected configurations | Margin | Regret (95% interval) |
|---|---:|---:|---|---:|---:|
| proxy_C_ms_gold | 0.768 / 0.816 / 0.620 | [0.401, 0.930] (10000) | t2_sonnet5\|D0 | 0.001 | 0.104 [0.008, 0.379] |
| identity_C_ident | 0.784 / 0.769 / 0.662 | [0.528, 0.892] (10000) | opus55x\|D0, opus55x\|H0, opus55x\|H2, qwen36\|D0, qwen36\|H0, qwen36\|H1, qwen36\|H2, qwen36\|R4, t2_qwen\|D0, t2_qwen\|H2, t2_sonnet5\|D0, t2_sonnet5\|H2 | 0.000 | 0.087 [0.047, 0.238] |
| human_mirror_H2 | 0.853 / 0.836 / 0.740 | [0.645, 0.931] (10000) | opus55x\|H2, qwen36\|H2, t2_qwen\|H2, t2_sonnet5\|H2 | n/a | 0.018 [0.009, 0.116] |
| random | 0.784 / 0.769 / 0.662 | [0.528, 0.892] (10000) | opus55x\|D0, opus55x\|H0, opus55x\|H2, qwen36\|D0, qwen36\|H0, qwen36\|H1, qwen36\|H2, qwen36\|R4, t2_qwen\|D0, t2_qwen\|H2, t2_sonnet5\|D0, t2_sonnet5\|H2 | n/a | 0.087 [0.047, 0.238] |
| transferred_prompt | 0.853 / 0.836 / 0.740 | [0.645, 0.931] (10000) | opus55x\|H2, qwen36\|H2, t2_qwen\|H2, t2_sonnet5\|H2 | n/a | 0.018 [0.009, 0.116] |

Proxy − H2: -0.086 [95% -0.308, 0.058; valid task draws=10000; p-val=n/a].

Proxy − random: -0.017 [95% -0.162, 0.080; valid task draws=10000; p-val=n/a].

## Pool/view summary

| Pool | View | Shared items/tasks | Proxy | H2 | Random | Proxy − H2 |
|---|---|---:|---:|---:|---:|---:|
| primary_full_context | original45 | 42/15 | 0.768 | 0.853 | 0.784 | -0.086 |
| primary_full_context | no_placeholder36 | 33/12 | 0.525 | 0.702 | 0.602 | -0.177 |
| primary_full_context | no_ambiguity36 | 34/12 | 0.845 | 0.898 | 0.838 | -0.053 |
| primary_full_context | neither27 | 25/9 | 0.625 | 0.762 | 0.665 | -0.137 |
| primary_full_context | test_only30 | 29/10 | 0.798 | 0.848 | 0.778 | -0.050 |
| same_H2 | original45 | 45/15 | 0.837 | 0.847 | 0.847 | -0.010 |
| same_H2 | no_placeholder36 | 36/12 | 0.673 | 0.704 | 0.704 | -0.030 |
| same_H2 | no_ambiguity36 | 36/12 | 0.873 | 0.891 | 0.891 | -0.019 |
| same_H2 | neither27 | 27/9 | 0.706 | 0.756 | 0.756 | -0.051 |
| same_H2 | test_only30 | 30/10 | 0.854 | 0.856 | 0.856 | -0.002 |
| broad | original45 | 41/15 | 0.787 | 0.868 | 0.586 | -0.081 |
| broad | no_placeholder36 | 32/12 | n/a | n/a | n/a | n/a |
| broad | no_ambiguity36 | 33/12 | 0.859 | 0.907 | 0.643 | -0.048 |
| broad | neither27 | 24/9 | n/a | n/a | n/a | n/a |
| broad | test_only30 | 28/10 | 0.824 | 0.871 | 0.585 | -0.047 |

## Frozen transferred prompt

```json
{
  "train": [
    {
      "prompt": "D0",
      "mean_spearman": 0.5699855014255655,
      "n_configs": 2,
      "configs": [
        "sol6h|D0",
        "sonnet5m|D0"
      ]
    },
    {
      "prompt": "H0",
      "mean_spearman": 0.6058246792046529,
      "n_configs": 2,
      "configs": [
        "sol6h|H0",
        "sonnet5m|H0"
      ]
    },
    {
      "prompt": "H1",
      "mean_spearman": 0.7945343529018559,
      "n_configs": 2,
      "configs": [
        "sol6h|H1",
        "sonnet5m|H1"
      ]
    },
    {
      "prompt": "H2",
      "mean_spearman": 0.7968912718674801,
      "n_configs": 2,
      "configs": [
        "sol6h|H2",
        "sonnet5m|H2"
      ]
    },
    {
      "prompt": "LEX",
      "mean_spearman": -0.16031009633678558,
      "n_configs": 2,
      "configs": [
        "sol6h|LEX",
        "sonnet5m|LEX"
      ]
    },
    {
      "prompt": "P1",
      "mean_spearman": 0.053715958822775425,
      "n_configs": 2,
      "configs": [
        "sol6h|P1",
        "sonnet5m|P1"
      ]
    },
    {
      "prompt": "P4",
      "mean_spearman": 0.07498973204389654,
      "n_configs": 2,
      "configs": [
        "sol6h|P4",
        "sonnet5m|P4"
      ]
    },
    {
      "prompt": "P8",
      "mean_spearman": -0.10293861442092418,
      "n_configs": 2,
      "configs": [
        "sol6h|P8",
        "sonnet5m|P8"
      ]
    },
    {
      "prompt": "R4",
      "mean_spearman": 0.6447288301690133,
      "n_configs": 2,
      "configs": [
        "sol6h|R4",
        "sonnet5m|R4"
      ]
    }
  ],
  "retained_top3": [
    {
      "prompt": "H2",
      "mean_spearman": 0.7968912718674801,
      "n_configs": 2,
      "configs": [
        "sol6h|H2",
        "sonnet5m|H2"
      ]
    },
    {
      "prompt": "H1",
      "mean_spearman": 0.7945343529018559,
      "n_configs": 2,
      "configs": [
        "sol6h|H1",
        "sonnet5m|H1"
      ]
    },
    {
      "prompt": "R4",
      "mean_spearman": 0.6447288301690133,
      "n_configs": 2,
      "configs": [
        "sol6h|R4",
        "sonnet5m|R4"
      ]
    }
  ],
  "validation": [
    {
      "prompt": "H2",
      "mean_spearman": 0.8349845945425787,
      "n_configs": 3,
      "configs": [
        "gem31h|H2",
        "luna6h|H2",
        "t2_luna|H2"
      ]
    },
    {
      "prompt": "H1",
      "mean_spearman": 0.8119151970713432,
      "n_configs": 2,
      "configs": [
        "gem31h|H1",
        "luna6h|H1"
      ]
    },
    {
      "prompt": "R4",
      "mean_spearman": 0.7336582025277594,
      "n_configs": 2,
      "configs": [
        "gem31h|R4",
        "luna6h|R4"
      ]
    }
  ],
  "chosen_prompt": "H2"
}
```

## Sensitivities and next priority

All declared criterion views, proxy-eligible fixed-mask comparisons, leave-one-base-model-out summaries, and single-call/agent-only summaries are in `results/selector_table.json` and `results/sensitivity.json`; unavailable broad-pool cells remain explicit rather than dropped. The next priority is a prospective confirmation with new raters under the same frozen rubric and a frozen proxy, rather than further tuning on this reused panel.

## Verification and limitations

- Reconstructed every source test configuration's original-mask Spearman, Pearson, and Kendall statistic and the original pooled TEST_RECEIPT association from final-status measured/deterministic cached scores and median repeats before utility computation.
- The 10,000 paired bootstrap draws resample tasks (retaining repeated task rows) and hold candidates, proxy values, and selectors fixed. Positive-weight members with undefined correlation make that selector draw undefined; pairwise contrasts use each pair's shared finite draws.
- All reported p-values are `n/a`; no inferential threshold was imposed. Missing proxy values exclude only the proxy selector and are retained in random, H2, and oracle comparisons. The small, non-independent set of base models, reused human panel, and fixed-candidate conditional bootstrap limit generalization.


## Additional primary diagnostics

Intervals below use the same paired task draws; complete counts and all sensitivity intervals are in [the machine-readable receipt](results/SUMMARY_RECEIPT.json).

| Selector | Pearson 95% interval | Kendall 95% interval | Mean absolute error | Mean bias | Judge / human means | Observed repeats per member |
|---|---:|---:|---:|---:|---:|---:|
| proxy_C_ms_gold | [0.537, 0.936] | [0.304, 0.829] | 0.154 | -0.010 | 0.493 / 0.502 | 126–126 of 126 |
| identity_C_ident | [0.603, 0.860] | [0.440, 0.791] | 0.190 | 0.097 | 0.600 / 0.502 | 115–126 of 126 |
| human_mirror_H2 | [0.712, 0.909] | [0.551, 0.843] | 0.173 | 0.120 | 0.623 / 0.502 | 115–126 of 126 |
| random | [0.603, 0.860] | [0.440, 0.791] | 0.190 | 0.097 | 0.600 / 0.502 | 115–126 of 126 |
| transferred_prompt | [0.712, 0.909] | [0.551, 0.843] | 0.173 | 0.120 | 0.623 / 0.502 | 115–126 of 126 |

Score-level diagnostics use the same common items and normalized [0,1] scale. Bias is judge minus human (positive means lenient); these diagnostic point estimates do not determine selection. The [repeat diagnostics](results/repeat_diagnostics.json) record raw-repeat sample standard deviations, unavailable values, and missing slots, separately from median-score agreement.

**TLDR-end:** [cert-judge: 44_cached_score_judge_selection_utility] This completed exploratory cached-score study measures frozen-proxy selection utility with task-cluster uncertainty and preserves all declared support and missingness rules.
