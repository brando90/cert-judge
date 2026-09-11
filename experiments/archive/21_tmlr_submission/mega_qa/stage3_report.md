# MEGA QA — Stage 3 (clean-eyes final pass) — TMLR resubmission Candidate B

**Date:** 2026-08-01
**Reviewer:** Claude Fable 5 (fresh-eyes stage 3; assumed nothing from stages 1–2, re-verified everything below against artifacts)
**Target:** `paper_latex/TMLR_2026/main.tex` + `main.pdf` (29 pages, recompiled clean this pass)
**Untouched per instructions:** `TMLR_2026_submission/` (frozen), `TMLR_2026_resubmission/` (deprecated A′), the four OPEN items (343-vs-345 policy, author list, human-subjects form, two PROVENANCE-TODO tables).

## VERDICT: SHIP

Ship to Brando's human read + co-author window. No blockers found. Every number I spot-checked reproduces from its artifact (several independently recomputed, not just grepped). Six residual overclaim phrasings were found and fixed this pass (F1, mechanical, consistent with stage-2's established framing); the paper recompiles cleanly with no page-budget change. Remaining items are minor polish or Brando's open decisions.

---

## Findings (most severe first)

### F1 — FIXED: six residual "amortization achieved" phrasings survived the stage-2 softening sweep
Stage 2 softened the abstract/intro/contributions ("aims to amortize", "is designed to extend") but missed six spots that still asserted amortized screening as an achieved property — exactly the claim the n=32 pre-registered null says was not established. Fixed in place (minimal edits, same framing vocabulary stage 2 already used), recompiled with `latexmk -g -pdf`:

| Location (pre-fix line) | Was | Now |
|---|---|---|
| §2 LLM-as-a-Judge (151) | "keeps humans as the measurement anchor but **amortizes** re-measurement … checks **that screen** future judge configurations" | "**aims to amortize** … checks **intended to screen**" |
| §5.3 closing (385) | "**so new judge configurations can be compared** by automated property checks" | "so, **within the calibration construct**, new judge configurations can be compared…" |
| §5.4 takeaway (415) | "This supports amortized evaluator validation when…" | "…amortized evaluator validation **on the calibration construct** when…" |
| App. B peer-prediction (684) | "our calibration protocol **amortizes** the human-annotation cost" | "**is designed to amortize**" |
| App. B Specialist (698) | "Property certification instead **amortizes** across judge configurations" | "instead **aims to amortize**" |
| App. B Vericode (754) | "a calibrated, semantics-sensitive judge **that enables** scalable oversight" | "**intended to enable** scalable oversight" |

Recompile result: exit 0, **29 pages** (unchanged), 0 overfull boxes, no new warnings, References still start on page 11.

After these fixes I re-swept: no remaining instance of (a) amortized/label-free screening asserted as achieved, (b) statistical power asserted without analysis ("power" appears only as the registered "underpowered" outcome and "at this power" scoping the null — both correct), (c) the n=32 null stated as proof of no signal (all statements are scoped to "at the registered success bar / at this power"). Left intact as legitimate protocol-design descriptions: §1 line "aims to amortize" (already softened), contribution 1 ("design goal is that…"), Table 1 caption ("can be screened automatically" = the checks are computable label-free, which is factually true), §6 "We present an amortized protocol… calibrate once… then screen new evaluators automatically" (immediately followed by the negative-transfer caveat in the same paragraph).

### F2 — Numeric spot-check: ALL PASS (verified against artifacts, several independently recomputed)

| Claim in paper | Artifact | Result |
|---|---|---|
| Trio 0.833 / 0.905 / 0.738 (abstract, contrib 2, §5.3, Table 2, App. H) | `results_exp28_varaware_codex_{avg,pass1,pass2}/summary.json → correlations.rho_TI_vs_human` | ✓ 0.8333 / 0.9048 / 0.7381 |
| All 9 cells of Table 2 (incl. Opus 0.810/0.595/0.643, Qwen 0.476/0.857/0.905) | same, opus/qwen dirs | ✓ exact; the stage-2 Qwen-pass2 fix (0.905→0.857) is correct — artifact says 0.8571 |
| Bootstrap CIs [0.24,1.00]/[0.41,1.00]/[0.11,1.00], perm p 0.017/0.005/0.045, seed 42, 10k | **independently recomputed** from `judge_trust_vector.csv` (n=8), pure-Python Spearman, seed 42, 10k resamples | ✓ CIs match exactly to 2dp; perm p recomputed 0.015/0.004/0.045 — within Monte-Carlo noise of a different RNG stream (SE ≈ 0.0013 at p≈0.017). No machine-readable artifact exists for these (only `TMLR_REVISION_BACKLOG.md` note of the 2026-07-29 recompute); my recompute now constitutes independent confirmation. |
| "six of nine family/pass combinations exceed 0.7" | Table 2 values | ✓ exactly 6 |
| v2→TI_var per family 0.476→0.833, 0.143→0.643, 0.500→0.905; GM worst-family 0.714 vs 0.643; TI_var higher cross-family mean | Table 3 + arithmetic | ✓ (GM mean 0.786 < TI_var mean 0.794) |
| P3 strongest property 0.747, P2 second 0.714 | `results_exp17_final_robust_avg/summary.json` | ✓ 0.7470 / 0.7143 (P1 −0.024, P4 0.135 — "weaker standalone" claim also holds) |
| Weight sweep 0.762→0.881 in-sample | `results_exp21_cert_index_sweep/median/summary.md` | ✓ |
| EXP46: strongest ρ=−0.3911 Holm p=0.2484; LOO ρ=+0.2416 p=0.4908; identity +0.13 p=0.48; subgroups −0.62 / +0.85; drift gate 6/7 pass, stab fails at 0.80; verdict (b); n=32; seed 42 | `experiments/24_expanded_panel_cli/results/pass2_full_screen_results.json` | ✓ all (−0.3911/0.2484; 0.2416/0.4908; ident 0.1285/0.4805; existing −0.618, metered 0.853; stab gate 0.7978; registered_verdict "b"; n_real 32) |
| Pool: 343 labels, 78 pairs, 5 raters, ≈4.4 raters/item, mean pairwise 0.42, Spearman–Brown 0.76, ceiling ≈0.87; median real-judge ρ −0.24, best +0.42, 14 real configs | `experiments/22_pooled_heldout_and_noise_ceiling/results/results.json` | ✓ (343/78/5/4.397; 0.418; 0.760; 0.872; median −0.237; best 0.4219; n_real_judges 14) |
| Drift ρ≈0.13 (n=63); relabel-vs-pool 0.90; own-earlier ≈0.18; strict-vs-pool 0.96; lexical controls −0.57 / −0.46; calibration reproduction to <1e-12 | `experiments/22_pooled_heldout_and_noise_ceiling/REPORT.md` (corrected Finding C) | ✓ all |
| exp42 pool-internal transfer: single-split −0.460…0.295; multiseed 0.119±0.275…0.457±0.218; oracle 0.843–0.870 | `results_exp42_proper_transfer/PAPER_TABLE.md`, `MULTISEED_TABLE.md` | ✓ |
| Screens n=14 then n=32; "the 14 real judge configurations" | prereg dirs + results.json judge_context | ✓ |

No stale variants of any of these numbers remain anywhere in the tex (swept for the pre-fix values, e.g. no leftover 0.905 in the Qwen pass2 cell, no "345", no unscoped p-values).

### F3 — EiC 3-minute triage simulation: SEND TO REVIEW (honest assessment, with residual risk)
Read as a skeptical EiC under volume, title + abstract + pages 1–2 only:

- **What lands well vs. the desk-rejected version:** the question-form title announces a measurement question, not an inflated system claim. The abstract now discloses in one breath: in-sample-only calibration, n=8, wide CIs printed *in the abstract*, the near-zero frozen test, the audit that refuted the paper's own first explanation, and two pre-registered screens ending in a registered negative. This reads as a paper whose claims cannot exceed its evidence because the evidence boundaries are the content. TMLR's stated bar is "claims supported by evidence + of interest to some TMLR readers" — both are now arguably met: scoped claims, and the label-lineage/protocol-drift audit is a genuinely useful cautionary result for the LLM-judge-evaluation audience.
- **Residual triage risks (why this is not a slam dunk):** (1) the headline correlations rest on n=8 judge configurations with CIs like [0.11,1.00] — an EiC in a hurry could still pattern-match to "pilot-scale study"; the honesty mitigates but does not remove this. (2) The narrative is "calibration worked in-sample; the transfer test was confounded; the re-anchored screens came back null" — a reader wanting a positive takeaway finds mostly methodology. TMLR explicitly welcomes well-executed negative results, so this is defensible, but the paper's fate at review will hinge on reviewers valuing the audit as a contribution. (3) Abstract is long (~230 words) and dense; it survives a 3-minute read but only just.
- **Verdict:** would **send to review**, not desk-reject. The prior generic triage ("unlikely to meet acceptance criteria") was most plausibly triggered by claim/evidence mismatch, which is now gone. Estimated desk-reject risk: low-to-moderate, dominated by risk (1).

### F4 — Anonymity + compliance: PASS
- Page 1 of the PDF: "Anonymous authors / Paper under double-blind review", "Under review as submission to TMLR" header. ✓
- PDF metadata: `/Author()` empty, no name leakage. ✓
- Tex body: no author names, emails, or identifying URLs render (the only name occurrences are in non-rendered `%` comments and third-person citations — `miranda2026veribench`, `chen2026rethinking` — which is standard and permitted under double-blind norms). ✓
- `tmlr.sty` byte-identical (MD5 `e302463e…`) to the copies in the frozen submission and deprecated resubmission dirs — unmodified. ✓ No geometry/margin/layout overrides in the preamble (package loads + hyperref colors + listings styles only). ✓
- References start on **page 11** (verified from the compile log after my recompile) — under the ≤12 requirement; main text ends mid-page-11 with Broader Impact + Reproducibility. ✓

### F5 — Rendering: PASS
- `latexmk -g -pdf` exit 0; **29 pages**; **0 overfull boxes**; no missing figures, no undefined references or citations, no multiply-defined labels. Only warning: benign font substitution (`T1/lmr/bx/sc` undefined → substituted), invisible in output (checked rendered pages 1, 2, 10, 11, 12 visually — headings, tables, math, and the two-column reference formatting all render correctly).
- Contribution 2's "(Appendix H)" cross-ref resolves to the correct appendix (Validation-Set Human Alignment). ✓

### F6 — Minor observations (non-blocking; for Brando's read)
1. **"Diverse" single-annotator tension:** Table 1 step 1 says "Collect a diverse set of human ratings" and §1 says "humans rate a compact validation set", while §4.1/§5.1 correctly disclose one annotator × two rubric passes. Not an error (the paper is explicit where it matters), but a picky reviewer may poke at "diverse". Framing decision — left untouched.
2. **Bib cosmetics:** Bowman 2022 renders as "In *arXiv preprint arXiv:2211.03540*"; "Llms instead of human judges?" lowercase (needs `{LLM}s` brace-protection); sparse entries "Z. Ding et al.", "A. Naik et al.", "Yang Liu et al." lack full author lists. Cosmetic only; harmless for triage.
3. **Internal cite-key mislabel (renders correctly):** key `Kocmi2024HumanVsLLM` is actually Bavaresco et al. (JUDGE-BENCH, arXiv 2406.18403) — the rendered citation and the claim it supports are correct; only the key name is misleading. No action needed.
4. **Artifact-release reminder:** `results_exp17*/summary.json` (and likely siblings) embed a co-author's local path (`/Users/ethanhersch/...Stanford_Research/...`). Irrelevant to the PDF, but the Reproducibility Statement promises *anonymized* supplementary artifacts — scrub absolute paths at release time.
5. **Perm-p provenance:** the abstract's 0.017/0.005/0.045 have no machine-readable artifact in-repo (backlog note only). My independent recompute (F2) confirms them; consider committing a small script + JSON so the next QA pass doesn't have to re-derive them.

### OPEN items (Brando's decisions — verified untouched, listed for the record)
- 343-vs-345 label inclusion policy (tex consistently says 343; no 345 anywhere).
- Author-list reconciliation (title block is the anonymous placeholder; title itself is marked PROPOSED pending Brando + co-author sign-off, per the comment at line 75).
- Human-subjects form answer.
- Two `% PROVENANCE-TODO` tables: P4 rewrite/invariance table (`tab:codex_invariance_variants`) and downstream VeriBench table (`tab:theorem_quality_table_split`, 0.470/0.615/0.588) — both still lack machine-readable sources; comments preserved in tex.

---

## Files touched this pass
- `paper_latex/TMLR_2026/main.tex` — six one-phrase overclaim softenings (F1 table above).
- `paper_latex/TMLR_2026/main.pdf` (+ aux files) — recompiled, 29 pages.
- This report.

**Final verdict: SHIP** — hand to Brando for the human read and the co-author window; resolve the four OPEN items there.
