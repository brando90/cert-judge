# Experiment 34 — Rewrite the cert-judge ICLR 2027 paper into a core-only, accept-grade submission

**TLDR:** You are rewriting `paper_latex/ICLR_2027_submission/` (one `.tex` file per section) into an ICLR 2027 main-track submission that reads as if one careful senior author wrote it: a ≤9-page main text built around one claim (a one-time human panel plus four falsifiable properties screens new LLM judges of Lean formal specifications without new labels), an appendix reduced to what the main text needs, everything else moved (not deleted) to `paper_latex/ICLR_2027_submission/archive/`, every number traced to a committed artifact, and every reviewer complaint from four OpenReview rounds either answered in the text or disclosed as a limitation. You work on the git branch `astra/iclr-mega-rewrite` in a worktree, build the PDF there, keep `experiments/34_iclr_mega_rewrite_astra/results.md` live, and finish with `REPORT.md` for Brando. No LLM API calls, no new experiments, no pushes to `main`.

---

## 0. Who you are and what "done" means

You are a top ML researcher and editor writing for ICLR 2027 (main track). Your goal is acceptance, and if the science supports it, a spotlight. You are the single voice of the paper: the current text was written by several people and several agents over six months and it shows. Rewrite for one voice, one claim, one narrative.

"Done" = the branch builds cleanly, the main text is ≤ 9 pages (target 8–9, spend the room on clarity and one or two well-designed figures, not on cramming), the appendix holds only what the main text cites or needs to defend a claim, every retained number traces to an artifact path, the reviewer-complaint checklist in §6 below is fully ticked, and `REPORT.md` + `results.md` are committed on the branch.

## 1. Read these first (in this order; they are binding)

1. `CLAUDE.md` at the repo root — especially "Terminology for Scientific Prose", "'Specification' has one meaning here", the data-split naming rule, and the LaTeX one-sentence-per-line rule.
2. `~/agents-config/writing/ml_research/ml_research_writing.md` — the persona, Scientific Rigor rules 1–10, the 6-point abstract structure with `% CS197 move` source comments, the Sentence-Level Prose Discipline antipatterns 1–15, and the LaTeX layout rules. Apply all of it. Antipattern 15 (no AI-tell phrasing) matters especially: Brando reads agent-written prose and rejects it on sight. Write the way a careful human author writes.
3. `docs/terminology_cleanup_20260913.md` — why the word "calibration" was removed and what to say instead (development-set association, fitted score mapping, threshold selection, score–outcome reliability). The word `calibrat*` must not appear in the paper.
4. `experiments/archive/31_final_iclr_paper_writing/notes.md` — the preserved ledger of decisions taken on this paper (read all of it; §3 below summarizes the ones that bind you).
5. The reviewer complaints: `experiments/33a_ai4math_reviews/complaints.md`, `experiments/33d_mathai_reviews/complaints.md`, `experiments/33e_tmlr_desk_reject/complaints.md`, and the hub `experiments/33b_or_ledger/results.md`. (`33c_dl4c_reviews` is empty until Brando pastes the reviews; if it has content when you start, include it.)
6. The current paper: `paper_latex/ICLR_2027_submission/main.tex` (preamble + `\input` list), `00_abstract.tex` … `07_conclusion.tex`, `990_…` – `997_…` appendix files, `refs.bib`, `OPEN_QUESTIONS.md`.

## 2. Hard constraints (violating any of these fails the task)

- **No LLM API calls of any kind, and no new experiments.** You may not import `openai`/`anthropic`/`litellm` or call any provider endpoint, and you may not read `~/keys/*`. You may run *zero-inference* analyses over already-committed outputs under `experiments/archive/` (see §7), with the script committed and cited.
- **Every number in the paper traces to a committed artifact.** Keep the existing provenance (`experiments/33b_or_ledger/results.md` "Numbers introduced" table; `experiments/archive/31_final_iclr_paper_writing/notes.md`). If you cannot cite the artifact for a number, the number does not go in. Never invent, round differently, or "recall" a value.
- **Do not reintroduce what was cut today** (§3). Do not add the VeriBench agent-ranking table, the word "calibration", "predicts" for a validation-set association, fitted weights for `TI_var`, PTI-v0 (a different, archived instrument), or any Claude 3.7 downstream result.
- **Scientific objects stay distinct:** the protocol; the four properties P1–P4; the fixed equal-weight index `TI_var`; the 72-pair single-annotator validation set (75 rated, 72 analyzed); three judge families × eight configurations; the separate 343-label five-rater pool that measures a *different* criterion (ρ≈0.13 with the panel) and is not a held-out test.
- **Splits vocabulary:** train / validation / test. The 72-pair panel is the *validation set* (it chose the index form, aggregation, threshold, prompts). There is no training set (`TI_var` has no fitted weights) and no test-set result. Never write "development panel".
- **"Specification" has one meaning** (CLAUDE.md): the theorem statements about the implementation plus the predicates they use. Unit tests are tests, proofs are proofs. "Intent" is the informal requirement. Keep frozen identifiers (P3 "missing-specification ladder" removes theorem statements *and* tests — say so).
- **LaTeX layout:** one sentence per line; `% CS197 move N: …` comments above the abstract's sentences and the intro's paragraphs; `\textsc{}` for system names; `~` before `\ref`/`\cite`; no hard wraps mid-sentence. Check with `python3 ~/agents-config/scripts/latex_sentence_lines.py --check <files>`.
- **Git:** you are on branch `astra/iclr-mega-rewrite` in the worktree `/Users/brandomiranda/cert-judge-astra`. Commit often with explicit pathspecs (`git commit -m "…" -- <paths>`), never `git add -A`, never touch `main`, never force-push. Push the branch (`git push -u origin astra/iclr-mega-rewrite`) after each milestone. Other agents are editing `main` concurrently; you do not need to merge — Brando decides.
- **Build only inside the worktree** (`cd /Users/brandomiranda/cert-judge-astra/paper_latex/ICLR_2027_submission && latexmk -pdf -interaction=nonstopmode main.tex`). Never run `latexmk` in `/Users/brandomiranda/cert-judge/paper_latex/…` (other sessions build there; a concurrent build corrupted their `.aux` today).
- **Preserve, don't delete:** anything you remove from the appendix goes to `paper_latex/ICLR_2027_submission/archive/<original_filename>` with an `archive/README.md` index (file, section titles, why archived, what still cites it — nothing may). Figures that nothing references move to `archive/figures/`.
- **Double-blind:** the paper is anonymous; no author names, no "our lab", no links that identify authors. The repo path in the reproducibility statement is described generically.

## 3. What happened today and what it commits you to (from the ledger)

1. `calibration` → gone (PR #44, 09-13). The residual *concept* leaks were fixed: `TI_var` has fixed equal weights (1/3 each) and is *selected*, not fitted; the cross-pass 0.881/0.810 table is a **weight-tuned geometric variant** (exp23, random search over six component weights) and must be labeled as such, never as `TI_var`; the headline is the validation-set Spearman 0.833 (avg) / 0.905 (pass1) / 0.738 (pass2) for the Codex family, with bootstrap CIs [0.24, 1.00] p=0.017; [0.41, 1.00] p=0.005; [0.11, 1.00] p=0.045 (artifact: `experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json`).
2. The abstract's last sentence is the implication/vision (CS197 move 6), never a hedge. The validation-set caveat lives in the evaluation sentence and in Limitations. Brando approved this closing: *"Judge validation thus moves from a per-judge annotation cost toward a one-time human panel plus automated, falsifiable checks that any new judge must pass."* Keep its meaning; you may improve the wording.
3. §5.4 "Downstream use: ranking VeriBench agents" (Baseline/DSPy ReAct/Trace+/Trace++, Claude 3.7 judge) was removed: it was the VeriBench ICML 2025 result carried over from the workshop version, scored by an uncertified judge. Reviewer DeJF flagged it. It stays out.
4. The intro now frames the problem as the test-oracle problem for AI-written checks ("checking the checks"): agents write code *and* the tests/specs meant to establish trust in it; running a check cannot tell whether the check is right; a theorem is the formal analogue of a grading test with a universal guarantee; the judgment of intent falls to a human oracle, and LLM judges already stand in for it at scale. Brando likes this framing. Keep it and make it sharper, shorter, and cited as it is now.
5. "Reference-based specification quality" is the construct: how completely and correctly a candidate specification captures the gold reference. Judge prompts instruct fidelity; `True` theorems score 0. Presentation (bloat, redundant theorems, over-abstraction) is *not* assessed by any instrument; say so in Limitations only.
6. Annotation facts: one annotator, 0–5 rubric, two strictness passes (pass1 stricter, pass2 lenient), 75 pairs rated (25 problems × 3 agent generations), 72 analyzed (one gold missing); inter-pass Spearman 0.249, QWK 0.372, MAE 0.771 on the 72 overlapping pairs. Codex-panel scores are the median over 3 repeated calls for LLM judges and 9 for the edit-distance/random controls.
7. Two pre-registered screens on the 343-label pool found no qualifying signal (n=14 underpowered; n=32: strongest ρ −0.39, Holm p=0.25; LOO transfer ρ=0.24, p=0.49). They are disclosed in §6 and stay disclosed.
8. An open `% TODO(internal-review)` in the intro asks why a new judge on the *same* domain cannot simply reuse the existing labels. Resolve it in the text: amortization pays off for new artifact distributions, new domains, and repeated judge selection on one fixed labeled set (adaptive overfitting, Dwork et al. 2015 "reusable holdout" — add the bib entry only if you verify it), and the property suite is the mechanism that avoids re-using the labels for each new configuration.
9. The main text is currently ~7.1 pages. You have room up to 9. Use it for clarity, a proper Figure 1 (the protocol), and answers to reviewers — not for restored material.
10. Brando's stated taste: direct, no padding, no self-congratulation, no hedging tails, no "human-agreement assessment protocol" style noun stacks, no agent-flavored prose. He reads source line by line; he wants the appendix reduced to core material because most of it is inherited from earlier experiments by a master's student.

## 4. Target shape of the paper

**Main text (≤ 9 pages), sections in this order:**

1. **Abstract** — six sentences-ish following the 6-point structure, each above a `% CS197 move` comment: problem (AI-written checks need checking; LLM judges stand in for the human oracle), the assumption being challenged (reliability = per-judge human validation, repeated for every judge/prompt/model), the flip (collect labels once; screen every new judge with falsifiable properties whose correct direction is known by construction), the instantiation (P1–P4, `TI_var`, Lean 4 specifications vs gold), the evaluation with numbers (3 families × 8 configs; 0.833/0.905/0.738 on the 72-pair validation set; the lexical grader caught by the properties but not by human agreement; P3 the most informative property), the implication (Brando's closing).
2. **Introduction** — ≤ 1.25 pages. Paragraphs = CS197 moves, each with a comment. Keep the test-oracle framing. Contributions as 2–3 crisp bullets. Resolve the label-reuse TODO here or in §6.
3. **Related work** — ≤ 0.6 page, three paragraphs (LLM-as-a-judge validation; judges for code; judging formal statements), each prior work with its gap attached in the same sentence (antipattern 9).
4. **Problem setup** — task, intent vs formal specification, why a gold reference, the judge model θ = (model, prompt, repeats, aggregation).
5. **Property certification protocol** — the one-time panel, the workflow table, P1–P4 with the cumulative-ladder sentence, `TI_var` with the displayed formula and the plain-words reason for the multiplicative form; a schematic **Figure 1** of the protocol if you can draw it in TikZ cleanly (inputs: gold + candidate; ladders; properties; index; one-time panel link to human agreement; new judges screened by the index). If a figure would be worse than the table, keep the table.
6. **Experiments** — data and human panel (validation set facts, both passes, why correlations on it are optimistic); property sanity checks on GPT-5.3-Codex incl. the alpha-renaming failure and the canonicalization proxy (0.250 → 0.070); `TI_var` tracks judge-level human agreement across three families (figure + merged table with CIs); "human agreement alone can miss a bad judge" (BAD_STRINGY); choice of index (GM competitive; tuned variant separate); which properties matter (per-property table); decision threshold (one short paragraph; table in appendix).
7. **Limitations and held-out test protocol** — validation set not test set; the 343-label pool is a different criterion; the two pre-registered screens; what certification does not cover (vacuity/weakening/over-constraint untested; formatting-only edits beyond the four rewrites; Lean 4 only; gaming untested; presentation unassessed); the locked held-out test that would settle generalization.
8. **Conclusion** — four sentences, ending on the vision.
9. **ICLR statements** after the conclusion (do not count toward the 9 pages): a **Reproducibility Statement** written from repository facts (frozen result directories under `experiments/archive/`, the judge prompt templates in the appendix, the exact model IDs, the repeat/aggregation protocol, the scripts that regenerate each table — cite paths generically, anonymized), an **Ethics Statement** (human annotation by an author, no personal data, no deployment claims), and an **LLM Usage Statement** marked `% TODO(Brando): confirm` stating that LLMs were used as the judges under study and as writing/editing assistants under author supervision.

**Appendix — keep only:** judge prompt templates (`app:judge-prompts`, with the note that "REFERENCE IMPLEMENTATION" in the prompt is filled with the gold's final theorem block, and reconcile the 0–10 vs 0.0–1.0 score-scale statements per panel); index definitions (`app:index-definitions`, v1/v2/GM/`TI_var`, `C_f`); additional results cited from the main text (cross-pass tuned variant, threshold table, per-property/13-configuration figure, human–human agreement statistics, exp19 failure-mode figures); the "unit tests as ground theorems" definition note (`app:spec-vs-tests`); Claude Opus / Qwen sanity figures that §5.2 cites. Everything must be `\ref`'d from the main text or needed to defend a main-text claim.

**Appendix — archive** (move to `paper_latex/ICLR_2027_submission/archive/`): "Related Work (Cont.)" incl. "Scalable Oversight" and "HCI for Solving Scalable Oversight"; "Formal verification context and tooling"; "Why Judge Scores Are Specification-Relative" unless you fold its one useful sentence (Rice) into §6; "Cross-Model Validation Status (Full vs Preliminary)"; "Naive Codex-Style Blind Baseline" unless the main text uses it; "Judge Certification: Additional Plots" unless cited; the Leanstral re-aggregation subsection — Brando is undecided ("Leanstral, fix it?"): keep it only as a short, clearly labeled negative-control paragraph if it fits and is cited from §5.3 or §6; otherwise archive it and say so in `REPORT.md`.

## 5. Writing brief (how, not just what)

- One claim per sentence, ≤ 25 words in abstract/intro, active voice, agent pinned, connectives that match the logic (no "while" for "and"), no colon carrying two propositions, no nominalization stacks, no hype words ("novel", "first", "frontier"), no deepities, no AI-tell phrasing. Run the guide's self-edit checklist on every sentence you write.
- Numbers speak: prefer "0.833 (95% CI [0.24, 1.00])" to adjectives.
- Every table and figure caption states what the reader should see, in one sentence, then the details.
- Name the operation, not a catch-all: association on the validation set; index-form selection; threshold selection; a fitted score mapping (only for the exp23 tuned variant).
- Hedging is calibrated: *we observe* (with N), *we conjecture*, never *we prove*.
- Where a reviewer will object, pre-empt in the sentence that makes the claim, not in a later disclaimer.
- Keep the page budget honest: if the main text exceeds 9 pages, cut restated material and move detail to the appendix, never shrink fonts or margins.

## 6. Reviewer complaints you must resolve in the text (tick each in `REPORT.md`)

From `experiments/33a_ai4math_reviews/complaints.md` (A26-*), `33d_mathai_reviews` (N25-*), `33e_tmlr_desk_reject` (T26-*):

| Must be visibly handled | How |
|---|---|
| Small single-annotator validation set; same labels shaped index/prompts/threshold (A26-meta-1, uMVy-1, c7ev-1, c7ev-2, DeJF-1, DeJF-3) | State it where the numbers appear (§5.1, §5.3) and in §6; keep the CIs; keep "correlations on it are optimistic". |
| Annotation protocol clarity (uMVy-2, c7ev-10) | One paragraph in §5.1 with pass1/pass2 meaning, 75 rated / 72 analyzed, agreement statistics. |
| `TI_var` not uniquely justified; simpler indices competitive (uMVy-3, DeJF-4, c7ev-7) | "Choice of index" paragraph: GM competitive; `TI_var` kept for the variance penalty and positivity across families and passes; tuned variant labeled separately. |
| Weight/normalization sensitivity (uMVy-8) | If you run the zero-inference analysis in §7, report it in one sentence + appendix table; else disclose as not run. |
| Leave-one-family-out / bootstrap (uMVy-6, c7ev-9, DeJF-2) | Bootstrap CIs already exist; LOFO as in §7 or disclosed. |
| Held-out pool not analyzed (uMVy-5, c7ev-3) | §6: the pool is a different criterion (ρ≈0.13); the two pre-registered screens and their outcome; the locked test that would settle it. |
| Alpha-renaming; canonicalization (uMVy-7, c7ev-4, DeJF "surface wording") | §5.2 paragraph + the 0.250 → 0.070 proxy; "a real fix must rescore canonicalized text". |
| Property suite incomplete: vacuity, weakening, over-constraint, formatting-only (c7ev-5, c7ev-11, c7ev-12, N25-ivJs-1) | §6 names the untested classes explicitly and says probes with known direction are the next step (no result claimed). |
| Readability for non-Lean readers (DeJF-6) | §1 and §3 bridge sentences: what a Lean artifact is in programming terms; what alpha-renaming is; why type-checking is not enough. Test: an ML reviewer with no Lean knows what is being judged by the end of §3. |
| Other proof assistants (DeJF-7) | §6: Lean 4 only; the protocol is assistant-agnostic in principle, untested elsewhere. |
| Judge details, severity of edits, strict vs weak monotonicity, figure captions "w.r.t.", missing refs/typos (N25-36Hd-1,3,6,9,10,11) | Already fixed; do not regress them (E1, E2, E7 in `33b_or_ledger/results.md`). |
| Abstract must survive a skim and a plain-text OpenReview form (T26-*) | Abstract has no `\(…\)` that breaks in plain text, no internal `\ref`s; regenerate `experiments/33b_or_ledger/openreview_form_abstract.txt` from your final abstract with `make_openreview_form_abstract.py`. |
| Reference hygiene (c7ev-8) | No anonymous/future-dated entries; every entry complete; run BibTeX and confirm 0 warnings. |

## 7. Optional zero-inference analyses that would strengthen the paper (no LLM calls)

Only from committed outputs, with a script under `experiments/34_iclr_mega_rewrite_astra/analysis/` and its output committed; cite both. Skip any that cannot be traced.

1. **Weight-sensitivity of `TI_var`** (uMVy-8): recompute the judge-level Spearman with human agreement for weight triples on the simplex around (1/3,1/3,1/3) using `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/` (detail rows / summary; `py_src/cert_judge/hsj_scoring.py` has the formulas). Report the range.
2. **Leave-one-family-out** (uMVy-6): with three families × eight configurations, report the pooled association leaving each family out.
3. **Per-family per-property table** if the artifacts exist (exp17 `per_property_correlations.csv` pattern).

## 8. Process and deliverables

1. Start `results.md` in `experiments/34_iclr_mega_rewrite_astra/` with `**Status:** RUNNING (started <ts>)`; update and commit it after each phase (audit → outline → main text → appendix archive → statements → verification).
2. Phase A: read everything in §1; write `outline.md` (claim, section plan, page budget, list of every number with its artifact path, list of appendix keep/archive decisions). Commit.
3. Phase B: rewrite the main text section files; build; iterate until ≤ 9 pages with no overfull boxes in the main text.
4. Phase C: appendix reduction and archive move with `archive/README.md`; figures no longer referenced → `archive/figures/`.
5. Phase D: ICLR statements; `refs.bib` hygiene; regenerate the OpenReview form abstract.
6. Phase E: verification gate (all must pass): `latexmk` exit 0; `grep -ci calibrat *.tex` = 0; no `predict` applied to validation-set associations; no "development panel"; no DSPy/Trace/"Claude 3.7"/PTI; `latex_sentence_lines.py --check` passes on every `.tex`; 0 undefined references/citations; BibTeX 0 warnings; main text ≤ 9 pages (report the page on which References starts); every `\ref` target exists; every appendix section is referenced from the main text; the number-provenance table in `REPORT.md` covers every numeral in the main text.
7. `REPORT.md`: TLDR; what changed and why, section by section; the reviewer-complaint checklist from §6 with the sentence that handles each; the appendix keep/archive table; the number-provenance table; three title candidates (keep the current title unless Brando chooses); open questions for Brando (LLM-usage facts; title; Leanstral; anything you could not trace); the `pdftotext` page count before/after. Commit and push the branch.

TL;DR: Rewrite the ICLR 2027 cert-judge paper on branch `astra/iclr-mega-rewrite` (worktree `/Users/brandomiranda/cert-judge-astra`) into a single-voice, ≤9-page core submission with a reduced appendix (cut material archived under `paper_latex/ICLR_2027_submission/archive/`), every number artifact-traced, every OpenReview complaint answered or disclosed, ICLR statements drafted; no LLM calls, no new experiments, no edits to `main`; deliver `results.md` (live), `outline.md`, `REPORT.md`, and the pushed branch.
