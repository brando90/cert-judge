# Experiment 26 — What the human-judgment dataset actually is

> **This folder holds two documents.** This `README.md` answers *"what are `n=75`, `pass1`, `pass2`
> in the paper?"* and recomputes every published number. [`CAMPAIGN_INVENTORY.md`](CAMPAIGN_INVENTORY.md)
> zooms out to **all** human-label campaigns in cert-judge + veribench (who rated what, which study
> was never run, the stale-filename catalogue). They were written by two concurrent sessions and
> merged into one folder; §7 records how they relate and the one number that needed reconciling.
>
> **Numbering:** authored as `21_`, but `21_tmlr_submission` already owns that number upstream, so
> this is `26_`. See §8 for what `20_`–`25_` are.

**TLDR:** The paper's page-4 sentence (`n = 75` aligned pairs, one annotator, two rubric strictness
levels) describes a **label file**, not the panel any result was computed on. The label files hold
**75 rated pairs over 25 problems**; every published judge-alignment and inter-pass number was
computed on **72 pairs over 24 problems**, because one problem's gold Lean file is missing from the
repo and gets skipped. `pass1` and `pass2` are the *same annotator* rating the *same 75 pairs twice*
under two rubric strictness levels — and their names are inverted relative to chronology.

---

## 1. Direct answer to the question

### What is `n = 75`?

`75` is the number of **(candidate `.lean`, gold `.lean`) pairs** in the human-label TSV — **25
problems × 3 agent generations**. It is *not* 75 annotators, 75 problems, or 75 judge scores.

| | value | where |
| --- | ---: | --- |
| problems (distinct gold files) | 25 | `results/aligned_panel_n75.tsv` |
| agent generations per problem | 3 (`agent0`, `agent1`, `agent2`) | same |
| rated pairs = 25 × 3 | **75** | same |
| **pairs actually analyzed in every published result** | **72** | `results_exp16_final_robust/summary.json` |

The gap is a **stale filename, not missing data**. The annotator rated a 25th problem under the name
`0_unsafeMultiply_safe`, which the dataset later renumbered to `1_unsafeMultiply_safe`. The gold
lookup misses, and EXP16 logs it explicitly:

```
# experiments/04_veribench_validation/results_exp16_final_robust/skipped_pairs.csv
0_unsafeMultiply_safe.lean,0_unsafeMultiply_safe__agent0.lean,missing_gold
0_unsafeMultiply_safe.lean,0_unsafeMultiply_safe__agent1.lean,missing_gold
0_unsafeMultiply_safe.lean,0_unsafeMultiply_safe__agent2.lean,missing_gold
```

No judge can score a pair whose gold key does not resolve, so all three drop out and every run
reports `n_union_rows = 72`, `n_human_rows_pass1/pass2/avg = 72`.

The artifacts themselves are fine — only the key is stale:

| filename | matches in repo | resolves to |
| --- | ---: | --- |
| `0_unsafeMultiply_safe.lean` | 0 | **absent (stale name)** |
| `1_unsafeMultiply_safe.lean` | 2 | `data/veribench_dataset/lean_src/veribench/security_6858/safe/…` |

> **This is why `24 problems × 3 generations` and `n=75` appear in the same sentence on page 4 and
> don't multiply out.** `24 × 3 = 72` is the analyzed panel; `75` is the file row count. Both numbers
> are real, they just describe different things.

**This is fixable.** Renaming those 3 label rows to `1_unsafeMultiply_safe` restores the full
25-problem / 75-pair panel and makes the paper's `n=75` true. Four more problems (`1_bisect_left`,
`2_heappush`, `3_heappop`, `4_json_decoder`) carry the same class of stale name and survive only
because the older gold snapshot still holds their pre-rename filenames — so this is one instance of a
broader label/dataset drift, catalogued in the sibling audit (§7).

### What are `pass1` and `pass2`?

**One annotator (participant 1 / Ethan) rated the same pairs twice under two different rubric
strictness levels.** They are not two people and not two disjoint data splits — they are two
*label views* of one panel, which is why the paper reports `pass1`, `pass2`, and `avg` side by side.

| paper name | file the pipeline reads | rubric | mean score | character |
| --- | --- | --- | ---: | --- |
| `pass1` | `experiments/04_veribench_validation/data/ethan_human_scores_20260425.tsv` | strict | **3.60** | harsher |
| `pass2` | `experiments/04_veribench_validation/data/ethan_human_scores_ORIGINAL.tsv` | loose | **3.91** | more lenient |
| `avg`   | `experiments/04_veribench_validation/data/ethan_human_scores_avg_two_passes_20260425.tsv` | — | 3.77 | mean of the two |

The `avg` file reproduces `mean(pass1, pass2)` on **73 of 75** pairs. The two exceptions are
`0_unsafeMultiply_safe__agent1` and `__agent2`, which carry `5.0` where the mean of `(4, 5)` is `4.5`
— the same broken problem again. Over the panel, `mean((pass1+pass2)/2) = 3.757`; the file's own mean
is `3.770` purely because of those two rows.

**The naming is inverted relative to chronology.** By content hash:

- paper `pass1` is byte-identical (`sha256[:12] = 1e9e4c3fc72a`) to
  `experiments/human_labels/old_prompt/participant1_data_pass_2.tsv` — the annotator's *second* pass,
  re-rated on 2026-04-25.
- paper `pass2` is the annotator's *first* pass (`ethan_human_scores_ORIGINAL`), matching
  `old_prompt/participant1_data_pass_1.tsv` at Spearman `1.000`.

So **paper `pass1` = annotator pass 2**, and **paper `pass2` = annotator pass 1**. Read `pass1`/`pass2`
as "strictness level 1 / 2", never as "first / second in time". File mtimes corroborate:
`ethan_human_scores_ORIGINAL.tsv` (paper `pass2`) is dated May 1, `ethan_human_scores_20260425.tsv`
(paper `pass1`) May 17.

### How much do the two passes agree?

Barely. On the 72 analyzed pairs: Spearman `0.249`, Pearson `0.375`, Kendall `0.221`, QWK `0.372`.
One person, same artifacts, two rubrics → **moderate-at-best self-agreement**. That is the effective
ceiling for any judge–human correlation on this panel, and the paper is right to report all three
label views rather than one.

---

## 2. The complete dataset, in one table

Everything on disk, recomputed by `audit_human_labels.py` (full detail in `results/AUDIT.md`):

| file | rows | unique pairs | problems | what it is |
| --- | ---: | ---: | ---: | --- |
| `04_veribench_validation/data/ethan_human_scores_20260425.tsv` | 75 | 75 | 25 | **paper `pass1`** (strict) |
| `04_veribench_validation/data/ethan_human_scores_ORIGINAL.tsv` | 78 | 75 | 25 | **paper `pass2`** (lenient); 3 duplicated rows |
| `04_veribench_validation/data/ethan_human_scores_avg_two_passes_20260425.tsv` | 75 | 75 | 25 | **paper `avg`** |
| `human_labels/participant1_data_correct_prompt.tsv` | 74 | 74 | 25 | Ethan under the **revised** rubric prompt |
| `human_labels/participant2_data_pass_1.tsv` | 75 | 75 | 25 | Jolene (= `data/jolene_data_pass_1.tsv`) |
| `human_labels/participant3_data_pass_1.tsv` | 44 | 44 | 15 | superset of `steven_data_pass_1` (30 identical rows) + 14 more; **31 blank cells** |
| `human_labels/participant4_data_pass_1.tsv` | 75 | 75 | 25 | rater 4 |
| `human_labels/participant5_data_pass_1.tsv` | 75 | 75 | 25 | rater 5 |
| `human_labels/old_prompt/participant1_data_pass_1.tsv` | 75 | 75 | 25 | = `ethan_ORIGINAL` (deduped) |
| `human_labels/old_prompt/participant1_data_pass_2.tsv` | 75 | 75 | 25 | = `ethan_20260425`, byte-identical |
| `human_labels/expert_harsh_set_data.tsv` | 193 | 78 | 26 | **derived**: concat of participants 1–3 |
| `human_labels/lenient_set_data.tsv` | 297 | 90 | 30 | **derived**: concat of 4 rater views |
| `04_veribench_validation/data/steven_data_pass_1.tsv` | 30 | 30 | 10 | subset of participant 3 |
| `04_veribench_validation/data/super_human_pass3_avg_five_raters.tsv` | 44 | 44 | 15 | derived 5-rater mean |

**Row counts above are numeric cells, not file lines.** Several files are only partially collected —
blank `human_score_0_5` cells are silently dropped by every loader in the repo:

| file | file rows | numeric | blank |
| --- | ---: | ---: | ---: |
| `human_labels/participant3_data_pass_1.tsv` | 75 | 44 | 31 |
| `04_veribench_validation/data/steven_data_pass_1.tsv` | 75 | 30 | 45 |
| `human_labels/expert_harsh_set_data.tsv` | 225 | 193 | 32 |
| `human_labels/participant1_data_correct_prompt.tsv` | 75 | 74 | 1 |

### Four traps in this layout

1. **Duplicate files under different names.** `participant2_data_pass_1.tsv` *is*
   `jolene_data_pass_1.tsv`; `old_prompt/participant1_data_pass_2.tsv` *is*
   `ethan_human_scores_20260425.tsv`. Same bytes, two paths.
2. **The `*_set_data.tsv` files are stacked, not independent.** `expert_harsh_set_data.tsv` = participants
   1+2+3 concatenated (74+75+44 = 193 rows over only 78 distinct pairs). `lenient_set_data.tsv` =
   participants 4+5 + `old_prompt/pass_1` + the 72-row subset of `ethan_20260425` (75+75+75+72 = 297).
   Both decompose exactly — see `results/PANEL_TRACE.md` §4. Treating either as one rater's scores
   double-counts. Worse, `lenient_set_data.tsv` **mixes rubrics**: it carries both lenient passes and
   the harsher `20260425` pass.
3. **`ethan_human_scores_ORIGINAL.tsv` has 78 rows for 75 pairs.** Problem `4_json_decoder` appears
   twice (all 3 candidates), scored `1` and `2`. Averaging gives the three `1.5` values visible in the
   appendix histogram.
4. **Row counts are not label counts.** Summing every file in `experiments/human_labels/` gives 983
   numeric cells, but the derived `*_set_data.tsv` files (490 rows) are concatenations of the very
   rater files sitting next to them, and `old_prompt/` (150 rows) is the same annotator's two passes.
   The number of **independent** labels from the five-rater pool is **343**, which is what the paper
   reports and what `exp43_frozen_tivar_heldout.py` consumes. Any count above that is double-counting.

---

## 3. Two label populations that are *not* interchangeable

| | calibration panel | held-out pool |
| --- | --- | --- |
| raters | 1 (participant 1 / Ethan) | 5 (participants 1–5) |
| views | 2 rubric strictness passes | 1 pass each |
| rubric prompt | **old** prompt | **revised** ("correct") prompt |
| labels | 150 (75 × 2) | **343** |
| distinct pairs | 75 (72 analyzed) | **78** |
| problems | 25 (24 analyzed) | 26 |
| used for | `0.833 / 0.905 / 0.738` headline | frozen held-out test |

The held-out pool numbers reproduce the paper exactly: **343 labels, 78 pairs, 5 raters** — all MATCH.
Pool ∩ panel = 63 pairs.

**The two populations use different rubrics, and that difference dominates everything else.** Same
annotator, same artifacts, old vs revised prompt:

| view | Spearman vs `participant1_data_correct_prompt` | n |
| --- | ---: | ---: |
| `pass1` | 0.076 | 62 |
| `pass2` | 0.165 | 62 |
| `avg` | 0.128 | 62 |
| **mean** | **0.123** | |

That `0.123` is the paper's "cross-protocol label correlation ≈ 0.13". One person re-rating the same
files under a reworded rubric produces **essentially uncorrelated** scores — larger than any
between-rater disagreement in the pool (inter-rater Spearman there ranges 0.05–0.87). So the frozen
held-out null is a **construct mismatch, not a data-integrity problem**, which is what the two-stage
audit already concluded.

---

## 4. Reproducing every published number

`results/PANEL_TRACE.md` checks the paper against the cached run artifacts:

| statistic | cached run | paper | status |
| --- | ---: | ---: | --- |
| inter-pass Spearman | 0.2486 | 0.249 | MATCH |
| inter-pass Pearson | 0.3747 | 0.375 | MATCH |
| inter-pass Kendall | 0.2214 | 0.221 | MATCH |
| inter-pass QWK | 0.3718 | 0.372 | MATCH |
| inter-pass MAE | 0.7708 | 0.778 | **MISMATCH** |
| inter-pass MSE | 1.1215 | 1.139 | **MISMATCH** |
| held-out labels / pairs / raters | 343 / 78 / 5 | 343 / 78 / 5 | MATCH |

The four correlations reproduce exactly. **MAE and MSE do not**, and the cause is pinned down:
`0.778 = 56/72` and `1.139 = 82/72` are what you get when the three duplicated `4_json_decoder` rows
take pass2 `= 1.0` (first-of-duplicates) instead of `1.5` (mean-of-duplicates). Appendix
Table `tab:app-human-human-ceiling` therefore mixes two duplicate-handling conventions across its own
rows. Direction and magnitude are unaffected; only the third decimal moves.

Convention sweep over all five duplicate rules × two row subsets is in
`results/interpass_convention_sweep.csv` — no convention on the *current 75-pair* files reproduces the
published decimals, which is itself the evidence that the published numbers are 72-pair numbers.

---

## 5. Suggested paper corrections

Line numbers are `paper_latex/TMLR_2026/main.tex` **as of 2026-08-11 after the mid-session patch**
(the file is being edited concurrently — re-grep before applying).

### ⚠️ First: line 312 is now wrong in a *new* way

The patch rewrote line 312 to read:

> "an aligned panel of \(n=75\) candidate--gold pairs (**\(72\) unique pairs plus three
> legacy-duplicate rows**) from \(24\) problems with \(3\) agent generations per problem"

**This conflates two unrelated 3s and should not ship.** Measured from the files:

| | pass1 file | pass2 file | aligned panel |
| --- | ---: | ---: | ---: |
| rows | 75 | **78** | — |
| unique pairs | 75 | 75 | **75** |
| duplicated pairs | 0 | 3 (`4_json_decoder`) | 0 |
| problems | 25 | 25 | **25** |

- The panel has **75 unique pairs over 25 problems**, not 72 unique + 3 duplicates.
- The three legacy duplicates are extra **rows in the pass2 file** (making it 78 rows), and they
  collapse to the same 75 pairs. They never inflated the panel.
- The 72-vs-75 gap is a **different** three: the `0_unsafeMultiply_safe` pairs dropped on a stale
  gold filename. Both are "3", and they are not the same 3.

Correct phrasing: *"an aligned panel of 75 rated candidate–gold pairs from 25 problems × 3 agent
generations; 72 pairs (24 problems) enter the analyses, because one problem's gold artifact is
indexed under a pre-renumbering filename."*

### Remaining edits

| line | current | issue | suggested |
| ---: | --- | --- | --- |
| 201 (page 4) | "`n=75` aligned candidate–gold pairs are rated by one annotator under two rubric strictness levels" | `75` is the rated count; analyses used 72 | "…`n=72` of `75` rated aligned pairs…" |
| 312 | see above | conflates the two 3s | see above |
| 90, 122, 131, 250, 489, 584, 1161 | `n=75` | same | `n=72` analyzed, or "72 of 75 rated" |
| 1167 | "the `~72`–`75` overlapping aligned rows" | hedge that hides a determinate fact | state 72 |
| 1115 | MAE `0.771` "On `n=72` overlap" | ✅ **already fixed** by the patch — matches the cached run | keep |
| — | MSE row | appears to have been dropped in the patch | if reinstated, use `1.122` (not `1.139`) |
| 312 | "Each pair receives two human passes" | true but reads as two annotators | "one annotator scores each pair twice under two rubric strictness levels" |

Everything qualitative in the paper survives: the panel is small and single-annotator, inter-pass
agreement is moderate, the headline correlations are in-sample with wide CIs, and the held-out null is
a rubric-construct mismatch. Only exact counts and two error decimals need editing.

**Alternative to editing the prose:** fix the label file instead. Renaming the 3
`0_unsafeMultiply_safe` rows to `1_unsafeMultiply_safe` and re-running EXP16/EXP18 makes `n=75` and
`25 problems` literally correct, at the cost of re-generating the headline numbers. Editing the text
is cheaper; fixing the data is more correct. Both are defensible — but the paper cannot keep
`n=75` *and* `24 problems` in the same sentence.

---

## 6. Files

```text
experiments/26_human_label_dataset_audit/
├── README.md                     # this document — the paper's n=75 / pass1 / pass2 panel
├── CAMPAIGN_INVENTORY.md         # every human-label campaign in cert-judge + veribench
├── audit_human_labels.py         # inventory + panel + held-out pool, recomputed from raw TSVs
├── reconcile_paper_numbers.py    # duplicate-convention sweep; problem-level composition
├── trace_analyzed_panel.py       # proves n=72 from cached run artifacts; protocol drift
└── results/
    ├── AUDIT.md                     # full inventory, all pairwise agreements
    ├── RECONCILIATION.md            # convention sweep + per-problem coverage matrix
    ├── PANEL_TRACE.md               # 72-vs-75 evidence, set decomposition, drift
    ├── audit_summary.json           # machine-readable summary
    ├── aligned_panel_n75.tsv        # tidy panel: gold, candidate, problem, agent, pass1, pass2, avg
    └── interpass_convention_sweep.csv
```

### Run it

```bash
cd experiments/26_human_label_dataset_audit
python3 audit_human_labels.py
python3 reconcile_paper_numbers.py
python3 trace_analyzed_panel.py
```

Pure stdlib — no `numpy`/`pandas`/`scipy`, so it runs in the bare macOS interpreter. Read-only
except for `results/`. No LLM or network calls.

### Recommended single source of truth

`results/aligned_panel_n75.tsv` is the tidy long form of the panel — one row per pair with `pass1`,
`pass2`, `avg`, plus parsed `problem` and `agent` columns. It keeps all 75 rated pairs; filter
`problem != "0_unsafeMultiply_safe"` to get the 72 the published results used.

---

## 7. The two documents in this folder

Two concurrent sessions audited this data from different angles. Both outputs live here now:

| | `README.md` (this file) | `CAMPAIGN_INVENTORY.md` |
| --- | --- | --- |
| question | what are `n=75` / `pass1` / `pass2` in the paper? | what human-label data exists *at all*? |
| scope | the one calibration panel the paper's numbers rest on | every campaign, cert-judge + veribench |
| method | recompute every published statistic from raw TSVs | git archaeology + cross-repo inventory |
| unique findings | `n=75` file count vs `n=72` analyzed panel; `pass1`/`pass2` inverted vs chronology; MAE/MSE convention mismatch; exact decomposition of the stacked set files | participant↔name mapping recovered from `6169a29f`; study `18_/41_` is 0% collected; "30 problems" = 25 + 5 stale aliases; `ethan_hand_labels` (78 rows) |
| artifacts | 3 runnable stdlib scripts + regenerable `results/` | prose |

They agree everywhere they overlap: 25 problems × 3 agents, ρ ≈ 0.13 cross-protocol drift,
150 old-protocol labels, 343 in the five-rater sub-pool, `avg` file mean 3.77, pass1 mean 3.60, and
96% exact agreement between `old_prompt/participant1_data_pass_1.tsv` and `ethan_ORIGINAL` (72/75
rows identical; the 3 that differ are the `4_json_decoder` duplicates).

**`CAMPAIGN_INVENTORY.md`'s alias finding upgraded this one.** Its §7 identifies
`0_unsafeMultiply_safe` as one of five stale pre-renumbering filenames — the correct root cause for
the 3 dropped pairs, better than "the artifact is absent", which is what a naive filename search
suggests. §1 above is written against that explanation, verified independently here.

### Two numbers that needed reconciling

1. **835 vs 343 labels.** `CAMPAIGN_INVENTORY.md` originally headlined `835` usable labels for the
   revised-protocol pool. That is the row total across 7 files: `835 ≈ 343` (participants 1–5)
   `+ 193` (`expert_harsh_set`) `+ 297` (`lenient_set`). But `results/PANEL_TRACE.md` §4 decomposes
   both aggregates **exactly, with zero unexplained rows** — they contain no ratings that are not
   already in the participant files, so `835` counts most raters roughly three times. **Use 343**;
   it is what the paper reports and what `exp43_frozen_tivar_heldout.py` consumes. Corrected inline
   in that document's §9, with its own §2 and §8 already making the same point.
2. **pass-2 mean 3.89 vs 3.91.** Just duplicate handling: `3.89` is the 75-row `old_prompt` copy,
   `3.91` is the 78-row `ethan_ORIGINAL` copy deduplicated by averaging the `4_json_decoder` rows to
   `1.5`. Same ratings; the raw 78-row mean is `3.82`.

---

## 8. Why `20_`–`26_` all exist

The numbers are **not chronological** and the directory number is **not** the EXP number — which is
most of the confusion. What each one is:

| dir | added | what it is |
| --- | --- | --- |
| `20_fixed_judge_across_agents` | 2026-06-04 | separate thread: one frozen judge evaluated across many VeriBench-solving agent CLIs |
| `21_tmlr_submission` | 2026-08-01 | TMLR **desk-reject response** + resubmission kit, mega-QA, evidence map |
| `22_pooled_heldout_and_noise_ceiling` | 2026-07-21 | **EXP44** — pooled held-out power analysis; found the held-out null is labeling-protocol drift (ρ ≈ 0.13), not data corruption |
| `23_reanchored_calibration` | 2026-07-21 | **EXP45** — pre-registered re-anchoring, n=14, registered outcome (c) *underpowered* |
| `24_expanded_panel_cli` | 2026-07-29 | **EXP46** — expanded panel, n=32, registered verdict (b) *no label-free property signal* |
| `25_motivation_llm_judges` | 2026-08-11 | the `motivation.md` notes, moved out of a bare `experiments/20/` |
| `26_human_label_dataset_audit` | 2026-08-11 | this folder |

`22`/`23`/`24` are the three steps the paper's abstract narrates in order — the audit that explained
the frozen held-out null, then the two pre-registered screens (`n=14`, then `n=32`). `21_` is dated
*after* them because it was created later, in response to the desk reject.

The repo also has pre-existing duplicate numbers unrelated to this work (`03_`, `04_`, `17_`, `18_`
each appear twice) — the numbering has never been a strict sequence.

---

## Dependencies

- `experiments/human_labels/*.tsv` (shared rater files)
- `experiments/04_veribench_validation/data/*.tsv` (files the pipeline reads)
- `experiments/04_veribench_validation/results_exp16_final_robust/` (cached judge run)
- `experiments/04_veribench_validation/results_final_stat_reliability_suite/exp18_human_label_reliability/` (cached reliability run)

## Status

| Step | Status | Notes |
| --- | --- | --- |
| Inventory every human-label file | Done | 16 files, `results/AUDIT.md` §1 |
| Explain `n=75` | Done | 25 problems × 3 generations; 72 analyzed |
| Explain `pass1` / `pass2` | Done | one annotator, two rubric strictness levels, names inverted vs chronology |
| Verify held-out pool (343/78/5) | Done | all three MATCH |
| Reproduce inter-pass statistics | Done | 4/6 exact; MAE/MSE traced to a duplicate-convention mix |
| Suggested paper edits | Done | §5 |
| Cross-check vs sibling audit `21_` | Done | §7; agree on all shared facts; 835-vs-343 reconciled |
| New human labels collected | N/A | audit only; no new annotation or judge calls |
