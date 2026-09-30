# Checkpoint: experiment 43, judge-gaming resistance (score-optimizing attacker vs the label-free property index)

**Last updated:** 09-30-2026 14:04 PDT
**Worker:** Claude Code (claude-opus-5-5, effort high), tmux `cj-e43-gaming-resistance` on skampere1; clone `/lfs/skampere1/0/brando9/cert-judge_e43`, branch `e43-gaming-resistance`.
**Model switches:** none so far (fallback per dispatcher: claude-sonnet-5 at high effort; record any switch here).

## Current step
1. Checkpoint and ledger (this file; `results.md` RUNNING). DONE 09-30-2026 14:04 PDT.
2. Harness, zero calls: IN PROGRESS.

## Environment facts (recorded as found)
- VeriBench clone (read-only): `/lfs/skampere1/0/brando9/veribench_e43`.
- Lean: experiment 39's grading project `/lfs/skampere1/0/brando9/vb90_grading/lean_project` lacks the `VeriBench` prelude modules; experiment 39 solved this with a private mirror project. Experiment 43 builds its own mirror, the same way, at `/lfs/skampere1/0/brando9/cj_e43_lean_project`: `lakefile.toml`, `lake-manifest.json`, `lean-toolchain` copied from the grading project, `.lake/packages` symlinked to the grading project's built packages (read-only use), and the empty prelude modules `VeriBench`, `VeriBench.Common`, `VeriBench.Prelude` compiled with `cert_judge.probe_validation.LeanCompiler.compile_module` from cert-judge's `data/veribench_dataset/lean_src/{veribench.lean,veribench/Common.lean,veribench/Prelude.lean}` (sha256 d0d1fda6…, 6a3ad70c…, 6a3ad70c…; identical to experiment 39's record). A probe `import VeriBench` + `import Mathlib` file elaborates.
- Raw elaboration of the 47 rated candidates with expert-mean coverage ≤ 0.6: 2 elaborate (`13_MyUppercase__agent1`, `33_MyMinimum__agent2`).

## Next actions
- Measure the deterministic Lean-repair ladder for attack starts; write the harness and offline tests; lock `PROTOCOL.md`.
- Wait gate: experiment 39's `results.md` must show its transport smoke passed before any model call (poll every 20 min, no model calls).
