# Adoption and Centrality of LLM-as-a-Judge in AI/ML Evaluation (2023–2026)

Scope: the GENERAL claim "LLM judges are increasingly central to evaluating AI outputs." Code/tests/formal-spec evidence is covered by other researchers.

Verification method (2026-09-22): every arXiv id below was resolved via the arXiv export API (`export.arxiv.org/api/query?id_list=...`). Title, authors, and the arXiv `comments`/`journal_ref` field were checked. Venue and citation counts come from the Semantic Scholar Graph API batch endpoint (`api.semanticscholar.org/graph/v1/paper/batch`). Citation counts are Semantic Scholar snapshots from 2026-09-22. They are noisy: some records look split, e.g. "Cheating Automatic LLM Benchmarks" shows only 48. Use them as orders of magnitude, not exact figures. Quoted sentences are verbatim from arXiv abstracts unless a section is named. "UNVERIFIED" marks anything I could not confirm in this session.

## Q1. Which surveys of LLM-as-a-judge exist, and what do they say about scale and adoption?

### Takeaway
By late 2024 there were at least three dedicated LLM-as-a-judge surveys and two broader LLM-based NLG-evaluation surveys. The most-cited has about 1.8k Semantic Scholar citations. They describe adoption only qualitatively ("rapidly", "growing attention from both academia and industry"). None of the surveys I checked gives an adoption count. The best count I found is a 2026 ACL Anthology keyword study that finds 650 papers mentioning LLM-as-a-judge.

### Cited Findings
**Dedicated LLM-as-a-judge surveys**
- **Gu, Jiang, Shi, et al. (16 authors), "A Survey on LLM-as-a-Judge," arXiv:2411.15594 (v1 2024-11-23; v6 2025-10).** arXiv and Semantic Scholar list it as an arXiv preprint with no venue. It has about 1,832 Semantic Scholar citations. The abstract says LLMs "present a compelling alternative to traditional expert-driven evaluations" and that "ensuring the reliability of LLM-as-a-Judge systems remains a significant challenge." The introduction says "the adoption of LLM in evaluation has progressed rapidly in practice" (Sec. 1). It also mentions LLM use in ICLR 2025 peer review, via a footnote. It gives no publication counts or growth figures. — [arXiv abs](https://arxiv.org/abs/2411.15594); [HTML v6](https://arxiv.org/html/2411.15594v6)
- **Dawei Li, Bohan Jiang, Liangjie Huang, et al. (13 authors), "From Generation to Judgment: Opportunities and Challenges of LLM-as-a-judge," arXiv:2411.16594.** The arXiv comment says "EMNLP 2025", which matches ACL Anthology `2025.emnlp-main.138`. About 682 Semantic Scholar citations. It proposes a taxonomy of "what to judge, how to judge, and how to benchmark". It says LLMs are used "to perform scoring, ranking, or selection for various machine learning evaluation scenarios." — [arXiv](https://arxiv.org/abs/2411.16594); [ACL Anthology PDF](https://aclanthology.org/2025.emnlp-main.138.pdf)
- **Haitao Li, Qian Dong, Junjie Chen, et al. (8 authors), "LLMs-as-Judges: A Comprehensive Survey on LLM-based Evaluation Methods," arXiv:2412.05579 (2024-12-07).** A 60-page arXiv preprint with about 619 Semantic Scholar citations. It says the framework "has attracted growing attention from both academia and industry due to their excellent effectiveness, ability to generalize across tasks, and interpretability." — [arXiv](https://arxiv.org/abs/2412.05579)

**Broader LLM-based evaluation surveys**
- **Mingqi Gao, Xinyu Hu, Jie Ruan, et al., "LLM-based NLG Evaluation: Current Status and Challenges," arXiv:2402.01383 (2024).** Semantic Scholar lists the venue as *Computational Linguistics*; the arXiv record does not state a venue. About 153 citations. It classifies methods into LLM-derived metrics, prompting, fine-tuning, and human–LLM collaborative evaluation. — [arXiv](https://arxiv.org/abs/2402.01383)
- **Zhen Li, Xiaohan Xu, Tao Shen, et al., "Leveraging Large Language Models for NLG Evaluation: Advances and Challenges," arXiv:2401.07103 (2024).** Semantic Scholar lists the venue as EMNLP 2024. About 47 citations. — [arXiv](https://arxiv.org/abs/2401.07103)
- **Yupeng Chang, Xu Wang, Jindong Wang, et al. (16 authors), "A Survey on Evaluation of Large Language Models," arXiv:2307.03109 (2023).** Published in ACM Transactions on Intelligent Systems and Technology (TIST), per the arXiv comment. About 3,815 citations. It covers LLM evaluation in general, not judges specifically. — [arXiv](https://arxiv.org/abs/2307.03109)

**Position papers and meta-studies that describe adoption**
- **Doğruöz, Liao, Blaschke, Prange, Li, Adelani, "Challenges and Recommendations for LLM-as-a-Judge in Multilingual Settings and for Low-Resource Languages," arXiv:2607.02235 (submitted 2026-09-09).**
  - Abstract: "LLM-as-a-Judge has become the dominant evaluation paradigm for many natural language generation tasks (albeit mostly in English) due to shortcomings of conventional metrics and high correlations with human judgment."
  - Method (Sec. 3): a reproducible keyword search over the titles and abstracts of the whole ACL Anthology, pinned to snapshot commit `370911e` from 2025-11-14. The script is at github.com/verenablaschke/aclanthology-llmasajudge.
  - Result: "Out of 650 papers mentioning LLM-as-a-judge, only 33 of them focus on low-resource or multilingual settings." There were 49 candidates before manual screening.
  - [arXiv PDF](https://arxiv.org/pdf/2607.02235)
- **Chehbouni, Haddou, Cheung, et al., "Neither Valid nor Reliable? Investigating the Use of LLMs as Judges," arXiv:2508.18076 (2025).** A position paper: "their adoption has outpaced rigorous scrutiny of their reliability and validity as evaluators." It uses measurement theory to examine four assumptions: that judges proxy human judgment, that they are capable evaluators, that they scale, and that they are cost-effective. Venue conflict: Semantic Scholar lists NeurIPS 2025, but the arXiv comment only says "Prepared for conference submission" (treat NeurIPS 2025 as UNVERIFIED). It gives no adoption numbers. — [arXiv](https://arxiv.org/abs/2508.18076)

### Inferences
- Having three dedicated surveys within about three weeks (Nov–Dec 2024) is itself evidence that the practice had become a recognized subfield by late 2024. MT-Bench/Chatbot Arena coined the term "LLM-as-a-judge" in June 2023, per Doğruöz et al. (arXiv:2607.02235, Sec. 1).
- For the ICLR abstract, the safest survey citations are Gu et al. 2024 (most cited) and Li et al. 2025 (EMNLP 2025, peer-reviewed). Doğruöz et al. 2026 supplies the only quotable count (650 ACL Anthology papers) and the "dominant evaluation paradigm" wording. It is a fresh, non-peer-reviewed preprint.

### Gaps
- None of the surveys gives a quantitative adoption rate, such as the percent of papers or benchmarks that use LLM judges. I found no systematic "X% of NeurIPS/ICLR papers use LLM judges" study.
- The Doğruöz et al. count of 650 is a title/abstract keyword count. It is a lower bound on usage and not a rate: no denominator for the whole Anthology is reported in the text I read.

## Q2. Which widely used benchmarks and leaderboards rely on LLM judges?

### Takeaway
Most of the standard open-ended chat and instruction-following benchmarks use an LLM judge: MT-Bench, AlpacaEval (2.0 / length-controlled), Arena-Hard-Auto, and WildBench. Each validates itself by correlating with Chatbot Arena human Elo, at 0.89–0.98. By 2025, frontier-lab benchmarks also use LLM graders even for closed-form or rubric tasks: HLE uses o3-mini, HealthBench uses GPT-4.1, and PaperBench uses its own LLM judge. Frontier model reports, e.g. DeepSeek-R1, report these LLM-judged scores as headline metrics.

### Cited Findings
**Benchmarks scored by an LLM judge**
- **MT-Bench (and the coining of "LLM-as-a-judge"). Zheng, Chiang, Sheng, et al. (13 authors), "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena," arXiv:2306.05685, NeurIPS 2023 Datasets & Benchmarks Track** (per the arXiv comment).
  - "strong LLM judges like GPT-4 can match both controlled and crowdsourced human preferences well, achieving over 80% agreement, the same level of agreement between humans."
  - It also names position, verbosity, and self-enhancement biases.
  - About 11,349 Semantic Scholar citations, the most cited paper in this note.
  - **[= existing bib key `Zheng2023MTBench`.** The bib entry is an arXiv @MISC; it could be upgraded to the NeurIPS 2023 D&B venue.]
  - [arXiv](https://arxiv.org/abs/2306.05685)
- **G-Eval. Yang Liu, Dan Iter, Yichong Xu, et al., "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment," arXiv:2303.16634.** Semantic Scholar lists EMNLP 2023. "G-Eval with GPT-4 as the backbone model achieves a Spearman correlation of 0.514 with human on summarization task." The paper also flags "a bias towards the LLM-generated texts." About 3,185 citations. **[= existing key `Liu2023GEval`.]** — [arXiv](https://arxiv.org/abs/2303.16634)
- **AlpacaFarm. Dubois, Li, Taori, et al., arXiv:2305.14387, NeurIPS 2023 Spotlight.** It designs "LLM prompts to simulate human feedback that are 50x cheaper than crowdworkers and display high agreement with humans." This is the precursor of the AlpacaEval auto-annotator. — [arXiv](https://arxiv.org/abs/2305.14387)
- **Length-Controlled AlpacaEval. Dubois, Galambosi, Liang, Hashimoto, arXiv:2404.04475, COLM 2024.** "LLM-based auto-annotators have become a key component of the LLM development process due to their cost-effectiveness and scalability compared to human-based evaluation." Length control "increases the Spearman correlation with LMSYS Chatbot Arena from 0.94 to 0.98." About 962 citations. — [arXiv](https://arxiv.org/abs/2404.04475)
  - UNVERIFIED this session: the original AlpacaEval software citation (Li, Zhang, Dubois, et al. 2023, GitHub tatsu-lab/alpaca_eval). Cite the COLM 2024 paper above instead.
- **Arena-Hard-Auto / BenchBuilder. Tianle Li, Wei-Lin Chiang, Evan Frick, et al., arXiv:2406.11939.** Semantic Scholar lists ICML 2025 (year field 2024). It uses "LLM-as-a-Judge for automatic model evaluation" on 500 prompts. It reports "3x higher separation of model performances compared to MT-Bench and achieves 98.6% correlation with human preference rankings, all at a cost of $20." — [arXiv](https://arxiv.org/abs/2406.11939)
- **WildBench. Bill Yuchen Lin, Yuntian Deng, Khyathi Chandu, et al., arXiv:2406.04770.** Semantic Scholar lists ICLR 2025. It has 1,024 tasks from real user logs, and its metrics are "computable using advanced LLMs such as GPT-4-turbo." Pearson correlations with Chatbot Arena Elo on hard tasks:

  | Metric | Pearson r |
  |---|---|
  | WB-Reward | 0.98 |
  | WB-Score | 0.95 |
  | ArenaHard | 0.91 |
  | AlpacaEval 2.0, length-controlled | 0.89 |
  | AlpacaEval 2.0, regular | 0.87 |

  — [arXiv](https://arxiv.org/abs/2406.04770)
- **ChatEval. Chi-Min Chan, Weize Chen, Yusheng Su, et al., arXiv:2308.07201.** Uses multi-agent debate among LLM evaluators. About 990 citations. Semantic Scholar lists the venue as arXiv; ICLR 2024 is from my memory and UNVERIFIED this session. **[= existing key `Chan2024ChatEval`. BIB ERROR: the bib author is "Zheng Cheng Chan", but arXiv lists the first author as "Chi-Min Chan".]** — [arXiv](https://arxiv.org/abs/2308.07201)

**Chatbot Arena: the human-vote reference these benchmarks validate against**
- **Chiang, Zheng, Sheng, et al., "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference," arXiv:2403.04132, ICML 2024.** Arena rankings come from human votes, not an LLM judge. It serves as the human reference that the LLM-judged benchmarks above correlate against. About 1,554 citations. — [arXiv](https://arxiv.org/abs/2403.04132)

**Dedicated judge models (a research subfield in its own right)**
- Prometheus (Kim et al., arXiv:2310.08491, ICLR 2024). — [arXiv](https://arxiv.org/abs/2310.08491)
- Prometheus 2 (Kim et al., arXiv:2405.01535, EMNLP 2024 main). — [arXiv](https://arxiv.org/abs/2405.01535)
- JudgeLM (Zhu, Wang, Wang, arXiv:2310.17631, ICLR 2025). — [arXiv](https://arxiv.org/abs/2310.17631)
- PandaLM (Wang et al., arXiv:2306.05087, ICLR 2024). — [arXiv](https://arxiv.org/abs/2306.05087)

**Frontier-lab benchmarks with LLM graders (2024–2025)**
- **Humanity's Last Exam. Phan, Gatti, Han, et al. (1,158 authors), arXiv:2501.14249.** Semantic Scholar lists a *Nature* 2025 publication under a different title. Sec. 4.1: "we use o3-mini as a judge to verify answer correctness against model predictions while accounting for equivalent formats." This is notable: even a closed-ended benchmark relies on an LLM judge for answer matching. — [arXiv HTML](https://arxiv.org/html/2501.14249)
- **HealthBench. Arora, Wei, Hicks, et al. (OpenAI), arXiv:2505.08775.**
  - Size: 5,000 conversations and 48,562 rubric criteria written by 262 physicians.
  - Grader: "a model-based grader, validated against physician judgment", namely GPT-4.1 (Sec. 8.1).
  - Meta-evaluation: "Model-physician agreement is similar to physician-physician agreement". GPT-4.1 macro F1 is 0.709 (Sec. 8.1, Table 6).
  - [arXiv HTML](https://arxiv.org/html/2505.08775)
- **PaperBench. Starace, Jaffe, Sherburn, et al. (OpenAI), arXiv:2504.01848.** Semantic Scholar lists ICML 2025. It has 8,316 gradable rubric tasks. "we also develop an LLM-based judge to automatically grade replication attempts against rubrics, and assess our judge's performance by creating a separate benchmark for judges." — [arXiv](https://arxiv.org/abs/2504.01848)
- **SimpleQA. Wei, Karina, Chung, et al. (OpenAI), arXiv:2411.04368.** Each answer is graded "correct, incorrect, or not attempted." That the grading uses a prompted model grader is from my memory of the paper and simple-evals, and is UNVERIFIED this session; the abstract does not say so. — [arXiv](https://arxiv.org/abs/2411.04368)

**Frontier model reports that headline LLM-judged scores**
- **DeepSeek-R1 (DeepSeek-AI, arXiv:2501.12948).**
  - Its evaluation tables report "AlpacaEval2.0 (LC-winrate)" and "ArenaHard (GPT-4-1106)" (Sec. D.1 / Table 3).
  - For training the helpfulness reward model: "For each preference pair, we query DeepSeek-V3 four times, randomly assigning the responses as either Response A or Response B to mitigate positional bias" (Sec. 3.1).
  - [arXiv HTML](https://arxiv.org/html/2501.12948)

**How the field itself describes these benchmarks**
- Zheng et al. (arXiv:2410.07137, ICLR 2025 Oral): "Automatic LLM benchmarks, such as AlpacaEval 2.0, Arena-Hard-Auto, and MT-Bench, have become popular for evaluating language models due to their cost-effectiveness and scalability compared to human evaluation. Achieving high win rates on these benchmarks can significantly boost the promotional impact of newly released language models." — [arXiv](https://arxiv.org/abs/2410.07137)

### Inferences
- The main open-ended chat leaderboards of 2023–2025 all rest on LLM judges. Each validates itself by correlating with human Elo. That is population-level (system-ranking) agreement, not per-item validity. This distinction matters for the paper's argument.
- HLE, HealthBench, and PaperBench show judges moving from "chat quality" into correctness grading and expert-rubric grading at frontier labs. This supports "increasingly central" beyond chatbots.

### Gaps
- I did not verify the exact judge model version each leaderboard currently uses (AlpacaEval 2.0 annotator, Arena-Hard v2 judge). These change over time.
- I did not collect Llama 3, Qwen, GPT, Claude, or Gemini model cards to count how many frontier reports cite LLM-judged benchmarks. DeepSeek-R1 is the only one verified here.

## Q3. Is there quantitative adoption evidence (fraction of papers or benchmarks, industry reports, frontier-lab pipelines, RLAIF/reward models)?

### Takeaway
Hard adoption rates are scarce. The citable numbers are:
- An industry survey (LangChain, 1,340 respondents, Nov–Dec 2025): 53.3% use LLM-as-judge.
- 650 ACL Anthology papers mentioning LLM-as-a-judge (Doğruöz et al. 2026).
- Keyword counts that grow steeply from 2023 to 2026. These are my own reproducible arXiv / Semantic Scholar queries.
- Heavy citation of the founding papers: MT-Bench about 11.3k citations, Constitutional AI about 3.7k.

On the training side, RLAIF, Constitutional AI, and Self-Rewarding make LLM judgments a reward signal, not just an evaluation tool.

### Cited Findings
**Industry survey**
- **LangChain, "State of Agent Engineering" report.** The page is dated 2026-06-12. Survey of 1,340 respondents, 2025-11-18 to 2025-12-02. It reports "LLM-as-judge (53.3%)", "human review (59.8%)", "offline evaluations (52.4%)", and "online evaluations 37.3%". Quote: "These organizations running evals also rely on a mix of human and automated approaches for evaluation, implementing LLM-as-judge for breadth and human review for depth." Caveats: this is a vendor survey, and the 53.3% denominator appears to be organizations that run evals, not all respondents (ambiguous on the page). — [LangChain report](https://www.langchain.com/state-of-agent-engineering)

**Paper counts**
- **ACL Anthology count.** 650 papers match "LLM"/"large language model" + "judge"/"evaluator"/"LLM-as-a-judge"/... in the title or abstract (snapshot 2025-11-14). — [Doğruöz et al., arXiv:2607.02235, Sec. 3](https://arxiv.org/pdf/2607.02235)
- **My own arXiv API counts** (abstract phrase search, run 2026-09-22; reproducible via `export.arxiv.org/api/query?search_query=...`):

  | Year | Exact `"LLM-as-a-judge"` | Broad phrase set* | All cs.CL/cs.LG/cs.AI | Broad share |
  |---|---|---|---|---|
  | 2022 | 1 | 2 | 40,536 | — |
  | 2023 | 4 | 56 | 51,034 | about 0.11% |
  | 2024 | 103 | 316 | 67,318 | about 0.47% |

  \*Broad set: `"LLM-as-a-judge" OR "LLM judge(s)" OR "LLM-as-judge" OR "LLM evaluator(s)"`.

  The 2025 and 2026 queries returned empty responses (API failure or throttling), so NOT OBTAINED. The arXiv phrase search is known to under-match hyphenated phrases, so treat these as lower bounds. — [arXiv API](https://export.arxiv.org/api/query?search_query=abs:%22LLM-as-a-judge%22+AND+submittedDate:%5B202401010000+TO+202412312359%5D&max_results=1)
- **My own Semantic Scholar bulk-search counts** for the phrase `"LLM-as-a-judge"` by year, run 2026-09-22:

  | Year | Papers |
  |---|---|
  | 2022 | 1 |
  | 2023 | 5 |
  | 2024 | 120 |
  | 2025 | 645 |
  | 2026 (to Sep 22) | 913 |

  These are noisy keyword matches, not usage rates. — [Semantic Scholar API](https://api.semanticscholar.org/graph/v1/paper/search/bulk?query=%22LLM-as-a-judge%22&year=2025&fields=title)

**Citation counts** (Semantic Scholar, 2026-09-22)

| Paper | Citations |
|---|---|
| MT-Bench/LLM-as-a-judge (2306.05685) | 11,349 |
| Constitutional AI (2212.08073) | 3,707 |
| G-Eval (2303.16634) | 3,185 |
| Gu et al. survey (2411.15594) | 1,832 |
| Wang et al. "not Fair Evaluators" (2305.17926) | 1,292 |
| LC-AlpacaEval (2404.04475) | 962 |
| Panickssery self-preference (2404.13076) | 792 |
| RLAIF vs RLHF (2309.00267) | 730 |
| Self-Rewarding (2401.10020) | 716 |

— [Semantic Scholar Graph API](https://api.semanticscholar.org/graph/v1/paper/arXiv:2306.05685?fields=citationCount)

**LLM judgments as a training signal (RLAIF / reward models)**
- **Constitutional AI. Bai, Kadavath, Kundu, et al. (51 authors, Anthropic), arXiv:2212.08073 (Dec 2022).** "In the RL phase, we sample from the finetuned model, use a model to evaluate which of the two samples is better, and then train a preference model from this dataset of AI preferences. We then train with RL using the preference model as the reward signal, i.e. we use 'RL from AI Feedback' (RLAIF)." It predates the 2023 window but is the origin of the practice. — [arXiv](https://arxiv.org/abs/2212.08073)
- **RLAIF vs. RLHF. Harrison Lee, Samrat Phatale, Hassan Mansoor, et al. (Google), arXiv:2309.00267, ICML 2024 (PMLR 235:26874–26901).** "RLAIF achieves comparable performance to RLHF" on summarization, helpful dialogue, and harmless dialogue. It also introduces d-RLAIF, which takes rewards directly from an off-the-shelf LLM. — [arXiv](https://arxiv.org/abs/2309.00267)
- **Self-Rewarding Language Models. Weizhe Yuan, Richard Yuanzhe Pang, Kyunghyun Cho, et al. (Meta/NYU), arXiv:2401.10020, ICML 2024.** "the language model itself is used via LLM-as-a-Judge prompting to provide its own rewards during training." — [arXiv](https://arxiv.org/abs/2401.10020)
- **DeepSeek-R1 (arXiv:2501.12948, Sec. 3.1)** uses DeepSeek-V3 pairwise judgments, queried four times with position randomization, to train its helpfulness reward model. — [arXiv HTML](https://arxiv.org/html/2501.12948)
- **Ye et al., "Justice or Prejudice?" (arXiv:2410.02736; Semantic Scholar lists ICLR 2025):** "LLM-as-a-Judge has been widely utilized as an evaluation method in various benchmarks and served as supervised rewards in model training." — [arXiv](https://arxiv.org/abs/2410.02736)

**Quotable adoption statements from peer-reviewed papers**
- Bavaresco et al., ACL 2025: "There is an increasing trend towards evaluating NLP models with LLMs instead of human judgments." — [arXiv:2406.18403](https://arxiv.org/abs/2406.18403)
- Tan et al., JudgeBench, ICLR 2025: "LLM-based judges have emerged as a scalable alternative to human evaluation and are increasingly used to assess, compare, and improve models." — [arXiv:2410.12784](https://arxiv.org/abs/2410.12784)
- Zeng et al., LLMBar, ICLR 2024: "LLM-based evaluation has emerged as a scalable and cost-effective alternative to human evaluations." — [arXiv:2310.07641](https://arxiv.org/abs/2310.07641)
- Dubois et al., COLM 2024: auto-annotators are "a key component of the LLM development process." — [arXiv:2404.04475](https://arxiv.org/abs/2404.04475)

### Inferences
- The growth curves agree with each other. On Semantic Scholar the exact phrase goes from about 5 papers (2023) to 120 (2024) to 645 (2025) to 913 (2026, partial year). On arXiv the broad phrase set goes from 56 (2023) to 316 (2024), roughly 4x of the cs.CL/LG/AI share. Together these support "increasingly". Present them in the paper as keyword-mention counts, if at all, not as usage rates.
- The strongest single citable line for "central" is Doğruöz et al.'s "the dominant evaluation paradigm for many natural language generation tasks." It is a 2026 preprint, so pair it with peer-reviewed statements (Bavaresco ACL 2025; JudgeBench ICLR 2025).
- RLAIF, CAI, Self-Rewarding, and DeepSeek-R1 show that judges shape training as well as evaluation. This raises the stakes of judge validity; Bowman et al. 2022, key `bowman2022scalable`, gives the scalable-oversight framing.

### Gaps
- I found no peer-reviewed study that measures the fraction of ML-venue papers (NeurIPS/ICLR/ICML) using LLM judges. There is a gap between LangChain's industry number and academic keyword counts.
- The arXiv 2025/2026 counts could not be retrieved (API returned empty).
- Frontier-lab internal eval pipelines (OpenAI/Anthropic/Google model-graded evals) are documented mostly in blogs and model cards. I did not verify those this session, apart from the OpenAI benchmarks above.

## Q4. What reliability concerns motivate validating judges?

### Takeaway
Six kinds of problem are well documented at ACL, EMNLP, ICLR, and NeurIPS 2023–2025:
- Position, verbosity/length, and self-preference biases.
- Agreement with humans that varies by task, property, and expertise level.
- Failure on hard, correctness-heavy items (near-random on JudgeBench).
- Dependence on the judge being able to solve the item itself.
- Gameability, e.g. constant "null model" outputs reach top win rates.
- Theoretical limits on how far debiasing with a few gold labels can go.

The shared recommendation is to validate judges before use. That is the gap a label-free screening proxy targets.

### Cited Findings
**Agreement with humans varies by task**
- **Bavaresco, Bernardi, Bertolazzi, et al. (20 authors), "LLMs instead of Human Judges? A Large Scale Empirical Study across 20 NLP Evaluation Tasks," arXiv:2406.18403, ACL 2025 main** (per the arXiv comment). About 347 citations.
  - It builds JUDGE-BENCH (20 datasets) and evaluates 11 LLMs.
  - Models "are reliable evaluators on some tasks, but overall display substantial variability depending on the property being evaluated, the expertise level of the human judges, and whether the language is human or model-generated. We conclude that LLMs should be carefully validated against human judgments before being used as evaluators."
  - **[= existing key `Kocmi2024HumanVsLLM`.** The key name is misleading, but the bib authors are correct (Bavaresco et al.). Consider upgrading the entry to ACL 2025.]
  - [arXiv](https://arxiv.org/abs/2406.18403)
- **Thakur, Choudhary, Ramayapally, et al., "Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges," arXiv:2406.12624, GEM² Workshop @ ACL 2025.** Tests 13 judge models on 9 exam-taker models. "only the best (and largest) models achieve reasonable alignment with humans. However, they are still quite far behind inter-human agreement and their assigned scores may still differ with up to 5 points from human-assigned scores". It also finds "judges with high percent agreement can still assign vastly different scores." — [arXiv](https://arxiv.org/abs/2406.12624)
- **Szymanski, Ziems, Eicher-Miller, et al., "Limitations of the LLM-as-a-Judge Approach for Evaluating LLM Outputs in Expert Knowledge Tasks," arXiv:2410.20266.** Semantic Scholar lists IUI 2025 (year field 2024); treat the venue as per Semantic Scholar. — [arXiv](https://arxiv.org/abs/2410.20266)

**Position bias**
- **Wang, Li, Chen, et al., "Large Language Models are not Fair Evaluators," arXiv:2305.17926.** Semantic Scholar venue: ACL. The year field says 2023; ACL 2024 is from memory and UNVERIFIED. By changing only the order of responses, "Vicuna-13B could beat ChatGPT on 66 over 80 tested queries with ChatGPT as an evaluator." About 1,292 citations. — [arXiv](https://arxiv.org/abs/2305.17926)
- **Lin Shi, Chiyu Ma, Wenhua Liang, et al., "Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge," arXiv:2406.07791, AACL-IJCNLP 2025.** Uses 15 judges and "over 150,000 evaluation instances". "position bias is not due to random chance and varies significantly across judges and tasks," and is "strongly affected by the quality gap between solutions." — [arXiv](https://arxiv.org/abs/2406.07791)

**Verbosity / length bias**
- **Saito, Wachi, Wataoka, Akimoto, "Verbosity Bias in Preference Labeling by Large Language Models," arXiv:2310.10076.** "GPT-4 prefers longer answers more than humans." — [arXiv](https://arxiv.org/abs/2310.10076)
- LC-AlpacaEval (above) documents that AlpacaEval "is known to favor models that generate longer outputs." — [arXiv:2404.04475](https://arxiv.org/abs/2404.04475)

**Self-preference bias**
- **Panickssery, Bowman, Feng, "LLM Evaluators Recognize and Favor Their Own Generations," arXiv:2404.13076, NeurIPS 2024** (Semantic Scholar). Finds "a linear correlation between self-recognition capability and the strength of self-preference bias." — [arXiv](https://arxiv.org/abs/2404.13076)
- G-Eval (above) also flags a bias toward LLM-generated text. — [arXiv:2303.16634](https://arxiv.org/abs/2303.16634)

**Bias catalogues**
- **Ye, Wang, Huang, et al., "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge," arXiv:2410.02736, ICLR 2025** (Semantic Scholar). Identifies "12 key potential biases" with the CALM framework; "significant biases persist in certain specific tasks." — [arXiv](https://arxiv.org/abs/2410.02736)
- **Koo, Lee, Raheja, et al., "Benchmarking Cognitive Biases in Large Language Models as Evaluators," arXiv:2309.17012. The arXiv comment says "Publishsed [sic] at ACL 2024"; whether main or Findings is UNVERIFIED.** — [arXiv](https://arxiv.org/abs/2309.17012)
- **Guiming Hardy Chen, Shunian Chen, Ziche Liu, et al., "Humans or LLMs as the Judge? A Study on Judgement Biases," arXiv:2402.10669, EMNLP 2024.** Tests misinformation-oversight, gender, authority, and beauty biases; "even the cutting-edge judges possess considerable biases." — [arXiv](https://arxiv.org/abs/2402.10669)
- **Stureborg, Alikaniotis, Suhara, "Large Language Models are Inconsistent and Biased Evaluators," arXiv:2405.01724.** — [arXiv](https://arxiv.org/abs/2405.01724)

**Failure on hard, correctness-heavy items**
- **Tan, Zhuang, Montgomery, et al., "JudgeBench: A Benchmark for Evaluating LLM-based Judges," arXiv:2410.12784, ICLR 2025.** On knowledge, reasoning, math, and coding pairs, "many strong models (e.g., GPT-4o) performing just slightly better than random guessing." — [arXiv](https://arxiv.org/abs/2410.12784)
- **Zeng, Yu, Gao, et al., LLMBar, arXiv:2310.07641, ICLR 2024.** Uses 419 adversarial pairs; "even the highest-scoring ones have substantial room for improvement." — [arXiv](https://arxiv.org/abs/2310.07641)
- **Krumdick, Lovering, Reddy, et al., "No Free Labels: Limitations of LLM-as-a-Judge Without Human Grounding," arXiv:2503.05061.** Without a correct reference, "judges show high agreement with human experts only on questions the judges were able to correctly answer themselves." Expert-written references largely mitigate this. — [arXiv](https://arxiv.org/abs/2503.05061)
- **Zhou, Arnold, Ding, Weinberger, Hua, Sha, "Graders should cheat: privileged information enables expert-level automated evaluations," arXiv:2502.10961.** Semantic Scholar lists EMNLP 2025. It asks "how can we trust the grader LM, which is presumably weaker than the candidate LM, to assess problems that are beyond the frontier" and finds that privileged information (ground-truth solutions or guidelines) helps. **[= existing key `zhou2025graders`.]** — [arXiv](https://arxiv.org/abs/2502.10961)

**Gameability and robustness**
- **Xiaosen Zheng, Tianyu Pang, Chao Du, et al., "Cheating Automatic LLM Benchmarks: Null Models Achieve High Win Rates," arXiv:2410.07137, ICLR 2025 Oral.** A constant-output "null model" gets "an 86.5% LC win rate on AlpacaEval 2.0; an 83.0 score on Arena-Hard-Auto; and a 9.55 score on MT-Bench." — [arXiv](https://arxiv.org/abs/2410.07137)
- **Raina, Liusie, Gales, "Is LLM-as-a-Judge Robust? Investigating Universal Adversarial Attacks on Zero-shot LLM Assessment," arXiv:2402.14016, EMNLP 2024** (Semantic Scholar). — [arXiv](https://arxiv.org/abs/2402.14016)

**Theoretical limits and reliability metrics**
- **Dorner, Nastl, Hardt, "Limits to scalable evaluation at the frontier: LLM as Judge won't beat twice the data," arXiv:2410.13341, ICLR 2025.** "when the judge is no more accurate than the evaluated model, no debiasing method can decrease the required amount of ground truth labels by more than half." In practice the savings are "even more modest." — [arXiv](https://arxiv.org/abs/2410.13341)
- **Schroeder & Wood-Doughty, "Can You Trust LLM Judgments? Reliability of LLM-as-a-Judge," arXiv:2412.12509.** Uses McDonald's omega across samples and temperatures, and warns of "risks associated with over-reliance on single-shot evaluations." **[= existing key `Li2024TrustLLMJudgments`.** The key name is misleading, but the bib authors are correct.]** — [arXiv](https://arxiv.org/abs/2412.12509)
- **Norman, Rivera, Hughes, "Reliability without Validity: A Systematic, Large-Scale Evaluation of LLM-as-a-Judge Models Across Agreement, Consistency, and Bias," arXiv:2606.19544 (2026-06-17 preprint).**
  - Scale: 21 judges from 9 providers, about 541,000 judgments, on MT-Bench, JudgeBench, and RewardBench.
  - Finds "kappa deflation" of 33–41 points from exact match to Cohen's κ on MT-Bench.
  - Two production-deployed judges combine "high test–retest reliability (>0.95)" with "severe position bias (>0.10)".
  - [arXiv](https://arxiv.org/abs/2606.19544)
- **Robertson & Koyejo, "Let's Measure Information Step-by-Step: AI-Based Evaluation Beyond Vibes," arXiv:2508.05469, TMLR 2026** (per the arXiv comment). Covers label-free, manipulation-resistant evaluation: TVD-MI keeps AUC 0.70–0.77 under attack. **[= existing key `robertson2025stepbystep`.]** — [arXiv](https://arxiv.org/abs/2508.05469)
- **Bowman, Hyun, Perez, et al., "Measuring Progress on Scalable Oversight for Large Language Models," arXiv:2211.03540 (2022).** Gives the oversight motivation. **[= existing key `bowman2022scalable`.]** — [arXiv](https://arxiv.org/abs/2211.03540)

### Inferences
- The literature converges on "validate before use" (Bavaresco et al.), but validation is usually done by agreement with human labels. Dorner et al. and Krumdick et al. show that human labels remain the bottleneck exactly where judges matter most: at the frontier and on correctness-heavy items. This motivates cheap, label-free screening of judges, which is the paper's PTI angle.
- Norman et al. 2026 ("reliability without validity") and Thakur et al. ("high percent agreement can still assign vastly different scores") directly support separating reliability, agreement, and validity, as the paper's TW/TI/PTI distinction does.
- Suggested wording for the abstract's first sentence, general half: "LLM judges are now a standard evaluation instrument (Zheng et al., 2023; Gu et al., 2024; Li et al., 2025), yet their agreement with human judgment varies widely by task (Bavaresco et al., 2025)". This is fully supported. The "code, tests, and formal specifications" qualifier needs the other researchers' evidence.

### Gaps
- Venue for Stureborg et al. (2405.01724): Semantic Scholar says arXiv only; I did not find a peer-reviewed venue (UNVERIFIED).
- Venue for Krumdick et al. (2503.05061): Semantic Scholar says arXiv; a peer-reviewed venue is UNVERIFIED.
- Venue for Saito et al. (2310.10076): Semantic Scholar says arXiv; a peer-reviewed venue is UNVERIFIED.
- ChatEval's ICLR 2024 venue is UNVERIFIED this session.
- I did not verify exact per-task correlation tables inside Bavaresco et al. Only abstract-level claims are used above.

### Existing bib-key cross-check (paper_latex/ICLR_2027_submission/*.bib)
- `Zheng2023MTBench`: matches arXiv:2306.05685. Could upgrade to NeurIPS 2023 D&B.
- `Liu2023GEval`: matches arXiv:2303.16634. Semantic Scholar venue EMNLP 2023.
- `Chan2024ChatEval`: matches arXiv:2308.07201. **The first author is wrong in the bib: "Zheng Cheng Chan" should be "Chi-Min Chan".**
- `Kocmi2024HumanVsLLM`: this is Bavaresco et al., arXiv:2406.18403. Bib authors correct; the key name is misleading; could upgrade to ACL 2025.
- `Li2024TrustLLMJudgments`: this is Schroeder & Wood-Doughty, arXiv:2412.12509. Bib authors correct; the key name is misleading.
- `zhou2025graders`: matches arXiv:2502.10961. Semantic Scholar venue EMNLP 2025.
- `robertson2025stepbystep`: matches arXiv:2508.05469. TMLR 2026 per the arXiv comment.
- `bowman2022scalable`: matches arXiv:2211.03540.
