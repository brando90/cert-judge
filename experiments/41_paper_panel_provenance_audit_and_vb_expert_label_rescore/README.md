# Experiment 41: provenance audit of the paper's 72-pair validation set, and a re-score of its frozen judges against VeriBench's expert labels

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/README.md>

**TLDR:** The paper's headline association (the index `TI_var` tracks judge–human agreement; Codex Spearman 0.833 on averaged labels, 0.905 and 0.738 on the two passes) rests on one annotator's two rating passes, and two facts found on 09-30-2026 leave it unverified. First, the paper's `pass1` / `pass2` label files have the same scores as VeriBench participant 1's two *old-prompt* passes (75/75 and 72/75 items identical, pass names swapped); VeriBench later replaced those with a corrected-prompt re-rating plus two more experts. Second, VeriBench experiment 100 found that its judges were given different reference files than the raters saw for 9 of 25 tasks (5 were `True` placeholders at rating time). With zero model calls, this experiment establishes which reference bytes the paper's judges saw, and recomputes the paper's judge-level results on reference-matched items and against VeriBench's three-expert labels.

## Goal, uncertainty and decision

**Central uncertainty (Trigger Rule 50).** Does the paper's only human-grounded evidence survive matched inputs and better labels? If the association disappears once judges and raters see the same references, or once the criterion is the corrected three-expert mean, then the paper's validation-set result is an artifact and experiment 39 (held-out judges against the expert labels) becomes the only evidence.

**Pre-registered analysis (locked in this README before any computation; deviations go in `results.md`).**

- **Gate G0 (reproduction).** Recompute the nine judge-level Spearman values (3 families × averaged / pass1 / pass2) from the committed `judge_trust_vector.csv` inputs and match the paper to 3 decimals (Codex 0.833 / 0.905 / 0.738; the rest as in `experiments/archive/38_iclr_body_rewrite_to_trust_artifact_abstract/analysis/results/judge_level_diagnostics.csv`). If G0 fails, stop the re-analysis and report the discrepancy.
- **Primary views.** For each family (Codex, Claude Opus, Qwen3-Coder; 8 configurations each): Spearman, Kendall and Pearson between `TI_var` and per-judge human agreement, where human agreement is recomputed from the frozen per-item judge scores under
  - V1 paper labels, all 72 pairs (reproduction);
  - V2 paper labels, reference-matched items only;
  - V3 VeriBench expert mean (participants 1–3, corrected prompt, ÷ 5), reference-matched items;
  - V4 VeriBench expert mean, all items with expert ratings;
  - V5 VeriBench participant 1's corrected-prompt pass alone, matched items.
  Report task-clustered bootstrap intervals (10,000 draws) and exact permutation p (8! orderings), plus every per-judge agreement value, so a moved criterion is visible.
- **Reading.** Robust: V3 Spearman positive in all three families and inside V1's interval. Not robust: V3 ≤ 0 in at least two families. Otherwise inconclusive. These readings are descriptive; no paper sentence changes without Brando.

**Secondary.**
- S1 (catalog item 35.2): leave-one-family-out and leave-one-configuration-out associations under V1 and V3.
- S2 (catalog item 35.12): recover the old-prompt and corrected-prompt rater instructions from VeriBench git history; document what changed and the pass-name swap.
- S3: label-agreement matrix (paper pass1 / pass2 against participants 1-corrected, 2, 3, 4, 5 and the expert mean), split by matched / unmatched references; revisit the archived Spearman ≈ 0.13 in `experiments/archive/22_pooled_heldout_and_noise_ceiling`.
- S4: the label-free headline (the lexical judge reverses on 20 of 24 bug ladders) needs no labels; confirm it is unaffected by reference provenance or say how it is affected.

## Inputs (all read-only)

- Paper judge-level vectors: `experiments/archive/04_veribench_validation/results_exp28_varaware_{codex,opus,qwen}_{avg,pass1,pass2}*/judge_trust_vector.csv` (exact paths in `experiments/archive/38_iclr_body_rewrite_to_trust_artifact_abstract/analysis/exact_permutation_and_subsets.py`); per-item judge scores behind them (Codex: `results_exp16_final_robust_r9_median/detail_rows.csv`; Opus and Qwen via `experiments/archive/34_iclr_mega_rewrite_astra/analysis/number_provenance.py`, which maps every paper number to its artifact).
- Paper labels: `experiments/archive/04_veribench_validation/data/ethan_human_scores_{20260425,ORIGINAL,avg_two_passes_20260425}.tsv`.
- VeriBench (own clone): `veribench_dataset/human_labels/` (participants 1–5 and `old_prompt/`); `experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/{provenance.json,items.jsonl,references/,MANIFEST.json}` and `scripts/phase0_audit.py` (the same audit for VeriBench's judges); `experiments/75_J1_validating_formal_spec_judge_train_val_test/{HUMAN_JUDGMENT_DATA.md,PROMPT_DIRECTION_AUDIT.md,data_description/items.csv}`.
- The gold files the paper's judges were given: resolve the actual bytes from the frozen pipeline (cert-judge `data/` roots, the gold-precedence policy in `experiments/archive/04_veribench_validation/pti_v0_v4/base_pool_manifest.json`, and any cached prompts or requests). If a task's judged bytes cannot be established, it counts as unmatched and is listed.

## Method and artifacts

Runbook: [cc.md](cc.md). Live ledger: [results.md](results.md). Checkpoint: `CKPT_provenance_audit.md` (written by the worker). Outputs: `results/provenance_by_task.csv` (task, reference hash the judges saw, hash at each rating date, matched?), `results/label_identity.json`, `results/judge_level_views.csv` (family × view × statistic), `results/per_judge_agreement.csv`, `REPORT.md` with drafted paper sentences (the paper itself is not edited).

Zero model calls, no credentials, no writes outside this folder.

**TLDR-end:** [cj: e41-provenance] Planned zero-call audit: which references the paper's judges and raters saw, and whether the paper's judge-level association survives matched items and VeriBench's corrected three-expert labels.
