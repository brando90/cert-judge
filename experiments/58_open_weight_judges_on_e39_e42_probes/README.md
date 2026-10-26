# Experiment 58: open-weight judges on experiment 39's frozen probes (E39 + E42)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/58_open_weight_judges_on_e39_e42_probes/README.md>

**TLDR:** As of 10-26-2026, [PR 83](https://github.com/brando90/cert-judge/pull/83) reports FarmShare results for four E58 judges (36 configurations); the complete 13-model panel is unfinished. A separate mercury1 smoke and completed later E59/E60 results also exist; the later studies use their own registered settings. This folder defines the 13-model E58 panel on experiment 39's frozen design and experiment 42's semantic probes. Its frozen-analysis implementation has been audited and repaired; see [the findings and exact saved-data reproduction](RESULTS_analysis_audit.md). Read `PROTOCOL.md` first; the Slurm steps are in `slurm/SUBMIT.md`.

## Layout

| Path | What |
|---|---|
| `PROTOCOL.md` | The frozen protocol: panel, generation rules, gate, always-reported items, exploratory TVD-MI, bridge. |
| `scripts/e58.py` | Panel (HF repo, pinned revision, GPUs, context), prompt list, constants, read-only imports of E39/E42. |
| `scripts/rebuild_prompts.py` | Rebuilds E39 and E42 probe texts and prompts off-SNAP from `brando90/veribench`, verifies every hash. Writes `results/REBUILD_REPORT.json` and git-ignored `private/prompts/`. |
| `scripts/token_budget.py` | Tokenizer-only pre-check: prompt lengths, over-context cells per model. |
| `scripts/judge_vllm.py` | vLLM offline driver (resumable, chunked); writes raw output and the harvest. |
| `scripts/harvest_lib.py` | Raw output to E39-schema harvest JSON, with E39's own parsers. |
| `scripts/analyze58.py` | The frozen analysis (gate, clustered permutation, PTI_v0, TI_var, E42 screen, scale curves, TVD-MI, bridge). |
| `scripts/analysis_inputs.py` | Declared-panel coverage, input identity/hash verification, recorded runtime checks and failure counts. |
| `slurm/` | `prepare.sh`, `smoke.sbatch`, `run_model.sbatch`, `submit_all.sh`, `collect.sh`, `SUBMIT.md`, GPU-hour estimates. |
| `scripts/fetch_models.py`, `verify_prompts.py`, `make_package.py` | Pinned-revision weight download; prompt hash check; builds the upload tarball. |
| `tests/` | CPU tests (no GPU, no model): panel config, parsers, harvest schema, clustered statistics, a synthetic 117-unit run through the harvest writer and the whole analysis. |
| `results/` | `REBUILD_REPORT.json` (hash verification), `criterion_items.json`, later the analysis outputs. |

## Run it

1. Upload `e58_pkg.tgz` and follow `slurm/SUBMIT.md` (FarmShare primary, Sherlock fallback): prepare, smoke, `submit_all.sh`, `collect.sh`. About 90 GPU-hours for all 13 models, about 16 for the seven 1-GPU models (`slurm/GPU_HOURS.md`, assumed throughput until the smoke measures it).
2. `python scripts/analyze58.py --run <collected runs/main>` verifies `MANIFEST.sha256` and recorded frozen runtime settings, then writes `results/ANALYSIS.json` and `results/RESULTS_open_weight_judges.md`. All 117 units remain visible; unavailable statistics are `NOT_COMPUTABLE`.
3. Partial/uncollected inputs: `python scripts/analyze58.py --run <existing partial directory> --out <diagnostic directory> --dry-run`. This writes distinct `ANALYSIS_DRY_RUN.json` and `RESULTS_open_weight_judges_DRY_RUN.md`. Reduced draw counts require `--dry-run`; ordinary analysis uses the frozen 10,000 draws. Dry runs never establish an E58 scientific result.
4. Context for reading the gate: experiment 39's test units gave `C_ms_gold` Spearman 0.558 (permutation p 0.0127) over 18 hosted-judge units.

## Verified so far (no model call)

Prompts rebuilt byte-identically: probes 249/249; E39 cells 4689/4689; E42 cells 5238/5238 (`results/REBUILD_REPORT.json`; reverified 10-26-2026 without changing that frozen receipt). CPU tests: 32 pass, zero skipped (`python -m pytest experiments/58_open_weight_judges_on_e39_e42_probes/tests -q`, needs rebuilt prompts). The audit made zero judge calls and incurred $0.00 in provider charges. [Reproduction receipt](results/audit_10-26-2026/REPRODUCTION.json) records a labelled compatibility dry run on existing E60 inputs, not original E58 observations.
