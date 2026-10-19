# Experiment 56 — Frozen candidate definitions

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex/cj-e56-training-margin/experiments/56_semantic_margin_training_only_diagnosis_and_revisions/CANDIDATE_DEFINITIONS.md>

**TLDR:** The property family is fixed before training outcomes: raw semantic-minus-formatting margin, identity-headroom normalization, and a specificity candidate using only existing audit-confirmed redundant weakening edits with a retained-guarantee rationale. This file is reusable implementation-level detail; `PROTOCOL.md` is the scientific contract.

| Candidate | Per-task definition | Availability rule |
|---|---|---|
| `original_S_minus_F` | `S - F` | identity; all formatting; at least 80% strict; at least 80% tasks |
| `headroom_normalized` | `(S - F) / I` | original support plus nonzero identity `I` |
| `semantic_specificity` | `S - G` | original support plus audit-confirmed redundant weakening controls matching the task |

`S` is the mean accepted identity-minus-strict-weakening median; `F` is the mean absolute identity-minus-formatting median; and `G` is the mean absolute identity-minus-audit-confirmed-redundant-weakening median.
Medians need at least two accepted repeats and accepted statuses are exactly `measured` and `deterministic`.
An audit control requires `label == redundant`, a nonempty `restated_by`, and a nonempty retained-guarantee rationale in `why`; `unclear` is never promoted to a control.
