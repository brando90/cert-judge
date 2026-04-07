# Plan: Integrating Mutual Evaluation into the Judge Certification Framework

## Core Question

Can mutual evaluation be used to further increase the trustworthiness of a judge?

**Answer: Yes, but it adds _reliability_ (internal consistency, evaluator-independence), not _validity_ (correctness).** It fills a real gap in the current P1-P7 framework: no existing property tests whether the judging *process* (rubric + protocol) is robust to evaluator substitution. This is a genuinely new dimension of trustworthiness.

---

## What the Current Framework Measures vs. What's Missing

| Property | What it tests | Dimension |
|----------|--------------|-----------|
| P1 | Reflexivity — identical files get max score | Sanity check |
| P2 | Bug monotonicity — scores decrease with bugs | Correctness sensitivity |
| P3 | Spec monotonicity — scores decrease with missing specs | Completeness sensitivity |
| P4 | Low variance — same judge, same input, repeated runs | **Intra-rater** reliability |
| P5 | TVD-MI — discriminates same-source vs different-source | Discrimination |
| P6 | Human correlation | External validity |
| P7 | Prover correlation | Criterion validity |

**What's missing:** Inter-rater reliability — is the judging *process* stable across different evaluators executing the same rubric? P4 tests whether Judge-A is consistent with itself. Nothing tests whether Judge-A and Judge-B reach the same conclusions given the same rubric.

**Why this matters:** A rubric that only "works" with one specific LLM may be exploiting model-specific biases (e.g., Claude's tendency to give verbose explanations might accidentally align with a rubric clause). Mutual evaluation detects this.

---

## Proposed New Properties

### P8: Evaluator Replicability (Inter-Rater Reliability)

**Question:** Do independent evaluators applying the same rubric produce consistent conclusions?

**Protocol:**
1. Fix a set of N (candidate, gold) file pairs from the existing evaluation dataset.
2. Run K independent LLM judges (e.g., Claude Opus, GPT-4o, Gemini, Codex) — all given the *same* rubric/prompt template.
3. Each judge scores each pair, producing a K x N score matrix.
4. Compute:
   - **Cross-evaluator Spearman correlation** (pairwise between all judge pairs, then average): Do judges agree on *ranking*?
   - **Cross-evaluator conclusion stability**: For each pair, does the qualitative conclusion (e.g., "high quality" vs "low quality") change across judges? Measure as fraction of pairs where all judges agree on the qualitative bucket.
   - **Statistical robustness**: For key claims (e.g., "file A > file B"), compute p-values per evaluator. Flag claims where significance flips across evaluators (as in Robertson's BenchPress: p=0.069 vs p=0.002).

**Scoring:**
$$P_8 := \text{mean pairwise Spearman } \rho \text{ across evaluator pairs, normalized to } [0,1] \text{ via } \frac{\rho+1}{2}$$

**Why this adds trustworthiness:** If P8 is high, the rubric encodes a robust specification that any competent evaluator can execute consistently. If P8 is low, the rubric is ambiguous or model-dependent — you should not trust the judge's output even if P1-P7 look fine.

**Relationship to existing properties:**
- P4 tests intra-rater reliability (same judge, same input, multiple runs). P8 tests inter-rater reliability (different judges, same rubric, same input). Both are necessary; neither is sufficient alone.
- P8 low + P4 high = the rubric is ambiguous (different judges interpret it differently, but each is internally consistent). This is the most dangerous failure mode — you'd never catch it with P4 alone.

**Cost:** Requires running K different LLM judges. Expensive but can be done on a subset of the evaluation data.

---

### P9: Rubric Specification Robustness (via Evaluation-Welfare)

**Question:** Does the rubric produce structured, item-specific signal — or just noise that happens to look like a score?

**Protocol (following Robertson's mutual evaluation protocol):**
1. Take the existing rubric/prompt template for the judge.
2. Have the LLM judge(s) produce **deterministic coding annotations** (not just a single score, but answers to ~20-30 discrete yes/no or categorical questions about each file pair). These questions are derived from the rubric dimensions (e.g., "Does the candidate define the same type signature as the gold?", "Does the candidate prove the main theorem?", "Are auxiliary lemmas present?").
3. Build a **response matrix**: rows = file pairs (items), columns = coding questions, cells = annotations.
4. Compute **evaluation-welfare** (TVD-MI) on the response matrix: can a classifier distinguish genuine item-response vectors from shuffled ones?
5. If disagreement clusters emerge (as in Robertson's TMLR experiment), analyze them: do clusters correspond to different interpretations of the rubric, or to item difficulty?

**Scoring:**
$$P_9 := \text{clip}(\text{evaluation-welfare} / \tau, 0, 1)$$
where $\tau$ is a normalization threshold calibrated on the permutation null distribution (e.g., $\tau$ = 95th percentile of welfare under random relabeling).

**Why this adds trustworthiness:** P9 directly measures whether the judge's coding scheme is extracting real structural signal from the files. A high P9 means the judge's annotations contain genuine item-specific information. A low P9 means the judge is essentially generating random annotations — its final score is noise dressed up as measurement.

**Key insight from Robertson's talk:** The minority cluster scored *higher* on evaluation-welfare than the majority (slide 20: 0.092 vs 0.076). This means P9 does NOT reward majority agreement — it rewards *information content*. A small group of evaluators with a coherent, diagnostic interpretation is better than a large group with a diffuse one.

**Relationship to existing properties:**
- P5 already uses TVD-MI to test discrimination on same-source vs different-source pairs. P9 uses TVD-MI differently: it tests whether the *coding scheme itself* produces structured information, not whether the judge can distinguish pair types. P5 asks "can the judge tell same from different?" P9 asks "is the judge measuring anything real at all?"

---

## How P8 and P9 Relate to Each Other

```
P8 (Evaluator Replicability)         P9 (Rubric Specification Robustness)
─────────────────────────────        ─────────────────────────────────────
Tests: Do different judges agree?    Tests: Does the coding scheme carry signal?
Requires: Multiple LLM judges       Requires: Deterministic coding matrix
Detects: Rubric ambiguity (via       Detects: Noise vs. structure (via
         disagreement between                  evaluation-welfare)
         evaluators)
Analogous to: Inter-rater           Analogous to: Internal consistency
              reliability                        (Cronbach's alpha)
```

**The four quadrants:**

| | P9 High (structured signal) | P9 Low (noise) |
|---|---|---|
| **P8 High (judges agree)** | Best case: rubric is clear and produces real measurement | Red flag: judges agree on nonsense (possible shared bias) |
| **P8 Low (judges disagree)** | Informative disagreement: the rubric specification is ambiguous, but each interpretation is coherent | Worst case: unreliable process |

---

## Integration into JTI

Two options for integrating P8/P9 into the Judge Trust Index:

### Option A: Extend JTI to P1-P9
$$\text{JTI} = \sum_{k=1}^{9} w_k \cdot P_k$$
where $\sum w_k = 1$. Suggested weights: give P8 and P9 equal weight to P4 (stability), since they measure related but distinct reliability facets.

### Option B: Hierarchical — Mutual Evaluation as a Multiplier
$$\text{JTI}' = \text{JTI}_{1-7} \times \text{ME\_factor}$$
where $\text{ME\_factor} = \alpha \cdot P_8 + (1-\alpha) \cdot P_9 \in [0,1]$. This treats mutual evaluation as a "meta-reliability" gate: if the evaluation process itself is unreliable (low P8/P9), then even a high JTI from P1-P7 should be discounted.

**Recommendation:** Option B is more principled. P1-P7 measure properties of a single judge-rubric pair. P8-P9 measure properties of the *evaluation process*. They operate at different levels of abstraction, so multiplicative combination (a gate) makes more sense than additive (a weighted average).

---

## Implementation Plan

### Phase 1: Deterministic Coding Scheme Design
- Design 20-30 binary/categorical coding questions derived from the existing rubric for Lean 4 file pair evaluation.
- Examples:
  - "Does the candidate define the same top-level declarations as the gold?" (Y/N)
  - "Does the candidate prove the main theorem?" (Y/N)
  - "Are the type signatures compatible?" (Y/N/Partial)
  - "Does the candidate contain auxiliary lemmas not in the gold?" (Y/N)
  - "Is the candidate's proof strategy the same as the gold's?" (Same/Different/Can't determine)
- These questions should cover: logical preservation, mathematical consistency, formal quality, completeness.

### Phase 2: Response Matrix Collection
- For each (candidate, gold) pair, run the LLM judge with the coding scheme prompt.
- Collect responses into a structured matrix: rows = pairs, columns = coding questions.
- Run this with K >= 2 independent LLM judges (e.g., Claude Opus + GPT-4o).
- Also run each judge R >= 3 times per pair (for both P4-style intra-rater and P8-style inter-rater analysis).

### Phase 3: Compute P8 and P9
- **P8:** From the K judges' score vectors, compute pairwise Spearman correlations and conclusion stability.
- **P9:** From the response matrix, compute evaluation-welfare (TVD-MI) and test against permutation null.
- Implement in `py_src/cert_judge/mutual_evaluation.py`.

### Phase 4: Integration and Validation
- Add P8/P9 to the JTI computation in `hsj_scoring.py`.
- Run on existing evaluation data and compare JTI with and without P8/P9.
- Check: do P8/P9 catch failure modes that P1-P7 miss? (The key validation question.)

### Phase 5: Paper Writing
- Position in the paper as: "Mutual evaluation strengthens the reliability side of the JTI by testing evaluator-independence and rubric robustness — two dimensions that single-judge properties (P1-P7) cannot measure."
- Cite Robertson & Koyejo (arXiv:2508.05469) for TVD-MI and the mutual evaluation talk for the protocol.

---

## Honest Limitations

1. **Reliability != Validity.** P8 and P9 measure whether the judge is *consistently* measuring *something*. They cannot tell you whether that something is *correct*. You still need P6 (human correlation) and P7 (prover correlation) for validity. Mutual evaluation is necessary but not sufficient for trustworthiness.

2. **Cost.** Running multiple LLM judges is expensive. P8 requires at least K=2 independent judges; P9 requires deterministic coding with ~20-30 questions per pair. This is significantly more expensive than P1-P5.

3. **Evaluation-welfare scores are small.** Robertson's TMLR results show welfare scores of 0.06-0.09. These are statistically significant (via permutation null) but not large. The normalization threshold $\tau$ for P9 needs careful calibration.

4. **The "reliably wrong" failure mode.** P8 high + P9 high + P6/P7 low means all judges agree on a coherent but wrong assessment. This can happen when all judges share systematic biases (e.g., rewarding verbosity). Mutual evaluation cannot detect this.

5. **Rubric overfitting risk.** If you iterate on the rubric to maximize P8 (agreement across judges), you might converge on a rubric that is trivially unambiguous but uninformative. Robertson explicitly warns against this. The solution is to optimize P8 and P9 jointly — a rubric that produces high agreement AND high information content is non-trivially good.

---

## Summary

| What mutual evaluation adds | What it does NOT add |
|---|---|
| Inter-rater reliability (P8) | Correctness / validity |
| Rubric specification robustness (P9) | Protection against shared systematic bias |
| Diagnostic power (localize *why* a judge fails) | Guarantee of trustworthiness |
| Reference-free reliability measurement | Replacement for human/prover correlation |

**Bottom line:** Mutual evaluation fills a real gap in the current framework. P1-P7 characterize a single judge. P8-P9 characterize the *evaluation process*. Both layers are needed. A judge that passes P1-P7 but fails P8-P9 has a fragile rubric — its scores are an artifact of one particular model's interpretation, not a robust measurement. A judge that passes all nine properties is the most trustworthy you can get without full ground truth.
