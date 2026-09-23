# results.md — experiment 33 (OpenReview complaints → ICLR 2027 paper)

**Status:** DONE for three venues; BLOCKED on the DL4C paste (started 09-22-2026 14:58 PDT)
**Last updated:** 09-22-2026 15:42 PDT

| Phase | Status | Evidence |
|---|---|---|
| 1. Locate every OpenReview forum | DONE | `reviews/fetch_attempts.md` (4 forums; no NeurIPS 2026 / ICLR 2026 submission found) |
| 2. Capture reviews verbatim | DONE for 3 venues; BLOCKED for DL4C | `reviews/*.md`; DL4C skeleton + 13 logged fetch attempts |
| 3. Ledger (one row per complaint) | DONE | `complaints_ledger.md`: 14 `N25-*`, 3 `T26-*`, 29 `A26-*`, `D26-*` placeholders, open items O1–O3 |
| 4. Prompts 01–04 | DONE | `prompts/` |
| 5. Paper edits E1–E9 | DONE | commit `e0631b6`; 27-page PDF, 0 undefined citations/references, 0 BibTeX warnings |
| 6. DL4C ingestion + re-audit | PENDING (needs Brando's paste) | `prompts/03_…` |

## Ledger counts after the edits (46 rows, DL4C placeholders excluded)

| Status | Rows |
|---|---|
| Addressed | 24 |
| Disclosed (stated as a limitation) | 12 |
| Deferred (named owner: experiment 31 or future work) | 3 |
| Superseded (old Fig. 1; §5.4 VeriBench table removed 09-22-2026) | 7 |
| Unknown (DL4C) | placeholders only |

## Edits

| Edit | Landed | Commit |
|---|---|---|
| E1 weak-monotonicity wording + cumulative-ladder sentence | yes | `e0631b6` |
| E2 Fig. 1 "vs." → "w.r.t." | yes | `e0631b6` |
| E3 Codex headline bootstrap CIs / permutation p (0.833 [0.24, 1.00] p=0.017; 0.905 [0.41, 1.00] p=0.005; 0.738 [0.11, 1.00] p=0.045) | yes | `e0631b6` |
| E4 alpha canonicalization proxy (mean per-judge std 0.250 → 0.070, eight Codex configurations) | yes | `e0631b6` |
| E5 pre-registered screens disclosed (n=14 underpowered; n=32 strongest ρ −0.39, Holm p=0.25; LOO ρ=0.24, p=0.49) | yes | `e0631b6` |
| E6 untested failure classes + Lean-only scope | yes | `e0631b6` |
| E7 median over repeated calls: three for LLM judges, nine for the two non-LLM controls (corrected from "nine" after cert-judge-57's check) | yes | `e0631b6` |
| E8 appendix agreement statistics on the 72 overlapping pairs; MAE 0.771 / MSE 1.121 | yes | `e0631b6` |
| E9 refs.bib hygiene (anonymous entry deleted; Bach, Ding, Bowman entries completed) | yes | `e0631b6` |

## Numbers introduced (paper value ← artifact)

| Paper text | Value | Artifact |
|---|---|---|
| §5.3 bootstrap CIs / permutation p | [0.24, 1.00] p=0.017; [0.41, 1.00] p=0.005; [0.11, 1.00] p=0.045 | `experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json` (0.241/1.0/0.0167; 0.407/1.0/0.0054; 0.114/1.0/0.0451) |
| §5.2 canonicalization proxy | 0.250 → 0.070 | `…/results_exp24_alpha_canonicalized_identity/summary.json` (0.2501 → 0.0697, `alpha_policy` clip, `n_judges` 8) |
| §6 registered screens | n=14; n=32; −0.39; Holm 0.25; LOO 0.24, p 0.49 | `experiments/archive/23_reanchored_calibration/REPORT.md`; `experiments/archive/24_expanded_panel_cli/results/pass2_full_screen_results.json` |
| §5.3 repeats | 3 (LLM judges), 9 (controls), median | `…/results_exp16_final_robust_r9_median/detail_rows.csv` (`repeat_scores` lengths), `summary.json` (`repeat_agg` median) |
| §5.1 + appendix MAE / MSE / n | 0.771 / 1.121 / 72 | `…/results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json` (`mae_0_5` 0.7708, `rmse_0_5` 1.0590 → MSE 1.1215, `n_overlap_pairs` 72) |

## Still open

- DL4C reviews (forum `gGR1gE7x3a`): Brando pastes them into `reviews/icml2026_dl4c_gGR1gE7x3a.md`, then prompt 03 runs.
- O2 (appendix "best Spearman 0.480/0.559" comes from the alpha-ablation panel) and O3 (intro TODO on label reuse) are with experiment 31.
- §5.4 (VeriBench agent ranking, Table 5) was removed from main.tex on 09-22-2026 by Brando's decision (uncertified Claude 3.7 judge; exp32 stopped at commit d7f37c3), which closes the six VeriBench-judge rows as Superseded.

## Provenance note (09-22-2026 15:45)

Commit `57ccf9f` also carries the §5.4 / Table 5 cut of `main.tex` and `main.pdf` (−25 lines) that session "paper writing certjudge" had staged in the shared index; the paper content in that commit is theirs, made on Brando's decision, and the pushed HEAD builds in a scratch copy (26 pages, 0 undefined citations or references). Lesson recorded in memory: commit with explicit pathspecs (`git commit -- <paths>`) when other sessions share the checkout.

**TLDR-end:** [cj: or-complaints] All 46 complaints from the three retrievable OpenReview rounds are ledgered and the nine artifact-traced paper edits landed in commit `e0631b6`; the DL4C reviews remain the one missing input and need Brando's paste before prompt 03 can run.
