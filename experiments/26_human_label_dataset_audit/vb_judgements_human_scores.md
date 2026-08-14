# The VeriBench human-judgment data (5-rater pool) — and how it compares to the cert-judge calibration panel

> Part of [`experiments/26_human_label_dataset_audit/`](README.md). Companion to
> [`cert_judge_judgements_human_scores.md`](cert_judge_judgements_human_scores.md), which covers
> the calibration panel. This document covers the **other** human dataset — the multi-rater
> VeriBench pool — and answers directly: *is it larger, and is it higher quality, than the data
> the paper's headline numbers rest on?*

**TLDR: Larger — yes (343 independent labels vs 150; 5 raters vs 1). Higher quality as a
measurement instrument — yes by every reliability metric (multi-rater redundancy ≈ 4.4
ratings/item; Spearman–Brown ceiling ≈ 0.87 vs the panel's 0.249 single-rater rubric
stability). But it is NOT a drop-in replacement:** it was annotated under a **revised rubric**
and correlates with the calibration labels at only **ρ ≈ 0.13**, so it measures a *different
criterion*. Every published bridge number rests on the calibration panel; using the pool as the
criterion requires re-bridging judges against it from scratch (attempted in exp 23/24 —
outcomes: *underpowered* at n=14, then *no label-free property signal* at n=32).

---

## 1. What the pool is

Collected 2026-05-03 → 2026-05-12 under the **revised** rubric prompt
(`veribench_prompts/human_judgements_prompt.md`: checklist A–D, 0–5 base score, spam deduction
up to −2). Humans and the LLM judge use the same prompt, so scores share a scale. The files
live in `experiments/human_labels/` and are **byte-identical between the veribench and
cert-judge repos** — "VeriBench human data" and "the 5-rater pool in cert-judge" are the same
files, not two datasets.

| file | usable labels | problems | mean (0–5) | rater |
| --- | ---: | ---: | ---: | --- |
| `participant1_data_correct_prompt.tsv` | 74 | 25 | 2.78 | Ethan (revised prompt) |
| `participant2_data_pass_1.tsv` | 75 | 25 | 2.53 | Jolene |
| `participant3_data_pass_1.tsv` | 44 | 15 | 2.23 | Steven (31 blanks) |
| `participant4_data_pass_1.tsv` | 75 | 25 | 3.87 | Yegor |
| `participant5_data_pass_1.tsv` | 75 | 25 | 3.13 | **unidentified** (added post-anonymization; candidates: Kirill / Simon / Andrew — ask Ethan) |
| **independent total** | **343** | 26 (25 + 1 alias) | | 5 raters, 78 distinct pairs, ≈ 4.4 ratings/pair |

Rating unit and item base are identical to the calibration panel: (gold `.lean`, agent `.lean`)
pairs over 25 VeriBench-v1 problems (5 per split: easy / cs / humaneval / realcode / security)
× 3 agent generations (`__agent0/1/2`).

The participant↔name mapping was recovered from veribench commit `6169a29f` ("Remove names from
datasets", a pure rename) and verified by exact score agreement against the un-anonymized
copies — see `CAMPAIGN_INVENTORY.md` §6.

## 2. Size: pool vs calibration panel

| | calibration panel (cert-judge headline data) | VeriBench 5-rater pool |
| --- | --- | --- |
| raters | **1** (Ethan) | **5** |
| views/passes | 2 rubric-strictness readings | 1 pass each |
| rubric | old prompt | **revised** prompt |
| independent labels | 150 (75 × 2); 144 analyzed | **343** |
| distinct pairs | 75 (72 analyzed) | **78** |
| ratings per pair | 2 (same person) | **≈ 4.4 (different people)** |
| problems | 25 (24 analyzed) | 26 (25 + 1 stale alias) |
| collected | pre-May 2026 (two rounds) | 2026-05-03 → 05-12 |
| role in the paper | criterion behind ALL headline bridge numbers | intended held-out test (returned null → traced to rubric drift) |

Overlap: **63 pairs** appear in both.

## 3. Quality: the pool is the better measurement instrument

Numbers from `experiments/22_pooled_heldout_and_noise_ceiling/REPORT.md` (verified against the
cached analysis in this audit):

| reliability metric | calibration panel | 5-rater pool |
| --- | ---: | ---: |
| inter-rater agreement | — (impossible: one rater) | mean pairwise Spearman **0.42** (range 0.05–0.87) |
| within-source stability | rubric stability Spearman **0.249** (same person, two rubrics) | within-campaign stable; same annotator agrees with pool mean at **ρ = 0.90** under the revised protocol |
| reliability of the mean target | — | Spearman–Brown **0.76–0.78** → judge-vs-pool-mean ceiling **≈ 0.87–0.88** |
| known outlier | — | participant5 (0.22–0.46 vs everyone else) |

Interpretation: a judge correlating with the **pool mean** can in principle reach ρ ≈ 0.87; a
judge correlating with any single calibration view is bounded near the panel's 0.249–0.375
self-agreement band. As a criterion in the $\mathrm{TI}_{m_1}$ sense, the pool mean is the
better-measured target. **Label noise does not explain the held-out null** — that was checked
and ruled out.

## 4. Why it still cannot replace the calibration panel (criterion drift)

The two datasets were annotated under **different rubrics**, and that difference dominates
everything else:

| comparison | Spearman | n |
| --- | ---: | ---: |
| calibration labels (avg view) vs pool mean | **≈ 0.13** | 63 |
| same annotator (Ethan), old-rubric labels vs own revised-rubric relabels | 0.18 | 63 |
| within pool: strict-set aggregate vs pool mean | 0.96 | 78 |

One person re-rating the same files under a reworded rubric produces nearly uncorrelated
scores — a bigger effect than any between-rater disagreement inside the pool. Directionally
the revised rubric moved lexical → semantic: the lexical negative-control judges (editdist,
BAD_STRINGY) correlate *positively* with the old labels (+0.20, +0.43) but *negatively* with
the pool (−0.57, −0.46).

Consequences, in ICLR 2027 notation:

- The pool is a different $H$; $\mathrm{TI}_{m_1}$ measured against it is a **different
  criterion**, not a held-out estimate of the same one. A bridge calibrated on criterion A and
  tested on criterion B with $\mathrm{Corr}(A,B) \approx 0.13$ fails at any judge count —
  which is exactly what exp43's frozen held-out test showed, and why the paper reports
  "criterion drift precedes power."
- Re-anchoring on the pool as the criterion was attempted: exp 23 (`23_reanchored_calibration`,
  n=14 → registered outcome *underpowered*) and exp 24 (`24_expanded_panel_cli`, n=32 →
  registered verdict *no label-free property signal*). Both are honest pre-registered outcomes,
  not failures of the data.
- **One rubric and one rater pool per claim** — the paper's stated protocol requirement — is
  the operational lesson of this section.

⚠️ **Do not confuse** the pool's stacked aggregate files with the panel's strict/lenient views:

| file | what it actually is |
| --- | --- |
| `human_labels/expert_harsh_set_data.tsv` (193 usable rows) | concatenation of participants 1+2+3 (pool) |
| `human_labels/lenient_set_data.tsv` (297 rows) | concatenation of participants 4+5 **+ two old-rubric panel passes** — it mixes rubrics |
| panel **strict** view | `04_veribench_validation/data/ethan_human_scores_20260425.tsv` |
| panel **lenient** view | `04_veribench_validation/data/ethan_human_scores_ORIGINAL.tsv` |

Both aggregates decompose exactly into the files sitting next to them (zero unexplained rows;
`results/PANEL_TRACE.md` §4). Treating either as one rater's scores double-counts; summing all
files gives 835–983 rows, but only **343** labels are independent.

## 5. Pre-cleaned copies (use these, don't re-parse)

- `04_veribench_validation/results_exp34_all_human_task_aggregation/human_labels_cleaned.csv`
  (835 rows) + `all_human_item_targets.csv` (90 items) + `all_human_task_targets.csv` (30 tasks)
- `04_veribench_validation/data/super_human_pass3_avg_five_raters.tsv` (44 rows, 5-rater mean)
- veribench repo: `65_certifying_judge_veribench/new_human_labels_cleaned.csv` (837 rows)

⚠️ Task-level aggregations built on the "30 tasks" list double-count: 5 of the 30 "problems"
are stale pre-renumbering aliases of the other 25 (`CAMPAIGN_INVENTORY.md` §7). De-alias to 25
before any per-task fit or split.

## 6. The upgrade path: study 41/18 (designed, never run)

`experiments/18_human_judgment_study/` (≡ veribench `41_`) is a fully specified, seeded
(seed 41) study: 30 fresh problems, 3 current-generation agents (`claude_code_opus47`,
`codex_gpt54_xhigh`, `leanstral`), per-rater sheets for 6 named raters (ethan, jolene, kirill,
steven, yegor, brando), calibration items, side-by-side renders. **Collected: 0 cells.** It is
the only ready-made path to labels that would be simultaneously (a) multi-rater, (b)
single-rubric, (c) on current SOTA agents — i.e., a criterion with the pool's reliability and
none of the drift confound. It also serves the memo's Route-B need (human ratings on perturbed
ladder items) if extended.

## 7. Bottom line

The VeriBench 5-rater pool is the **larger and more reliable** human-judgment dataset (343
labels, 5 raters, ceiling ≈ 0.87), and the right criterion for any *future* trustworthiness
claim. The cert-judge calibration panel (150 labels, 1 rater, ceiling ≈ 0.25) is the **smaller
and weaker** dataset that all *current* published numbers rest on. They are ρ ≈ 0.13 apart
because the rubric changed between campaigns — so the choice is not "use the better one" but
"pick one criterion per claim and re-bridge against it." The cheapest clean fix is running
study 41/18.
