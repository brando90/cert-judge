# Proposed methods and appendix disclosure

**Doc link:** [Five-rater protocol](PROTOCOL.md)

**Status:** Proposed wording for review; no manuscript file was edited.

We reanalyze cached judge scores using VeriBench’s existing task-grouped train, validation, and test partitions of 10, 5, and 10 tasks, with three candidate outputs per task. The primary target averages the available ratings from the five current participants; participants 1–3 provide a paired sensitivity comparison. We retain individual ratings and missingness. Two historical passes from participant 1 represent a different instruction regime and enter only a separately weighted training sensitivity. Historical ratings on validation and test tasks are excluded from fitting, selection, and evaluation. These items and earlier outcomes informed previous analyses, so the present comparisons are exploratory. We recorded the new selection rules before computing the new comparisons. The validation-selected rule remains unavailable because shared coverage is 13 of 15 outputs, below the frozen 90% requirement of 14 outputs. Reference provenance uses reconstructed repository snapshots; these do not establish exactly which bytes each participant viewed.

Optional context sentence: Empirical studies show that repeated evaluation need not produce substantial adaptive overfitting, but do not establish its absence in this panel [Roelofs et al., 2019].

## Verified reference and scope

Rebecca Roelofs, Vaishaal Shankar, Benjamin Recht, Sara Fridovich-Keil, Moritz Hardt, John Miller, and Ludwig Schmidt. **A Meta-Analysis of Overfitting in Machine Learning.** Advances in Neural Information Processing Systems 32, 2019. [Official proceedings](https://proceedings.neurips.cc/paper_files/paper/2019/hash/ee39e503b6bedf0c98c388b7e8589aca-Abstract.html).

The citation supports a limited observation about dataset reuse. It neither estimates overfitting here nor licenses a claim of pristine test data. Avoid an unsupported claim that this panel was used only twice. `experiments/39_label_free_proxy_index_train_val_test_over_judge_families/README.md`, `experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/REPORT.md`, and `experiments/archive/44_cached_score_judge_selection_utility/results.md` record earlier criterion reuse; `experiments/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/REPORT.md` records the earlier historical-label and reference audit. New synthetic probes do not erase that exposure.
