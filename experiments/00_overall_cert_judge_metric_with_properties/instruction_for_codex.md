```
\documentclass[numbers]{article}
\usepackage{subcaption}
% Extra space between figures/tables and their captions
\captionsetup[figure]{skip=12pt} % gap between figure and its caption
\captionsetup[table]{skip=12pt}  % gap between table and its caption

% if you need to pass options to natbib, use, e.g.:
%     \PassOptionsToPackage{numbers, compress}{natbib}
% before loading neurips_2025

% Use this for double-blind submission:
\usepackage[dblblindworkshop]{neurips_2025}

% Use this for the camera-ready version:
% \usepackage[dblblindworkshop,final]{neurips_2025}

\workshoptitle{MATH-AI}

% Use this for preprint:
% \usepackage[preprint]{neurips_2025}

% to avoid loading the natbib package, add option nonatbib:
%    \usepackage[nonatbib,dblblindworkshop]{neurips_2025}

% Encoding & typography
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc} % (only if using pdfLaTeX; not needed for XeLaTeX/LuaLaTeX)
\usepackage{microtype}

% Colors
\usepackage[dvipsnames]{xcolor}

% Math & symbols
\usepackage{amsmath,amssymb,amsfonts,amsthm,mathtools,bm,dsfont}
\usepackage{nicefrac,xfrac}

% Algorithms
\usepackage{algorithm}
\usepackage{algorithmic}

% Tables & figures
\usepackage{graphicx}
\usepackage{subcaption} % loads caption
\usepackage{wrapfig}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{makecell}
\usepackage{colortbl}
\usepackage{adjustbox}
\usepackage{array}
\usepackage{tabularx}
\usepackage{rotating}
\usepackage{arydshln}

% Code
\usepackage{listings}

% TikZ & icons
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning}
\usepackage{fontawesome5}

% Bibliography
% \usepackage[numbers]{natbib}
% Hyperlinks (load last)
\usepackage{hyperref}

% ---------- Moderately tight (slightly increased) spacing ----------
\usepackage{enumitem}
\setlist[itemize]{noitemsep, topsep=4pt}
\setlist[enumerate]{noitemsep, topsep=4pt}

\usepackage{caption}
\captionsetup{skip=7pt} % was 4pt

% Floats
\setlength{\textfloatsep}{10pt plus 3pt minus 3pt} % was 8pt
\setlength{\floatsep}{10pt plus 3pt minus 3pt}     % was 8pt
\setlength{\intextsep}{10pt plus 3pt minus 3pt}    % was 8pt

% Math displays
\setlength{\abovedisplayskip}{9pt plus 3pt minus 3pt}        % was 6pt
\setlength{\belowdisplayskip}{9pt plus 3pt minus 3pt}        % was 6pt
\setlength{\abovedisplayshortskip}{6pt plus 2pt minus 2pt}   % was 4pt
\setlength{\belowdisplayshortskip}{6pt plus 2pt minus 2pt}   % was 4pt

% Bibliography (natbib)
% \usepackage{natbib} % already loaded earlier
\setlength{\bibsep}{1pt plus 0.4ex} % was 0pt

% Listings
\lstset{
  aboveskip=6pt, belowskip=6pt,      % was 4pt
  basicstyle=\ttfamily\scriptsize,
  frame=single,                      % consider 'frame=none' if still long
  numbers=none
}

% Note. For the workshop paper template, both \title{} and \workshoptitle{} are required, with the former indicating the paper title shown in the title and the latter indicating the workshop title displayed in the footnote. 
% titles: https://chatgpt.com/c/68d73122-c130-8323-a16c-7a3e80cd339c 
\title{Trusting the Formal Judge: Certifying LLM Theorem Scorers for Code Verification in Lean~4}
% \title{Towards Reliable LLM Judging for Code-Verification Theorems in Lean~4}

\author{%
  David S.~Hippocampus\thanks{Use footnote for providing further information
    about the author (webpage, alternative address)---\emph{not} for acknowledging
    funding agencies.} \\
  Department of Computer Science\\
  Cranberry-Lemon University\\
  Pittsburgh, PA 15213 \\
  \texttt{hippo@cs.cranberry-lemon.edu} \\
}

\begin{document}

\maketitle

\begin{abstract}
Formal methods provide unparalleled rigor in software verification, and with the advent of AI systems, we are beginning to see their potential realized at scale; however, evaluating the quality of the theorems and specifications these systems generate remains a critical bottleneck.
Traditional benchmarks often provide a fixed theorem statement, but agentic systems must infer and synthesize these properties on their own, demanding a scalable and reliable evaluation method.
We present an LLM-based judge designed to score the quality of generated Lean~4 theorems based on correctness, completeness, and semantic alignment with a reference implementation.
More importantly, we introduce a novel methodology to certify the judge's trustworthiness by verifying its adherence to fundamental logical properties.
We demonstrate that our judge satisfies identity (identical inputs yield maximal scores) and monotonicity (scores decrease predictably as bugs are introduced or specifications are removed), with Pearson correlations up to 0.973.
By applying this validated judge to the \textsc{VeriBench}\citep{veribench_icml25}scalable oversight benchmark, we show that agentic approaches for formal code generation significantly outperform baseline prompting, with a top score of 0.615 vs.\ 0.470.
This work provides a blueprint for creating and validating reliable automated judges, enabling robust and scalable evaluation of next-generation theorem-proving agents.
\end{abstract}

\section{Introduction}
% https://chatgpt.com/c/68dc3b7a-8240-832c-9707-4187b4ec4005
% In modern proof assistants such as Lean~4, code can be verified through machine-checkable proofs. However, assessing the quality of the theorems themselves presents a deeper challenge. Determining what constitutes a good specification is inherently difficult, as it requires balancing correctness, expressiveness, and alignment with the intended semantics of the underlying program.
% The idea of this intro is to frame the problem in context: Writing proofs is hard, but easy to check. Writing theorems is hard, and hard to check. Even defining the problem is hard.

Agentic AI systems are emerging as a powerful tool for formal code verification, capable of not just proving theorems but also generating the code and the theorems themselves. This end-to-end synthesis presents a profound evaluation challenge. In traditional auto-formalization benchmarks, models are given a precise natural language statement to formalize. However, in a more realistic, agentic setting, the system must infer and propose relevant theorems from a source program and its docstring. This autonomy makes manual evaluation intractable and requires automated, scalable solutions \citep{zhou2025graders,khattab2024dspy,cheng2024trace}.

We propose a radical approach: use LLMs themselves as judges of specification quality. But can you really trust such a judge? An unreliable judge can produce misleading results, rewarding stylistic mimicry over semantic correctness and hindering genuine progress. Without a principled validation method, LLM-based evaluation remains ad hoc and its results questionable \citep{Kocmi2024HumanVsLLM,Li2024TrustLLMJudgments}.

In this paper, we present evidence indicating that it is possible to trust an LLM judge. We introduce an LLM judge for scoring the quality of synthesized theorems in Lean~4 and, crucially, present a methodology for validating its trustworthiness. We demonstrate that an LLM judge, when properly validated, can serve as a reliable proxy for human evaluation, enabling the scalable assessment of complex, agentic systems.

Our \textbf{contributions} are:
\begin{enumerate}
    \item \textbf{An LLM Judge for Theorem Quality:} We design an LLM judge that scores generated Lean~4 artifacts on a 0--10 scale based on correctness, completeness, and semantic alignment.
    \item \textbf{A Trustworthiness Validation Methodology:} We propose and execute a set of property checks to certify the judge's reliability and trustworthiness, verifying its adherence to logical properties like identity and monotonicity under controlled perturbations.
    \item \textbf{Empirical Demonstration of the Judge on \textsc{VeriBench}:} We apply our validated judge to evaluate multiple agentic frameworks, providing evidence that feedback-driven methods significantly outperform non-agentic baselines in theorem-synthesis quality.
\end{enumerate}

\section{Related Work}
\paragraph{LLM-as-a-Judge.}
LLMs are increasingly used as \emph{automated evaluators} across open-ended tasks, often reaching strong agreement with human ratings—e.g., GPT-4 judges achieving $>$80\% agreement with human preference labels in dialogue \citep{Zheng2023MTBench}. However, large-scale audits caution that reliability varies by task and setup, and stress the need for explicit validation before replacing human judgment \citep{Kocmi2024HumanVsLLM,Li2024TrustLLMJudgments}. Common biases include position and verbosity effects and sensitivity to prompt phrasing \citep{Zheng2023MTBench,Li2024TrustLLMJudgments}.

\paragraph{Improving judge reliability.}
To mitigate biases and instability, multi-agent debate frameworks such as \emph{ChatEval} emulate panel-style review to yield more robust consensus scores \citep{Chan2024ChatEval}. Structured prompting like \emph{G-Eval} elicits rubric-driven, stepwise reasoning prior to scoring, improving agreement with human criteria on NLG tasks \citep{Liu2023GEval}. Reliability can also be quantified via repeated scorings and internal consistency measures (e.g., Cronbach’s $\alpha$) to detect prompt/run sensitivity \citep{Li2024TrustLLMJudgments}.

\paragraph{Code and formal-spec evaluation.}
For programming, single-pass metrics like pass@k can be brittle or unavailable; early LLM-judge approaches such as \emph{ICE-Score} highlighted difficulty distinguishing partial vs.\ full correctness from a one-shot review \citep{Zhuo2024ICEScore}. \emph{CodeJudge} operationalizes a two-stage “analyze-then-summarize’’ procedure with a taxonomy of code faults, significantly improving correlation with functional ground truth \citep{TongZhang2024CodeJudge}. In formal verification/autoformalization, prior work typically provides fixed target theorems, reducing evaluation to proof success. In contrast, agentic systems must propose specifications, necessitating \emph{semantic} judges. We adopt a certification protocol (akin to metamorphic testing) and verify that our LLM judge obeys \emph{identity/consistency} and \emph{monotonicity} with respect to injected bugs and specification omissions, directly answering recent calls for validated, trustworthy LLM evaluators in safety-critical domains \citep{Kocmi2024HumanVsLLM,Li2024TrustLLMJudgments}.

\paragraph{Overview of \textsc{VeriBench}.}
Concretely, \textsc{VeriBench} consists of 857 theorems divided into five subsets: 
\begin{enumerate}
    \item \textbf{HumanEval} – 387 theorems derived from 56 standard programming puzzles from \citet{chen2021evaluating};
    \item \textbf{EasySet} – 278 theorems extracted from 41 introductory logic and programming tasks;
    \item \textbf{CSSet} – 68 theorems drawn from 10 classical data-structure and algorithm problems;
    \item \textbf{SecuritySet} – 112 theorems taken from 28 examples of buffer overflows, privilege escalation, and race-condition labs based on real code;
    \item \textbf{RealCodeSet} – 12 theorems extracted from 5 Python standard library programs, used to test model performance on production-grade code.
\end{enumerate}
This design covers a spectrum of tasks, from simple correctness theorems to more complex invariants, algorithmic properties, and real-world code verification. See the ICML AI4Math workshop poster for \textsc{VeriBench} for additional context \citep{veribench_icml25}.

\section{Methodology: A Certification Protocol for LLM Judges}

\paragraph{Why is an LLM judge needed for theorem-quality scoring?}
Evaluating AI-generated theorems/specifications requires a method to assess their quality, as proof assistants can verify a proof's correctness but not whether the agent proved the correct theorem.
This is challenging because proving the logical equivalence of two arbitrary theorem statements is generally undecidable, and an agent may generate theorems that are semantically valid but syntactically different or incomparable with the gold reference specification/theorem (e.g., by splitting a theorem into different parts).

Our goal is to certify the trustworthiness of an LLM judge for the task of formal specification/theorem generation.
This is akin to scoring the quality of a conjecture.
We operationalize this by requiring the judge to compare a candidate Lean~4 artifact (implementation, tests, theorems) against its gold-standard Lean~4 reference.
We provide the full set of Lean~4 artifacts because theorems might not make sense in isolation.
The judge returns a discrete score $s\in\{0,1,\dots,10\}$ for correctness, completeness, and semantic alignment, which we later normalize to $[0,1]$.
We use this score as a metric signal for evaluating the specifications generated by the agents.

To be considered trustworthy, the judge must satisfy the following falsifiable properties.
These are necessary conditions for trust: they certify that the judge reacts logically to structured perturbations.

\paragraph{P1 — Identity \& Consistency.}
The judge must be idempotent at the maximum score when comparing an artifact to itself.
For any reference $X$, it must hold that $s(X,X)=1$.
%, with variance across repeated runs approaching zero.

\paragraph{P2 — Monotonicity to Bugs.}
The judge’s score must decrease as semantic bugs are cumulatively introduced. Let $B_1$ and $B_2$ be sets of bugs such that $B_1 \subset B_2$. For candidates $C_{B_1}$ and $C_{B_2}$ containing precisely these bug sets, the expected scores must satisfy $\mathbb{E}[s(C_{B_1})] > \mathbb{E}[s(C_{B_2})]$.

\paragraph{P3 — Monotonicity to Missing Specs.}
The judge’s score must decrease as specification elements are removed. 
Let $S_1$ and $S_2$ be sets of specifications (theorems and tests) such that $S_2 \subset S_1$. 
For candidates $C_{S_1}$ and $C_{S_2}$ containing precisely these specification sets, the expected scores must satisfy $\mathbb{E}[s(C_{S_1})] > \mathbb{E}[s(C_{S_2})]$.

\paragraph{Certification Protocol.}
We implement three scripted perturbation families on the \emph{candidate} while holding the \emph{gold} fixed: 
(i) \emph{Identity} (P1), pairing each gold file with itself (and a semantically identical reflow) to test idempotence robustness; 
(ii) a \emph{Bug Ladder} (P2), applying $k\!\in\!\{0,\ldots,K\}$ semantics-changing transformations (e.g., broken identities, violated commutativity, incorrect base cases); and 
(iii) \emph{Specification Ablation} (P3), removing $m\!\in\!\{0,\ldots,M\}$ theorems or tests. 
We then verify monotonicity by computing rank correlations (Kendall’s $\tau$, Spearman’s $\rho$) between $(k,m)$ and judged scores, and by reporting pairwise ordering accuracy (AUC) that “worse’’ artifacts receive lower scores \citep{TongZhang2024CodeJudge,Zhuo2024ICEScore}.

\textbf{Establishing trust in the LLM judge.} To ensure trustworthiness of the LLM judge in evaluating agentic autoformalization, we systematically validate key properties the judge must satisfy in Figure~\ref{fig:judge_sanity_checks}: (1) scores decrease consistently as more theorems and tests are omitted, (2) scores similarly degrade when more implementation bugs are introduced, and (3) identical file pairs always yield maximal scores.
Empirical results confirm these properties strongly hold (Pearson correlations up to $-0.973$), thus validating that our Claude~3.5-based LLM judge provides a reliable and semantically meaningful measure for correctness, completeness, and alignment of autonomously inferred theorems across \textsc{VeriBench} subsets (Table~\ref{tab:theorem_quality_table_split}) \citep{Li2024TrustLLMJudgments,Kocmi2024HumanVsLLM}.

\begin{figure*}[t]
  \centering
  \begin{subfigure}[t]{0.315\textwidth}
    \centering
    \includegraphics[width=\linewidth]{../figures/identity_property.png}
    \caption{Identity (Reflexivity)}
    \label{fig:judge_identity}
  \end{subfigure}\hfill
  \begin{subfigure}[t]{0.315\textwidth}
    \centering
    \includegraphics[width=\linewidth]{figures/monotonicity_bugs.png}
    \caption{Monotonicity vs.\ Bugs}
    \label{fig:judge_mono_bugs}
  \end{subfigure}\hfill
  \begin{subfigure}[t]{0.315\textwidth}
    \centering
    \includegraphics[width=\linewidth]{figures/monotonicity_missing_specs.png}
    \caption{Monotonicity vs.\ Missing Specs}
    \label{fig:judge_mono_specs}
  \end{subfigure}
  \vspace{-2mm}
\caption{\textbf{LLM Judge Trustworthiness Sanity Checks.} 
The judge demonstrates reliability against our certification protocol. 
\textbf{(a) Identity:} When comparing a gold-standard file to itself, the judge consistently returns the maximum normalized score of 1.0 ($R^2=1.000$). 
\textbf{(b) Monotonicity vs.\ Bugs:} The judge's score shows a strong negative correlation with the number of injected bugs (Pearson $r = -0.973$, Spearman $\rho = -0.985$). 
\textbf{(c) Monotonicity vs.\ Missing Specs:} Similarly, the score decreases predictably as specifications are removed (Pearson $r = -0.979$, Spearman $\rho = -0.985$).}
  \label{fig:judge_sanity_checks}
  \vspace{-3mm}
\end{figure*}

\section{Results: Evaluating Agentic Theorem Generation with a Certified Judge}
Table~\ref{tab:theorem_quality_table_split} presents the normalized average scores across different splits of \textsc{VeriBench}: Easy Set (Easy), CS Set (CS), Real Python Code (Real), HumanEval Set (HE), and Security Set (Sec). 
As expected, the baseline prompting approach achieves the lowest overall normalized score (0.470), reflecting its limited capability in autonomously identifying comprehensive theorem properties.
It also gives us further confidence in our judge. 
Conversely, agentic methods leveraging iterative self-debugging and self-improvement demonstrate significant enhancements. 
Specifically, the DSPy ReAct agent, which incorporates feedback-driven self-debugging, achieves the highest overall average score of 0.615. 
The Trace++ agent, employing both self-debugging and self-improvement mechanisms, also shows notable improvement, attaining an average score of 0.588. 
These results underscore the effectiveness of agentic, feedback-driven approaches in enhancing theorem-generation quality compared to non-agentic baselines \citep{khattab2024dspy,cheng2024trace,chen2021evaluating}.

\begin{table}[H]
\renewcommand{\arraystretch}{1.30}
\centering
\begin{tabular}{@{}llccccc c@{}}
\toprule
& & \multicolumn{5}{c}{\textbf{Split}} & \\
\cmidrule(lr){3-7}
\textbf{Agent} & \textbf{Eval} & \textbf{Easy} & \textbf{CS} & \textbf{Real} & \textbf{HE} & \textbf{Sec} & \textbf{Avg} \\
\midrule
\multirow{1}{*}{\makecell[l]{Baseline Prompting}}
& Normalized & 0.580 & 0.690 & 0.472 & 0.410 & 0.347 & \makecell{\textbf{0.470}} \\
\addlinespace[2pt]
\hdashline[0.5pt/4pt]
\addlinespace[2pt]
\multirow{1}{*}{\makecell[l]{\textsc{DSPy ReAct}}}
& Normalized & 0.659 & 0.754 & 0.580 & 0.650 & 0.454 & \makecell{\textbf{0.615}} \\
\addlinespace[2pt]
\hdashline[0.5pt/4pt]
\addlinespace[2pt]
\multirow{1}{*}{\makecell[l]{\textsc{Trace+} (Self-Debug)}}
& Normalized & 0.342 & 0.680 & 0.592 & 0.573 & 0.411 & \makecell{\textbf{0.477}} \\
\addlinespace[2pt]
\hdashline[0.5pt/4pt]
\addlinespace[2pt]
\multirow{1}{*}{\makecell[l]{\textsc{Trace++} (Self-Improve)}}
& Normalized & 0.620 & 0.756 & 0.504 & 0.645 & 0.432 & \makecell{\textbf{0.588}} \\
\bottomrule
\end{tabular}
\caption{\textbf{Theorem Quality Scores.} Average normalized scores in \textsc{VeriBench} split: Easy Set (Easy), CS Set (CS), Real Python Code (Real), HumanEval Set (HE), Security Set (Sec). 
All rows use Claude~3.7 as the agent model and as the LLM judge. 
Trace+ denotes the trace self-debug agent and Trace++ the self-debug and self-improve agent. 
The DSPy ReAct agent only performs self-debug.
The LLM judge issues 5 scoring calls per file pair and returns an integer rubric score in $\{0,1,\dots,10\}$. 
Normalized scores are computed by dividing by the maximum score (10) and averaging across all examples. 
The Avg Norm Score shows the overall average over the entire benchmark.}
\label{tab:theorem_quality_table_split}
\end{table}

\section{Discussion, Limitations, and Future Work}
We study an LLM judge that \emph{compares each candidate artifact against its task’s gold reference} for Lean~4 code verification and a framework to increase confidence in it. 
The judge satisfies two falsifiable properties: (i) \textbf{identity}—gold vs.\ gold yields maximal, repeatable scores; and (ii) \textbf{monotonicity}—scores decrease predictably when we inject semantic bugs or ablate specification elements. 
In experiments, certified judging produces informative method rankings and tracks engineering signals (Pass@$k$, unit-test accuracy); Easy and HumanEval show the strongest agreement, while Security and RealCode remain hardest \citep{chen2021evaluating}.

\textbf{Limitations.} The judge is a \emph{proxy}: scores are prompt/rubric-sensitive and do not constitute kernel-level proof checking; they certify agreement with a rigorous yet necessarily incomplete gold specification since no complete mechanical checks of specification equivalence exist~\citep{rice1953}. 
Our certification relies on a finite perturbation suite, so untested failure modes may persist. Specifications that are exotic to this dataset may be correct but receive incorrect scores.
We also did \emph{not} collect human expert ratings, leaving the judge–human correlation unmeasured.
Future work will add human validity studies (correlations and reliability), strengthen semantic equivalence handling (candidate $\Rightarrow$ gold postcondition checks), expand robustness and adversarial tests, and introduce uncertainty reporting and standardized “judge cards’’ for reproducible, certified use \citep{zhou2025graders}.

% -------------------------------
% References (inline for portability)
% -------------------------------
\bibliographystyle{plainnat}
\bibliography{refs} % expects refs.bib in the same directory

% \begin{thebibliography}{99}
% \bibitem[Chan et al.(2024)]{Chan2024ChatEval}
% Zheng~Cheng Chan, et al.
% \newblock ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate.
% \newblock \emph{arXiv:2308.07201}, 2024.

% \bibitem[Chen et al.(2021)]{chen2021evaluating}
% Mark Chen, et al.
% \newblock Evaluating Large Language Models Trained on Code.
% \newblock \emph{arXiv:2107.03374}, 2021.

% \bibitem[Kocmi et al.(2024)]{Kocmi2024HumanVsLLM}
% Tom Kocmi, et al.
% \newblock LLMs instead of Human Judges? A Large Scale Empirical Study across 20 NLP Evaluation Tasks.
% \newblock \emph{arXiv:2406.18403}, 2024.

% \bibitem[Li et al.(2024)]{Li2024TrustLLMJudgments}
% Shulei Li, et al.
% \newblock Can You Trust LLM Judgments? Reliability of LLM-as-a-Judge.
% \newblock \emph{arXiv:2412.12509}, 2024.

% \bibitem[Liu et al.(2023)]{Liu2023GEval}
% Yang Liu, et al.
% \newblock G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment.
% \newblock \emph{arXiv:2303.16634}, 2023.

% \bibitem[Tong \& Zhang(2024)]{TongZhang2024CodeJudge}
% Yanfei Tong and Chiyuan Zhang.
% \newblock CodeJudge: Evaluating Code Generation with Large Language Models.
% \newblock \emph{arXiv:2410.02184}, 2024.

% \bibitem[Zheng et al.(2023)]{Zheng2023MTBench}
% Lianmin Zheng, et al.
% \newblock Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.
% \newblock \emph{arXiv:2306.05685}, 2023.

% \bibitem[Zhuo(2024)]{Zhuo2024ICEScore}
% Tianyi Zhuo.
% \newblock ICE-Score: LLM-as-a-Judge for Code without Ground Truth Outputs.
% \newblock \emph{arXiv preprint}, 2024.

% \bibitem[Zhou et al.(2025)]{zhou2025graders}
% Jin Peng Zhou, Sébastien M.~R.~Arnold, Nan Ding, Kilian Q.~Weinberger, Nan Hua, and Fei Sha.
% \newblock Graders should cheat: privileged information enables expert-level automated evaluations.
% \newblock \emph{arXiv:2502.10961}, 2025.

% \bibitem[Khattab et al.(2024)]{khattab2024dspy}
% Omar Khattab, Arnav Singhvi, Paridhi Maheshwari, Zhiyuan Zhang, Keshav Santhanam, Sri Vardhamanan, Saiful Haq, Ashutosh Sharma, Thomas T.~Joshi, Hanna Moazam, Heather Miller, Matei Zaharia, and Christopher Potts.
% \newblock DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines.
% \newblock In \emph{The Twelfth International Conference on Learning Representations (ICLR)}, 2024.

% \bibitem[Cheng et al.(2024)]{cheng2024trace}
% Ching-An Cheng, Allen Nie, and Adith Swaminathan.
% \newblock Trace is the next autodiff: Generative optimization with rich feedback, execution traces, and LLMs.
% \newblock \emph{arXiv:2406.16218}, 2024.

% \bibitem[VeriBench ICML AI4Math (2025)]{veribench_icml25}
% \newblock VeriBench: End-to-End Formal Verification Benchmark for AI Code Generation in Lean~4 (Poster, AI4Math @ ICML 2025).
% \newblock \url{https://icml.cc/virtual/2025/52376}

% \bibitem[Rice (1953)]{rice1953}
% H.~G.~Rice.
% \newblock Classes of Recursively Enumerable Sets and Their Decision Problems.
% \newblock \emph{Transactions of the American Mathematical Society}, \textbf{74}(2):358--366, 1953.
% \newblock \url{https://doi.org/10.2307/1990888}

% \end{thebibliography}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\appendix

% \section{Technical Appendices and Supplementary Material}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\section{Related Work (Cont.)}

\paragraph{Autoformalization.} Complementing this line of work, \citet{wang2024theoremLlama} present \textsc{TheoremLlama}, a framework aimed at enhancing LLM translation into Lean 4. Drawing on over 100K proof examples from the Mathlib4 library, TheoremLlama employs a novel natural-language-to-formal-language (NL-FL) bootstrapping strategy and iterative proof synthesis. This enables the reuse of verified examples as templates for future translations. The framework achieves 36.48\% and 33.61\% accuracy on the MiniF2F-Valid and MiniF2F-Test benchmarks, respectively—surpassing GPT-4 by more than ten percentage points on both.

\textbf{Techniques for Code Verification.}
\textsc{ImProver}~\citep{ahuja2024improver} introduces a Lean-aware Chain-of-States prompting loop that integrates retrieval, best-of-$n$ sampling, and iterative correction to rewrite formal proofs with improved properties. By optimizing for metrics such as brevity and readability, ImProver reduces the number of tactics by half, doubles proof readability, and boosts theorem prover acceptance rates by over 80\%.
In addition, \textsc{Clover}~\citep{sun2024clover} implements a closed-loop pipeline in which an LLM first generates code, docstrings, and formal annotations, then uses reconstruction-based prompting to enforce consistency across these outputs, and finally applies SMT-based verification to validate correctness. Evaluated on the CloverBench suite of Dafny programs, Clover accepts 87\% of correct solutions, rejects 100\% of flawed ones, and even uncovers bugs in human-written code—demonstrating the power of hybrid generation-verification pipelines.
In a complementary direction, \citet{zhou2025graders} improve general-purpose LLM-based graders by augmenting them with “privileged” information such as gold-standard solutions, grading rubrics, and detailed annotations. When necessary, the system provides targeted hints back to candidate models. This approach achieves grading performance on par with or exceeding that of specialized systems—and even expert humans—on difficult programming benchmarks.

\textbf{Agentic Frameworks and Tools for Code Verification.}
\textsc{Trace}~\citep{cheng2024trace} proposes \emph{generative optimization}, tuning entire computational workflows—including code, prompts, tool calls, and error signals—by treating execution traces as gradients in the OPTO framework. With a PyTorch-like API and the LLM-based optimizer OptoPrime, it supports diverse tasks such as prompt tuning, debugging, and robot control, rivaling specialized optimizers.
Building on modular composition, \textsc{DSPy}~\citep{khattab2024dspy} treats LLM calls as declarative modules in a computational graph. Users define concise input–output signatures, and DSPy’s compiler automatically bootstraps or fine-tunes pipelines using built-in “teleprompters.” This enables a few-line programs to outperform expert-crafted prompts in math, QA, and agent workflows.
Extending agentic capabilities to formal reasoning, \textsc{Pantograph}~\citep{aniva2025pantograph} offers a programmatic interface to Lean 4 with support for advanced proof search. It exposes internal proof states and tactics for integration with learning agents, replacing human-facing interfaces with API-level control.

\subsection{Related Work: Scalable Oversight}

\paragraph{Scalable Oversight with LLM Judges}
Researchers have proposed multi-agent oversight frameworks such as debate and consultancy, where weaker LLMs act as judges supervising stronger agents \citep{kenton2024oversight,Chan2024ChatEval}. 
Debate, in which two models argue opposing sides before a judge, consistently improves truth-tracking compared to single-pass QA. \citet{kenton2024oversight} demonstrate that debate reduces the likelihood of judges being misled in math and code tasks, highlighting it as a scalable oversight mechanism. 

\paragraph{Self-Improving Critics.}
In the absence of stronger supervisors, models can bootstrap judgment skill through self-critique. 
The Self-Evolving Critic (SCRIT) framework trains LLMs to generate critiques of flawed outputs, validate corrections, and iteratively refine their ability to spot errors. \citet{zheng2024scrit} report improvements of over 10\% on critique benchmarks, showing that self-critique fosters scalable, autonomous oversight.

\paragraph{Certifying Judges.}
Naïve LLM judges are often inconsistent, rewarding stylistic cues over correctness \citep{Kocmi2024HumanVsLLM,Li2024TrustLLMJudgments}. 
% To mitigate this, \citet{anonymous2025formaljudge} propose certifying judges with falsifiable properties. Their Lean-aware theorem judge satisfies both \emph{Identity} (identical inputs yield maximal scores) and \emph{Monotonicity} (scores decrease as bugs or omissions are introduced), with Pearson correlations up to 0.973. This validation enables the judge to serve as a reliable proxy for human evaluation of Lean theorems and specifications.

\paragraph{Validity-Centered Evaluation.}
Certifying judges requires not only behavioral properties but also principled validity evidence. \citet{salaudeen2025measurement} introduce a framework that distinguishes between measurement, claims, and evidence, grounded in psychometrics. They emphasize construct, content, and criterion validity, and systematically enumerate threats to validity. This framework provides a blueprint for reporting and interpreting judge certification results, complementing identity/monotonicity checks with broader validity cards.

\paragraph{Robust Evaluation without Ground Truth.}
Standard judge queries can be brittle in the absence of ground truth, particularly under adversarial manipulation \citep{Zhuo2024ICEScore,TongZhang2024CodeJudge}. \citet{robertson2025stepbystep} model the overseer as an agent and propose using information-theoretic, incentive-compatible queries instead of direct ratings. They introduce bounded $f$-divergence measures such as TVD-MI, which exhibit polynomial robustness to adversarial strategies, unlike unbounded KL-based criteria. This work highlights a pathway toward robust, certifiable judges when explicit ground truth is unavailable.

\paragraph{Formal Methods as Oversight.}
Proof assistants provide binary, kernel-level guarantees. \citet{zhou2024donttrustverify} autoformalize math solutions into Isabelle/HOL and show that filtering via proof checking outperforms majority voting by 12\% on GSM8K. \citet{liu2025safe} extend this approach with SAFE, which verifies every intermediate step in Lean 4 and introduces the FormalStep benchmark, reducing hallucinations and enabling fine-grained oversight.

\paragraph{Agentic Iterative Pipelines.}
\citet{ospanov2023apollo} integrate Lean feedback into recursive repair cycles, boosting general-purpose LLM proof success from 3--7\% to over 40\% on miniF2F, and achieving 75\% with fewer than 1000 samples. \citet{miranda2025veribench} extend this paradigm to program verification, showing that self-debugging agents quadruple success compared to one-shot prompting. 
Incorporating an LLM judge improved completeness on security tasks but required calibration to avoid regressions on simpler cases.

\paragraph{Benchmarks for Judge Reliability.}
Benchmarks such as VeriBench and FormalStep quantify judge reliability across compilation, proof success, and specification quality. 
\citet{miranda2025veribench} report normalized specification scores of 0.470 for one-shot prompting versus 0.615 for self-debugging agents. 
Outside formal mathematics, MT-Bench and G-Eval provide complementary judge-evaluation settings using pairwise preferences and rubric-guided scoring, underscoring the need for calibration and validity reporting \citep{Zheng2023MTBench,Liu2023GEval}. 
Together with validity frameworks and robust information-theoretic scoring, these benchmarks advance the agenda of certifying LLM judges for formal verification.

% https://chatgpt.com/c/68dc36c7-c4b0-8327-9dcd-694c10fa5d93?model=gpt-5-pro
\subsection{HCI for Solving Scalable Oversight}

\paragraph{From more evaluation to \emph{human-centered} oversight.}
HCI reframes scalable oversight as a \emph{calibration} problem: design interactions that let people verify, steer, and place \emph{appropriate} trust in LLM outputs rather than maximizing raw trust \citep{bach2022trusthci}. Interface choices (e.g., citations, explanations, confidence cues) can substantially shift user trust---sometimes in misleading ways---so the goal is to expose process and embed lightweight verification instead of presenting one-shot answers \citep{ding2025citations}. User studies in AI pair-programming similarly surface needs to communicate model performance, provide control over output style/constraints, and expose uncertainty to avoid over-reliance \citep{wang2024trustcode}.%
% :contentReference[oaicite:0]{index=0}

\paragraph{Hybrid human$\leftrightarrow$AI evaluation.}
HCI work operationalizes scalable evaluation by combining expert/lay judgments with automated judges. Humans annotate failures or verify slices of output; systems then train or condition LLM-based ``reference evaluators'' on those signals to scale up assessment while staying anchored to what users value (accuracy, safety, usefulness). This human-in-the-loop pattern complements LLM-as-judge approaches---whose reliability varies by task and setup \citep{Kocmi2024HumanVsLLM,Li2024TrustLLMJudgments}---and is especially relevant when pass@k or single-shot metrics are brittle.%
% :contentReference[oaicite:1]{index=1}

\paragraph{Interfaces that \emph{operationalize} oversight.}
HCI systems instantiate oversight as interaction loops that make correctness checkable \emph{during} generation: (i) \emph{test-driven code generation} (TiCoder) elicits yes/no judgments about candidate unit tests before showing code; a few interactions reduced cognitive effort and lifted pass@1 by $\sim$45.7\% on coding benchmarks \citep{naik2024ticoder}; (ii) \emph{explain$\rightarrow$correct loops} (IntelliExplain) pair each snippet with a natural-language rationale that users can critique, improving novice task success by $\sim$11--25\% \citep{yan2024intelliexplain}; (iii) \emph{pair debugging} (HypoCompass) has humans hypothesize faults while the LLM attempts fixes, yielding $\sim$12\% learning gains \citep{ma2024hypocompass}; (iv) \emph{multi-step pipelines} (PromptChainer) expose intermediate steps (e.g., tests $\rightarrow$ verification $\rightarrow$ proof attempt), enabling user intervention where failures arise \citep{wu2022promptchainer}; and (v) \emph{source-grounded verification} (SymGen) highlights claim-level spans backed by exact sources and leaves unsupported text unhighlighted, speeding verification by $\sim$20\% and raising user confidence \citep{shen2024symgen}. Collectively, these patterns shift trust from fluency to \emph{verifiable progress}.%
% :contentReference[oaicite:2]{index=2}

\paragraph{Applying HCI patterns to formal specs/theorems.}
Formal kernels (Lean/Isabelle) already deliver binary checks; HCI contributes the \emph{workflow glue} that helps users evaluate \emph{which} theorem/spec to prove and whether it is complete. Two actionable patterns: (1) \emph{counterfactual spec probes}---UI toggles that remove a postcondition or inject a known bug and display the impact on tests/judge score---help detect missing clauses or overfitting; and (2) \emph{stepwise proof oversight}---surfacing intermediate goals and marking unverified suggestions---keeps the human in control of proof search. In our setting, these patterns interface naturally with a graded, semantics-sensitive evaluator.%
% :contentReference[oaicite:3]{index=3}

% \paragraph{Complementarity with a \emph{certified} formal judge.}
% \citet{anonymous2025formaljudge} propose certifying an LLM theorem/spec judge via falsifiable properties---\emph{identity} and \emph{monotonicity}---and report strong negative correlations between injected error and score (e.g., $|r|\approx 0.973$) on \textsc{VeriBench} \citep{veribench_icml25}. HCI turns this certified signal into usable oversight by: (a) rendering per-clause rubrics and local confidence hints, (b) exposing the judge’s own sanity checks (identity pairs and monotone ladders) so users see \emph{why} scores move, and (c) attaching a concise \emph{judge card} (intended claim, evidence, threats) in the validity-centered sense of \citet{salaudeen2025measurement}. For settings with weak ground truth or adversaries, information-theoretic overseer queries provide robustness beyond rubric scores \citep{robertson2025stepbystep}.%
% % :contentReference[oaicite:4]{index=4}

% \paragraph{Design takeaways for scalable oversight.}
% \emph{Expose process}, not just outputs (\citealp{wu2022promptchainer}); \emph{facilitate incremental verification} (\citealp{naik2024ticoder,shen2024symgen}); \emph{empower corrective feedback} (\citealp{yan2024intelliexplain}); and \emph{communicate uncertainty honestly} (\citealp{wang2024trustcode,ding2025citations}). These HCI patterns consistently reduce cognitive load, improve objective accuracy, and---critically---align user trust with actual reliability across code/spec/theorem tasks.%
% % :contentReference[oaicite:5]{index=5}


\section{Discussion (Cont.)}
\textbf{Why Lean 4?} 
Lean 4 is a full fledge programming language and lets VeriBench contain full runnable code and machine-checked proofs in the same dependently-typed language. 
% \leni{The following sentence should be eliminated. Coq and Isabelle are not inherently less trustworthy}
% This eliminates the extraction gap that separates proof from execution in systems like Coq to OCaml or Isabelle to SML/Scala -- making Lean 4 more trustworthy. 
Ahead-of-time compilation with the Lake toolchain produces fast native binaries, while first-class \texttt{Task} primitives, async I/O, and a thread-pool scheduler enable genuine concurrent programs inside the prover. 
% TODO ([lean-lang.org][1], [lean-lang.org][2])  
Lean’s C-level foreign-function interface (FFI) lets those binaries call out to high-performance libraries when needed. 
% TODO ([docs.lean-lang.org][3], [proofassistants.stackexchange.com][4])  
On the proof side, Lean ships a powerful metaprogramming system written in Lean itself, giving researchers a programming interface to access its internals. This led to the creation of tools such as Pantograph and Aesop.
% ([lean-lang.org][5], [leanprover-community.github.io][6])  
Finally, the community-maintained \texttt{mathlib4} and \texttt{std4} libraries supply thousands of reusable theorems and data structures, and they are expanding quickly thanks to an active Zulip and GitHub ecosystem. Lean also has a work-in-progress program verification library, CSLib, which has recently seen rapid growth.
Lean 4 is backed by an unusually vibrant open-source community: hundreds of contributors refine \texttt{mathlib4} on GitHub each week, the public Zulip sees expert discussion around the clock, and even Fields-Medalist Terence Tao has chosen Lean to formalize portions of his current research—clear testimony to the ecosystem’s accessibility and intellectual depth.
% ([github.com][7], [leanprover-community.github.io][8])
Unlike the unit tests, fuzzers, and code sanitation pipelines common in industry—tools that sample inputs or rely on heuristics—Lean 4 supplies machine-checked proofs that a property holds for \emph{all} executions.  
Its dependent type system can encode deep invariants (e.g., length-indexed arrays, bounded integers), so programs that violate them fail to compile, eliminating whole classes of bugs such as buffer overflows or integer wrap-around. 
Code, specification, and proof reside in the same file and are compiled by Lake into the shipped native binary, preventing the drift that arises when verification artifacts live outside the build. 
% Tactic automation accelerates proof construction while keeping each step inspectable, and Lean’s FFI plus ahead-of-time compilation allow verified components to link with existing C/C++ libraries and run at production speed—even for concurrent tasks handled through built-in async primitives. 
In short, Lean turns informal “best-effort” checks into formal, end-to-end guarantees without sacrificing performance or interoperability.

\textbf{Lean 4’s limitations.}
Lean’s toolchain is still younger than Coq’s or Isabelle’s, making its standard libraries and automation smaller, and thus some formalizations demand extra groundwork. Lean’s runtime has not been stress-tested at the scale of mainstream systems languages, meaning large-scale or safety-critical deployments may require additional vetting. Lean tactics could contain bugs and fail to typecheck on different environments.
Acknowledging these gaps clarifies that VeriBench chooses Lean 4 for its unique unified programming-plus-proving model and modern automation hooks, not because it already matches the decades-old industrial maturity of older theorem provers. 
\noindent\textit{Static vs.\ runtime caveat:}
Lean’s guarantees are \emph{static} and specification‑relative: they certify the Lean program meets the stated properties, but they do not by themselves detect emergent runtime faults outside the model (e.g., I/O (Input/Output) failures, environment misconfiguration, FFI (Foreign Function Interface) unsoundness, resource exhaustion, or undefined behavior in linked C code). 
Such behaviors must either be modeled and proved, or mitigated with production safeguards (monitoring, sandboxing, input validation).

% [1]: https://lean-lang.org/doc/reference/latest/IO/Tasks-and-Threads/?utm_source=chatgpt.com "15.11. Tasks and Threads - Lean"
% [2]: https://lean-lang.org/doc/reference/4.19.0/Build-Tools-and-Distribution/Lake/?utm_source=chatgpt.com "Lake - Lean"
% [3]: https://docs.lean-lang.org/lean4/doc/dev/ffi.html?utm_source=chatgpt.com "Foreign Function Interface - Lean Documentation Overview"
% [4]: https://proofassistants.stackexchange.com/questions/4445/lean-4-foreign-function-interface-for-matrix-multiplication?utm_source=chatgpt.com "lean 4 foreign function interface for matrix multiplication?"
% [5]: https://lean-lang.org/doc/reference/latest/Notations-and-Macros/Macros/?utm_source=chatgpt.com "19.5. Macros - Lean"
% [6]: https://leanprover-community.github.io/lean4-metaprogramming-book/main/06_macros.html?utm_source=chatgpt.com "Macros - Metaprogramming in Lean 4"
% [7]: https://github.com/leanprover-community/mathlib4?utm_source=chatgpt.com "leanprover-community/mathlib4: The math library of Lean 4 - GitHub"
% [8]: https://leanprover-community.github.io/mathlib4_docs/index.html?utm_source=chatgpt.com "Mathlib Documentation - Lean community"

\textbf{Lean 4 versus Dafny.}  
Unlike Dafny, whose verifier translates each program into the Boogie intermediate language and then discharges first-order verification conditions with an SMT solver such as Z3, Lean 4 reasons natively in a dependently-typed calculus. 
% ([leino.science][1], [dafny.org][2])  
Because Lean 4’s types can mention run-time data and the very same source code is ahead-of-time compiled to a native binary via Lake, we can both state and prove value-indexed, higher-order properties (e.g., length-indexed vectorsand run the verified program itself—an end-to-end, fidelity that Dafny’s SMT-centred, Boogie-to-Z3 workflow cannot natively match.  
This gives Lean the expressive power to specify and prove higher-order, data-dependent properties—precisely the kind of semantic guarantees VeriBench seeks to test—while still yielding runnable binaries compiled by the same toolchain. 
Dafny’s SMT-centric workflow offers impressive push-button automation for imperative code but cannot natively encode the richer specifications (e.g., length-indexed vectors, algebraic invariants) that Lean handles directly. 
% ([lean-lang.org][3])

% [1]: https://leino.science/papers/krml221.pdf?utm_source=chatgpt.com "[PDF] Using Dafny, an Automatic Program Verifier - Rustan Leino"
% [2]: https://dafny.org/dafny/DafnyRef/DafnyRef.html?utm_source=chatgpt.com "Dafny Documentation"
% [3]: https://lean-lang.org/theorem_proving_in_lean4/dependent_type_theory.html?utm_source=chatgpt.com "Dependent Type Theory - Theorem Proving in Lean 4"

\textbf{Lean 4 versus TLA+.} 
TLA+ excels at high-level specification of concurrent and distributed protocols, with correctness checked by the TLC model-checker and the TLAPS proof system that dispatches first-order obligations to external provers. % ([lamport.azurewebsites.net][1], [proofs.tlapl.us][2], [lamport.azurewebsites.net][3])  
However, TLA+ specifications are not executable programs; a separate implementation step is required, and state-space explosion can limit model-checking scalability. 
VeriBench instead needs a prover where the specification, proof, and runnable code live in the same language. 
Lean 4’s dependently-typed core lets us capture fine-grained, data-dependent invariants and then compile the very same artifacts to fast native binaries—capabilities outside TLA+’s scope. 

\textbf{Lean 4 verus Verus.}
Verus is a verification framework for Rust programs using SMT solvers. A user state intermediate goals and an SMT backend fills in the intermediate steps. Compared to Verus, users have the option to use or not use SMT Solver-based tactics in Lean. This enables more fine-grained control and steering of the proof process. Verus also has a much larger kernel compared to Lean, and is more susceptible to soundness problem than Lean whose kernel is small.

\section{Future Work (cont.)}

% https://chatgpt.com/c/68dc38a5-93f4-8322-bf91-c2802fe73f6f
While \citep{robertson2025stepbystep} study demonstrates that total-variation-based mutual information (TVD-MI) provides robust, gaming-resistant evaluation without ground truth, many settings—such as VeriBench—do provide gold specifications in Lean 4. 
A promising direction is to develop hybrid protocols that combine TVD-MI’s black-box robustness with supervised ground-truth checks (compile success, unit tests, post-condition proofs, and equivalence theorems). 
By calibrating MI scores against known gold outcomes, we can create composite metrics that preserve gaming-resistance while offering calibrated probabilities of correctness where supervision exists. 
This opens the door to semi-supervised label propagation, active selection of items to prove, and cross-system experiments in domains with heterogeneous supervision.
Such an integration would extend Robertson’s information-theoretic framework into a practical, specification-aware oversight system that leverages the best of both unsupervised robustness and supervised precision.

\section{Why Judge Scores Are Specification-Relative}

It is tempting to interpret a perfect score from our LLM judge as a guarantee of absolute program correctness. However, this is fundamentally impossible due to established limits from computability theory. The obstacle is not a lack of ingenuity in our benchmark design or judge prompting, but an established negative result.

\paragraph{Rice’s Theorem.}
The core limitation stems from Rice’s theorem, which states that any non-trivial, semantic property of programs in a Turing-complete language is undecidable.

\begin{quote}
  \textbf{Rice's Theorem (Informal):} Let $\mathcal{S}$ be any property of a program's input-output behavior (e.g., "the program always terminates" or "the output is always sorted"). If $\mathcal{S}$ is non-trivial (meaning some programs have it and some don't), then no algorithm can exist that decides for \emph{every} program whether it satisfies $\mathcal{S}$.
\end{quote}

\paragraph{Impact on the Gold Standard and the Judge.}
Rice's theorem directly implies that the gold reference files used by our judge are necessarily incomplete. If a recursively enumerable gold standard could capture \emph{every} true semantic property of a program, one could use it to build a decision procedure that contradicts the theorem. Therefore, our gold standards, while rigorous, represent a curated but fundamentally finite set of important specifications.

This leads to a critical conclusion for our work: the judge's evaluation is **specification-relative**. A perfect score does not certify universal semantic correctness; rather, it certifies perfect **conformance to our specific gold standard**. Acknowledging this limitation is essential for correctly interpreting the judge's scores and understanding the scope of our evaluation.


\section{Judge Certification: Additional Plots}\label{app:judge-cert}
We report raw scatterplots used during certification of the LLM judge. These plots visualize the judge’s response to controlled perturbations: (P1) identity/reflexivity, (P2) cumulative bug injection, and (P3) removal of specification items (tests/theorems). Figures A.1–A.3 show that scores drop as artifacts worsen; the bug plot is noisier with an early prompt, which motivated the simplified rubric used in the main experiments.

\textit{Protocol variants.} The scatterplots below are “sanity-check” runs with the simplest prompts to stress visible monotonic behavior. In the bug study (Fig.~\ref{fig:app-bugs}) the earlier, theorem-equivalence prompt produced a noisier trend; this prompted a simplified, rubric-first prompt that we use for all reported results in the main paper, yielding the stronger correlations cited in Fig.~\ref{fig:judge_sanity_checks}. For missing-specs (Fig.~\ref{fig:app-missing-specs}), both Claude 3.5 and 3.7 show clear negative trends; minor non-monotonicity in 3.7 disappears with the finalized rubric.

\begin{figure*}[t]
  \centering
  \begin{subfigure}[t]{0.48\textwidth}
    \centering
    \includegraphics[width=\linewidth]{figures/3.5_specs_missing.png}
    \caption{Claude 3.5 Sonnet v1: strong monotonic decrease (\(y=-0.056x+0.771\), \(R^2=0.929\), Pearson \(r=-0.964\), Spearman \(\rho=-0.975\)).}
  \end{subfigure}\hfill
  \begin{subfigure}[t]{0.48\textwidth}
    \centering
    \includegraphics[width=\linewidth]{figures/3.7_specs_missing.png}
    \caption{Claude 3.7 Sonnet v1: clear negative trend with minor non-monotonicity (\(y=-0.047x+0.620\), \(R^2=0.785\), Pearson \(r=-0.886\), Spearman \(\rho=-0.872\)).}
  \end{subfigure}
  \caption{\textbf{(P3) Monotonicity w.r.t.\ missing specifications.}
  Candidate scores decrease as more theorems/tests are withheld. We retain both model variants to show robustness of the trend; 3.7’s small non-monotonicity motivated the simplified rubric used in the main results.}
  \label{fig:app-missing-specs}
\end{figure*}

\begin{figure}[t]
  \centering
  \includegraphics[width=0.85\linewidth]{figures/3.5_bugs.png}
  \caption{\textbf{(P2) Monotonicity w.r.t.\ cumulative bugs (Claude 3.5 Sonnet).}
  Scores drop as more semantic bugs are injected (Pearson \(r=-0.714\), Spearman \(\rho=-0.709\), \(R^2=0.509\)); the higher noise with the initial “theorem-equivalence” prompt led us to simplify the rubric used for the final judge in the main paper.}
  \label{fig:app-bugs}
\end{figure}
\end{document}
```

Awesome—let’s fuse your **certified LLM‑judge** (P1–P4) with Robertson & Koyejo’s **TVD‑MI** overseer into a single, principled scoring recipe you can drop into VeriBench.

---

## Hybrid Spec‑Judging Score (HSJ‑Score)

**Goal.** Produce (i) a **trust score** for the judge itself and (ii) a **final per‑submission quality score** that blends supervised and unsupervised evidence, with guardrails that automatically down‑weight the judge when it fails certification.

### Inputs

* **Candidate** artifact (c) (Lean 4 code + tests + theorems) and (when available) its **gold** reference.
* **LLM judge** (J) returning a raw rubric score (r\in{0,\dots,10}) for ((c,\text{gold})).
* **Info critic** (I) that yields **TVD‑MI** (via “same‑source?” CoT classification) between responses.
* (Optional GT) **Rungs** for calibration: (G\in{0,\dots,4}) for ({)compile, tests, Post, Equiv(}).

---

### Phase 0 — Certify the judge once per domain (trust score)

Compute four property scores in ([0,1]) from your perturbation suites; each is “1 = ideal”.

1. **P1 Identity/Consistency.**

   * Identity accuracy: fraction of identity pairs scoring at the maximum (or within (\epsilon)).
   * (P1 := \mathrm{median}\big(s(X,X)\big)) after normalization to ([0,1]).

2. **P2 Monotonicity to Bugs.**

   * Use **pairwise AUC** over bug ladders (fewer bugs should score higher).
   * (P2 := 2,( \mathrm{AUC}_{\text{bugs}} - 0.5 )).

3. **P3 Monotonicity to Missing Specs.**

   * Same AUC construction for ablation ladders (more omissions → lower score).
   * (P3 := 2,( \mathrm{AUC}_{\text{miss}} - 0.5 )).

4. **P4 Low Variance (stability/robustness).**

   * Repeat (J) (R) times on a fixed set; compute reliability, e.g., **ICC** or (1 - \frac{\sigma^2}{\sigma^2_{\max}}).
   * Map to ([0,1]): (P4 := \mathrm{clip}(1 - \sigma^2 / \tau^2,0,1)) with (\tau) a small, pre‑declared tolerance.

**Judge Trust Index (JTI).**
[
\boxed{;\mathrm{JTI} ;=; w_1 P1 + w_2 P2 + w_3 P3 + w_4 P4,\quad \sum w_i=1;}
]
Default (w_i=\tfrac14). (Add a **P5 tamper‑resistance** term if you run format/padding/case/pattern attacks; weight it by shaving (w_4).)

**Guardrails (thresholds).**

* **Green**: (\mathrm{JTI}\ge 0.85) → judge is trustworthy.
* **Yellow**: (0.70\le \mathrm{JTI}<0.85) → use cautiously (down‑weight).
* **Red**: (\mathrm{JTI}<0.70) → don’t rely on the judge for scoring (retain it only for qualitative evidence).

---

### Phase 1 — Calibrate signals to ground truth (when GT exists)

On items with rungs (G):

* **Calibrate the judge**: fit **isotonic regression** (f_J: r/10 \mapsto \mathbb{P}(G\ge k)) (or directly to (\mathbb{E}[G])).
  Let (\widehat{S}_{\text{judge}}(c) := f_J(r(c)/10)\in[0,1]).

* **Calibrate the info critic**: fit **isotonic regression** (f_I: \text{TVD-MI}(c) \mapsto \mathbb{P}(G\ge k)) (or (\mathbb{E}[G])).
  Let (\widehat{S}_{\text{mi}}(c) := f_I(\text{TVD-MI}(c))\in[0,1]).

> Both mappings convert raw, incomparable signals into the same semantic target (e.g., expected rung), enabling clean fusion and error bars (via bootstrap on the isotonic fit).

---

### Phase 2 — Compute per‑submission scores

1. **Supervised (judge) score with trust weighting**
   [
   S_{\text{sup}}(c) ;=; \mathrm{JTI}\cdot \widehat{S}_{\text{judge}}(c)
   ]

2. **Unsupervised (information‑theoretic) score**
   [
   S_{\text{unsup}}(c) ;=; \widehat{S}_{\text{mi}}(c)
   ]

3. **Adaptive fusion weight (\alpha)** (how much we trust supervised evidence)
   [
   \alpha ;=; \mathrm{clip}\Big( \underbrace{\lambda_{\text{GT}}}_{\text{GT coverage in this split}} \cdot \mathrm{JTI}^{\gamma},;0,1\Big)
   ]
   Typical: (\gamma\in[1,2]). If GT is sparse or JTI is low, (\alpha) shrinks automatically.

4. **Final Hybrid Score (HSJ‑Score)**
   [
   \boxed{;Q_{\text{final}}(c);=;(1-\alpha), S_{\text{unsup}}(c);+;\alpha, S_{\text{sup}}(c);}
   ]

---

### Reporting & interpretation

* **Trustworthiness of the judge** = **JTI** (single number with a 95% CI via bootstrap over the property suites).
* **Per‑submission quality** = (Q_{\text{final}}(c)\in[0,1]) with error bars from the calibration bootstraps.
* **Fail‑safe:** If (\mathrm{JTI}<0.70) or you detect inversion in attacks, set (\alpha:=0) (fall back to MI only).
* **Spec‑relative caveat:** All scores certify conformance to the **provided** gold spec (rungs), not universal semantic truth.

---

### Practical defaults (works well out of the box)

* (w_1=w_2=w_3=w_4=\tfrac14), (\gamma=1.5), (\lambda_{\text{GT}}=) fraction of items with GT in the current domain/split.
* Use **AUC‑based** P2/P3 (not correlations): it maps cleanly to ([0,1]) and is robust to scale.
* For uncertainty, bootstrap the isotonic fits (e.g., 1k resamples) and propagate to (Q_{\text{final}}).

---

### Why this is principled

* The **unsupervised leg** inherits **gaming‑resistance** (TVD‑MI, DPI‑based) and stays informative even without labels.
* The **supervised leg** is **spec‑aware** and grounded in your Lean 4 rungs, but only contributes proportionally to how **trustworthy** the judge is (JTI) and how much **GT** exists.
* The **fusion** is adaptive, safe (guardrails), and yields a single score you can rank by, alongside a domain‑level JTI you can cite as the judge’s reliability.

If you want, I can also format this as a neat **Algorithm block** for your NeurIPS workshop paper and add a one‑paragraph “Trust Card” description of JTI for the methods section.


do an excellent implementation of this in python please. I'd like to be able to score my formal judges. 


# Follow Up Questions

- are the bug insertion tests cumulitative? ie every bug for the previous 
file is present in the next one so that llm_judge(lean_{t}) <= llm_judge(lean_{t+1})
holds. 


# TVD-mi

Yes—and to cover the “other properties” from Robertson & Koyejo, here’s a clean, production-ready Python module that implements their TVD-MI critic math (Youden’s (J)), item-level AUC decomposition, the (\kappa)(\leftrightarrow)TVD relationships, a tamper-suite report (format/padding/case/pattern), and an optional “effective rank” utility for the inverted-U analysis. It’s self-contained and designed to sit alongside your HSJ code.

**What’s implemented (and where it maps in the paper):**

* **TVD-MI lower bound via categorical critic** (I_{\text{TVD}}\ge \text{TPR}+\text{TNR}-1=) **Youden’s (J)** (Sec. 3.4, Eqs. (3)–(5)).
* **Item-level AUC** decomposition and macro-average (Sec. 5.2, Table 3).
* **(\kappa)–TVD bounds** and **(J)–AUC** identities (Appendix F.1).
* **Tamper-suite** score inflation and discrimination degradation reporting (Sec. 5.3, Tables 4–5).
* **Effective rank** to analyze inverted-U vs. information structure (Appendix B.1, Fig. 2).
  These correspond directly to the paper’s definitions and empirical analyses. 

---

### Download the module
```python
# tvd_mi_tools.py
# ------------------------------------------------------------------
# Implementations inspired by Robertson & Koyejo (2025) "Let’s Measure
# Information Step-by-Step: LLM-Based Evaluation Beyond Vibes".
#
# This module provides:
# 1) TVD–MI lower-bound estimation via a categorical critic:
#       I_TVD >= TPR + TNR - 1  (Youden's J)  [Eq. (3)–(5)]
# 2) Item-level AUC utilities for decomposability tests.
# 3) κ (Cohen's kappa) ↔ TVD relationships (Appendix F.1).
# 4) Tamper-suite reporting for robustness experiments (format/padding/
#    case-flip/pattern), reporting score inflation and discrimination drops.
# 5) Optional "effective rank" computation to study the inverted‑U
#    phenomenon relating mechanism performance to information structure.
#
# References: see paper sections 3.4, 5.2, Tables 3–5, and Appendix F.1–F.2.
# CITATION HANDLE FOR PAPER (in-chat): fileciteturn2file0
#
# NOTE: This file is self-contained (numpy/scipy optional). It expects that
# the *categorical critic outputs* already exist (e.g., from an LLM calling
# convention). We map critic labels to accept/reject and compute TPR/TNR
# against pair ground-truth (same-source vs different-source).

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Literal, Mapping, Optional, Sequence, Tuple, Union
import math
import numpy as np


CriticLabel = Literal["Significant Gain", "Little Gain", "No Gain"]
# Map critic labels to acceptance of "same-source" hypothesis A (paper Sec. 3.4)
DEFAULT_ACCEPT_SET = {"Significant Gain"}


@dataclass
class TVDMIReport:
    tpr: float
    tnr: float
    youdens_j: float       # J = TPR + TNR - 1  (equals TVD lower bound)
    tvd_lower_bound: float # alias of J
    n_pos: int
    n_neg: int


def tvd_mi_from_critic(
    y_true_same_source: Sequence[bool],
    y_pred_labels: Sequence[CriticLabel],
    accept_set: Optional[Iterable[str]] = None,
) -> TVDMIReport:
    """
    Compute TVD–MI lower bound via type-based test r on pair labels.
    Implements Eq. (3)-(5): I_TVD >= TPR + TNR - 1 = Youden's J.
    See: Sec. 3.4 and Appendix F.1 of the paper. fileciteturn2file0

    Parameters
    ----------
    y_true_same_source : sequence of bool
        Ground truth per pair: True if the two responses are from the same source (P+),
        False if independently sourced (P-).
    y_pred_labels : sequence of {"Significant Gain","Little Gain","No Gain"}
        Critic outputs. We "accept" (same-source) when label ∈ accept_set.
    accept_set : optional iterable of labels to accept; default = {"Significant Gain"}.

    Returns
    -------
    TVDMIReport with TPR, TNR, J (Youden's J), and counts.
    """
    if accept_set is None:
        accept_set = DEFAULT_ACCEPT_SET

    y_true = np.asarray(y_true_same_source, dtype=bool)
    y_pred_accept = np.array([lbl in accept_set for lbl in y_pred_labels], dtype=bool)

    pos = y_true.sum()
    neg = (~y_true).sum()
    if pos == 0 or neg == 0:
        raise ValueError("y_true must contain both positive (same-source) and negative (independent) pairs.")

    # TPR: accept when truly same-source
    tpr = (y_pred_accept & y_true).sum() / pos
    # TNR: reject when truly independent
    tnr = ((~y_pred_accept) & (~y_true)).sum() / neg

    j = tpr + tnr - 1.0
    return TVDMIReport(tpr=float(tpr), tnr=float(tnr), youdens_j=float(j), tvd_lower_bound=float(j),
                       n_pos=int(pos), n_neg=int(neg))


# ------------------------------------------------------------------
# Item-level AUC utilities (Sec. 5.2). We compute AUC between classes
# of pairs per item, then macro-average across items. Critic scores
# can be any real-valued scalar (e.g., mapped from labels).
# ------------------------------------------------------------------

def _auc_binary(scores_pos: np.ndarray, scores_neg: np.ndarray) -> float:
    """
    Classic AUC = P(score_pos > score_neg) + 0.5*P(=). Stable and fast.
    """
    a = np.asarray(scores_pos, dtype=float).reshape(-1, 1)
    b = np.asarray(scores_neg, dtype=float).reshape(1, -1)
    diffs = a - b
    greater = (diffs > 0).sum()
    ties = (diffs == 0).sum()
    total = diffs.size
    if total == 0:
        return 0.5
    return (greater + 0.5 * ties) / total


def per_item_auc_macro(
    item_ids: Sequence[Union[str, int]],
    pair_scores: Sequence[float],
    pair_class: Sequence[int],
) -> Tuple[float, List[Tuple[Union[str, int], float]]]:
    """
    Compute per-item AUCs and macro-average across items.
    - pair_class: 1 for positive (e.g., Faithful–Faithful), 0 for negative (e.g., Faithful–Problematic).
    - pair_scores: critic scores per pair (e.g., mapped label score or calibrated TVD-MI evidence).
    Returns (macro_auc, per_item_list).

    Mirrors Sec. 5.2 item-level AUC analysis. fileciteturn2file0
    """
    item_ids = np.asarray(item_ids)
    scores = np.asarray(pair_scores, dtype=float)
    classes = np.asarray(pair_class, dtype=int)

    aucs: List[Tuple[Union[str, int], float]] = []
    for iid in np.unique(item_ids):
        mask = (item_ids == iid)
        s = scores[mask]
        c = classes[mask]
        if (c == 1).sum() == 0 or (c == 0).sum() == 0:
            continue
        auc = _auc_binary(s[c == 1], s[c == 0])
        aucs.append((iid, float(auc)))
    if not aucs:
        return 0.5, []
    macro = float(np.mean([a for _, a in aucs]))
    return macro, aucs


# ------------------------------------------------------------------
# Kappa ↔ TVD relationships (Appendix F.1).  κ ≤ 2*TVD / (1 - p_e).
# We also provide lower bounds and helper conversions to/from Youden’s J.
# ------------------------------------------------------------------

def kappa_upper_bound_from_tvd(tvd: float, p_e: float) -> float:
    """
    Given TVD(P, P_X P_Y) and chance agreement p_e, return κ upper bound:
        κ ≤ 2*TVD / (1 - p_e)
    See Appendix F.1. fileciteturn2file0
    """
    if not (0.0 <= tvd <= 1.0):
        raise ValueError("tvd must be in [0,1]")
    if not (0.0 <= p_e < 1.0):
        raise ValueError("p_e must be in [0,1)")
    return min(1.0, (2.0 * tvd) / (1.0 - p_e + 1e-12))


def tvd_lower_bound_from_kappa(kappa: float, p_e: float) -> float:
    """
    From Appendix F.1: TVD ≥ 0.5 * κ * (1 - p_e).
    """
    if not (-1.0 <= kappa <= 1.0):
        raise ValueError("kappa must be in [-1,1]")
    if not (0.0 <= p_e <= 1.0):
        raise ValueError("p_e must be in [0,1]")
    return max(0.0, 0.5 * kappa * (1.0 - p_e))


def j_from_auc(auc: float) -> float:
    """
    Youden’s J = 2*(AUC - 0.5) for symmetric ROC (Appendix F.1). fileciteturn2file0
    """
    return 2.0 * (auc - 0.5)


# ------------------------------------------------------------------
# Tamper-suite reporting (Sec. 5.3, Table 4–5). We compute score
# inflation and discrimination degradation for multiple transformations.
# ------------------------------------------------------------------

@dataclass
class TamperResult:
    score_delta_mean: float
    auc_before: float
    auc_after: float
    auc_delta: float


def tamper_suite_report(
    base_scores: Sequence[float],
    base_labels_pos1_neg0: Sequence[int],
    transformed: Mapping[str, Sequence[float]],
) -> Mapping[str, TamperResult]:
    """
    Given baseline pair scores and class labels (1=positive, 0=negative), and
    a dict of transformed scores {name: scores}, compute for each transform:
      - mean score delta
      - AUC before/after and delta.
    This mirrors the reporting style of Table 4–5 (Sec. 5.3). fileciteturn2file0
    """
    base_scores = np.asarray(base_scores, dtype=float)
    y = np.asarray(base_labels_pos1_neg0, dtype=int)
    auc_before = _auc_binary(base_scores[y == 1], base_scores[y == 0])

    out = {}
    for name, sc in transformed.items():
        sc = np.asarray(sc, dtype=float)
        if sc.shape != base_scores.shape:
            raise ValueError(f"Shape mismatch for transform '{name}'.")
        delta = float(np.mean(sc - base_scores))
        auc_after = _auc_binary(sc[y == 1], sc[y == 0])
        out[name] = TamperResult(score_delta_mean=delta, auc_before=float(auc_before),
                                 auc_after=float(auc_after), auc_delta=float(auc_after - auc_before))
    return out


# ------------------------------------------------------------------
# Optional: Effective rank (information structure) to study inverted‑U
# performance vs. structure (Appendix B.1, Fig. 2). This does not compute
# performance; it gives the structural descriptor (effective rank).
# ------------------------------------------------------------------

def effective_rank(matrix: np.ndarray, eps: float = 1e-12) -> float:
    """
    Effective rank of a matrix via entropy of singular values:
       r_eff = exp( H(p) ), where p_i = s_i / sum_j s_j (s_i singular values).
    r_eff ∈ [1, min(n_rows, n_cols)].
    Useful to study inverted‑U trend vs. mechanism performance. fileciteturn2file0
    """
    # Use singular values of |matrix|; works for non-square.
    s = np.linalg.svd(matrix, compute_uv=False)
    s = np.maximum(s, 0.0)
    s_sum = s.sum()
    if s_sum <= eps:
        return 1.0
    p = s / s_sum
    h = -(p * np.log(p + eps)).sum()
    return float(np.exp(h))


# -------------------- Tiny demo (synthetic) --------------------

if __name__ == "__main__":
    # Synthetic critic outputs for 100 pairs (50 same-source, 50 different).
    rng = np.random.default_rng(7)
    y_true = np.array([True]*50 + [False]*50)
    # Simulate a decent critic
    labels = []
    for t in y_true:
        if t:
            labels.append(rng.choice(["Significant Gain","Little Gain","No Gain"], p=[0.75,0.20,0.05]))
        else:
            labels.append(rng.choice(["Significant Gain","Little Gain","No Gain"], p=[0.10,0.25,0.65]))

    rep = tvd_mi_from_critic(y_true, labels)
    print("TVD-MI lower bound (Youden's J):", rep.tvd_lower_bound)

    # Simulate item-level AUC: suppose we have per-item pair scores
    item_ids = np.repeat(np.arange(10), 10)         # 10 items, 10 pairs each
    pair_scores = rng.normal(loc=0.6, scale=0.15, size=100)
    pair_class = np.array([1,0]*50)                 # toy alternating labels
    macro_auc, per_item = per_item_auc_macro(item_ids, pair_scores, pair_class)
    print("Macro AUC:", macro_auc)

    # Tamper example: add padding noise
    transformed = {
        "padding": pair_scores + rng.normal(0.02, 0.01, size=100),
        "caseflip": pair_scores - rng.normal(0.03, 0.01, size=100),
    }
    tamper = tamper_suite_report(pair_scores, pair_class, transformed)
    for k, v in tamper.items():
        print(k, v)
```

* **[Download `tvd_mi_tools.py`](sandbox:/mnt/data/tvd_mi_tools.py)**

Key functions:

* `tvd_mi_from_critic(y_true_same_source, y_pred_labels, accept_set=...) -> TVDMIReport`
  Maps critic labels (e.g., “Significant/Little/No Gain”) to accept/reject; returns TPR, TNR, and **Youden’s (J)** (=) TVD-MI lower bound.
* `per_item_auc_macro(item_ids, pair_scores, pair_class)`
  Computes **per-item AUCs** and macro-averages (Faithful–Faithful vs Faithful–Problematic).
* `kappa_upper_bound_from_tvd(tvd, p_e)`, `tvd_lower_bound_from_kappa(kappa, p_e)`, `j_from_auc(auc)`
  Implements Appendix F.1 relationships.
* `tamper_suite_report(base_scores, base_labels, transformed_dict)`
  Reports **mean score inflation** and **AUC deltas** for each transformation (format/padding/case/pattern).
* `effective_rank(matrix)`
  Entropy-of-singular-values measure used to study the inverted-U phenomenon.

The file includes a tiny synthetic demo in its `__main__` block.

---

### How you integrate this with HSJ

* Use your LLM **categorical critic** (same-source? CoT) to label each pair as `"Significant Gain"|"Little Gain"|"No Gain"`.
  Pass those labels and pair ground truth (same-source vs independent) to `tvd_mi_from_critic(...)` to get **(J)** (our **unsupervised signal** pre-calibration).
* For **item-level** decomposability checks, compute pair scores (e.g., numeric mapping of labels or calibrated TVD-MI evidence) and call `per_item_auc_macro(...)`.
* To reproduce the **tampering experiments**, pass baseline pair scores and class labels plus transformed scores (padding/format/case/pattern) to `tamper_suite_report(...)`.
* If you want to **study inverted-U**, compute `effective_rank` on a response matrix (e.g., critic logits or pairwise evidence) per domain/task and correlate against performance.

---

### Answering your follow-ups directly

* **Are the bug insertion tests cumulative?**
  Yes—that’s critical. Each rung (X^{(t+1)}) must include **all** bugs from (X^{(t)}), so the intended monotone inequality (s(X^{(t)},X)\ge s(X^{(t+1)},X)) is meaningful. Your ladder harness should enforce **compile-success** at every rung and (optionally) a **unit-test flip** gate to avoid trivial/ineffective edits.

* **Other properties from the paper—done**
  The module implements the **TVD-MI lower bound** (via Youden’s (J)), **item-level AUC** decomposition, **(\kappa) edges**, **tamper-suite** reporting, and **effective rank**—which together reproduce the principal analyses and robustness checks highlighted in the study. See in-code comments pointing to the relevant sections and equations. 

---

If you’d like, I can add a short convenience wrapper that consumes your **VB pairs** (with a `critic_fn` callback) and produces a **judge card**: (J) with CIs, per-item AUC histograms, tamper-suite deltas, and an optional effective-rank summary—ready to paste into your appendix.


