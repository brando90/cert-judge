# Experiment 29 — PTI-v0 CLI bridge

This is the executable, subscription-CLI-only successor to the blocked exact-
model v4 protocol in `experiments/04_veribench_validation/pti_v0_v4/`.

The PTI metric and audited probes are reused rather than forked. Only the model
panel and the preregistered batching execution protocol are versioned to v5.

## Current status

The full run is complete: 774/774 CLI tasks, 4,728/4,728 score cells, and
14,184 score records. Property and 72-row criterion outputs have 100% coverage
and passed independent numerical reconstruction. The mandatory pre-bridge
commit is the current gate; the outer bridge has not yet been computed.

Claude's retained CLI telemetry records `claude-sonnet-5` as the requested and
scoring model plus a small auxiliary `claude-haiku-4-5` helper on all Claude
calls. See `RESULTS_QA.md`; downstream claims must not say "Sonnet-only."

## Layout

- `PROTOCOL.md`: pre-result scientific/execution freeze.
- `frozen_config.json`: machine-readable metric, judge, role, and bootstrap
  authority.
- `run_pti_v0_cli.py`: resumable, fail-closed subscription-CLI runner.
- `results/`: authoritative frozen manifests, raw transcripts, scores,
  properties, and human criterion.
- `expt_v5/cc.md`: paste-into-agent execution prompt for this version.
- `REPORT.md`: human-readable run report.
- `RESULTS_QA.md`: independent pre-bridge results audit.
- `writing.tex`: paper-bound draft, updated only from committed outputs.

| Deliverable | Status |
|---|---|
| Frozen manifests and runner | Complete |
| Full CLI workload | Complete |
| Properties and criterion | Complete and independently reconstructed |
| Pre-bridge results commit | In progress |
| Outer bridge and SESOI | Blocked until pre-bridge commit |
| W&B Report and local summary | Pending bridge |
| ICLR manuscript update | Pending committed bridge |

## Pre-result freeze

```bash
python experiments/29_pti_v0_cli_bridge/run_pti_v0_cli.py freeze
python experiments/29_pti_v0_cli_bridge/run_pti_v0_cli.py build
python -m pytest -p no:cacheprovider tests/test_pti_v0_cli_pipeline.py -q
```

Commit the frozen config and request/batch manifests before scoring.

## Resumable score run

```bash
python experiments/29_pti_v0_cli_bridge/run_pti_v0_cli.py score --workers 2
python experiments/29_pti_v0_cli_bridge/run_pti_v0_cli.py status
```

The runner never initializes a provider client or reads an LLM key. It strips
inherited provider-key variables before CLI launch, verifies subscription auth,
rejects Codex tool use, and retains CLI transcripts. Each artifact-disjoint raw
batch/repeat is atomic and validated; rerunning resumes missing work.

## Properties and criterion

```bash
python experiments/04_veribench_validation/run_pti_v0.py compute-properties \
  --probe-manifest experiments/04_veribench_validation/results_pti_v0_v4/probe_validity_manifest.json \
  --requests experiments/29_pti_v0_cli_bridge/results/score_requests.json \
  --config experiments/29_pti_v0_cli_bridge/frozen_config.json \
  --scores experiments/29_pti_v0_cli_bridge/results/scores.json \
  --out-dir experiments/29_pti_v0_cli_bridge/results/properties \
  --bootstrap-iters 10000 --seed 0 --no-api

python experiments/29_pti_v0_cli_bridge/run_pti_v0_cli.py compute-criterion
```

Commit the complete property outputs before invoking the canonical v4 bridge
command with that commit's full SHA. Figure, W&B Report, and manuscript commands
are recorded after the property gate is crossed.
