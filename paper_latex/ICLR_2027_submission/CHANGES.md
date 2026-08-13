# CHANGES — ICLR 2027 port (`TMLR_2026_resubmission/main.tex` → `ICLR_2027_submission/main.tex`)

TLDR: full change log for the ICLR 2027 port per `docs/certjudge-revision-memo.md` (the memo) and
`docs/agent-prompt-iclr2027-port.md` (the prompt); every inserted/changed number is labeled
DOCUMENTED (traced to a repo artifact), DERIVED (computed, command shown), or UNKNOWN (none inserted).

Compiled: `tectonic --keep-logs --outdir _build main.tex` → 0 errors, 0 overfull boxes, 23 pages
total; **countable main text ends on page 9** (Conclusion ends p9; uncounted Reproducibility/LLM-use
statements begin p9–10; references pp10–12; appendix p13–23).

## 0. Pre-flight verification (prompt ground rule 4)

Re-ran `experiments/26_human_label_dataset_audit/audit_human_labels.py`, `reconcile_paper_numbers.py`,
and `trace_analyzed_panel.py` (pure stdlib) on this branch before editing any number.
Outcome vs memo §4: **MATCH on every fact** — 75 rated / 72 analyzed (25/24 problems), one annotator
× two rubric rounds, 150/144 labels, inter-round Spearman 0.2486 / Pearson 0.3747 / Kendall 0.2214 /
QWK 0.3718 (cached exp18 run, via regenerated `results/PANEL_TRACE.md`), MAE 0.7708 / MSE 1.1215
under mean-of-duplicates, held-out pool 343/78/5, cross-protocol drift 0.123 (≈0.13), selection
frozen 2026-04-07 commit `3a7b75c` with no script/seed.

## 1. Template (prompt step 0)

- Official style files downloaded from `media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip`
  and unzipped here; stock `iclr2027_conference.tex` built once (73 KB PDF) before content work.
- `refs.bib` + `figures/` copied from `TMLR_2026_resubmission/` (TMLR dir untouched).
- `\PassOptionsToPackage{dvipsnames}{xcolor}` before the style file (option-clash fix).

## 2. Rename ledger (memo §1; prompt step 1) — applied in one pass

| Old | New | Where |
|---|---|---|
| `TI_var` / "trust index" / "cert index" | `\PTIvar` (variance-aware variant of `\PTI_p`); family `\PTI_p = GM(P_k : k∈p)` defined once in §3 | text, math, tikz axis labels, table headers, captions |
| per-judge "human alignment"/"human Spearman" | `\TIm{1}` | everywhere |
| "certification protocol" / CERTIFY | "amortized judge validation" / SCREEN (FAIL-SCREEN / PASS-SCREEN / DEFER) | §1, §4, §5 |
| pass1 / pass2 | **strict / lenient** (pass1=strict, pass2=lenient; sha-verified inversion vs chronology stated in §6.1 + App. A; **no temporal language anywhere**) | all tables/prose |
| "reflexivity" | "identity" | (no occurrences remained) |

- "Trust Index" does not appear in title, abstract, or any heading (memo ban; title-collision).
  Lowercase "trust index" survives only as internal-math naming: the §3 notation table naming what
  `TI_m` denotes, and the Fig. 1 caption's "label-free proxy trust index" gloss of `PTI` —
  memo: "`TI_m` survives as internal math."
- No `CI`/`CC` abbreviations as names; "CI" appears only as "95% confidence interval (CI)" in
  standard statistics usage.
- Repo slug `cert-judge` unaffected (not referenced in the paper).

## 3. Claims surgery (memo §2; prompt step 2)

- **Abstract rewritten to screen semantics**: probes are a cheap screen; acceptance licensed only by
  the demonstrated bridge, population-scoped. Every abstract claim cross-checked by grep against the
  results sections; the two negatives (drift ρ≈0.13; registered-negative 32-config screen) are in the
  abstract.
- **"Sound rejection by construction" removed** (0 occurrences). Route A (definitional TW :=
  [TI≥τ_A] ∧ ⋀[P_k≥τ_k]) + Route B (conditional-falsification) inserted in §3; Route B lemma +
  one-line proof in Appendix B; main text carries only the licensed sentence ("under stated
  metamorphic-validity and margin assumptions, sufficiently large probe violations falsify pointwise
  ε-alignment") + "δ assumed, not measured".
- **GM = soft AND**: GM(1,1,1,0.5) ≈ 0.84 stated (DERIVED: 0.5^(1/4) = 0.8409); hard screen decision
  = per-property UCB thresholds; auditable object = property vector; `min_k P_k` for worst-case.
- **One-conjunct statement** replaces any "half is free": P4 estimates the stability conjunct with a
  CI; P4 leaves the primary bridge aggregate; headline bridge object going forward = `PTI_{1,2,3}`
  vs `TI_{m1}`, reported profile = (PTI_{1,2,3}, P4±CI, violation flags); stability never on both
  sides. **Note:** the *measured* numbers in this paper remain the documented `PTIvar` aggregates
  (see §6 below) — the text says so explicitly and a footnote-level sentence explains why
  PTIvar-vs-TI_{m1} does not violate the both-sides rule (criterion here is m1, correlation-only).
- **Cost claim**: C_amortized decomposition (memo §2.5) as Eq. (5); "de-indexed, not eliminated";
  approved phrasings only.
- **Validation-set labeling**: every correlation from the calibration labels is labeled
  validation-set/calibration evidence (§6 header, figure caption, §7 opening, Limitations).
- **Three-claim structure** (A/B/C) in §3; four generalization axes named incl. item-level b′→b
  (72 validated / 157×3 scored).
- Two-jobs table (screen vs surrogate) + SESOI ρ₀=0.5 pre-registration + "calibration map deferred
  until ~40 configs" in §5. Decision utility defined as the headline oversight quantity with **no
  value claimed** (UNKNOWN by design; registered as next analysis — see OPEN_QUESTIONS).

## 4. Data-facts corrections (memo §4; prompt step 3)

- §6.1 + Appendix A: **Option A wording** — "75 rated candidate–gold pairs = 25 problems × 3
  generations; 72 pairs (24 problems) enter all analyses (pre-renumbering filename misses the gold
  lookup)". The old "24 problems × 3 = 75" sentence is gone. The two unrelated "3"s (dropped
  `0_unsafeMultiply_safe` rows vs duplicated `4_json_decoder` lenient rows averaged to 1.5) are
  separated explicitly in App. A and the histogram caption.
- One-rater disclosure: single annotator × two rubric-strictness rounds; 150 rated / 144 analyzed;
  inter-round agreement framed as **rubric stability**, not inter-rater agreement (§6.1, §7, App. A).
- Selection disclosure: stratified 5-per-subset, hand-picked, frozen before judge experiments, no
  script/seed, not compile-filtered; estimand = fixed curated panel; seeded study-41 template named
  as upgrade path (§6.1, App. A).
- Criterion-drift paragraph: 5-rater 343-label pool = separate population, revised rubric, ρ≈0.13;
  one rubric + one pool per claim; "criterion drift first, power second" (§7).
- b′→b extrapolation sentence added (§3, Limitations).
- **MAE/MSE fixed to mean-of-duplicates**: 0.771 / 1.122 on n=72 (was 0.778 / 1.139 mixed-convention);
  table now single-convention and says so (App. E, Table `tab:app-human-human-ceiling`).
- "~72–75 overlapping rows" hedge resolved to **72** everywhere the analyzed set is meant
  (incl. the old line-1325 sentence, now simply "the 72 analyzed rows").

## 5. ICLR compliance (prompt step 4)

- Main text ≤ 9 pages ✓ (Conclusion ends p9). References uncounted; appendix after references.
- Double-blind: `\author{Anonymous authors}`; no acknowledgments; no grant numbers; no repo URLs in
  the paper; supplementary referred to as "anonymized archive". Grep results (source + bib):
  no {author names, lab, university, GitHub handles} outside standard third-person bib entries
  (citing published work by its authors is standard and allowed; the paper never claims ownership).
  Workshop version cited third person in §2 via `anonymous2025formaljudge` (added after light-QA
  review flagged it missing — the first committed version of this port omitted it); VeriBench cited
  third person via `miranda2026veribench`.
- Required LLM-use statement added (`\section*{The Use of Large Language Models}`, uncounted);
  Reproducibility statement added; Ethics statement left as a commented stub (per prompt).
- Title = memo shortlist option 1 (working title per prompt): *The Surrogate Gap: When Do
  Label-Free Behavioral Tests Track Human Agreement for LLM Judges?*
- Auto line numbers active (submission mode; `\iclrfinalcopy` commented).

## 6. Number provenance ledger

**DOCUMENTED** (repo artifact, path):
- Bridge 0.833 avg — `experiments/04_veribench_validation/results_exp28_varaware_codex_avg/summary.json`
  (`rho_TI_vs_human = 0.8333`); 0.905 strict / 0.738 lenient + Opus row (0.810/0.595/0.643) + Qwen
  row (0.476/0.905/0.905) — TMLR draft Table `tab:tivar_cross_model_results` + tikz coordinates
  (generator: `experiments/04_veribench_validation/make_fig2_tivar_cross_model.py`).
- Bootstrap CIs [0.24,1.00]/[0.41,1.00]/[0.11,1.00], perm p=0.017/0.005/0.045, seed 42 — TMLR draft
  App. (exp16 robust suite). Pearson 0.774/0.661/0.837; Kendall 0.571/0.571/0.643 — draft §5.3.
- Index comparison v1/v2/GM/PTIvar table — draft `tab:cross_model_index_compare_avg`.
- Cross-view fits (0.881/0.810; 0.857/0.786) — draft `tab:cross_pass_generalization`
  (pass1→strict, pass2→lenient mapping applied).
- Per-property (P3 0.747 p=0.043, Pearson 0.744 p=0.048; P2 0.714 p=0.056, Pearson 0.636 p=0.037) —
  draft §5.4 + `figures/exp17_final_robust/`.
- Sanity run (|F|=184, repeats 3; P2 r=−0.687 ρ=−0.808 weak 52.2%; P3 r=−0.892 ρ=−0.899 weak 89.1%)
  — draft Fig. caption (codex_api_gpt53_r3_20260418_230027 package).
- P4 invariance (RENAME .936/.005, REORDER .849/.029, STYLE .982/.001, ALPHA .399/.096) — draft
  `tab:codex_invariance_variants`.
- Threshold sweep (flip/pass rates; t=0.85; ρ_bug=−0.790) — draft `tab:exp13_threshold_sweep`.
- 13-judge panel (0.769/0.764/0.753) — draft Fig. caption (exp25 package).
- Downstream VeriBench table (0.470/0.615/0.477/0.588 + per-subset) — draft
  `tab:theorem_quality_table_split`.
- VeriBench composition (857 theorems; 387/278/68/112/12 over 56/41/10/28/5) — draft §4.1.
- Held-out: 343 labels / 78 pairs / 5 raters; 63 shared; ρ≈0.13; ceiling ≈0.87; re-label 0.90;
  screen 1 (14 configs, underpowered); screen 2 (32 configs, |ρ|=0.39 Holm p=0.25, LOO 0.24 perm
  p=0.49) — draft §sec:val-vs-test; drift also re-derived (0.123) by `trace_analyzed_panel.py`.
- Inter-round Spearman 0.249 (CI [−0.015,0.489]), Pearson 0.375 (CI [0.076,0.604]), Kendall 0.221,
  QWK 0.372 (CI [0.073,0.581]) — cached exp18 reliability run, re-verified via
  `experiments/26_human_label_dataset_audit/results/PANEL_TRACE.md` (4/4 MATCH).
- Best single-judge Spearman (avg 0.480, strict 0.559); naive blind baseline table; Leanstral
  re-aggregation table; alpha-ablation deltas (0.810→0.690 strict, 0.810→0.714 lenient,
  0.881→0.786 avg — trend-v1); reversal rates (0.00/0.167/0.833/0.667–0.750/1.00);
  canonicalization 0.250→0.070 (median 64%); BAD_STRINGY ≈0.45 with 12.5% weak mono;
  r9/median rerun table — all from the TMLR draft's corresponding tables/paragraphs (cached exp
  packages under `experiments/04_veribench_validation/results_*`).
- Panel agents codex/claude/llama — `experiments/04_veribench_validation/run_veribench_validation.py:29`
  (`AGENT_MAP`).
- Selection freeze commit `3a7b75c` (2026-04-07) — `git log`, `experiments/ethan_hand_labels/`.
- Study-41 seeded template (seed 41, n=30) — veribench
  `experiments/41_human_judgment_study/expt2_human_ratings/selection.json` + `selection_audit.md`.

**DERIVED** (command shown; all pure stdlib):
- 75/72, 25/24, 150/144, per-subset 5×5×3 — `python3 audit_human_labels.py` +
  direct TSV recount (this session; also §0 above).
- Inter-round on n=72: Spearman 0.2486, Pearson 0.3747, Kendall 0.2214, MAE 0.7708, MSE 1.1215 —
  direct recompute from `results/aligned_panel_n75.tsv` filtering
  `problem != 0_unsafeMultiply_safe` (matches cached run to 4 decimals).
- Histogram counts (strict {1:1,2:7,3:18,4:44,5:5}; lenient {1.5:3,2:6,3:10,4:33,5:23}) — Counter
  over the tidy panel (matches the draft's embedded tikz coordinates exactly).
- GM(1,1,1,0.5)=0.5^0.25≈0.841.
- 471 candidate files = 157 problems × 3 — `ls data/generated_agents/*.lean | wc -l` + name parse.

**UNKNOWN → removed rather than guessed:**
- Draft's JS divergence 0.081 bits and KL 0.415 bits (inter-pass): not reproducible from the raw
  files under any duplicate/binning convention tried (plug-in KL is infinite — disjoint support
  cells; my JS on n=72 = 0.1035 bits ≠ 0.081). Both rows **dropped** from the ceiling table
  (the dispersion story is carried by MAE/MSE + histogram). If wanted back, regenerate from the
  exp18 script with its exact smoothing and re-insert.
- Decision-utility number: intentionally not claimed (framework defined; measurement registered).

## 7. Figures needing regeneration (embedded old labels — NOT silently regenerated)

| Figure (used in paper) | Embedded legacy text | Generating script |
|---|---|---|
| `figures/pull_fig.png` (Fig. 1) | "TI_var" | original overview graphic (source asset; no script in repo — flagged) |
| `figures/exp16_final_robust/fig_cert_vs_human_scatter_{pass1,pass2,avg}.png` | "cert index", "pass1/pass2" | `experiments/04_veribench_validation/exp16_multi_judge_human_sets.py` (`_make_plots`) |
| `figures/exp16_final_robust/fig_human_corr_by_judge_and_labelset.png` | "pass1/pass2" | same as above |
| `figures/exp17_final_robust/fig_property_vs_human_bars_{pass1,pass2,avg}.png` | "pass1/pass2" | exp17 property-vs-human script (results package `results_exp17_*`) |
| `figures/fig7_trend_update_baseline_vs_geom_13judge_avg.png` | "trust index (geometric)" | `experiments/04_veribench_validation/exp25_plot_baseline_vs_geometric*.py` |
| `figures/fig_main_monotonicity_lowvar_exp19.png` + exp19 failure plots | judge-id labels only (OK); axis wording fine | `exp19_replot_low_variance.py` |

Captions in the ICLR draft explicitly note the legacy labels where a figure with old text is shown
(Fig. 1 caption; Appendix E preamble), so the submitted draft is internally consistent even before
regeneration.

## 8. Anonymization checklist results

- [x] `\author` anonymous; no `\thanks`, no acknowledgments section, no grant numbers.
- [x] Grep source for `brando|miranda|koyejo|stanford|hersch|jolene|steven|yegor|kirill|github.com`:
      0 hits in `main.tex` outside bib-entry author lists of cited published works.
- [x] Workshop version cited third person via `anonymous2025formaljudge`; VeriBench via
      `miranda2026veribench` (third person).
- [x] No repository or Overleaf URLs in the paper; supplementary described as anonymized archive.
- [x] Line numbers on (submission mode); `\iclrfinalcopy` commented out.
- [ ] Supplementary zip itself not yet assembled (see OPEN_QUESTIONS #7).

## 9. Structural moves (memo §5 allocation)

Moved out of main text → appendix: threshold-sweep table (App. G), downstream VeriBench table
(App. H), early Sonnet protocol plots (App. I), index formulas + Leanstral control (App. C),
full bridge diagnostics/figures (App. E), related-work long tail + formal-verification context
(App. L), Rice/specification-relativity (App. K), prompts (App. J).
New in main text: three-objects table, m-ladder, TI_2′/PTI definitions, three-claim structure,
data-pipeline/type-rule paragraph, cost equation, two-jobs table, SESOI, SCREEN semantics.
New in appendix: audited-facts reconciliation (App. A), Route-B lemma + proof + δ-measurement
design (App. B), pre-registration summaries (App. M).
