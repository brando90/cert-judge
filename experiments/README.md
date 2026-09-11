# Experiments

**TLDR:** Start here for the paper rewrite: reviewer feedback, retained baselines, trust plots, and proxy validation. Folder names are short; the table explains each purpose, and completed historical work lives in [`archive/`](archive/README.md).

| Folder | Purpose |
|---|---|
| [`02_neurips_reviews/`](02_neurips_reviews/) | Neural Information Processing Systems (NeurIPS) Math-AI 2026 reviewer feedback and response experiments. |
| [`03_tvdmi/`](03_tvdmi/) | Total Variation Distance–Mutual Information (TVD-MI): compare information-based elicitation with direct scoring. |
| [`04_efg_baseline/`](04_efg_baseline/) | Epistemically and Formally Grounded (EFG) judge baseline against human labels. |
| [`12_leanstral/`](12_leanstral/) | Leanstral replication: judge agreement with humans and repeated-score stability. |
| [`18_icml_reviews/`](18_icml_reviews/) | International Conference on Machine Learning (ICML) AI4Math 2026 OpenReview feedback. |
| [`27_trust_plots/`](27_trust_plots/) | Manuscript figures of human agreement and repeated-score stability. |
| [`29_proxy_validation/`](29_proxy_validation/) | Completed Proxy Trust Index version 0 (PTI-v0) validation against human agreement, with the scoring runner and frozen results. |
| [`ethan_hand_labels/`](ethan_hand_labels/), [`human_labels/`](human_labels/) | Shared human-label data. |
| [`archive/`](archive/README.md) | Earlier experiments and the folder-rename history. |

## Run or inspect

Entry points that display help without model inference:

```bash
python experiments/archive/04_veribench_validation/run_pti_v0.py --help
python experiments/29_proxy_validation/run_pti_v0_cli.py --help
```

The retained runner imports the frozen predecessor from the archive. Reusable
metric calculations live in `py_src/cert_judge/pti_v0.py`; historical result files
keep their original provenance paths. Paid judge inference still requires an
exact quote and explicit approval.
