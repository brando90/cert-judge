# Experiment 29 — Test the Proxy Trust Index against human agreement

**TLDR:** This completed experiment tests whether label-free Proxy Trust Index version 0 (PTI-v0) scores track judges’ agreement with human ratings. It contains the frozen protocol, command-line scoring runner, accepted results, and negative/inconclusive validation finding; it does not validate the combined agreement-and-stability target.

This directory is the single self-contained home for the experiment. It now
contains the original planning/preflight handoff, the frozen protocol and
runner, all accepted raw outputs, derived results, independent QA, manuscript
number bindings, and the final decision report. The planning material was
initially staged under an Experiment 28 directory and consolidated after the run.
The folder now has a descriptive name; frozen result and configuration payloads
retain their original provenance paths and hashes.

This is the executable, subscription-CLI-only successor to the blocked exact-
model v4 protocol in `experiments/archive/04_veribench_validation/pti_v0_v4/`.

The PTI metric and audited probes are reused rather than forked. Only the model
panel and the preregistered batching execution protocol are versioned to v5.

## Current status

The full run is complete: 774/774 CLI tasks, 4,728/4,728 score cells, and
14,184 score records. Property and 72-row criterion outputs have 100% coverage
and passed independent numerical reconstruction. After the mandatory
pre-bridge commit, the pre-specified primaries-only validation association was
Spearman `-0.3536` (95% CI `[-1.0000, 0.3953]`, `n=5`): below the `0.5` SESOI
and inconclusive about zero.

Claude's retained CLI telemetry records `claude-sonnet-5` as the requested and
scoring model plus a small auxiliary `claude-haiku-4-5` helper on all 258
accepted Claude CLI tasks. See `RESULTS_QA.md`; downstream claims must not say
"Sonnet-only."

## Decision reading order

1. `results.md` — one-minute result and decision summary.
2. `results/figures/outer_bridge_primaries.png` — the primary bridge visually.
3. `REPORT.md` — complete human-readable scientific report.
4. `results/properties/property_table.csv` and
   `results/criterion/criterion.csv` — compact judge-level inputs.
5. `results/bridge/bridge_pti_v0.json` and
   `results/sesoi/sesoi_simulation.json` — exact bridge/bootstrap/power output.
6. `RESULTS_QA.md` and `PAPER_QA.md` — independent numerical and manuscript QA.
7. `MEGA_QA_REPORT.md` — final three-stage adversarial QA and release verdict;
   the exact stage records are `MEGA_QA_FABLE.md`, `MEGA_QA_CODEX.md`, and
   `MEGA_QA_FINAL_CODEX.md`.
8. `results/scores.json` and `results/raw_batches/` — normalized records and
   retained CLI evidence for a full audit.

## Layout

- `00-CODEX-SOL-MAX-PREFLIGHT.md` through
  `05-ICLR2027-FINALIZATION-CHECKLIST.md`: original plan and execution gates.
- `README_FOR_BRANDO.md`, `FABLE_HANDOFF_AUDIT.md`, and `ref/`: original handoff
  and its reference material. The original `ref/files (22).zip` archive is
  retained byte-for-byte (SHA-256
  `7362ab1d1dcc9161fefca3aff87c33276b71941a647f2bd2b7f8e176509d6859`).
- `PREFLIGHT_PTI_V0_V4.md`, `BLOCKED.md`, `FABLE_PTI_V0_REVIEW.md`, and
  `FABLE_PTI_V0_REREVIEW.md`: the zero-spend preflight, blocker record, and
  independent v4 implementation reviews.
- `STATUS_PTI_V0_V4.md`: final execution, manuscript, provenance, and handoff
  status.
- `PROTOCOL.md`: pre-result scientific/execution freeze.
- `frozen_config.json`: machine-readable metric, judge, role, and bootstrap
  authority.
- `run_pti_v0_cli.py`: resumable, fail-closed subscription-CLI runner.
- `results/`: authoritative frozen manifests, raw transcripts, scores,
  properties, and human criterion.
- `expt_v5/cc.md`: paste-into-agent execution prompt for this version.
- `REPORT.md`: human-readable run report.
- `RESULTS_QA.md`: independent pre-bridge results audit.
- `06-MEGA-QA-PROMPT.md`, `MEGA_QA_FABLE.md`, `MEGA_QA_CODEX.md`,
  `MEGA_QA_FINAL_CODEX.md`, and `MEGA_QA_REPORT.md`: the exact final QA prompt,
  three fresh-context stage records, and consolidated release verdict.
- `PR_BODY.md`: canonical direct-to-`main` PR description and validation plan.
- `writing.tex`: paper-bound draft, updated only from committed outputs.

| Deliverable | Status |
|---|---|
| Frozen manifests and runner | Complete |
| Full CLI workload | Complete |
| Properties and criterion | Complete and independently reconstructed |
| Pre-bridge results commit | Complete: `6f55c44299eadda78db5738c7913475d06ea671f` |
| Outer bridge and SESOI | Complete; below-SESOI/inconclusive |
| W&B Report and local summary | Complete; canonical report updated in place on 2026-09-10 |
| ICLR manuscript update | Complete on `main` through merged PR #40 |

## Pre-result freeze

```bash
python experiments/29_proxy_trust_index_vs_human_agreement/run_pti_v0_cli.py freeze
python experiments/29_proxy_trust_index_vs_human_agreement/run_pti_v0_cli.py build
python -m pytest -p no:cacheprovider tests/test_pti_v0_cli_pipeline.py -q
```

Commit the frozen config and request/batch manifests before scoring.

## Resumable score run

```bash
python experiments/29_proxy_trust_index_vs_human_agreement/run_pti_v0_cli.py score --workers 2
python experiments/29_proxy_trust_index_vs_human_agreement/run_pti_v0_cli.py status
```

The runner never initializes a provider client or reads an LLM key. It strips
inherited provider-key variables before CLI launch, verifies subscription auth,
rejects Codex tool use, and retains CLI transcripts. Each artifact-disjoint raw
batch/repeat is atomic and validated; rerunning resumes missing work.

## Properties and criterion

```bash
python experiments/archive/04_veribench_validation/run_pti_v0.py compute-properties \
  --probe-manifest experiments/archive/04_veribench_validation/results_pti_v0_v4/probe_validity_manifest.json \
  --requests experiments/29_proxy_trust_index_vs_human_agreement/results/score_requests.json \
  --config experiments/29_proxy_trust_index_vs_human_agreement/frozen_config.json \
  --scores experiments/29_proxy_trust_index_vs_human_agreement/results/scores.json \
  --out-dir experiments/29_proxy_trust_index_vs_human_agreement/results/properties \
  --bootstrap-iters 10000 --seed 0 --no-api

python experiments/29_proxy_trust_index_vs_human_agreement/run_pti_v0_cli.py compute-criterion
```

Commit the complete property outputs before invoking the canonical v4 bridge
command with that commit's full SHA. Figure, W&B Report, and manuscript commands
are recorded after the property gate is crossed.

## Relocation and frozen provenance

The original `frozen_config.json` is retained byte-for-byte from before the
archive move. `runtime_relocation.json` binds that file hash to the complete
relocated runtime fingerprint, including the current runner and input hashes.
The runner accepts only that exact reviewed combination or an exact newly
frozen configuration; it still rejects any unrecorded drift. Numerical inputs,
judge settings, request identities, and accepted score records are unchanged.
Historical paths inside frozen results and attached reference packets are
provenance, not current launch commands; the relocation table is in
[`../archive/README.md`](../archive/README.md).
