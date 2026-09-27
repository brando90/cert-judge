# Experiment 39: selection bias from choosing the best of K judges on the 72-pair validation set

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/39_best_of_k_judge_selection_bias_validation_set/README.md>

**TLDR:** The introduction says that selecting many judge configurations against the same labels risks adaptive overfitting, but gives no magnitude. This experiment measures that magnitude on the paper's own 72-pair validation set, using only frozen judge scores and labels (no inference): how much the apparent human agreement of the best of K configurations overstates its agreement on unseen problems, and whether choosing by a label-free property statistic avoids the overstatement. It implements item 35.3 of `experiments/35_missing_experiments_from_reviews/EXPERIMENTS.md`.

**Outcome (09-26-2026, complete):** choosing the best of 8 configurations on 12 problems overstates its Spearman agreement on the other 12 by 0.15; a simulation fitted to the panel puts it at about 0.10 on all 72 pairs. With permuted labels, the best of 8 still shows 0.15. Adjusting for the choice among the four reported index forms multiplies the judge-level p-values by 1.9–3.2 (4 of 9 cells below 0.05 instead of 6). Choosing by the label-free v1 index is unbiased but no better than a random pick. Details and drafted paper text: [REPORT.md](REPORT.md).

## Question and decision

**Consequential uncertainty.** The paper's validation-set correlations are called optimistic because the same labels chose the index form, repeat aggregation, threshold and prompt panel. Nobody has measured how optimistic. If best-of-K selection on 72 pairs inflates agreement by only a few hundredths, the adaptive-overfitting sentence overstates a small effect; if it inflates agreement by amounts comparable to the gaps between the judges we compare (0.365–0.466 for the three semantic Codex prompts), the sentence deserves a number, and the argument for label-free screening becomes quantitative.

**Decision it informs.** Whether the introduction (and Section 5.1's "correlations on it are optimistic") can carry a measured magnitude, and which one. The pre-registered rules are in [PROTOCOL.md](PROTOCOL.md).

## Inputs (frozen, read-only)

- Labels: the three exp16 label files under `experiments/archive/04_veribench_validation/data/` (pass1 `ethan_human_scores_20260425.tsv`, pass2 `ethan_human_scores_ORIGINAL.tsv`, averaged `ethan_human_scores_avg_two_passes_20260425.tsv`); 72 analyzed pairs from 24 problems.
- Judge scores: every frozen exp16-format `detail_rows.csv` under `experiments/archive/` that scores the same 72 pairs, with its sibling `judge_rows.csv` for the label-free `cert_index`. The pool rule is fixed in the protocol.
- Judge-level vectors (analysis D): `results_exp28_varaware_*/judge_trust_vector.csv`, the exp16 `judge_rows.csv` files, and the exp22/exp25 geometric-index outputs, as used by `experiments/34_iclr_mega_rewrite_astra/analysis/rebuild_paper_evidence.py`.

## Method (summary; details in the protocol)

- **A. Null best-of-K.** Permute labels in problem blocks, draw K real configurations, record the largest Spearman agreement. This is what the winner shows when no configuration tracks the labels.
- **B. Split-half selection.** Choose on 12 problems, evaluate on the other 12; compare choosing by labels, at random, and by the label-free `cert_index`.
- **C. Synthetic sweep.** A latent-quality model calibrated to the panel's clustering and inter-pass agreement extends K to 64 and translates the 36-pair split-half result to 72 pairs.
- **D. Judge-level adjustment.** Exact permutation of the judge-level association with the maximum taken over the four reported index forms.

No model calls, no credentials, no network; nothing under `paper_latex/` is edited. Drafted paper sentences go in `REPORT.md`.

| Artifact | Purpose |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | Frozen analysis plan, parameters, seeds and decision rules |
| [results.md](results.md) | Live results and phase status |
| [CKPT_selection_bias.md](CKPT_selection_bias.md) | Resumable checkpoint |
| `analysis/best_of_k_selection_bias.py` | The whole analysis (deterministic, seeded) |
| `analysis/make_figure.py` | Figure from the committed CSVs |
| `results/` | CSV and JSON outputs with input hashes |
| `figures/` | Inflation-versus-K figure |
| [REPORT.md](REPORT.md) | Findings, drafted paper text and its drop-in build check |
| `tests/test_best_of_k_selection_bias.py` (repository root) | Unit tests and a reproduction-gate regression test |
