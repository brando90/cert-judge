# EXP46 Pass-2 Results — Expanded Panel (n=32): Registered Verdict (b), Complete

**TLDR:** The pre-registered pass-2 (PREREG commit c5a621c, before results) is now **complete on n=32** (14 existing + 18 clean new configs: 12 metered gpt-5.3-codex/gpt-4o-mini + 6 GPT-5.6-Sol). All three registered routes to (a) FAIL, giving the formal **registered verdict (b)**: identity primary +0.129 (p=0.48); nine-candidate screen — no candidate reaches |ρ|≥0.50 with Holm p<0.05 (strongest: variance-stability index −0.391, Holm p=0.22); leave-one-out selection-transfer +0.242 (p=0.47). No label-free property signal provides stable transfer to the semantic-protocol target at adequate power. Feature pipeline drift-gated per candidate against the published exp30 vectors (6/7 reproduce at rank-Spearman ≥0.90; `stab` failed the reproduction check at 0.80 and was excluded).

Analysis: `pass2_full_screen.py` (+ `pass2_analysis.py` for the identity primary). Raw: `results/pass2_full_screen_results.json`. Seed 42, no LLM calls in analysis.

## Registered screen (n=32, real non-control configs)

| candidate | Spearman(·, y) | perm p | Holm p |
|---|---:|---:|---:|
| varscore_1_minus | −0.391 | 0.028 | 0.221 |
| ti_var_v3 | −0.362 | 0.043 | 0.298 |
| GM | −0.345 | 0.055 | 0.329 |
| v1 | −0.312 | 0.086 | 0.427 |
| weak | −0.289 | 0.108 | 0.430 |
| varcorr_1_minus | −0.182 | 0.312 | 0.936 |
| ident | +0.129 | 0.480 | 0.961 |
| mono | +0.054 | 0.769 | 0.961 |

- **Success bar (registered):** |ρ|≥0.50 AND Holm p<0.05. **No candidate meets it.**
- **LOO selection-transfer:** ρ=+0.242, perm p=0.468 — null.
- **Identity primary (pooled):** ρ=+0.146 (p=0.47) at n=26; +0.129 at n=32. The pass-1 identity lead does not hold at power; note the pooled identity number masks opposite-sign subgroups (existing-14 diverse −0.618 = the same pass-1 observations, not an independent replication; new narrow panel +0.85 over a pseudo-replicated range with effective sample size well below its config count).

## What the screen shows honestly

Several variance/aggregate indices (`varscore_1_minus`, `ti_var_v3`, `GM`) are weak-to-moderate *negative* at n=32 (ρ ≈ −0.35 to −0.39) with raw permutation p<0.05, but **none survives Holm multiple-comparison correction, and none reaches the pre-registered |ρ|≥0.50 bar.** So there is a weak hint that higher variance-stability indices anti-track semantic alignment, reported descriptively — but no candidate qualifies as a usable certification signal under the pre-registered criteria. This is the registered negative outcome (b), not a positive discovery.

## Data quality / validity

- 18 new configs, all error rate <15% (metered 3–7%; Sol 0–1%). Drift gate: my recomputed features reproduce exp30's published columns at rank-Spearman ident 0.9985, mono 0.979, weak 0.995, varcorr 0.968, varscore 0.9985, ti_var 0.970 — all ≥0.90; `stab` 0.798 failed and was excluded from the screen (it was not a strong candidate).
- Metered spend ~$31 (OpenAI only; **no Opus, no anthropic_bm_key_koyejolab**). CLI (Sol) free, subscription-billed.

## Bottom line

Registered verdict **(b)**: the property-certification suite, calibrated on the original (partly lexical) protocol, does not yield a label-free signal that transfers stably to the semantic-protocol construct at adequate power. This is a complete, pre-registered negative-transfer result → the measurement-lessons paper.
