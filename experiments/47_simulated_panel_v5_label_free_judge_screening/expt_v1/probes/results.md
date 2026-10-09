# Frozen v5 probe compilation

**Doc link:** [Runbook](cc.md)
**Status:** VERIFIED FOR SCOPED PUBLICATION
**Last updated:** 10-08-2026 18:57 PDT

| Phase | State | Evidence |
| --- | --- | --- |
| Frozen source inventory | DONE | 750 declared rows: 691 nonblank, 59 blank; 50 unique fresh references. |
| Lean provenance | DONE | Lean 4.22.0 / Mathlib grading project verified. |
| Probe construction and compilation | DONE | Terminal cache has 2,641 distinct source-hash-bound Lean compilations under one pinned Lean 4.22.0 environment fingerprint: 1,711 succeeded, 930 failed, and no completed receipt was rerun. |
| Manifest validation | PASS | Source/probe/summary SHA-256 values are mutually consistent; unique keys, retained candidate criterion rows, all declared denominators, G01 source recovery, level bounds, and cache accounting were independently checked. |

The frozen source inventory is complete: 750 declared candidates, comprising 691 nonblank hash-verified candidates and 59 source-declared blanks, with 50 distinct task references and all 50 G01 candidate hashes verified.
The sanitized probe manifest has 2,722 rows: 750 retained `crit` rows, 1,474 `ms_cand` rows, 198 `ms_gold` rows, 200 `bm_gold` rows, 50 `ident` rows, and 50 `blank` rows.
The 930 terminal failed compilations are preserved as 421 elaboration, 392 type-or-elaboration, 110 parse, 4 unresolved-import, and 3 timeout receipts; the timeouts are neither rerun nor interpreted as demonstrated Lean errors.
The terminal artifact SHA-256 values are source `c032ac46e92dfe2ed326b1372e21f8d69a6d2b719fffc1ca379ea33a507493aa`, probe `d41ceff706a47eebc6310935f983f4837c1e22b4a12091d0b15fc73abe4b743a`, and summary `18771989748e56fc15ad9f1c5658ac259276482ecb006043c0c0b28a85eca62d`.
`uv run --no-project --with pytest pytest -q probes/tests/test_build_probes_v5.py` passed 4/4 tests, and the independent terminal-manifest audit passed.
The repository-wide experiment-layout check is unavailable in this sparse scoped checkout because `experiments/archive/layout.json` is absent; this is not used to infer probe validity.
No judge score, criterion statistic, semantic weakening claim, reference repair, or model-scoring call has been made by this worker.


**TLDR-end:** [cert-judge: 47_simulated_panel_v5_label_free_judge_screening > frozen probes] The full frozen E39-derived E47 probe pool has terminal Lean evidence, verified manifests, and zero judge calls.
