# Errata: experiment 46 frozen protocol wording

**Date:** 10-08-2026.

`PROTOCOL.md` is byte-frozen and is not modified by this erratum.

The direction-gated deletion section says that the experiment 39 `ms_gold` ladder removes “theorem statements AND unit tests.”
That description conflates this helper with an older pipeline.
The actual E39 helper is [`scripts/probes.py:116-136`](../../39_label_free_proxy_index_train_val_test_over_judge_families/scripts/probes.py#L116-L136): `delete_theorems_ladder` finds `theorem` and `lemma` declarations through `theorem_decls` ([lines 47-70](../../39_label_free_proxy_index_train_val_test_over_judge_families/scripts/probes.py#L47-L70)) and cumulatively deletes those declarations.
The E39 builder invokes that helper for gold ladders at [`scripts/build_probes.py:44-50`](../../39_label_free_proxy_index_train_val_test_over_judge_families/scripts/build_probes.py#L44-L50).
It does not delete unit tests.

This wording correction does not alter any formula, source cache, or eligibility rule.
In particular, `ms_gold` intentionally has one accepted repeat per level, so `deletion_tvd` remains unavailable under the frozen requirement of at least two accepted repeats at every level.
