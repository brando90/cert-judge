# Checkpoint: one-step bound weakenings

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/52_one_step_bound_weakening_probes_lean_checked/CKPT_one_step_weakenings.md>

Created: 10-18-2026 10:25 PDT
Last updated: 10-18-2026 10:33 PDT

## State

1. **Goal** — Lean-check seven one-step bound relaxations, and keep set N on the frozen fixed rubric.
2. **Now** — done. Construction STOP at 0/7. Archived.
3. **Results** — 5 elaborate with reverse unproved; default tactics do not prove the forward direction. 2 do not elaborate because a finished proof has the tighter type.
4. **Blocked** — scoring stays off. The $50 cap was conditional on 4 valid probes.
5. **Next** — do not call judges on these files. A new checker with an explicit proof is a separate experiment.

## Log

- 10-18-2026 10:25 PDT: Locked the seven edits, the 4-of-7 gate, the set-N adoption, and the $50 scoring cap.
- 10-18-2026 10:29 PDT: Default checker returned 0/7. Construction STOP. No judge calls.
