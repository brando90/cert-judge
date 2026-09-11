# cert-judge experiments — live work for the paper rewrite

**TLDR:** `experiments/` holds only active work. Experiments `00_`–`26_` that are not OpenReview, Leanstral, Total Variation Distance Mutual Information (TVD-MI), or Epistemically and Formally Grounded (EFG) live under [`archive/`](archive/README.md). Start with the OpenReview folders; 27 and 29 stay live because they are the current plot and Proxy Trust Index version 0 (PTI-v0) CLI, not leftover 00–26 campaigns.

## Keepers (do not archive)

These are the 00–26-range folders that stay live through the rewrite, plus shared labels:

| Folder | Why it stays |
|---|---|
| [`02_reviewer_response_neurips_math_ai_2026/`](02_reviewer_response_neurips_math_ai_2026/) | NeurIPS Math-AI 2026 reviewer-response packet |
| [`18_open_revievew_feedback_ICML_2026_mathai_ws/`](18_open_revievew_feedback_ICML_2026_mathai_ws/) | ICML 2026 AI4Math OpenReview (OR) feedback (folder name misspelled; do not rename without rewriting pointers) |
| [`12_leanstral_replication_exp16_exp19/`](12_leanstral_replication_exp16_exp19/) | Leanstral replication of Exp16 / Exp19 / Exp22 |
| [`03_tvdmi_elicitation_crossover/`](03_tvdmi_elicitation_crossover/) | TVD-MI elicitation vs direct scoring (offline) |
| [`04_efg_baseline/`](04_efg_baseline/) | EFG judge baseline (Zhang, Valentino & Freitas, arXiv:2506.10903) vs human labels |
| [`ethan_hand_labels/`](ethan_hand_labels/), [`human_labels/`](human_labels/) | Shared label data used by EFG, plots, and PTI-v0 |

## Supporting live work (outside 00–26)

| Folder | Why it stays |
|---|---|
| [`27_ti_plot_like_scatter_plots/`](27_ti_plot_like_scatter_plots/) | Trust Index 2-prime (`TI_2'`) scatter figures for the ICLR 2027 manuscript; reads archived Exp06/Exp26 artifacts |
| [`29_pti_v0_cli_bridge/`](29_pti_v0_cli_bridge/) | Live CLI-only PTI-v0 scorer and accepted v5 run; calls [`archive/04_veribench_validation/run_pti_v0.py`](archive/04_veribench_validation/run_pti_v0.py) |
| [`30_pti_ti_criterion_validity/`](30_pti_ti_criterion_validity/) | Does PTI-v0 predict the human-grounded Trust Index (`TI_m`)? Label-reliability ceiling, resolving power, and held-out-family splits; numerics in `py_src/cert_judge/ti_validation.py` |

Zero-spend PTI-v0 entry point:

```bash
python experiments/archive/04_veribench_validation/run_pti_v0.py --help
python experiments/29_pti_v0_cli_bridge/run_pti_v0_cli.py --help
python experiments/30_pti_ti_criterion_validity/design_check.py --demo
```

Paid judge inference still needs an exact quote and explicit approval.

## Archive

Finished 00–26 campaigns, including the frozen PTI-v0 v4 runner, are in [`archive/`](archive/README.md). Do not start new results from there. The reusable numerics remain in `py_src/cert_judge/pti_v0.py`.
