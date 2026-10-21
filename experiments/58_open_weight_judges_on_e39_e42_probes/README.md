# Experiment 58: open-weight judges on experiment 39's frozen probes (E39 + E42)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/58_open_weight_judges_on_e39_e42_probes/README.md>

**TLDR:** The build is complete and CPU-tested; no judge has been run. This folder re-scores experiment 39's frozen design (and experiment 42's semantic probes) with 13 open-weight judges run locally with vLLM, to test `C_ms_gold` on a fresh panel with E39's exact criterion and gates. Read `PROTOCOL.md` first (frozen before any judge call); the Slurm steps are in `slurm/SUBMIT.md`.

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
| `slurm/` | `prepare.sh`, `smoke.sbatch`, `run_model.sbatch`, `submit_all.sh`, `collect.sh`, `SUBMIT.md`, GPU-hour estimates. |
| `tests/` | CPU tests (no GPU, no model). |
| `results/` | `REBUILD_REPORT.json` (hash verification), `criterion_items.json`, later the analysis outputs. |

## Verified so far (no model call)

Prompts rebuilt byte-identically: probes 249/249; E39 cells 4689/4689; E42 cells 5238/5238 (`results/REBUILD_REPORT.json`). Judge calls so far: 0. Paid API charges: $0.00.
