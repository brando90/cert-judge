# Abstract motivation: independent code formalizations

Created: 09-25-2026

## Adopted opening

> Correct end-to-end code autoformalizations need not share a reference's interfaces or theorem statements, motivating validated language-model judges to assess their guarantees.

Scope: change only the abstract's opening sentence and its explanatory source comment, then align the introduction's motivation and cite VeriBench there, not in the abstract. Preserve all other abstract claims and numbers.

## Evidence and claim boundaries

- VeriBench's current manuscript, `paper_latex/ICLR_2027_VeriBench/03_veribench.tex` in the sibling VeriBench repository, defines the Python-to-Lean task as joint generation of implementations, tests, formal statements, and proofs. Its schema does not require the reference's exact theorem decomposition.
- The same manuscript's `04_eval_metric.tex` records representation mismatches as a source of false negatives when applying reference tests and statements directly to generated code. Its coverage judge estimates coverage; it does not prove implications, and the deployed judge is not described as having passed its human-agreement gate.
- The sibling repository's `experiments/98_literature_review_test_generation_correctness/RESULTS_test_quality_taxonomy.md`, especially its joint-artifact comparison and semantic-alignment discussion, supports the distinction between shared-interface testing and evaluation across independently generated representations.
- Execution-based specification evaluation does exist: [nl2postcond, Section 2.1](https://arxiv.org/html/2310.01831) tests generated postconditions on reference and buggy executions. The revised opening therefore does not dismiss tests as incapable of supplying correctness evidence.
- Semantic comparison is the unmet evaluation step; language-model judging is one practical empirical strategy. Independently validated adapters, formal correspondence proofs, or human review remain alternatives. No claim is made that every other benchmark fixes signatures, every signature is acceptable, or VeriBench has universal novelty priority.
- The existing VeriBench bibliography entry is cited in third person in the introduction. No claim is added that the deployed VeriBench judge has already been validated successfully.

## Alternate openings considered

1. End-to-end code autoformalization can express the same guarantees through different interfaces and theorem statements, making semantic evaluation essential.
2. Correct autoformalizations need not resemble their references, so language-model judges must assess guarantees across different interfaces and theorem statements.

The adopted sentence names the concrete mismatch and the validation requirement together, without implying that a language-model judge is logically indispensable.

## Verification

- Opening: one sentence, 21 whitespace-separated words; no abstract citation. The remaining eight abstract sentences are unchanged.
- Source layout: `latex_sentence_lines.py --check` passed for both edited section files (exit 0).
- Scratch compilation: `latexmk -pdf -interaction=nonstopmode -halt-on-error` passed (exit 0), producing 16 pages.
- Final compilation log: zero TeX errors, undefined references/citations, and overfull boxes. Existing underfull-box notices remain.
- Rendered pages 1 and 2 inspected: opening, introduction, citation, and section transition are legible without clipping or overlap.
- `git diff --check` passed; exact source diff reviewed. No empirical results or judge settings changed.

OpenReview is not updated by this source edit; any earlier upload remains a separate submission artifact.

## Move 2 revision: judge-validation assumption (09-25-2026)

> Practitioners assess judge reliability through agreement with human ratings and consistency across repeated evaluations.
> Extending this evidence to new judges and tasks can require costly human annotation.

Move 1 remains one sentence: the independently generated formalizations motivate semantic judging. Move 2 now has two sentences: the first names the validation evidence, and the second exposes the annotation dependence that move 3 seeks to reduce. The abstract develops one central contribution for this paper, reusable behavioral screening, rather than presenting VeriBench's task design as a second contribution.

### Terminology and factual boundaries

- Prefer **validation** for empirical evidence about judge scores under a specified task, rubric, and evaluation distribution; **screening** describes the finite property checks. Unqualified **certification** could imply a guarantee that the current evidence does not establish. This is a manuscript-specific recommendation, not an assertion about a coauthor's personal preference. This edit does not rename existing section headings or frozen identifiers elsewhere.
- Agreement with human ratings and consistency across repetitions are distinct measurements, not a sufficient definition of trustworthiness. A judge can be consistently wrong. The property index remains a behavioral proxy rather than a certificate of semantic correctness.
- A changed judge configuration needs appropriate evaluation evidence, but not necessarily freshly collected annotations. [G-Eval, Sections 3.1--3.2](https://arxiv.org/html/2303.16634) compares different judge models against the same human-rated benchmarks. The wording therefore says annotation **can** be required when extending evidence; it does not claim that every model or prompt change requires re-annotation.
- [Schroeder and Wood-Doughty](https://arxiv.org/html/2412.12509) distinguish repeated-output consistency from correctness. Current manuscript Sections 4 and 6 likewise state that the screen does not establish transfer to unseen judges or distributions.
- No claim of VeriBench priority or universal inadequacy of supplied interfaces is added. No experiment, numerical result, or scientific setting changes.

Verification for this revision: move 2 has two sentences (14 and 13 words); all other abstract sentences are unchanged. Scratch compilation and sentence-layout checks passed (exit 0); the document has 16 pages, with zero TeX errors, undefined references/citations, or overfull boxes. Rendered pages 1 and 2 were inspected without clipping or overlap. Exact source diff and `git diff --check` passed. The earlier verification block records the preceding move-1 revision.

## Moves 1-2 rewrite: trust artifacts and the flipped validation protocol (09-25-2026, Claude Fable session)

Brando's request (`msgs_sent_to_bots.md`): the motivation must be accurate to the end-to-end setting, punchy, and readable by someone who has never seen VeriBench; the assumption must be the per-judge human-validation protocol that move 3 flips.

> When AI agents write their own trust artifacts, the tests and formal specifications that vouch for their code, those artifacts need checking at scale.
> In end-to-end autoformalization, agents choose their own interfaces and theorems, so reference tests do not transfer and a language-model judge compares specifications instead.
> The standard evidence that such a judge can be trusted is agreement with human ratings, a check repeated for every new model, prompt, and task.

- **Move 1 is two sentences on purpose.** The general pattern (agent-written trust artifacts must be checked) is what a reader should take away; the second sentence gives the concrete reason a language-model judge appears in this setting. Brando's earlier one-sentence opening hid three inferences in a participle.
- **Accuracy boundary kept from the previous revision.** With compatible interfaces, generated specifications can be checked by execution (nl2postcond); the claim is that end-to-end generation breaks that transfer (VeriBench `04_eval_metric.tex`: direct application of reference tests and theorems produced systematic false negatives). The abstract therefore says "reference tests do not transfer", not "tests cannot settle whether a check is right".
- **VeriBench** is still cited only in the introduction; the abstract describes the task without naming it.
- **Terminology decision:** *validation* for the human-agreement evidence, *screen* for the property checks, *certification* nowhere in prose. Certification connotes a guarantee that eight configurations per family on a validation set cannot support, and earlier reviews penalized overclaiming. A screen is exactly what a falsifiable property is: it can fail a judge without certifying one. The Section 4 heading "Property Certification Protocol" is the remaining exception and is flagged, not changed here.
- **Repeat stability** is P4 in our suite, so it is not written into the flipped assumption.
- **"Trust artifacts"** is new vocabulary; the introduction's move 1 should adopt it so the abstract has no stale echo.

Verification: sentence-layout check exit 0; ten sentences, each at most 25 words, 221 prose words; no CS197 jargon, `certif*`, `\cite`, or `\ref` in prose; OpenReview form abstract regenerated with zero generator warnings (see the commit).
