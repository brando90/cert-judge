# 1st port to neurips 2026 format

**TLDR:** Historical instructions for porting the manuscript and revising its paper pitch. The retained request distinguishes development-panel optimization from a later test on untouched human ratings.

Port NeurIPS 2025 (/lfs/mercury2/0/brando9/cert-judge/paper_latex/NeurIPS_2025) to the NeurIPS 2026 format (/lfs/mercury2/0/brando9/cert-judge/paper_latex/NeurIPS_2026/Formatting_Instructions_For_NeurIPS_2026) please.
Then rename the template file to /paper folder please. Go.

ref: https://neurips.cc/Conferences/2026/CallForPapers


---

# 2nd request: Rewrite paper -- especially abstract and intro excellently according to the current paper pitch

pitch
```txt
Idea3: "Property Certification as Amortized Scalable Oversight: Assess Once, Deploy Forever"
Pitch: validating LLM judges against humans is the standard reliability check but doesn't scale — every new judge, prompt, or model needs fresh annotation. Properties (identity, bug-monotonicity, spec-monotonicity, repeat-stability) collectively predict human alignment at Spearman ρ ≈ TODO (n=TODO judges, p=TODO) after a single human-agreement study with gold references.
This converts trust validation from O(N labels × M judges) to O(N labels + property scores per new judge for free).
Pro1: reframes the contribution as economics of oversight, not yet-another-proxy-metric — connects to scalable oversight as a research agenda (Bowman et al. 2022). Pro2: pre-empts Yegor's "strict prerequisite" / "spurious proxy" critique — properties don't replace humans, they extend humans to new judges via development-panel validation ("use humans once, properties forever after"). Pro3: turns the BAD_STRINGY caveat into a feature — human-agreement assessment is needed precisely because some judges have moderate human-corr (≈0.45) but fail individual properties (12.5% weak monotonicity); human-agreement assessment identifies which property patterns indicate trustworthy judges. Pro4: methodological contribution (human-agreement assessment protocol) is stronger than metric contribution → elevates from COLM-tier to NeurIPS-tier.
Con1: still requires gold refs for the one human-agreement study (shared with Idea 2). Con2: generalization claim needs hold-out validation (split 12 judges into 8 development plus 4 held-out, show JTI predicts held-out human-corr) — about three to four days of work, not yet run. Con3: doesn't go as far as Idea 1's paradigm-shift; doesn't claim humans are insufficient, only that they're expensive.
```
Rewrite paper 2026 version. Git push to main. PR merge to main assign to ethan elyas please.
Then do this and make sure the paper is clear about the validation validation thing
```txt
I think this is a good plan ```Brando — 11:48 AM
i think we need to adapt the experiments a bit...or this would have been better:
have the properties correlate with human judgements on some "validation set" of human judgements --> we are allowed to "overfit here" ie do human research optimization over the judge, aggregation, prompt, models, etc
then test if these properties still correlate give the judge from 1 on a test set of human judgements that are untouched by the "human research optimization"
idk if we have time to do it...
I think the current 2 judgements you have @Ethan Hersch we can use them as the "validation"/train for searching for the judge with high corr and low variance
then I can finish the human judgements protocol and we can collect more human judgements with multiple humans
and then!
we can report the "final" human correlation & stability/variance
I think this is a good plan!``` So we can keep doing what we are doing. We can report for now just the validation errors and admit it's the validation but then later this week produce the new fixed experiments.
```

TL;DR: This historical prompt describes manuscript revision and Git publication using the stated development-versus-test distinction; it is retained as paper context.
