**TLDR:** Run the frozen PTI-v0 CLI v5 protocol with subscription-authenticated Codex/Claude CLIs, retain every transcript, require 100% completeness, commit the property table before bridge computation, and report the auxiliary Claude model telemetry exactly.

# Experiment 29 v5 agent prompt

## Hard constraint

Do not use provider API keys, provider SDKs, HTTP model callers, score fallback,
imputation, post-result metric changes, or a bridge computed before the
byte-identical property table is committed. Never relabel this v5 execution as
the inaccessible exact-model v4 run.

## Authoritative inputs

- `../PROTOCOL.md`
- `../frozen_config.json`
- `../batch_score_schema.json`
- `../run_pti_v0_cli.py`
- `../results/score_requests.json`
- `../results/batch_manifest.json`
- `../results/criterion_manifest.json`
- experiment 04's frozen structural manifest and canonical PTI-v0 runner

## Execution

From the repository root:

```bash
python experiments/29_pti_v0_cli_bridge/run_pti_v0_cli.py status
python experiments/29_pti_v0_cli_bridge/run_pti_v0_cli.py score --workers 2
python experiments/04_veribench_validation/run_pti_v0.py compute-properties \
  --probe-manifest experiments/04_veribench_validation/results_pti_v0_v4/probe_validity_manifest.json \
  --requests experiments/29_pti_v0_cli_bridge/results/score_requests.json \
  --config experiments/29_pti_v0_cli_bridge/frozen_config.json \
  --scores experiments/29_pti_v0_cli_bridge/results/scores.json \
  --out-dir experiments/29_pti_v0_cli_bridge/results/properties \
  --bootstrap-iters 10000 --seed 0 --no-api
python experiments/29_pti_v0_cli_bridge/run_pti_v0_cli.py compute-criterion
```

Run independent read-only results QA. Commit every validated score, transcript,
property, and criterion artifact. Only then invoke the canonical bridge with the
full property-commit SHA, followed by the frozen SESOI simulation, figures,
W&B Report, manuscript update, and paper QA.

## Acceptance criteria

- 774/774 accepted CLI tasks and 4,728/4,728 complete cells.
- Exactly three bound scores per cell; no missingness-as-zero or fallback.
- 100% property and criterion coverage.
- 10,000 preregistered bootstrap replicates.
- `$0` provider-API spend and subscription-auth evidence.
- Exact primary, control, model-family, three-property, and per-property bridge
  outputs after the pre-bridge commit.
- Exact model provenance disclosure, including any CLI-internal auxiliary model.
- Permanent W&B Report URL, timestamped local summary, stable `results.md`,
  source-data tables, manuscript build, and two stacked draft PRs.
