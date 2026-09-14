---
title: "CertJudge Revision Memo: Notation, Claims, Data, and the ICLR 2027 Plan"
date: "13 August 2026"
---

**Purpose.** This memo is the source of truth for revising *Certifying the Judge* into an ICLR
2027 submission. It fixes the final notation and terminology, states which claims the paper may
make and which it must retract, records the audited facts about the human-annotation data, and
allocates content to the 9-page main text versus the appendix. Claude Code should implement the
paper edits directly from this document (companion prompt: `agent-prompt-iclr2027-port.md`).
The full working archive (derivations, handwritten-page transcriptions, reconciliation log)
remains in `certifying-the-judge-COMPLETE.*` for provenance; nothing there overrides this memo.

**Venue facts (verified 13 Aug 2026).** ICLR 2027: abstract deadline **Sep 18, 2026 AoE**
(abstracts must be genuine; used for reviewer bidding); paper deadline **Sep 25, 2026 AoE**;
submissions via OpenReview. Main text **9 pages** at submission (10 at rebuttal/camera-ready),
strictly enforced; references uncounted; unlimited appendix after references, which reviewers
are not required to read. Double-blind — identity leaks in main text *or* supplementary are
desk-rejected; cite our own prior versions in third person. A short **AI-use statement is
required** (uncounted); reproducibility and ethics statements are recommended (uncounted).
Style files: `https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip`. Authors on
3+ submissions owe 6 reviews each.

# 1 Terminology and notation (final)

We separate three objects that earlier drafts collapsed into one scalar. The role labels follow
the validity-centered evaluation framework of Salaudeen et al. (2025), which the paper already
cites.

| Object | Role | Notation | Needs human labels |
|---|---|---|---|
| Trustworthiness (the predicate we care about) | construct | $\mathrm{TW}_m(aj)$ | — |
| Trust Index (the construct's measured scalar on a specified panel and item set) | criterion | $\mathrm{TI}_m(aj)$ | yes |
| Proxy Trust Index (label-free behavioral aggregate) | instrument / surrogate | $\mathrm{PTI}_p(aj)$ | no |

Subscripts follow the $L_p$ convention: the capital letter names the family, the subscript
selects the variant. $m$ indexes the **matching criterion** on the target side; $p \subseteq
\{1,\dots,K\}$ indexes the **property set** on the proxy side and is **locked before any bridge
analysis** (choosing $p$ to maximize the bridge correlation is model selection over $2^K - 1$
subsets and reintroduces the selection circularity).

**The $m$-ladder.** $m_0$: distributional match, $P_\theta(s \mid \cdot, aj) \approx P_H(s
\mid \cdot, h_j)$. $m_1$: correlational, $\mathrm{Corr}(S_{aj}, S_{h_j})$ high over items.
$m_2$: $m_1$ plus stability, $\mathrm{std}(\hat s_{aj})$ low. We write $\mathrm{TW}_2 \equiv
\mathrm{TW}_{m_2}$; $m_2$ is the working target.

**Core definitions.**

$$\mathrm{TW}_m(aj):\quad \forall a \in L_A,\ \text{if } aj \approx_\Pi h_j \text{ then }
\big\lVert P_\theta(s \mid x, y^*, \hat y{=}a(x), aj)\ \approx_m\ P_H(s \mid x, y^*, \hat
y{=}a(x), h_j) \big\rVert_m \ \text{small,}$$

where $aj \approx_\Pi h_j$ is the persona precondition (the judge is conditioned toward the
rater persona; without it the definition is unsatisfiable over a heterogeneous pool). Items are
what the $m_1$/$m_2$ criteria integrate over — they are never universally quantified in a
correlational statement.

$$\mathrm{TI}_{m_1}(aj) \;=\; \mathrm{Corr}_{i \in \text{panel}}\big(\hat s_{aj}(i),\,
s^*_{h_j}(i)\big) \qquad\qquad
\mathrm{PTI}_p(aj) \;=\; \mathrm{GM}\big(P_k(aj) : k \in p\big)$$

$$\mathrm{TI}_{2'}(aj) \;=\; \Big(\mathrm{clip}_{[0,1]}\big(\mathrm{Corr}(D_{\hat S_{aj}},
D_{\hat S^*_H})\big)\cdot\big(1 - \mathrm{STD}[D_{\hat S_{aj}}]\big)\Big)^{1/2}$$

The stability term is judge-side (it is $P_4$, the label-free conjunct), orientation-flipped,
and the correlation is clipped before entering the geometric mean. Correlation is computed only
over **paired** observations — the same candidate scored by both sides — with repeats
aggregated first ($K_a$ agent generations, $K_{aj}$ judge repeats, and $K_{h}$ human passes
are three distinct indices that never align pairwise).

**Effective parameters and the amortization asymmetry.** The gold criterion is only measurable
on the annotated subset $b' \subseteq b$; the proxy runs on the full benchmark:

$$\mathrm{PTI}(b,\, L_A,\, aj,\, P)\ \approx\ \mathrm{TI}_{2'}(b',\, L_A,\, aj,\, H).$$

This exposes four generalization axes, all of which the paper must name: held-out **judges**
(the primary claim), new **agents**, new **benchmarks**, and within-benchmark **item-level
extrapolation** $b' \to b$ (the bridge is validated on 72 items and the proxy is used on
$157 \times 3$ candidates).

**Rename ledger** (apply in one pass across text, figures, captions, and code identifiers):

| Old | New |
|---|---|
| $\mathrm{TI}_{\mathrm{var}}$, "trust index", "cert index" | $\mathrm{PTI}_p$ |
| $\mathrm{Align}$, "human alignment/Spearman" (per judge) | $\mathrm{TI}_{m_1}$ |
| "certification protocol", CERTIFY | **amortized judge validation**, SCREEN |
| pass1 / pass2 | **strict / lenient** (the pass names are inverted vs. chronology; see §4) |
| "reflexivity" (lay contexts) | **identity** (the paper's existing term) |

**Bans.** "Trust Index" never appears in the title or public branding (title collision:
arXiv:2507.16028, Rug et al. 2025); $\mathrm{TI}_m$ survives as internal math. No `CI` or `CC`
abbreviations. No hat notation: a hat is earned by a fitted score-mapping function
$f_{\mathrm{cal}}: \mathbf P \mapsto \widehat{\mathrm{TI}}_{m_1}$, which is premature below
roughly 40 judge configurations; the raw aggregate never receives one.

# 2 Claims the paper may make, and the retractions it must reflect

**2.1 No "sound rejection by construction" at the ratified target.** Under $\mathrm{TW}_2$,
correlation is an aggregate: a judge can carry high $\mathrm{TI}_{m_1}$ while exhibiting a
local bug-ladder reversal or one rename sensitivity, so $P_k$ low does not logically imply
$\mathrm{TI}_{m_1}$ low. Necessity of $P_1$–$P_3$ holds only for pointwise trustworthiness.
Two repair routes, both acceptable:

- **Route A (definitional).** $\mathrm{TW}(aj) := [\mathrm{TI}_{m_1} \ge \tau_A] \wedge
  \bigwedge_k [P_k \ge \tau_k]$; a probe violation then rejects by definition, and "properties
  predict alignment" is reported as a separate empirical result.
- **Route B (conditional falsification lemma).** If $\lvert J(z) - H(z)\rvert \le \varepsilon$
  pointwise and humans satisfy a margin $H(x) - H(Tx) \ge \delta$ on a transformation $T$, then
  $J(x) - J(Tx) \ge \delta - 2\varepsilon$; an observed reversal exceeding $2\varepsilon -
  \delta$ refutes $\varepsilon$-alignment, and human-invariant $T$ gives $\lvert J(x) -
  J(Tx)\rvert \le 2\varepsilon$. The paper sentence: *under stated metamorphic-validity and
  margin assumptions, sufficiently large probe violations falsify pointwise
  $\varepsilon$-alignment.* The margins $\delta$ are currently assumed, not measured — a small
  human collection on perturbed ladder items (a few dozen ratings) turns the lemma into a
  grounded theorem and simultaneously tests whether ALPHA renaming is human-invariant, which is
  the standing $P_4$ failure mode.

**2.2 Acceptance is licensed, never free.** High $\mathrm{PTI}_p$ "certifies" (scare quotes
deliberate) only because the bridge correlation with $\mathrm{TI}_{m_1}$ was demonstrated, and
only within the validated judge population. The abstract must state the screen semantics
explicitly; the prior desk rejection traces to an abstract that claimed prediction while the
experiments reported a screen that found no qualifying signal.

**2.3 The geometric mean is a soft AND.** $\mathrm{GM}(1,1,1,0.5) \approx 0.84$: the aggregate
collapses only at exactly zero. GM remains the right ranking summary (zero-annihilating,
imbalance-penalizing), but the hard screening decision uses per-property confidence bounds —
FAIL-SCREEN when $\mathrm{UCB}(\hat P_k) < \tau_k$ for any required $k$ — and the auditable
object is always the property vector $\mathbf P(aj)$, with $\min_k P_k$ reported when
worst-case conformance matters.

**2.4 One conjunct of $\mathrm{TW}_2$ is directly estimable label-free** — the stability
conjunct, via $P_4$ (an estimate with a CI, not a verification). Never "half is free."
Consequently $P_4$ leaves the primary bridge aggregate: the headline bridge is
$\mathrm{PTI}_{\{1,2,3\}}$ versus $\mathrm{TI}_{m_1}$, the reported object is the profile
$\big(\mathrm{PTI}_{\{1,2,3\}},\ \hat P_4 \pm \mathrm{CI},\ \text{violation flags}\big)$, and
the full GM survives only as a single-number deployment convenience. Stability must never
appear on both sides of the bridge.

**2.5 Labels are de-indexed, not eliminated.** The honest cost claim:
$$C_{\mathrm{amortized}} \;=\; \underbrace{\lvert\Pi\rvert\, n\, c_{\mathrm{human}}}_{\text{persona conditioning}}
\;+\; \underbrace{\lvert AJ_{\mathrm{val}}\rvert\, \lvert I\rvert\, c_{\mathrm{human}}}_{\text{bridge, once}}
\;+\; \underbrace{\lvert AJ\rvert\, \lvert A\rvert\, \lvert Q\rvert\, c_{\mathrm{API}}}_{\text{per screened judge}}$$
— $O(1)$ in agents and screened judges, $O(\lvert\Pi\rvert)$ in personas. Approved phrasings:
"no new human labels per screened judge," "human-anchored," "human-label amortized."

**2.6 Three-claim structure.** Claim A (definitional): $aj$ is $\mathrm{TW}_2$-trustworthy —
needs humans. Claim B (proxy): $\mathrm{PTI}_p(aj) \ge \tau$ — label-free. Claim C (bridge):
$\mathrm{PTI}_p \approx_C \mathrm{TI}_{m_1}$ over held-out judges — established once. At
$m_2$, failing B is evidence against A with strength set by C; refutation requires Route A or
Route B. Passing B never establishes A except through C, population-scoped.

# 3 Two jobs, two validations

The instrument does two jobs that require different evidence. The paper studies both and never
conflates their metrics.

| | Screen (gate before humans) | Surrogate (predict the criterion) |
|---|---|---|
| Claim | catches unacceptable judges cheaply | $\mathrm{PTI}$ tracks $\mathrm{TI}_{m_1}$ numerically |
| Decision | FAIL-SCREEN / PASS-SCREEN / DEFER | predicted score with interval |
| Metrics | false-pass rate, false-reject rate, defer rate, coverage, **human ratings saved at a fixed false-pass tolerance** | held-out rank correlation, MAE/score-scale agreement, prediction intervals, transfer across families/prompts/personas/agents |

Decision utility is the headline scalable-oversight number: *at false-pass tolerance
$\alpha$, the screen avoids X% of human validations*, with sensitivity to shift and a stated
re-validation horizon. For power-limited analyses we pre-register a smallest effect size of
interest (SESOI; candidate $\rho_0 = 0.5$, the level below which screening saves less than it
costs) and run equivalence tests, so an inconclusive interval is reported as inconclusive and a
bounded null becomes a finding. A learned score-mapping function is deferred until roughly 40 judge
configurations exist; at $n \approx 8$–13 the honest object is the pre-specified aggregate
with its raw held-out correlation.

**Data pipeline: what feeds $\mathrm{PTI}$, what feeds $\mathrm{TI}$, and where the bridge
correlation lives.** Three datasets with distinct index sets, and one type rule: *items pair
inside each side; judges pair across sides.*

1. **Probe-response tensor (PTI's data; label-free).**
   $D_Q(aj)[f, T, r, k] = \hat s_{aj}(T_r(x_f), g_f)$ over base artifacts $f \in F$ (the
   published run: $|F| = 184$), transform families $T$ (identity-self; RENAME / REORDER /
   STYLE / ALPHA; bug ladder L0–L4; cumulative spec-removal ladder), rung $r$, and repeats
   $k \le K_{aj} = 3$. This tensor has **no human axis**: the supervision that labels provide
   on the gold side is provided here by construction — the ladder order is known because we
   built it. The suite $Q$ is scripted once from existing candidates and golds, cached, and
   reused across judges; per new judge the cost is inference only (order
   $|F| \times (\text{variants}{+}\text{rungs}) \times K_{aj}$ API calls, zero annotation).
2. **Panel scores (TI's judge side).** $D_{\hat S_{aj}}\vert_{b'}$: the judge's
   repeat-aggregated scores on the 72 aligned pairs — required only for judges in the bridge
   set, never for newly screened judges.
3. **Human tensor.** $D_{\hat S^*_H}$: 72 items $\times$ {strict, lenient, avg}; fixed,
   collected once.

Estimators collapse (1) to the property vector — e.g. $P_2 = \frac{1}{|F|}\sum_f
\mathrm{clip}\big(\frac{1-\rho_f}{2}, 0, 1\big)$ with $\rho_f$ the Spearman correlation of (rung,
median-over-repeats score); $P_4$ alone consumes the un-aggregated repeat axis — and (2)+(3)
collapse to $\mathrm{TI}_{m_1}(aj) = \mathrm{Spearman}_{i \in 72}(\text{median}_k\,\hat
s_{aj}(i),\, s^*_H(i))$ per label view. **The bridge dataset is judge-indexed:**
$\{(\mathrm{PTI}_{\{1,2,3\}}(aj_j),\ \mathrm{TI}_{m_1}(aj_j))\}_{j=1}^{n}$, one point per
judge configuration ($n = 8$–13 today, target $\approx 40$), with
$\hat\rho = \mathrm{Spearman}_j$ bootstrapped over judges. $D_Q$ and $D_{\hat S^*_H}$ share no
index and are never correlated row-wise — humans never rated perturbed variants, by design.
This is why the outer power constraint counts judges, not items, and why the fix is more judge
configurations.

# 4 Data: audited ground truth the paper must state

A repository audit (`cert-judge@main`, 13 Aug 2026; write-up in
`experiments/archive/26_human_label_dataset_audit/`, tidy source of truth
`results/aligned_panel_n75.tsv`) established the following. The revised paper states these
facts plainly.

| Fact | Audited value |
|---|---|
| Annotated panel | **75 rated candidate–gold pairs = 25 problems $\times$ 3 agent generations; 72 analyzed** (24 problems). The submitted text's "24 $\times$ 3 = 75" never multiplies out |
| The dropped 3 | `0_unsafeMultiply_safe` rows carry a pre-renumbering filename, miss the gold lookup, and are skipped (`missing_gold`); they drop rather than add. The three 1.5-scores in the score-dispersion figure are an unrelated duplication (`4_json_decoder`, scored 1 and 2, averaged) |
| Raters | **One annotator, two rubric-strictness rounds** — not two raters. The published pass names are inverted relative to chronology (sha-verified); rename to strict/lenient. No per-row rater field exists anywhere in the label data |
| Label totals | **150 rated (75 $\times$ 2), 144 analyzed (72 $\times$ 2)**, 0–5 rubric |
| Inter-round agreement | Spearman 0.249, Pearson 0.375, QWK 0.372 on the 72. With one rater this is **rubric stability**, not inter-rater agreement: the criterion itself moves this much under a strictness change alone |
| Item selection | Stratified 5-per-split, **hand-picked** within split, frozen 2026-04-07 (commit `3a7b75c`), no script, no seed, not compile-filtered. Estimand: alignment on a fixed curated panel — say so. A seeded selection template (study 41, seed 41, $n=30$) exists but was never run; it is the upgrade path if a probability sample is demanded |
| Agents on the slice | codex / claude / llama (`AGENT_MAP`); the full candidate pool is 471 files $= 157$ problems $\times 3$ (problem granularity; 857 is the theorem count) |
| The 5-rater pool | A **separate population**: 343 labels over 78 pairs, 5 raters, revised rubric. It correlates with the original human panel at only $\rho \approx 0.13$ |
| Number hygiene | The draft's MAE/MSE (0.778/1.139) uses first-of-duplicates; the cached mean-of-duplicates values are 0.7708/1.1215 — pick one convention and regenerate. The "approximately 72-75" hedge is determinate: 72 |

**Interpretation the paper needs (one paragraph each).** (i) With $\lvert H\rvert = 1$, the
panel criterion is one person's judgment under a stated rubric — legitimate as a *scoped*
criterion via the $h_j = (\text{person}, \pi)$ decomposition, but it must be said, and the
rubric is part of the criterion's identity. (ii) **Criterion drift, then power**: the held-out
null is documented in-repo as caused by testing against a different rater pool under a revised
rubric ($\rho \approx 0.13$ with the original-rubric criterion) — a bridge fitted on criterion
A and tested on criterion B with $\mathrm{Corr}(A,B) \approx 0.13$ fails at any judge count.
Power remains binding on top: the outer correlation's $n$ is the number of judge
configurations (8–13 today; CI roughly $\pm 0.5$), and the fix is more judges (~40, API-priced),
not more items. The inner correlation runs over 72 items (CI roughly $\pm 0.2$); report both
CIs. (iii) All reported correlations to date are **validation-set numbers** — the same labels
tuned the index form, aggregation, and thresholds — and are labeled as development-set evidence;
held-out claims come only from the locked protocol.

# 5 Packaging for ICLR 2027

**Title shortlist** (no "Trust Index"; graded /10):

1. *The Surrogate Gap: When Do Label-Free Behavioral Tests Track Human Agreement for LLM
   Judges?* — 9
2. *Do Behavioral Stress Tests Predict Human Agreement? Scalable Validation of LLM Judges for
   Formal Code* — 9
3. *JudgeProbe: Amortizing Human Validation of LLM Judges with Falsifiable Behavioral Tests* —
   8.5
4. *Screen, Then Validate: Scalable Oversight of LLM Judges* — 8
5. *Falsifiable Behavioral Properties for Amortized Validation of LLM Judges* — 7.5 (safest)

("Necessary but Not Sufficient" is withdrawn until Route B is proven or Route A adopted.)

**Contributions (survives positive, negative, heterogeneous, or family-restricted outcomes).**
(1) We distinguish scoped judge trustworthiness $\mathrm{TW}_m$ (construct), its human-grounded
criterion $\mathrm{TI}_m$ measured on a specified panel, and the automated behavioral
instrument $\mathbf P(aj)$. (2) We introduce a reusable suite of falsifiable behavioral probes
for LLM judges of formal-code artifacts with pre-registered ladders and estimators. (3) We
evaluate whether $\mathrm{PTI}_{\{1,2,3\}}$ is a valid surrogate for $\mathrm{TI}_{m_1}$ on
held-out judge configurations, separating property violations (screen) from prediction
(surrogate), with SESOI-anchored equivalence analysis where power is limited. (4) We measure
the screen's decision utility: human validations avoided at a fixed false-pass tolerance.

**One-sentence thesis.** We test whether automatically measured behavioral properties can
predict a scoped human-alignment criterion for unseen LLM judges, thereby amortizing — not
eliminating — the cost of human validation.

**Nine-page allocation.**

| Main text (9 pp) | Appendix (unlimited; reviewers not obliged to read) |
|---|---|
| Problem + amortization framing; construct/criterion/instrument; definitions ($m$-ladder compressed to one table); properties and estimators; screen-vs-surrogate protocol; bridge results with CIs and validation/test labeling; decision-utility result; criterion-drift and single-rater disclosure; limitations | Full $m$-ladder derivation; Route B lemma proof and $\delta$-measurement design; index-formulation comparisons (v1/v2/GM/$\mathrm{PTI}$); per-property diagnostics and failure modes (ALPHA analysis, reversal rates); audit details and counts reconciliation; prompt templates; threshold-selection sweeps; expanded judge-panel analyses; pre-registration documents |

**Compliance items.** Genuine abstract by Sep 18 (bidding uses it). Anonymize: strip
acknowledgments and identifying repo links (use an anonymized repo or zip), cite the workshop
version in third person. Include the required AI-use statement and a reproducibility statement
(both uncounted). Ethics statement only if warranted.

# 6 Action items

1. **72-vs-75, Option B (recommended):** rename the three stale label rows to
   `1_unsafeMultiply_safe` and regenerate the affected experiment outputs, making $n = 75$
   literally true — near-zero marginal cost since a full single-artifact regeneration of all
   headline numbers is already committed. Fallback Option A: reword to "75 rated from 25
   problems; 72 analyzed (stale filename)."
2. **Rename strict/lenient** everywhere (paper, code, cached results).
3. **Commit the audit folder** (currently local-only) so its pointers resolve for the team.
4. **Re-run the audit scripts before editing numbers in the manuscript**; agent-reported
   figures get the same verification discipline as any others.
5. **Expand judge configurations toward ~40** for outer-bridge power; pre-register the SESOI
   and the locked held-out protocol (single rubric, single pool per claim).
6. **Run the $\delta$-measurement collection** (human ratings on perturbed ladder items) to
   ground Route B and adjudicate ALPHA human-invariance.
7. Open notational threads: the "IS" benchmark-subset label is unidentified; the prompt
   dimension $k_x$ is deliberately deferred; one subscript-discipline pass over the manuscript
   ($m$ on the gold side, $p$ on the proxy side).
