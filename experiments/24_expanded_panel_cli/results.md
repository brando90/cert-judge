# EXP46 Pass-2 Results — Expanded Panel (n=26): Identity Primary Fails (a); Screen + LOO Pending

**TLDR:** The pre-registered expansion (n=14 → 26) has the identity primary fail the (a) bar — pooled Spearman(ident, pool-alignment y) = **+0.146 (n=26, perm p=0.469)** — but this pooled sample correlation masks **opposite-sign subgroup correlations**: the diverse existing-14 configs give **−0.618** (these are the original pass-1 observations, not an independent replication), and the 12 new homogeneous prompt-variant configs give **+0.853** over a narrow, pseudo-replicated range. The accurate reading is **configuration/population heterogeneity — no evidence of a stable, population-independent label-free signal**. This points to the measurement-lessons paper (outcome b). **Formal registered verdict is NOT yet complete:** PREREG defines (a) as identity OR the 9-candidate screen OR LOO; only the identity primary is computed here, so the screen + LOO must run on the full panel before (b) can be declared registered (morning, with the n≈32 Sol panel). Drift gate passed (my ident ≡ exp30 ident, rank-Spearman 0.9985); all 12 new metered configs clean (3–7% error).

**Heterogeneity is the headline, not the pooled number:**

| panel | n | sample Spearman(ident, y) | note |
|---|---:|---:|---|
| existing (diverse: controls→strong, ident 0.40–0.92) | 14 | **−0.618** | the original pass-1 observations (same data, not a new replication) |
| new (homogeneous: 2 models × 6 prompts, ident 0.73–0.94) | 12 | **+0.853** | restricted range + prompt pseudo-replication (effective n well below 12) |
| **pooled (pre-registered primary)** | **26** | **+0.146** | **p=0.469 — fails (a); opposite-sign subgroups cancel** |

The pass-1 negative sample correlation is on a *diverse* panel; the new *narrow strong-judge* panel gives the opposite sign — so identity is not a reliable, population-independent certification signal. The +0.853 is over ident ∈ [0.73, 0.94] with six near-duplicate prompts per model (effective n well below 12), so it is not robust evidence of a positive law either. Net: sign-heterogeneous, no stable signal — which supports the measurement-lessons framing once the screen + LOO confirm no other candidate reaches (a).

Prereg: `PREREG.md` (commit c5a621c, before results). Analysis: `pass2_analysis.py` (drift-gated). Raw: `results/pass2_results.json`. Seed 42, no LLM calls in analysis.

## Powering trajectory (pooled)

| n | panel | Spearman(ident, y) | perm p |
|---:|---|---:|---:|
| 14 | pass-1 (dir 23) | −0.539 | 0.051 |
| 26 | +12 metered (pass-2, pooled) | +0.146 | 0.469 |

The pre-registered pooled primary fails the (a) bar. But per the subgroup table above, this is a sign-heterogeneity result, not a demonstration that ident is unrelated to y — the observed sample correlations have opposite signs across the two subgroups, so no single stable law is supported. That is the answer to the pass-1 open question: the lead is not a reliable, population-independent signal. (The registered screen + LOO on the full panel still run before the formal (b) verdict is complete.)

## Data provenance & quality

- **New configs (12, metered, ~$31, OpenAI key only — no Opus, no anthropic_bm_key_koyejolab):** gpt-5.3-codex × 6 prompts + gpt-4o-mini × 6 prompts, scored on the identical exp16 item set (72 human panel + 96 identity + 120 bug, r3, seed 42). Per-config error rate 3–7% (responses-API timeouts → retried; residual error rows are random noise, not systematic), all under the 15% exclusion gate → all 12 retained.
- **Existing 14:** recomputed from their detail_rows for a uniform pipeline.
- **Drift gate (validity):** my self-computed `ident` reproduces exp30's published `ident` at rank-Spearman **0.9985** (max abs diff 0.024, n_shared=20) → feature computation faithful.
- **CLI note:** Fable-5 configs excluded (Claude subscription credit-exhausted → cli_failed, auto-gated). GPT-5.6-Sol configs (wave 2, free, working post-reset) are still scoring → a morning refinement to n≈32 with a CLI-vs-metered cross-method sign check.

## Direction is (b), not (c); formal registered (b) pending screen + LOO

Pass 1 ended (c) "underpowered" because n=14 could neither confirm nor rule out the ident lead. Pass 2 was pre-registered with a **forced (a)/(b)** and n≈26: the pooled identity primary fails the (a) bar (|ρ|≥0.45, p<0.05), and the subgroup analysis shows why a methods claim is unsafe — the observed sign is population-dependent (−0.62 diverse vs +0.85 narrow/pseudo-replicated). A candidate signal whose sample sign reverses across judge populations is not a usable, population-independent criterion. The other eight candidates were all weaker than ident at n=14 (|ρ|≤0.27), but PREREG's (a) is disjunctive (identity OR screen OR LOO), so the registered (b) verdict is only complete once the full 9-candidate screen + LOO are run on the panel (with the n≈32 Sol configs) and confirm none reaches (a) — a required registered step, not optional confirmation.

## Scientific reading

The property-certification suite was calibrated against the original annotation protocol, which the dir-22 audit showed partly rewards lexical overlap. Under the semantic-protocol pool, the identity signal's relationship to alignment is **not stable across judge populations** — strongly negative on the diverse original panel, positive on a narrow homogeneous prompt-variant panel, and null when pooled. A signal whose sign depends on which judges you look at cannot serve as a population-independent certification criterion. This is the honest, powered answer: property certification as currently formulated does not yield a stable transfer signal to the semantic construct — a cautionary, reproducible measurement-science result, and the reason we frame the paper around calibration + audit rather than a transfer claim.
