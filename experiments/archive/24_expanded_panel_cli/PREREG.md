# EXP46 (dir 24) — Pre-Registered Pass 2: Expanded-Panel Property→Semantic-Alignment Screen

**TLDR:** Registered BEFORE the x–y screen is computed (this file's commit precedes the results commit). Pass 1 (dir 23) returned registered outcome (c) "underpowered" at n=14 real configs, with one lead: identity compliance anti-correlates with pool (semantic-protocol) alignment (ρ=−0.539). Pass 2 expands the panel with new judge configs scored two ways (free subscription-CLI: Fable-5, GPT-5.6-Sol; cheap metered API: gpt-5.3-codex, gpt-4o-mini — NO Opus, NO anthropic_bm_key_koyejolab), then re-runs the same screen at higher n with a **forced (a)/(b) decision — no middle zone this time.**

## Question (unchanged from pass 1, higher power)

Across judge configurations, does any label-free property signal predict judge-level alignment to the revised-protocol five-rater pool (the semantic construct)? And specifically: does the pass-1 identity anti-correlation replicate at larger n?

## Data

- **Existing:** the 14 real configs from dir-22 (x = exp30 trust-vector features; y = pool-anchored item Spearman).
- **New (this experiment):** additional (model, prompt) configs, each scored on the SAME item set (exp16 ethan-panel 72 rows + identity variants + bug ladder, r3, seed 42) so features + y join identically. New models: `cli-fable`, `cli-sol` (subscription CLIs, $0 metered), `gpt-5.3-codex`, `gpt-4o-mini` (metered, OpenAI key only). New prompts: P2_FORMAL, P3_CONCISE, P7_STRICT_A, P13_HUMAN_ALIGN_STRICT, P14_HUMAN_ALIGN_V2, P16_ERIC_COMPARATIVE_TRACKED.
- Whichever scoring wave (CLI / metered) completes cleanly contributes its configs; a config enters the analysis only if its run has zero `_cli_failed` rows and reproduces on a 5% recompute spot-check. Target ≥26 real configs; report the actual n reached.
- x-features per new config computed by exp28 from its detail_rows (`ident,mono,weak,stab,varcorr_1_minus,varscore_1_minus,ti_var_v3`); y = Spearman(judge human_eval_union scores, pool mean) on aligned items, exactly as dir-22.

## Registered analyses (same estimators as dir-23 `analysis.py`)

1. **Primary — identity-sign replication:** Spearman(ident, y) over all real configs; two-sided permutation p (20,000 perms, seed 42). Pre-registered directional hypothesis from pass 1: ρ < 0.
2. **Screen:** the 9 candidates (`ident, mono, weak, stab, varcorr_1_minus, varscore_1_minus, ti_var_v3, GM, v1`) vs y; Holm across 9; permutation p each.
3. **LOO selection-transfer** (dir-23 procedure) over the expanded real-config set.
4. **Sensitivity:** strict-set anchor y2; CLI-only vs metered-only subgroup screens (do the two scoring backends agree in sign? — a cross-method robustness check the pass-1 panel could not do).

## Decision criteria (fixed now — forced binary, no (c))

- **(a) Signal exists → re-anchored methods paper.** Primary: Spearman(ident, y) significant (perm p < 0.05, |ρ| ≥ 0.45) with the pass-1 sign; OR any screen candidate |ρ| ≥ 0.50 Holm-p < 0.05; OR LOO ≥ 0.50 p < 0.05. (The identity signal counts for (a) whether its predictive sign is + or −: a reliable −ident predictor is still a usable, novel certification signal.)
- **(b) No usable signal → measurement-lessons paper.** None of the (a) conditions met at the achieved n.
- If the achieved n < 20 (both waves degrade), report (b)-provisional and name the power shortfall explicitly rather than inventing a third bucket.

## Guardrails

- Deterministic seed 42; the analysis reuses dir-23 `analysis.py` estimators verbatim (imported, not reimplemented) to prevent drift.
- No metered spend beyond the user-approved cheap OpenAI+Mistral scope; Opus / anthropic_bm_key_koyejolab never loaded. CLI calls are subscription-billed.
- Data-quality gate: any config with CLI-failure rows or a failed recompute spot-check is excluded and logged, never silently kept.
- This file committed + pushed before `pass2_analysis.py` produces any x–y number.
