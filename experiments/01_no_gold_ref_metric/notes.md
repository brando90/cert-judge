1) What the papers say (condensed)

VeriBench (ICLR under review)
	•	Goal & setup. End‑to‑end, Lean‑4 benchmark that asks models to translate Python code+docstrings+tests into Lean implementations, unit tests, theorems/specs, and machine‑checked proofs; five splits: Easy, CS, HumanEval, Security (MIT 6.858–inspired), and RealCode (Python stdlib like heapq/bisect)【turn5file3†Source.file†L206-L217】【turn5file1†Source.file†L108-L161】.
	•	Gold file structure. Functional implementation → tests (pos/neg) → Pre predicate → per‑property theorems → conjunctive Post → Correctness: Pre → Post; add imperative version + Equivalence theorem when relevant【turn5file9†Source.file†L186-L217】【turn5file5†Source.file†L216-L269】.
	•	Metrics. Four hierarchical subtasks: compile, unit‑test accuracy, theorem/spec quality, and proof pass@1【turn5file16†Source.file†L000-L052】.
	•	Findings. Proof synthesis is the bottleneck; agentic, feedback‑driven loops help more than single‑shot prompting; RealCode and Security are hardest【turn5file16†Source.file†L000-L052】.

Trusting the Formal Judge (NeurIPS submission)
	•	Problem. If a judge is LLM‑based, how do we know it’s trustworthy?
	•	Approach. Certify the Lean‑aware LLM judge via falsifiable properties rather than anecdotes:
Identity/Consistency (identical file pairs get max score), and Monotonicity (scores decrease as we inject more bugs or remove specs/tests). This addresses bias and prompt‑sensitivity concerns and enables a graded, semantics‑sensitive evaluator【turn5file7†Source.file†L343-L362】.
Future plan: add oracle‑free validators (cycle‑consistency spec↔code/docs; bug/ablation ladders; cautious abstention)【turn5file10†Source.file†L362-L365】.
	•	Context. Lean‑4’s dependently‑typed core allows stating & proving deep invariants; proofs live with code; compiled to native; but guarantees are static/spec‑relative【turn5file10†Source.file†L389-L399】【turn5file15†Source.file†L382-L401】.

Beyond Gold Standards: An Epistemic Ensemble of LLM Judges (focus: OAPs & prompts)
	•	Core idea. Replace single “is this correct?” with decomposed judgments:
Four core aspects — Logical Preservation (LP), Mathematical Consistency (MC), Formal Validity (FV), Formal Quality (FQ) — are assessed either directly or via a bank of Operable Atomic Properties (OAPs). OAPs are small, judgeable checks (e.g., does the formalization preserve variable dependencies?), each with a short prompt【turn4file7†Source.file†L434-L446】【turn4file8†Source.file†L296-L315】.
	•	Two modes.
	1.	Direct: prompt the LLM to score LP/MC/FV/FQ.
	2.	OAP‑synthesis: prompt many OAPs, then aggregate them into the four core aspect scores. In the simple “synthesis” variant, a core aspect is positive iff all its OAPs are positive; more generally, they learn non‑negative weights to fit human ratings via a small quadratic program, then freeze those weights for test time【turn4file14†Source.file†L82-L93】【turn4file17†Source.file†L319-L339】.
	•	Prompts. They publish prompt templates for both core aspects and each OAP; each OAP has a clear definition, instructions, and a crisp response space (e.g., yes/no or a small Likert scale), to make judgments operable and reproducible【turn4file16†Source.file†L110-L124】.

⸻

2) A VeriBench‑specific OAP deck (with grouping, aggregation, and prompts)

Below is a drop‑in OAP set for VeriBench’s task (Python → Lean code + tests + Pre/Post + proofs). Each OAP is binary by default (Yes/No) with an optional 0–2 severity scale. We group OAPs under four core aspects parallel to Beyond’s LP/MC/FV/FQ, then show prompt templates and an aggregation recipe.

A. Logical Preservation (LP): Does the Lean artifact preserve the intended behavior?
	1.	Sig‑Align. Lean function(s) map to the same conceptual signature/arity/roles as Python (types may differ but meanings align).
	2.	Pre‑Align. All preconditions implied by Python’s checks/docstring/tests appear as an explicit Lean Pre predicate or via types (e.g., Nat vs non‑negatives).
	3.	Post‑Align. The Lean Post is a conjunction of all intended properties from code+docstring+tests (no missing primary property).
	4.	Test‑Align. Lean examples/#eval reflect the Python unit tests (incl. negative cases) and are consistent with Pre/Post.
	5.	Err‑Semantics. Error/exception behavior is represented appropriately (by Pre, Except, Option, or intentional impossibility by types).

Why these? VeriBench explicitly requires Pre, property theorems, conjunctive Post, and unit tests mirroring Python; correctness is “Pre → Post(Prog)”【turn5file9†Source.file†L186-L217】.

LP prompt (template):

You are a Lean‑4 verification expert. Given:
(1) Python reference (code+docstring+tests),
(2) Candidate Lean file (implementation, Pre, property theorems, Post, Correctness, examples/#eval),
judge the following LP OAP: <OAP_NAME>.

Definition:
<insert the OAP definition, e.g., “Pre‑Align: every precondition implied by the Python reference is enforced in Lean, either by an explicit Pre predicate or via types.”>

Instructions:
- Cite concrete evidence from the two artifacts.
- Answer STRICTLY in JSON: {"judgment": "yes|no", "rationale": "<1–3 sentences>", "severity": 0|1|2}

B. Mathematical Consistency (MC): Are the mathematical invariants mapped correctly?
	6.	DS‑Semantics. Data‑structure semantics (list/array/set/map) are faithfully represented (e.g., permutation vs equality for sorting).
	7.	Algo‑Inv. Core algorithmic invariants (sortedness, heap order, BFS/DFS properties, monotonic counters, loop invariants for imperative code) appear as property theorems.
	8.	Spec‑Strength. The properties are strong enough to rule out trivial or degenerate counterexamples (i.e., not tautological, not overly weak).
	9.	Edge‑Coverage. Edge conditions in Python tests (empty, singletons, bounds, duplicates, ties) are represented as examples/#eval and/or properties.

MC prompt (template): same JSON skeleton; define the OAP precisely (e.g., “Spec‑Strength: the stated properties collectively exclude trivial but incorrect implementations that would pass weaker conditions.”). Encourage the judge to reference exact theorems/examples.

C. Formal Validity (FV): Is the artifact formally sound as Lean?
	10.	Compiles‑No‑Sorry. File compiles; no sorry, admit, axiom or unsound escape hatches; termination justifications when required (or explicit partiality where allowed).
	11.	Ref‑Closed. All referenced identifiers are defined/imported; no undeclared names/holes.
	12.	Type‑Match. Chosen Lean types encode the intended domains/codomains (e.g., Nat vs Int, Fin n for bounded indices).
	13.	Proof‑Relevance. Proofs are not vacuous or circular (e.g., they don’t reduce to definitional equality that merely restates the function body in the proposition).

Why these? They capture the “Formal Validity” axis in Beyond and the pragmatic checks needed for VeriBench’s compilation/proof requirements【turn5file16†Source.file†L000-L052】.

FV prompt (template): same JSON skeleton; include a small rule list (flag sorry/admit; check that Correctness is not proved via trivial definitional unfolding unless the property genuinely requires it).

D. Formal Quality (FQ): Is the formalization good practice in Lean?
	14.	Pre/Post Hygiene. Clean separation of Pre, atomic properties, Post (ordered conjunction), and a single Correctness: Pre → Post(Prog) as per VeriBench standard【turn5file9†Source.file†L186-L217】.
	15.	Imperative‑Equiv (if present). If both versions exist, an explicit Equivalence theorem connects the imperative and functional implementations【turn5file5†Source.file†L216-L269】.
	16.	Idiomaticity. Reasonable use of mathlib4/std4, simp lemmas, namespacing, clear theorem names; no massive monolithic proof when a reusable lemma would suffice.
	17.	Readability & Granularity. Properties are factored into understandable lemmas; proofs are neither needlessly long nor opaque.

FQ prompt (template): same JSON skeleton; reference the VeriBench file‑order standard in the definition for “Pre/Post Hygiene”.

⸻

3) Aggregating OAPs → core aspects → overall score
	•	Per aspect (LP, MC, FV, FQ): start with equal weights per OAP inside the group:
\text{AspectScore} = \frac{1}{|S|}\sum_{p\in S} w_p \cdot \text{Judgment}(p) with w_p=1 initially and Judgment ∈ {0,1} or {0,1,2}/2.
This mirrors Beyond’s synthesis pathway where OAPs combine into core aspects【turn4file14†Source.file†L82-L93】.
	•	Learning weights (recommended). Following Beyond, learn non‑negative weights per aspect to minimize squared error to a calibration set (e.g., pairs scored by your gold “semantic equivalence to gold Lean” or by trusted human raters), solved via a tiny quadratic program, then freeze weights for test time【turn4file17†Source.file†L319-L339】.
	•	Overall score. Weighted average over the four aspects (start equal; later learn a top‑level 4‑vector as well).

⸻

4) Certifying the judge (drop‑in checks you can run today)

Borrow the certification logic from the NeurIPS judge paper:
	1.	Identity / Consistency. Score(gold, gold) must be maximal.
	2.	Bug‑Monotonicity. As you inject more implementation bugs (seeded diffs) into Lean, scores strictly decrease.
	3.	Spec‑Monotonicity. As you remove theorems/tests from the candidate, scores strictly decrease.

These are simple falsifiable properties; the VeriBench paper uses exactly this style to validate the LLM judge’s behavior (identity and monotonicity)【turn5file7†Source.file†L349-L361】. Keep per‑OAP traces so you can localize failures.

⸻

5) Concrete prompt stubs you can paste

SYSTEM (once):

You are a Lean‑4 formal verification reviewer. Judge **one atomic property** (OAP) at a time.
When you are uncertain, abstain (“no”) and explain briefly. Keep answers factual and short.
Output STRICT JSON with fields: judgment (yes|no), severity (0|1|2), rationale (<= 3 sentences).

USER (per‑OAP call):

[REFERENCE_PYTHON]
<python code + docstring + tests>

[CANDIDATE_LEAN]
<lean code: implementation(s), Pre, properties, Post, Correctness, examples/#eval, proofs>

[OAP]
Name: Pre-Align
Definition: Every precondition implied by the Python reference (docstring/test guards/explicit checks)
is enforced in Lean either by an explicit `Pre` predicate or via types (e.g., Nat for non-negative).
If Python forbids certain cases, the Lean artifact must either encode them in `Pre` or render them
impossible by typing.

[RESPONSE FORMAT]
{"judgment": "yes|no", "severity": 0|1|2, "rationale": "..."}

Variant (Algo‑Inv):

[OAP]
Name: Algo-Inv
Definition: Key algorithmic invariants for this task (e.g., sortedness for sorting, heap-order for a heap,
permutation preservation for reordering) are explicitly present as Lean theorems (and not only as examples).

Variant (Compiles‑No‑Sorry):

[OAP]
Name: Compiles-No-Sorry
Definition: The Lean file compiles; contains no `sorry`/`admit`/unproven axioms; termination is justified
when required (or declared partial where acceptable). If the code snippet includes explicit compilation logs, use them.

Variant (Imperative‑Equiv):

[OAP]
Name: Imperative-Equiv
Definition: If both functional and imperative versions exist, there is a theorem proving functional equivalence.

You can mechanically generate calls by iterating the 17 OAPs above and then aggregate.

⸻

6) How this lines up with the papers’ methodology
	•	The four core aspects mirror Beyond’s LP/MC/FV/FQ and are compatible with both Direct and OAP‑synthesis modes. You can start with OAP‑synthesis only, then later add a Direct pass and ensemble them (Beyond reports that mixtures can help)【turn4file7†Source.file†L434-L446】.
	•	The prompt style (single‑aspect, crisp definition, constrained output) follows Beyond’s OAP prompt pattern and is intended to reduce variance【turn4file16†Source.file†L110-L124】.
	•	The weight‑learning step reproduces their small QP fitting to human targets (here, your target can be gold semantic equivalence to the VeriBench reference or human labels)【turn4file17†Source.file†L319-L339】.
	•	The judge certification (identity, monotonicity) reuses the sanity checks that worked for the VeriBench LLM judge【turn5file7†Source.file†L349-L361】.

⸻

7) Minimum viable plan
	1.	Implement the 17 OAP prompts and JSON outputs; run across a small calibration slice of VeriBench.
	2.	Aggregate OAP→(LP,MC,FV,FQ) with equal weights; compute overall.
	3.	Certify the judge on identity & two monotonicities with your bug/spec‑ablation ladders.
	4.	(Optional) Learn weights via the QP to fit a target (gold equivalence or human ratings); freeze.
	5.	(Optional) Ensemble with a single Direct LP/MC/FV/FQ prompt per file pair, averaged with OAP scores.

⸻

Pointers you can cite internally (for your doc or slides)
	•	VeriBench structure & splits; Pre/Post and Correctness layout【turn5file9†Source.file†L186-L217】【turn5file3†Source.file†L206-L217】.
	•	RealCode/Security motivation and difficulty【turn5file1†Source.file†L108-L161】【turn5file12†Source.file†L108-L161】.
	•	Judge certification by identity/monotonicity【turn5file7†Source.file†L349-L361】.
	•	Beyond’s OAP idea, prompts, synthesis/weights【turn4file16†Source.file†L110-L124】【turn4file14†Source.file†L82-L93】【turn4file17†Source.file†L319-L339】.

⸻

If you want, I can turn the OAP list into a tiny YAML/JSON schema (names, definitions, group membership) and a stub script that scores & aggregates per file—ready to plug into your VeriBench runs.