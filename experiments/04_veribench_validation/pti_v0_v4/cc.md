# Reproduce the frozen PTI-v0 v4 zero-spend stage

**TLDR:** Load the repository rules, verify `PROTOCOL.md` and `frozen_config.json` are unchanged, then run the no-API commands in `README.md` through the gated bridge status. Success means every deterministic artifact regenerates with matching fingerprints and the bridge remains `NOT_COMPUTABLE` unless a complete, committed primary-judge property table already exists. Never load an LLM key, initiate paid inference, edit the active manuscript, or manufacture missing scores.

Work from the repository root on a feature branch. Read `experiments/28_new_notation_and _experiments/03-SPEC-OVERRIDES-R41-R49.md`, `docs/spec/PTI_V0.md`, and this directory’s locked protocol before executing anything.

Run the command sequence in `README.md` exactly. Treat a structural hash mismatch, failed required Lean elaboration, incomplete score cell, panel mismatch, or property hard-gate failure as an explicit blocked outcome. Run the focused pytest suite, Ruff checks, `lake build`, package build, and `git diff --check`; report the exact artifact hashes and spend of `$0`.

Do not compute a bridge statistic from local controls alone. A future computed bridge requires a complete admissible score payload, a separately recorded inference approval, and the full SHA of a pre-bridge commit containing the byte-identical property output.
