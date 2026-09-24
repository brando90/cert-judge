## Scientific question (locked)

**Doc link:** [protocol](PROTOCOL.md)

**TLDR:** Can one real paper-rubric judgment complete through Vals-funded gateway inference from SNAP? This is an infrastructure smoke, not a scientific evaluation.

Frozen before inference on 09-24-2026. Exactly one model × task × repetition cell: GPT-6 Astra, `my_add` identity, repeat 1. The manifest binds the source revision, original fixture hash, delivered prompt hash, full settings and completion criteria. No statistical split is assessed. Use P1_BASELINE with the historical last-theorem reference extraction and full candidate fixture; a prospective completion reminder is prepended. Historical measurements are untouched.

Use reasoning effort `xhigh`, temperature omitted, max_tokens 4096, tools empty. One client inference request, zero client retries or continuations, no model fallback. A terminal error remains in the denominator. Do not regenerate after inspecting the outcome. Any later diagnostic run must be a separately frozen version.

Use the authenticated Vals-hosted model gateway, its assigned host-owned credential and server-held provider keys. Never send custom_api_key or custom_endpoint; never use personal provider credentials or agent subscriptions for this judgment. Registry metadata must confirm the exact model/effort and no configured fallback. Record provider receipt identifiers, usage, reported cost, output hash and finish reason. The client does not independently observe the provider invoice account or unreported server retry charges.

The admission ceiling is $1. Preflight conservatively bounds input as prompt UTF-8 bytes plus 1024 framing tokens and output as all 4096 permitted tokens, using the authenticated registry price. Fail closed if the resulting estimate exceeds the ceiling. Current estimate: $0.29305. No purchase, recharge or limit increase.

Run durably with nohup and an exclusive attempt reservation. Client timeout 3600 seconds exceeds the gateway's documented 3540-second server cap; controller allocation 3900 seconds reserves finalization. Do not cancel healthy execution at a coordinator boundary. Save terminal evidence for the entire declared set, including errors and incomplete generation.

Transport pass: HTTP 200, no provider error envelope and final output. Parsing pass: finite numeric score in [0,1] plus nonempty reasoning. Identity sanity pass: score exactly 1.0. These are separate findings. One passing identity does not establish scientific validity, stability, human agreement, discrimination, or complete benchmark support.
