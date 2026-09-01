# ICLR 2027 anonymized supplement allowlist

**TLDR:** Build the review supplement only from the content-bound artifacts below, using sanitized derivatives where stated. Never distribute internal status, W&B, authentication, local-path, Git-history, or public-commit records during double-blind review.

## Directly allowed

These paths contain repository-relative provenance and passed the identity-string scan:

- `experiments/29_pti_v0_cli_bridge/frozen_config.json`
- `experiments/29_pti_v0_cli_bridge/results/batch_manifest.json`
- `experiments/29_pti_v0_cli_bridge/results/score_requests.json`
- `experiments/29_pti_v0_cli_bridge/results/scores.json`
- `experiments/29_pti_v0_cli_bridge/results/properties/properties.json`
- `experiments/29_pti_v0_cli_bridge/results/properties/property_table.csv`
- `experiments/29_pti_v0_cli_bridge/results/criterion/criterion.json`
- `experiments/29_pti_v0_cli_bridge/results/criterion/criterion.csv`
- `experiments/29_pti_v0_cli_bridge/results/sesoi/sesoi_simulation.json`
- `experiments/29_pti_v0_cli_bridge/results/figures/outer_bridge_source_data.csv`
- `experiments/29_pti_v0_cli_bridge/results/figures/outer_bridge_primaries.pdf`
- `experiments/29_pti_v0_cli_bridge/results/figures/ti2prime_scatter_gpt53_p4_source.json`
- `experiments/27_ti_plot_like_scatter_plots/results/ti2prime_scatter_gpt-5.3-codex_P4_CHECKLIST.pdf`
- `experiments/29_pti_v0_cli_bridge/MANUSCRIPT_NUMBER_MAP.md`

Include the frozen analysis and figure-generation code needed to interpret these files, preserving repository-relative layout.

## Allowed only after deterministic sanitization

- `results/bridge/bridge_pti_v0.json`, `results/bridge/bridge_eq_bm_ms.json`, and `results/figures/outer_bridge_source_data.json`: replace the identity-bearing `prebridge_commit` value with the bundle-local identifier `ANONYMIZED_PREBRIDGE_AUTHORITY`; retain `properties_sha256`, which binds `properties.json` (the property-table CSV hash is recorded separately in the number map).
- `experiments/04_veribench_validation/results_pti_v0_v4/probe_validity_manifest.json`: replace local home/repository prefixes inside captured compiler diagnostics with `${ANON_HOME}` and `${ANON_REPO}`; retain all structural statuses, hashes, and counts.
- Accepted CLI transcripts: include only identity-scanned copies; remove local paths, authentication/account fields, session UUIDs, and provider dashboard links without changing prompts, normalized outputs, model telemetry, or score bindings.

Record the SHA-256 of each original internal source and each sanitized bundle copy in a bundle-local manifest.

## Never include during review

- `STATUS_PTI_V0_V4.md`
- `experiments/29_pti_v0_cli_bridge/expt_v5/results/results_summary_*.md`
- W&B report/link artifacts, authentication-status files, or credential diagnostics
- `experiments/27_ti_plot_like_scatter_plots/results/ti2prime_demo_summary.json` (contains local absolute paths; the sanitized Experiment 29 sidecar replaces it)
- `PAPER_QA.md`, internal review transcripts, Git metadata/history, public VCS identifiers, PR links, branch names, author emails, or machine-local absolute paths

## Mandatory pre-upload scan

Extract every text-bearing archive member and fail the bundle if any of these remain:

```bash
rg -n -i '/Users/|brando|wandb\.ai|github\.com|@.*\.(com|edu)|TODO|TBD|FIXME'
rg -n --pcre2 '(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])'
```

Also inspect PDF metadata and rendered pages, and verify every copied figure and machine-readable authority against the bundle-local SHA-256 manifest.
