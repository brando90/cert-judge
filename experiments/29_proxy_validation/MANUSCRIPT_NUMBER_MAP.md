# ICLR 2027 manuscript number and result-status map

**TLDR-start:** [cj: pti-v0] Every new PTI-v0 number in the ICLR 2027 manuscript is bound below to a committed machine-readable authority and a deterministic reproduction command. Historical calibration numbers remain explicitly separate; malformed legacy probe plots and an unbound downstream table were removed rather than carried forward.

## Scope and authority

This map covers the new Experiment 29 claims in `paper_latex/ICLR_2027_submission/main.tex`, the reused Experiment 27 item-level diagnostic, and the historical audit/registered-negative facts retained in the main text. It does not relabel any historical `TI_var`/JTI result as `PTI_v0`.

Canonical Experiment 29 authorities:

- `results/batch_manifest.json` — batch and CLI invocation counts.
- `results/scores.json` — accepted normalized scores, unique-cell inventory, record count, source, and provider-API spend.
- `results/properties/properties.json` and `results/properties/property_table.csv` — coverage, per-property estimates, exact-zero diagnoses, PTI values, and artifact-cluster intervals.
- `results/criterion/criterion.json` and `results/criterion/criterion.csv` — 72-item human-criterion estimates and paired-item intervals.
- `results/bridge/bridge_pti_v0.json` — primary and pooled outer bridge, per-property sensitivity, family leave-one-out status, and valid bootstrap counts.
- `results/bridge/bridge_eq_bm_ms.json` — labeled three-property sensitivity.
- `results/sesoi/sesoi_simulation.json` — frozen SESOI/power simulation.
- `results/figures/outer_bridge_source_data.{csv,json}` — plotted points and both-axis intervals.
- `results/figures/ti2prime_scatter_gpt53_p4_source.json` — repository-relative source bindings, item-level statistics, and uncertainty for the reused Experiment 27 diagnostic.
- `experiments/archive/04_veribench_validation/results_pti_v0_v4/probe_validity_manifest.json` — judge-free structural pool and valid-probe counts.

The property-table authority was content-frozen before the bridge; its committed CSV SHA-256 is `7a904f31a6dbd626a728e44fd7a00043c61b5e1630937986f111a0be4af15c0a`. The identity-bearing public VCS identifier is deliberately excluded from blinded submission material.

## New Experiment 29 manuscript numbers

| Manuscript claim | Exact value(s) | Machine-readable authority / field | Status |
|---|---|---|---|
| Metric and execution versions | `PTI_v0`; exact schema/protocol field `PTI_v0_cli_protocol_v5` (human-facing shorthand: v5) | `frozen_config.json:.metric_version,.schema_version`; `results/scores.json:.metric_version,.protocol_version` | Bound |
| Exact v4 panel | `NOT_RUN` | `frozen_config.json:.v4_status`; `results/v4_model_rejection_evidence.md` | Bound; never pooled with v5 |
| Actual scoring panel | `gpt-5.6-terra`; requested/scoring `claude-sonnet-5` | `results/batch_manifest.json:.batches[].model`; `results/raw_batches/*.json:.requested_model,.usage.requested_model` | Bound; Codex JSONL exposes no served-model field, so Terra is requested-by-argument, not observed telemetry |
| Claude auxiliary telemetry | `claude-haiku-4-5` on all 258 accepted Claude CLI tasks | Claude `results/raw_batches/*.json:.usage.canonical_models`; 258 = 43 batches × 3 repeats × 2 prompts | Bound; Sonnet-only execution is not claimed |
| Subscription authentication and spend | ChatGPT + first-party `claude.ai` Max; `$0` provider-API spend | `results/cli_auth_status.json`; `results/scores.json:.provider_api_spend_usd` | Bound |
| Accepted CLI tasks | `774/774` | `results/batch_manifest.json:.cli_invocation_count` and `258 × 3` | Complete |
| Unique score cells | `4,728/4,728` | `results/scores.json:.expected_unique_cells,.complete_unique_cells` | Complete |
| Bound score records | `14,184` = 4,728 × 3 | `results/scores.json:.record_count,.records` | Complete |
| Excluded failed attempts | `4` exhausted-batch failure records (12 attempts), each batch later completed; accepted artifacts additionally record `34` unretained in-run retries (`attempt` 2: 24, 3: 5), so at least `820` CLI invocations produced the 774 accepted tasks | Four `results/raw_batches/*.failure.*.json` files; `results/raw_batches/*__r[0-2].json:.attempt`; accepted inventory remains complete in `scores.json` | Excluded, not silently accepted |
| Invalid accepted / quarantined tasks | `0/0` | Schema validation of every accepted `results/raw_batches/*__r[0-2].json`; `RESULTS_QA.md` records the reconstruction | Complete |
| Typed structural pool | `470` candidate artifacts | `.../results_pti_v0_v4/probe_validity_manifest.json:.artifact_count` | Audited |
| Structurally valid probe counts | equality `86`; bug ladder `49`; missing-spec ladder `63`; alpha `67` | Same manifest: `.valid_probe_counts` | Audited |
| Property and criterion coverage | `1.0` for every required judge/property/view | `properties.json:.judges[].properties.*.coverage`; `criterion.json:.records[].views.*.coverage` | Complete |
| Primary/control panel | `5` primaries, `3` controls, `8` total | `frozen_config.json:.judges`; `bridge_pti_v0.json:.source_rows[].role` | Frozen |
| Frozen property table | all 8 rows and four factors shown in manuscript Table 3 | `results/properties/property_table.csv` and `.judges[]` in `properties.json` | Byte-bound before bridge |
| Exact-zero primary PTI values | four of five primary point estimates equal exactly `0` | `properties.json:.judges[] | select(.role=="primary") | .PTI_v0.value` | Computed; zero is not missingness |
| Sonnet–P8 PTI | `0.8114197682`, 95% interval `[0.7820434991, 0.8390616239]` | `properties.json`, Sonnet–P8 `.PTI_v0.value,.bootstrap` | Computed |
| PTI and per-property uncertainty | all eight PTI intervals and all 32 property intervals in manuscript Table 3 / Appendix table | `properties.json:.judges[].PTI_v0.bootstrap,.property_bootstrap`; rounded to three decimals in the manuscript | Computed; Sonnet–P4 PTI is `0` with interval `[0,0.8467228651]` |
| Validated primary alpha properties | Terra `0`, `0.8827563824`, `0.9386547798`; Sonnet `0.9366158880`, `0.9035832943` | `properties.json:.judges[].properties.P_eqalpha.value` | Computed |
| Human criterion sample | `72` paired items per judge; median over three repeats | `criterion.json:.human_panel_count`; `.records[].views.average.repeat_aggregation,required_count` | Computed |
| Primary bridge | Spearman `-0.3535533906`; Kendall tau-b `-0.3162277660`; 95% interval `[-1, 0.3952847075]`; `6,647/10,000` valid; `n=5` | `bridge_pti_v0.json:.analyses.primaries` | Computed |
| Three-property bridge sensitivity | same rank statistics and interval as the primary | `bridge_eq_bm_ms.json:.analyses.primaries` | Computed, labeled sensitivity |
| Pooled-control sensitivity | Spearman `-0.2474358297`; Kendall tau-b `-0.2142857143`; 95% interval `[-0.8164965809, 0.2567762955]`; `6,521/10,000` valid; `n=8` | `bridge_pti_v0.json:.analyses.pooled_with_controls` | Computed, secondary |
| Leave-one-family-out | both families `NOT_COMPUTABLE` | `bridge_pti_v0.json:.leave_one_family_out` | Honest non-result |
| Per-property bridge sensitivity | `P_eq=-0.3535533906`, `P_bm=-0.2236067977`, `P_ms=-0.2236067977`, `P_eqalpha=0.6`; all intervals include zero | `bridge_pti_v0.json:.exploratory_per_property` | Exploratory; not used for selection |
| Frozen SESOI | Spearman `0.5` | `frozen_config.json:.statistics.sesoi_rho`; `sesoi_simulation.json:.sesoi_rho` | Frozen before result |
| SESOI simulation at true rho 0.5 | positive-rule power `0.271`; mean realized Spearman `0.47473`; point-threshold rate `0.6067`; false-pass rate `0.2583333`; top-1 retention `0.4531372` | `sesoi_simulation.json:.rows[] | select(.rho_target==0.5)` | Derived with frozen DGP/seed |
| Primary interpretation | below SESOI and inconclusive about zero | Point and upper CI from `bridge_pti_v0.json`; frozen rule in `sesoi_simulation.json:.bridge_decision_rule` | No positive bridge, PASS-SCREEN, deployment, causal, or savings claim |

## Reused item-level criterion diagnostic

The appendix figure is not an Experiment 29 outer-bridge point. It is the existing Experiment 27 diagnostic for `gpt-5.3-codex|P4_CHECKLIST` over 72 paired items.

| Manuscript claim | Value | Authority | Status |
|---|---:|---|---|
| Item count | 72 | `results/figures/ti2prime_scatter_gpt53_p4_source.json:.n_items` | Reused, not duplicated |
| Spearman | `0.4796677727` (shown as `0.48`) | Same sidecar: `.spearman`; source hashes under `.source_bindings` | Bound |
| Repeat instability | `0.0495473336` (shown as `0.05`) | Same sidecar: `.repeat_instability` | Bound |
| TI2-prime | `0.6752047938` (shown as `0.675`) | Same sidecar: `.ti2prime` | Bound |
| Kendall tau-b and paired-item interval | `0.3943471708`; `[0.2713917630,0.6516681223]` (shown as `0.39`; `[0.27,0.65]`) | Same sidecar: `.kendall_tau_b,.spearman_bootstrap`; 2,000 paired-item replicates at seed 0 | Bound; historical illustrative diagnostic |
| Figure asset | PDF SHA-256 `43420c246bcadfcd09f9949bb172cfdfe433bb415980cb505a0918b548bbc7cc` | Same sidecar: `.source_bindings.figure_pdf,.paper_copy_sha256` | Copied byte-identically into paper tree |

## Retained historical/audit facts

These facts are context, not PTI-v0 evidence:

| Main-text fact | Authority | Status |
|---|---|---|
| 75 rated pairs = 25 problems × 3 generations; 72 analyzed pairs | `experiments/archive/26_human_label_dataset_audit/results/audit_summary.json`, `RECONCILIATION.md`, and `aligned_panel_n75.tsv` | Audited; appendix explains 75-vs-72 and duplicate policy |
| Published 72-row rubric-stability statistics: Spearman `0.249`, Pearson `0.375`, QWK `0.372`, MAE `0.771` | `experiments/archive/04_veribench_validation/results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json`; alternative duplicate-policy recomputations in Exp26 `RECONCILIATION.md` | Historical published pipeline; discrepancy disclosed |
| Revised-protocol pool: 5 raters, 343 labels, 78 pairs, 63 shared | Exp26 `audit_summary.json:.heldout_pool`; Exp22 `results/results.json` | Audited |
| Cross-protocol Spearman approximately `0.13` on 63 shared pairs and pool ceiling approximately `0.87` | `experiments/archive/22_pooled_heldout_and_noise_ceiling/results/results.json` and `REPORT.md` | Criterion drift; not pooled with PTI-v0 |
| First registered screen: `n=14`, underpowered | `experiments/archive/23_reanchored_calibration/results/results.json` and `REPORT.md` | Historical registered outcome |
| Expanded registered screen: `n=32`, strongest `|rho|=0.3911`, Holm `p=0.2484`; LOO `rho=0.2416`, `p=0.4908` | `experiments/archive/24_expanded_panel_cli/results/pass2_full_screen_results.json` | Historical registered negative |
| Calibration-era `PTI_var` associations | `experiments/archive/04_veribench_validation/results_exp16_final_robust*` and `results_exp28_varaware_*` | Retained only in appendix as `LEGACY—NOT PTI-v0` |

The workshop-era alpha mean `0.399`, its malformed-transform plots, early degradation plots that predate the structural gate, and a downstream theorem-ranking table without a located machine-readable result authority were removed from the submitted PDF.

## Deterministic reproduction commands

Run from repository root in the project `uv` environment:

```bash
python experiments/29_proxy_validation/run_pti_v0_cli.py status

python experiments/archive/04_veribench_validation/run_pti_v0.py compute-properties \
  --probe-manifest experiments/archive/04_veribench_validation/results_pti_v0_v4/probe_validity_manifest.json \
  --requests experiments/29_proxy_validation/results/score_requests.json \
  --config experiments/29_proxy_validation/frozen_config.json \
  --scores experiments/29_proxy_validation/results/scores.json \
  --out-dir experiments/29_proxy_validation/results/properties \
  --bootstrap-iters 10000 --seed 0 --no-api

python experiments/29_proxy_validation/run_pti_v0_cli.py compute-criterion

python experiments/archive/04_veribench_validation/run_pti_v0.py compute-bridge \
  --properties experiments/29_proxy_validation/results/properties/properties.json \
  --criterion experiments/29_proxy_validation/results/criterion/criterion.json \
  --variant PTI_v0 \
  --prebridge-commit <PREBRIDGE_COMMIT_FROM_ANONYMIZED_BUNDLE> \
  --bootstrap-iters 10000 --seed 0 \
  --out experiments/29_proxy_validation/results/bridge/bridge_pti_v0.json \
  --no-api

python experiments/archive/04_veribench_validation/run_pti_v0.py simulate-sesoi \
  --criterion experiments/29_proxy_validation/results/criterion/criterion.json \
  --rhos 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 \
  --draws 10000 --seed 0 --sesoi 0.5 --decision-bootstrap-iters 10000 \
  --out experiments/29_proxy_validation/results/sesoi/sesoi_simulation.json \
  --no-api

MPLBACKEND=Agg python experiments/29_proxy_validation/generate_bridge_figure.py
python experiments/27_trust_plots/run_ti2prime_demo.py

cd paper_latex/ICLR_2027_submission
SOURCE_DATE_EPOCH=1787763818 FORCE_SOURCE_DATE=1 TZ=UTC \
  latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Primary outer-figure source asset SHA-256 is `dd91088665e36525649d005f81983a9ed3c94a3b5a8999ed925d82a8d7b4a745` (regenerated during the final Mega-QA pass with a disclosed horizontal offset for judges tied at identical PTI values; the plotted values and `outer_bridge_source_data.{csv,json}` are byte-unchanged); the paper copy is required to match it byte-for-byte.

The reproducible manuscript PDF SHA-256 is `a35e582f936635dbdf6d21b1a17aba27ad5d5d9494d5459b7c477da8ba23644e`; two forced builds with the command above produced identical bytes after the 2026-08-31 provenance-wording correction.

For double-blind distribution, this map and the supplement use repository-relative paths and content hashes. Internal status files, W&B links, local absolute paths, Git history, and public VCS identifiers are excluded by `paper_latex/ICLR_2027_submission/ANONYMIZED_SUPPLEMENT_ALLOWLIST.md`.

**TLDR-end:** [cj: pti-v0] The manuscript’s new result is fully traceable and fails to support the registered positive bridge: it is below the 0.5 SESOI and inconclusive about zero. Legacy malformed probes and unbound numbers are excluded, not repaired by relabeling.
