# PTI-v0 v4 cache inventory

**TLDR:** The legacy cache contains 27,102 entries and 148 potential content/model matches, but zero entries are admissible for `PTI_v0`; no cached call was subtracted from the frozen spend quotes.

## Inventory

| Field | Value |
|---|---:|
| Legacy entries | 27,102 |
| Malformed entries | 0 |
| Potential content/model matches | 148 |
| Prompt/content/model matches | 94 |
| Prompt/content/model matches with three scores | 80 |
| Matching error-fallback cells | 2 |
| Admissible request cells | 0 |
| Admissible paid calls | 0 |

Observed stored repeat-count histogram:

| Repeats | Entries |
|---:|---:|
| 1 | 771 |
| 2 | 1 |
| 3 | 12,245 |
| 5 | 9,738 |
| 7 | 27 |
| 9 | 4,320 |

Extended historical keys do bind namespace, prompt, model, and content hashes, and stored score cardinality can be inspected. They do not bind `PTI_v0_scores_v1`, a versioned scorer/decoding contract, or successful non-fallback parsing; matching error fallbacks exist. Exact matches therefore remain audit information only, and treating them as completed PTI cells would be unsafe.

## Frozen request set

- Request-manifest fingerprint: `c71fe78609e2880d9fd05c0c414833a5a8186496174f5011e8f13d52cca46046`.
- Content-deduplicated cells across all judges: 4,176.
- Paid-judge cells: 3,132.
- Required paid calls at three repeats: 9,396.
- Local-control cells: 1,044, materialized deterministically as 3,132 records.

## Quotes

| Quote | Calls | Upper-bound cost |
|---|---:|---:|
| Missing alpha transformed side | 918 | `$7.6127427` |
| Uncached original plus alpha pair | 1,836 | `$15.2020962` |
| Full paid-judge request set | 9,396 | `$85.0848855` |

All quotes assume uncached input. Optional RENAME/REORDER/STYLE diagnostics are `NOT_QUOTABLE_UNVALIDATED_TRANSFORM`, not `$0`.

Actual provider/API calls and spend: **0 calls, `$0`**.
