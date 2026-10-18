# Strict weakening inside the deployable prompt family

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/51_strict_weakening_within_fuller_context_heldout_judges/README.md>

**TLDR:** Done 10-18-2026. On 12 held-out fuller-context judges, strict weakening accuracy is Spearman −0.324 [−0.761, 0.045] p-val=0.8656 against the existing human-agreement criterion (reading REVERSED). Ten of the twelve scores are exactly 1, so the probes do not rank the judges one would deploy. No new model calls.

## Status

DONE. Report: [RESULTS_strict_within_family.md](RESULTS_strict_within_family.md). Protocol: [PROTOCOL.md](PROTOCOL.md).

## Why this and not another cached selector

The deletion-monotonicity screen passes only across prompt families. The judges one would deploy all use fuller-context prompts. This test asked whether the strict subset of the existing weakening probes repairs that within-family association. It does not. The locked rule says to stop fitting new scores on this cache.
