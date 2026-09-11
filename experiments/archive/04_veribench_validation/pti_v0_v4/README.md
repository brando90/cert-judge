# PTI-v0 v4 frozen experiment

**TLDR:** This directory freezes the PTI-v0 protocol and base-artifact pool before any bridge statistic. Generated zero-spend audit outputs live in the adjacent `results_pti_v0_v4/` directory.

The reusable numerical implementation is `py_src/cert_judge/pti_v0.py`; Lean-safe transformations are in `py_src/cert_judge/probe_validation.py`; the no-API experiment entry point is `../run_pti_v0.py`.

## Goal

Evaluate whether the frozen, label-free `PTI_v0` proxy ranks judge configurations like the paired human `TI_m1` criterion, without conflating structural probe failures, missing judge scores, or behavioral failures. This directory freezes the design before any primary-judge result or bridge statistic is observed.

## Structure

```text
pti_v0_v4/
├── README.md
├── PROTOCOL.md
├── frozen_config.json
├── judge_manifest.csv
├── base_pool_manifest.json
├── score_schema.json
└── writing.tex

../results_pti_v0_v4/
├── panel_audit/
├── probe_validity_manifest.json
├── score_requests.json
├── local_control_scores.json
├── criterion/
├── properties/
├── properties_local_controls/
└── bridge/
```

## Dependencies

- Pinned Lean project: `data/veribench_dataset/lean_src/` with Lean/Mathlib 4.22.
- Candidate pool: `data/generated_agents/`; gold precedence is frozen in `base_pool_manifest.json`, and score references reproduce Exp16’s final-theorem/lemma-block preprocessing.
- Human criterion source: `../results_exp16_final_robust/detail_rows.csv` plus the audited strict/lenient label files. LLM rows require exact non-fallback legacy-cache lineage; deterministic controls are recomputed locally.
- Review dependency order: ultimate-utils PR #44, then cert-judge PR #38. Exp27 remains the inner item-level diagnostic and is not duplicated here.
- Any future LLM scoring requires a separate CLI-only mechanism, exact quote, and explicit approval. This pipeline cannot load credentials or call a provider.

## Method

The authoritative steps and abort rules are in `PROTOCOL.md`. The commands below freeze inputs, prove the included transformations compile, bind score cells to hashes and prompt provenance, materialize only local controls, inventory admissible caches, and emit a bridge-blocked status until primary scores satisfy every gate.

Run from the repository root:

```bash
python experiments/04_veribench_validation/run_pti_v0.py freeze-config --no-api
python experiments/04_veribench_validation/run_pti_v0.py freeze-pool --no-api
python experiments/04_veribench_validation/run_pti_v0.py audit-panel --no-api
python experiments/04_veribench_validation/run_pti_v0.py audit-probes --workers 8 --no-api
python experiments/04_veribench_validation/run_pti_v0.py build-requests --no-api
python experiments/04_veribench_validation/run_pti_v0.py materialize-local-controls --no-api
python experiments/04_veribench_validation/run_pti_v0.py inventory-cache --no-api
python experiments/04_veribench_validation/run_pti_v0.py quote-spend --transforms ALPHA --dry-run --no-api --out experiments/04_veribench_validation/results_pti_v0_v4/spend_alpha_only.json
python experiments/04_veribench_validation/run_pti_v0.py quote-spend --transforms ORIGINAL ALPHA --dry-run --no-api --out experiments/04_veribench_validation/results_pti_v0_v4/spend_alpha_property_from_empty_cache.json
python experiments/04_veribench_validation/run_pti_v0.py quote-spend --transforms ALL --dry-run --no-api --out experiments/04_veribench_validation/results_pti_v0_v4/spend_full_pti_v0.json
python experiments/04_veribench_validation/run_pti_v0.py quote-spend --transforms RENAME REORDER STYLE --dry-run --no-api --out experiments/04_veribench_validation/results_pti_v0_v4/spend_optional_diagnostics.json
python experiments/04_veribench_validation/run_pti_v0.py compute-properties --cache-only --no-api
python experiments/04_veribench_validation/run_pti_v0.py compute-properties --scores experiments/04_veribench_validation/results_pti_v0_v4/local_control_scores.json --cache-only --no-api --out-dir experiments/04_veribench_validation/results_pti_v0_v4/properties_local_controls
python experiments/04_veribench_validation/run_pti_v0.py compute-criterion --no-api
python experiments/04_veribench_validation/run_pti_v0.py simulate-sesoi --no-api
python experiments/04_veribench_validation/run_pti_v0.py compute-bridge --properties experiments/04_veribench_validation/results_pti_v0_v4/properties_local_controls/properties.json --no-api
```

These commands never initialize an inference provider or read credentials. `audit-probes` first builds the three local VeriBench support modules and binds the resolved Lake/olean inventory. `materialize-local-controls` deterministically reproduces the frozen edit-distance and seeded-random baselines; it does not fill any LLM score. `compute-criterion` rejects historical API/parse fallbacks rather than treating 0.5 as a neutral score. The first quote is incremental alpha-only, the second includes the uncached original side required to compute `P_eqalpha`, and `ALL` quotes every frozen score cell. An LLM score run is intentionally outside this CLI and requires explicit approval after an exact quote.

`compute-bridge` writes an honest `NOT_COMPUTABLE` status when properties are absent. If properties exist, it also requires the full SHA of a pre-bridge commit containing the byte-identical property file.

## Status

| Step | Status | Evidence |
|---|---|---|
| Protocol, metric, vectors, schema | Done | This directory, `docs/spec/PTI_V0.md`, and `tests/` |
| Pool and 72-row panel freeze | Done | `base_pool_manifest.json` and adjacent `panel_audit/` |
| Full structural probe audit | Done | Adjacent `probe_validity_manifest.json`: 470 rows under pinned Lean 4.22 |
| Local controls and human criterion | Done / fail-closed | Controls complete; seven criteria at 72/72, one primary `NOT_COMPUTABLE` at 64/72 after eight fallback rows were excluded |
| Primary LLM properties | Blocked on approval and admissible scores | No inference mechanism exists in this CLI |
| Outer bridge and paper figure | Blocked by property hard gate | Must follow a committed complete primary property table |
| Active manuscript revision | Not started | No machine-readable bridge result exists |
| W&B Report | N/A for blocked zero-spend preparation | Required only after an approved experiment completes |
