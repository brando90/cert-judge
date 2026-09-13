# Proxy validation follow-up results

**TLDR-start:** [cert-judge: proxy-followups] Version3 independently confirms that the string-control ordering comparison is inconclusive within problems; version2 did not establish proxy validity after adding repeat stability. No new inference or human labeling ran.

**Status:** RUNNING (publication only; version3 analysis and review DONE, started 2026-09-13 11:46 PDT).
**Last updated:** 2026-09-13 12:03 PDT

| Version3 phase | Status | Evidence |
|---|---|---|
| Protocol and input validation | DONE | Locked protocol; 8 judges × 72 candidates × 3 repeats; 24 problems |
| Within-problem audit | DONE | All three human rubric views INCONCLUSIVE |
| Pilot inventory | DONE | 18 candidates; 160 judge/cell keys; 480 repeat scores; no bug/missing-spec probes |
| Independent review and fixes | DONE | Strongest Codex fallback PASS, two minor fixes; 90 tests pass |
| Report and main publication | IN PROGRESS | Pull request 43 |

Average-rubric within-problem accuracy is **0.477** for the string control and **0.576** for Sonnet checklist; their difference is −0.098 with a conditional 95% interval [−0.280, 0.071]. All five paired intervals cross zero. This does not establish label invalidity, a composition explanation or new-family generalization.

Version3: [protocol](expt_v3/PROTOCOL.md), [report and figure](expt_v3/results/report.md), [review and fixes](expt_v3/QA.md), [meeting note](meeting_2026-09-14.md). The deterministic six-problem cache selection is not ready for complete four-property validation. Fresh-family inference remains unstarted.

## Preserved version2 results

Source pull requests: [41](https://github.com/brando90/cert-judge/pull/41) and [42](https://github.com/brando90/cert-judge/pull/42).

Version2 review evidence: [expt_v2/QA.md](expt_v2/QA.md).

The [full report](expt_v2/results/report.md) contains figures and source-linked tables. The [Weights & Biases report](https://wandb.ai/brando-su/cert-judge-pti-v0/reports/Experiment-30-—-Combined-trust-and-zero-handling-diagnostics--VmlldzoxNzkxMjU0OA==) and [run](https://wandb.ai/brando-su/cert-judge-pti-v0/runs/cj30v26ce871c57089a715) are published. The immutable local summary is [results_summary_2026-09-10__23-07-40.md](expt_v2/results/results_summary_2026-09-10__23-07-40.md).

Version2 final verification: 173 tests passed; one unchanged Lean integration test was excluded. The independent review passed with zero critical or major issues and reproduced all nine numerical outputs.

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
