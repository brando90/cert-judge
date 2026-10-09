# Frozen E47 v5 probe construction

**Doc link:** [Main protocol](../../PROTOCOL.md)

This directory builds only the frozen experiment-39 identity, blank, reference theorem-deletion, candidate theorem-deletion, and reference implementation-bug probe rows for the 50-task E47 v5 fresh pool.
`build_probes_v5.py` imports the frozen experiment-39 `probes.py` transformations and compiled every available original source and transformed artifact with the pinned Lean project.
It makes no model-scoring call.

The driver copies allowed source bytes into ignored `expt_v1/private/probes_worker/input_bytes/`, stores compile receipts by source hash in ignored `compile_cache.jsonl`, and resumes successful hashes without recompilation.
Committed manifests expose logical identifiers, source/probe hashes, compilation receipts, and retrieval locations but no private candidate bytes or absolute private paths.
To reproduce the ignored source-byte cache, use the command below against the declared source manifests; it rechecks every bound SHA-256 digest before copying any bytes and reuses only cache entries whose Lean environment hash matches.

Run from the repository root:

```bash
python3 experiments/47_simulated_panel_v5_label_free_judge_screening/expt_v1/probes/build_probes_v5.py --jobs 2
```

## Verified terminal inventory (10-08-2026 18:57 PDT)

The terminal manifests retain all 750 declared candidate criterion rows: 691 nonblank hash-verified sources and 59 source-declared blanks across 50 unique tasks and 50 hash-verified references, including all 50 recovered G01 candidate files.
The source, probe, and compilation-summary SHA-256 digests are respectively `c032ac46e92dfe2ed326b1372e21f8d69a6d2b719fffc1ca379ea33a507493aa`, `d41ceff706a47eebc6310935f983f4837c1e22b4a12091d0b15fc73abe4b743a`, and `18771989748e56fc15ad9f1c5658ac259276482ecb006043c0c0b28a85eca62d`.
The cache contains 2,641 unique source-hash-bound Lean compilations under one exact Lean 4.22.0 environment fingerprint: 1,711 succeeded and 930 failed (421 elaboration, 392 type-or-elaboration, 110 parse, 4 unresolved-import, and 3 timeout receipts).
The published probe denominator is 2,722 rows: 750 `crit`, 1,474 `ms_cand`, 198 `ms_gold`, 200 `bm_gold`, 50 `ident`, and 50 `blank`; all 750 `crit` rows remain retained independently of candidate compilation.
The terminal deterministic audit confirmed unique source item and probe identifiers, source/reference hash equality, G01 coverage, ladder-level bounds, cache/summary agreement, and both terminal-manifest digests.

Compilation is structural evidence only: it neither demonstrates semantic weakening nor validates a judge score.
The three timeouts remain distinct terminal infrastructure outcomes and were not rerun or reclassified as Lean errors.
Raw source bytes, generated Lean artifacts, diagnostics, and the cache remain ignored under `expt_v1/private/probes_worker/`; only sanitized logical identifiers, hashes, and receipt summaries are published here.

**TLDR-end:** [cert-judge: 47_simulated_panel_v5_label_free_judge_screening > frozen probes] The completed frozen E39 structural probe subset for E47 is hash-verified and Lean-compiled without judge calls.
