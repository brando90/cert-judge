# CertJudge ICML 2026 Reviewer-Feedback Action Prompt
**TLDR:** Yes, act on the feedback. Prioritize claim calibration, annotation-protocol clarity, uncertainty intervals, TI_var ablations, alpha-renaming treatment, VeriBench-judge consistency, citation hygiene, and readability; treat held-out validation carefully because the existing Exp23 held-out analysis is weak/negative, not confirmatory.

## Recommendation Summary

Use this file as the launch prompt for an agent that revises the ICML 2026 AI4Math workshop paper after acceptance. The raw OpenReview feedback is preserved in `experiments/18_icml_reviews/pre_prompt.md`.

Target paper paths:

- `paper_latex/ICML_2026_AI4Math/main.tex`
- `paper_latex/ICML_2026_AI4Math/sections/abstract.tex`
- `paper_latex/ICML_2026_AI4Math/sections/methodology.tex`
- `paper_latex/ICML_2026_AI4Math/sections/appendix.tex`
- `paper_latex/ICML_2026_AI4Math/refs.bib`

Main supporting experiment paths:

- `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/summary.json`
- `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/detail_rows.csv`
- `experiments/archive/04_veribench_validation/results_exp23_heldout_human_labels/report.md`
- `experiments/archive/04_veribench_validation/results_exp23_heldout_human_labels/summary.json`
- `experiments/archive/04_veribench_validation/results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json`
- `experiments/archive/04_veribench_validation/results_exp18_alpha_ablation_r9/summary.json`
- `experiments/archive/04_veribench_validation/results_exp24_alpha_canonicalized_identity/summary.json`
- `experiments/archive/04_veribench_validation/results_exp21_cert_index_sweep/median/summary.md`
- `experiments/archive/04_veribench_validation/results_exp30_tivar_v3_all_models/summary.json`

Safety and evidence rules:

- Do not run new experiments, judge scoring, LLM-provider APIs, LLM CLI calls for evidence generation, or scripts that read LLM keys unless the user explicitly approves the exact command, model/provider, data coverage, and estimated cost.
- Use existing local artifacts for all paper numbers. If a required number is absent, report it as missing work rather than generating it silently.
- The current Exp23 held-out result is not positive evidence: `experiments/archive/04_veribench_validation/results_exp23_heldout_human_labels/report.md` reports primary held-out Spearman(TI_var, held-out human Spearman) = -0.238 with p = 0.5821 on 60 exact matched pairs; the candidate-alias sensitivity is 0.119 with p = 0.7930 on 72 pairs. Only a later locked rerun with complete coverage and positive results could change this conclusion.

## Recommended Actions

| Priority | Action | Importance | Rationale | What to do |
|---:|---|---:|---|---|
| 1 | Clarify and temper the central empirical claim | 10/10 | Every reviewer and the meta-review identified calibration-vs-generalization as the main weakness. The paper is already accepted, but the camera-ready should protect the claim from overreach. | Ensure abstract, intro, results, conclusion, and captions consistently say "validation-set calibration evidence" rather than "generalizes" or "certifies reliability." Add one explicit limitations sentence near the main TI_var result. |
| 2 | Clarify the human-labeling protocol | 10/10 | Reviewers were confused about single annotator vs multiple annotators, pass1/pass2, and disagreement handling. This is the easiest high-impact fix. | Add a concise protocol paragraph/table: annotators, label scale, pass1/pass2 meaning, number of aligned pairs, overlap size, how average labels are computed, and how disagreements are reported. |
| 3 | Add uncertainty for judge-level correlations | 9/10 | With only eight judge configurations, point correlations are fragile. Reviewers directly asked for CIs/bootstrap/permutation tests. | Pull CIs and p-values from `results_exp16_final_robust_r9_median/summary.json` and related summaries. Report Spearman with CI and permutation p-value where space allows; otherwise put full table in appendix. |
| 4 | Report TI_var sensitivity and simpler-index baselines | 9/10 | Reviewers questioned whether TI_var is uniquely justified. The response should show whether simpler geometric/arithmetic variants are competitive. | Use `results_exp21_cert_index_sweep/median/summary.md`, `results_exp29_geom_p1_p4_plus_var`, and `results_exp30_tivar_v3_all_models/summary.json`. Add a short ablation paragraph and avoid claiming uniqueness. |
| 5 | Address held-out validation honestly | 9/10 | Reviewers asked for a frozen held-out test, but the existing Exp23 held-out result is weak/negative: primary Spearman is -0.238 with p = 0.5821 on 60 exact matched pairs. Do not bury or spin this. | If including Exp23, frame it as a stress test showing current evidence does not yet establish deployment-time generalization. If the goal is to strengthen the paper, rerun a complete frozen held-out analysis only after confirming all missing pairs can be scored and budget is approved. |
| 6 | Expand alpha-renaming discussion and mitigation | 8/10 | Alpha-renaming sensitivity is the most concrete technical failure mode reviewers named. | Add a failure-analysis paragraph. Use `results_exp18_alpha_ablation_r9/summary.json` and `results_exp24_alpha_canonicalized_identity/summary.json` to say post-hoc alpha-canonicalization reduces identity variance, but true canonicalization requires rescoring canonicalized Lean text. |
| 7 | Fix VeriBench judge-family consistency | 8/10 | One reviewer flagged that the VeriBench demo appears to use Claude 3.7 while the main validation focuses on other judge families. This can undermine "same calibrated judge" wording. | Audit every mention of downstream VeriBench ranking. State the exact judge model/prompt used for ranking and whether it is the same family as the calibration judges. If not, call it a downstream demonstration, not independent validation. |
| 8 | Add failure modes beyond alpha-renaming | 7/10 | Reviewers listed vacuity, weakening, over-constraint, formatting-only perturbations, and rubric ambiguity. | Add a compact threats-to-validity paragraph and, if there is existing evidence, a small appendix table. Do not run new LLM scoring unless approved. |
| 9 | Audit citations and future/anonymous references | 7/10 | Reviewer c7ev explicitly flagged unstable references. This is a low-cost camera-ready fix. | Inspect `refs.bib`; replace anonymous/future-dated/workshop-only refs with stable URLs/DOIs/arXiv IDs where possible, or mark them as workshop/preprint transparently. |
| 10 | Improve readability for non-Lean readers | 6/10 | One reviewer asked to simplify dense Lean/formal-methods sections. This helps workshop readers without changing claims. | Add one or two bridge sentences around Lean kernel vs intended theorem semantics. Translate "specification" as "theorem formulation" where an ML reader may misread it. |
| 11 | Leave broader proof-assistant/generalization claims for future work | 5/10 | Reviewers asked whether the approach transfers beyond Lean, but the current paper likely cannot prove this. | Add one sentence in limitations/future work. Do not broaden the claim without data. |

## Decision

Act now on Actions 1-4, 6-10 for the camera-ready or public revision. Treat Action 5 as conditional: include the existing held-out result only if the authors want a candid limitation, or rerun the held-out analysis with complete frozen pair coverage and no metric retuning. Do not present the current Exp23 held-out result as confirmatory evidence.

## Mega Prompt 1: Paper Revision Agent

```text
TLDR at the top of your response.

You are revising the accepted ICML 2026 AI4Math workshop paper "CertJudge: Evaluating Lean Formal-Code With Falsifiable Properties" in `/Users/brandomiranda/cert-judge`.

First load and follow:
- `/Users/brandomiranda/cert-judge/AGENTS.md` if present, plus the global agents-config rules it references.
- `~/agents-config/writing/ml_research/ml_research_writing.md`.

Inputs:
- Raw reviewer feedback: `experiments/18_icml_reviews/pre_prompt.md`
- Action plan: `experiments/18_icml_reviews/agent_prompt.md`
- Paper source:
  - `paper_latex/ICML_2026_AI4Math/main.tex`
  - `paper_latex/ICML_2026_AI4Math/sections/abstract.tex`
  - `paper_latex/ICML_2026_AI4Math/sections/methodology.tex`
  - `paper_latex/ICML_2026_AI4Math/sections/appendix.tex`
  - `paper_latex/ICML_2026_AI4Math/refs.bib`

Goal:
Make camera-ready-quality edits that directly address reviewer feedback without overclaiming. Preserve the paper's core contribution, but make the evidence level scientifically precise.

Safety:
- Do not run new experiments, judge scoring, LLM-provider APIs, LLM CLI calls for evidence generation, or scripts that read LLM keys unless the user explicitly approves the exact command, model/provider, data coverage, and estimated cost.
- Use existing local artifacts first. If evidence is missing, report the missing artifact/work instead of generating new LLM-scored results silently.

Required edits:
1. Calibration-vs-generalization:
   - Audit abstract, intro, results, captions, conclusion, and appendix for any phrase implying universal reliability or deployment-time generalization.
   - Replace with precise language: "validation-set calibration evidence", "judge-level association on this panel", "not a deployment-time guarantee", etc.
   - Keep the strongest numeric results only where supported by a cited experiment file.

2. Human-labeling protocol:
   - Add a concise protocol paragraph or table explaining label scale, number of pairs, pass1/pass2, overlap, averaging, and disagreement handling.
   - Use exact values only after checking the experiment JSON/CSV files. Relevant sources include:
     - `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/summary.json`
     - `experiments/archive/04_veribench_validation/results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json`
     - `experiments/archive/04_veribench_validation/results_exp23_heldout_human_labels/summary.json`

3. Uncertainty:
   - Add CIs and/or permutation p-values for judge-level correlations if available.
   - If space is tight, put the complete uncertainty table in the appendix and put one representative CI in the main text.
   - Do not invent intervals. Every number must trace to a local artifact.

4. TI_var justification and ablations:
   - Add a short paragraph explaining why the variance-aware index is used: it rewards property success and penalizes instability.
   - Add an ablation/sensitivity sentence or appendix table comparing TI_var to simpler alternatives.
   - Use existing artifacts first:
     - `experiments/archive/04_veribench_validation/results_exp21_cert_index_sweep/median/summary.md`
     - `experiments/archive/04_veribench_validation/results_exp29_geom_p1_p4_plus_var/summary.json`
     - `experiments/archive/04_veribench_validation/results_exp30_tivar_v3_all_models/summary.json`
   - Do not claim TI_var is uniquely optimal. Say it is a reasonable operational summary supported by validation-set evidence.

5. Held-out validation:
   - Read `experiments/archive/04_veribench_validation/results_exp23_heldout_human_labels/report.md` and `summary.json`.
   - The existing held-out result is weak/negative under the primary exact-match analysis. Do not present it as confirmatory.
   - Either:
     - include it as a limitation/stress-test result, or
     - leave it out of the main paper and add a future-work sentence saying a fully locked held-out test remains the next step.
   - If you believe a new held-out run is needed, stop and surface a proposed command, expected LLM/API cost, and data coverage before running anything that calls LLM APIs.

6. Alpha-renaming:
   - Add a concrete failure-mode paragraph.
   - Use:
     - `experiments/archive/04_veribench_validation/results_exp18_alpha_ablation_r9/summary.json`
     - `experiments/archive/04_veribench_validation/results_exp24_alpha_canonicalized_identity/summary.json`
   - State that post-hoc alpha-canonicalization reduces identity variance, but true Lean-side canonicalization requires rescoring canonicalized text.

7. VeriBench downstream demo:
   - Audit exact judge model/prompt names used for downstream VeriBench ranking.
   - Remove or soften any claim that the downstream ranking independently validates judge correctness.
   - State whether it is the same calibrated judge or a demonstration using a related judge.

8. Citation and prose cleanup:
   - Audit `refs.bib` for anonymous, future-dated, workshop-specific, and very recent references.
   - Add stable URLs/DOIs/arXiv IDs when available.
   - Improve readability for non-Lean readers using the ML writing guide. Translate "specification" where needed as "theorem formulation" or "formal property to prove."

Verification:
- Build the paper with `latexmk -pdf main.tex` from `paper_latex/ICML_2026_AI4Math`.
- Run `git diff --check`.
- Inspect the generated PDF for obvious missing refs, overfull visual breakage, and stale claims.
- Report changed files, key reviewer points addressed, and any unresolved caveats.
```

## Mega Prompt 2: Evidence and Held-Out Audit Agent

```text
TLDR at the top of your response.

You are the evidence-audit agent for the CertJudge ICML 2026 AI4Math paper. Work in `/Users/brandomiranda/cert-judge`.

Purpose:
Determine exactly which reviewer-requested analyses are already supported by local artifacts, which are unsupported, and which would require new LLM calls or new human annotation.

Rules:
- Do not run any script that calls LLM-provider APIs or reads LLM keys.
- Do not write paper prose until the evidence table is complete.
- Every numeric claim must cite a path and JSON/CSV field or row source.

Audit tasks:
1. Build an evidence table with columns:
   - Reviewer concern
   - Local artifact path
   - Exact result
   - Supports positive claim? yes/no/partial
   - Safe paper wording
   - Missing work

2. Cover at least these concerns:
   - frozen held-out validation on independent reviewers
   - human-label protocol and inter-pass agreement
   - uncertainty intervals for judge-level correlations
   - TI_var vs simpler/geometric/arithmetic index sensitivity
   - alpha-renaming sensitivity and canonicalization
   - downstream VeriBench ranking judge-family consistency
   - citation stability

3. Read at minimum:
   - `experiments/archive/04_veribench_validation/results_exp23_heldout_human_labels/report.md`
   - `experiments/archive/04_veribench_validation/results_exp23_heldout_human_labels/summary.json`
   - `experiments/archive/04_veribench_validation/results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json`
   - `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/summary.json`
   - `experiments/archive/04_veribench_validation/results_exp18_alpha_ablation_r9/summary.json`
   - `experiments/archive/04_veribench_validation/results_exp24_alpha_canonicalized_identity/summary.json`
   - `experiments/archive/04_veribench_validation/results_exp21_cert_index_sweep/median/summary.md`
   - `experiments/archive/04_veribench_validation/results_exp30_tivar_v3_all_models/summary.json`
   - `paper_latex/ICML_2026_AI4Math/main.tex`
   - `paper_latex/ICML_2026_AI4Math/refs.bib`

4. Output a markdown report at:
   `experiments/18_icml_reviews/evidence_audit.md`

Report requirements:
- Start with `# CertJudge ICML 2026 Evidence Audit`.
- Include a `**TLDR:**` immediately below the title.
- Be explicit that current Exp23 held-out evidence is not confirmatory unless a later rerun changes it.
- Include recommended exact wording snippets for the paper, but mark them as snippets, not final integrated prose.
```

## Mega Prompt 3: Final QA Agent

```text
TLDR at the top of your response.

You are the final QA reviewer for reviewer-response edits to the CertJudge ICML 2026 AI4Math workshop paper.

Scope:
- Review paper edits and any new docs under:
  - `paper_latex/ICML_2026_AI4Math/`
  - `experiments/18_icml_reviews/`

Check:
1. Claims:
   - No paper sentence claims held-out generalization unless a locked held-out result supports it.
   - Current Exp23 held-out result is not spun as positive.
   - All numbers are traceable to local artifacts.

2. Reviewer coverage:
   - Calibration-vs-generalization limitation addressed.
   - Human-labeling protocol clarified.
   - CIs/p-values or uncertainty caveat included.
   - TI_var sensitivity/alternatives discussed.
   - Alpha-renaming failure mode and mitigation discussed.
   - VeriBench ranking framed as demonstration, not independent validation.
   - References audited for unstable entries.
   - Dense Lean language simplified where practical.

3. Formatting and build:
   - Run `git diff --check`.
   - Run `latexmk -pdf main.tex` in `paper_latex/ICML_2026_AI4Math`.
   - Inspect warnings for undefined citations/references.

Output:
- PASS only if there are no critical claim/evidence issues and the paper builds.
- Otherwise list blocking issues first with file/line references and concrete fixes.
```
