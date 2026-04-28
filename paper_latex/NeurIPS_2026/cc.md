# 1st port to neurips 2026 format

Port NeurIPS 2025 (/lfs/mercury2/0/brando9/cert-judge/paper_latex/NeurIPS_2025) to the NeurIPS 2026 format (/lfs/mercury2/0/brando9/cert-judge/paper_latex/NeurIPS_2026/Formatting_Instructions_For_NeurIPS_2026) please.
Then rename the template file to /paper folder please. Go.

ref: https://neurips.cc/Conferences/2026/CallForPapers


---

# 2nd request: Rewrite paper -- especially abstract and intro excellently according to the current paper pitch

pitch
```txt
Idea3: "Property Certification as Amortized Scalable Oversight: Calibrate Once, Deploy Forever"
Pitch: validating LLM judges against humans is the standard reliability check but doesn't scale — every new judge, prompt, or model needs fresh annotation. Properties (identity, bug-monotonicity, spec-monotonicity, repeat-stability) collectively predict human alignment at Spearman ρ ≈ TODO (n=TODO judges, p=TODO) after a single one-time calibration on gold refs.
This converts trust validation from O(N labels × M judges) to O(N labels + property scores per new judge for free).
Pro1: reframes the contribution as economics of oversight, not yet-another-proxy-metric — connects to scalable oversight as a research agenda (Bowman et al. 2022). Pro2: pre-empts Yegor's "strict prerequisite" / "spurious proxy" critique — properties don't replace humans, they extend humans to new judges via calibration ("use humans once, properties forever after"). Pro3: turns the BAD_STRINGY caveat into a feature — calibration is needed precisely because some judges have moderate human-corr (≈0.45) but fail individual properties (12.5% weak monotonicity); calibration identifies which property patterns indicate trustworthy judges. Pro4: methodological contribution (calibration protocol) is stronger than metric contribution → elevates from COLM-tier to NeurIPS-tier.
Con1: still requires gold refs for the one-time calibration step (shared with Idea 2). Con2: generalization claim needs hold-out validation (split 12 judges into 8 calibration plus 4 held-out, show JTI predicts held-out human-corr) — about three to four days of work, not yet run. Con3: doesn't go as far as Idea 1's paradigm-shift; doesn't claim humans are insufficient, only that they're expensive.
```
Rewrite paper 2026 version. Git push to main. PR merge to main assign to ethan elyas please.