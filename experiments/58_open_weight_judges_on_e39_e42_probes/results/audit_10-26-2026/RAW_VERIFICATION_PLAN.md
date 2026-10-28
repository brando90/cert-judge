# FarmShare raw-data verification contract

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/58_open_weight_judges_on_e39_e42_probes/results/audit_10-26-2026/RAW_VERIFICATION_PLAN.md>

**TLDR:** Verify the existing collected snapshot byte-for-byte and replay its frozen parser and analysis; make no new model calls or scientific choices.

Recorded before acquiring or replaying the raw archive, 10-26-2026 14:40 PDT.
Scope: `58_open_weight_judges_on_e39_e42_probes`, the four-judge FarmShare snapshot reported in PR #83.
Expected archive SHA256: `3fd6e86cb2b1b68de79c9c7dfb31e0b63dbf111ae210eddea5c4fc0767c486d7`.

| Check | Expected outcome | Failure/control expectation |
|---|---|---|
| Archive digest and collection manifest | Exact archived digest; every listed file matches; every raw/meta/harvest input covered | Altered bytes, missing file, duplicate/escaping path fail |
| Raw identity | Every raw row maps to one declared rendered cell, with matching prompt hash | Duplicate, unknown, non-rendered or wrong-hash row fails, even if the old harvester would ignore/overwrite it |
| Recorded generation | Per-cell seed and budget equal the frozen driver rules; output token count within budget | Wrong seed/budget or unknown raw status fails; a missing raw row stays missing |
| Parser replay | Rebuilding from exact raw text, prompt rows and metadata equals the saved harvest, excluding only `written_utc` | Score/status/rationale/metadata change fails; empty or unclosed reasoning text follows the frozen parse-error/incomplete rules |
| Coverage | Reported snapshot has 72 observed harvests, 36 observed model/prompt units; repaired analysis retains all 117 declared units | Empty input cannot count as a completed raw verification; absent units stay unavailable |
| Recorded runtime | Compare all existing runtime fields with frozen E58 constants | Any deviation is reported separately; it is not silently admitted or rewritten |
| Numerical reproduction | Observed-unit primary statistics and gate flags match PR #83 exactly at frozen seeds and 10,000 draws | Differences are traced to raw inputs or documented implementation corrections, never adjusted to obtain a match |

This is a deterministic audit of previously collected data, not a new judge-validation experiment. The oracle is the unchanged archive plus independently checked frozen identities and driver rules. Literal compliance means replaying the recorded final answer through the original parser. An all-missing or empty input must not pass completion. Synthetic malformed rows are controls for the verifier, not new scientific results. The already-reproduced processed-unit gates are the comparison baseline.

Trace at least one measured and one failed raw response through prompt hash, final-text extraction, parsed score/status and saved cell. Inspect a deterministic spread of saved responses across score levels and failure states; retain raw texts privately and publish hashes/counts only. Do not infer executed weight identity from a metadata claim.
