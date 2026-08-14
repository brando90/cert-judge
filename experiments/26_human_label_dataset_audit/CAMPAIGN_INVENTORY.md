# Campaign inventory — every human-label campaign in the repo

> Part of [`experiments/26_human_label_dataset_audit/`](README.md) — start at the README for the
> folder map. The calibration-panel deep dive is
> [`cert_judge_judgements_human_scores.md`](cert_judge_judgements_human_scores.md); the 5-rater
> pool deep dive is [`vb_judgements_human_scores.md`](vb_judgements_human_scores.md). This
> document zooms out to **all** human-label campaigns across cert-judge and veribench.
>
> It was written independently (concurrent session) and merged here so there is one folder, not two.
> Its facts were cross-checked against `cert_judge_judgements_human_scores.md`'s recomputation — they agree everywhere they
> overlap, **with one exception, corrected inline below**: the `835` usable-label figure in §2/§9 is
> a row total across 7 files, and the two `*_set_data.tsv` aggregates are concatenations of the
> participant files sitting next to them. The number of **independent** labels is **343**. See
> `cert_judge_judgements_human_scores.md` §7 and `results/PANEL_TRACE.md` §4 for the exact decomposition.
>
> Its §7 (stale filename aliases) is the *correct* root cause for the 3 dropped pairs discussed in
> `cert_judge_judgements_human_scores.md` §1 — that finding originated here.

**TLDR:** There are **three real human-label campaigns** (not one), all on the same underlying task — *25 VeriBench v1 problems × 3 agents = 75 items*, rated 0–5 for theorem-statement coverage. The big one is the **revised-protocol pool** (`experiments/human_labels/`, 835 usable labels, 5 named raters + 2 aggregate sets); the second is the **old-protocol calibration lineage** (`04_veribench_validation/data/ethan_human_scores_*.tsv`, 150 labels) that produced the famous 0.7033 and correlates with the pool at only **ρ ≈ 0.13**; the third is **Ethan's April hand-labels** (`ethan_hand_labels/`, 78 rows). A fourth thing that *looks* like data — the 30-problem named study in `18_human_judgment_study/` (= veribench `41_`) — is **fully designed but 0% collected** (every `score` cell blank). Two long-standing gaps are resolved here: the **participant↔name mapping** is recovered from git, and the **"30 problems"** figure used by exp34/exp32 is really **25 problems + 5 stale filename aliases**.

_Compiled 2026-08-11 against cert-judge `main` @ `d6947d5` and veribench `main` @ `c2da7573` (both freshly pulled; `experiments/human_labels/` is byte-identical in the two repos)._

---

## 1. The rating task (shared by all campaigns)

- **Unit:** one (gold Lean file, agent Lean file) pair. Agents are `__agent0/1/2`.
- **Scale:** integer/float **0–5**, "how well do the agent's Lean *theorem statements* cover the gold's".
- **Rubric:** `veribench/veribench_prompts/human_judgements_prompt.md` — checklist A–D (coverage / pre-post / spam / spam severity), base score 0–5, then a spam deduction of up to −2. Humans and the LLM judge use the *same* prompt, so they sit on one scale.
- **Columns:** `gold_file`, `candidate_file`, `human_score_0_5`.
- **Problem base:** 25 problems, 5 per VB v1 split.

| VB v1 split | problems rated | example |
|---|---:|---|
| `easy_set` | 5 | `1_MyAdd.lean`, `18_MyFibonacci.lean` |
| `cs_set` | 5 | `binary_search.lean`, `merge_sort.lean` |
| `humaneval_set` | 5 | `humaneval_31_is_prime.lean` |
| `realcode_set` | 5 | `0_bisect_right.lean`, `24_json_decoder.lean` |
| `security_set` (6858) | 5 | `4_unsafeCounter_safe.lean` |

25 problems × 3 agents = **75 items** is the ceiling for any single rater.

---

## 2. Campaign A — revised-protocol pool (the main asset)

**Path:** `experiments/human_labels/` (identical in veribench and cert-judge). Collected 2026-05-03 → 2026-05-12.

| File | rows | usable | problems | mean 0–5 | who |
|---|---:|---:|---:|---:|---|
| `participant1_data_correct_prompt.tsv` | 75 | 74 | 25 | 2.78 | **Ethan** (revised prompt) |
| `participant2_data_pass_1.tsv` | 75 | 75 | 25 | 2.53 | **Jolene** |
| `participant3_data_pass_1.tsv` | 75 | 44 | 25 | 2.23 | **Steven** (31 blanks) |
| `participant4_data_pass_1.tsv` | 75 | 75 | 25 | 3.87 | **Yegor** |
| `participant5_data_pass_1.tsv` | 75 | 75 | 25 | 3.13 | **unknown** — see §6 |
| `expert_harsh_set_data.tsv` | 225 | 195 | 26 | 2.55 | strict/harsh **aggregate** |
| `lenient_set_data.tsv` | 297 | 297 | 30 | 3.62 | lenient **aggregate** |
| **total** | **897** | **835** | **25 (+5 aliases)** | | 90 distinct item keys |

Usable counts are exp34's cleaner. A naive parse gives 833 — exp34's `_clean_candidate_and_score` repairs 2 malformed `expert_harsh` cells (`candidate_file` values like `…__agent1 1`). exp32/exp65's cleaner reports 837 because it treats participant1/participant3 blanks differently. The five-rater sub-pool is **343** labels, matching `22_pooled_heldout_and_noise_ceiling/REPORT.md` exactly.

- Every rater covers all 5 splits ≈ evenly (15 rows each), except Steven (missing `easy_set` + `security_set`) and the two aggregates.
- The lenient/harsh split is real and large: **3.62 vs 2.55** mean. exp62 uses exactly this as train/test (`train = lenient`, `test = expert/strict`), and the judge scores 0.70 Pearson against lenient but only 0.37 against experts.
- Reliability (from `22_pooled_heldout_and_noise_ceiling/REPORT.md`): mean pairwise inter-rater Spearman **0.42**; Spearman–Brown ceiling on the pool mean **≈ 0.87**; leave-one-rater-out human bar **0.57**. participant5 is the outlier rater (0.22–0.46 vs everyone).
- Pre-cleaned copies exist — use these rather than re-parsing the TSVs:
  - `04_veribench_validation/results_exp34_all_human_task_aggregation/human_labels_cleaned.csv` (835 rows) + `all_human_item_targets.csv` (90 items) + `all_human_task_targets.csv` (30 tasks)
  - `…_with_old_prompt/` variant (985 rows) adds Campaign B's two files
  - veribench `65_certifying_judge_veribench/new_human_labels_cleaned.csv` (837 rows) — the 7-file pool only

## 3. Campaign B — old-protocol calibration lineage

**Path:** `experiments/04_veribench_validation/data/` + `experiments/human_labels/old_prompt/`. Earlier annotation round (pre-May), different instructions.

| File | rows | problems | mean | note |
|---|---:|---:|---:|---|
| `old_prompt/participant1_data_pass_1.tsv` ≈ `data/ethan_human_scores_ORIGINAL.tsv` (78 rows) | 75 | 25 | 3.89 | Ethan pass 1 — the two copies agree on 96 % of 75 shared keys |
| `old_prompt/participant1_data_pass_2.tsv` ≡ `data/ethan_human_scores_20260425.tsv` | 75 | 25 | 3.60 | Ethan pass 2 — 100 % match |
| `data/ethan_human_scores_avg_two_passes_20260425.tsv` | 75 | 25 | 3.77 | derived average, not new labels |

Primary labels here = **150** (two passes × 75); the third file is derived.

**This is the label set behind the headline 0.7033 Pearson.** It is *not* interchangeable with Campaign A:

| comparison | Spearman | n |
|---|---:|---:|
| Campaign B (ethan avg) vs Campaign A pool mean | **+0.13** | 63 |
| same annotator, B vs own A relabel | **+0.18** | 63 |
| within Campaign A (strict set vs pool mean) | +0.96 | 78 |

Directionally the rubric moved lexical → semantic: under B the lexical negative controls score *positive* (editdist +0.20, BAD_STRINGY +0.43); against A they score *negative* (−0.57, −0.46). Any experiment that calibrates on B and tests on A is confounded — that is the documented cause of exp43's near-zero transfer result.

## 4. Campaign C — Ethan's hand labels (earliest)

**Path:** `cert-judge/experiments/ethan_hand_labels/`, committed 2026-04-07 (`3a7b75c`). Five CSVs, one per split, `GOLD, CANDIDATE, Score`:

| file | rows | problems | scores seen |
|---|---:|---:|---|
| `cs_set.csv` | 15 | 5 | 3–5 |
| `easy_set.csv` | 15 | 5 | 3–5 |
| `humaneval_set.csv` | 15 | 5 | 4–5 |
| `real_code.csv` | 18 | 5 (one problem has 6 rows) | 1–4 |
| `security_6858.csv` | 15 | 5 | 2–5 |
| **total** | **78** | 25 | markedly lenient except realcode |

## 5. Campaign D — the named study that was never filled in

**Path:** veribench `experiments/41_human_judgment_study/` ≡ cert-judge `experiments/18_human_judgment_study/` (byte-identical).

Fully specified: seed 41, 30 problems `hjs_01…hjs_30` (easy 10, cs 5, humaneval 5, realcode 5, security 5), 2 batches of 15, 3 agents (`claude_code_opus47`, `codex_gpt54_xhigh`, `leanstral`), side-by-side render dirs under `sxs/`, short + long rater prompts, 3 calibration problems, and per-rater sheets for **ethan, jolene, kirill, steven, yegor, brando**.

**Collected: nothing.** All 24 sheets (5 × 90-row, 12 × 45-row batch sheets, 6 × 9-row calibration) have **0 filled `score` cells**. `selection_audit.md` says the file manifest is CLEAN, so this is ready to run — it is the obvious place to add labels, and it is the only design that would give per-rater *named* labels on a fresh 30-problem sample with the current SOTA agents.

## 6. Recovered: the participant ↔ name mapping

`62_arxiv_llm_judge_tuning_heldout_alignment_bm/00_WHAT_ETHAN_DID_prior_judge_work.md` §6 flags this as an open **⚠️ GAP**. It is recoverable from veribench commit **`6169a29f` "Remove names from datasets" (2026-05-05)**, which is a pure `R100` rename:

```
old_prompt/ethans_data_pass_1.tsv     -> old_prompt/participant1_data_pass_1.tsv
old_prompt/ethans_data_pass_2.tsv     -> old_prompt/participant1_data_pass_2.tsv
ethans_data_correct_prompt.tsv        -> participant1_data_correct_prompt.tsv
jolene_data_pass_1.tsv                -> participant2_data_pass_1.tsv
steven_data_pass_1.tsv                -> participant3_data_pass_1.tsv
yegor_data_pass_1.tsv                 -> participant4_data_pass_1.tsv
```

Confirmed independently by exact score agreement against the un-anonymized copies still sitting in `04_veribench_validation/data/`: participant1 ≡ `ethans_data_same_prompt.tsv` 100 %/75, participant2 ≡ `jolene_data_pass_1.tsv` 100 %/75, participant3 ≡ `steven_data_pass_1.tsv` 81 %/74 (differs only where p3 is blank).

**`participant5` remains unidentified** — it was added *after* the anonymization commit (`6bd4db97` "Added 5th participant", author Ethan Hersch), so no pre-rename name exists in git. Candidates named in the exp62 thread: Kirill, Simon, Andrew. Ask Ethan; this is a one-line answer that unblocks the exp62 by-rater split.

## 7. Gotcha: "30 problems" is really 25 + 5 stale aliases

`exp34`/`exp32` report 30 tasks / 90 items. Five of those "problems" are **old filenames for problems that were renumbered** in the dataset and no longer exist on disk:

| stale name (old_prompt + lenient era) | current name | split |
|---|---|---|
| `1_bisect_left.lean` | `2_bisect_left.lean` | realcode |
| `2_heappush.lean` | `4_heappush.lean` | realcode |
| `3_heappop.lean` | `5_heappop.lean` | realcode |
| `4_json_decoder.lean` | `24_json_decoder.lean` | realcode |
| `0_unsafeMultiply_safe.lean` | `1_unsafeMultiply_safe.lean` | security |

`lenient_set_data.tsv` contains **both** names (hence 30 problems / 297 rows); `expert_harsh_set_data.tsv` contains one alias (hence 26). Consequence: **task-level aggregation over "30 tasks" double-counts 5 problems**, and realcode/security get ~1.8× their intended weight. Any per-task isotonic fit or task-split CV built on the 30-task list should be re-run on a de-aliased 25-task list.

## 8. Derived / downstream files (not new labels — don't double-count)

- `04_veribench_validation/data/super_human_pass3_avg_five_raters.tsv` — 44 rows, five-rater average
- `04_veribench_validation/results_security/human_judgments.csv` — 15 rows, security only, `human_mean`
- `results_exp36_super_human_pass3_min5/super_human_item_targets.csv` — min-5-rater target
- veribench `archive/data/human_judgements_evaluations/veribench_01_14_2026_ICML/bm_human_judgements.json` — **1 item**, Brando, a different weighted sub-score rubric (`theorem_equivalence` / `implementations` / `contract_pre_post_corr_thm` / `all_tests`). Prototype only.

## 9. Bottom line

| campaign | usable labels | raters | problems | status |
|---|---:|---:|---:|---|
| A — revised pool | **343** independent (835 rows) ¹ | 5 named + 2 aggregates | 25 | ✅ the asset; ceiling ρ ≈ 0.87 |
| B — old protocol | 150 | 1 (Ethan × 2 passes) | 25 | ⚠️ legacy; ρ ≈ 0.13 vs A — do not mix |
| C — Ethan hand labels | 78 | 1 | 25 | ℹ️ earliest, coarse |
| D — study 41/18 | **0** | 6 designed | 30 | 🚧 built, never run |
| E — bm rubric JSON | 1 | 1 (Brando) | 1 | prototype |

¹ **Corrected on merge.** `835` is the row total across the pool's 7 files, but `expert_harsh_set_data.tsv` (193 rows) = participants 1+2+3 and `lenient_set_data.tsv` (297 rows) = participants 4+5 + `old_prompt/pass_1` + a 72-row subset of `ethan_20260425` — both decompose exactly, with zero unexplained rows (`results/PANEL_TRACE.md` §4). The aggregates contain **no ratings not already in the participant files**, so `835` counts most raters ~3×. Use **343** as the sample size; it is also what the paper reports and what `exp43_frozen_tivar_heldout.py` consumes. (§2 and §8 of this document already say as much; only the §9 bottom line needed fixing.)

**572 distinct human 0–5 judgments** (343 pool + 150 old-protocol + 78 hand-labels + 1 prototype), over **25 distinct VB v1 problems × 3 agents**, of which only Campaign A (343) should be treated as the current-protocol ground truth. Counting the derived aggregate files as well gives the 1,064 row total — a description of the directory, not of the evidence.

## Next actions

1. Ask Ethan who `participant5` is → unblocks the exp62 by-rater train/val/test split.
2. De-alias the 5 stale filenames and re-run any task-level split (§7).
3. Decide whether to actually run study 41/18 — it is the only path to more labels, and its sheets are ready.

---

> ✅ **Numbering collision resolved.** This document originally lived in a separate
> `experiments/21_human_label_dataset_audit/`, which collided with `experiments/21_tmlr_submission/`.
> It now lives here in `experiments/26_human_label_dataset_audit/` alongside the panel deep-dive (now `cert_judge_judgements_human_scores.md`) and the
> runnable audit scripts — one folder, one number.
