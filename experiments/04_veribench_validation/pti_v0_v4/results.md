# PTI-v0 v4 result pointer

**TLDR:** The frozen zero-spend run is complete, but primary `PTI_v0` and the outer bridge are `NOT_COMPUTABLE` because no admissible paid-judge scores exist.

The canonical human-readable report is `../results_pti_v0_v4/RESULTS.md`. Machine-readable artifacts live in `../results_pti_v0_v4/` and are bound to the frozen files in this directory.

Current boundary:

- structural validity sets: `P_eq=86`, `P_bm=49`, `P_ms=63`, `P_eqalpha=67`;
- deterministic controls: computed, both `PTI_v0=0`;
- human criterion: seven judges computed at 72/72; one primary is `NOT_COMPUTABLE` at 64/72 after eight fallback rows were excluded;
- frozen-rule power at the `rho=0.5` SESOI: 0.1492 with four valid primaries;
- primary properties and PTI: `NOT_COMPUTABLE/DEFER`;
- outer bridge: no statistic computed;
- actual provider/API spend: `$0`.
