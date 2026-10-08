# Information-based evaluation: paper summary and scalar-score adaptation limits

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex/cj-e46-tvdmi-properties/experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation/PAPER_SUMMARY.md>

Publication status: intended branch address; this document has not yet been published.

**TLDR:** Total variation distance mutual information motivates information-preservation diagnostics, but information does not establish correctness. Experiment `46_tvdmi_inspired_properties_cached_judge_validation` adapts the idea to existing scalar judge scores; reproducing the paper's text-pair critic requires a future Valkyrie run.

**The current paper studies information detection rather than a universal correctness metric.**

**Historical-cache result (10-08-2026): no prospective claim.**

Across the fixed 12-configuration pool, train-selected repeat total variation distance selected `opus55x|H2` and achieved historical test Spearman correlation 0.844 [0.472, 0.951] on 29/30 shared files from 10 tasks.
The fixed H2 selector achieved 0.826 [0.507, 0.934], so the paired difference was +0.018 [−0.127, +0.186] over 10,000 task-cluster bootstrap draws; this interval is inconclusive.
Semantic AUC selected an eleven-way tie and achieved 0.768 [0.455, 0.888], a difference −0.059 [−0.156, +0.054] versus H2.
Train-property versus test-agreement associations were negative and conditional across correlated configurations (semantic AUC Spearman −0.306 [−0.480, +0.306]; repeat total variation Spearman −0.168 [−0.529, +0.252]).
Deletion total variation was unavailable for all 56 configurations because the frozen cache has one accepted deletion repeat per level but the property requires two.
These reused historical splits and conditional intervals do not demonstrate prospective utility or generalization.

Robertson and Koyejo's *Let's Measure Information Step-by-Step: AI-Based Evaluation Beyond Vibes* develops mutual evaluation, treating the overseer as an information estimator.
Version four, revised 06-22-2026, motivates total variation distance mutual information through worst-case limits on distribution-free certification.
Its practical critic classifies response pairs as sharing a source or coming from independent sources; aggregation contrasts acceptance rates under those two distributions.
Experiments cover translation, summarization, and peer review, comparing information-based mechanisms with quality judges and testing case changes, formatting, padding, and injected patterns.
The paper distinguishes a certification ceiling from the concentration of a fixed critic's bounded statistic.
It limits the data-processing argument to local post-processing without shared randomness.
It acknowledges untested adaptive overlap attacks, difficult extreme compression, and dependence on pretrained knowledge.
The current conclusion treats shared information as an auxiliary signal rather than a standalone correctness or ranking guarantee.
See [version four, Sections 3–7](https://arxiv.org/html/2508.05469v4).

**A fixed critic's population gap lower-bounds total variation; an observed gap needs uncertainty control.**

Let the joint distribution contain matched-source response pairs, and let the comparison distribution be the product of the response marginals.
For a fixed acceptance event applied to individual pairs, the true positive rate (TPR) minus the false positive rate (FPR) is no larger than the total variation (TV) distance between those distributions:

\[
\underbrace{\mathrm{TPR}-\mathrm{FPR}}_{\text{fixed-event population gap}}
\;\leq\;
\underbrace{\mathrm{TV}(P,Q)}_{\text{standard half-sum of absolute probability differences}}.
\]

For example, acceptance rates of 0.8 and 0.3 give a population gap of 0.5; those rates alone do not identify the full distance.
Finite-sample estimates can be negative or exceed the population distance through sampling noise.
A population inequality is not automatically a finite-sample confidence guarantee.
If the critic or threshold is selected on evaluation observations, that selection must also be accounted for.
The standard normalization uses half the sum of absolute probability differences; a definition using the full sum is twice that distance.
The gap compares response-pair distributions, whereas a distance between a balanced class label and its binary prediction is a different object with a different factor.
See the paper's [Definitions 3.1 and Section 3.4](https://arxiv.org/html/2508.05469v4#S3) for the motivating construction; the distinctions above are our mathematical interpretation.

**Repeat information can remain high for a consistently wrong judge.**

A one-to-one inversion of the scoring scale preserves statistical dependence.
Thus, a judge that reliably reverses coverage rankings can retain the same repeat-score information as a correctly oriented judge.
Stable item-specific biases can also identify matched items without measuring formal-specification coverage.
Conversely, a constant judge has perfect repeat agreement but zero joint-versus-product information.
Direction, absolute score displacement, semantic sensitivity, nuisance invariance, and negative controls must therefore remain separate checks.
Data processing governs true information under a specified channel; it does not guarantee the behavior of an arbitrary scalar judge or the monotonicity of an imperfect fixed critic's gap.

**This experiment uses cached scalar-score adaptations and preserves the sealed evaluation set.**

The planned analysis contrasts responses to strict weakening and harmless formatting, examines repeated-score dependence, and uses constant, shuffled, inverted, and nuisance-only controls where existing cache coverage permits.
These are falsifiable behavioral screens for Lean formal-specification coverage judges, not a replication of the original text-pair mechanism or proof of trustworthiness.
The protocol owns the final operational definitions, eligibility rules, uncertainty procedure, and verdict criteria.
No competing final formulas are specified here.
Missing cached cross-reference scores cannot be created by relabeling existing scores.
Reproducing the real text-pair critic requires a future Valkyrie inference run with a declared matched-source and independent-source design.
VeriBench set-N human ratings and scores remain sealed and outside this analysis.
