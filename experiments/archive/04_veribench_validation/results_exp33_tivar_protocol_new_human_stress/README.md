# EXP33 TI-var Protocol and New-Human Stress Test
**TLDR:** This run restores the Figure-3-style TI_var judge-selection protocol on the legacy aligned panel, then evaluates the same TI_var scores on the larger new-human panel as a held-out stress test. The legacy aligned panel supports the high judge-level correlations; the expanded new-human panel does not, so the isotonic oracle is kept as an appendix-only diagnostic.

## What changed
- Uses `TI_var` from EXP30 rather than the quick EXP32 optimized CertJudge index.
- Reports separate model-family panels instead of pooling heterogeneous judges.
- Expands the new-human held-out target from 15 test items to 72 overlapping items.
- Keeps test-set isotonic oracle artifacts in `appendix_isotonic_oracle/`.

## Legacy aligned-panel TI_var correlations
- `claude_opus` avg labels: Spearman=0.429, Pearson=0.608, n_judges=8.
- `codex` avg labels: Spearman=0.762, Pearson=0.811, n_judges=8.
- `qwen` avg labels: Spearman=0.667, Pearson=0.572, n_judges=8.

## Expanded new-human held-out stress test
These correlations are not headline-ready; they are the larger held-out check requested after EXP32.
- `claude_opus` item-level avg: Spearman=0.262, Pearson=0.052, n_items=72.
- `codex` item-level avg: Spearman=-0.071, Pearson=-0.312, n_items=72.
- `leanstral` item-level avg: Spearman=-0.143, Pearson=0.068, n_items=72.
- `qwen` item-level avg: Spearman=-0.310, Pearson=-0.485, n_items=72.

## Outputs
- `legacy_tivar_family_label_summary.csv`
- `expanded_new_human_tivar_summary.csv`
- `expanded_new_human_judge_alignment.csv`
- `new_human_rater_diagnostics.csv`
- `fig_legacy_tivar_avg_fig3_style.{png,pdf}`
- `fig_expanded_new_human_tivar_item_fig3_style.{png,pdf}`
- `appendix_isotonic_oracle/`
