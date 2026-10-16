# Semantic-margin cached judge-selection run

**Status:** COMPLETE — historical cached-data analysis
**Last updated:** 10-16-2026 14:02 PDT

| Phase | Status | Evidence |
|---|---|---|
| Definition freeze | COMPLETE | Commit `b34a633`; 163-file resolved input manifest and 12 deterministic tests. |
| Cached selection | COMPLETE | 56 configuration overview and per-probe/task components; selector digest `5cce7bd…523bd858`; selection receipt states `human_outcomes_read=false`. |
| Human comparison | COMPLETE | Test: 29/30 common files, 10 tasks; margin Spearman 0.815 [0.414, 0.950] versus fixed H2 0.826 [0.507, 0.934], paired delta -0.012 [-0.197, +0.183]. Validation unavailable: 13/15 (<14 required). |
| Verification and publication | COMPLETE | 15 deterministic tests; experiment-46 reproduction PASS across 550 comparable cells at tolerance 1e-12. |

New judge calls: 0. Runtime acknowledgement: skampere1, CPU-only cached-data analysis, one worker, authenticated Codex CLI execution profile `gpt-5.6-terra` / high with native bypass permissions recorded in `dispatch.json`; no provider key or measured-model call used. The maximum-training-margin selector is `t2_sonnet5|D0`; deletion total-variation distance remains unavailable under the frozen two-repeat rule. Full report: [RESULTS_semantic_margin.md](RESULTS_semantic_margin.md).

**TLDR-end:** [cert-judge: 50_semantic_effect_margin_cached_judge_selection_train_val_test] Completed frozen cached-data semantic-margin selection; the test comparison is inconclusive and validation support is unavailable.
