# Frozen v5 probe compilation

**Doc link:** [Runbook](cc.md)
**Status:** RUNNING (started 10-08-2026 11:01 PDT)
**Last updated:** 10-08-2026 11:33 PDT

| Phase | State | Evidence |
| --- | --- | --- |
| Frozen source inventory | DONE | 750 declared rows: 691 nonblank, 59 blank; 50 unique fresh references. |
| Lean provenance | DONE | Lean 4.22.0 / Mathlib grading project verified. |
| Probe construction and compilation | IN PROGRESS | Hash-resumable driver process 689488 is running in tmux with exactly two Lean workers; 99 hash-bound receipts are preserved (40 successful, 59 failed, 0 timeouts) and will not be rerun. No model calls. |
| Manifest validation | PENDING | Awaiting terminal compile receipts. |

All 50 initially absent G01 candidate sources have now been delivered through the permitted pinned v5 path and independently verified against their declared SHA-256 hashes. The running cache contains these bytes; terminal publication will include them without broader source traversal.
The host is deliberately held to two workers under high shared load. With 741 distinct base hashes and up to 3,014 original/deletion proposals before variable frozen bug-mutation searches, completion is expected to take hours; the resumable source-hash cache preserves every completed compilation.
No judge score or criterion statistic has been computed by this worker.


**TLDR-end:** [cert-judge: 47_simulated_panel_v5_label_free_judge_screening > frozen probes] The frozen E39-derived E47 probe compilation is being launched on the full declared fresh pool with two Lean workers and zero judge calls.
