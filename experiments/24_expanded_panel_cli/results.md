# EXP46 Pass-2 Results — Expanded Panel (n=32): Registered Verdict (b), Complete

**TLDR:** The pre-registered pass-2 (PREREG commit c5a621c, before results) is now **complete on n=32** (14 existing + 18 clean new configs: 12 metered gpt-5.3-codex/gpt-4o-mini + 6 GPT-5.6-Sol). All three registered routes to (a) FAIL, giving the formal **registered verdict (b)**: identity primary +0.1285 (p=0.4805); nine-candidate screen — no candidate reaches |ρ|≥0.50 with Holm p<0.05 (strongest: variance-stability index −0.3911, Holm p=0.2484); leave-one-out selection-transfer +0.2416 (p=0.4908). No label-free property signal met the registered transfer criterion at n=32. Feature pipeline drift-gated per candidate against the published exp30 vectors (6/7 reproduce at rank-Spearman ≥0.90; `stab` failed the reproduction check at 0.7978 and was excluded from the eight-candidate drift-gated sensitivity screen, not from the pre-registered nine-candidate primary).

Analysis: `pass2_full_screen.py` (+ `pass2_analysis.py` for the identity primary). Raw: `results/pass2_full_screen_results.json`. Seed 42, no LLM calls in analysis.

## Registered screen (n=32, real non-control configs)

| candidate | Spearman(·, y) | perm p | Holm p |
|---|---:|---:|---:|
| varscore_1_minus | −0.3911 | 0.0276 | 0.2484 |
| ti_var_v3 | −0.3622 | 0.0426 | 0.3408 |
| GM | −0.3453 | 0.0548 | 0.3836 |
| v1 | −0.3116 | 0.0855 | 0.5130 |
| weak | −0.2895 | 0.1076 | 0.5380 |
| varcorr_1_minus | −0.1824 | 0.3121 | 1.0000 |
| stab | −0.1763 | 0.3347 | 1.0000 |
| ident | +0.1285 | 0.4805 | 1.0000 |
| mono | +0.0537 | 0.7688 | 1.0000 |

- **Success bar (registered):** |ρ|≥0.50 AND Holm p<0.05. **No candidate meets it.**
- **LOO selection-transfer:** ρ=+0.2416, perm p=0.4908 — null.
- **Identity primary (pooled):** ρ=+0.146 (p=0.47) at n=26; +0.129 at n=32. The pass-1 identity lead does not hold at n=32; note the pooled identity number masks opposite-sign subgroups (existing-14 diverse −0.618 = the same pass-1 observations, not an independent replication; new narrow panel +0.85 over a pseudo-replicated range with effective sample size well below its config count).

## What the screen shows honestly

Several variance/aggregate indices (`varscore_1_minus`, `ti_var_v3`, `GM`) are weak-to-moderate *negative* at n=32 (ρ ≈ −0.35 to −0.39) with raw permutation p<0.05, but **none survives Holm multiple-comparison correction, and none reaches the pre-registered |ρ|≥0.50 bar.** So there is a weak hint that higher variance-stability indices anti-track semantic alignment, reported descriptively — but no candidate qualifies as a usable certification signal under the pre-registered criteria. This is the registered negative outcome (b), not a positive discovery.

## Data quality / validity

- 18 new configs, all error rate <15% (metered 3–7%; Sol 0–1%). Drift gate: my recomputed features reproduce exp30's published columns at rank-Spearman ident 0.9985, mono 0.979, weak 0.995, varcorr 0.968, varscore 0.9985, ti_var 0.970 — all ≥0.90; `stab` 0.7978 failed. The pre-registered nine-candidate primary remains unchanged; an eight-candidate sensitivity screen excludes `stab` and has strongest Holm p=0.2208.
- Metered spend ~$31 (OpenAI only; **no Opus, no anthropic_bm_key_koyejolab**). CLI (Sol) free, subscription-billed.

## Bottom line

Registered verdict **(b)**: at n=32, no label-free signal met the pre-registered transfer criterion for the semantic-protocol construct. This is a complete, pre-registered negative-transfer result → the measurement-lessons paper.
