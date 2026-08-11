# Experiment 21 — What the human-judgment dataset actually is

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

The gap: the annotator rated a 25th problem, `0_unsafeMultiply_safe`, whose gold `.lean` file
**does not exist anywhere in the repo**. EXP16 logs it explicitly:

```
# experiments/04_veribench_validation/results_exp16_final_robust/skipped_pairs.csv
0_unsafeMultiply_safe.lean,0_unsafeMultiply_safe__agent0.lean,missing_gold
0_unsafeMultiply_safe.lean,0_unsafeMultiply_safe__agent1.lean,missing_gold
0_unsafeMultiply_safe.lean,0_unsafeMultiply_safe__agent2.lean,missing_gold
```

No judge can score a pair whose gold artifact is absent, so all three drop out and every run
reports `n_union_rows = 72`, `n_human_rows_pass1/pass2/avg = 72`.

> **This is why `24 problems × 3 generations` and `n=75` appear in the same sentence on page 4 and
> don't multiply out.** `24 × 3 = 72` is the analyzed panel; `75` is the file row count. Both numbers
> are real, they just describe different things.

### What are `pass1` and `pass2`?

**One annotator (participant 1 / Ethan) rated the same pairs twice under two different rubric
strictness levels.** They are not two people and not two disjoint data splits — they are two
*label views* of one panel, which is why the paper reports `pass1`, `pass2`, and `avg` side by side.

| paper name | file the pipeline reads | rubric | mean score | character |
| --- | --- | --- | ---: | --- |
| `pass1` | `experiments/04_veribench_validation/data/ethan_human_scores_20260425.tsv` | strict | **3.60** | harsher |
| `pass2` | `experiments/04_veribench_validation/data/ethan_human_scores_ORIGINAL.tsv` | loose | **3.91** | more lenient |
| `avg`   | `experiments/04_veribench_validation/data/ethan_human_scores_avg_two_passes_20260425.tsv` | — | 3.75 | mean of the two |

**The naming is inverted relative to chronology.** By content hash:

- paper `pass1` is byte-identical (`sha256[:12] = 1e9e4c3fc72a`) to
  `experiments/human_labels/old_prompt/participant1_data_pass_2.tsv` — the annotator's *second* pass,
  re-rated on 2026-04-25.
- paper `pass2` is the annotator's *first* pass (`ethan_human_scores_ORIGINAL`), matching
  `old_prompt/participant1_data_pass_1.tsv` at Spearman `1.000`.

So **paper `pass1` = annotator pass 2**, and **paper `pass2` = annotator pass 1**. Read `pass1`/`pass2`
as "strictness level 1 / 2", never as "first / second in time".

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
| `human_labels/participant3_data_pass_1.tsv` | 44 | 44 | 15 | Steven + others (partial coverage) |
| `human_labels/participant4_data_pass_1.tsv` | 75 | 75 | 25 | rater 4 |
| `human_labels/participant5_data_pass_1.tsv` | 75 | 75 | 25 | rater 5 |
| `human_labels/old_prompt/participant1_data_pass_1.tsv` | 75 | 75 | 25 | = `ethan_ORIGINAL` (deduped) |
| `human_labels/old_prompt/participant1_data_pass_2.tsv` | 75 | 75 | 25 | = `ethan_20260425`, byte-identical |
| `human_labels/expert_harsh_set_data.tsv` | 193 | 78 | 26 | **derived**: concat of participants 1–3 |
| `human_labels/lenient_set_data.tsv` | 297 | 90 | 30 | **derived**: concat of 4 rater views |
| `04_veribench_validation/data/steven_data_pass_1.tsv` | 30 | 30 | 10 | subset of participant 3 |
| `04_veribench_validation/data/super_human_pass3_avg_five_raters.tsv` | 44 | 44 | 15 | derived 5-rater mean |

### Three traps in this layout

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

Line numbers are `paper_latex/TMLR_2026/main.tex`.

| line | current | issue | suggested |
| ---: | --- | --- | --- |
| 205 (page 4) | "`n = 75` aligned candidate–gold pairs are rated by one annotator under two rubric strictness levels" | `75` is the file row count; analyses used 72 | "…`n = 72` aligned candidate–gold pairs (24 problems × 3 agent generations; 75 were rated, 3 dropped for a missing gold artifact) are rated by one annotator under two rubric strictness levels" |
| 316 | "aligned panel of `n=75` … from `24` problems with `3` agent generations per problem" | internally inconsistent: 24 × 3 = 72 | use `n=72` / 24 problems / 3 generations |
| 96, 128, 136, 438, 531, 1043, 1100, 1101 | `n=75` | same | `n=72` (or "72 analyzed of 75 rated") |
| 1106 | "the `~72`–`75` overlapping aligned rows" | hedge that hides a determinate fact | state 72 |
| 1056–1057 | MAE `0.778`, MSE `1.139` | different duplicate convention than the same table's correlations | `0.771` and `1.122`, or footnote the convention |
| 316 | "Each pair receives two human passes" | true but reads as two annotators | "one annotator scores each pair twice under two rubric strictness levels" |

Everything qualitative in the paper survives: the panel is small and single-annotator, inter-pass
agreement is moderate, the headline correlations are in-sample with wide CIs, and the held-out null is
a rubric-construct mismatch. Only exact counts and two error decimals need editing.

---

## 6. Files

```text
experiments/21_human_label_dataset_audit/
├── README.md                     # this document
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
cd experiments/21_human_label_dataset_audit
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
| New human labels collected | N/A | audit only; no new annotation or judge calls |
