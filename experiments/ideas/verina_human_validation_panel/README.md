# Verina human panel: first out-of-benchmark test of TI_var against human agreement

**TLDR:** Label the 72 Verina candidate–gold pairs from the Verina transfer idea under the VeriBench validation set's exact 0–5 rubric, after freezing each judge configuration's Verina TI_var. This makes it the paper's first real test set: a new benchmark, properties and index frozen before labels are seen. It needs no extra judge calls (the pairs are already scored in that idea), only annotator time.

**Execution:** DEFERRED — NOT RUN · **Paper inclusion:** UNDECIDED · **Priority:** 2 of 5 · **Depends on:** [verina_property_transfer_no_new_labels](../verina_property_transfer_no_new_labels/README.md) · **Recorded:** 09-22-2026 · **Issue:** <https://github.com/brando90/cert-judge/issues/45> · **Prompt:** [cc.md](cc.md)

**Would become:** `experiments/<NN>_verina_human_test_panel_frozen_tivar/`.

## Hypothesis

Across judge configurations, frozen Verina TI_var is positively associated with each configuration's Spearman agreement with the new Verina human labels (the same judge-level association the paper reports on the VeriBench validation set: 0.833 / 0.905 / 0.738 for average / pass1 / pass2).

## Motivation

- The limitations section says there is no test-set result and that a real test needs new raters under the validation set's rubric, with the properties and TI_var frozen first (`06_limitations.tex`; repo `CLAUDE.md` § Data splits).
- The five-rater pool cannot serve that role: it used a revised rubric that agrees with the validation labels at only ρ ≈ 0.13 on 63 shared pairs.
- A Verina panel answers two reviewer questions at once: a second benchmark and a held-out test.

## Minimal comparison

1. Freeze each configuration's Verina TI_var and hash it into `PREREGISTRATION.md` before any label exists.
2. One annotator labels the 72 pairs twice (strict and lenient, matching pass1 and pass2), blind to judge scores and agent identity, in a randomized order.
3. Report the judge-level Spearman between frozen TI_var and human agreement, with a bootstrap over pairs, next to the VeriBench validation-set value.

## Cost

- Judge calls: 0 extra when run after the Verina transfer idea (its 72 pairs × 8 configurations × 3 repeats are already scored).
- Human time: 72 pairs × 2 passes = 144 ratings. Minutes per rating on VeriBench were not recorded, so this is **not quoted**; measure it on the first 10 pairs.

## Key uncertainty

- The exact written rubric and annotator instructions behind the VeriBench pass1/pass2 labels must be recovered verbatim. The label files are `experiments/archive/04_veribench_validation/data/ethan_human_scores_20260425.tsv` (pass1) and `ethan_human_scores_ORIGINAL.tsv` (pass2) per `exp16_multi_judge_human_sets.py:98–99`, but the instruction text is not next to them.
- Who labels: the original annotator keeps the rubric identical; a new annotator makes it a stronger test of the rater. Brando decides.
- With about 8 configurations per family, the judge-level association has low power; pool families if the protocol allows it, and pre-register that choice.

## Revisit condition

As soon as the Verina transfer idea has produced frozen Verina TI_var values.
