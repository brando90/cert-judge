# Experiments

Only currently pursued experiments belong directly in this directory.
| Active experiment | Current task |
|---|---|
| [38_iclr_body_rewrite_to_trust_artifact_abstract](38_iclr_body_rewrite_to_trust_artifact_abstract/README.md) | Rewrite the ICLR 2027 body (sections 1–7) to the approved trust-artifact abstract from frozen evidence; Claude Fable 5.1, deterministic checks only. Started 09-26-2026. |
| [37_openreview_feedback_current_iclr_revision](37_openreview_feedback_current_iclr_revision/README.md) | OpenReview automated feedback versus current ICLR manuscript; Claude Fable assessment, then warranted Astra Ultra edits. Started 09-26-2026. |
| [33a_ai4math_reviews](33a_ai4math_reviews/README.md) | ICML 2026 AI4Math reviews (verbatim) and their 29 complaint rows against the ICLR paper; formerly 18_icml_reviews. Moved 2026-09-22. |
| [34_iclr_mega_rewrite_astra](34_iclr_mega_rewrite_astra/PROMPT.md) | Core-only ICLR rewrite by Codex GPT-6 Astra (ultra) on branch `astra/iclr-mega-rewrite`; runbook + live results. Started 2026-09-22. |
| [35_missing_experiments_from_reviews](35_missing_experiments_from_reviews/EXPERIMENTS.md) | Reviewer-driven missing experiments with ready CLI-only prompts (zero-inference / subscription / human-label tiers). Started 2026-09-22. |
| [33b_or_ledger](33b_or_ledger/README.md) | Hub: edits ledger E1–E9 (artifact-traced, landed), live results, prompts 01–04, fetch log, OpenReview form abstract. Split from the former 33_ folder 2026-09-22. |
| [33c_dl4c_reviews](33c_dl4c_reviews/README.md) | ICML 2026 DL4C reviews: skeleton awaiting Brando's paste, then D26 complaint rows via prompt 03. Started 2026-09-22. |
| [33d_mathai_reviews](33d_mathai_reviews/README.md) | NeurIPS 2025 MATH-AI reviews (verbatim) and their 14 complaint rows. Started 2026-09-22. |
| [33e_tmlr_desk_reject](33e_tmlr_desk_reject/README.md) | TMLR 2026 desk-reject record and its 3 rows; form-abstract lesson applied. Started 2026-09-22. |

The completed proxy studies are archived; the suggested new-family follow-up
has not started and is not an active run. This is a repository classification,
not a claim about processes on remote machines.

| Location | Purpose |
|---|---|
| [archive/](archive/README.md) | Completed, superseded, or parked studies, including recent results. |
| [human_labels/](human_labels/) | Shared human-label data; not an experiment. |
| [ethan_hand_labels/](ethan_hand_labels/) | Shared human-label data; not an experiment. |
| [ideas/](ideas/README.md) | Optional, deferred research ideas; recording one does not launch it. |

The ignored local `keys/` directory is credential storage, not an experiment.

## Recent completed work

- [31_final_iclr_paper_writing](archive/31_final_iclr_paper_writing/README.md): archived 09-25-2026 — earlier manuscript writing and research superseded by Experiment 34's corrected rewrite and submission preparation; original notes, research, and exploratory output preserved.

- [36_vals_gateway_cert_judge_smoke](archive/36_vals_gateway_cert_judge_smoke/results.md): completed 09-24-2026 — 1/1 real GPT-6 Astra xhigh identity judgment via Vals gateway on SNAP; score 1.0, reported cost $0.0394425. Infrastructure smoke only.

- [32_veribench_ranking_certified_judge](archive/32_veribench_ranking_certified_judge/REPORT.md): stopped 2026-09-22 — re-ranked VeriBench agents with a certified prompt on gpt-5.6-terra (826 cells, $0 API); superseded when §5.4/Table 5 (a carried-over VeriBench result) was cut from the paper.
- [29_proxy_validation](archive/29_proxy_validation/README.md): completed behavioral-proxy validation; negative/inconclusive finding.
- [30_proxy_trust_index_held_out_validity](archive/30_proxy_trust_index_held_out_validity/README.md): completed combined-target and within-problem diagnostics; new-family validation remains unstarted.
- [27_trust_plots](archive/27_trust_plots/README.md): completed figures from existing scores; reusable plotting functions remain in `py_src/cert_judge/`.

## Layout maintenance

Register new active work in [the inventory](archive/layout.json) with a concrete
current task, and add it here. Archive finished or parked work promptly; a future
idea or a paper citation does not make a finished experiment active.

Git moves tracked files but leaves ignored caches and local outputs behind. After
a pull, check and reconcile those leftovers without deleting unique evidence:

```bash
python3 py_src/cert_judge/experiment_layout.py --check
python3 py_src/cert_judge/experiment_layout.py --reconcile
```

Reconciliation never overwrites existing files; collisions are preserved under
`archive/.local_leftovers/` and remain ignored. Frozen records retain their original
provenance paths; executable consumers use the current archive locations.
