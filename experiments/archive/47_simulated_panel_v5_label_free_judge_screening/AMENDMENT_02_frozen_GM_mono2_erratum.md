# Frozen `GM_mono2` composition correction

**Doc link:** [Main protocol](PROTOCOL.md)
**TLDR:** The historical experiment-39 implementation defines `GM_mono2` as the geometric mean of reference and candidate theorem-deletion components. This additive correction preserves the original protocol and requires candidate deletion probes before any property or criterion measurement.

Written: 10-08-2026 10:43 PDT. Target reconstruction had already occurred, but no experiment-47 property value, criterion association, or new judge score had been computed at this amendment.

Authority: frozen experiment-39 source [analysis_lib.py](../39_label_free_proxy_index_train_val_test_over_judge_families/scripts/analysis_lib.py), line 32, has `"GM_mono2": ("gm", ("ms_gold", "ms_cand"))`; `candidate_value` at line 335 applies the geometric mean after component aggregation.

- Correct the parenthetical prose in the immutable protocol: `GM_mono2` is `geometric_mean(C_ms_gold, C_ms_cand)`, not a reference-deletion-plus-bug composition. `C_bm_gold` remains a separate prespecified property.
- Build and fail-closed-compile the frozen experiment-39 candidate theorem-deletion ladders (up to three cumulative levels) for all fresh candidate artifacts. Score their declared cells with the original parser and repeat rules, retain structural failures and missing cells, and recompute the complete admission manifest and Valkyrie quote before new scoring.
- `GM_mono2` is candidate-dependent. For leave-one-agent-group-out selection, aggregate `ms_cand` only from non-held-out candidate groups while `ms_gold` remains the declared shared-reference component. For five task folds, aggregate both components only from the four selected task folds. The pooled value is the geometric mean of the component means, never a mean of per-item geometric means.
- This correction was discovered by source-code verification before any experiment-47 property value, criterion association, or outcome-informed property choice. It changes neither the protocol bytes nor the fixed judge pool, target definition, scoring limits, or other four primary properties.
