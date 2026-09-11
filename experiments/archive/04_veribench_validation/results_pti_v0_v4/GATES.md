# PTI-v0 v4 gate ledger

**TLDR:** The zero-spend engineering gates pass, while the paid-score, primary-property, bridge, figure, and manuscript gates remain closed by design.

| Gate | Status | Evidence or required action |
|---|---|---|
| Versioned metric, vectors, and schema | PASS | `PTI_v0`, v4 vectors, formal score schema, and focused tests are checked in. |
| Typed pool freeze | PASS | 470 observed artifacts, 157 items, one explicit missing grid member. |
| Candidate/gold elaboration audit | PASS | Pinned Lean 4.22 manifest covers all 470 rows, prepares local support modules, binds Lake/olean state, and classifies failures. |
| Bug-ladder structural set | PASS | 49 four-step cumulative compile-valid ladders; 421 exclusions recorded independently of scores. |
| Missing-spec structural set | PASS | 63 four-step cumulative compile-valid ladders; 407 exclusions recorded independently of scores. |
| Alpha structural set | PASS | 67 conservative, non-no-op, compile-valid transformations; 403 exclusions recorded. |
| Human panel lineage | PASS WITH 72 | 72 supported rows; the unsupported 72-to-75 rename is not applied. |
| Legacy-cache admissibility | FAIL CLOSED | 0 admissible calls; 94 exact prompt/content matches and 80 three-score matches still lack the PTI scorer/success contract. |
| Exact spend quote | PASS | Alpha-only, pair, and full quotes generated without inference. |
| Paid inference approval | BLOCKED | No explicit approval exists; no key was loaded and actual spend is `$0`. |
| Primary properties | BLOCKED | All five primaries have zero admissible property coverage and are `NOT_COMPUTABLE`. |
| Deterministic controls | PASS | Both controls computed at 100% structural-set coverage; each has `PTI_v0=0`. |
| Human criterion | PARTIAL / FAIL CLOSED | Seven judges compute at 72/72; one primary is `NOT_COMPUTABLE` at 64/72 after eight HTTP-401 fallbacks are excluded. |
| SESOI simulation | PASS, UNDERPOWERED | Frozen decision-rule power is 0.1492 at the `rho=0.5` SESOI with four valid primaries. |
| Outer bridge | FAIL CLOSED | Property hard gate forbids computation; output records `bridge_statistic_computed=false`. |
| Outer figure | BLOCKED | Requires a committed computable bridge. |
| Active manuscript result update | BLOCKED | Requires committed machine-readable bridge evidence. |
| Screen/deployment claim | PROHIBITED | No per-property thresholds were frozen. |
| W&B Report | N/A | The approved paid experiment has not run. |

The remaining human decisions are to resolve dependency review order (#44 then #38), decide whether to authorize an exact quoted scoring scope, and separately decide whether the three unsafeMultiply candidates should be rerated against the intended safe gold.
