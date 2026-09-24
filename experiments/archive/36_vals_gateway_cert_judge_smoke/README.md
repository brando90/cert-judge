# Vals gateway Certification Judge smoke

**Doc link:** [experiment home](./)

**TLDR:** One real Certification Judge identity judgment checks that the Vals-funded model route can serve the paper harness on Stanford Network Analysis Project (SNAP). It does not validate a judge or change paper results.

## Setup and decision

The consequential uncertainty is authenticated inference, beyond successful metadata listing. Reuse the historical P1_BASELINE rubric, its last-theorem reference extraction, and the current local `my_add` Lean fixture. Run one frozen cell on GPT-6 Astra at extra-high reasoning (`xhigh`), at most 4,096 output/reasoning tokens and one client call. Successful transport plus valid score JSON establishes usability; the identity sanity criterion is score 1.0. Other scores remain evidence. No retries, alternate models, personal model subscriptions or direct provider credentials.

The catalog-derived admission estimate is $0.29305 at $10 input/$50 output per million tokens, using 8,825 conservative input tokens and the full 4,096-token output limit, below the $1 admission ceiling. Server internal retry charges are not independently exposed. The Vals-hosted gateway owns provider credentials; invoice account identity is not exposed to this client.

## Files

- [Frozen protocol](expt_v1/PROTOCOL.md), [manifest](expt_v1/manifest.json), [dispatch instructions](expt_v1/agents_v1.md).
- [Runner](expt_v1/scripts/run_smoke.py), [input fixture](expt_v1/data/my_add.lean), [delivered prompt](expt_v1/data/prompt.txt).
- [Live results](results.md), [checkpoint](CKPT_vals_smoke.md), [readable results](expt_v1/results/RESULTS_vals_smoke.md).
- Private host settings and raw gateway responses stay ignored under the version directory.

## Execution storage

The isolated remote packet lives under `/lfs/skampere1/0/brando9/cert-judge-vals-smoke-09-24-2026/experiments/36_vals_gateway_cert_judge_smoke/`, matching this experiment layout. Local-filesystem storage isolates execution from stale shared checkouts and existing workers. Synchronize this exact experiment directory back to the canonical Mac checkout after completion; preserve input and manifest hashes. The runner requires Python, PyYAML and boto3 from the verified Valkyrie runtime; it uses the gateway wire contract documented by [Vals model-library](https://github.com/vals-ai/model-library/blob/main/docs/gateway.md).

| Status | Value |
|---|---|
| Declared cells | 1 |
| Execution | Complete: 1/1 terminal; score 1.0; reported cost $0.0394425 |
| Paper claims | None added |
