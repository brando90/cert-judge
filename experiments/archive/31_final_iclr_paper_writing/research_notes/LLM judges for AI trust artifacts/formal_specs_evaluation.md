# How AI-generated formal statements and specifications are checked for faithfulness (2022–2026)

Scope: autoformalization of theorem statements (Lean 4, Isabelle) and specification generation for verified code (Dafny, Verus, Lean, Java/C). Researched 2026-09-22.

How items were verified: every arXiv ID below was checked against the arXiv API (title, first authors, date, and the comment/journal-ref field). Quotes and numbers come from the full-text PDFs (downloaded from arxiv.org and converted with pdftotext), not from search snippets, unless marked otherwise. Venues are shown only if the paper's own header, its arXiv comment, or a proceedings/publisher page confirmed them; anything else is marked UNVERIFIED. OpenReview blocked automated access (403 "ChallengeRequiredError"), so OpenReview-only pages could not be read.

---

## Q1. How are autoformalized statements checked for faithfulness? (human review, BLEU/typecheck, back-translation, BEq, FormalAlign, LLM judges)

### Takeaway
There are four families of methods: human expert review, which is still the gold standard; surface proxies (BLEU, typecheck/compile rate), which are widely called inadequate; reference-based formal equivalence (BEq, BEq+, GTED, SMT for geometry); and model-based judges (NLI after back-translation, trained critics like FormalAlign and CriticLeanGPT, prompted LLM judges and LLM ensembles). Since late 2025, papers openly state that LLM judges are the dominant scalable choice. The same papers note that those judges' reliability is only now being measured against human labels, at roughly 86–90% agreement.

### Cited Findings
**Human evaluation and surface metrics (the 2022–2023 baseline)**
- **Wu et al., "Autoformalization with Large Language Models," NeurIPS 2022, arXiv 2205.12615** (Isabelle/HOL). Evaluation used (a) BLEU against human formalizations on a miniF2F subset (140 algebra + 120 number theory problems) and (b) manual review: "We randomly pick 150 formalizations and manually evaluate their correctness. Among them, LLMs are capable of producing 38 perfect formalizations" (25.3%). — [arXiv](https://arxiv.org/abs/2205.12615); venue: [NeurIPS proceedings](https://proceedings.neurips.cc/paper_files/paper/2022/hash/d0c6bc641a56bebee9d985b937307367-Abstract-Conference.html)
- **Zheng, Han, Polu, "MiniF2F," ICLR 2022, arXiv 2109.00110.** Quote: "miniF2F is a dataset of manually formalized statements of Olympiad type problems, aligned in Lean, Metamath, and Isabelle." The reference statements come from human formalization. — [arXiv](https://arxiv.org/abs/2109.00110)
- **Azerbayev et al., "ProofNet," 2023, arXiv 2302.12433** (Lean 3). Human annotators formalized the statements. Model autoformalizations are graded by a human expert; typecheck rate and BLEU are also reported. Few-shot Codex was correct on 13.4%, and 16.1% with prompt retrieval. Venue: UNVERIFIED (the arXiv record has no venue). — [arXiv](https://arxiv.org/abs/2302.12433)
- **Tsoukalas et al., "PutnamBench," NeurIPS 2024 Datasets & Benchmarks, arXiv 2407.11214.** Quote: "The formalizations are all manually constructed and have been carefully debugged." Statements exist in Lean 4 and Isabelle, and many also in Coq. — [arXiv](https://arxiv.org/abs/2407.11214)

**Back-translation plus NLI, with an LLM as the NLI judge**
- **Ying et al., "Lean Workbook," NeurIPS 2024 Datasets & Benchmarks, arXiv 2406.03847.** The pipeline filters by Lean compile ("Compiling Correctness test"), then back-translates to natural language and runs an NLI test, then human diagnosis. Quote: "we still query the Qwen-1.5-14B-Chat to judge if the original question is the same as the back-translated version. If we do not get a positive response, the sample is marked as needing human revision." Result: about 57K problems; "Manual examination reports an accuracy of 93.5% of a random sample." — [arXiv](https://arxiv.org/abs/2406.03847)
- **Gao et al., "Herald," arXiv 2410.10878.** Described by a 2026 survey-style related-work section as using "compiler and back-translation checks." — [arXiv](https://arxiv.org/abs/2410.10878); description from [Zhang et al. 2026](https://arxiv.org/abs/2606.31002). Venue ICLR 2025: seen only in a search-result summary, so treat as UNVERIFIED.

**Trained alignment evaluators and critics**
- **Lu et al., "FormalAlign," ICLR 2025, arXiv 2410.10135.** A model trained with a dual loss (autoformalization plus alignment) scores whether an informal/formal pair matches. Quote: "Existing approaches heavily rely on manual verification, hindering scalability." It beats GPT-4 on Alignment-Selection Score (99.21% vs 88.91% on FormL4-Basic; 66.39% vs 64.34% on MiniF2F-Valid). — [arXiv](https://arxiv.org/abs/2410.10135); venue: [OpenReview PDF header "Published as a conference paper at ICLR 2025"](https://openreview.net/pdf/d4b5216f0d4d6c9fcd224c1bbfb843d197ae89d0.pdf)
- **Peng et al., "CriticLean," 2025, arXiv 2507.06181.** CriticLeanGPT is trained with SFT and RL "to rigorously assess the semantic fidelity of Lean 4 formalizations." The paper introduces CriticLeanBench, a benchmark of critic accuracy, and uses the critic to build FineLeanCorpus (over 285K problems, human-evaluated for correctness). It argues that the critic phase "is not only underexplored but also fundamentally essential." Venue: UNVERIFIED. — [arXiv](https://arxiv.org/abs/2507.06181)
- **Xuejun et al., "Mathesis," 2025, arXiv 2506.07047.** Proposes LeanScorer, "a novel evaluation method combining LLM-based analysis with Sugeno Fuzzy Integral," and the Gaokao-Formal benchmark (488 problems with human-verified formal statements). It says existing benchmarks' human formal statements "subtly deviate from the original NL intent by simplification." — [arXiv](https://arxiv.org/abs/2506.07047)

**Reference-based formal equivalence (symbolic or neuro-symbolic)**
- **Liu, Zheng, Lu, Cao, Yan, "Rethinking and Improving Autoformalization: Towards a Faithful Metric and a Dependency Retrieval-based Approach," ICLR 2025 (Spotlight), OpenReview hUb2At2DsQ.** Proposes BEq (Bidirectional Extended Definitional Equivalence): an LLM prover tries to derive each statement from the other using restricted tactics. On 200 expert-labeled pairs, accuracy rose from 82.50% to 90.50% and precision from 70.59% to 100.0%. It critiques existing metrics: "evaluated by laborious human annotation … or unreliable proxy automated metrics including … BLEU … symbolic type check pass rate … or LLM grader (Ying et al., 2024a) … Type check is too weak … It is a necessary but not sufficient condition … LLM graders are non-determinant and highly dependent on prompts, and are easily misled by imperceptible but fundamental differences or huge but nonessential transformations." — [ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d630537fc4402cfa3ebbc7450a0cac91-Abstract-Conference.html); [PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/d630537fc4402cfa3ebbc7450a0cac91-Paper-Conference.pdf). No arXiv ID was found. **This is NOT the bib key `chen2026rethinking`** (see the final section).
- **Poiroux, Weiss, Kunčak, Bosselut, "Reliable Evaluation and Benchmarks for Statement Autoformalization," EMNLP 2025, arXiv 2406.07222.**
  - BEq+ is a deterministic, CPU-only, reference-based metric.
  - ProofNetVerif has 3,752 formal/informal pairs with human binary equivalence labels.
  - ProofNet# is a corrected ProofNet.
  - On ProofNetVerif, BEq+ has precision 98.0%, recall 48.3%, and F1 64.7%. Its benchmark-level Pearson correlation with humans is 0.974 (type-check: 0.655).
  - Quote: "current metrics still show relatively low recall relative to near-perfect precision, underestimating true autoformalization accuracy."
  - [arXiv](https://arxiv.org/abs/2406.07222)
- **Liu et al., "Generalized Tree Edit Distance (GTED)," AI4Math@ICML25, arXiv 2507.07399.** Quote: "proof-based approaches (Liu et al., 2025a) … frequently miss valid formalizations due to the limited capabilities of the underlying prover. Concurrently, LLM-assisted evaluations (Ying et al., 2024a) contend with reproducibility and high cost concerns." — [arXiv](https://arxiv.org/abs/2507.07399)
- **Murphy et al., "Autoformalizing Euclidean Geometry," ICML 2024, arXiv 2405.17216.** Uses SMT-based equivalence checking. BEq's authors describe it as "pioneers to utilize SMT solver for faithful automated evaluation, but is restricted to Euclidean geometry only." — [arXiv](https://arxiv.org/abs/2405.17216); characterization from the [BEq paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/d630537fc4402cfa3ebbc7450a0cac91-Paper-Conference.pdf)
- **Wu et al., "StepFun-Formalizer," AAAI 2026 Oral, arXiv 2508.04440.** Headline evaluation is BEq@1 (40.5% on FormalMATH-Lite, 26.7% on ProverBench). BEq also serves as the verifiable RL reward. Training data was curated with "majority voting and an LLM-based judge." The paper also reports GPT-4o-based and human error analyses side by side. — [arXiv](https://arxiv.org/abs/2508.04440)

**LLM-as-judge evaluation, and meta-evaluation of LLM judges (2025–2026)**
- **Chen et al., "ReForm," ICLR 2026, arXiv 2510.24592.** Key quote: "while recent works predominantly rely on LLMs as judges for semantic consistency evaluation in autoformalization (Wang et al., 2025a; Lin et al., 2025b), the reliability of these LLM-based judges is not sufficiently studied." The two cited works are Kimina-Prover Preview and Goedel-Prover-V2, per ReForm's own reference list. ReForm builds ConsistencyCheck (859 expert-annotated items): "Frontier LLMs make correct determination 85.8% of the time," and "16.4% of miniF2F and 38.5% of ProofNet's human-written formal statements contain semantic errors." — [arXiv](https://arxiv.org/abs/2510.24592)
- **Zhang, Valentino, Meadows, Freitas, "Beyond Gold Standards: Epistemic Ensemble of LLM Judges for Formal Mathematical Reasoning," 2025, arXiv 2506.10903.** Abstract: "methods for automatically evaluating autoformalization remain underexplored. LLM-as-a-judge presents a promising approach." It proposes an ensemble of LLM judges scoring logical preservation, mathematical consistency, formal quality, and formal validity, and calls it "a more suitable emerging proxy for evaluation." The VeriBench PDF characterizes it as reaching r = 0.479 with humans on Lean 4 with a single annotator; that figure was not checked in the source. Venue: UNVERIFIED. — [arXiv](https://arxiv.org/abs/2506.10903)
- **Zhang, Gallardo Candela, Murthy, Xie, Wang, Raissi, "Beyond Compilation: Evaluating Faithful Natural-Language-to-Lean Statement Formalization," 2026, arXiv 2606.31002.**
  - The criterion is Lean compilation plus strict consensus between GPT-5.2 and Gemini-2.5-Pro.
  - It "agrees with human majority on 89.7% of cases (Wilson 95% CI: 82.1–94.3%)" (87/97).
  - The compile–faithfulness gap ranges from 3.0 to 29.0 percentage points across systems. For the full agent, "compilation reaches 89.5%, but faithfulness reaches only 60.5%."
  - Preprint.
  - [arXiv](https://arxiv.org/abs/2606.31002)
- **Moore & Shah, "Evaluating Autoformalization Robustness via Semantically Similar Paraphrasing," 2025, arXiv 2511.12784.** Faithfulness is scored by an LLM judge that sees the natural-language statement, the Lean code, and the compile flag; "faithful if and only if the code compiles and the score is >=9." — [arXiv](https://arxiv.org/abs/2511.12784) (judge criterion from a search snippet of the [HTML version](https://arxiv.org/html/2511.12784))
- **Yu et al., "FormalMATH," 2025, arXiv 2505.02735.** Benchmark construction combines "(1) specialized LLMs for statement autoformalization, (2) multi-LLM semantic verification, and (3) negation-based disproof filtering," then human verification. The pipeline "reduces expert annotation costs by retaining 72.09% of statements before manual verification." — [arXiv](https://arxiv.org/abs/2505.02735)
- **Amrollahi, Lopez, Barrett, "Faithful Autoformalization via Roundtrip Verification and Repair," 2026, arXiv 2604.25031.** Reference-free round trip: formalize, informalize, re-formalize, then check logical equivalence with a formal tool. Tested on statutory law (Texas codes), not mathematics. Amrollahi is also a VeriBench co-author. — [arXiv](https://arxiv.org/abs/2604.25031)

### Inferences
- Methods moved in stages. 2022–2023 relied on human review plus BLEU and typecheck. 2024 added back-translation plus NLI with a small LLM, and trained aligners. 2024–2025 brought reference-based formal equivalence (BEq, BEq+, GTED). 2025–2026 brought LLM judges, judge ensembles, and meta-benchmarks for those judges (ConsistencyCheck, ProofNetVerif, CriticLeanBench, Beyond Compilation).
- Human expert review is still the reference standard, but it is itself unreliable: ReForm finds semantic errors in 16.4% of miniF2F and 38.5% of ProofNet human formalizations. This strengthens the case for measuring judges against a carefully validated human criterion rather than assuming the reference is correct.
- Reference-based formal equivalence is high-precision but low-recall (BEq+ recall 48.3%). It also needs a gold formal reference, so it cannot evaluate reference-free generation. That gap is where LLM judges are being used.

### Gaps
- Herald's internal evaluation protocol was not confirmed from its own text; its description comes from Zhang et al. 2026's related-work section.
- Venues not confirmed for ProofNet, CriticLean, Mathesis, FormalMATH, Beyond Gold Standards, and GTED beyond the AI4Math@ICML25 comment.
- The 2025 survey (Weng et al., arXiv 2505.23486, [arXiv](https://arxiv.org/abs/2505.23486)) was searched for LLM-judge statements, and no relevant sentence was found.

---

## Q2. Are LLM judges used at scale to filter autoformalized statements in prover-training pipelines?

### Takeaway
Yes. Nearly every open prover pipeline since 2024 filters autoformalized statements with an LLM, on top of Lean compilation and often negation or contradiction checks. The judge is usually a mid-sized open model (Qwen-1.5-14B, Qwen2.5-72B, QwQ-32B, Qwen3-8B, DeepSeek-V3) sampled several times with voting. The corpora filtered this way range from 57K to 1.78M statements. The teams themselves report false positives and use human spot-checks.

### Cited Findings
- **DeepSeek-Prover V1 (Xin et al., 2024, arXiv 2405.14333).** The DeepSeek-Prover model itself, prompted with few-shot miniF2F-valid examples and chain-of-thought, rates each autoformalized statement "excellent," "good," "above average," "fair," or "poor"; "Statements rated as 'fair' or 'poor' were subsequently excluded." "Manual review of these scores confirmed that the model's evaluations closely matched human intuition" (no numbers given). A second filter, hypothesis rejection, has the prover try to prove `False` from the hypotheses. Result: "a refined set of 712,073 high-quality formal statements," and in total 8M formal statements with proofs. Note that this judge mainly targets quality and triviality ("many formal statements were overly simplistic"), not faithfulness directly. — [arXiv](https://arxiv.org/abs/2405.14333)
- **DeepSeek-Prover-V1.5 (arXiv 2408.08152) and V2 (Ren et al., arXiv 2504.21801).** No new statement-faithfulness judge was found in the full text. V2 "incorporate[s] additional problems derived from autoformalization and various open-source datasets (Ying et al., 2024; …; Lin et al., 2025)," so it inherits upstream LLM-filtered sets. — [V1.5](https://arxiv.org/abs/2408.08152), [V2](https://arxiv.org/abs/2504.21801)
- **Lean Workbook (arXiv 2406.03847).** Qwen-1.5-14B-Chat acts as the NLI judge over back-translations, with human revision of failures, producing 57K problems (see Q1). It is a widely reused training source: Goedel, DeepSeek-V2, and StepFun-Prover all ingest it. — [arXiv](https://arxiv.org/abs/2406.03847)
- **Goedel-Prover (Lin et al., 2025, arXiv 2502.07640).**
  - Two tests: the Compiling Correctness (CC) test and a "Faithfulness and Completeness (FC) Test," which checks that "the formalized statement must accurately capture the original informal problem, incorporating all assumptions, conditions, and implicit definitions."
  - "For the FC test, we use Qwen2.5-72B-Instruct … we generate four independent judgments … We filter out formalized statements with an FC score less than 0.5."
  - FC pass@1 is 48.06% for Formalizer A and 80.42% for Formalizer B.
  - Result: "a total of 1.78M formal statements" (Numina, AOPS, and 140K from Lean Workbook).
  - Venue: UNVERIFIED.
  - [arXiv](https://arxiv.org/abs/2502.07640)
- **Goedel-Prover-V2 (Lin et al., 2025, arXiv 2508.03613).** "we then query Qwen3-8B for 3 times for each formalization, and decide if the formalization is aligned with the informal statement using majority voting." The pipeline combines "Lean syntax checks and semantic evaluation via LLMs … Only statements that pass both checks are included." A separate LLM prompt judges "correctness and simplicity" of synthesized statements. — [arXiv](https://arxiv.org/abs/2508.03613)
- **Kimina-Prover Preview (Wang et al., 2025, arXiv 2504.11354).** Appendix C.2.2, "Expert Iteration with LLM Judge": "We then employ a QwQ-32B as a judge to evaluate the semantic correctness of each remaining formalization … using multiple samples from the judge model and unanimous voting structure significantly reduces the amount of false positives." Caveat in the paper: "LLM-based feedback is susceptible to false positives, we monitor model outputs throughout training with Lean 4 experts and gradually improve the judge prompt." Also: "the model would repeatedly make mistakes that the LLM judge model cannot catch, as long as it passed compilation. We believe this presents a significant challenge in applying reinforcement learning in non-verifiable domains." About 100K autoformalized statements were mixed 1:1 with about 10K human-annotated ones (resampled) into a 200K problem set. — [arXiv](https://arxiv.org/abs/2504.11354)
- **StepFun-Prover Preview (Shang et al., 2025, arXiv 2507.20199).** Found "Tautological statements … Contradictory premises … Irrelevant conclusions … Trivial or ill-posed problems" in both open-source and autoformalized sets; "we employ DeepSeek-V3 to filter out low-quality problems." — [arXiv](https://arxiv.org/abs/2507.20199)
- **StepFun-Formalizer (arXiv 2508.04440).** Data comes from Kimina-Autoformalizer, "followed by majority voting and an LLM-based judge to ensure data quality." Its related work names "expert iteration with LLM judgers (Wang et al. 2025)" as a standard technique. — [arXiv](https://arxiv.org/abs/2508.04440)
- **CriticLean / FineLeanCorpus (arXiv 2507.06181).** A trained LLM critic gates a 285K-problem corpus. — [arXiv](https://arxiv.org/abs/2507.06181)
- **Seed-Prover (Chen et al., 2025, arXiv 2507.23726).** Uses an LLM judge only for lemma "semantic relevance." Contrast quote: "Formal languages like Lean offer rapid proof verification, making them far more cost-effective than human experts and more reliable than LLM judges." — [arXiv](https://arxiv.org/abs/2507.23726)
- **Meta-level confirmation (ReForm, ICLR 2026).** "recent works predominantly rely on LLMs as judges for semantic consistency evaluation in autoformalization," citing Kimina-Prover and Goedel-Prover-V2. — [arXiv](https://arxiv.org/abs/2510.24592)

### Inferences
- In prover data pipelines, LLM-judge filtering is **established practice (2024–2025)**. The typical setup is compile gate, then LLM semantic judge with k samples and voting, then negation/contradiction or triviality filters, with occasional human spot-checks.
- The judge's decisions are rarely validated quantitatively in these pipelines. DeepSeek-V1 and Kimina report qualitative manual checks only. This supports the "trust in the judge" motivation of a judge-certification paper.
- The judge's role shifted from "quality/difficulty rater" (DeepSeek-V1) to "semantic faithfulness gate" (Goedel FC test, Kimina, Goedel-V2).

### Gaps
- AlphaProof (DeepMind) autoformalization filtering is not covered; no primary technical text was retrieved.
- Judge false-positive rates inside these pipelines are generally not reported, so no figures can be given.

---

## Q3. How do spec-generation-for-code benchmarks and tools judge spec quality (nl2postcond, SpecGen, AutoSpec, Clover, VERINA, CLEVER, VeriBench, vericoding, FVAPPS, DafnyBench)?

### Takeaway
Code-spec work leans more on executable or formal checks than autoformalization does:
- verifier acceptance;
- test-based soundness and completeness;
- mutation-based discriminative power;
- symbolic testing;
- proven equivalence or isomorphism to a hidden reference spec.

LLM judges do appear, but mostly as auxiliary filters for translation fidelity or misalignment: Clover's docstring check, vericoding's spec-translation validation, and AlphaVerus's critique. VeriBench (Miranda et al.) is one of the few that uses an LLM judge as a *scoring* factor for statement equivalence.

### Cited Findings
- **Endres, Fakhoury, Chakraborty, Lahiri, "nl2postcond," FSE 2024 (PACMSE), arXiv 2310.01831.** Metrics are "correctness and discriminative power of generated postconditions" (test-set correctness; completeness measured by killing LLM-generated code mutants). Quote: "we believe this paper is the first to propose the use of LLMs to derive a natural distribution of code mutants to evaluate the completeness of specifications." — [arXiv](https://arxiv.org/abs/2310.01831)
- **Ma et al., "SpecGen," ICSE 2025, arXiv 2401.08807** (Java/JML). The main metric is whether specs pass the verifier ("verifiable"). A 120-program dataset has "manually written ground-truth specifications" (three formal-verification experts), plus "a user study was conducted to evaluate the semantic quality of the generated specifications." — [arXiv](https://arxiv.org/abs/2401.08807); venue: [ICSE 2025 page](https://conf.researchr.org/details/icse-2025/icse-2025-research-track/173/SpecGen-Automated-Generation-of-Formal-Program-Specifications-via-Large-Language-Mod)
- **Wen et al., "AutoSpec" ("Enchanting Program Specification Synthesis by LLMs using Static Analysis and Program Verification"), CAV 2024, arXiv 2404.00762** (C/Frama-C). Specs must be "satisfiable and adequate," that is, verifier-accepted and sufficient to prove the target property. The headline metric is "successfully verifying 79% of programs." No faithfulness judge. — [arXiv](https://arxiv.org/abs/2404.00762); venue: [Springer CAV chapter](https://link.springer.com/chapter/10.1007/978-3-031-65630-9_16)
- **Sun, Sheng, Padon, Barrett, "Clover," SAIV 2024 (LNCS), arXiv 2310.17807** (Dafny; bib key `sun2024clover`).
  - Six consistency checks run across code, docstring, and annotations.
  - Annotation equivalence is proved as a formal lemma, and code equivalence is checked by I/O tests.
  - Docstring equivalence is **LLM-judged**: "we ask an LLM (GPT-4) to check whether two docstrings are semantically equivalent"; the prompt is "Do these two docstrings describe the exact same functional behavior of a Dafny program? Return 'Yes' or 'No'."
  - [arXiv](https://arxiv.org/abs/2310.17807); venue: [Springer SAIV 2024](https://link.springer.com/chapter/10.1007/978-3-031-65112-0_7)
- **Lahiri, "Evaluating LLM-driven User-Intent Formalization for Verification-Aware Languages," FMCAD 2024, arXiv 2406.09757.** Advocates "symbolically testing specifications to provide an intuitive metric for evaluating the quality of specifications." The metric "agrees closely on a human-labeled dataset of Dafny specifications for the popular MBPP code-generation benchmark, yet demonstrates cases where the human labeling is not perfect." — [arXiv](https://arxiv.org/abs/2406.09757)
- **Misu, Lopes, Ma, Noble, "Towards AI-Assisted Synthesis of Verified Dafny Methods," FSE 2024, arXiv 2402.00247.** "In order to assess the semantic correctness of the generated verification code, we manually reviewed all verified methods" (focusing on postcondition strength). This is human review. — [arXiv](https://arxiv.org/abs/2402.00247)
- **Loughridge et al., "DafnyBench," 2024, arXiv 2406.08467.** Specs are given (human-written). The task is generating verification hints, so spec quality is not judged. It notes Clover specs sometimes "directly repeat[] the implementation." Venue: UNVERIFIED (the downloaded PDF header said "Preprint"). — [arXiv](https://arxiv.org/abs/2406.08467)
- **Ye et al., "VERINA," ICLR 2026, arXiv 2505.23135** (Lean; 189 tasks). "a multi-stage evaluation pipeline that systematically assesses model-generated specifications by combining theorem proving and comprehensive testing … to score their soundness and completeness against our ground truth specifications." The best model (o3) scores 52.3% on spec soundness and completeness. — [arXiv](https://arxiv.org/abs/2505.23135)
- **Thakur et al., "CLEVER," NeurIPS 2025 Datasets & Benchmarks, arXiv 2505.13938** (Lean; 161 problems). Models must prove "an isomorphism between the generated specification and a human-written specification." Quote: "CLEVER avoids test-case supervision, LLM-generated annotations, and specifications that leak implementation logic or allow vacuous solutions." LLMs solve at most 1/161 end-to-end. — [arXiv](https://arxiv.org/abs/2505.13938)
- **Bursuc et al., "A benchmark for vericoding," 2025, arXiv 2509.22908** (bib key `bursuc2025benchmarkvericodingformallyverified`). Specs are *given* (12,504 in Dafny, Verus, and Lean), and "spec generation is an important problem" is left out of scope. LLM translation of specs was checked by an LLM judge plus manual sampling: "we used the 'LLM as a judge', asking it to compare each translation against its tagged source to verify faithful preservation of preconditions, postconditions, and invariants … Second, through manual inspection … a handful of specifications admitted trivial solutions." Venue: UNVERIFIED. — [arXiv](https://arxiv.org/abs/2509.22908)
- **Dougherty & Mehta, "Proving the Coding Interview" (FVAPPS), LLM4Code@ICSE 2025, arXiv 2502.05714** (Lean; 4,715 samples). Spec sanity comes in assurance tiers. "Guarded" means solutions pass unit tests. "Guarded and Plausible" (1,083 samples) also passes property-based testing; these are "solvable and well-stated to the highest possible probability short of a full proof." — [arXiv](https://arxiv.org/abs/2502.05714)
- **Aggarwal, Parno, Welleck, "AlphaVerus," 2024, arXiv 2412.06176** (Verus). The critique phase combines a rule-based filter, an LLM "comparison model" ("reject an output if at least r sequences indicate rejection"), and an "exploit model." Quote: "critique models detect misaligned translations and specifications–the one part of the pipeline that lacks formal guarantees." Venue: UNVERIFIED. — [arXiv](https://arxiv.org/abs/2412.06176)
- **Zeng et al., "VeriEquivBench," ICLR 2026, arXiv 2510.06296** (Dafny). Replaces ground-truth matching with a formal "equivalence score." Quote: "progress is bottlenecked by specification quality evaluation." It also reports that "10% of expert-written specifications in DafnySynthesis are wrongly claimed as ground-truths, and our own review finds another 18%." — [arXiv](https://arxiv.org/abs/2510.06296)
- **Yan et al., "Re:Form," TMLR 05/2026, arXiv 2507.16331** (Dafny). Grades outputs as Syntax Error, then Syntax Correct, then Verified, then "Verified with Superior Specification" (a spec stronger than the ground truth), with a spec-subset reward. This is a formal check, not an LLM judge. — [arXiv](https://arxiv.org/abs/2507.16331)
- **Shefer et al., "Can LLMs Enable Verification in Mainstream Programming?," 2025, arXiv 2503.14183.** Uses manually curated HumanEval-derived Dafny, Nagini, and Verus reference solutions. — [arXiv](https://arxiv.org/abs/2503.14183)
- **Miranda et al., "VeriBench"** (bib key `miranda2026veribench`, AI4Math workshop 2026, OpenReview lkL0qnUv3p; OpenReview was not readable here). The longer version PDF on the author's Stanford page says:
  - The SCSC score is "a log-domain geometric mean over five per-task factors."
  - Its theorem-equivalence factor "TE1 is computed by a Claude Sonnet 4.6 LLM judge over extracted agent and gold theorem statements."
  - "A separate Codex CLI rubric check reaches raw Pearson r = 0.61 on a pool labeled by five human raters, with weaker rank correlations (ρ≈0.38)."
  - Estimated theorem–gold equivalence is "≤ 0.156 across evaluated systems."
  - [Stanford PDF](https://cs.stanford.edu/people/brando9/professional_documents/papers/NeurIPS_2026_VeriBench.pdf)
  - **Version caution:** task counts differ across versions (this PDF says 884 tasks; a search snippet says 896; the ICLR draft says 857 theorems). Cite the version matching the bib entry.

### Inferences
- For **code specs**, the established evaluation is formal or executable: verifier acceptance, tests and mutants, symbolic testing, and proven equivalence to a reference (VERINA, CLEVER, VeriEquivBench). LLM judges show up as auxiliary fidelity filters (Clover, vericoding, AlphaVerus) and, in VeriBench, as a reference-equivalence scoring factor. That makes LLM-judged spec quality an **emerging** practice here, less established than in math autoformalization.
- Both communities report that expert reference specs are themselves error-prone (VeriEquivBench: 10% + 18% in DafnySynthesis; Lahiri: human labels "not perfect"; ReForm for math). Reference-only evaluation therefore has a trust problem too.

### Gaps
- Neither the VeriBench workshop (OpenReview) version nor its human-agreement numbers could be read; the numbers above come from the NeurIPS-2026-labeled PDF.
- Recent 2026 Verus spec work (for example Verus-SpecGym, arXiv 2605.26457; VeriAct, arXiv 2604.00280) turned up only in search titles and was not read.

---

## Q4. Do papers explicitly say that the kernel/verifier cannot check statement or spec faithfulness, and that this is an open evaluation problem?

### Takeaway
Yes, this is stated explicitly and repeatedly in ML (ICLR/NeurIPS), formal-methods (FMCAD), and prover technical reports. The quotes below can be used directly.

### Cited Findings
- "Lean verifies that a generated declaration is well typed, but not that it expresses the statement a user intended." — Zhang et al. 2026, [arXiv 2606.31002](https://arxiv.org/abs/2606.31002) (abstract)
- "Unlike proof search, where success is easily defined by whether a theorem is proven, there is no straightforward way to verify the correctness of a generated formal problem statement with respect to the natural language input." — Kimina-Prover Preview, [arXiv 2504.11354](https://arxiv.org/abs/2504.11354) §2.1
- "Although the problem of checking an implementation against a specification can be defined mechanically, there is no algorithmic way of ensuring the correctness of the user-intent formalization for programs — that a specification adheres to the user's intent behind the program. This is because intent or requirement is expressed informally in natural language and the specification is a formal artefact." — Lahiri, FMCAD 2024, [arXiv 2406.09757](https://arxiv.org/abs/2406.09757) (abstract)
- "Because there may be multiple ways to formalize the same statement in Lean and no general way to automatically verify whether two statements that are not definitionally equal have the same mathematical content, autoformalizations are evaluated for correctness by a human expert." — ProofNet, [arXiv 2302.12433](https://arxiv.org/abs/2302.12433) §4.1
- "Type check is too weak to filter out syntactically correct but semantically absurd autoformalization. It is a necessary but not sufficient condition for the ideal equivalence." and "absence of faithful and universal automated evaluation for autoformalization results" — Liu et al., ICLR 2025, [PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/d630537fc4402cfa3ebbc7450a0cac91-Paper-Conference.pdf)
- "critique models detect misaligned translations and specifications–the one part of the pipeline that lacks formal guarantees." — AlphaVerus, [arXiv 2412.06176](https://arxiv.org/abs/2412.06176)
- "a fundamental question remains largely unaddressed: when an LLM produces a formalization, how do we know it faithfully captures the meaning of the original text? Existing evaluations rely on syntactic validity or downstream task success, neither of which directly tests semantic fidelity." — Amrollahi, Lopez, Barrett 2026, [arXiv 2604.25031](https://arxiv.org/abs/2604.25031)
- "progress is bottlenecked by specification quality evaluation. Current benchmarks rely on matching against ground-truth specifications, a manual and expertise-intensive process … and also suffers from a reliability issue." — VeriEquivBench, ICLR 2026, [arXiv 2510.06296](https://arxiv.org/abs/2510.06296)
- "the model would repeatedly make mistakes that the LLM judge model cannot catch, as long as it passed compilation. We believe this presents a significant challenge in applying reinforcement learning in non-verifiable domains." — Kimina-Prover Preview, [arXiv 2504.11354](https://arxiv.org/abs/2504.11354) App. C.2
- "ensuring semantic alignment between the informal and formalized statements remains challenging. Existing approaches heavily rely on manual verification, hindering scalability." — FormalAlign, ICLR 2025, [arXiv 2410.10135](https://arxiv.org/abs/2410.10135)

### Inferences
- The "kernel checks proofs, not meaning" gap is consensus framing from 2023 to 2026, so the ICLR paper can cite 2–3 of these directly (strongest: Lahiri 2024, ProofNet 2023, Kimina 2025, Zhang et al. 2026) instead of arguing the point itself.

### Gaps
- None material for this question.

---

## Q5 (synthesis). Does the draft claim hold ("LLM judges are increasingly central to evaluating AI-generated … formal specifications")? And which bib keys match?

### Takeaway
The claim is **supported, but should be scoped**:
- It is established for filtering autoformalized theorem statements in prover training. Examples include Lean Workbook 2024, Goedel-Prover 2025 (1.78M statements), Kimina-Prover 2025, Goedel-Prover-V2, and StepFun.
- It is emerging and contested as the *evaluation metric* for statement faithfulness (ReForm, Beyond Compilation, Beyond Gold Standards, LeanScorer, CriticLean, VeriBench).
- It is auxiliary in code-spec evaluation, where formal, test, and mutation checks dominate.
- ReForm (ICLR 2026) says it directly: "recent works predominantly rely on LLMs as judges … the reliability of these LLM-based judges is not sufficiently studied."

### Cited Findings
- Scale and centrality evidence:
  - Goedel-Prover FC test over 1.78M statements ([arXiv 2502.07640](https://arxiv.org/abs/2502.07640)).
  - Kimina QwQ-32B judge ([arXiv 2504.11354](https://arxiv.org/abs/2504.11354)).
  - Goedel-V2 Qwen3-8B majority vote ([arXiv 2508.03613](https://arxiv.org/abs/2508.03613)).
  - ReForm "predominantly rely" quote ([arXiv 2510.24592](https://arxiv.org/abs/2510.24592)).
- Counter-evidence and caveats:
  - BEq calls LLM graders "non-determinant and highly dependent on prompts" ([ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/d630537fc4402cfa3ebbc7450a0cac91-Paper-Conference.pdf)).
  - GTED cites "reproducibility and high cost concerns" ([arXiv 2507.07399](https://arxiv.org/abs/2507.07399)).
  - CLEVER explicitly avoids "LLM-generated annotations" ([arXiv 2505.13938](https://arxiv.org/abs/2505.13938)).
  - Seed-Prover calls Lean "more reliable than LLM judges" ([arXiv 2507.23726](https://arxiv.org/abs/2507.23726)).
- Measured judge–human agreement:
  - 85.8% (frontier LLMs, ConsistencyCheck; [ReForm](https://arxiv.org/abs/2510.24592)).
  - 89.7% (GPT-5.2 + Gemini-2.5-Pro consensus; [Zhang et al. 2026](https://arxiv.org/abs/2606.31002)).
  - FormalAlign vs GPT-4 alignment selection 88.91% on FormL4-Basic ([arXiv 2410.10135](https://arxiv.org/abs/2410.10135)).
  - VeriBench rubric r = 0.61, ρ ≈ 0.38 ([Stanford PDF](https://cs.stanford.edu/people/brando9/professional_documents/papers/NeurIPS_2026_VeriBench.pdf)).

**Bib-key matches (checked against `paper_latex/ICLR_2027_submission/refs.bib`):**
- `sun2024clover` matches Clover, arXiv 2310.17807 (authors correct). The published venue is SAIV 2024 (LNCS) ([Springer](https://link.springer.com/chapter/10.1007/978-3-031-65112-0_7)); the entry could be upgraded from @MISC.
- `bursuc2025benchmarkvericodingformallyverified` matches arXiv 2509.22908 (13 authors match). Relevant quote: spec translations validated by "LLM as a judge" plus manual inspection.
- `miranda2026veribench` matches VeriBench (AI4Math workshop 2026, OpenReview lkL0qnUv3p). Caution: task counts differ across versions (857 / 884 / 896).
- `wang2024theoremLlama` matches arXiv 2407.03203 (Ruida Wang et al.; confirmed via arXiv API). It is about NL–Lean data generation, not faithfulness evaluation; its judge usage was not examined.
- `aniva2025pantograph` matches arXiv 2410.16429 (2024 submission; the entry's YEAR=2024 while the key says 2025). Not relevant to this topic.
- `chen2026rethinking` is **NOT** the BEq paper. It is Chen, Gulati, Miranda, Tang, Koyejo, "Rethinking LLM Judges: CoT and Multi-Step Pipelines for Math Grading" (ICLR 2026 LLM-reasoning workshop). **The BEq paper (Liu et al., ICLR 2025) needs a new bib key**, e.g. `liu2025rethinkingautoformalization`, with URL https://openreview.net/forum?id=hUb2At2DsQ.
- `ospanov2023apollo` looks **WRONG**. The actual paper is "APOLLO: Automated LLM and Lean Collaboration for Advanced Formal Reasoning," Azim Ospanov, Farzan Farnia, Roozbeh Yousefzadeh, **arXiv 2505.05758 (May 2025)**, confirmed via arXiv API ([arXiv](https://arxiv.org/abs/2505.05758)). The bib title ("Apollo: Recursive Repair with Lean Feedback Boosts MiniF2F Proof Success"), year (2023), and authors ("Ospanov et al.") do not match any record found. Fix it.
- `anonymous2025formaljudge` is this project's own anonymous prior work; there is no public record to match.
- **Suggested new keys** (all arXiv-verified):
  - Wu et al. 2022 (2205.12615)
  - ProofNet (2302.12433)
  - Lean Workbook (2406.03847)
  - DeepSeek-Prover (2405.14333)
  - Goedel-Prover (2502.07640)
  - Goedel-Prover-V2 (2508.03613)
  - Kimina-Prover (2504.11354)
  - FormalAlign (2410.10135)
  - Poiroux et al. (2406.07222)
  - ReForm (2510.24592)
  - Beyond Gold Standards (2506.10903)
  - Beyond Compilation (2606.31002)
  - CriticLean (2507.06181)
  - FormalMATH (2505.02735)
  - nl2postcond (2310.01831)
  - Lahiri FMCAD (2406.09757)
  - VERINA (2505.23135)
  - CLEVER (2505.13938)
  - AlphaVerus (2412.06176)
  - VeriEquivBench (2510.06296)
  - FVAPPS (2502.05714)
  - SpecGen (2401.08807)
  - AutoSpec (2404.00762)

### Inferences
- Safer wording for the paper: "LLM judges are increasingly used, and in prover-training pipelines are often the only scalable check, to decide whether AI-generated formal statements and specifications faithfully capture intent (e.g., Ying et al. 2024; Lin et al. 2025; Wang et al. 2025), yet their reliability is rarely validated against human criteria (Chen et al. 2025 [ReForm]; Zhang et al. 2026)."
- Avoid implying that LLM judges are the *established evaluation standard* for code specs. There, VERINA, CLEVER, and VeriEquivBench deliberately use formal or test-based reference checks.

### Gaps
- Venue status is UNVERIFIED for Goedel-Prover, Kimina-Prover, CriticLean, Mathesis, FormalMATH, vericoding, AlphaVerus, and Beyond Gold Standards. Cite them as arXiv preprints unless a venue is confirmed.
- No paper was found that quantifies what share of autoformalization papers use LLM judges. "Increasingly" rests on the timeline plus ReForm's "predominantly rely" statement, not on a bibliometric count.
