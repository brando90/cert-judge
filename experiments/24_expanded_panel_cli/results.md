# EXP46 Pass-2 Results — Expanded Panel (n=26): Registered Verdict (b)

**TLDR:** The pre-registered expansion (n=14 → 26) fails the (a) bar, but NOT as a clean null — the pooled Spearman(ident, pool-alignment y) = **+0.146 (n=26, perm p=0.469)** masks a **sign flip between subgroups**: the diverse existing-14 panel gives **−0.618** (pass-1 effect, replicated), while the 12 new homogeneous prompt-variant configs give **+0.853** over a narrow, pseudo-replicated range. The honest reading is **sign-unstable / judge-population-dependent — there is no stable, generalizable label-free property signal** for semantic alignment. **Registered verdict: (b)** — the measurement-lessons paper. Drift gate passed (my ident ≡ exp30 ident, rank-Spearman 0.9985); all 12 new metered configs clean (3–7% error).

**Heterogeneity is the headline, not the pooled number:**

| panel | n | Spearman(ident, y) | note |
|---|---:|---:|---|
| existing (diverse: controls→strong, ident 0.40–0.92) | 14 | **−0.618** | pass-1 effect replicated |
| new (homogeneous: 2 models × 6 prompts, ident 0.73–0.94) | 12 | **+0.853** | restricted range + pseudo-replication (effective n ≪ 12) |
| **pooled (pre-registered primary)** | **26** | **+0.146** | **p=0.469 — fails (a); subgroups cancel** |

The pass-1 lead does replicate on a *diverse* panel, but reverses on a *narrow strong-judge* panel — so it is not a reliable certification signal. The +0.853 is over ident ∈ [0.73, 0.94] with six near-duplicate prompts per model, so its effective degrees of freedom are ~2–4, not 12; it is not robust evidence of a positive law either. Net: no stable signal → (b).

Prereg: `PREREG.md` (commit c5a621c, before results). Analysis: `pass2_analysis.py` (drift-gated). Raw: `results/pass2_results.json`. Seed 42, no LLM calls in analysis.

## Powering trajectory (pooled)

| n | panel | Spearman(ident, y) | perm p |
|---:|---|---:|---:|
| 14 | pass-1 (dir 23) | −0.539 | 0.051 |
| 26 | +12 metered (pass-2, pooled) | +0.146 | 0.469 |

The pre-registered pooled primary fails the (a) bar. But per the subgroup table above, this is a sign-heterogeneity result, not a demonstration that ident is unrelated to y — the relationship exists in both subgroups with opposite signs, so no single stable law holds. That is itself the answer to the pass-1 open question: the lead is not a reliable, population-independent signal.

## Data provenance & quality

- **New configs (12, metered, ~$31, OpenAI key only — no Opus, no anthropic_bm_key_koyejolab):** gpt-5.3-codex × 6 prompts + gpt-4o-mini × 6 prompts, scored on the identical exp16 item set (72 human panel + 96 identity + 120 bug, r3, seed 42). Per-config error rate 3–7% (responses-API timeouts → retried; residual error rows are random noise, not systematic), all under the 15% exclusion gate → all 12 retained.
- **Existing 14:** recomputed from their detail_rows for a uniform pipeline.
- **Drift gate (validity):** my self-computed `ident` reproduces exp30's published `ident` at rank-Spearman **0.9985** (max abs diff 0.024, n_shared=20) → feature computation faithful.
- **CLI note:** Fable-5 configs excluded (Claude subscription credit-exhausted → cli_failed, auto-gated). GPT-5.6-Sol configs (wave 2, free, working post-reset) are still scoring → a morning refinement to n≈32 with a CLI-vs-metered cross-method sign check.

## Why (b), not (c)

Pass 1 ended (c) "underpowered" because n=14 could neither confirm nor rule out the ident lead. Pass 2 was pre-registered with a **forced (a)/(b)** and n≈26: the pooled primary fails the (a) bar (|ρ|≥0.45, p<0.05), and the subgroup analysis shows why a methods claim is unsafe — the sign is population-dependent (−0.62 diverse vs +0.85 narrow/pseudo-replicated). A certification signal that reverses sign across judge populations is not usable, which is the (a) failure the criteria are meant to catch. The other eight candidates were all weaker than ident at n=14 (|ρ|≤0.27); the full 9-candidate screen + LOO on the n≈32 Sol panel by morning is confirmation, not a decision dependency.

## Scientific reading

The property-certification suite was calibrated against the original annotation protocol, which the dir-22 audit showed partly rewards lexical overlap. Under the semantic-protocol pool, the identity signal's relationship to alignment is **not stable across judge populations** — strongly negative on the diverse original panel, positive on a narrow homogeneous prompt-variant panel, and null when pooled. A signal whose sign depends on which judges you look at cannot serve as a population-independent certification criterion. This is the honest, powered answer: property certification as currently formulated does not yield a stable transfer signal to the semantic construct — a cautionary, reproducible measurement-science result, and the reason we frame the paper around calibration + audit rather than a transfer claim.
