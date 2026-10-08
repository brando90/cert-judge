# Frozen E47 v5 probe construction

**Doc link:** [Main protocol](../../PROTOCOL.md)

This directory builds only the frozen experiment-39 identity, blank, reference theorem-deletion, candidate theorem-deletion, and reference implementation-bug probe rows for the 50-task E47 v5 fresh pool.
`build_probes_v5.py` imports the frozen experiment-39 `probes.py` transformations and compiles every available original source and transformed artifact with the pinned Lean project.
It makes no model-scoring call.

The driver copies allowed source bytes into ignored `expt_v1/private/probes_worker/input_bytes/`, stores compile receipts by source hash in ignored `compile_cache.jsonl`, and resumes successful hashes without recompilation.
Committed manifests expose logical identifiers, source/probe hashes, compilation receipts, and retrieval locations but no private candidate bytes or absolute private paths.

Run from the repository root:

```bash
python3 experiments/47_simulated_panel_v5_label_free_judge_screening/expt_v1/probes/build_probes_v5.py --jobs 2
```

**TLDR-end:** [cert-judge: 47_simulated_panel_v5_label_free_judge_screening > frozen probes] This owned worker constructs and Lean-compiles the frozen E39 structural probe subset for E47 without judge calls.
