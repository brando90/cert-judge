# Proxy validation follow-up results

**TLDR-start:** [cert-judge: proxy-followups] Completed and independently reviewed all follow-ups. The frozen and floored proxies remain negatively associated with the combined target among primary judges, with intervals crossing zero. These are exploratory analyses of previously inspected data, not a fresh held-out test.

**Status:** DONE. Analyses, independent review and report publication complete; this record accompanies the final main-branch commit.
**Last updated:** 2026-09-10 23:08 PDT

| Phase | Status | Evidence |
|---|---|---|
| Read pull requests 41 and 42 | DONE | Both merged; experiment 30 uses human agreement alone. |
| Verify input coverage | DONE | 8 judges × 72 candidates × 3 repeats; 24 problems. |
| Combined target and zero-handling analyses | DONE | Both frozen outputs reconstructed; all declared sensitivities computed. |
| Shared-problem uncertainty and family diagnostics | DONE | 2,000 problem draws; 32 synthetic settings × 2,000 datasets; only two primary model families. |
| Independent review | DONE | PASS, zero critical or major issues; every numerical output reproduced. |
| Report publication | DONE | New experiment-30 run and report verified; frozen experiment-29 artifacts preserved. |

Source pull requests: [41](https://github.com/brando90/cert-judge/pull/41) and [42](https://github.com/brando90/cert-judge/pull/42).

Review evidence: [expt_v2/QA.md](expt_v2/QA.md).

The [full report](expt_v2/results/report.md) contains figures and source-linked tables. The [Weights & Biases report](https://wandb.ai/brando-su/cert-judge-pti-v0/reports/Experiment-30-—-Combined-trust-and-zero-handling-diagnostics--VmlldzoxNzkxMjU0OA==) and [run](https://wandb.ai/brando-su/cert-judge-pti-v0/runs/cj30v26ce871c57089a715) are published. The immutable local summary is [results_summary_2026-09-10__23-07-40.md](expt_v2/results/results_summary_2026-09-10__23-07-40.md).

Final verification: 173 tests passed; one unchanged Lean integration test was excluded. The independent review passed with zero critical or major issues and reproduced all nine numerical outputs.

| Proxy, primary judges only | Spearman against combined trust | Conditional 95% problem interval |
|---|---:|---|
| Frozen Proxy Trust Index | −0.354 | [−0.707, 0.709] |
| Artifact-factor floor 0.001 | −0.600 | [−0.975, 0.600] |
| Mean within each property, geometric mean across properties | −0.600 | [−0.900, 0.600] |

These are exploratory results on previously inspected data. Intervals condition
on observed labels, repeat calls and judge configurations; they do not validate
new families. Both the negative point estimates and the wide intervals remain
visible. No frozen data changed, no new human labels were opened, and no new
model inference ran.

**TLDR-end:** [cert-judge: proxy-followups] Zero handling improves resolution without establishing the intended ranking; the reviewed report preserves the negative findings and the limits of the current panel.
