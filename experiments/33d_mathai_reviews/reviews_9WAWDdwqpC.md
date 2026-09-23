# NeurIPS 2025 MATH-AI workshop — OpenReview reviews (verbatim capture)

**TLDR:** Verbatim copy of the two official reviews of submission #161, "Trusting the Formal Judge: Certifying LLM Theorem Scorers for Code Verification in Lean4" (OpenReview forum `9WAWDdwqpC`). Reviewer ivJs rated 6 (marginally above threshold); Reviewer 36Hd rated 3 (clear rejection). The capture shows the venue line "Submitted to MATH-AI 2025" with no accept tag; no decision note or meta-review was captured. Source of truth: `experiments/archive/02_neurips_reviews/or_neurips_2025_math_ai_workshop/or_reviews.md` (byte-identical below the separator).

- Forum: https://openreview.net/forum?id=9WAWDdwqpC
- Paper version: NeurIPS 2025 draft (`paper_latex/archive/…`), the ancestor of the ICML 2026 workshop papers.
- Copied 09-22-2026 by the collection pass of experiment 33; complaints extracted into `complaints.md` (IDs `N25-*`).

---

OpenReview.net
Search OpenReview...
Notifications538
Activity
Tasks
Brando Miranda 
back arrowGo to NeurIPS 2025 Workshop MATH-AI homepage
Trusting the Formal Judge: Certifying LLM Theorem Scorers for Code Verification in Lean4
Download PDF
Brando Miranda, Srivatsava Daruru, Slim Barkallah, Allen Nie, Zhanke Zhou
~Zhanke_Zhou1
, Leni Aniva, Elyas Obbad, Weston Kirk, Ying Li, Rylan Schaeffer, Santiago Cuellar, Dilara Soylu, Eric Chen, Bo Han, Sanmi Koyejo 
26 Sept 2025 (modified: 20 Nov 2025)
Submitted to MATH-AI 2025
MATH-AI, Reviewers, Authors
Revisions
BibTeX
CC BY 4.0
Keywords: LLM-as-a-Judge, Trustworthiness, Certification Protocol, Formal Verification, Theorem Generation, Metamorphic Testing, Lean 4
TL;DR: We certify LLM judges for evaluating AI-generated theorems by testing for logical properties like identity and monotonicity. This protocol yields a validated judge that reliably ranks AI agents, enabling scalable evaluation.
Abstract:
Formal methods provide unparalleled rigor in software verification, and with the advent of AI systems, we are beginning to see their potential realized at scale; however, evaluating the quality of the theorems and specifications these systems generate remains a critical bottleneck. Traditional benchmarks often provide a fixed theorem statement, but agentic systems must infer and synthesize these properties on their own, demanding a scalable and reliable evaluation method. We present an LLM-based judge designed to score the quality of generated Lean~4 theorems based on correctness, completeness, and semantic alignment with a reference implementation. More importantly, we introduce a novel methodology to certify the judge's trustworthiness by verifying its adherence to fundamental logical properties. We demonstrate that our judge satisfies identity (identical inputs yield maximal scores) and monotonicity (scores decrease predictably as bugs are introduced or specifications are removed), with Pearson correlations up to 0.973. By applying this validated judge to the VeriBench benchmark, we show that agentic approaches for formal code generation significantly outperform baseline prompting, with a top score of 0.615 vs. 0.470. This work provides a blueprint for creating and validating reliable automated judges, enabling robust and scalable evaluation of next-generation theorem-proving agents.

Supplementary Material:  pdf
Submission Number: 161
Filter by reply type...
Filter by author...
Search keywords...

Sort: Newest First
2 / 2 replies shown
Add:
Review of Trusting the Formal Judge: Certifying LLM Theorem Scorers for Code Verification in Lean 4
Official Reviewby Reviewer ivJs13 Oct 2025, 17:09 (modified: 17 Oct 2025, 07:46)Program Chairs, Reviewer ivJs, AuthorsRevisions
Review:
This paper introduces an LLM-based judge for evaluating AI-generated Lean 4 theorems and proposes a certification protocol to validate its trustworthiness through falsifiable properties: identity and monotonicity. The judge achieves strong correlations (up to 0.973) on certification tests and shows agentic methods outperform baselines on VERIBENCH (0.615 vs 0.470).

Strengths

Novel certification methodology: The falsifiable property-based validation (identity, monotonicity to bugs/missing specs) is principled and goes beyond typical human correlation studies
Strong empirical validation: R²=1.000 for identity, high negative correlations for monotonicity provide compelling reliability evidence
Important problem: Addresses a genuine bottleneck in evaluating agentic systems that synthesize specifications autonomously
Weaknesses

Limited generalization: Certification uses finite perturbations on one benchmark; unclear how it handles novel theorem types or adversarial cases
Single architecture: No comparison with other LLM judges or ensemble methods limits generality claims
No human validation: Doesn't confirm judge aligns with expert assessments of theorem quality
Rating: 6: Marginally above acceptance threshold
Confidence: 4: The reviewer is confident but not absolutely certain that the evaluation is correct
A Slightly Unclear Attempt at an LLM-Based Judge for Formal Verification
Official Reviewby Reviewer 36Hd10 Oct 2025, 13:02 (modified: 17 Oct 2025, 07:46)Program Chairs, Reviewer 36Hd, AuthorsRevisions
Review:
The paper studies an important problem in formal verification called the specification adequacy problem—the gap between what we formally prove and what we actually intended to prove. The authors propose using an LLM to asses this gap and evaluate its performance.

However, as far as I can see, the judge is simply Claude 3.5 (Section 3) or Claude 3.7 (Section 4) and no further details are provided. VeriBench (in Lean 4) is used for evaluations, but the evaluation is unconvincing. Essentially, the judge takes two formal specifications and scores their alignment. Not surprisingly, the score is perfect when comparing identical specifications (identity) and gradually decreases as one specification is modified (monotonicity) by breaking or removing parts of it. But this is not particularly similar to the real problem the authors want to study; it looks more like a form of edit distance over strings. Moreover, the monotonicity experiment likely ignores the severity of the changes.

In Section 4, the judge is used for an agentic theorem generation, but the details are missing. In fact, I am not even sure what is the input and I only guess that DSPy and Trace are used similarly as in the VeriBench paper. This is slightly surprising as I find a lot of details about Lean 4 and even other systems in the Appendix. However, the paper does not mention how Lean 4 is actually used. I only guess that in Section 4 and in Section 3 (P2). The main problem is that the missing details make it hard to even evaluate the merit of the paper.

Accordingly, my current evaluation is negative, as I believe that several aspects of the paper should be clarified.

Pros
It is an important problem in formal verification.
Using an LLM for the problem seems natural.
Cons
The missing details make it hard to evaluate the contribution of the paper.
The experiments in Section 3 are not that similar to the real problem.
The setup in Section 4 is unclear.
The judge seems to be just Claude 3.5 or 3.7.
Using an LLM as a judge is not that novel.
Remarks
In Section 3, monotonicity should not be defined as a strict ordering.
Why Claude 3.5 in Section 3? Why Claude 3.7 in Section 4? Why both in Appendix D.
Figure 1 is unreadable.
Typos
Figure 1: vs. should be w.r.t.
Missing references in the Appendix.
Appendix B: Lean 4 verus Verus.
Appendix C: **
Rating: 3: Clear rejection
Confidence: 3: The reviewer is fairly confident that the evaluation is correct
About OpenReview
Hosting a Venue
All Venues
Contact
Sponsors
Donate
FAQ
Terms of Use / Privacy Policy
News
OpenReview is a long-term project to advance science through improved peer review with legal nonprofit status. We gratefully acknowledge the support of the OpenReview Sponsors. © 2026 OpenReview

https://openreview.net/forum?id=9WAWDdwqpC&noteId=9WAWDdwqpC