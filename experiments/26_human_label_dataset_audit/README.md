# Experiment 26 — Human-label dataset audit (READ THIS FIRST)

> **Purpose of this folder:** one place that answers, with receipts, *what human judgment data
> cert-judge has, what every published number was computed on, and which data can be used as the
> human criterion going forward.* Everything here is recomputable from raw TSVs with the three
> stdlib-only scripts (no API keys, no network).

**Status: audit complete; confirmed by the annotator (Ethan, Slack, 2026-08-14).** See
[`ethan_slack_confirmation.md`](ethan_slack_confirmation.md).

---

## Reading order

| read | if you want | length |
| --- | --- | --- |
| **this README** | the headline facts and the map | 2 min |
| [`cert_judge_judgements_human_scores.md`](cert_judge_judgements_human_scores.md) | the calibration panel the paper's numbers rest on (`n=75` / 72, strict/lenient, every published statistic recomputed) | deep dive |
| [`vb_judgements_human_scores.md`](vb_judgements_human_scores.md) | the **VeriBench 5-rater pool** — the larger multi-rater dataset, how it differs from the calibration panel, and whether it is the better criterion (answer: yes for reliability, but it measures a *different construct*) | 10 min |
| [`ethan_slack_confirmation.md`](ethan_slack_confirmation.md) | the annotator's own answers checked against the audit | 5 min |
| [`CAMPAIGN_INVENTORY.md`](CAMPAIGN_INVENTORY.md) | every human-label campaign ever (A–E), git archaeology, stale-filename catalogue | reference |
| [`results/`](results/) | machine-recomputed evidence behind all of the above | reference |

## The five facts everything else hangs on

1. **The calibration panel is 75 rated candidate–gold pairs (25 problems × 3 agents); 72 pairs
   (24 problems) enter every published analysis** — 3 pairs drop on a stale pre-renumbering
   filename (`0_unsafeMultiply_safe` → now `1_unsafeMultiply_safe`), not missing data.
2. **`strict` and `lenient` (formerly `pass1`/`pass2`) are one annotator — Ethan — rating the
   same 75 pairs twice under two rubric-strictness readings.** Not two raters. The old pass
   names are inverted relative to chronology, which is why the ICLR 2027 paper abandons
   temporal names entirely. Inter-round agreement on the 72: Spearman 0.249 — that is *rubric
   stability*, and it is the ceiling for any judge–human correlation on this panel.
3. **The 5-rater VeriBench pool (343 labels, 78 pairs, 5 raters) is a separate population under
   a revised rubric.** It is bigger and much more reliable (Spearman–Brown ceiling ≈ 0.87 vs
   the panel's 0.249 self-agreement) — but it correlates with the calibration labels at only
   **ρ ≈ 0.13**, so it is a *different criterion*, not a drop-in held-out test. That drift —
   not label noise, not data corruption — is why the frozen held-out test came back null.
4. **All headline bridge numbers (0.833 / 0.905 / 0.738 avg/strict/lenient, n=8 judge configs)
   are validation-set evidence on the calibration panel**, and the ICLR 2027 paper labels them
   as such.
5. **Total distinct human 0–5 judgments in the repo: 572** (343 pool + 150 panel + 78 early
   hand-labels + 1 prototype). Any larger count is double-counting the derived aggregate files.

## ICLR 2027 notation crosswalk

The paper (`paper_latex/ICLR_2027_submission/main.tex`) and the Aug-2026 revision memo renamed
the working vocabulary. Older docs in this folder keep the historical names where they quote
files on disk; translate as:

| old (files, code, this folder's history) | ICLR 2027 (current) |
| --- | --- |
| `pass1` | **strict** view |
| `pass2` | **lenient** view |
| "cert index", "trust index", `TI_var` | $\mathrm{PTI}_p$ (label-free Proxy Trust Index; variance-aware aggregate $\mathrm{PTI}_{\mathrm{var}}$) |
| per-judge "human alignment" Spearman | $\mathrm{TI}_{m_1}$ (the human-grounded criterion) |
| "certification", CERTIFY | **screen** / amortized judge validation |
| P1 / P2 / P3 / P4 | $P_{\mathrm{rfl}}$ / $P_{\mathrm{mb}}$ / $P_{\mathrm{mms}}$ / $P_{\mathrm{ps\&SI}}$ |

In that notation: the **calibration panel** below is the human tensor
$D_{\hat S^*_H \mid b', L_A}$ that defines $\mathrm{TI}_{m_1}$ (72 items × {strict, lenient,
avg}); the **5-rater pool** is a different $H$ (different rubric ⇒ different criterion
identity). The bridge correlation is judge-indexed — its $n$ is the number of judge
configurations (8–13 today, target ≈ 40), not the number of items.

⚠️ **Naming hazard:** the pool's aggregate files `expert_harsh_set_data.tsv` /
`lenient_set_data.tsv` are **stacked multi-rater concatenations from the 5-rater pool** — they
are *not* the strict/lenient views of the calibration panel, despite the similar names. Never
mix the two; details in `vb_judgements_human_scores.md` §4.

## Files

```text
experiments/26_human_label_dataset_audit/
├── README.md                              # this index
├── cert_judge_judgements_human_scores.md  # deep dive: the calibration panel (was README.md)
├── vb_judgements_human_scores.md          # deep dive: the VeriBench 5-rater pool + comparison
├── ethan_slack_confirmation.md            # annotator confirmation vs audited facts
├── CAMPAIGN_INVENTORY.md                  # all campaigns A–E, git archaeology
├── audit_human_labels.py                  # recompute inventory + panel + pool from raw TSVs
├── reconcile_paper_numbers.py             # duplicate-convention sweep
├── trace_analyzed_panel.py                # proves n=72 from cached run artifacts
└── results/
    ├── AUDIT.md                           # full file inventory, pairwise agreements
    ├── PANEL_TRACE.md                     # 72-vs-75 evidence, set decomposition, drift
    ├── RECONCILIATION.md                  # convention sweep, per-problem coverage
    ├── audit_summary.json                 # machine-readable summary
    ├── aligned_panel_n75.tsv              # ★ tidy source of truth: one row per rated pair
    └── interpass_convention_sweep.csv
```

**Single source of truth for the panel:** `results/aligned_panel_n75.tsv` — one row per rated
pair with strict (`pass1` column), lenient (`pass2` column), `avg`, `problem`, `agent`. Filter
`problem != "0_unsafeMultiply_safe"` to get the 72 all published results use.

## Run it

```bash
cd experiments/26_human_label_dataset_audit
python3 audit_human_labels.py       # regenerates results/AUDIT.md, audit_summary.json, aligned_panel_n75.tsv
python3 reconcile_paper_numbers.py  # regenerates results/RECONCILIATION.md, interpass_convention_sweep.csv
python3 trace_analyzed_panel.py     # regenerates results/PANEL_TRACE.md
```

Pure stdlib; read-only outside `results/`.
