# Experiment 29 — PTI-v0 CLI bridge

This is the executable, subscription-CLI-only successor to the blocked exact-
model v4 protocol in `experiments/04_veribench_validation/pti_v0_v4/`.

The PTI metric and audited probes are reused rather than forked. Only the model
panel and the preregistered batching execution protocol are versioned to v5.

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
