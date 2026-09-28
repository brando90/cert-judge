# Optional research ideas

**TLDR:** Index of optional, deferred research ideas. Recording one does not launch it. Five ideas answer "why only VeriBench?" (issue #45), each with a README and a ready-to-paste `cc.md` prompt; the catalog `35_missing_experiments_from_reviews` holds twelve reviewer-requested experiments with dispatch-ready prompts. Each would become its own numbered experiment if run.

## Benchmark transfer ([issue #45](https://github.com/brando90/cert-judge/issues/45))

Motivation: the paper's results all come from VeriBench (`05_experiments.tex:4`), and NeurIPS 2025 MATH-AI reviewer ivJs flagged "finite perturbations on one benchmark". The limitations section now names Verina and Vero as untested (commit 543c524).

| Priority | Idea | Execution | Paper inclusion | Judge-call spend | One-line setup |
|---:|---|---|---|---|---|
| 1 | [verina_property_transfer_no_new_labels](verina_property_transfer_no_new_labels/README.md) | DEFERRED — NOT RUN | UNDECIDED | ~5,184 calls, ~$23 ([quote](verina_property_transfer_no_new_labels/COST_QUOTE.md)) | Paper's exact TI_var pipeline on 24 Verina items, Codex-family panel, compared with VeriBench. |
| 2 | [verina_human_validation_panel](verina_human_validation_panel/README.md) | DEFERRED — NOT RUN | UNDECIDED | 0 extra; 144 human ratings | Label the 72 Verina pairs under the validation rubric after freezing TI_var: the first real test set. |
| 3 | [lean_benchmark_breadth_structural_screen](lean_benchmark_breadth_structural_screen/README.md) | DEFERRED — NOT RUN | UNDECIDED | $0 | Which of CLEVER, FVAPPS, miniCodeProps support which probes. |
| 4 | [vero_repo_level_probe_feasibility](vero_repo_level_probe_feasibility/README.md) | DEFERRED — NOT RUN | UNDECIDED | $0 (scoring quoted separately) | Probes and judge inputs for Vero's 43 multi-module Lake projects. |
| 5 | [non_lean_dafny_verus_transfer](non_lean_dafny_verus_transfer/README.md) | DEFERRED — NOT RUN | UNDECIDED | $0 | Probes ported to Verus (VeriContest) and Dafny (DafnyBench). |

Idea 2 depends on idea 1. Ideas 3–5 are independent and make no model calls.

## Reviewer-requested experiments

Moved here from the active list on 09-28-2026: the catalog is complete, and none of its twelve experiments has started.

| Priority | Idea | Execution | Paper inclusion | Judge-call spend | One-line setup |
|---:|---|---|---|---|---|
| 1 | [35_missing_experiments_from_reviews](35_missing_experiments_from_reviews/EXPERIMENTS.md) | DEFERRED — NOT RUN | UNDECIDED | Tier 0 (35.1–35.4): $0; Tier 1 (35.5–35.9): subscription CLI, $0 API, quote first; Tier 2 (35.10–35.12): new human labels | Twelve gaps from four OpenReview rounds, ranked by decision impact per unit cost, each with a CLI-only prompt. |

Catalog item 35.10 (locked held-out test) and benchmark-transfer idea 2 both target the first real test set.
