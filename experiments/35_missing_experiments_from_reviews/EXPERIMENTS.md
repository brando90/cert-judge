# Experiment 35 — the experiments the reviews say are missing, each with a ready prompt

**TLDR:** Twelve gaps distilled from four OpenReview rounds (33a AI4Math, 33d MATH-AI, 33e TMLR, DL4C pending) plus today's audit, ranked by how much each would move an ICLR decision per unit of cost. Four are **zero-inference** (recompute from frozen outputs, run today), five need **subscription-CLI judge calls** (quote first; $0 API), three need **new human labels** (Brando decides; the only way to get a real held-out test). Every prompt below is written for a coding agent, is CLI-only (Hard Rule 9), starts with a call quote, records exact model IDs, and registers its own experiment folder. Nothing here edits the paper; results feed experiment 34's successor pass.

Reviewer IDs refer to `experiments/33a_ai4math_reviews/complaints.md` (A26-*), `33d_mathai_reviews/complaints.md` (N25-*), and the preserved ledger `experiments/archive/31_final_iclr_paper_writing/notes.md`.

Common rules for every prompt (prepend when dispatching): read `CLAUDE.md` and `~/agents-config/INDEX_RULES.md`; register the experiment in `experiments/archive/layout.json` (`active`) and `experiments/README.md`; write `results.md` at launch and keep it live; CLI-only inference (`codex exec` / `claude -p`), scrub `*_API_KEY` from child environments, never read `~/keys/*`; write the exact call quote to `CKPT.md` before the first call; record the CLI-requested model ID in every result file; commit with explicit pathspecs; never touch `paper_latex/` — deliver `REPORT.md` with drafted paper sentences instead.

---

## Tier 0 — zero inference (run today; each is a few hours of agent time)

### 35.1 `TI_var` weight and normalization sensitivity — A26-uMVy-8
- **Gap:** reviewers ask whether the equal-weight geometric form matters. We only compare v1/v2/GM/`TI_var`.
- **Design:** sweep weight triples on the simplex (step 0.05) over (`C_f`, 1−VarCorr, 1−VarScore); for each, recompute the judge-level Spearman between the index and human agreement (avg/pass1/pass2) for the Codex, Claude Opus, and Qwen3-Coder panels; also try the alternative normalizations of the variance penalties already coded in `py_src/cert_judge/hsj_scoring.py`. Report min/median/max ρ, the fraction of the simplex where ρ ≥ 0.7, and where equal weights sit.
- **Inputs:** `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/` (Codex), the Opus and Qwen panels under `experiments/archive/13_qwen_replication_exp16_exp19/results/` and the Opus results referenced by the paper's Figure 2 data (find the JSON the figure's `\addplot` coordinates came from; cite it).
- **Unlocks:** one sentence in §5.3 + appendix table; closes uMVy-8.
- **Prompt:** "Experiment 35.1. Compute how sensitive `TI_var` is to its three weights and to the variance-penalty normalization, using only frozen outputs (paths above). Reproduce the paper's equal-weight values first (0.833/0.905/0.738 for Codex avg/pass1/pass2 within 1e-6; otherwise stop and report). Then sweep the simplex at step 0.05, and the normalization variants in `hsj_scoring.py`. Output `results/weight_sensitivity.csv`, a heatmap per family, and `REPORT.md` with the min/median/max and the share of the simplex with ρ ≥ 0.7. Draft one sentence for §5.3 and one appendix caption."

### 35.2 Leave-one-family-out and leave-one-configuration-out robustness — A26-uMVy-6, DeJF-2
- **Gap:** eight configurations per family is small; reviewers want to know the association is not carried by one family or one control.
- **Design:** pooled association over the 24 (family, configuration) points; recompute leaving each family out and leaving each configuration out; report the distribution and the worst case; bootstrap CIs per subset (10k draws).
- **Inputs:** same as 35.1.
- **Unlocks:** one sentence in §5.3; closes uMVy-6/DeJF-2 beyond the existing CIs.
- **Prompt:** "Experiment 35.2. From the frozen per-configuration `TI_var` and human-agreement values of the three families, compute pooled, leave-one-family-out, and leave-one-configuration-out Spearman associations with 10k bootstrap CIs. Reproduce the per-family headline values first. Output `results/lofo.csv`, `results/loco.csv`, `REPORT.md`, and one drafted sentence for §5.3."

### 35.3 Adaptive-overfitting bound for reusing one labeled panel — the intro `TODO(internal-review)` (O3)
- **Gap:** "why can't a new judge on the same domain reuse the labels?" The honest answer needs a number: how fast does selection on one fixed 72-pair panel inflate the apparent judge–human correlation?
- **Design:** simulation with the panel's own label statistics (72 items, inter-pass agreement as noise model): draw K candidate judges with a null or weak true association, select the best on the panel, report the optimistic bias of the selected judge's correlation as a function of K (1…64). Compare with screening by properties (which does not consult the labels).
- **Inputs:** the 72 labels (both passes) in `experiments/archive/04_veribench_validation/data/`; no judge calls.
- **Unlocks:** a quantitative sentence in §1 or §6 replacing the TODO; cites Dwork et al. 2015 (verify the bib entry).
- **Prompt:** "Experiment 35.3. Quantify adaptive overfitting when many judge configurations are selected on the same 72-pair panel: simulate K∈{1,2,4,…,64} candidate judges under a null and a weak-true-association model calibrated to the panel's label noise (inter-pass Spearman 0.249), select the best on the panel, and report the expected inflation of the selected correlation. Output `results/reusable_panel_bias.csv`, a figure, `REPORT.md`, and a drafted sentence for §6 with the number."

### 35.4 Build (do not score) the missing property probes — A26-c7ev-5, c7ev-11, c7ev-12, N25-ivJs-1
- **Gap:** the suite does not test vacuity, weakening, over-constraint, formatting-only edits, or bloat.
- **Design (construction only, fail-closed Lean elaboration as in `py_src/cert_judge/probe_validation.py`):** (a) vacuity: replace each theorem statement with `True`; (b) weakening: drop one conjunct of a postcondition / weaken a bound; (c) over-constraint: add an unsatisfiable or overly strong hypothesis; (d) formatting-only: whitespace, comment, and layout edits; (e) bloat: add redundant theorems implied by existing ones. Expected direction is known by construction: (a)–(c) must lower the score, (d)–(e) must leave it unchanged. Every probe must elaborate; invalid constructions are excluded before scoring.
- **Inputs:** the 24 validation-panel golds and the VeriBench golds under `data/veribench_dataset/lean_src/veribench`; the Lean toolchain pinned in the repo.
- **Unlocks:** 35.6 (scoring); until then, §6 can say the probes exist and are unscored.
- **Prompt:** "Experiment 35.4. Extend the probe builder with five new ladders (vacuity, weakening, over-constraint, formatting-only, bloat) following `probe_validation.py`'s fail-closed pattern. Emit a manifest with sha256 per probe, elaboration status, and the expected score direction. No judge calls. Report counts per ladder and per split in `REPORT.md`."

## Tier 1 — subscription-CLI judge calls ($0 API; quote first; regular-tier model `gpt-5.6-terra` unless Brando says otherwise)

### 35.5 Rescore canonicalized text (the real alpha-renaming fix) — A26-uMVy-7, c7ev-4
- **Gap:** §5.2 reports a *proxy* (0.250 → 0.070) and says "a real fix must rescore the canonicalized text".
- **Design:** canonicalize binder names (deterministic α-normal form via a Lean-aware script) for original and alpha-renamed artifacts; rescore both with the three certified prompts (P1/P4/P8) on the same model; report P4 invariance before/after and the effect on `TI_var`.
- **Quote shape:** 24 files × 2 variants × 3 prompts × 3 repeats ≈ 432 calls (+ the 96 existing identity cells for comparison).
- **Unlocks:** turns a proxy into a result in §5.2.
- **Prompt:** "Experiment 35.5. Implement a canonicalization pass for Lean binder names, verify each canonicalized file elaborates, then rescore original vs canonicalized vs alpha-renamed artifacts with prompts P1/P4/P8 via `codex exec -m gpt-5.6-terra` (quote: ~432 calls; write it to `CKPT.md` first). Report P4 invariance and `TI_var` before/after, with item-bootstrap CIs, and draft the §5.2 replacement paragraph."

### 35.6 Score the new probes from 35.4 on the certified panel — c7ev-5/11/12
- **Design:** run the five ladders through the eight Codex-family configurations (or the three prompts on the current Codex model if `gpt-5.3-codex` is unavailable — record the ID); compute per-ladder monotonicity/invariance; test whether `TI_var` rank order changes when the new properties are added as extra factors.
- **Quote shape:** ladders × files × repeats — expect 2–4k calls; run repeat-major so partial layers are complete.
- **Unlocks:** replaces "untested" in §6 with numbers; a new appendix table; possibly a fifth property.
- **Prompt:** "Experiment 35.6. Score the probes built in 35.4 with the certified prompt configurations via the subscription CLI (repeat-major order, cached per cell, quote in `CKPT.md` first). Report, per ladder, whether scores move in the expected direction, which judges fail, and how adding each property changes the judge ranking under `TI_var`. Draft the §6 sentences that replace 'untested'."

### 35.7 Certify the currently served judges (re-run P1–P4 on today's models) — practical relevance
- **Gap:** `gpt-5.3-codex` is no longer served; the paper's certified panel is a snapshot. Reviewers will ask whether the protocol still works on current models.
- **Design:** run the frozen P1–P4 suite (exp16 contract) for `gpt-5.6-terra` and one Claude model via `claude -p`, compute `TI_var`, and the judge–human association on the 72 pairs; the exp32 archive already has a runner and a quote (864 calls per configuration).
- **Unlocks:** a "protocol applied to a new judge" paragraph — the paper's own use case demonstrated end-to-end.
- **Prompt:** "Experiment 35.7. Reuse `experiments/archive/32_veribench_ranking_certified_judge/compute_property_suite.py` and the exp16 ladders to certify `gpt-5.6-terra|P1_BASELINE` (and one Claude configuration via `claude -p`): P1–P4, `TI_var`, and Spearman with the 72-pair labels. Quote first (~864 calls per configuration). Report where each new judge lands on the paper's Figure 2 and draft the paragraph."

### 35.8 Gaming resistance — E6 disclosure ("resistance to gaming remains untested")
- **Design:** let a coding agent optimize candidate specifications against the judge's score (score feedback only, no labels) for 24 problems; measure how much the judge score rises versus how the property suite and the human labels react; the question is whether `TI_var` or P1–P4 flag the gamed judge/candidates.
- **Quote shape:** agent loop ≈ 24 × 10 iterations × 1 judge call + property re-scoring; ~1k calls.
- **Prompt:** "Experiment 35.8. Build a judge-gaming loop: an agent edits candidate Lean specs to maximize the P1 judge score under elaboration constraints. Report the score gain, whether the gamed candidates score higher than their golds, and whether P2/P3 ladders built from the gamed candidates expose the judge. CLI-only; quote first."

### 35.9 Other proof assistants pilot — A26-DeJF-7
- **Design:** port P1–P3 ladders to Dafny or Verus using the vericoding benchmark's specs (`bursuc2025…`), 20 items, one judge; report whether the same prompts and index transfer.
- **Quote shape:** 20 × (identity + 5 bug + 5 spec levels) × 3 repeats ≈ 660 calls.
- **Prompt:** "Experiment 35.9. Pilot the property protocol on 20 Dafny (or Verus) items from the vericoding benchmark: build fail-closed ladders with the assistant's checker, score with one Codex prompt via CLI, and report P1–P3 and a provisional `TI_var`. Quote first; draft the §6 sentence that replaces 'untested elsewhere'."

## Tier 2 — new human labels (Brando decides; these are the only path to a held-out test)

### 35.10 Locked held-out test with independent raters under one frozen rubric — A26-uMVy-5, c7ev-1, c7ev-3, DeJF-1, OPEN_QUESTIONS #4
- **Design:** pre-register (properties, `TI_var`, judge panel, analysis) before labels exist; 2–3 independent raters rate a fresh set of ≥100 candidate–gold pairs under the *panel* rubric (not the pool rubric); report inter-rater agreement and the judge-level association on the held-out labels.
- **Cost:** human time (~100 pairs × 3 raters); judge calls only for pairs not already scored.
- **Prompt (for the pre-registration + tooling, before any labeling):** "Experiment 35.10. Write the pre-registration for a locked held-out test of the property-certification protocol: frozen definitions, hypotheses, decision rules, sample size from the panel's effect sizes, and a rater interface that records per-item rationale. No labels are collected by the agent; deliver the protocol and the tooling."

### 35.11 Re-rate the existing 72 pairs with two more raters — A26-DeJF-3, c7ev-11 ("number of annotators for stable targets")
- **Design:** the cheapest way to bound label noise: two additional raters on the same 72 pairs under the same rubric; report inter-rater reliability (Krippendorff's α) and how the headline associations change when the target is the rater mean.
- **Cost:** 2 raters × 72 pairs.

### 35.12 Recover the panel rubric text and an annotator report — today's audit
- **Design:** Brando asks Ethan for the two rubric texts he used and whether size/spam were penalized; record verbatim as an annotator report under `experiments/human_labels/`; the paper then states what the rubric instructed instead of inferring it.
- **Cost:** one email.

## Suggested order
35.1 → 35.2 → 35.3 (today, zero inference) → 35.4 (build) → 35.5 and 35.7 (quotes to Brando) → 35.6 → 35.8/35.9 (only if time) ; 35.12 now; 35.10/35.11 are Brando's call and are the only way to answer "does it generalize".
