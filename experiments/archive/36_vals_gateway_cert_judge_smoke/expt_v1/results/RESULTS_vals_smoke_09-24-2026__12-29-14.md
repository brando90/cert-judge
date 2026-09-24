# Certification Judge Vals gateway smoke

**Doc link:** [results](RESULTS_vals_smoke.md)

**PASS:** 1/1 declared judgments completed through the Vals-hosted gateway on SNAP. GPT-6 Astra at `xhigh` returned a valid score **1.0/1.0** for the actual `my_add` identity fixture. Reported cost: **$0.0394425**. Client wall time: **6.394 seconds**.

| Check | Measured result | Criterion |
|---|---|---|
| Frozen manifest completion | 1 expected, 1 attempted, 1 terminal, 1 clean; 0 missing/interrupted | Every declared cell terminal |
| Gateway inference | HTTP 200; no error envelope | Successful real inference |
| Finish reason | stop / completed | No output truncation |
| Output parsing | Score 1.0; nonempty reasoning | Finite score in [0,1] |
| Positive identity sanity | 1.0 | Protocol threshold exactly 1.0 |
| Requested model / effort | GPT-6 Astra / xhigh | Frozen setting |
| Registry route / fallback | Resolves to gpt-6-astra; response fallback null | No alternate model |
| Reported usage | 3 ordinary input + 2,397 cache-write input; 49 answer + 140 reasoning tokens | All reported categories retained |
| Reported cost | $0.0394425 | Below $1 admission ceiling |

The request started on 09-24-2026 at 12:29:08 Pacific and finished at 12:29:14 Pacific. The authenticated deployed registry resolves the requested alias to `gpt-6-astra` at `reasoning_effort=xhigh`. The gateway response does not separately expose a provider model-name field; its response/request identifiers are retained privately, and no fallback was reported. Model/effort attribution therefore rests on the frozen request and authenticated registry, with provider correlation receipts available for audit.

## Exact scope

The input is the current local cert-judge `my_add.lean` fixture (6,639 bytes; source commit recorded in the manifest). P1_BASELINE uses the historical last-theorem reference extraction, the full candidate file, and a separately frozen completion reminder. The response says: “The generated theorem exactly matches the reference,” and identifies the functional/imperative equivalence statement; both reference and candidate retain `sorry`. The test checks judgment transport and an identity sanity case; it does not compile or repair proofs.

This is **not** a statistical train/validation/test result, a complete property suite, evidence of judge--human agreement, or scientific validation of the Astra judge. No paper results or claims changed. It is a direct use of Valkyrie's Vals model-gateway route, not a hosted Valkyrie benchmark run.

## Funding and limits

The runtime fetches only the assigned Vals gateway credential with explicit host Amazon Web Services (AWS) credentials. The HTTPS request goes only to the authenticated Vals gateway; no personal provider key, custom provider endpoint or custom_api_key is supplied. Provider credentials stay on the gateway server. The client cannot independently inspect the provider invoice account.

The preflight admission estimate was $0.29305 under the $1 ceiling. It uses conservative input bytes and the 4,096-token output limit at listed base prices; it is an admission estimate, not an independently enforced provider invoice cap. Cache-write markup and any failed gateway-internal retry charges are not independently bounded by that client estimate. The returned successful-call metadata reports all five cost components totaling $0.0394425; unreported failed-attempt charges are unavailable. One client request and zero client retries were used.

## Evidence and reproduction

[Sanitized terminal receipt](receipt.json), [preflight](preflight.json), [frozen manifest](../manifest.json), [delivered prompt](../data/prompt.txt), and [runner](../scripts/run_smoke.py) preserve the measured condition. Private settings, the exact request and raw provider response remain ignored. Deterministic checks verified frozen hashes, one-to-one terminal accounting, 5 parsing cases, source compilation and experiment layout.

The durable execution owner exited after the terminal receipt; no model worker remains. The remote immutable packet remains under the execution path documented in the experiment README. This completed smoke is archived; any new inference belongs in a newly registered active condition and must not remove the old attempt reservation.

**TLDR-end:** [cert-judge: vals-smoke] The Vals-funded route is usable from SNAP: 1/1 real Astra xhigh judgment completed, score 1.0, reported cost $0.0394425. This verifies infrastructure and one identity sanity case only.
