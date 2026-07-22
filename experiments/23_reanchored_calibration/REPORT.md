# EXP45 (dir 23) — Pre-Registered Re-Anchoring Analysis: Registered Outcome (c)

**TLDR:** Under the pre-registered criteria (PREREG.md, commit 241f3de, fixed before computation), the outcome is **(c) — suggestive middle zone / underpowered** on both anchors: no candidate reaches the (a) bar (ρ≥0.60, Holm p<0.05; or LOO ≥0.50 with p<0.05), and the flat-null (b) bar (all |ρ|≤0.35 and LOO ≤0.35) is broken by one coherent signal — **identity compliance anti-correlates with semantic alignment** (ident: ρ=−0.539 pool-anchor / −0.517 strict-anchor, raw p=0.051/0.062, Holm-corrected 0.46/0.56, n=14) with LOO selection-transfer +0.539 (p=0.155, folds essentially selecting −ident). Interpretation (post-hoc, marked as such): lexical-leaning judges ace P1 identity but misalign with the semantic construct — the strongest hint yet that the index needs re-derivation, not just re-weighting, under the revised protocol. Registered next step for (c): expand the config panel (~$100–300 judge scoring; needs Brando's approval) and adjudicate the ident sign plus any recovered positive signal in a second pre-registered pass.

Provenance: analysis run 2026-07-21 evening, results committed AFTER prereg 241f3de; deterministic seed 42; no LLM calls; inputs read-only. Reproduce: `python3 analysis.py` (~11 min: 4 screens × 9 candidates × 20k permutations + 2k whole-pipeline LOO permutations).

## Registered results

**Analysis 1 — screen, 14 real configs, pool anchor (ρ / raw perm p / Holm):**
ident **−0.539 / 0.051 / 0.459** · v1 −0.266/0.36/1.0 · GM −0.226/0.44/1.0 · ti_var_v3 −0.218/0.46/1.0 · stab −0.162/0.57/1.0 · varscore −0.143/0.63/1.0 · weak −0.095/0.75/1.0 · varcorr −0.026/0.93/1.0 · mono +0.020/0.95/1.0

Per the PREREG disclosure, the ti_var_v3-vs-y direction was already known to be ≈0/negative before registration (dir-22 real-14: −0.218); its row above reproduces that disclosed value and is consistency, not novel evidence.

**Analysis 2 — LOO selection-transfer:** predictive Spearman **+0.539**, permutation p **0.155** (2k whole-pipeline perms). Folds predominantly select `ident` with negative sign — the LOO result is the −ident relationship transferring across folds, not an independent positive signal.

**Analysis 3a — strict-set anchor (sensitivity):** same shape; ident −0.517/0.062/0.555; all others |ρ|≤0.22. Anchors agree → no (c)-by-conflict; (c) arises from the middle-zone criteria on both.

**Analysis 3b — all 20 configs (controls included):** ident **−0.642/0.0034/0.031** — the only Holm-significant row in any screen, but it mixes populations by design: five of six controls are lexical/stringy with high ident (0.86–0.95) and mostly negative y, so adding them amplifies the same anti-correlation rather than independently confirming it on real judges (the registered population for the decision criteria remains the 14 real configs). varcorr −0.338/0.145; all other candidates Holm-ns.

**Analysis 4 — directional validity:** controls' pool-alignment is appropriately low/negative (editdist −0.566, Codex-BAD −0.457, Opus-BAD −0.308, Qwen-BAD −0.259; LeanStral-BAD +0.032 and random +0.181 are the two soft spots). Property signals do detect controls: ti_var_v3/GM/v1/weak rank 5/6 controls below the real-config median (mono 4/6) — the suite flags degenerate judges; what it does not do (at n=14) is rank the *real* judges by semantic alignment.

## Registered verdict

- (a) bar: not met (no ρ≥0.60 with Holm<0.05; LOO 0.539 ≥0.50 but p=0.155 ≥0.05).
- (b) bar: not met (ident |−0.539| > 0.35; LOO 0.539 > 0.35).
- **Outcome: (c)** on pool anchor, strict anchor, and combined — recorded in `results/results.json` `registered_verdict` and applied mechanically by `analysis.py::apply_criteria`.

## Post-hoc interpretation (NOT registered; labeled as such)

The negative ident association is directionally coherent with the whole audit arc: the old-protocol labels partly rewarded lexical similarity; P1 identity (max score for X vs X) is the property easiest for lexical judges to ace; under the semantic pool, those judges do worst. If the expanded test confirms it, the certification suite's fix is qualitative — identity compliance alone cannot enter a semantic trust index positively; semantic-invariance probes (e.g., alpha-renaming stability, where lexical judges fail) should carry more of the load. This is a testable prediction for the second pre-registered pass, not a claim.

## Registered (c) action

Expand the judge-config panel (target ≥30 real configs across families; ≈$100–300 of judge scoring through the existing pipeline, or subscription-CLI-billed; requires Brando's explicit approval per Hard Rule 9), then run a second pre-registered pass with: (i) the ident-sign hypothesis, (ii) the 9-candidate screen, (iii) config-level train/test — one labeling protocol end-to-end.
