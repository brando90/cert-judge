# TMLR Revision Backlog — deferred reviewer asks (from ICML 2026 AI4Math OpenReview)

**TLDR:** Items from the AI4Math workshop reviews (uMVy, c7ev, DeJF + meta) deliberately NOT addressed in the initial TMLR submission (`paper_latex/TMLR_2026_submission/`), reserved for the TMLR revision phase. The submission already covers: held-out outcome disclosure (§6.1 caveat), bootstrap CIs + permutation p on the n=8 headline correlations, annotation-protocol clarification, alpha-canonicalization proxy sentence, VeriBench judge-family clarification.

## Deferred (real new work — natural TMLR-response material)

1. **Leave-one-family-out / robustness of judge-level correlations** (uMVy) — bootstrap CIs added; LOFO analysis across model families not yet run.
2. **TI_var formulation justification beyond validation fit** (uMVy, c7ev, DeJF) — sensitivity of results to weighting/normalization choices; GM comparison exists in paper but a systematic ablation table does not.
3. **Expanded failure-mode probes** (c7ev): vacuous specifications, subtle theorem weakening, over-constraint, formatting-only perturbations.
4. **True pre-scoring Lean canonicalization** (all three reviewers) — the submission cites the post-hoc proxy (exp24: within-item std 0.250→0.070); real canonicalize-then-rescore experiment not run.
5. **Bib stubs** (c7ev flagged reference quality): "Ding, Z. and others" (AAAI 2025), "Naik, A. and others" (TSE 2024), "{Ospanov et al.}" (2023, no eprint) — fill full author lists + arXiv/DOI (appendix-only cites; see evidence_map.md "Known issues").
6. **How many annotators for stable calibration targets** (c7ev open question) — could be answered with pool subsampling analysis on the 5-reviewer pool (within revised protocol only — respect label-lineage hazard).
7. **Property suite on theorem statements without gold references** (c7ev) — new experimental setting.
8. **Other proof assistants beyond Lean 4** (DeJF) — out of scope for revision; future-work paper.

## Hazards to respect in any revision

- **Never join** `experiments/human_labels/` (revised protocol) with `experiments/04_veribench_validation/data/ethan_human_scores_*` (old protocol) as if interchangeable — near-uncorrelated constructs (ρ≈0.13, n=63; re-verified deterministically 2026-07-29).
- `experiments/18_open_revievew_feedback_ICML_2026_mathai_ws/agent_prompt.md` quotes numbers that exist in no artifact (evidence_map.md) — do not copy from it.
- `experiments/02_reviewer_response_neurips_math_ai_2026/` is the previous paper generation (gpt-4o-mini era) — do not import its results.

## Submission-cited artifacts (must stay committed/public)

- Headline trio: `…/04_vb/results_exp28_varaware_codex_{avg_newindex,pass1,pass2_newindex}/summary.json` (`rho_TI_vs_human`).
- CIs (added in submission): recomputed 2026-07-29, seed 42, 10k resamples — avg [0.24,1.00] p=.017, pass1 [0.41,1.00] p=.005, pass2 [0.11,1.00] p=.045.
- §6.1 caveat numbers: exp22 REPORT (ρ≈0.13 n=63; ceiling 0.87; relabel 0.90), exp45 `23_reanchored_calibration/` (underpowered), exp46 `24_expanded_panel_cli/results/pass2_full_screen_results.json` (9-candidate screen: strongest |ρ|=0.39 Holm p=0.25; LOO ρ=0.24 p=0.49; registered verdict b).
- Inter-pass agreement: `…/04_vb/results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json` (Spearman 0.2486 [−0.015,0.489], QWK 0.372, n=72).
- Canonicalization proxy: `…/04_vb/results_exp24_alpha_canonicalized_identity/summary.json` (0.2501→0.0697, median reduction 64.28%).
