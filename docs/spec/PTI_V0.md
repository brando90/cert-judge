# PTI-v0 specification

**TLDR:** `PTI_v0` is the frozen, label-free four-property proxy for judge trustworthiness. It is distinct from the scoped construct `TW_m`, the human-grounded criterion `TI_m`, and all legacy JTI/TIvar outputs.

- Status: frozen v4 implementation contract
- Metric version: `PTI_v0`
- Frozen protocol: `experiments/archive/04_veribench_validation/pti_v0_v4/frozen_config.json`

## Scientific objects

- `TW_m(aj; C)` is the scoped trustworthiness construct.
- `TI_m(aj; C)` is an expensive human-grounded criterion. The primary criterion here is `TI_m1`, Spearman rank agreement between median judge scores and the paired average human view.
- `PTI_v0(aj)` is a label-free behavioral proxy. Passing it is not proof of trustworthiness; failing a property is a pre-specified behavioral diagnostic under the stated probe assumptions.

The outer bridge is the association across judge configurations between `PTI_v0` and `TI_m1`. The two axes are not calibrated level measurements, so the analysis must not use an identity line or a PTI-versus-TI level error.

## Typed indices

A base artifact is `f=(i,a,q)`, where `i` is the benchmark item, `a` the generating agent, and `q` its generation index. Judge repeats use `r`; ladder degradation uses `ell`. Those axes must never be pooled or paired positionally.

For a ladder type `T` and level `ell`, repeated normalized judge scores are aggregated locally:

```text
s_tilde[f,T,ell] = median_r s[f,T,ell,r]
```

Larger `ell` always means more degradation.

## Ladder factors

For a structurally valid bug or missing-specification ladder:

```text
rho[f,T] = Spearman(ell, s_tilde[f,T,ell])
C[f,T]   = (1 - rho[f,T]) / 2
```

Spearman is tie-aware and correlations within `1e-12` of an endpoint are snapped to that endpoint. Kendall tau-b, tie counts, constant flags, and adjacent reversals are diagnostics.

If all median ladder scores are exactly constant, Spearman is undefined and the frozen behavioral policy is `C=0`. No tolerance is applied to this equality test: any representable nonzero difference is nonconstant. Score parsing and normalization must therefore be deterministic. The ladder remains included. This differs from a structurally invalid ladder, which is excluded before any judge output is inspected.

When at least two judge repeats exist:

```text
sigma[f,T] = mean_ell(2 * sd_population_r(s[f,T,ell,r]))
mu[f,T]    = sqrt(C[f,T] * (1 - sigma[f,T]))
```

When exactly one repeat exists, stability is unobserved and `mu[f,T]=C[f,T]`.

## Four properties

Each property is a geometric mean over its independently, structurally validated probe set:

```text
P_eq      = GM_f median_r score(candidate_f, candidate_f)
P_bm      = GM_f mu[f,bug]
P_ms      = GM_f mu[f,missing_spec]
P_eqalpha = GM_f (1 - abs(median_r score(original_f, gold_i)
                            - median_r score(alpha_f, gold_i)))
PTI_v0    = GM(P_eq, P_bm, P_ms, P_eqalpha)
```

Alpha-renaming is the only headline invariance transform. `RENAME`, `REORDER`, and `STYLE` are optional diagnostics and cannot be substituted into `P_eqalpha`.

For every non-self score, the frozen reference preprocessing matches the paired Exp16 criterion: use the final theorem/lemma block selected by its versioned regex, or the complete gold source when no theorem/lemma block exists. Structural validation still elaborates the complete gold file. The request manifest records both the complete gold-source hash and the actual preprocessed reference hash.

If alpha is structurally blocked or its inference is declined, the only allowed fallback is the explicitly labeled `PTI_eq_bm_ms = GM(P_eq,P_bm,P_ms)`. It is not four-property PTI-v0.

## Geometric-mean numerics

For nonempty factors in `[0,1]`:

```text
GM(v) = 0                                  if any v_i is exactly zero
GM(v) = exp(mean(log(v_i)))                otherwise
```

There is no epsilon floor. Missing, non-finite, unparsable, or out-of-range values are not zeros. Empty properties are errors.

## Structural validity and coverage

Probe validity is determined without judge scores. A probe is invalid if any intended artifact is missing, duplicate/no-op, malformed, does not implement the declared syntactic transformation, or fails the required Lean 4.22 parsing/elaboration check. Bug mutations and specification removals are intended, compile-valid cumulative faults under Route B; compilation does not prove semantic worsening, and conclusions remain conditional on that metamorphic-validity assumption. Invalid probes are recorded and excluded globally.

After the structural set is frozen, score coverage is strict: the v4 threshold is `1.0`. Any missing or unparsable required score makes that property `NOT_COMPUTABLE` and the screen `DEFER`. A constant judge-score ladder is observed behavior, not missingness.

The observed repository pool contains 470 candidate files across 157 items. The nominal three-agent grid contains 471; `24_matrix_multiply__agent1.lean` is absent and is recorded as a structural missing artifact rather than imputed.

## Frozen analysis policy

- Human panel: the defensible 72-row intersection; the three stale `0_unsafeMultiply_safe` rows are excluded because their historical gold provenance points to the vulnerable file.
- Human views: recomputed average of strict and lenient is primary; strict and lenient are secondary.
- Judge repeats: three, aggregated by median.
- Controls: `editdist_e1` is exact normalized character-Levenshtein similarity; `random_r1` is the frozen SHA-256/seed-42 baseline used by the paired historical criterion rows. Each deterministic value is repeated at all three repeat IDs, matching the historical control contract. A checked fixture reproduces the stored Exp16 score `0.811802` from the frozen reference extraction.
- Score coverage: 100% within each frozen structural probe set.
- Human-criterion coverage: 100% after exact legacy-cache lineage checks. Error/parse fallback values are missing observations, not neutral scores. The legacy cache stores one reasoning string for the first repeat only, so the non-fallback check is limited to that stored first-repeat reasoning plus exact three-score agreement; later-repeat parse recovery cannot be classified independently from this legacy record.
- Property/PTI bootstrap: 10,000 percentile replicates, seed 0, clustered by base artifact `f` with shared resampling across properties.
- Bridge: primaries-only Spearman is primary; Kendall tau-b is robustness; pooled controls are secondary; judge is the bootstrap unit.
- Undefined bridge bootstrap replicates are omitted and their valid count is reported.
- SESOI: bridge `rho=0.5`; the frozen design simulation reports the power of the complete point-estimate-plus-bootstrap-CI decision rule. With only four valid primaries, the bootstrap interval excludes zero only for the perfect rank order, so the reported positive-rule power is the probability of that discrete event rather than a smooth large-sample power curve.
- Screening thresholds remain unfrozen; no `PASS-SCREEN` claim is permitted.
- QWK is omitted because half-score encoding was not frozen.

## Required outputs

Every result must include `metric_version="PTI_v0"`, exact probe and score-manifest fingerprints, property statuses and coverage, zero counts, per-ladder diagnostics, judge roles/families, and bootstrap configuration. Legacy JTI/TIvar files remain compatibility artifacts and must never be renamed or reported as PTI-v0.

The metric and transformer source hashes are intentional config-fingerprint integrity gates. Any byte change to either file, including a comment-only change, requires deterministic config and downstream-artifact regeneration. The raw pipeline-file hash is provenance only; `PIPELINE_VERSION` is its semantic identity and must be bumped for a semantic pipeline change. Structural manifests also record the host platform and measured filesystem case sensitivity because this checkout has lowercase `veribench` source/olean paths while some imports use `VeriBench`.

The canonical executable is `experiments/archive/04_veribench_validation/run_pti_v0.py`. It contains no inference client and cannot load API credentials. Paid scoring requires a separately reviewed scorer, an exact request/cost quote, and explicit approval.
