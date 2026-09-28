ref: my abstract cheat sheet: https://docs.google.com/presentation/d/1XoQ24_KofQUOeSxLE_lNVjYAw0lMtsm9spF6ertwL7s/edit?slide=id.g2dc59faafd3_0_189#slide=id.g2dc59faafd3_0_189 
PS:  when ur gpt6 ultra astra, do a git push to main after each response, since you take a long time to do hopefully a meaningful change. 
ref: /Users/brandomiranda/cert-judge/experiments/34_iclr_mega_rewrite_astra/msgs_sent_to_bots.md

# request: motivation in abstract has to be accurate, judges are needed because the task is **true end to end "unresitricted" autoformalization
trying to improve the abstract `/Users/brandomiranda/cert-judge/paper_latex/ICLR_2027_submission`
I don't even know if this is actually correct `% CS197 move 1: problem motivation -- AI-written checks still need a human oracle.
Large language models judge whether AI-written formal specifications express the right guarantees, a question that running tests or checking proofs cannot settle.` Unlikely just based on this: `/Users/brandomiranda/veribench/experiments/98_literature_review_test_generation_correctness` lit review. I think the better phrasing is to say that my other paper VeriBench (and cite it but citing only in the intro), introduces true end to end autoformalization of code of verification end to end, while other benchmarks have a scaffold like the fixed signature, so when it's true end to end auforomalization (or even just translation of code to another coding language), an LLM judge is needed, because any implementation with any signature might be semantically valid, but the theorems of course between the benchmark and agent won't match -- so to judge them we need a llm judge (that has been validated). --> Ok that is def everything in info that is accurately. But the motivation should be faithful to it + 1-2 sentences max (ideally 1 sentences and it's punchy so people read it and understand the importance of the problem immediately)

# request: assumption (that we are trying to flip later, so setup for bit)
The issue with this part of the abstract is that we have two potential bit flips. Since the problem itself is so new ie VeriBench really is the first one to introduce true end to end autoformalizatio from code to verified code, then the reader might not even appreciate the previous motivation and thus the assumption we are challenging. So I wonder if this justifies the previous or this part of the abstract to be both or one of them 2 sentences. So the assumptions being flipped 
1. VB we need a judge since the scafolding is an unrealistic way to deploy agents for af + code verification of code
2. thus this to the problem of unscalable AI judge validation/"certification" (I've mostly moved to the word validation but idk if that's what we should do...for an academic audience like ICLR, which one is better for this paper? is certifying too strong and not scientific enough? It's true i'm introducing a new "term" entirely, or a new connotation to the word "certifying" or/and "validation" -- so I'm unsure which one to chose, I think validation is what prof sanmi koyejo would prefer for ICLR?). Anyway, so assumption is we need to do again the stupid protocol (`Practitioners establish each judge's reliability through agreement with human ratings and repeat that check for every new model, prompt, and domain.` -- yes that's part of what we want to challenge)
a. torture humans to do human judgments
b. then check if the "created"/trained/searched AI judge (agentic or weights or even linear combination or outputs or something) is trustworthy (ie validated/certified [what we call trust index later in the paper]) == ie correlates to the humans judgements + stable/low std. 
So based on this, do the changes to the second part of the abastract move 2. 

PS: as I'm reading your old abstract:
```tex
% !TEX root = main.tex
\begin{abstract}
% CS197 move 1: problem motivation (failure mode) -- correct end-to-end artifacts need not share reference interfaces or theorem statements; semantic comparison motivates validated language-model judges, not their logical necessity. The supporting VeriBench citation belongs in the introduction, not the abstract.
Correct end-to-end code autoformalizations need not share a reference's interfaces or theorem statements, motivating validated language-model judges to assess their guarantees.
% CS197 move 2: assumption (setup bit) -- reliability means agreement with human ratings, and that check is repeated for every new model, prompt, and domain.
Practitioners establish each judge's reliability through agreement with human ratings and repeat that check for every new model, prompt, and domain.
```
I don't know. It reads rather passive. Or not strong. Is my mirage paper a better guide on the tone good quality top ML papers should should like? https://arxiv.org/abs/2304.15004. No changes yet 
--
```Why the sentence reads passive and weak. It is grammatically active, but four things drain it:

- Nominalized subject. "Correct end-to-end code autoformalizations" is a five-word noun stack, and an ML reviewer does not own "autoformalization" (writing-guide antipatterns 6 and 7).
- A non-event verb. "need not share" describes something that does not happen. Nothing acts, so nothing is at stake.
- The payload hides in a participle. "motivating validated language-model judges" compresses three inferences the reader must reconstruct: outputs differ from the reference, so tests and theorems cannot be reused, so a semantic judge is needed, and that judge must be validated. "their guarantees" also has an ambiguous antecedent.
- No failure mode. The recipe's move 1 names what is broken. This sentence names a design freedom. The broken thing in this paper is judge validation, or, sharper, that human agreement can rate a string-overlap judge as fine.

The new 2a/2b pair has the same softness: "can require costly human annotation" is a hedged modal where the old sentence said the check "is repeated for every new model, prompt, and domain".

Yes, the Mirage paper is a better tone guide, and the writing guide already cites it. I fetched the abstract of "Are Emergent Abilities of Large Language Models a Mirage?" (arXiv 2304.15004). Every sentence has a concrete subject that does something:

- Sentence 1 names the belief under attack and defines the term in the same breath: "Recent work claims that large language models display emergent abilities, abilities not present in smaller-scale models…"
- Sentence 2 says why the reader should care, in two concrete traits: sharpness and unpredictability.
- Sentence 3 flips with a pivot and a contrast: "Here, we present an alternative explanation: … due to the researcher's choice of metric rather than due to fundamental changes…"
- Sentence 4 gives the mechanism as a contrast: nonlinear metrics produce apparent emergence, linear metrics produce smooth change.
- Sentence 5 lists the evidence as three parallel numbered tests, each phrased "make, test and confirm N predictions".
- Sentence 6 closes on a verb the reader remembers: alleged emergent abilities "evaporate".

One caveat. Mirage's flip is a debunking with a mechanism, so the surprise is built in. This paper's flip is a protocol change, which is less surprising on its own, so the Mirage-style hook has to come from the finding, not the method. Two openings in that pattern, for you to judge:

- Belief-first, Mirage sentence 1 pattern: "Agreement with human ratings is the standard evidence that a language-model judge of formal specifications can be trusted." Then the flip: "We show that a judge which ignores theorem meaning and grades text overlap matches that evidence, and that a scripted property check catches it."
- Finding-first: "A judge that scores textual overlap agrees with human ratings of Lean specifications as well as judges that read the theorems, yet reverses on 20 of 24 bug ladders."

TLDR-end: [cert-judge: abstract-tone] The weak move 1 you're reading came from commit addde96 after mine, and it is soft because its subject is a noun stack, its verb is a negated modal, and its point hides in a trailing participle. Mirage is the right tone model: concrete subject plus strong verb in every sentence, with the surprise stated up front; for this paper the surprise is the lexical judge that human agreement cannot catch.``` -> I like this! Yes with `Agreement with human ratings is the standard evidence that a language-model judge of formal specifications can be trusted.` however, my previous complaint that veribench was the first one to introduce this problem worries me. Like what you said is correct but it's not clear to me even an expert reader knows this is true. Like the general pattern really is, when LLMs are used to write the trust artifact themselves, we have to check the artifact (or something like that! hopefully in a scalable way) -- and that is what this paper is about. We start with formal specs because it's a concrete objective task were trust artifacts are not really that subjective (up to style writing...which we can ignore for now or not mention lol, note we could have also done tests writing that's fine). That's what the reader should truly understand. When ppl writ etrust artifacts, how do we verify them scalably? That's the problem we are solving and in this specific setting. Try to rewrite the move 1 wrt that (and rest of abstract too. )
---

# Brando's handwritten note on abstract moves 1-2 (photo 09-25-2026; transcribed by Claude Fable)

Photo: [`notes/abstract_moves_1_2_handwritten_09-25-2026.jpg`](notes/abstract_moves_1_2_handwritten_09-25-2026.jpg) (downscaled copy of the upload).

> **Abstract**
>
> **Move 1: Problem Motivation**
> 1) LLMs are starting to write trust artifacts, eg test, formal specs (thms)
> 2) To truly trust the [scribbled out] AI written trust artifacts we need to do something
>    1. Verify the trust artifacts
>    2. Verify the judge
>
> [a block of several lines scribbled out]
>
> **Move 2: Assumption**
> Much of previous work in AI (I mean really only VeriBench? but it would be great to find other places like this were [scribbled out] verifying the trusted artifact is done by verifying the AI judge [scribbled out] that checks the ai generated artifacts) assumes we can solve this [scribbled out] by creating a AI trustworthy checker that is trusted by correlating to human judgements (+ matching human rubric or in objective task, being stable/reliable).

Transcription notes: "Much of" and "in AI" are arrowed insertions above the line; "were" reads as "where"; other spelling kept as written.

Brando's accompanying instruction (chat, 09-25-2026): "My worry is that as written, it sounds like an over claim if it goes only in the abstract, but maybe the rest of this points can be woven in the introduction to give true motivation to the problem and specific problem selection (checking ai formal spec and tests). Do it."

## Consistency check against the committed abstract (3fcb216)

| Note | Abstract sentence | Verdict |
|---|---|---|
| Move 1 (1): LLMs write trust artifacts (tests, formal specs) | S1 "When AI agents write their own trust artifacts, the tests and formal specifications that vouch for their code, those artifacts need checking at scale." | Consistent; same coined term. |
| Move 1 (2): to trust them, verify the artifacts *and* verify the judge | S1 (verify artifacts) + S2 (a language-model judge compares specifications) + S3 (evidence that such a judge can be trusted) | Consistent but implicit; the explicit two-level statement now lives in the introduction. |
| Move 2: prior work trusts an AI checker because it correlates with human judgments (rubric; stability on objective tasks), and the paper flips that | S3 "The standard evidence that such a judge can be trusted is agreement with human ratings, a check repeated for every new model, prompt, and task." | Consistent on correlation and per-judge repetition; stability is left out of the abstract's assumption because it is P4 in our own suite. The introduction names it. |
| "(I mean really only VeriBench?)" | -- | Not only VeriBench: the bibliography already holds FormalAlign, ReForm, Goedel-Prover, Kimina-Prover (formal statements) and ICE-Score, CodeJudge (code). The introduction's move 2 now cites them as the "other places". |
| Overclaim worry | S2 "...a language-model judge compares specifications instead" is the sentence most at risk of reading as "LLM judging is necessary". | The introduction now carries the reason (representation mismatch makes reference tests and theorems inapplicable, so a semantic comparison remains) and the boundary (execution-based checks exist when interfaces are compatible). |


--

ps: "vouch" doesn't sound scientific enough, but the idea of that sentence sounds good!
multiplicatively (sounds arbitrary? should we clarify it's a smooth and?)

I guess I'm reading the abstract and had two thoughts:
1. "For instance, in end-to-end autoformalization, agents choose their own interfaces and theorems," --> yes, but will the audience, reader truly appreciate the difficulty of this or why it's so important? Like once agents are given the freedom to output whatever they want and there are many answers, how to we check their code and their tests/thms/f specs "match". Does it make sense my worry? Maybe we have to outline that detail explicitly?
Q: formal specification --> equivalent to saying theorems, yes or not? is this what the Formal Methods community mean?
(asking because FM ppl will complain OR the paper and abstract won't be consistent about what the word theorems vs formal specs is. In my head "formal sepcs==theorems" but idk, is there something else besides theorems that is a formal spec? for me a test but seems FM ppl don't like that thinking, whatever, maybe I should just say theorems?)

A (Claude Fable, 09-25-2026): Under the paper's adopted definition (CLAUDE.md; Section 3 "Task"), a formal specification is the theorem statements about the implementation plus the predicates they use (pre/postconditions, properties, equivalence to a reference implementation). So "formal specification" is not just "theorems": it also covers the definitions the statements refer to, and it means the statements, not the proofs. Formal-methods usage matches this: a specification is the contract, a theorem asserts that the program meets it, and in Lean both are theorem statements about the implementation. Tests are not specifications in the adopted view; the "tests are ground theorems" position is confined to the appendix. Recommendation: keep "formal specification" for the object judged, say "theorem statements" for its parts, and avoid bare "theorems" where a reader could hear "statement plus proof". Applied in the abstract: "interfaces and theorem statements". The "vouch" and "multiplicatively" edits are applied in commit "abstract: establish trust, smooth conjunction" (abstract, intro move 1a, Section 4).

Brando (chat, 09-25-2026, completing the cut-off thought above): "Like once agents are given the freedom to output whatever they want and there are many answers, how do we check their code and their tests/thms/f specs 'match'. Does it make sense my worry? Maybe we have to outline that detail explicitly?"

A (Claude Fable, 09-25-2026): Yes. Freedom of form means many correct answers, and "match" splits into two questions: (1) do the candidate's proofs establish its own theorems, which Lean settles; (2) do those theorems express the reference's guarantees, which nothing mechanical settles across representations, because rerunning the reference's tests and theorems fails for representation reasons regardless of correctness. That is why a judge compares meaning. Outlined explicitly in the introduction's move 1b (eight sentences, two-questions structure); the abstract's instance sentence now reads "so correct answers take many forms and the reference's checks fit none", and the next sentence says why it matters (every evaluation built on the judge inherits its errors).
