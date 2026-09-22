# 31_final_iclr_paper_writing — ledger

**TLDR:** "Calibration" is already removed from every paper tree (PR #44, commit `be4449a`, 2026-09-13,
wording-only). No full rewrite. The *concept* still leaks in ~4 places in the ICLR main text; fix is a
targeted pass on abstract / §1 / §4 opening / §5.3 / §6.1 / §7 (~25–30 sentences). Appendix untouched.

**DECIDED + APPLIED 2026-09-22 (Brando) — "quality" wording. Discussion closed.** In `main.tex`:
- **Term:** "reference-based specification quality" = how completely and correctly a candidate captures the gold
  reference. Used in the abstract and in the §3 goal sentence.
- **Gameability counter:** new §3 `\paragraph{Why a gold reference.}` cites `robertson2025stepbystep` in the main
  body. Without ground truth, direct ratings can be manipulated; our gold reference anchors each rating to
  "which of the reference's guarantees does the candidate state". Limitations adds: gaming is untested.
- **Presentation (spam / bloat / abstraction):** kept low-key, in Limitations only. Neither the judge prompts nor the
  development-panel protocol explicitly addressed it; the held-out pool rubric deducts only for superfluous theorem
  statements. Holistic panel ratings may reflect it implicitly (not measured); future protocols should make it
  explicit. It is NOT part of the definition.
- Other spec-sense "quality" hits normalized; C_f "quality term" → "monotonicity term". PDF rebuilt (28 pp).

**Background (2026-09-22), scroll down:**
- What each instrument actually scores (panel rubric = text lost; pool rubric = coverage + spam −2; LLM prompts =
  captured correctness properties; nothing covers implementation bloat). Also two main.tex precision bugs.
  → section *what each instrument actually scores*
- ICML 2026 reviews: nobody objected to "quality". They objected to the unclear annotation protocol and to missing
  vacuity coverage. → section *ICML 2026 reviews*
- "Calibration" explained → section *"calibration": what the word means*
- **Checklist** of pending edits → last section of this file

Target file: `paper_latex/ICLR_2027_submission/main.tex` (09-16 verbatim port of the accepted ICML DL4C paper;
main text = lines 104–719, `\appendix` at 791). Build: `latexmk -pdf main.tex`.

## Audit 2026-09-22 (calibration concept, main text only)

| # | Where (main.tex) | Problem | Fix |
|---|---|---|---|
| 1 | `:107` abstract, `:336` §5.3 header, `:596`, `:603` | "predicts" / "predictor" for an n=8 development-set association where the index form was chosen with the labels in view | "is associated with" / "tracks … on the development panel"; §5.3 header → "TI_var tracks judge-level human alignment on the development panel" |
| 2 | `:107` "weightings discovered on n=75", `:138` "fits the pooled development corpus", `:712` "we fit and select once" | Say TI_var is *fitted*. It is not: §4 `:221` and App. `app:index-definitions` define it with fixed equal 1/3 weights. Only the index *form* was selected on the panel. | "selected" / "the reported values are development-set associations of a fixed-weight index" |
| 3 | `:560–572` Table `tab:cross_pass_generalization` + `:572` "when TI_var is fit using one human pass" | The Fit/Test numbers (0.881/0.810, 0.857/0.786) come from `exp23_cross_pass_calibration.py`, a 200k-iter random search over **six** weights (`ident,mono,weak,stab,anti,subtle`); pass1-fit weights = (mono 0.4, stab 0.6). That is a *tuned-weight geometric variant*, not TI_var. | Caption + sentence: "a weight-tuned geometric variant (Appendix …)"; never call it TI_var |
| 4 | `:688` "the answer (ρ=0.881 across 8 judges)" | Quotes the exp23 tuned *in-sample* fit as TI_var's headline; abstract headline is 0.833/0.905/0.738 | Replace with the avg-label 0.833 (or the trio) and say "development-set association" |
| 5 | `:342` "within each regression" | No regression is run; figure is a Spearman scatter | "within each family panel" |
| 6 | `:142,:144,:156,:198,:596,:706` | "human-agreement assessment protocol/panel" is a mechanical drop-in for "calibration protocol/panel"; reads badly | Rewrite prose: "one-time human panel", "development panel", "property–human-agreement link" as fits |

Evidence for #3: `experiments/archive/04_veribench_validation/results_exp23_cross_pass_calibration/summary_fit_pass1.json`
(`fit_corr_spearman=0.88095`, `test_corr_spearman=0.80952`, weights mono 0.4 / stab 0.6) and `summary_fit_pass2.json`
(`0.85714` / `0.78571`, six non-zero weights).

## Decision (Trigger Rule 57 — decided, not asked)

TI_var is the **fixed equal-weight** index; the cross-pass table is a **separate tuned-weight variant** and will be
labeled as such. Headline stays 0.833 / 0.905 / 0.738 (avg / pass1 / pass2). Operation names per
`docs/terminology_cleanup_20260913.md`: development-set association (headline), index-form selection (what the panel
did), fitted score mapping (only exp23's tuned variant), threshold selection (§5.5). Nothing is called a prediction,
generalization, or calibration in the main text.

## Plan

1. Rewrite abstract + §1 (also the biggest page-cut opportunity; main text is 11 pp vs 9 limit — `OPEN_QUESTIONS.md` #1).
2. §4 opening paragraph + Table `tab:protocol_workflow` caption.
3. §5.3 header + "Takeaway" paragraph; cross-pass table caption/sentence.
4. §6.1 + `:688`; §7.
5. `latexmk -pdf`; grep main text for `predict|fit|regression|calibrat`; diff --stat; page count.
6. Leanstral fix (Brando's task list) is separate — not in this pass.
7. "Quality" pass + judge/human precision fixes — see the three 2026-09-22 sections at the end of this file
   ("quality" term, what each instrument scores, ICML-review evidence). Checklist there.

## Status

- 2026-09-22: audit done, experiment registered in `experiments/archive/layout.json` + `experiments/README.md`.
  Rewrite not started. `experiment_layout.py --check` currently fails only on Brando's pre-existing uncommitted
  moves of `18_icml_reviews` / `20` (not touched here).

## 2026-09-22 — abstract "fresh human ratings" claim

- Abstract: "least scalable way possible: fresh human ratings for every new judge, prompt, model, and threshold" → "Practitioners typically establish their reliability through agreement with human ratings and must repeat that check for every new judge, prompt, model, and domain."
- Dropped "threshold": picking a threshold reuses existing labels, so it does not need fresh ratings (and §5.5 picks one on the dev panel). Replaced with "domain" (Bavaresco et al. 2024: agreement varies across datasets and properties).
- Intro: cited the per-judge human-validation practice (G-Eval, MT-Bench) and why it is necessary (Bavaresco et al. 2024, bib key `Kocmi2024HumanVsLLM`). Deleted the duplicate uncited restatement in the ¶ starting "Property certification amortizes".
- refs.bib: `Li2024TrustLLMJudgments` author fixed to Schroeder & Wood-Doughty (checked against arXiv 2412.12509).
- Open: `% TODO(internal-review)` in the intro asks why a new judge on the same domain can't just reuse the n=75 labels. Also, Related Work says "Cronbach's α" for 2412.12509, but that paper uses McDonald's ω.

## 2026-09-22 — "specification" definition (decided by Brando)

- Adopted the formal-methods experts' definition: formal specification = theorem statements about the implementation (+ the Prop predicates they use). Unit tests are not specification. NL problem statement = "intent".
- Brando's competing view (a unit test is a ground theorem, e.g. `example : myAdd 1 2 = 3 := by native_decide`) is stated only in new appendix `app:spec-vs-tests` (App. E) and is not adopted.
- main.tex: definition added to §3 "Task"; §3 retitled "Judging Lean Formal-Specification Quality"; P3 text/§1/§5/App. figures now say "theorem statements and unit tests" (the ladder removes both); abstract no longer lists theorems apart from formal specs.
- Rule recorded in CLAUDE.md + AGENTS.md ("Specification" has one meaning here).

## 2026-09-22 — the word "quality" (background; DECIDED + APPLIED, see top)

Line numbers below are for `main.tex` at HEAD `a3c33a2` (after the one-sentence-per-line reflow).

**Decision (recommended):** keep "quality", but never bare. Always write **reference-based specification quality**
and define it in one clause.
- **Why not bare "quality":** it reads as a direct rating with no ground truth. That is the setting where
  Robertson & Koyejo argue direct ratings are gameable, and the paper already cites that (`:897-899`, `:1058`).
  Anchoring to the gold reference is the defense: the judge answers a question that has a real answer in principle
  ("does x establish g's guarantees?").
- **Why not "fidelity" alone:** it overclaims. The headline panel's rubric text is lost, and the lexical controls
  correlate *positively* with the panel labels (editdist +0.20, BAD_STRINGY +0.43;
  `archive/26_human_label_dataset_audit/vb_judgements_human_scores.md:93`). A cross-checking reviewer could say
  "your human criterion isn't fidelity."
- **Definition:** reference-based quality is **operationalized as fidelity**: coverage + correctness relative to g,
  i.e. not under-specified, not over-constrained/wrong-target, not vacuous (vacuous → 0). Vacuity and "spec restates
  the implementation" (`f x = <body of f>`, true by definition) are fidelity failures, not a separate axis.
- **Presentation (theorem spam, bloat, over-abstraction) was NOT assessed — do not put it in the definition**
  (corrected 2026-09-22; an earlier draft listed it as a "secondary" part of the construct).
  - Headline panel: rubric text lost, so we can't say it covered presentation.
  - Pool rubric: only *theorem spam*, folded into the single 0–5 score (−1/−2). The C/D spam answers were never
    recorded: all label TSVs are `gold_file|candidate_file|human_score_0_5`, so the spam effect can't be separated.
    The pool also isn't behind any headline number.
  - LLM judge prompts (P1/P4/P8): no presentation instruction.
  - Property probes (identity, bug, missing-spec, alpha): none target presentation.
  - Nothing anywhere covers implementation bloat or over-abstraction.
  → Presentation goes in **Limitations** as unassessed. The honest human-side sentence is "panel ratings are
  holistic, so presentation may have influenced them implicitly."

**Proposed text**
- Abstract `:108`: "…a property-certification protocol for LLM judges of *reference-based* Lean~4 specification
  quality (how completely and correctly a candidate specification captures a gold reference), where each judge is
  scored by…"
- §3 (`sec:problem-setup`), one new paragraph: quality is measured relative to g and operationalized as fidelity
  (judge prompts ask for captured correctness properties; `True` → 0). Judge prompts give no instruction on
  presentation, but judges see the full candidate file. Panel ratings are holistic 0–5. The pool rubric (not used
  for headline numbers) folds a theorem-spam deduction of up to 2 points into its score.
- Limitations: "Scores are anchored to a gold reference, but we do not evaluate candidates optimized against the
  judge, so resistance to gaming is untested." Plus: "We do not assess presentation (redundant or bloated theorem
  statements, implementation size, abstraction level); holistic human ratings may reflect it implicitly."

**Other "quality" hits (fix differently)**

| lines | fix |
|---|---|
| `:123` "theorem-quality evaluation", `:189` §3 title, `:698`/`:705` table caption (keep the `\label` id), `:710`, `:979` | "specification quality" (or "reference-based specification quality" on first use) |
| `:205`, `:360` "theorem/specification quality"; `:582` "Lean theorem and specification quality" | Also break the CLAUDE.md spec rule (theorems *are* the spec) → "specification quality" |
| `:670` "should leave theorem quality unchanged" | "should leave the specification's meaning unchanged" |
| `:240`, `:1456`, `:1472`, `:1477` "(monotonicity-)quality term" for C_f; `:613` "property quality" | Different meaning → "monotonicity term" / "property scores" |
| `:934` "specification quality" (describes external benchmarks) | optional light rephrase |

## 2026-09-22 — what each instrument actually scores (facts for §3 / §5 / appendix)

| instrument | used for | written instruction | bloat / style | what it sees |
|---|---|---|---|---|
| **Headline human panel**: 1 annotator (Ethan), 0–5, 2 strictness passes, 72/75 pairs analyzed | every TI_var↔human number | "old prompt": **text not found** in cert-judge or `~/veribench` | unknown; lexical controls correlate + with these labels | full gold + candidate files |
| **5-rater pool**: 343 labels, collected 2026-05-03→05-12 | held-out attempt, VeriBench appendix | `~/veribench/py_src/veribench_prompts/human_judgements_prompt.md`: "Judge **statement coverage only** (not proof style or proof quality)"; a stronger agent theorem that implies the gold one counts as covering it | **yes: theorem-spam deduction up to −2** (trivial/`True`, redundant restatements, irrelevant theorems, filler) | Python source + gold + agent file |
| **LLM judge panels** (P1_BASELINE / P4_CHECKLIST / P8_STRICT_B, App. `app:judge-prompts`) | property scores + judge–human correlations | "how well the GENERATED THEOREM captures the correctness properties of the REFERENCE IMPLEMENTATION"; `True` → 0.0 (`:1103-1109`) | not mentioned | **whole** candidate file; gold = its **last theorem block** only (`archive/04_veribench_validation/exp16_multi_judge_human_sets.py:476-477`) |

- Bottom line: "mainly fidelity" is the honest phrasing for the construct. Do NOT say "fidelity only".
- Correction to an earlier claim in chat: the "Do not grade … proof style" line is from
  `results_manual_agentic/p15_lenient_prompt.md` / `comparative_semantic_v1`. Those are side prompts, not the main panels.
- Naming: in the paper say **"panel rubric"** and **"pool rubric (coverage with a spam deduction)"**. Do not say
  "old/revised": the pool labels are finished, and "revised" sounds like a change after the fact. No re-annotation
  is proposed. All labels are frozen.
- Reviewer answer on vacuous or bloated output:
  - Vacuous statements: penalized by every written rubric.
  - Theorem bloat: penalized only by the pool rubric.
  - Implementation bloat / over-abstraction: no instruction covers it anywhere. Judges see it, so any effect is
    implicit and unmeasured.

**Precision bugs in main.tex (fix regardless of the wording decision)**
1. `:222` and `:702` say the judge returns an integer in {0,…,10}, but the appendix prompts (`:1103`) ask for a
   float 0.0–1.0. Reconcile per panel: which judge/prompt uses which scale?
2. The prompt label "REFERENCE IMPLEMENTATION" (`:1103`, `:1111`, `:1134`, `:1156`) is filled with the gold's last
   theorem block, not an implementation. Say so in the appendix.

**Open item for Brando:** ask Ethan for the **text** of the panel rubric (the two rubrics he already used). This
retrieves documentation; it does not ask him to relabel. If it's gone, describe the panel only as "holistic 0–5 ratings
by one annotator under two rubric strictness levels" and claim nothing about what it penalized.

## 2026-09-22 — ICML 2026 reviews: evidence for the wording decision (`experiments/18_icml_reviews/pre_prompt.md`)

- **Nobody objected to "quality".** The AC meta-review (`:47`) and reviewer uMVy's summary (`:59`) use the word
  themselves. `grep -i 'gam|manipul|adversar'` over the reviews → 0 hits.
- **What they attacked** (the wording pass should close these):
  - "unclear annotation protocol" (AC, uMVy, c7ev: "what pass1 and pass2 represent");
  - c7ev: the property suite "cannot cover … vacuity, subtle theorem weakening, over-constraint", "How often do
    high-TI judges still miss vacuous, overly weak, or over-constrained theorem specifications?", and "separate judge
    failures caused by natural-language rubric ambiguity from … Lean-code semantic misunderstanding";
  - DeJF: judges "affected by surface-level wording" (the alpha-renaming result).
- **Highest-value follow-up:** a vacuity/weakening probe (replace theorem statements with `True`; drop a postcondition
  conjunct), plus optionally a bloat probe (add redundant implied theorems; a fidelity score should not change).
  c7ev asked for exactly this, and it turns "quality includes non-vacuity" into a tested property. Building the probes
  costs nothing. **Scoring them needs paid judge inference → exact cost quote + Brando's approval first.**
- Optional: simulated AI-reviewer comparison of three abstract variants (bare "quality" / "fidelity" / anchored
  "reference-based quality") via `clauded -p` + `codex exec`. Not run: reviewer passes are opt-in only.

## 2026-09-22 — "calibration": what the word means (Brando's question, answered in chat)

- **Calibration** = P(Y=1 | p̂(X)=p) = p for every p: of all inputs scored p, a fraction p are positive. It
  conditions on the score's level set, not on each x. p̂(x)=p*(x) for every x is strictly stronger: it implies
  calibration, not the reverse.
- **Why the term exists:** accuracy and AUC only see ranking/argmax, so any monotone rescaling leaves them unchanged.
  Scoring 0.51 for every positive and 0.49 for every negative gives AUC=1 and is badly miscalibrated. Predicting the
  base rate for everyone is perfectly calibrated and useless. Brier = reliability (calibration) − resolution +
  uncertainty (Murphy), so one loss number mixes the two parts. Guo et al. 2017: modern networks got more accurate
  and more overconfident at once; temperature scaling fixes calibration without changing accuracy.
- **For this paper:** judge scores are not probabilities of any event, so the statistical sense rarely applies. Use
  the operation names (CLAUDE.md): development-set association / fitted score mapping / threshold selection /
  score–outcome reliability. `main.tex` already has 0 "calibrat" hits.
- **Related trap:** in psychometrics "reliability" = consistency (test–retest, α); "measures what it claims" =
  validity. The abstract uses "reliability" in the validity sense.

### Checklist — quality/precision pass (pending Brando's OK on the wording)
- [x] Abstract `:108` → anchored "reference-based specification quality (how completely and correctly …)"
- [x] §3: goal sentence defines reference-based specification quality; `Why a gold reference` paragraph with the
      Robertson & Koyejo citation. Presentation is in Limitations only, not in the definition.
- [x] Replace the spec-sense "quality" hits per the table; C_f "quality term" → "monotonicity term" (5 sites incl. `:613`)
- [ ] Fix the 0–10 vs 0.0–1.0 scale inconsistency (`:222`, `:702` vs `:1103`)
- [ ] (DEFERRED: appendix out of scope for now) Appendix: note that "REFERENCE IMPLEMENTATION" = the gold's last theorem block
- [x] Limitations: gaming untested; presentation not explicit in judge prompts or panel protocol
- [ ] Brando → Ethan: panel rubric text
- [ ] (optional, paid) vacuity/weakening probe — quote first
- [x] `latexmk -pdf` (28 pp, no undefined refs); `latex_sentence_lines.py --check` passes

## 2026-09-22 — did the HUMANS assess presentation? (zero-spend check on existing labels)

Brando: "More than the judge judging presentation, what matters is if the humans did — that's the hard part to
redo. Judges I could re-run."

Script: `presentation_probe.py` (this folder). Output: `presentation_probe_output.txt`. No API calls, no new labels.
Presentation proxies come from the candidate `.lean` file (comments stripped): chars, non-empty lines, # theorem/lemma
declarations, # `def`s, # `: True :=` theorems. "Within-problem" = ranks demeaned across the 3 candidates of the same
problem (same gold). "|judge" = additionally residualized on gpt-5.3-codex P4_CHECKLIST, a fidelity-targeted score.

| view (n=72, 24 problems) | chars: within-prob / within\|judge | # theorems: within\|judge |
|---|---|---|
| panel avg | **+0.38 / +0.38 (p<0.01)** | −0.04 (p=0.71) |
| panel pass1 | +0.17 / +0.18 (p=0.13) | +0.05 |
| panel pass2 | +0.29 / +0.28 (p=0.02) | −0.02 |
| pool mean | +0.24 / +0.25 (p=0.03) | +0.00 |

**Findings (exploratory: n=72, 5 proxies × 4 views, crude proxies):**
1. **No sign that humans penalized size.** Within a problem, the *longer* candidate gets the *higher* human score,
   even after controlling for the judge's fidelity score. Theorem count is unrelated to scores.
2. **Spam and vacuity were never exercised.** Panel candidates have 1–7 theorem/lemma declarations (median 1) and
   **0/72** contain a `: True :=` theorem. Whatever the rubric said, this panel has no theorem spam and no trivially
   true specs to penalize. The human data cannot show that raters penalize either.
3. **Consequence:** don't claim humans assessed presentation or vacuity. Scope the claim: "on a panel whose candidates
   contain few theorem statements (median 1, max 7) and no trivially true ones".

**No human relabel is needed.** Judge behavior on vacuity/bloat can be tested with **property probes whose direction
is known by construction**, which needs no human labels. That is the paper's own method:
- vacuity probe: replace theorem statements with `True` (or add a `False` hypothesis) → score must drop toward 0;
- bloat probe: add redundant implied theorems → fidelity score must stay the same (like alpha-renaming).
Building the probes costs nothing. Scoring = paid judge inference → exact quote + Brando's OK first.
The only human-side action is retrieval: ask Ethan for the panel rubric text and whether he penalized size/spam.
Record his answer as an annotator report.

## 2026-09-22 — abstract "predicts" (audit #1, abstract only)

- "TI_var strongly predicts judge-level human alignment ..., reporting validation-set Spearman correlations" → "We evaluate eight judge configurations ... On this development panel, TI_var is associated with judge-level human alignment, with Spearman correlations of 0.833 / 0.905 / 0.738."
- "strongest single predictor" → "Among single properties, specification monotonicity has the strongest association with human agreement, followed by bug monotonicity". This uses the property names the abstract already defines, not "removed specifications", since the P3 ladder also removes tests.
- Dropped "strongly" (n=8 judges) and "validation-set" (it is the development panel).
- Still open in the main text: §5.3 header `:369`, `:641`, `:646-647`, caption `:1314`, and the intro/contributions still say "validation-set".

## 2026-09-22 — remaining "predict" wording (audit #1 closed)

- §5.3 header → "TI_var tracks judge-level human alignment on the development panel" (labels unchanged).
- `:642` takeaway → "on our development panel, judges that score higher on falsifiable diagnostics also agree more with human assessments".
- `:647-648` property-level → "only weakly associated" / "most consistent association".
- `:766` held-out corpus → "whether the association ... holds under broader item coverage" (was "continues to predict", which assumed the claim).
- App. caption `:1315` → "strongest association"; "weaker standalone signals".
- Kept on purpose: "peer-prediction", "prediction-weighted", "Predict-the-Future" (`:912-920`, external names) and `:1070` (probabilistic predictions matching observed frequencies = score–outcome reliability, correct usage).
- Still open: "validation-set" in the intro, contributions, `:648`, `:767`; `:778` says "validation panel".

## 2026-09-22 — abstract first sentence: deep research + rewrite (APPLIED)

Report: `reports/LLM judges for AI trust artifacts.md`. Notes: `research_notes/LLM judges for AI trust artifacts/`
(5 threads: general adoption, code, tests, formal specs, open problem).

**Verdict on the old sentence** ("LLM judges are increasingly central to evaluating AI-generated code, tests, and formal
specifications"):
- General use of LLM judges: accurate.
- Code: "increasingly used" holds; "central" is overstated (benchmarks and RL rewards still run tests).
- Tests: **inaccurate** (graded by execution; LLM judges only triage).
- Lean theorem statements: accurate (prover pipelines filter with LLM judges).
- Program specs: emerging.

**Applied (candidate A):** "LLM judges are increasingly used to evaluate AI-generated code and formal specifications,
especially where passing tests or type-checking cannot show that an artifact captures its intended meaning."

**Intro support added** (§1 ¶1):
- `lahiri2024evaluating` on the kernel/intent gap.
- A new sentence citing code judges (`Zhuo2024ICEScore`, `TongZhang2024CodeJudge`, `he2025llmjudgese`) and
  prover-pipeline statement filtering (`ying2024leanworkbook`, `lin2025goedelprover`, `wang2025kiminaprover`).
- "Yet the reliability of these judges on formal statements has received little study" (`chen2026reform`).
- Also fixed §1's first sentence to follow the spec rule: "unit tests and formal specifications", not
  "tests, specifications, and formal theorems".

**refs.bib fixes:**
- `Chan2024ChatEval`: first author → Chi-Min Chan.
- `TongZhang2024CodeJudge`: authors → Weixi Tong & Tianyi Zhang; venue → EMNLP 2024.
- `naik2024ticoder`: → Fakhoury et al., TSE 50(9).
- `kenton2024oversight`: title now starts with "On".
- `ospanov2023apollo`: → APOLLO, arXiv 2505.05758, 2025. The "3–7% → over 40%" claim is verified against the abstract.
  The paper's "75% with fewer than 1000 samples" does NOT match the v5 abstract (84.9%, sub-8B, <100 samples).
  (Appendix-only; DEFERRED: Brando 2026-09-22, appendix out of scope for now.)

**Not done (optional):** the trust-artifact framing with citations for "agents write tests" (AIDev, Haque et al.) and
for "models game their own tests" (Baker et al., ImpossibleBench, Claude 3.7 card). A Lahiri/Yang open-problem sentence.
The PDF grew from 28 to 29 pages.

## 2026-09-22 — "validation-set" → "development panel"

- Every use that called the n=75 panel a validation set/panel/labels now says development panel (8 sentence rewrites plus 24 pattern replacements, main text and appendix). Examples: intro "compact development panel", §6 "Development panel vs. held-out test protocol", App. "Development-Panel Human Alignment Appendix", table rows "Best development-panel Spearman".
- `:152` also lost "fits the pooled development corpus" (audit #2): it now reads "the development-panel Spearman correlation between TI_var and judge-level human agreement is 0.833 / 0.905 / 0.738".
- Kept: "validation" meaning the act of validating judges against humans (per-judge human validation, human-validation protocol, trust-validation protocol, cross-model validation status) and the `sec:validation-human-alignment` label.
- Build: 29 pp (was 28). The extra page comes from appendix float placement (app:judge-prompts p20→p21); the main text ends on the same page. 0 overfull boxes.
- Still open from the audit: #2 "weightings discovered on n=75" (abstract), #3 cross-pass table labelling, #4 the ρ=0.881 quote at `:748`, #6 "human-agreement assessment protocol" phrasing, page cut to 9.
- **2026-09-22 follow-up: motivation now cited (resolves Brando's "new emerging problem or cite it" ask).**
  - §1's first sentence cites AI-written tests (`haque2026agentictests`) and AI-written specs
    (`yang2024formalreasoning`, `bursuc2025…`).
  - New sentence: "the checks can be gamed". Coding agents modify or delete failing tests (`baker2025monitoring`,
    `zhong2025impossiblebench`).
  - New sentence: faithful AI-generated specs are an open challenge (`yang2024formalreasoning`).
  - All four bib entries were checked against the arXiv API.
