# PTI-v0 v5 experiment report

**TLDR-start:** [cj: pti-v0] The complete CLI-only v5 workload finished: 774/774 accepted tasks, 4,728/4,728 score cells, 14,184 records, full property/criterion coverage, and `$0` provider-API spend. Four of five primary four-property PTIs are exactly zero under the preregistered zero-first geometric mean; Sonnet + P8 scores `0.8114`. The outer bridge is intentionally withheld until these property outputs are committed.

## Run identity

- Metric version: `PTI_v0`
- Execution protocol: `PTI_v0_cli_v5`
- Frozen-config fingerprint:
  `735bd5951d4e6f8e9bf5f0d5e374028e1e46d92077b64584a7f89ff30981be9e`
- Pre-result commit: `395efdc00584cad32f6e9a525a8dbd9b201ff2a7`
- Exact v4 model run: `NOT_RUN`
- Actual v5 workload: `gpt-5.6-terra` and requested/scoring
  `claude-sonnet-5`; Claude telemetry also records the CLI-internal auxiliary
  `claude-haiku-4-5` helper on all 258 Claude calls.
- Authentication: locally authenticated ChatGPT and `claude.ai` subscriptions.
- Provider API spend: `$0`.

The v5 outputs are not pooled with or relabeled as v4. Batching remains an
execution limitation: unrelated cases share a context, while artifact-disjoint
packing prevents any batch from containing two cells for the same typed
artifact.

## Completion and integrity

| Item | Result |
|---|---:|
| Accepted CLI tasks | 774 / 774 |
| Accepted tasks per LLM configuration | 129 / 129 |
| Complete unique cells | 4,728 / 4,728 |
| Score records | 14,184 |
| Local-control cells | 1,182 |
| Invalid accepted raw tasks | 0 |
| Quarantined tasks | 0 |
| Excluded failed attempts | 4, each successfully retried |
| Human panel rows | 72 |
| Property bootstrap replicates | 10,000 |
| Criterion bootstrap replicates | 10,000 |

Authoritative score SHA-256:
`c51a2ee78c7552af3c021a666ad1c55ba6eeed65f4a91c79d1b0a41d7f36e6c1`.

## Four-property results

All four properties are `COMPUTED` at coverage `1.0` for every judge.

| Judge | Role | P_eq | P_bm | P_ms | P_eqalpha | PTI_v0 |
|---|---|---:|---:|---:|---:|---:|
| Terra + P8 | primary | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Terra + P4 | primary | 0.0000 | 0.0000 | 0.0000 | 0.8828 | 0.0000 |
| Terra + P1 | primary | 0.0000 | 0.0000 | 0.0000 | 0.9387 | 0.0000 |
| Sonnet + P8 | primary | 0.9187 | 0.6467 | 0.7791 | 0.9366 | 0.8114 |
| Sonnet + P4 | primary | 0.0000 | 0.6651 | 0.8069 | 0.9036 | 0.0000 |
| String control | control | 1.0000 | 0.0000 | 0.8456 | 0.9359 | 0.0000 |
| Edit distance | control | 1.0000 | 0.0000 | 0.0000 | 0.9992 | 0.0000 |
| Random | control | 0.4241 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |

For Sonnet + P8, the four-property 95% artifact-cluster bootstrap interval is
`[0.7820, 0.8391]`. The exact zeros are not failed computations: the frozen
zero-first geometric mean returns zero when any included artifact factor is
exactly zero. Independent QA verified a directly observed zero factor behind
every zero aggregate.

## Human criterion (primary average view)

| Judge | TI_m1 Spearman | 95% paired-cluster CI | Kendall tau-b |
|---|---:|---:|---:|
| Terra + P8 | 0.0105 | [-0.2294, 0.2475] | 0.0082 |
| Terra + P4 | 0.2106 | [-0.0338, 0.4425] | 0.1772 |
| Terra + P1 | 0.3377 | [0.0933, 0.5514] | 0.2861 |
| Sonnet + P8 | 0.0886 | [-0.1463, 0.3291] | 0.0685 |
| Sonnet + P4 | 0.2098 | [-0.0396, 0.4426] | 0.1656 |
| String control | 0.4255 | [0.2061, 0.6102] | 0.3337 |
| Edit distance | 0.1987 | [-0.0793, 0.4562] | 0.1484 |
| Random | -0.0008 | [-0.2351, 0.2254] | -0.0031 |

## Independent QA and pre-bridge state

The read-only audit in `RESULTS_QA.md` independently reconstructed all score,
property, criterion, bootstrap, and CSV/JSON outputs. Its numerical and
structural checks passed. It returned a formal `FAIL` only because literal
exact-model-only provenance cannot be certified for Claude's auxiliary Haiku
telemetry. This report adopts the narrower evidence-backed model claim.

At this report stage the outer bridge is `NOT COMPUTED BY DESIGN`: the protocol
forbids it until the complete property table is committed byte-identically.
The next canonical action is the pre-bridge results commit, followed by a bridge
command bound to that full commit SHA.

**TLDR-end:** [cj: pti-v0] The v5 run is complete and numerically audited; property/criterion artifacts are ready for the mandatory pre-bridge commit, with the Claude auxiliary-model limitation explicitly preserved.
