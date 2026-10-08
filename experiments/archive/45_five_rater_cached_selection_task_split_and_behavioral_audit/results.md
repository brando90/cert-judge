# Five-rater cached comparison results ledger

**Doc link:** [Verified report](RESULTS_five_rater_comparison.md)

**Status:** DONE — verified, merged to main and archived.
**Last updated:** 10-07-2026 21:20:11 PDT

| Phase | Status | Verified evidence |
|---|---|---|
| Current ratings, task split and provenance | DONE | 345 observations / 75 outputs / 25 tasks; 177 manifest hashes; original 10/5/10 task split |
| Frozen selection receipt | DONE | 13/15 shared validation outputs below 14 required; selected rule remains null |
| Cached utility comparison | DONE | 42 declared views, 34 computed and eight unavailable; 10,000 paired task draws |
| Modern proxy and current-rater comparisons | DONE | 24 proxy views; all 345 ratings exported individually; 20 rater agreement views |
| Historical-score sensitivity | DONE | 15 fixed-score views; no old validation/test labels used |
| Behavioral evidence | DONE | 60 semantic configurations and 90 gaming cells reproduced; no new scores |
| Stronger integrated design | DONE | Strict weakening/countermodel and equivalent gaming plan; proposed 300 cells, no calls admitted |
| Deterministic verification | DONE | Four numerical/coverage tests; 2,408 independent point checks; sources unchanged |

All three scientific jobs completed on skampere2 with exit 0. Their launch, heartbeat, completion and log evidence is retained in `research_notes/recovery_10-07-2026/job-*/` at repository root. Model ownership recovered once; the stalled model process was stopped, and healthy numerical work was adopted. No paid inference, new human labels, benchmark changes, or manuscript edits.

Main five-rater test-only result: frozen proxy Spearman 0.815 [0.411, 0.950] versus fixed human-rating rubric 0.826 [0.494, 0.936]; paired difference −0.012 [−0.198, 0.186], p-val=n/a. Support is 29/30 outputs across ten tasks; 9,999/10,000 paired task-bootstrap draws are finite. Intervals condition on existing raters/caches/choices. Detailed Pearson, Kendall, absolute error, signed bias and repeated-score variability are in the report.

**TLDR-end:** [cert-judge: 45_five_rater_cached_selection_task_split_and_behavioral_audit] Five-current-rater cached analysis is complete and archived; association persists without demonstrated selection advantage. New validation selection stays unavailable, and the next study requires stronger valid probes before new scoring.

Confirmed publication: [pull request #56](https://github.com/brando90/cert-judge/pull/56), merge `df3af48f66ef402b7ef8ab1573a7158d8ea4a834`; verified source `3735d94309db6c3585da4f70f02ff7a7851368d0`. Fetched main has identical contents.
