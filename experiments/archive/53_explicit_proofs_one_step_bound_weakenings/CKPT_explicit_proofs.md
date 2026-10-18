# Checkpoint: explicit proofs for one-step weakenings

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/53_explicit_proofs_one_step_bound_weakenings/CKPT_explicit_proofs.md>

Created: 10-18-2026 13:58 PDT
Last updated: 10-18-2026 14:08 PDT

## State

1. **Goal** — prove the forward direction of the five elaborating one-step weakenings.
2. **Now** — done. 4/5 valid. Archived after the verdict.
3. **Results** — Fibonacci, is-prime, below-zero, and uppercase pass. Bisect's renamed `Post` does not unfold.
4. **Blocked** — no judge calls. Scoring was not in this run.
5. **Next** — a judge batch only if a cap is spent on these four files. Not started.

## Log

- 10-18-2026 13:58 PDT: Locked the five edits and the 4-of-5 gate.
- 10-18-2026 14:05 PDT: Combined `unfold` failed. Split unfolds prove Fibonacci.
- 10-18-2026 14:08 PDT: 4/5 valid, reverse unproved on all five. Construction SUCCESS.
