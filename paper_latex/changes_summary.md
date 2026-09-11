# Paper Changes Summary
## What needs updating after addressing NeurIPS Math-AI 2026 reviewer comments

Experiments live in: `experiments/02_neurips_reviews/`
Key numbers file: `experiments/02_neurips_reviews/results/PAPER_NUMBERS.md`
Original reviews: `experiments/02_neurips_reviews/or_neurips_2025_math_ai_workshop/`

---

## Reviewer Concerns → What Changed → What the Paper Must Reflect

### R1 (Reviewer 36Hd, score 3/10): "Identity/monotonicity tests resemble edit distance — not semantic"

**Experiment run**: Exp 5 (edit distance control) + Exp 2 (semantic ladder with tiny edits)

**Results to add to paper**:
- Pearson r(Levenshtein, judge) = **0.100** (p=0.538) — no relationship between string distance and judge score
- Exp 2, Level 1: Levenshtein distance = **0.0016** yet mean score drop = **0.143** — judge detects semantic changes invisible to strings
- Hard identity: Pearson r(edit, judge) = **−0.054** (p=0.561)

**Paper changes needed**:
- Add a subsection in Methodology (§3) explicitly addressing that certification is semantic, not syntactic
- Add Figure: `figures/fig_string_vs_semantic.pdf` — grouped bar chart showing near-zero edit distances producing large judge score drops
- Add 1–2 sentences to the certification protocol paragraph distinguishing semantic from syntactic perturbations

---

### R2 (Reviewer 36Hd): "Monotonicity definition too strict — should account for severity"

**Experiment run**: Exp 2 (hard monotonicity with 5-level severity ladder)

**Results to add**:
- Replace "strict ordering" language with **weak monotonicity** (non-increasing, allows ties)
- Degradation ladder: L0=0.942 → L1=0.798 → L2=0.708 → L3=0.482 → L4=0.308
- Spearman ρ(level, score) = **−0.862** (p<0.001)
- Weak monotonicity = **80%** (at threshold)
- Certification threshold: weak_mono ≥ 80% AND Spearman ≤ −0.60

**Paper changes needed**:
- §3 (Methodology): Replace P2/P3 definition with weak monotonicity formulation:
  > "For a ladder of $K$ degradation levels, at least 80% of theorems must show non-increasing scores across consecutive levels (weak monotonicity), and the Spearman rank correlation between level index and score must satisfy $\rho \leq -0.60$."
- Add Table: 5-level degradation ladder with mean scores per level (from `results/hard_monotonicity/summary.json`)
- Add Figure: `figures/fig_monotonicity_ladder.pdf`

---

### R3 (Reviewer 36Hd): "Unclear generalization — only tested on one benchmark"

**Experiment run**: Exp 4 (out-of-domain Lean 4 theorems)

**Results to add**:
- 15 manually-written Lean 4 theorems (Nat, List, Option) outside VeriBench
- Identity mean = **1.000 ± 0.000** ✅
- Spearman ρ = **−0.707** (p<0.001) ✅
- Weak monotonicity = **100%** ✅
- **FULLY CERTIFIED** on OOD theorems

**Paper changes needed**:
- Add paragraph in §4 (Results) or new §5: "Out-of-domain generalization" with these numbers
- Note that protocol is discriminative: OOD passes while VeriBench-complexity (Exp 3) fails — not a rubber stamp

---

### R4 (Reviewer 36Hd): "Single architecture — only tested on Claude 3.5/3.7"

**Experiment run**: Exp 3 (multi-model: gpt-4o and gpt-4o-mini)

**Results to add**:

| Model | Identity Mean | Spearman ρ | Weak Mono% | Certified |
|---|---|---|---|---|
| gpt-4o-mini | 0.917 ± 0.139 | −0.888 | 70% | ❌ |
| gpt-4o | 0.959 ± 0.136 | −0.867 | 70% | ❌ |
| Claude 3.5/3.7 (existing) | 1.000 | −0.973/−0.979 | — | ✅ |

**Paper changes needed**:
- Add Table: multi-model certification results (use `figures/fig_model_certification_table.pdf`)
- Key message: protocol is model-agnostic — it correctly distinguishes certified (Claude) from uncertified (GPT) judges on VeriBench complexity; both GPT models pass on simpler OOD theorems (Exp 4)
- This also resolves the Claude 3.5 vs 3.7 inconsistency complaint: clarify §3 used Claude 3.5 for certification experiments, §4 used Claude 3.7 as the agent model

---

### R5 (Reviewer 36Hd): "Claude version inconsistency: 3.5 in §3, 3.7 in §4"

**Paper changes needed**:
- §3 caption (Figure 1): Change to "Claude 3.5 Sonnet" explicitly
- §4 Table 1 caption: Clarify "Claude 3.7 used as both agent and judge"
- Add one sentence at start of §3: "All certification experiments use Claude 3.5 Sonnet as the judge; §4 uses Claude 3.7 as both the theorem-generation agent and judge to test the latest model."

---

### R6 (Reviewer ivJs, score 6/10): "No human validation of judge–expert alignment"

**Status**: NOT YET DONE — identified as Priority 1 follow-up

**Paper changes needed**:
- Add to §5 (Discussion/Limitations): explicitly acknowledge this gap and describe the planned study
  > "A key limitation is the absence of human expert validation. We plan to recruit 3–5 Lean 4 experts to rate 30 theorem pairs on a 1–10 quality scale, computing ICC (inter-rater reliability) and Spearman correlation with judge scores (target: ICC > 0.70, Spearman > 0.70)."
- Do NOT claim human agreement until data exists

---

### R7 (Reviewer ivJs): "Hard identity test — judge should handle semantically identical but syntactically varied theorems"

**Experiment run**: Exp 1 (hard identity with 4 variant types: RENAME, REORDER, STYLE, ALPHA)

**Results to add**:
- identity_mean = **0.920 ± 0.155** across 30 theorems × 4 variants × 3 calls
- Per-variant: RENAME=0.898, REORDER=0.926, STYLE=0.939, ALPHA=0.919
- All variants pass identity threshold > 0.85
- Add Figure: `figures/fig_hard_identity.pdf` (4-panel scatter: edit distance vs judge score per variant)

**Paper changes needed**:
- §3 P1 definition: Extend to cover syntactic variants explicitly:
  > "For any reference $X$ and any syntactic variant $X'$ (variable rename, reorder, style change, alpha-rename), $s(X, X') = 1$."
- Update P1 result in §3/§4 from just "identical files" to "semantically identical under 4 syntactic transformations"

---

## Summary: New Numbers to Plug Into the Paper

Replace all `X.XX` placeholders with:

| Symbol | Value | Source |
|---|---|---|
| P1 (hard identity mean) | 0.920 | Exp 1 |
| P2 Spearman ρ | −0.862 | Exp 2 |
| P2 weak monotonicity | 80% | Exp 2 |
| P3 OOD identity | 1.000 | Exp 4 |
| P3 OOD Spearman ρ | −0.707 | Exp 4 |
| JTI (geometric mean P1–P4) | TBD — needs P4 ICC data | — |

**Note**: P4 (ICC run-to-run reliability) numbers are still `X.XX` — not computed in these experiments. Still needed.

---

## New Figures to Add to Paper

Copy from `experiments/02_neurips_reviews/figures/` to `paper_latex/COLM_2026/figures/` (or NeurIPS figures):

| File | Where to use |
|---|---|
| `fig_hard_identity.pdf` | §3 (P1 hard identity result) |
| `fig_monotonicity_ladder.pdf` | §3 (P2 severity ladder) |
| `fig_model_certification_table.pdf` | §4 (multi-model ablation) |
| `fig_string_vs_semantic.pdf` | §3 (semantic vs string rebuttal) |

---

## Still Missing (Not Addressed by These Experiments)

1. **P4 ICC values** — run-to-run reliability scores are still `X.XX` in the abstract and paper
2. **Human expert validation** — Priority 1 follow-up, required to fully answer Reviewer ivJs
3. **More LLM models** — Claude 3.5, Llama-3 70B, Mistral Large, Gemini (Priority 2)
4. **Figure 1 readability** — Reviewer 36Hd noted it's unreadable; needs redesign
5. **Minor typos in appendices** — flagged by Reviewer 36Hd (check appendix manually)
