# How Ethan computes the Cert Index (v1, v2) from properties

**Short answer to the framing in `cc.md`:**
Yes — the index is a function over per-property scores in `[0,1]`, aggregated by a **fixed-weight arithmetic mean** (no learning, no fit to human labels). Your generalization

```
TrustIndex(corr_p1, corr_p2, corr_p3, stability_p4)
≈ TrustIndex(spearman_p1, pearson_p2, icc_p3, var_p4)
```

is the right *shape*, but the actual v1/v2 indices in the repo differ in a few ways. Two corrections and one addition:

1. **P1 is not a correlation.** It's `identity_mean` — the mean self-pair score. So it's `score_P1`, not `corr_P1`.
2. **P3 (spec-completeness ladder) is not in v1 or v2.** Only P1, P2 (twice), and P4 appear; v2 adds anti-baseline terms instead of P3.
3. **P2 contributes twice** — once as Spearman ρ on the bug ladder (mapped to `[0,1]`), once as a weak-monotonicity percentage.

## General form

$$
\text{CertIndex} \;=\; \sum_i w_i\, s_i,\qquad s_i\in[0,1],\qquad \sum_i w_i = 1
$$

Weights are **predefined** (code comment: *"not tuned on human outcomes"* — `exp_multi_judge_trend.py:274`). Human Spearman is the **validation target** the index is correlated against, not an input.

## v1: 4 components

| Component | Property | Flavor | Definition (clipped to [0,1]) | Weight |
|---|---|---|---|---|
| `ident` | P1 reflexivity | fixed-point score | `identity_mean` | 0.30 |
| `mono_rank` | P2 bug Spearman | correlation w/ expected behavior | `(-bug_spearman_r + 1) / 2` | 0.30 |
| `weak` | P2 weak-monotonicity | correlation w/ expected behavior | `bug_weak_mono_pct / 100` | 0.25 |
| `flip_stability` | P4 stability | reliability / 1−variance | `1 − flip_rate` | 0.15 |

$$
\text{CertIndex}_{v1} \;=\; 0.30\,\text{ident} + 0.30\,\text{mono\_rank} + 0.25\,\text{weak} + 0.15\,(1-\text{flip})
$$

## v2: 4 above (re-weighted) + 2 anti-baseline

| Added component | Flavor | Definition | Weight |
|---|---|---|---|
| `anti_str` | anti-Levenshtein | `1 − |Spearman(levenshtein, identity_probe_score)|` | 0.20 |
| `subtle` | subtle-bug sensitivity | `clip(mean(max(0, L0 − L1 drop)) / 0.25, 0, 1)` | 0.15 |

$$
\text{CertIndex}_{v2} = 0.20\,\text{ident} + 0.20\,\text{mono\_rank} + 0.15\,\text{weak} + 0.10\,(1-\text{flip}) + 0.20\,\text{anti\_str} + 0.15\,\text{subtle}
$$

**Why v2:** v1 has no defense against a pure edit-distance baseline. v2 adds `anti_str` (penalize lexical proxies) and `subtle` (reward drop on the easiest bug rung). Code comment: *"v2 index adds explicit anti-string behavior and subtle semantic sensitivity. This is intended to penalize lexical baselines (e.g., pure edit distance)"* (`exp_multi_judge_trend.py:293-295`).

## Component flavors (the part you intuited correctly)

Components decompose into three (v2: four) flavors:

| Flavor | Members | Question being asked |
|---|---|---|
| Correlation with expected behavior | `mono_rank`, `weak` | Does score drop monotonically as bugs increase? |
| Fixed-point / identity | `ident` | Is `score(file, file) ≈ max`? |
| Reliability / 1−variance | `flip_stability` | Are repeated calls consistent? |
| Anti-baseline (v2 only) | `anti_str`, `subtle` | Decorrelated from edit-distance? Drop on easiest rung? |

So your reading — "property correlations with expected behavior + reliability/variance, aggregated" — is right; the index just (a) replaces the P1 correlation with an identity-mean score, (b) drops P3, and (c) v2 adds anti-cheating terms.

## Where this lives in the code

- v1 formula: `experiments/04_veribench_validation/exp_multi_judge_trend.py:273-281`
- v2 formula: `experiments/04_veribench_validation/exp_multi_judge_trend.py:284-309`
- Same functions duplicated in `exp16_multi_judge_human_sets.py:320-336`
- Self-documented formula strings: `exp_multi_judge_trend.py:644-651`
- Reported trend numbers: `experiments/04_veribench_validation/results_final_stat_reliability_suite/summary.md`
  - v1 Spearman(cert → human): 0.810 (pass1, pass2), 0.881 (avg)

## Generalized abstraction (matching your `TI(...)` framing)

If you were to write a P1–P4 (and possibly P5–P7) version that *did* match your initial framing exactly:

```
TrustIndex(score_P1, corr_P2, corr_P3, stability_P4 [, robustness_P5, …])
  = w1 * score_P1
  + w2 * f(corr_P2)              # e.g. (-ρ + 1) / 2
  + w3 * f(corr_P3)              # not in current v1/v2
  + w4 * (1 - var_P4)
  + …
```

The current v1/v2 are a **simplified instantiation** with P3 omitted, P1 implemented as a mean rather than a correlation, and P2 split into two complementary signals (rank-corr + weak-mono).
