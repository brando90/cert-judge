# PTI-v0 v4 blocked actions

**TLDR:** All safe zero-spend work is complete. Paid primary scoring, the outer bridge, its figure, and manuscript result edits remain blocked by explicit approval, data-admissibility, dependency, and pre-bridge-commit gates.

## Hard blockers still open

1. **No admissible primary score records.** The legacy cache has 27,102 entries and 148 potential model/content matches, including 94 prompt/content matches and 80 three-score matches, but zero entries satisfy the versioned PTI schema/scorer/decoding success contract. All five primary judges therefore remain `NOT_COMPUTABLE` for every PTI property.
2. **No paid-inference approval.** Exact conservative upper bounds are `$7.6127427` for the alpha transformed side, `$15.2020962` for an uncached original+alpha property run, and `$85.0848855` for the full frozen paid-judge request set. No scope was approved, no credential was loaded, and actual provider/API spend is `$0`.
3. **Bridge hard gate.** The primary property table is incomplete, so the checked output records `bridge_statistic_computed=false`. A future computable bridge additionally requires a full pre-bridge commit SHA containing the byte-identical property file.
4. **Panel repair remains unsupported.** The three stale unsafeMultiply ratings point to the vulnerable historical gold rather than the intended safe gold. The defensible panel stays at 72 unless the data owner authorizes rerating or explicitly redefines those rows.
5. **Dependency review remains open.** Review order is ultimate-utils PR #44, then cert-judge PR #38. Exp27 is reused as the inner diagnostic and is not duplicated.
6. **One primary human criterion is incomplete.** Eight HTTP-401 fallback rows for `gpt-5.3-codex|P8_STRICT_B` are quarantined, leaving 64/72 verified rows and a `NOT_COMPUTABLE` criterion under the frozen 100% rule. Restoring the planned five-primary criterion panel would require 24 approved re-score calls under a separate exact quote.

## Consequences

- No primary `PTI_eq_bm_ms` or four-property `PTI_v0` value is reported.
- No outer PTI-versus-`TI_m1` association, uncertainty interval, or figure is computed.
- The frozen design has only four lineage-valid primary criteria and 0.1492 simulated positive-rule power at the `rho=0.5` SESOI.
- The active ICLR manuscript is unchanged; legacy values are not relabeled.
- No screening/pass or human-validations-saved claim is permitted because thresholds were not frozen.
- No W&B Report is created for this blocked zero-spend preparation.

The exact gate ledger and completed local evidence are under `experiments/archive/04_veribench_validation/results_pti_v0_v4/`.
