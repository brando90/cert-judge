# ICML 2026 DL4C workshop — OpenReview reviews (verbatim, pasted by Brando 09-22-2026)

**TLDR:** "Certifying the Judge: Falsifiable Properties for LLM-Based Evaluation of Formal Code" (OpenReview forum `gGR1gE7x3a`, DL4C submission 105) was accepted as a poster by the Program Chairs on 06-15-2026 with three official reviews and no meta-review: Reviewers birm (6/10, confidence 4), cxkT (6/10, confidence 3), and nMnm (6/10, confidence 3). The text below is Brando's verbatim paste of the author-console forum (pasted into this chat on 09-22-2026 because the review notes are readable only by chairs, reviewers, and authors; see `../33b_or_ledger/fetch_attempts.md`). Complaints are extracted into `complaints.md` (IDs `D26-*`).

## Metadata

| Field | Value |
|---|---|
| Title | Certifying the Judge: Falsifiable Properties for LLM-Based Evaluation of Formal Code |
| Forum | https://openreview.net/forum?id=gGR1gE7x3a |
| Venue tag | ICML 2026 Workshop DL4C Poster (venueid `ICML.cc/2026/Workshop/DL4C`) |
| Submission number | 105 |
| Decision | Accept (Poster), Program Chairs, 15 Jun 2026 |
| Reviews | birm (6, conf 4), cxkT (6, conf 3), nMnm (6, conf 3); no meta-review posted |
| Local source | `paper_latex/ICML_2026_DL4C/main.tex`; the ICLR 2027 manuscript is this paper reformatted (commit history from 09-16-2026) |

## Reviews (verbatim paste)

```
OpenReview
.net
Search articles, authors and reviews...
Notifications973
Activity
Tasks
Brando Miranda 
back arrowBack to Author Console
Certifying the Judge: Falsifiable Properties for LLM-Based Evaluation of Formal Code
Download PDF
Ethan S Hersch, Brando Miranda, Elyas Obbad, Srivatsava Daruru, Kirill Acharya, Zixiao Jolene Wang, Steven Dillmann, Yegor Denisov-Blanch, Sanmi Koyejo
Published: 16 Jun 2026, Last Modified: 30 Jun 2026
ICML 2026 Workshop DL4C Poster
Everyone
Revisions
BibTeX
CC BY-NC 4.0
Keywords: LLM-as-a-Judge, Code Evaluation, Human-Centered Coding Agents, Formal Methods, Benchmarking and Evaluation
TL;DR: We propose a property-certification protocol for LLM code judges, showing that a variance-aware Trust Index predicts human alignment and supports scalable evaluation of AI-generated Lean 4 specifications.
Abstract:
LLM judges are increasingly central to evaluating AI-generated code, tests, and formal specifications, yet their reliability is still checked in the least scalable way possible: fresh human ratings for every new judge, prompt, model, and threshold. We challenge this validation loop by asking whether human judgment can be amortized and scaled through falsifiable behavioral properties. We propose a property-certification protocol for LLM judges of Lean 4 theorem and specification quality, where each judge is scored by four automatically testable conditions: identity, bug monotonicity, specification monotonicity, and repeat/prompt stability. Our variance-aware trust index TI_var is one calibrated instantiation of these diagnostics. Rather than presenting a single fitted weighting as a universal evaluator constant, we contribute a reusable certification protocol that converts falsifiable behavioral properties into an auditable trust signal for LLM judges.

On eight judge configurations spanning frontier prompts, weaker baselines, edit-distance, and random controls, TI_var strongly predicts judge-level human alignment on that calibration suite, reporting validation-set Spearman correlations of 0.833 (avg labels), 0.905 (pass1), and 0.738 (pass2). Property-level analysis shows that monotonicity under removed specifications is the strongest single predictor of human agreement, followed by monotonicity under injected bugs, while identity and stability are weaker standalone signals. Applied to VeriBench, the protocol illustrates how a small human calibration set can support scalable, auditable judge selection for AI-generated code, tests, theorems, and formal specifications, without claiming universal or deployment-time guarantees.

Submission Number: 105
Filter by reply type...
Filter by author...
Search keywords...

Sort: Newest First
4 / 4 replies shown
Add:
Paper Decision
Decisionby Program Chairs15 Jun 2026, 15:10 (modified: 22 Jun 2026, 17:40)Program Chairs, Area Chairs, Reviewers, AuthorsRevisions
Decision: Accept (Poster)
Certifying the Judge: Falsifiable Properties for LLM-Based Evaluation of Formal Code
Official Reviewby Reviewer birm08 Jun 2026, 09:34 (modified: 16 Jun 2026, 08:59)Program Chairs, Area Chairs, Reviewers, AuthorsRevisions
Reasons To Accept:
Addresses a timely problem: code agents can generate candidate formal artifacts far faster than humans can inspect them, so scalable judge validation is a real need.
The paper proposes four concrete, automatically testable properties (identity, bug monotonicity, spec monotonicity, and stability) that run on perturbed artifacts to score whether a judge can be trusted, replacing repeated human validation. Packaging these into a certification protocol is a clean, reusable idea.
Interesting finding on which checks matter most: how much a judge's score drops when specs are removed is the best predictor of agreement with human ratings, followed by how much it drops when bugs are added.
The appendix is detailed, with full prompts, clear reporting of failure modes, and useful background that makes the work easy to follow and reproduce.
Honest about its own weaknesses.
Reasons To Reject:
Small scale and weak ground truth: just 75 pairs, 8 judges, and one human rater. A bigger set (5 raters, 343 labels, 78 pairs) exists but hasn't been analyzed yet, so the stronger evidence is promised, not shown.
All evidence comes from a single benchmark (VERIBENCH), so it's unclear how well the protocol transfers to other Lean datasets or formal-verification settings. The benchmark is anonymized, which is fine for review, but it does make the data harder to assess independently right now.
Some headline numbers swing a lot across rating passes (e.g., Qwen3-Coder pass1 0.476 vs pass2 0.905). I'm not sure how concerning this is, but it stands out.
Generally quite heavy on statistics, making it hard to follow and verify without a strong relevant background.
Review:
The paper proposes a way to check whether an LLM judge (used to score AI-generated Lean code and specifications) can be trusted, without collecting fresh human ratings every time. It does this with four automatic checks that are calibrated once against human labels and combined into a single trust score. It is a borderline paper: the evidence is preliminary and the heavy statistics make it hard to follow in places. But the core idea is genuinely interesting and useful, and the authors are honest about the limitations, so I lean towards accepting it.

Recommend For Best Paper: No
Rating: 6: Marginally above acceptance threshold
Confidence: 4: The reviewer is confident but not absolutely certain that the evaluation is correct
Evaluation of judge reliability
Official Reviewby Reviewer cxkT05 Jun 2026, 14:58 (modified: 16 Jun 2026, 08:59)Program Chairs, Area Chairs, Reviewers, AuthorsRevisions
Reasons To Accept:
Addresses a real and timely bottleneck. Validating LLM judges by collecting fresh human labels for every new judge/prompt/model/threshold scales linearly and becomes untenable at agent-generation rates. Amortizing human judgment via reusable, automatically-testable properties is a sensible and useful framing, and the focus on Lean 4 specification quality (where type-checking alone cannot establish semantic adequacy) is well-motivated.
The certification signal tracks human alignment across judge families. TI_var predicts judge-level human Spearman across three distinct judge families (Codex, Claude Opus, Qwen3-Coder), with six of nine family/pass combinations exceeding 0.7. That the same signal remains informative across families is the paper's strongest empirical point.
Useful downstream demonstration. Applying the calibrated judge to VeriBench produces sensible agent rankings (DSPy ReAct 0.615 vs. baseline 0.470), showing the trust signal propagates to a real evaluation workload.
Reasons To Reject:
Tiny, single-annotator calibration with weak label reliability. Calibration rests on n=75 pairs rated by one annotator under two rubric passes. Inter-pass agreement is only moderate (Spearman 0.249, QWK 0.372). Judge-level trends are estimated over just n=8 judges, so correlations like 0.833–0.905 sit on extremely thin statistical ground, with wide confidence intervals (e.g., Table 12 CIs spanni negative values). Kendall τ is already noticeably noisier at this scale.

Review:
See above

Recommend For Best Paper: No
Rating: 6: Marginally above acceptance threshold
Confidence: 3: The reviewer is fairly confident that the evaluation is correct
Amortized Judge Certification for Lean 4 Formal Code Evaluation
Official Reviewby Reviewer nMnm05 Jun 2026, 14:56 (modified: 16 Jun 2026, 08:59)Program Chairs, Area Chairs, Reviewers, AuthorsRevisions
Reasons To Accept:
Addresses scalability bottleneck in evaluating LLM-generated formal code.
Proposes a practical amortized calibration protocol that reuses limited human annotation.
Uses falsifiable behavioral properties to test judge reliability.
Introduces TIvar as a variance-aware composite trust metric that predicts judge-level alignment with human ratings, enabling automated judge selection without repeated human annotation.
Provides comparisons across models and agents, with downstream evaluation on VERIBENCH.
Reasons To Reject:
Results are limited to the alibration set; as the authors note, no held-out test results are reported.
The calibration set is small and scored by a single annotator, which the authors also acknowledge.
Generalization beyond Lean 4 is not shown.
The paper is difficult to read in places, and the Additional Material section needs better formatting.
Review:
The paper makes a useful methodological contribution by proposing a reusable protocol for certifying LLM-based judges of Lean 4 formal artifacts. The idea is practical and relevant, especially for reducing repeated human annotation costs. However, the evidence is still limited by the small single-annotator calibration set, lack of held-out results, and unclear generalization beyond Lean 4. Overall, the paper is promising.

Recommend For Best Paper: No
Rating: 6: Marginally above acceptance threshold
Confidence: 3: The reviewer is fairly confident that the evaluation is correct
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

Source URL (author console): https://openreview.net/forum?id=gGR1gE7x3a
