# EXP45 (dir 23) — Pre-Registered Protocol Re-Anchoring Analysis

**TLDR:** Registered BEFORE computation (see this file's git commit timestamp vs. the results commit): does any label-free property signal predict judge alignment to the revised-protocol five-rater pool? Candidates, procedure, decision thresholds, and seed are fixed here; already-seen quantities are disclosed below so this registration only covers genuinely unseen analyses. Outcome (a)/(b)/(c) per the thresholds in §Decision criteria.

## Question

Under the revised-protocol construct (five-rater pool mean as target), do property-based signals — computed without any human labels — predict judge-level human alignment across judge configurations?

## Data (all existing; no LLM calls; no new labels)

- Unique judge configurations: the 20 from dir-22 (`experiments/22_pooled_heldout_and_noise_ceiling/results/results.json`, `unique_config_rows` construction: shared configs averaged across family panels). Primary population: the 14 "real" configs (excluding `editdist_e1`, `random_r1`, and the four `*BAD_STRINGY*` controls). Controls are analyzed separately as a directional validity check.
- Outcome y: pool-anchored alignment per config = Spearman(judge item scores, pool mean) on aligned items (~60/judge) — the `rho_heldout_items` values already computed in dir-22 (input scores verified valid by the corrected audit).
- Sensitivity outcome y2: same, anchored on the revised-protocol strict expert set (`experiments/human_labels/expert_harsh_set_data.tsv`, repeat-averaged) instead of the pool mean.
- Predictors x (label-free), from `results_exp30_tivar_v3_all_models/judge_trust_vector_{family}_avg.csv`, averaged across panels for shared configs. **Registered candidate list (9):** `ident`, `mono`, `weak`, `stab`, `varcorr_1_minus`, `varscore_1_minus` (each alone), `ti_var_v3`, GM = (ident·mono·weak·stab)^{1/4}, v1 = 0.30·ident + 0.30·mono + 0.25·weak + 0.15·stab. (v2 requires `anti`/`subtle` columns not present in the frozen CSVs — excluded, noted here.)

## Disclosure of already-seen results (this registration covers only what is NOT below)

- Frozen `ti_var_v3` vs y is already known to be ≈0/negative: per-family (exp43) and pooled/centered/unique (dir-22: pooled −0.124, unique-20 −0.075, real-14 −0.218, centered −0.029 p=0.87). The registered analyses therefore CANNOT claim novelty for the TI_var-vs-y direction; TI_var stays in the candidate list only for completeness of the LOO selection.
- All individual y values (per-config pool alignment) have been seen (results.json). No per-property x↔y correlation has been computed or seen. No LOO/selection analysis has been run.
- Controls' y are known negative (editdist −0.57, BAD −0.46 vs pool).

## Registered analyses

1. **Per-candidate screen (primary):** For each of the 9 candidates: Spearman(x, y) over the 14 real configs; two-sided permutation p (20,000 permutations of y, seed 42); Holm correction across the 9 tests.
2. **LOO selection-transfer test (secondary):** Leave-one-config-out over the 14 real configs. In each fold: on the 13 training configs, select the candidate (of 9) with max |Spearman|, record its sign; the left-out config's prediction is (sign × its candidate value). After 14 folds: predictive Spearman(predictions, y). Two-sided permutation p with 2,000 whole-pipeline permutations of y (seed 42).
3. **Sensitivity:** repeat 1 with y2 (strict-set anchor); repeat 1 on all 20 configs (controls included).
4. **Directional validity check:** controls (editdist/random/BAD) should rank low on y; report their y and each candidate's ability to rank controls below the real-config median.

## Decision criteria (fixed now)

- **(a) Re-anchor the methods paper:** ANY candidate reaches ρ ≥ 0.60 with Holm-corrected permutation p < 0.05 in analysis 1, OR the LOO predictive Spearman ≥ 0.50 with p < 0.05 in analysis 2.
- **(b) Measurement-lessons paper:** ALL candidates |ρ| ≤ 0.35 in analysis 1 AND LOO predictive Spearman ≤ 0.35.
- **(c) Underpowered / expand configs:** anything else (suggestive middle zone), OR (a)/(b) criteria conflict between y and y2 anchors.

## Provenance & guardrails

- Deterministic: seed 42 everywhere; pure Python/scipy; no LLM-provider calls; no `~/keys/*`.
- Inputs read-only: dirs 04/22 artifacts and `experiments/human_labels/`.
- This file is committed and pushed BEFORE `analysis.py` produces any number; results land in a separate later commit. Mega-QA chain (fresh-Claude verify → builder → fresh-agent; Codex still usage-capped until 2026-07-22 21:15) reviews both the code and the criteria application.
