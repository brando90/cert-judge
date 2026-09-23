# Complaints ledger — every OpenReview complaint about this paper, one row each

**TLDR:** 46 complaint rows from three OpenReview rounds (NeurIPS 2025 MATH-AI `N25-*`, ICML 2026 AI4Math `A26-*`, TMLR 2026 desk reject `T26-*`) plus reserved placeholders for the unretrieved ICML 2026 DL4C reviews (`D26-*`). Each row states what the reviewer asked, where the ICLR 2027 manuscript (`paper_latex/ICLR_2027_submission/main.tex`, HEAD `35df712` on 09-22-2026) stands, and the action taken in this experiment (edit IDs `E1`–`E9` are applied by `prompts/02_cc_address_complaints_in_iclr_main_tex.md`; see `results.md` for what landed). Status vocabulary: **Addressed** (paper already handles it), **Disclosed** (stated as a limitation, no new evidence), **Partial → E#** (edit in this pass), **Deferred (owner)** (real new work, not this pass), **Superseded** (the criticized artifact no longer exists), **Unknown** (DL4C text missing).

Line numbers (`:NNN`) refer to the monolithic `main.tex` at HEAD `35df712`. Since commit `710dda9` (09-22-2026) the prose lives in per-section files under `paper_latex/ICLR_2027_submission/` (`00_abstract.tex` … `07_conclusion.tex`, `990`–`997_appendix_*.tex`; `main.tex` is only the preamble and `\input` list), so locate text by section name and grep, not by line.

## Edits applied in this pass (traceable numbers)

| Edit | Where | What | Number source |
|---|---|---|---|
| E1 | `04_property_protocol.tex`, Properties paragraph | P2/P3 stated as weak (non-increasing) targets; ladders are cumulative, so the expected ordering holds by construction regardless of per-edit severity | definitional; probe construction in `py_src/cert_judge/probe_validation.py` (cumulative ladders) |
| E2 | `04_property_protocol.tex`, Fig. 1 subcaptions (b),(c) | "vs." → "w.r.t." for the monotonicity panels, matching the appendix captions | none |
| E3 | `05_experiments.tex`, §5.3 after the Pearson/Kendall sentence | Bootstrap 95% CIs and permutation p for the Codex headline trio | `experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json` (seed 42, 10,000 resamples/permutations): avg 0.833 [0.241, 1.0] p=0.0167; pass1 0.905 [0.407, 1.0] p=0.0054; pass2 0.738 [0.114, 1.0] p=0.0451 |
| E4 | `05_experiments.tex`, §5.2 alpha-renaming paragraph | Post-hoc binder-canonicalization proxy: mean within-item std 0.250 → 0.070, median reduction 64%, eight Codex configurations; a real fix must rescore canonicalized text | `experiments/archive/04_veribench_validation/results_exp24_alpha_canonicalized_identity/summary.json` (`mean_std_original` 0.2501, `mean_std_alpha_canon` 0.0697, `median_pct_std_reduction` 64.28, `n_judges` 8) |
| E5 | `06_limitations.tex`, "Validation set, not a test set" paragraph | Disclose the two pre-registered screens against the five-rater pool: n=14 underpowered; n=32 no candidate met the registered bar (strongest Spearman −0.39, Holm p=0.25; LOO transfer ρ=0.24, p=0.49) | `experiments/archive/23_reanchored_calibration/REPORT.md` (verdict c, n=14); `experiments/archive/24_expanded_panel_cli/results/pass2_full_screen_results.json` (`n_real` 32, `primary_screen_9candidate[0]` rho −0.3911 holm_p 0.2484, `loo` rho 0.2416 perm_p 0.4908, `registered_verdict` "b") |
| E6 | `06_limitations.tex`, "What certification does not cover" | Name the untested failure classes (vacuous, weakened, over-constrained statements; formatting-only edits beyond Table 1) and the Lean-4-only scope | none (scope statement) |
| E7 | `05_experiments.tex`, §5.3 first paragraph | State the aggregation behind the Codex panel: median over repeated calls per pair, three stored calls for the LLM judges and nine for the edit-distance and random controls (the run was configured for nine, but the judge-call cache held three per pair for LLM judges; flagged by session cert-judge-57, verified from the detail rows) | `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/summary.json` (`repeat_agg` median, `judge_repeats` 9 as configured) and `detail_rows.csv` (`repeat_scores` length: 3 for all six LLM configurations × 288 rows, 9 for `editdist_e1` and `random_r1`) |
| E8 | `997_appendix_human_alignment.tex` (ceiling paragraph and table) and `05_experiments.tex` §5.1 | Inter-pass agreement statistics are computed on the 72 overlapping pairs, not 75 | `…/results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json` (`n_overlap_pairs` 72; `n_pass2_only` 3) |
| E9 | `refs.bib` | Delete the uncited anonymous "NeurIPS (to appear)" self-entry; fix `bach2022trusthci` (first author is Tita Alissa Bach, add DOI/arXiv), `ding2025citations` (full authors, volume/pages, arXiv), `bowman2022scalable` (arXiv URL) | arXiv 2304.08795 / DOI 10.1080/10447318.2022.2138826; AAAI 39(22):23787–23795, arXiv 2501.01303; arXiv 2211.03540 |

All nine edits landed in commit `e0631b6` (main.tex, main.pdf, refs.bib), built in a scratch copy: 27 pages, 0 undefined citations/references, 0 BibTeX warnings, one-sentence-per-line check passed.

## NeurIPS 2025 MATH-AI (forum `9WAWDdwqpC`; ivJs 6/10, 36Hd 3/10; no accept tag)

| ID | Reviewer | Complaint | Status in ICLR main.tex | Evidence | Action |
|---|---|---|---|---|---|
| N25-ivJs-1 | ivJs | Limited generalization: finite perturbations on one benchmark; unclear on novel theorem types or adversarial cases | Disclosed (E6) | §6 `:636`–`:639`: "No finite perturbation suite can rule out every judge failure"; gaming "remains untested" | E6 applied (names the untested classes) |
| N25-ivJs-2 | ivJs | Single architecture; no comparison with other judges or ensembles | Addressed | §5.3: three families × eight configurations incl. GPT-4o-mini and non-LLM controls; Leanstral in App. | none |
| N25-ivJs-3 | ivJs | No human validation of the judge | Addressed | §5.1 72-pair validation set; §5.3 judge-level association; §6 validation-not-test caveat | none |
| N25-36Hd-1 | 36Hd | Judge details missing ("simply Claude 3.5 / 3.7") | Addressed (E7) | §3 judge model θ; App. prompt templates; repeats/aggregation not stated in §5.3 | E7 |
| N25-36Hd-2 | 36Hd | Identity/monotonicity looks like edit distance over strings, not the real problem | Addressed | §5.3 Table 3: edit-distance scorer (human ρ 0.20, TI_var 0.06) and lexical BAD_STRINGY exposed by the properties; alpha-renaming isolates lexical sensitivity | none |
| N25-36Hd-3 | 36Hd | Monotonicity experiment ignores severity of changes | Addressed (E1) | §4 says bugs are introduced "cumulatively" but does not say why that neutralizes severity | E1 |
| N25-36Hd-4 | 36Hd | Section 4 agentic setup unclear (inputs, DSPy/Trace, how Lean is used) | Superseded (§5.4 and Table 5 removed by Brando on 09-22-2026: a VeriBench result carried over from the workshop version with an uncertified Claude 3.7 judge; exp32 stopped, commit d7f37c3; main.tex removal committed by session "paper writing certjudge") | §5.4 names the agents and cites DSPy/Trace; framed as a sanity check | none (section deleted) |
| N25-36Hd-5 | 36Hd | LLM-as-judge is not novel | Addressed | §1 contributions: the protocol, not the judge, is the contribution; §2 positioning | none |
| N25-36Hd-6 | 36Hd | Monotonicity should not be defined as a strict ordering | Addressed (E1) | §4 P2/P3 read "scores decrease"; metrics are rank correlations and weak-monotonicity rates | E1 |
| N25-36Hd-7 | 36Hd | Why Claude 3.5 in Sec. 3, 3.7 in Sec. 4, both in App. D | Superseded (§5.4 and Table 5 removed by Brando on 09-22-2026: a VeriBench result carried over from the workshop version with an uncertified Claude 3.7 judge; exp32 stopped, commit d7f37c3; main.tex removal committed by session "paper writing certjudge") | App. "Cross-Model Validation Status": Claude 3.x plots were prompt-iteration runs, not headline statistics; §5.4 says the Claude 3.7 judge is not a certified configuration | none (section deleted) |
| N25-36Hd-8 | 36Hd | Figure 1 unreadable | Superseded | Fig. 1 is now a three-panel figure with error bars | none |
| N25-36Hd-9 | 36Hd | Figure 1: "vs." should be "w.r.t." | Addressed (E2) | main Fig. 1(b),(c) captions still say "vs."; appendix captions say "w.r.t." | E2 |
| N25-36Hd-10 | 36Hd | Missing references in the Appendix | Addressed | 09-22 build log: 0 undefined citations, 0 undefined references | re-check on every build |
| N25-36Hd-11 | 36Hd | Typos: "Lean 4 verus Verus"; stray "**" in App. C | Addressed | App. reads "Lean 4 versus Verus"; no `**` in `main.tex` | none |

## TMLR 2026 desk reject (forum `WKVtlskjeQ`, submission 10994, 07-31-2026)

| ID | Source | Complaint | Status | Evidence | Action |
|---|---|---|---|---|---|
| T26-EiC-1 | Editors-in-Chief | "Unlikely to meet TMLR acceptance criteria" under "extremely limited reviewer capacity" (discretionary triage; no reviews) | Addressed in principle | Claims are scoped as validation-set associations (abstract, §5.1, §6); ICLR has no discretionary triage | none (venue-specific) |
| T26-self-1 | authors' postmortem | OpenReview form abstract rendered "trust index, ," (`\(...\)` stripped) and carried internal appendix references | Addressed (form abstract file) | ICLR form abstract not yet prepared | `openreview_form_abstract.txt` written (plain text, `$…$` only, no internal refs); regenerate from the final abstract before submission |
| T26-self-2 | authors' postmortem | Abstract skim-read as "n=8 correlations + held-out test failed" | Addressed | Current abstract leads with the protocol and its evidence; the held-out caveat sits in §6 | none |

## ICML 2026 AI4Math (forum `xmHP3UhGQ8`; Accept (Poster); source of truth `experiments/18_icml_2026_reviews/pre_prompt.md`)

| ID | Reviewer | Complaint | Status in ICLR main.tex | Evidence | Action |
|---|---|---|---|---|---|
| A26-meta-1 | AC v5zC | Evidence is calibration-based: small panel, moderate label agreement, overfitting risk in metric/prompt/threshold choices, alpha-renaming sensitivity | Disclosed | §5.1 "correlations on it are optimistic"; §6 first paragraph; §5.2 alpha table | E3, E4, E5 strengthen the disclosure |
| A26-uMVy-1 | uMVy | Validation is small (~75 pairs, few configurations) and the same labels shaped metric design, prompt selection, aggregation, threshold | Disclosed | §5.1 `:298`; §6 `:628` | none beyond E3/E5 |
| A26-uMVy-2 | uMVy | Annotation protocol unclear: one annotator under strictness levels vs multiple passes | Addressed | §5.1: one annotator, two rubric strictness levels (pass1/pass2), 75 pairs = 25 problems × 3 generations, 72 analyzed | E8 corrects the appendix pair count for the agreement statistics |
| A26-uMVy-3 | uMVy | TI_var not uniquely justified; simpler alternatives competitive | Addressed | §5.3 "Choice of index": GM competitive for two families; why TI_var is kept; tuned-weight variant labeled separately | none |
| A26-uMVy-4 | uMVy | VeriBench rankings may carry judge-family bias | Superseded (§5.4 and Table 5 removed by Brando on 09-22-2026: a VeriBench result carried over from the workshop version with an uncertified Claude 3.7 judge; exp32 stopped, commit d7f37c3; main.tex removal committed by session "paper writing certjudge") | §5.4 `:604`: sanity check; Claude 3.7 judge not a certified configuration | none (section deleted) |
| A26-uMVy-5 | uMVy | Held-out reviewer-pool results not included; do trends persist once protocol choices are frozen? | Disclosed (E5) | §6 `:629`–`:630`: pool exists, different rubric, ρ≈0.13 with the panel; registered screens not mentioned | E5 |
| A26-uMVy-6 | uMVy | Leave-one-family-out or bootstrap robustness | Addressed (E3); LOFO deferred | §5.3 `:568`: bootstrap CI only for the 13-configuration tuned variant | E3 (CIs for the headline trio); LOFO deferred |
| A26-uMVy-7 | uMVy | Can Lean-aware canonicalization reduce alpha-renaming sensitivity? | Addressed (E4) | §5.2 `:313` names canonicalization as a fix without evidence | E4 |
| A26-uMVy-8 | uMVy | Sensitivity of TI_var to weighting and normalization | Deferred (weight ablation not run) | §4: fixed equal weights; §5.3: arithmetic/geometric/tuned comparison | Deferred (systematic weight ablation not run) |
| A26-uMVy-9 | uMVy | Do downstream rankings stay stable when judge and generator families are separated? | Superseded (§5.4 and Table 5 removed by Brando on 09-22-2026: a VeriBench result carried over from the workshop version with an uncertified Claude 3.7 judge; exp32 stopped, commit d7f37c3; main.tex removal committed by session "paper writing certjudge") | §5.4 uses one judge family | none (section deleted) |
| A26-c7ev-1 | c7ev | Main result is validation-set fit, not a locked held-out test | Disclosed | §1 `:157`; §6 | E5 |
| A26-c7ev-2 | c7ev | 75 pairs; two passes agree only moderately | Disclosed | §5.1 `:302`: Spearman 0.249, QWK 0.372, MAE 0.778 | none; see open item O1 |
| A26-c7ev-3 | c7ev | Larger independent annotation pool not analyzed | Disclosed (E5) | §6 `:629` | E5 |
| A26-c7ev-4 | c7ev | Alpha-renaming failure mode is important | Addressed | §5.2 paragraph + Table 1 | E4 |
| A26-c7ev-5 | c7ev | Property suite incomplete: vacuity, subtle weakening, over-constraint, domain-specific mismatch | Disclosed (E6) | §3 lists these failure kinds; §6 says no finite suite covers everything | E6 |
| A26-c7ev-6 | c7ev | VeriBench ranking is only a sanity check, not independent validation | Superseded (§5.4 and Table 5 removed by Brando on 09-22-2026: a VeriBench result carried over from the workshop version with an uncertified Claude 3.7 judge; exp32 stopped, commit d7f37c3; main.tex removal committed by session "paper writing certjudge") | §5.4 `:604` | none (section deleted) |
| A26-c7ev-7 | c7ev | Justify the geometric, variance-aware aggregation beyond validation fit | Addressed | §4 `:257`–`:258` (multiplicative penalty rationale); §5.3 "Choice of index" | none |
| A26-c7ev-8 | c7ev | Reference list has anonymous, future-dated, or workshop-only entries | Addressed (E9) | `refs.bib`: `anonymous2025formaljudge` ("NeurIPS (to appear)", uncited); `bach2022trusthci` wrong first author, no DOI; `ding2025citations` truncated | E9 |
| A26-c7ev-9 | c7ev | Add CIs, bootstrap, or other uncertainty for judge-level correlations | Addressed (E3) | only the 13-configuration interval `:568` | E3 |
| A26-c7ev-10 | c7ev | Clarify labeling protocol (annotators, pass1/pass2 meaning, disagreements) | Addressed | §5.1 | E8 |
| A26-c7ev-11 | c7ev | Open: reference-free property suite; number of annotators for stable targets; rubric ambiguity vs Lean misunderstanding | Deferred | future work only; the appendix paragraph that mentioned a reference-free extension (old "Vericode" subsection) was removed in the 09-22-2026 cleanup (commit 86ebd8c), so no paper text now promises it | Deferred (future work) |
| A26-c7ev-12 | c7ev | Failure analysis should include formatting-only perturbations | Disclosed (E6) | Table 1 covers RENAME/REORDER/STYLE/ALPHA only | E6 names the gap |
| A26-DeJF-1 | DeJF | Trust index calibrated and tested on the same 75-pair panel | Disclosed | §5.1, §6 | E5 |
| A26-DeJF-2 | DeJF | Only eight judge configurations; correlations may be unstable | Addressed (E3) | §5.3 `:569` "Intervals this wide…" | E3 |
| A26-DeJF-3 | DeJF | Labels are noisy: one annotator, two related passes, moderate agreement | Disclosed | §5.1 `:302` | none |
| A26-DeJF-4 | DeJF | TI_var not clearly better than the simpler geometric index | Addressed | §5.3 "Choice of index" | none |
| A26-DeJF-5 | DeJF | VeriBench demo uses Claude 3.7 while validation uses other families; "same calibrated judge" unclear | Superseded (§5.4 and Table 5 removed by Brando on 09-22-2026: a VeriBench result carried over from the workshop version with an uncertified Claude 3.7 judge; exp32 stopped, commit d7f37c3; main.tex removal committed by session "paper writing certjudge") | §5.4 `:604` | none (section deleted) |
| A26-DeJF-6 | DeJF | Dense sections; simplify for readers unfamiliar with Lean | Deferred (experiment 31) | §1 bridge sentences added 09-22 (commit `bb40162`) | Deferred (experiment 31 owns prose) |
| A26-DeJF-7 | DeJF | Does the approach work for other proof assistants? | Disclosed (E6) | not stated | E6 (Lean-4-only scope named) |

## ICML 2026 DL4C (forum `gGR1gE7x3a`; Accept (Poster); reviews NOT retrieved — see `reviews/fetch_attempts.md`)

| ID | Reviewer | Complaint | Status | Evidence | Action |
|---|---|---|---|---|---|
| D26-meta-1 | unknown | **Unknown**: meta-review text not retrievable without an OpenReview login | Unknown | `reviews/icml2026_dl4c_gGR1gE7x3a.md` (skeleton) | Brando pastes the reviews; then run `prompts/03_…` |
| D26-R1-1 … | unknown | **Unknown**: reviewer text not retrievable | Unknown | same | same |

## Open items found while auditing (not reviewer complaints)

| ID | Item | Evidence | Proposed handling |
|---|---|---|---|
| O1 | §5.1 and the appendix quote inter-pass MAE 0.778 and MSE 1.139, but the reliability artifact reports MAE 0.771 and RMSE 1.059 on the 72 overlapping pairs; no artifact containing 0.778/1.139 was found | `exp18_human_label_reliability/summary.json` (`mae_0_5` 0.7708, `rmse_0_5` 1.0590); grep of `experiments/` for `0.778`/`1.139` | Resolved by E8 on 09-22-2026: §5.1 and the appendix table now quote MAE 0.771 / MSE 1.121 on the 72 overlapping pairs (mean-of-duplicates convention, exp18 artifact); the pass histogram still uses the 75-pair files (owner: experiment 31) |
| O2 | Appendix ceiling table "Best validation-set Spearman (avg labels) 0.480 / pass1 0.559" vs Table 3 P1 avg 0.47 (0.4664 in `judge_rows`) | `results_final_stat_reliability_suite/exp18_identity_alpha_ablation/judge_rows_alpha_ablation.csv` contains 0.480/0.559 | Different run (alpha-ablation panel); label the appendix rows with their source or drop them; owner: experiment 31 (appendix) |
| O3 | Intro `% TODO(internal-review)` at `:146` (why a new judge on the same domain cannot reuse existing labels) | `main.tex:146` | Owner: experiment 31 |
