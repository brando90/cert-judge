# Experiment 41 results: provenance audit and re-score against VeriBench expert labels

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/results.md>

**TLDR:** DONE. Gate G0 reproduces the paper's nine judge-level Spearman values to 3 decimals (PASS). Paper labels confirmed = VeriBench participant 1's superseded old-prompt passes. Of 24 scored validation-set tasks (1 of 25 was silently skipped by the judge pipeline itself on a stale gold filename), only 7 have judge-seen reference bytes matching what the rater saw. Under the pre-registered reading, the re-scored association against VeriBench's corrected expert labels on matched items is **inconclusive** (positive for Codex +0.333 and Qwen3-Coder +0.667, negative for Claude Opus −0.381). Full detail: `REPORT.md`.

**Status:** DONE (09-30-2026, skampere1 tmux `cj-e41-provenance-audit`; zero model calls throughout; worker Claude Sonnet 5, effort high)
**Last updated:** 09-30-2026 14:55 PDT

| Step | Status | Evidence |
|---|---|---|
| Label identity | DONE — paper pass1 = participant1 old pass2 on 75/75; paper pass2 = participant1 old pass1 on 72/75; pass names swapped vs. old_prompt filenames | `results/label_identity.json` |
| Rating dates and rater-seen references | DONE (limitation: pass1/pass2 share one git-commit date, so not separately distinguishable by this method) | `results/provenance_by_task.csv` |
| Judge-seen references | DONE — 1/25 tasks never scored (missing_gold, stale filename); of 24 scored, 7/24 matched, 17/24 mismatched | same |
| Gate G0 (reproduce nine judge-level Spearman values) | **PASS** — Codex 0.833333/0.904762/0.738095 vs. paper-quoted 0.833/0.905/0.738 | `results/G0_reproduction.json` |
| Views V1–V5 | DONE, all 3 families | `results/judge_level_views.csv`, `results/per_judge_agreement.csv` |
| S1 (LOFO/LOCO) | DONE | `results/lofo_loco.csv` |
| S2 (old vs. corrected prompt) | Partially done — label identity + swap confirmed; exact instruction-text diff not extracted (unmeasured, disclosed in REPORT.md) | `results/label_identity.json`, `REPORT.md` |
| S3 (label-agreement matrix) | DONE | `results/label_agreement_matrix.csv` |
| S4 (label-free bug-ladder reversal) | DONE by citation — confirmed unaffected, no recomputation needed | `experiments/archive/04_veribench_validation/results_exp19_low_variance_replot/bug_reversal_rates.csv` |
| Report | DONE | `REPORT.md` |
| Landing (PR + merge + email receipt) | **DONE** — PR #50 merged (da61634), email receipt sent to brando.science@gmail.com, `private/DONE` touched | https://github.com/brando90/cert-judge/pull/50 |

## Headline numbers

| family | V1 (paper avg, all 72, reproduction) | V3 (VB expert mean, matched n=21) |
|---|---:|---:|
| Codex | 0.833 (p=0.015, CI [0.24, 0.98]) | 0.333 (p=0.428, CI [−0.32, 0.54]) |
| Claude Opus | 0.643 (p=0.096, CI [−0.26, 0.90]) | −0.381 (p=0.360, CI [−0.52, 0.66]) |
| Qwen3-Coder | 0.905 (p=0.005, CI [0.02, 0.90]) | 0.667 (p=0.083, CI [−0.57, 0.90]) |

**Reading:** neither "robust" (all three V3 positive) nor "not robust" (at least two V3 ≤ 0) — **inconclusive** per the pre-registered rule in `README.md`.

**TLDR-end:** [cj: e41-provenance] G0 passes exactly; paper labels are VeriBench's old-prompt passes; only 7/24 scored tasks have provenance-matched reference bytes; matched + corrected-label re-score is inconclusive (2 families positive, 1 negative). Landing (PR/merge/email) in progress.
