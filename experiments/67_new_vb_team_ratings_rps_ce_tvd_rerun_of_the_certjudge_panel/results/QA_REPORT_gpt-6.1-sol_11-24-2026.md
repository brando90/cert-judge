# CertJudge independent QA — 11-24-2026

As-of: 11-24-2026 (PST).

**Headline numbers reproduce. Preregistration compliance is not clean.** Independent code: `qa_out/check.py`; results: `qa_out/recomputed.json`; execution log: `qa_out/check.log`; input hashes: `qa_out/input_sha256.txt`. Python 3, NumPy 2.2.6, SciPy 1.17.1. No author-code imports/execution, network, or model calls. Inputs were not modified.

## C1–C5: independent recomputation

PASS tolerances: point estimates ≤0.02; interval endpoints ≤0.08. Counts checked exactly. Series below are the requested P8_STRICT_B series.

| Check | My result | Author | Result |
|---|---|---|---|
| C1 Codex Spearman | −0.240814 | −0.24 | PASS |
| C1 Opus Spearman | −0.213309 | −0.21 | PASS |
| C1 Qwen Spearman | −0.346506 | −0.35 | PASS |
| C1 H_vb items / tasks | 59 / 20 | 59 / 20 | PASS |
| C2 Codex 95% interval | [−0.603413, +0.201256] | [−0.60, +0.20] | PASS |
| C2 Opus 95% interval | [−0.509239, +0.110554] | [−0.51, +0.11] | PASS |
| C2 Qwen 95% interval | [−0.588974, −0.061661] | [−0.59, −0.06] | PASS |
| C3 T05/T08 Spearman | 0.624268 (100 paired items) | 0.62 (100) | PASS |
| C3 exact agreement | 62/100 = 0.620000 | 0.62 | PASS |
| C3 within-1 agreement | 100/100 = 1.000000 | 1.00 | PASS |
| C3 returned ratings at 5 | 180/247 = 0.728745 | 0.73; JSON 0.729 | PASS |
| C4 constant LOTO RPS | 0.173727359 | 0.1737 | PASS |
| C5 paper-vs-H_vb Spearman | −0.042346 (59 items) | −0.04 (59) | PASS |

**Methods / differences, one line per check:**
- **C1:** Parsed five participant TSVs independently, applied the unsafeMultiply alias, intersected with the common 72-item judge universe, retained ≥4 ratings, and correlated `score_mean` with item human means; no substantive method difference. Retained 268 ratings: 27 items with four, 32 with five.
- **C2:** Independently resampled 20 whole gold-file tasks with replacement, 2,000 draws, NumPy seed 0; recomputed tied-rank Spearman each draw, percentile endpoints. All draws finite; same specified estimator.
- **C3:** Joined by `item_id`, never `candidate_file`; retained the T06 note-bearing row. Counts reproduce: T05=100, T08=100, T12=30, T06=16, V04=1; 100 items / 25 tasks. Only difference is rounding.
- **C4:** Training marginal pools every individual rating outside the held-out task, adds 0.5 to each category, and scores each held-out empirical distribution with all five normalized expected-RPS cut points; equal item weighting. Same frozen definition, independently implemented.
- **C5:** Averaged the two paper passes, then correlated with H_vb means on shared items. ORIGINAL contains three conflicting duplicate keys (json_decoder agents 0–2, scores 1 then 2); author's last-row-wins convention is unstated, but these items are outside H_vb and first/last/within-pass averaging all give the same C5 result.

## C6: preregistration audit — FAIL (compliance, not headline arithmetic)

**Actual deviations / contradictions:**
1. **Frozen population count:** PREREG says H_vb has **60** items; T1/T3 and the ≥4-rating rule give **59**. `13_MyUppercase__agent1.lean` has only three participant ratings; the other 12 excluded judged items have none. The rule was followed, but the frozen inventory was wrong; label this correction rather than silently changing 60 to 59.
2. **Intervals:** PREREG says every bootstrap interval uses **2,000** draws, seed 0. `run_old.py` supplies **500** for A5/T7. T7's task-bootstrap description conceals this deviation. C2 itself complies.
3. **Learning-curve endpoint:** A4 freezes random subsets at k=4,8,12,16,20. T5 substitutes a full-data bootstrap at k=20 (explicitly disclosed in its caption). The frozen all-20 subset spread is **zero** in the CSV; bootstrap widths are **0.805 / 0.620 / 0.527**. These are different estimands, not a single learning curve. The planned spread×sqrt(k) diagnostic is not reported.
4. **Unlabelled additions:** T4's pooled/within-set-rank alignment comparisons and T6's pooled within-set-rank learning curve go beyond the frozen pooled-counts/new-set-baselines plan. No dated, labelled addendum appears in the supplied preregistration or tables. Treat them as exploratory, not preregistered confirmation.
5. **Calibration definition:** A2 describes CE-fit as maximum likelihood. `lib.py` instead adds `1e-3 * beta²` to average negative log likelihood, then clips predicted category probabilities at 0.001 and renormalizes. This is regularized, postprocessed fitting; those choices were not frozen. Fits were not rerun here.
6. **Baseline definition:** A6 freezes normalized edit **distance**; `run_new.py` uses Levenshtein normalized **similarity**. This reverses scalar Spearman's sign relative to distance. T4's “edit-distance baseline” needs its orientation stated explicitly; source files needed to recompute it are absent.

**Ordering / secondary status / omissions:** T1 and T2 correctly put RPS, CE, TVD first; H_vb remains primary. T7 reverses that order by listing secondary scalar Spearman first. Nothing supplied explicitly redefines Spearman or H_paper as primary. However, T1 omits the planned H_paper secondary panel and CE/TVD/Pearson intervals (available in the CSV), and T7/code omit the planned TI-versus-H_paper analysis. Tables also omit the planned headline leave-one-task-out range, tie diagnostic, and new random/CONST baseline results; some exist in JSON outputs. These are reporting/coverage gaps, not evidence of a target switch. A4 subset percentile spreads were explicitly planned: their use at k<20 is not itself a bootstrap violation.

### Predictions: what actually fails?

| Prediction | Evidence and judgment |
|---|---|
| **P1: most raw series no better than CONST** | **Supported independently:** all **24/24** raw RPS values exceed CONST 0.173727; range **0.193084–0.436936**. Not falsified. |
| **P2: CE-fit beats Pearson-fit in a majority; best series beat CONST, mostly inconclusive intervals** | **Consistent with author outputs only:** **13/24** beat Pearson-fit on RPS; **18/24** beat CONST by point estimate, **0/24** have intervals wholly below zero. Do not call P2 falsified because the family-averaged CE RPS is slightly worse than Pearson RPS: that is not the frozen majority-of-series criterion. Fits remain unchecked. |
| **P3: half-width >0.2 at 20 tasks; approximately 1/sqrt(k)** | **Wide-interval part supported independently:** half-widths **0.4023 / 0.3099 / 0.2637**. Scaling is not established: reported subset spreads collapse to zero at k=20, while T5 replaces that endpoint with a bootstrap. Cannot confirm the full scaling prediction from these mixed estimands. |
| **P4: >60% at 5, moderate agreement, new reliability lower than H_vb** | **Partly falsified independently:** 72.8745% at 5 supports concentration. “Moderate” has no frozen threshold; observed pairwise rho=0.6243. Using the author's Spearman–Brown proxy, new reliability **0.768676 > old 0.699606**, not lower (T3: 0.77 > 0.70). This reverses the predicted ordering; it is not a significance test or proof of universally higher reliability. |
| **P5: TI does not track proper-score alignment** | **Descriptively challenged, not independently established:** T7 reports negative TI correlations with proper-score alignment, including Qwen RPS/CE **−0.71**, TVD **−0.74**, permutation p **0.058/0.058/0.046**. A blanket “does not track” is incompatible with that pattern. No frozen effect/significance criterion or multiplicity rule defines falsification; do not claim broad statistical rejection. TI inputs/tests were not independently checked. |

**Correction priority:** P0—disclose the population correction, 500-draw TI intervals, and altered calibration definition; P1—label exploratory tables and separate subset spreads from bootstrap uncertainty. The confirmed falsified prediction component is **P4's lower-reliability ordering**; P5 is descriptive counterevidence, and P3's scaling remains unresolved. P1 and P2 should not be listed as falsified on the available evidence.

## NOT CHECKED

- CE-fit/Pearson-fit optimization, held-out predictions, paired intervals, and resulting winner counts independently; only recounted the supplied output rows for P2.
- TI source values (not supplied), permutation tests, bootstrap intervals, leave-one-judge-out ranges, or multiplicity-adjusted inference.
- Learning-curve resampling, new/pooled edit-distance or random baseline results, new agreement interval/kappa, and other non-headline proper-score metrics. Inspected their definitions/output where needed for C6; did not independently reproduce them.
- Historical preregistration timing/commit provenance, live Sheets completeness, de-identification correctness, source Lean files, or whether the author's model family differs from this reviewer's: the supplied folder cannot establish these.

VERDICT: Headline numbers reproduce (C1–C5 all PASS); preregistration/reporting deviations require disclosure, and P4's predicted lower new-set reliability is contradicted by the reported estimator.
