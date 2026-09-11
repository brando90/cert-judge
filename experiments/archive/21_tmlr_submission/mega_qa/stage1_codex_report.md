# Mega QA Stage 1 — TMLR desk-reject postmortem and resubmission audit

**TLDR:** The frozen submission passes the mechanical checks that were already ruled out: it is technically anonymous, uses the same `tmlr.sty` bytes as both live candidates, has 11 pages of main content, renders cleanly, and has no identifying PDF metadata. The broken OpenReview abstract was a real first-impression defect, but the stronger postmortem explanation is confirmed: at a three-minute skim the paper advertises an in-sample, tuned, judge-level correlation on only eight configurations, then says the intended held-out test was confounded and a later screen was negative. Candidate A′ still reads like that workshop paper plus a caveat. Candidate B has the substantially better TMLR story—measurement instrument, artifact audit, protocol drift, and a pre-registered negative result—but it is not ready to submit. Its abstract is overlong, omits `n=8` and uncertainty next to the positive correlations, its old title is both generic and exactly linkable to the public workshop paper, and its text overstates the n=32 screen as “powered,” “adequate power,” and closing the question despite no formal power analysis. I also found two recoverable raw scores that make the literal raw pool count 345 rather than the analysis-effective 343; this needs a frozen inclusion decision. Verdict: **neither-fix-first, then resubmit B**.

## 1. Severity-ranked findings

### BLOCKER 1 — Candidate B's central positive promise conflicts with its negative evidence

Candidate B repeatedly says property certification can be calibrated once and then used to screen new judge configurations without human remeasurement (`main.tex`, introduction and contribution 1). Its own strongest new evidence says no tested label-free property signal met the registered transfer bar on the revised semantic construct, while the pool-internal zero-leakage item-transfer analysis is weak-to-null.

This is not cured by saying the positive result is “calibration-scoped.” A skeptical EiC can summarize the first two pages as:

> The method's practical promise is label-free screening of new judges, but the only cross-configuration transfer test is negative and the original positive relationship is an in-sample fit over eight judge configurations.

That is a claim–evidence gap under TMLR's primary criterion, which asks whether claims have accurate, convincing, clear evidence. The safe scientific framing is that CertJudge is an **auditable diagnostic protocol whose attempted transfer exposed construct drift and failed its registered success criterion**, not that amortized evaluator validation has been demonstrated.

Recommendation requiring author judgment: remove or qualify every present-tense deployment promise (“extends that trust signal,” “any new judge can be screened,” “amortized oversight … is feasible,” “supports amortized evaluator validation”). Preserve the workflow as a hypothesis/design goal and make the failed boundary test the result.

### BLOCKER 2 — “Powered,” “adequate power,” and “closes the question” are unsupported

Candidate B's abstract, contribution list, Section 5.5 heading/text, and conclusion call the n=32 analysis “powered,” claim “adequate power,” or say it “closes the question.” `experiments/24_expanded_panel_cli/PREREG.md` specifies a target of at least 26 configurations and a forced `(a)/(b)` decision, but contains no prospective power analysis, minimum detectable effect calculation, or effective-sample-size treatment. The new panel also contains narrow prompt variants whose pseudo-replication is acknowledged in the paper.

The registered verdict `(b)` is real. A formal claim of adequate statistical power is not established by the artifact. Use language such as:

> In the expanded pre-registered n=32 panel, no candidate met the registered success criterion; the registered verdict was `(b)`.

Do not say the screen proves that no signal exists, is powered in the statistical sense, or closes the question unless a defensible prospective/simulation-based power analysis is added.

### BLOCKER 3 — Pool label count is internally reproducible as 343 but raw-file lineage exposes 345 recoverable scores

The paper, form kit, `results_exp43_frozen_tivar_heldout`, and dir-22 analysis all report 343 labels. That is the effective count produced by the current loader. A direct raw TSV audit found:

- ordinary populated score column: 343 labels;
- `participant1_data_correct_prompt.tsv:21` contains `13_MyUppercase__agent1.lean 1` in the candidate column;
- `participant3_data_pass_1.tsv:47` contains `0_bisect_right__agent0.lean 3` in the candidate column;
- including those two clearly embedded scores yields 345 scored labels.

The loader in `experiments/04_veribench_validation/exp43_frozen_tivar_heldout.py:200` converts the absent field to the nonempty string `"None"` before testing `if not score_text`, so its intended embedded-score recovery branch does not run for those rows.

This does not invalidate the reported analyses, and the headline cross-protocol correlation remains approximately 0.13. It does create an avoidable reviewer-level reproducibility trap. Before resubmission, choose and document one of two policies:

1. exclude malformed rows by a predeclared data-cleaning rule and explicitly call 343 the **analysis-effective** count; or
2. repair the parser, rerun every pool-derived artifact, and update all values/counts affected by the resulting 345-label pool.

I did not make this scientific/data-inclusion decision automatically.

### CRITICAL, FIXED — Candidate B had copied the wrong EXP46 adjusted and LOO p-values

Before this QA, B stated the pre-registered nine-candidate result as Holm `p=0.22` and LOO `p=0.47`. The authoritative JSON says:

- nine-candidate primary: strongest `rho=-0.3911`, raw `p=0.0276`, Holm `p=0.2484`;
- eight-candidate drift-gated sensitivity: Holm `p=0.2208`;
- LOO: `rho=0.2416`, permutation `p=0.4908`;
- registered verdict: `"b"`.

The paper had mixed the eight-candidate sensitivity Holm value into the nine-candidate primary and used a stale LOO p-value. I corrected Candidate B and the stale dir-24 Markdown summaries. I also clarified that stability remains in the pre-registered nine-candidate primary and is excluded only from the eight-candidate drift-gated sensitivity.

### MAJOR — Candidate B's first page still invites a triage rejection

The rewritten abstract is intellectually stronger but visually and rhetorically overloaded. It is 377 words after TeX stripping, occupies most of page 1, contains internal Appendix/Section links, and makes the reader process four stories at once: scalable validation, three large validation correlations, downstream VeriBench ranking, a confounded frozen test, an audit, pool reliability, and two pre-registered screens.

Most damagingly, it reports `0.833/0.905/0.738` without saying in the abstract that these are correlations over only **eight judge configurations**, and it omits their wide uncertainty. That presentation makes “strongly predicts” look stronger than the evidence. Candidate A′ at least restores the exact bootstrap intervals and permutation p-values in its contribution list; B drops them entirely.

Recommendation: reduce the paper abstract to roughly 180–220 words; state `n=8 judge configurations` immediately with the positive correlations; report or plainly summarize the wide uncertainty; remove internal references; make “registered `(b)` at n=32” the second result rather than an appended twist; omit the downstream ranking from the abstract.

### MAJOR — Candidate B retains the exact public workshop title

The PDF is formally anonymous, but `CertJudge: Evaluating Lean Formal-Code With Falsifiable Properties` is the exact title of the public AI4Math workshop paper. A title search immediately returns the named author list. TMLR instructs reviewers not to actively deanonymize submissions, so this is not evidence that submission 10994 violated anonymity. It is nevertheless unnecessary linkability and contradicts the resubmission kit's promise that the title will be differentiated.

Candidate A′ fixes linkability but overcorrects with a three-line, 19-word title that reads like a result inventory. Candidate B needs a shorter differentiated title centered on evaluator measurement/audit, not the old workshop title and not A′'s laundry list.

Public comparison: [AI4Math workshop paper](https://openreview.net/pdf?id=xmHP3UhGQ8). TMLR's [author guide](https://jmlr.org/tmlr/author-guide.html) requires an anonymous manuscript, while its [FAQ](https://jmlr.org/tmlr/faq.html) tells reviewers not to search for workshop/preprint identities.

### MAJOR — Frozen and original Candidate B used global layout compression despite an unmodified style file

The frozen `tmlr.sty` is unmodified, but frozen `main.tex` globally changed float spacing, caption size, table size, `arraystretch`, and `tabcolsep`. TMLR warns that template changes affecting layout may lead to rejection without review. The generic decision did not cite formatting, and the already verified stylefile fact stands, so I do not elevate this above the skim/claims explanation. It was still a needless compliance risk.

Candidate A′ had removed these overrides. Candidate B had accidentally retained them; I removed them. B now compiles to 29 total pages with References starting partway down page 11; the main content therefore ends on page 11 and remains within the 12-page short-review boundary.

### MODERATE — Bibliography quality is visibly unfinished

The frozen bibliography has abbreviated placeholder-like entries including `Z. Ding et al.`, `A. Naik et al.`, and literal `{Ospanov et al.}` without full provenance. This is not an anonymity leak, but it can reinforce a “writing not up to standard” skim impression. Complete the author lists and DOI/arXiv/venue fields before resubmission.

### MODERATE — Two numeric tables still lack raw named provenance

I could not locate a machine-readable result artifact for the downstream VeriBench table (`0.470/0.615/0.477/0.588`); the values occur in `experiments/00_overall_cert_judge_metric_with_properties/instruction_for_codex.md`, which is prose/input rather than result output. I also could not find an artifact matching Candidate B's P4 rewrite table (`RENAME 0.936/0.005`, `REORDER 0.849/0.029`, `STYLE 0.982/0.001`, `ALPHA 0.399/0.096`). Add `% source:` comments pointing to canonical raw/result files or remove/replace the tables.

## 2. Postmortem verification of frozen submission 10994

### Mechanical and policy checks

| Cause | Stage-1 result | Evidence |
|---|---|---|
| Technical anonymity | **Ruled out** | Page 1 says “Anonymous authors / Paper under double-blind review.” PDF Title/Author/Subject/Keywords metadata are blank. No filesystem paths, emails, or author names were found in PDF strings. Self-citations are written in the third person. |
| De facto linkability | **New risk, not a technical violation** | Exact title matches the public workshop paper; the abstract explicitly says “accepted workshop version.” This likely was not the cited cause, but a differentiated title is safer. |
| Stylefile modification | **Ruled out as stated** | SHA-256 for frozen, A′, and B `tmlr.sty`: `816214ff5919aa457b6b443bee52b15d9561421417b7f8a50cc84651519f0002`. The official author guide links the JmlrOrg template. Direct shell retrieval of raw GitHub was blocked by sandbox DNS, so the official-byte identity relies on the supplied verified fact; local equality was independently verified. |
| Template/layout modification | **Additional risk** | Frozen `main.tex` globally compressed floats/captions/tables. This is distinct from modifying `tmlr.sty`. TMLR's [submission instructions](https://jmlr.org/tmlr/submissions.html) warn against changes that alter formatting/layout. |
| Main-content length | **Ruled out** | Frozen PDF: 28 total pages; References starts on page 12; main content ends page 11. TMLR permits variable length and uses 12 main-content pages as the short-review boundary. |
| Workshop overlap | **Ruled out** | The decision did not cite overlap. TMLR's [editorial policy](https://jmlr.org/tmlr/editorial-policies.html) permits overlap with publicly declared non-archival workshops. |
| Quota | **Ruled out for this decision** | Not mentioned in the decision. The resubmission kit correctly keeps quota/author-list confirmation as an external preflight item. |
| Broken OpenReview abstract | **Confirmed contributor** | The supplied record of `\(...\)` stripping explains the visible `, ,` defect; standalone internal references also made the form abstract read like a bad PDF extraction. This is exactly the page an EiC skims first. |

### PDF structure and rendering

- Frozen PDF: 28 pages, US Letter, searchable text, no encryption, forms, or JavaScript.
- Fonts are embedded; PDF metadata contains no title or author identity.
- `main.log` contains no undefined citations/references, fatal errors, or overfull boxes. Only underfull boxes and a benign Latin Modern bold-small-caps substitution appear.
- I rendered all pages with Poppler and visually inspected page sheets plus representative original-resolution pages. I found no blank pages, clipping, overlap, missing glyphs, broken figures, or unreadable equations.
- Main figures are sharp enough for review. Some multi-panel plot labels and appendix x-axis labels are small, and several captions are dense, but no figure-quality defect plausibly explains a desk rejection by itself.
- The bibliography includes authors who are plausibly coauthors of this paper, but ordinary third-person self-citation is compatible with double blind. There is no “in our prior work” or explicit identity disclosure.

### Postmortem conclusion

The evidence supports the supplied hypothesis. The broken landing-page abstract lowered the writing-quality prior. Once the PDF was opened, the quickest defensible summary was “large correlations over n=8 configurations selected on the same validation corpus; intended held-out test did not answer transfer; later property screen was negative.” Under exceptional triage pressure, that makes “unlikely to meet the claims–evidence criterion” much more plausible than anonymity, stylefile, length, overlap, or quota.

TMLR's own [acceptance criteria](https://jmlr.org/tmlr/acceptance-criteria.html) are favorable to a corrected resubmission: claims may be reduced instead of requiring more experiments, and a careful robustness/generalizability audit with actionable lessons can satisfy audience interest. The paper needs to look like that audit in the first 30 seconds.

## 3. Three-minute EiC triage simulation

### Candidate A′ — cleaned/retitled submitted version

**Three-minute impression**

1. The title is differentiated and honestly names validation calibration, protocol drift, and a negative result, but it is three lines and reads like a list of rebuttal points.
2. The abstract begins with a useful question, then calls itself an extension of a workshop version. It still devotes most attention to the method and the three validation correlations.
3. The positive evidence is visibly small and tuned: n=8 judge configurations, wide bootstrap intervals, same labels used for model/index choices.
4. The held-out result is not a clean held-out validation: protocol drift prevents the frozen comparison from answering transfer.
5. The actual new result—the n=32 registered `(b)` screen—is compressed into one late abstract sentence and buried in a limitations section. It is absent from the three-item contribution list.
6. The downstream VeriBench result uses a judge outside the calibrated eight-judge panel and is expressly a sanity check, so it cannot rescue validation.

**Skeptical verdict: desk-reject.** A′ is cleaner than 10994 but still looks like the same workshop paper with a long caveat bolted on. It does not make the audit/negative result the paper's organizing contribution, so an EiC can still judge the evidence insufficient for the practical amortization claim and the TMLR-wide lesson insufficiently visible.

**Top five fixes for A′**

1. Promote the artifact audit, protocol-drift diagnosis, and registered `(b)` result into a main empirical section and the contribution list.
2. Replace the three-line title with a short differentiated measurement/audit title.
3. Rewrite the abstract around two scoped results: n=8 within-protocol calibration with uncertainty, then n=32 registered failure to meet transfer criteria; remove internal refs and the downstream ranking.
4. Stop claiming the method already enables new-judge screening without reannotation; frame this as the tested proposition that failed on the revised construct.
5. State the general lesson for TMLR readers—construct lineage and preregistered transfer tests for learned/LLM evaluators—before the Lean-specific implementation details.

### Candidate B — measurement-instrument/audit rewrite

**Three-minute impression**

1. This is the stronger paper. The first page makes evaluator validation a measurement problem, exposes the failed held-out attempt, describes the refuted integrity hypothesis, identifies protocol drift, reports pool reliability, and names the registered negative outcome.
2. The audit is credible and unusually transparent. It is the piece most likely to satisfy TMLR's “something to be learned” criterion beyond Lean.
3. The first page is nevertheless too dense. The old generic title hides the audit and exactly identifies the public workshop paper. The abstract is so long that the contribution is hard to prioritize.
4. The abstract presents the `0.833/0.905/0.738` trio without `n=8` or uncertainty, then later says transfer is open/negative. On skim, this can look like selective emphasis.
5. The introduction promises label-free screening of new judges, contradicting the registered failure to find a transferable signal on the semantic construct.
6. “Powered,” “adequate power,” and “closes the question” are stronger than the preregistration artifact supports.
7. The raw 343/345 lineage discrepancy gives a skeptical reviewer an easy handle unless resolved first.

**Skeptical verdict: desk-reject in its current scientific framing; likely send to review after the minimal fixes below.** B has a real TMLR-interest case that A′ lacks, but it currently overstates both the positive feasibility claim and the strength/finality of the negative test. The problem is repairable by narrowing claims and simplifying page 1, not by inventing a new positive experiment.

**Top five fixes for B**

1. Replace every unqualified amortization/deployment promise with the scoped methodological finding actually supported by the audit.
2. Replace “powered,” “adequate power,” and “closes the question” with the exact registered n=32 outcome, unless a formal power analysis is added.
3. Cut the abstract to about 200 words; put `n=8` and uncertainty beside the validation trio; put registered verdict `(b)` beside the n=32 result; remove internal refs and the VeriBench ranking.
4. Adopt a short differentiated title that foregrounds evaluator measurement and protocol drift/negative transfer.
5. Resolve and freeze the 343-versus-345 inclusion policy, regenerate affected artifacts if necessary, and add canonical `% source:` paths for the P4 and downstream tables.

## 4. Candidate B claims-versus-artifacts audit

Status refers to the source state encountered during this QA. `MISMATCH (FIXED)` means the paper/artifact summary was mechanically corrected in this stage. Paths are relative to the repository root.

| # | High-stakes claim in B | Named/canonical artifact and exact check | Status |
|---:|---|---|---|
| 1 | Codex `TI_var` vs human: avg/pass1/pass2 = `0.833/0.905/0.738` | `results_exp28_varaware_codex_{avg_newindex,pass1_newindex,pass2_newindex}/summary.json`, `rho_TI_vs_human` = `0.8333333333/0.9047619048/0.7380952381` | **CONFIRMED** |
| 2 | Cross-family table: Opus `0.810/0.595/0.643`, Qwen `0.476/0.857/0.905`, Codex trio above | Corresponding `results_exp28_varaware_{opus,qwen,codex}_*/summary.json` fields match all nine cells | **CONFIRMED** |
| 3 | Arithmetic v1 Pearson avg/pass1/pass2 `0.774/0.661/0.837`; Kendall `0.571/0.571/0.643` | `results_exp16_final_robust_r9_median/summary.json` exact Pearson `0.7740307/0.6611195/0.8368668`; Kendall `0.5714286/0.5714286/0.6428571` | **CONFIRMED** |
| 4 | In-sample weight sweep `0.762 -> 0.881`, with CIs `[0.103,1]` and `[0.392,1]` | `results_exp21_cert_index_sweep/median/summary.md` | **CONFIRMED** |
| 5 | P3 and P2 are the strongest single properties at `0.747` and `0.714` | `results_exp17_final_robust_avg/summary.json`: P3 `0.7470421737`, P2 `0.7142857143` | **CONFIRMED** |
| 6 | Cross-protocol drift is approximately `rho=0.13`, `n=63` | Independent exact-key, repeat-averaged raw TSV recomputation: `rho=0.1313978465`, `n=63`; consistent with dir-22 report | **CONFIRMED** |
| 7 | Analysis pool has 343 labels, 78 items, 5 raters | `experiments/22_pooled_heldout_and_noise_ceiling/results/results.json`: `n_labels=343`, `n_items=78`, `n_raters=5` | **CONFIRMED** for current analysis |
| 8 | Reviewers “contributed 343 scored labels” as a literal raw-data count | Five participant TSVs contain 343 ordinary score fields plus two recoverable scores embedded in candidate fields, totaling 345 | **MISMATCH** — paper `343`, raw recoverable `345` |
| 9 | Pool pairwise rho `0.42`, effective raters `4.4`, reliability `0.76`, ceiling `0.87`, LOO mean `0.57` | dir-22 `results.json`: `0.4184816`, `4.3974359`, `0.7598782`, `0.8717099`, `0.5719726` | **CONFIRMED** |
| 10 | Revised-protocol anchors: strict set vs pool `0.96`, annotator relabel vs pool `0.90`; old labels vs relabel about `0.18` | dir-22 `REPORT.md`: repeat-averaged `0.96`, relabel `0.90`, cross-campaign `0.18`; report explains last-wins `0.899` alternative | **CONFIRMED** |
| 11 | Real-judge pool alignment median `-0.24`, best `+0.42`; edit distance `-0.57`, BAD_STRINGY `-0.46` | dir-22 `results.json`: median `-0.2367953`, LeanStral P1 `+0.4219059`, edit distance `-0.5664186`, Codex BAD_STRINGY `-0.4565824` | **CONFIRMED** |
| 12 | Pool-internal zero-leakage transfer: single split `-0.460..+0.295`; ten-seed means `0.119±0.275..0.457±0.218`; oracle `0.843..0.870` | `results_exp42_proper_transfer/PAPER_TABLE.md` and `MULTISEED_TABLE.md` | **CONFIRMED** |
| 13 | First prereg screen: identity `-0.539`/`-0.517`, Holm `0.459`/`0.555`, LOO `+0.539 p=0.155`, verdict underpowered | `experiments/23_reanchored_calibration/results/results.json`: exact `-0.5390542`, `-0.5170520`, `0.4594270`, `0.5552722`, LOO `0.5390542`, `p=0.1554223`; registered outcome `c` | **CONFIRMED** |
| 14 | EXP46 n=32 identity `+0.13 p=0.48`; subgroups `-0.62/+0.85`; six of seven drift gates pass, stability about `0.80` | `pass2_full_screen_results.json`: `n_real=32`, identity `0.1285/0.4805`, subgroups `-0.618/+0.853`, gates six pass and stability `0.7978` | **CONFIRMED** |
| 15 | EXP46 nine-candidate strongest `-0.39` Holm `0.22`; LOO `0.24 p=0.47` | Authoritative JSON says `-0.3911`, nine-candidate Holm `0.2484`; `0.2208` is the eight-candidate sensitivity; LOO `0.2416 p=0.4908` | **MISMATCH (FIXED)** — current B now uses exact JSON values |
| 16 | EXP46 registered verdict is negative `(b)` | `pass2_full_screen_results.json`: `registered_verdict: "b"` and all three `a_via` flags false | **CONFIRMED** |
| 17 | Alpha canonicalization changes mean within-item std `0.250 -> 0.070`, median reduction `64.3%` | `results_exp24_alpha_canonicalized_identity/summary.json`: `0.250118 -> 0.069706`, median `64.284%` | **CONFIRMED** |
| 18 | Excluding alpha weakens avg trend `0.762 -> 0.619` | `results_exp18_alpha_ablation_r9/summary.json`: avg `0.7619048 -> 0.6190476` (pass1/pass2 changes also match) | **CONFIRMED** |
| 19 | Human-pass agreement `n=72`, Spearman `0.249`, Pearson `0.375`, Kendall `0.221`, QWK `0.372`, MAE `0.771`, RMSE `1.059` | `results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json` matches all rounded values | **CONFIRMED** |
| 20 | Label divergence JS `0.081` bits, KL `0.415` bits | `results_exp16_final_robust_r9_median/human_pass_divergence_aligned72.json`: `0.0809918`, `0.4152452` | **CONFIRMED** |
| 21 | BAD_STRINGY human rho about `0.45`, weak monotonicity `12.5%` | `results_exp16_final_robust/summary.json` / `judge_rows.csv`: avg human rho `0.4486132`, `bug_weak_mono_pct=12.5` | **CONFIRMED** |
| 22 | Threshold table `0.058 -> 0.046` flip rate and `0.583 -> 0.536` pass rate | `experiments/02_reviewer_response_neurips_math_ai_2026/results/threshold_calibration_sweep/threshold_metrics.csv`: `0.058081 -> 0.046086`, `0.582702 -> 0.535985`, intervals match | **CONFIRMED** |
| 23 | Downstream VeriBench table avg `0.470/0.615/0.477/0.588` | Values are repeated in `experiments/00_overall_cert_judge_metric_with_properties/instruction_for_codex.md`, but I found no canonical machine-readable output or `% source:` comment for this table | **ARTIFACT-MISSING** |
| 24 | P4 rewrite table `0.936/0.005`, `0.849/0.029`, `0.982/0.001`, `0.399/0.096` | No matching result artifact or source comment found under `experiments/`; exact-value search only found unrelated values | **ARTIFACT-MISSING** |

Audit result: 20 claim groups confirmed, one raw-lineage mismatch requiring an author decision, one substantive EXP46 mismatch fixed, and two source gaps. The high-stakes anchors supplied in the task all reproduce exactly after the fix.

## 5. Form-field kit review

File: `experiments/21_tmlr_submission/resubmission_kit.md`.

After the mechanical edit in this stage:

- **PASS:** the form abstract contains no `\(...\)` delimiters;
- **PASS:** it contains no `Section` or `Appendix` references;
- **PASS:** math uses OpenReview-compatible `$...$` delimiters;
- **PASS:** it is 206 words and states `n=8`, the validation-only scope, protocol drift, `rho≈0.13`, n=32, and failure to meet the registered success bar;
- **PASS with blocker:** its `343` label count matches the current analysis artifacts but inherits the 343/345 raw-lineage issue;
- **FIXED:** I removed “reported with bootstrap confidence intervals and permutation p-values,” because current Candidate B does not actually report those uncertainty values. If B restores the exact intervals/p-values from A′, the form can state them explicitly rather than merely claiming they are reported;
- **OPEN:** the checklist promises a differentiated title, but Candidate B still uses the exact workshop title;
- **OPEN external preflight:** author-list reconciliation, quota, and the accuracy of the “no external participants” human-subjects answer require coauthor confirmation and were not inferable from the repository.

The form abstract now matches current B more closely and will not reproduce the known MathJax stripping failure. It should still be updated after the paper abstract/title and label-count policy are finalized, then pasted into OpenReview and visually previewed.

## 6. Mechanical fixes applied

I did not modify any file under `paper_latex/TMLR_2026_submission/`.

1. `paper_latex/TMLR_2026/main.tex`
   - removed eight global layout-compression overrides;
   - corrected EXP46 nine-candidate and LOO values to `-0.3911 / 0.2484` and `+0.2416 / 0.4908`;
   - clarified nine-candidate primary versus eight-candidate drift-gated sensitivity.
2. `paper_latex/TMLR_2026/main.pdf`
   - rebuilt successfully with `latexmk` after the TeX changes;
   - 29 total pages; main content ends and References starts on page 11; no undefined refs/cites, fatal errors, or overfull boxes;
   - rerendered representative pages and found no clipping/overlap.
3. `experiments/21_tmlr_submission/resubmission_kit.md`
   - removed the unsupported claim that current B reports bootstrap CIs/permutation p-values;
   - verified form-safe math and no internal references.
4. `experiments/24_expanded_panel_cli/results.md` and `decision.md`
   - synchronized exact values with `pass2_full_screen_results.json`;
   - restored the nine-candidate primary table and separated the eight-candidate sensitivity;
   - replaced “adequate power” in the results bottom line with the exact n=32 registered-criterion statement.
5. `experiments/21_tmlr_submission/evidence_map.md`
   - replaced a stale “unresolved merge conflict” warning; `bug_reversal_rates.csv` is conflict-free and BAD_STRINGY is `20/24 = 0.833333...`.

## 7. Final verdict and minimum triage-survival gate

**Verdict: neither-fix-first. Use Candidate B as the only resubmission base after the following minimum fixes; do not resubmit A′.**

Minimum fix list, in order:

1. Resolve and freeze the 343-versus-345 label inclusion policy; rerun pool-derived results if 345 is adopted.
2. Remove unsupported “powered / adequate power / closes the question” wording, or add a defensible power analysis.
3. Reconcile the method promise with the negative evidence: present amortized screening as the tested proposition, not an achieved deployment capability.
4. Replace B's title with a short differentiated measurement/audit title.
5. Cut the paper and form abstracts to the same approximately 200-word story; put `n=8` and uncertainty next to the positive trio, and the exact registered `(b)` n=32 outcome next to the negative result; remove internal refs and downstream ranking.
6. Add canonical sources for the P4 rewrite and downstream VeriBench tables, and complete the three placeholder bibliography entries.
7. Obtain the required human read/coauthor sign-off, reconcile the author list and human-subjects answer, then preview the actual OpenReview landing page before submission.

**Final resubmission verdict: neither-fix-first; after the seven-item gate passes, resubmit B.**
