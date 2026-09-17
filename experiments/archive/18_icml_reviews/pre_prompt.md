# CertJudge ICML 2026 feedback

ref: https://claude.ai/chat/8926ea68-8d59-4988-98f3-8401c9b383bd
ref: https://openreview.net/forum?id=xmHP3UhGQ8&referrer=%5BAuthor%20Console%5D(%2Fgroup%3Fid%3DICML.cc%2F2026%2FWorkshop%2FAI4Math%2FAuthors%23your-submissions)
ref: /Users/brandomiranda/cert-judge/experiments/18_icml_reviews/pre_prompt.md

OpenReview (OR) feedback:
```

OpenReview
.net
Search articles, authors and reviews...
Notifications780
Activity
Tasks
Brando Miranda
back arrowBack to Author Console
CertJudge: Evaluating Lean Formal-Code With Falsifiable Properties
Download PDF
Ethan S Hersch, Brando Miranda, Elyas Obbad, Srivatsava Daruru, Zhanke Zhou, Kirill Acharya, Sanmi Koyejo
Published: 17 Jun 2026, Last Modified: 21 Jun 2026
ICML 2026 AI4Math Workshop Poster
Everyone
Revisions
BibTeX
CC BY 4.0
Keywords: LLM-as-a-Judge, Code Evaluation, Human-Centered Coding Agents, Formal Methods, Benchmarking and Evaluation
TL;DR: We propose a property-certification protocol for LLM code judges, showing that a variance-aware Trust Index predicts human alignment and supports scalable evaluation of AI-generated Lean 4 specifications.
Abstract:
LLM judges are increasingly used to evaluate AI-generated code, tests, theorems, and formal specifications. In our setting, a judge scores the quality of a candidate Lean 4 artifact relative to a gold reference, but validating each new judge, prompt, model, or threshold with fresh human ratings is expensive and does not scale. We ask whether this validation can be amortized through behavioral checks that are automatic and falsifiable. We propose CertJudge, a property-certification protocol for LLM judges of Lean~4 theorem and specification quality. Instead of treating human agreement as the only validation signal, CertJudge tests whether a judge behaves correctly under controlled perturbations measuring identity, bug monotonicity, specification monotonicity, and stability. These diagnostics are combined into a variance-aware trust index, TI_var which provides a summary of judge reliability rather than a universal evaluator constant. On a human-labeled validation suite, TI_var strongly predicts judge-level human alignment, reporting validation-set Spearman correlations of 0.833 (avg labels), 0.905 (pass1), and 0.738 (pass2). On VeriBench, we use the calibrated judge to rank theorem-generation methods, illustrating how a small human calibration set can support scalable judge selection. These results are validation-set calibration evidence, not a claim of universal reliability or deployment-time generalization.

Reciprocal Reviewer:  Brando Miranda
Submission Number: 109
Filter by reply type...
Filter by author...
Search keywords...

Sort: Newest First
5 / 5 replies shown
Add:
Paper Decision
Decisionby Program Chairs16 Jun 2026, 11:45 (modified: 16 Jun 2026, 12:02)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers, AuthorsRevisions
Decision: Accept (Poster)
Meta Review of Submission109 by Area Chair v5zC
Meta Reviewby Area Chair v5zC09 Jun 2026, 05:28 (modified: 16 Jun 2026, 12:15)Senior Area Chairs, Area Chairs, Authors, Reviewers Submitted, Program ChairsRevisions
Metareview:
The paper proposes CertJudge, a falsifiable property-certification protocol for evaluating LLM judges of Lean 4 formal-code and specification quality. Reviewers agree that the problem is timely and highly relevant to AI for Math, and that the identity, bug-monotonicity, specification-monotonicity, and stability checks form a useful practical framework. The main weakness is that the empirical evidence remains calibration-based, with a small human-labeled panel, moderate human-label agreement, possible overfitting in metric/prompt/threshold choices, and notable alpha-renaming sensitivity. Overall, the contribution is valuable for a workshop setting, but the current evidence does not justify an oral-level recommendation.

Justification For Recommendation:
All three reviewers are positive, with two weak accepts from high-confidence reviewers and one accept from a lower-confidence reviewer. The shared assessment is that the conceptual contribution is strong and well aligned with the workshop, while the main empirical claim should be interpreted cautiously because it lacks a locked held-out validation set and relies on a small, noisy human calibration panel. I give more weight to the detailed higher-confidence reviews, which support acceptance but emphasize overfitting risk, unclear annotation protocol, and incomplete justification of TIvar over simpler alternatives. These limitations prevent a stronger recommendation, but they do not outweigh the paper’s relevance, practical utility, and transparent framing of its claims.

Recommendation: Accept (Poster)
Confidence: 4: The area chair is confident but not absolutely certain
Best Paper Recommendation: No
Honorable Mention Recommendation: No
A relevant and useful judge-certification protocol for Lean, but right now it rests mostly on small validation-set calibration, with real overfitting risk
Official Reviewby Reviewer uMVy08 Jun 2026, 08:20 (modified: 16 Jun 2026, 12:15)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Reviewer uMVy, AuthorsRevisions
Summary:
This paper studies validation of LLM judges for Lean 4 formal-code and theorem-specification quality assessment when large-scale human annotation is impractical. The proposed framework, CertJudge, introduces four falsifiable behavioral properties: identity, monotonicity under semantic bug injection, monotonicity under specification removal, and stability under prompt or rewrite variation. These properties are aggregated into a variance-aware trust index, TIvar, which is shown to correlate with human agreement across several judge families. The certified judges are subsequently used to rank theorem- and specification-generation systems on VeriBench.

Review:
This is the strongest submission among those I reviewed and addresses a problem that is highly relevant to AI4Math.

As formal theorem-proving and code-generation systems improve, scalable evaluation becomes increasingly important. Proof checkers can verify correctness relative to a specification, but they cannot determine whether a generated theorem or specification accurately captures intended semantics. CertJudge directly addresses this gap.

The conceptual contribution is compelling. Rather than relying solely on human agreement, the paper evaluates judges through falsifiable behavioral properties under controlled perturbations. The four proposed properties capture distinct and meaningful aspects of judge behavior: identity preservation, sensitivity to semantic degradation, sensitivity to specification loss, and robustness under semantics-preserving transformations. The variance-aware trust index is a reasonable aggregation mechanism because it penalizes instability rather than merely averaging performance.

The reported correlation between TIvar and human alignment across multiple judge families is encouraging, and the paper transparently reports failure modes such as alpha-renaming sensitivity and monotonicity violations. Reproducibility is also relatively strong, with prompt templates, calibration details, and extensive appendices provided.

My primary concern is the limited scale of the validation. The main human-alignment analysis relies on approximately 75 labeled pairs and a relatively small collection of judge configurations. Furthermore, the same label set appears to influence metric design, prompt selection, aggregation choices, and threshold calibration, creating a substantial risk of overfitting. Independent evaluation on a held-out reviewer pool would significantly strengthen the evidence.

The labeling methodology also requires clarification. The manuscript appears to alternate between descriptions involving a single annotator under different strictness levels and multiple scoring passes. Since human-human agreement is only moderate, the precise annotation protocol materially affects interpretation of the reported correlations.

I am also not fully convinced that TIvar is uniquely justified. Simpler alternatives appear competitive in some experiments, and more extensive robustness analyses would help establish the necessity of the proposed formulation.

Despite these limitations, the paper addresses an important problem, proposes a practical evaluation framework, and presents useful empirical evidence. The contribution feels appropriate for workshop acceptance.

Strengths:
Addresses an important AI4Math evaluation problem. Introduces a concrete and falsifiable certification protocol. The four properties capture complementary aspects of judge behavior. Variance-aware aggregation appropriately penalizes instability. Transparently reports important failure modes. Strong reproducibility details. Practical relevance for scalable formal-system evaluation.

Weaknesses:
Human-alignment evaluation is relatively small. Potential overfitting due to reuse of labels during protocol design and calibration. Annotation methodology requires clarification. Human-human agreement is only moderate. Alternative trust-index formulations are not fully ruled out. Current judges exhibit substantial alpha-renaming sensitivity. VeriBench rankings may contain judge-family bias. Held-out reviewer results are not included.

Open Questions:
Do the reported trends persist on a fully held-out reviewer pool after protocol choices are frozen? How robust are the results under leave-one-family-out or bootstrap analyses? Can Lean-aware canonicalization reduce alpha-renaming sensitivity? How sensitive is TIvar to weighting and normalization choices? Do downstream rankings remain stable when judge and generator families are separated?

Rating: 4: Weak Accept - technically solid, moderate-to-high impact paper, with no major concerns regarding evaluation, resources, reproducibility, ethical considerations
Confidence: 4: Confident, but not absolutely certain. It is unlikely, but not impossible, that I did not understand some parts.
Best Paper Nomination: No
Honorable Mention Nomination: No
Useful Property-Certification Framework for Lean Judges, but Current Evidence Is Still Calibration Rather Than Generalization
Official Reviewby Reviewer c7ev07 Jun 2026, 02:28 (modified: 16 Jun 2026, 12:15)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Reviewer c7ev, AuthorsRevisions
Summary:
This paper introduces CertJudge, a property-certification protocol for evaluating LLM judges that score Lean 4 code, theorem, and specification artifacts against gold references. Instead of validating every new judge configuration only through fresh human labels, the authors propose four falsifiable behavioral checks: identity/consistency, monotonicity under injected bugs, monotonicity under removed specifications, and stability under prompt or semantics-preserving rewrites. These diagnostics are aggregated into a variance-aware Trust Index, TI(_{var}), which is shown to correlate with judge-level human agreement on a validation panel and is then used to rank theorem-generation methods on VeriBench.

Review:
I think the paper makes a useful and timely contribution to AI4Math evaluation. Lean formal-code generation creates an important evaluation problem: the Lean kernel can check whether a proof verifies a formal statement, but it cannot decide whether a candidate theorem or specification captures the intended semantic property. This makes LLM-based judging tempting, but also risky. The paper’s main contribution is to make judge validation more falsifiable by asking whether a judge behaves sensibly under controlled perturbations, rather than relying only on aggregate human agreement.

I find this framing valuable. The four proposed properties are intuitive and technically meaningful. A judge should score identical artifacts highly; it should penalize accumulating semantic bugs; it should penalize missing theorem/specification content; and it should be stable under rewrites that preserve Lean semantics. These are not complete guarantees, but they are concrete behavioral tests that are much more informative than simply trusting an LLM judge because it sounds reasonable.

The paper is also careful in its strongest claims. I appreciate that the authors describe the results as validation-set calibration evidence, not universal judge reliability or deployment-time generalization. This makes the contribution more credible.

The central limitation is that the current evidence is still calibration evidence, not a locked held-out test. The reported TI({var})-to-human-alignment correlations are encouraging, but the same validation labels appear to have informed the trust-index form, repeat aggregation, threshold choice, and prompt panel. Therefore, I would not treat the reported correlations as evidence that TI({var}) will generalize to new human raters, new Lean domains, or unseen judge families.

The human validation setup is also limited. The main calibration panel has 75 aligned candidate-gold pairs, and the paper reports moderate agreement between the two human passes. This means that the target signal itself is noisy. I appreciate that the authors report pass1, pass2, and averaged labels separately, but this also makes the results feel less settled. The larger independent annotation pool is promising, but it is not analyzed in the current submission, so it cannot yet support the main claims.

Overall, I view this as a promising and relevant workshop paper with a strong evaluation idea, but not yet a clear accept because the strongest claims require stronger held-out validation.

Strengths:
I find the problem important because Lean formal-code evaluation needs more scalable ways to validate LLM judges when exact semantic equivalence is difficult to check automatically.

The proposed property-certification framework is useful because identity, bug monotonicity, missing-spec monotonicity, and stability are concrete, falsifiable behaviors that a reliable judge should satisfy.

The paper clearly explains why Lean proof checking alone is not enough, since a candidate theorem can typecheck while still being incomplete, weak, vacuous, or misaligned with the intended specification.

I appreciate the variance-aware trust index because it accounts for instability across repeated runs and perturbations rather than only rewarding high average scores.

The reported validation-set correlations between TI(_{var}) and human agreement are promising and suggest that the property checks capture meaningful judge behavior.

The downstream VeriBench ranking is a useful demonstration of how a calibrated judge could support larger-scale evaluation of theorem-generation systems.

The paper is careful about its claims and explicitly frames the results as calibration evidence rather than universal reliability or deployment-time generalization.

The related work section connects LLM-as-judge evaluation, code evaluation, scalable oversight, formal methods, and Lean verification in a relevant and useful way.

Weaknesses:
The main result is still validation-set calibration rather than held-out validation, since the same human labels informed the trust-index form, aggregation choices, thresholding, and prompt panel.

The human-labeling setup is limited because the main calibration uses only 75 aligned pairs and the two human passes show only moderate agreement.

The larger independent annotation pool is promising, but it is not analyzed in the current paper and therefore cannot yet support the main reliability claims.

The alpha-renaming failure mode is important because such rewrites should preserve Lean semantics, yet the judge remains sensitive to surface-form changes.

The property suite is useful but incomplete, since it cannot cover all possible judge failures such as vacuity, subtle theorem weakening, over-constraint, or domain-specific semantic mismatch.

The downstream VeriBench ranking should be treated only as a sanity check, because it relies on the calibrated judge itself and is not independent evidence of judge correctness.

The TI(_{var}) formula seems reasonable, but the paper should better justify the specific geometric and variance-aware aggregation choices beyond validation-set fit.

The reference list should be checked carefully because several citations appear very recent, anonymous, future-dated, or workshop-specific and need stable formatting and accessibility.

Open Questions:
Would TI(_{var}) still correlate with human agreement on the newer five-reviewer annotation pool if all index choices are frozen before testing?
How sensitive are the results to the exact weighting in TI(_{var})?
Does the trust index generalize to new judge families that were not part of the calibration panel?
Can the alpha-renaming weakness be fixed by canonicalizing Lean artifacts before judging?
How often do high-TI judges still miss vacuous, overly weak, or over-constrained theorem specifications?
Would the property suite behave similarly on theorem statements without gold references?
Can the authors separate judge failures caused by natural-language rubric ambiguity from failures caused by Lean-code semantic misunderstanding?
How many human annotators are needed before human agreement becomes stable enough to support judge calibration reliably?
Recommendations for Improvement

The paper would be much stronger if the authors froze TI(_{var}), prompts, thresholds, and aggregation choices, then evaluated them on the newer independent annotation pool as a true held-out test.

The authors should clarify the human-labeling protocol, including how many annotators contributed to the main (n=75) panel, what pass1 and pass2 represent, and how disagreements were handled.

I recommend adding confidence intervals, bootstrap estimates, or other uncertainty measures for the judge-level correlations, since the number of judge configurations is small.

The paper should justify the TI(_{var}) formula more carefully and report whether the results are sensitive to different weights or aggregation choices.

The failure analysis should be expanded beyond alpha-renaming to include vacuous specifications, overly weak theorem statements, over-constrained specifications, and formatting-only perturbations.

Since alpha-renaming is a major weakness, the authors should consider Lean-side normalization, canonical variable names, or kernel-derived structural information before judge scoring.

The VeriBench ranking should remain framed as a downstream demonstration or sanity check rather than independent validation of judge correctness.

The authors should verify all anonymous, future-dated, workshop-specific, and very recent references, and ensure that stable URLs or identifiers are provided wherever possible.

Rating: 4: Weak Accept - technically solid, moderate-to-high impact paper, with no major concerns regarding evaluation, resources, reproducibility, ethical considerations
Confidence: 5: Absolutely certain about the assessment. Very familiar with the relevant literature.
Best Paper Nomination: No
Honorable Mention Nomination: No
A promising low-cost way to check AI graders
Official Reviewby Reviewer DeJF02 Jun 2026, 14:41 (modified: 16 Jun 2026, 12:15)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Reviewer DeJF, AuthorsRevisions
Summary:
When AI writes formal math/code in Lean, another AI can be used to grade it, but that grader also needs to be checked against human judgment. This paper proposes CertJudge, a cheaper way to do that by using a small human-labeled set once and then testing future AI graders with four automatic checks: identity, bug monotonicity, missing-specification monotonicity, and stability under meaning-preserving changes. These checks are combined into one trust score called TIvar, which the authors show lines up well with human agreement on a small validation set of 75 examples.

The results are promising, but still limited because the main evidence is validation-based and needs stronger held-out testing.

Review:
This paper looks at an important problem in AI for math. AI now writes a lot of code, tests, theorems, and formal specs. Humans cannot check all of it by hand. So people use one AI to grade another AI. But you have to keep checking that the grader is any good. That check needs human labels and it costs money every time you change the grader. The paper offers a cheaper way.

This paper addresses an important problem in AI for mathematics and formal verification. As AI systems generate more code, tests, theorems, and formal specifications, it becomes difficult for humans to review everything manually. The paper proposes a practical way to test whether an LLM judge is reliable before using it for larger-scale evaluation.

The core idea is clear and useful. Instead of only checking whether an LLM judge agrees with human ratings, the paper asks whether the judge follows basic expected behaviors. For example, a judge should give a high score when an artifact is compared with itself. It should lower the score when bugs are added. It should also lower the score when important specifications are removed. Finally, it should stay reasonably stable when the same meaning is written in a different way. These are simple but meaningful checks.

The paper’s results are encouraging. The authors report that TIvar, the variance-aware trust index, has strong correlation with human alignment on the validation set. The paper also applies the calibrated judge to VeriBench and shows reasonable rankings of theorem-generation methods. This supports the idea that CertJudge can be useful as a practical tool for selecting and comparing LLM judges.

One strength of the paper is that the authors are careful about their claims. They do not say that TIvar proves a judge is universally reliable. Instead, they clearly state that the results are validation-set calibration evidence. This is an important and honest limitation.

However, the evaluation still has some weaknesses. The main validation set has only 75 aligned candidate-gold pairs, which is small for making strong general claims. The paper also mentions a larger independent reviewer pool, but those results are not fully analyzed in the current version. Including that held-out analysis would make the paper much stronger.

Another concern is the alpha-renaming failure mode. Alpha-renaming should preserve the meaning of the Lean artifact, but the judge is less stable under this kind of change. This suggests that the judge may still be affected by surface-level wording or token patterns, even when the formal meaning has not changed. The authors discuss this issue clearly, but it remains an important limitation.

Overall, I find the paper technically reasonable and relevant to the workshop. The contribution is useful, the motivation is strong, and the method is easy to understand. I recommend acceptance, but I would not rate it as a strong accept because the current evidence is still mainly validation-based and needs stronger held-out testing.

Strengths:
The paper addresses an important problem in the AI centric world . how to evaluate LLM judges for Lean 4 code, theorem, and specification artifacts.

The proposed checks are clear and meaningful. Identity, bug monotonicity, missing-specification monotonicity, and stability are easy to understand and useful for judge evaluation.

The method offers a cheaper way to screen new graders, which could reduce repeated human labeling.

The authors are careful not to overclaim. They clearly state that the results are validation-set calibration evidence, not proof of universal reliability.

5)The experiments compare TIvar with human alignment and show encouraging results across several judge families, including GPT-5.3-Codex, Claude Opus 4.7, and Qwen3-Coder.

The bad-grader stress test is useful because it shows that TIvar can catch a judge that may look acceptable under human-agreement numbers alone.

The paper includes detailed prompts and appendix diagnostics, which helps readers understand and potentially repeat the evaluation setup.

Weaknesses:
The main trust-index result is calibrated and tested on the same small validation panel of 75 aligned examples. This means the result should be treated as calibration evidence, not proof that the method works on new data.

The main judge-level result uses only eight judge configurations, so the reported correlations may be unstable.

The human labels are noisy. The main validation panel was scored by one annotator under two related rubric passes, and the two passes only had moderate agreement.

TIvar is not clearly better than a simpler geometric index in all cases. In some model families, the simpler index performs similarly or better.

The downstream VeriBench demo appears to use Claude 3.7 as the judge, while the main validation results focus on GPT-5.3-Codex, Claude Opus 4.7, and Qwen3-Coder. It makes the “same calibrated judge” claim less clear.

Some sections are dense, especially for readers who are not familiar with Lean or formal methods.Please simplify them for readablity.

Open Questions:
How well does TIvar perform on a fully held-out dataset with independent reviewers?

Does the same property-based approach work for other proof assistants or formal languages beyond Lean 4?

Can alpha-renaming sensitivity be reduced using canonicalization, structural checks, or stronger Lean-aware preprocessing?

How sensitive is TIvar to the exact weighting and aggregation choices?

Would the same trust index remain useful for new judge models that were not included in the current experiments?

Rating: 5: Accept - technically solid paper with high impact on at least one sub-area or moderate-to-high impact on more than one area, with good-to-excellent evaluation, resources, reproducibility
Confidence: 3: Fairly confident, but there is a chance I missed some aspects.
Best Paper Nomination: No
Honorable Mention Nomination: No
About OpenReview
Contact
FAQ
Hosting a Venue
Sponsors
Terms of Use / Privacy Policy
All Venues
Donate
News
OpenReview is a long-term project to advance science through improved peer review with legal nonprofit status. We gratefully acknowledge the support of the OpenReview Sponsors. © 2026 OpenReview

```
