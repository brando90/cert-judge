# PR 64 (interim paper-framing draft): record kept in the repo, 11-11-2026

**TLDR:** PR 64 was closed on 11-11-2026, not merged (Brando, 11-11-2026: no open pull requests or issues in this repo). The paper framing is still Brando's call after the new human rating round. Everything the PR held stays reachable: the branch `paper/framing-10-13-2026` is kept (not deleted), the decision record is `docs/PAPER_FRAMING_DECISION_10-13-2026.md` (copied unchanged from that branch), and the PR text is below.

## Where each part of the PR lives

- Paper rewrite (interim, result-consistent draft, not the paper's new claims): branch `paper/framing-10-13-2026`, commits d0ea926, 86b7b62, dae1111, 5ac4c03, 359d76a. Not on `main` on purpose.
- Decision record with every number, interval, denominator and source file: `docs/PAPER_FRAMING_DECISION_10-13-2026.md`.
- Archive of experiments 39, 41, 42 and 43 into `experiments/archive/`: branch commit c9963c1. It conflicts with `main` in `experiments/archive/layout.json` and the READMEs, so it is not cherry-picked here; redo it on `main` when those experiments are archived.
- Master checkpoint update: branch commit 24d1947.

## The PR text, as it stood (10-13-2026)

> **Brando, 10-13-2026: this PR is an interim, result-consistent draft, not the paper's new claims.** The plan of record is more human data (the shared set-N rating round, then a cert-judge pool); the framing is decided after that round. Keep unmerged. The archive commit (experiments 39/41/42/43) can be cherry-picked separately.

## Summary

- Rewrites the paper to the framing decided on 10-13-2026 (VeriBench `experiments/DECISIONS_10-13-2026_open_decisions_resolved.md`, section "Cert-judge paper: what it claims now"): what transfers to held-out judges and what does not. Decision record with every number, interval, denominator, split and source file: `docs/PAPER_FRAMING_DECISION_10-13-2026.md`.
- Claim 1: the label-free gold deletion-monotonicity screen `C_ms_gold`, selected on the train and validation judges, predicts held-out judges' agreement with expert ratings under the pre-registered rule (test Spearman 0.558 [0.078, 0.762], one-sided permutation p-val=0.0127, 16 of 18 configurations), reported with the lower bound and the prompt-group sensitivity as a scope limit (0.453 [-0.177, 0.825], p-val=0.0551 on 14; -0.371 [-0.787, 0.304], p-val=0.8615 on the 10 fuller-context prompts).
- Claim 2: the paper's earlier indices do not transfer (`TI_var` -0.332 [-0.636, 0.135], p-val=0.9135, 18; `PTI_v0` -0.274 [-0.753, 0.111], p-val=0.7793, 9 of 18).
- Claim 3: selection utility is not demonstrated (proxy 0.768 vs fixed H2 0.853, paired difference -0.086 [-0.308, 0.058], p-val=n/a, 42 files / 15 tasks; experiment 44, five-rater sensitivity from 45).
- Claim 4: the semantic screen (15 of 56 pass) and the gaming study (gaps -0.162 to +0.033, no interval above zero; 59 of 62 edited candidates flagged and credited by the reference too) are characterization.
- Claim 5: the 72-pair validation-set results move to a new appendix (`999_appendix_validation_set_72_pairs.tex`) with the provenance caveat (7 of 24 scored tasks match the rater-seen references; corrected-label re-score inconclusive) and the best-of-k selection bias (+0.153 over 4,000 splits).
- Target venue TMLR; sources stay in `paper_latex/ICLR_2027_submission/` with the ICLR style (venue change recorded in `CHANGES.md`; `tmlr.sty` swap is a submission-time step). Nothing is submitted anywhere.
- Archives experiments 39, 41, 42 and 43 (all DONE 09-30-2026) into `experiments/archive/` with outcome rows, repointing the scripts in 42, 43, 46 and 47 that read 39 by path; `layout.json` updated.
- Updates the master checkpoint `experiments/CKPT_MASTER_tmux1_cc_6043a46f.md` (decision [p10] resolved, this PR, what remains, Brando to-do).

Reports: `experiments/archive/39_label_free_proxy_index_train_val_test_over_judge_families/results/RESULTS_proxy_index_train_val_test.md`, `experiments/archive/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/REPORT.md`, `experiments/archive/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/REPORT.md`, `experiments/archive/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/REPORT.md`, `experiments/archive/44_cached_score_judge_selection_utility/RESULTS_selection_utility.md`, `experiments/archive/40_best_of_k_judge_selection_bias_validation_set/REPORT.md`.

## Test plan

- `latexmk -pdf -interaction=nonstopmode main.tex` in a scratch copy: 0 errors, 0 undefined references or citations, PDF committed beside the sources (`main.pdf`); `python3 ~/agents-config/scripts/latex_sentence_lines.py --check main.tex 0*.tex 99*.tex` passes; prose scanned for "calibrat*", "dev set", "certif*" (none).
- Every paper number re-read from the archived receipts (`TEST_RECEIPT.json`, `units_test.json`, `RESULTS_selection_utility.md`, `index_association.json`, `analysis.json`); the two prompt-group rows recomputed from `units_test.json` with `analysis_lib.association` (10,000 draws, seed 39) and recorded in the decision document; the new figure is drawn by `figures/make_c_ms_gold_vs_criterion.py` from the committed unit files.
- After the archive move: `python3 py_src/cert_judge/experiment_layout.py --check` reports Layout OK; `pytest` on 39 `test_e39.py` (19 passed), 41 `test_rescore.py` (8 passed), 42 `test_e42.py` (13 passed, 1 skipped), 43 `test_e43.py` (13 passed, 1 skipped with `E43_VERIBENCH_REPO` pointing at a local VeriBench clone); the git-ref fallbacks in 42/43 `analyze.py` resolve the pre-archive path on `origin/main`.

Brando reads the framing before any submission; do not merge without him.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
