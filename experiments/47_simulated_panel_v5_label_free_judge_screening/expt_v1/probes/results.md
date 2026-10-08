# Frozen v5 probe compilation

**Doc link:** [Runbook](cc.md)
**Status:** RUNNING (started 10-08-2026 11:01 PDT)
**Last updated:** 10-08-2026 11:01 PDT

| Phase | State | Evidence |
| --- | --- | --- |
| Frozen source inventory | DONE | 750 declared rows: 691 nonblank, 59 blank; 50 unique fresh references. |
| Lean provenance | DONE | Lean 4.22.0 / Mathlib grading project verified. |
| Probe construction and compilation | IN PROGRESS | Verified driver process 325184 has two Lean children and 10 successful cached compile receipts at 10-08-2026 11:04 PDT. No model calls. |
| Manifest validation | PENDING | Awaiting terminal compile receipts. |

The allowed source copy lacks bytes for 50 nonblank G01 candidate declarations; they will remain explicit `missing_source` criterion rows, never recovered by reading outside the source allowlist.
No judge score or criterion statistic has been computed by this worker.


**TLDR-end:** [cert-judge: 47_simulated_panel_v5_label_free_judge_screening > frozen probes] The frozen E39-derived E47 probe compilation is being launched on the full declared fresh pool with two Lean workers and zero judge calls.
