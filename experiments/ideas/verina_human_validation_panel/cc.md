# Prompt — Verina human test panel with TI_var frozen before labeling

**TLDR:** Make the agent promote this idea into a numbered experiment, freeze and hash each judge configuration's Verina TI_var from the completed Verina transfer experiment, recover the VeriBench validation set's exact 0–5 rubric and annotator instructions, and build a blind labeling packet for the 72 Verina pairs (strict and lenient passes). After the human labels come back, it computes the pre-registered judge-level association. Success: `PREREGISTRATION.md` is committed before any label exists, and the final report gives the TI_var-to-human-agreement Spearman with a bootstrap interval next to the VeriBench validation-set values. Deliverable: the experiment folder with the packet, preregistration and live `results.md`, pushed to `main`. Load-bearing constraints: no judge calls, no model-written labels, and never invent or paraphrase the rubric.

Follow `~/agents-config/INDEX_RULES.md` (pull it first) and the repo `CLAUDE.md`.

## Precondition

The Verina transfer experiment (promoted from `experiments/ideas/verina_property_transfer_no_new_labels/`) must be complete: all 72 pairs scored by every configuration, with TI_var computed. If it is not, stop and report which of its cells are missing.

## Steps

1. **Promote.** Allocate the next free experiment number, `git mv` this idea folder to `experiments/<NN>_verina_human_test_panel_frozen_tivar/`, register it in `layout.json` and `experiments/README.md`, update the ideas index, and run `python3 py_src/cert_judge/experiment_layout.py --check`. Start `results.md` (live; closes with a tagged `**TLDR-end:**`).
2. **Freeze the predictor.** Copy each configuration's Verina TI_var and property values into `frozen_tivar.json` and record its SHA-256 in `PREREGISTRATION.md`. That file also states the primary analysis (judge-level Spearman between frozen TI_var and each configuration's Spearman agreement with the average of the two passes), the secondary analyses (pass1 and pass2 separately; Kendall), the bootstrap (10,000 replicates over pairs, seed 0), whether families are pooled, and the reading rule. Commit and push it **before** creating the labeling packet.
3. **Recover the rubric verbatim.** Find the exact written 0–5 instructions used for the VeriBench validation labels. Start from `experiments/archive/04_veribench_validation/data/ethan_human_scores_*.tsv`, `exp16_multi_judge_human_sets.py:98–99`, `experiments/human_labels/`, `experiments/archive/03_human_validation/`, `experiments/archive/18_human_judgment_study/`, `experiments/archive/26_human_label_dataset_audit/` and git history. Record the source path and commit. If you cannot find it, stop and ask Brando for it; do not write a new rubric.
4. **Build the packet.** Create one blind, randomized sheet per pass (`packet/pass_strict.tsv`, `packet/pass_lenient.tsv`) with a pair ID, the Verina description, the gold and the candidate, and an empty 0–5 column. Hide agent identity and judge scores. Put the verbatim rubric in `packet/RUBRIC.md` and the logistics in `packet/INSTRUCTIONS.md`: the two passes at least one day apart, and a timer column for minutes per pair.
5. **Hand off.** Set `results.md` to `BLOCKED — awaiting human labels`, report the packet paths, and stop. Labels are human-only.
6. **After labels arrive** (a later session): validate the sheets (72 rows each, scores in 0–5, no blanks; any blank stays missing, never imputed), then run exactly the pre-registered analysis with the same code paths as the paper (`exp16`/`exp17`/`exp28`). Report measured values next to the VeriBench validation set (0.833 / 0.905 / 0.738), human–human agreement between the two passes, and minutes per rating.
7. **Land.** Commit with explicit pathspecs (the index is shared), `git pull --rebase --autostash`, push to `main`, and tick issue #45.

## Guardrails

- No LLM judge or provider calls; nothing that reads `~/keys/*`.
- Never let a model produce, "pre-fill" or adjust human labels.
- The preregistration is immutable after commit; deviations go in `REPORT.md` → "Open questions".
- Call it a test set only if the preregistration commit precedes the first label; otherwise report it as another validation set.

TL;DR: Freezes Verina TI_var, recovers the validation-set rubric verbatim, builds a blind two-pass labeling packet for the 72 Verina pairs, and once humans return labels, runs the pre-registered judge-level association as the paper's first out-of-benchmark test; no model calls.
