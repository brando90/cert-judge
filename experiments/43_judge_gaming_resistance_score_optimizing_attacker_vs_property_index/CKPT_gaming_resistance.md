# Checkpoint: experiment 43, judge-gaming resistance (score-optimizing attacker vs the label-free property index)

**Last updated:** 09-30-2026 14:25 PDT
**Worker:** Claude Code (claude-opus-5-5, effort high), tmux `cj-e43-gaming-resistance` on skampere1; clone `/lfs/skampere1/0/brando9/cert-judge_e43`, branch `e43-gaming-resistance`.
**Model switches:** none so far (fallback per dispatcher: claude-sonnet-5 at high effort; record any switch here).

## Current step
1. Checkpoint and ledger (this file; `results.md` RUNNING). DONE 09-30-2026 14:04 PDT.
2. Harness, zero calls: DONE (scripts/attack.py, lean_guard.py, reference_checks.py, transport.py, analyze.py, build_items.py; 13 offline tests pass incl. real Lean).
3. Protocol lock: DONE, commit 36476e9 (`PROTOCOL.md`; attacker prompt sha256 b8d83d2e… system / d3b57c44… user template).
4. Wait gate: PASSED (09-30-2026 14:25 PDT): experiment 39 results.md at origin/e39-proxy-index-search 9823689 shows GPT-6 Sol 9/9, Claude Sonnet 5 9/9, GPT-6 Luna 9/9, Claude Opus 5.5 5/5 smoke cells measured (`results/wait_gate.json`).
5. Pilot: STARTING via `scripts/worker_loop.sh` (tmux window `cj-e43-gaming-resistance:worker`, log `private/logs/worker.log`).

## Environment facts (recorded as found)
- VeriBench clone (read-only): `/lfs/skampere1/0/brando9/veribench_e43`.
- Lean: experiment 39's grading project `/lfs/skampere1/0/brando9/vb90_grading/lean_project` lacks the `VeriBench` prelude modules; experiment 39 solved this with a private mirror project. Experiment 43 builds its own mirror, the same way, at `/lfs/skampere1/0/brando9/cj_e43_lean_project`: `lakefile.toml`, `lake-manifest.json`, `lean-toolchain` copied from the grading project, `.lake/packages` symlinked to the grading project's built packages (read-only use), and the empty prelude modules `VeriBench`, `VeriBench.Common`, `VeriBench.Prelude` compiled with `cert_judge.probe_validation.LeanCompiler.compile_module` from cert-judge's `data/veribench_dataset/lean_src/{veribench.lean,veribench/Common.lean,veribench/Prelude.lean}` (sha256 d0d1fda6…, 6a3ad70c…, 6a3ad70c…; identical to experiment 39's record). A probe `import VeriBench` + `import Mathlib` file elaborates.
- Raw elaboration of the 47 rated candidates with expert-mean coverage ≤ 0.6: 2 elaborate (`13_MyUppercase__agent1`, `33_MyMinimum__agent2`).

## Decisions recorded (Rule 57)
- Attacked judges: Claude Sonnet 5 (medium) × {LEX, D0, H0, H2, P1, P8} (experiment 39 train model: open index rows; outside the reference ensemble).
- Attacker: GPT-6 Luna (high), outside the judge family and the reference ensemble; substitute `openai/gpt-5.6-luna-high`.
- Lean-valid start rule: repair ladder S0–S4 (S4 deletes failing specification/test commands, never implementation). The strict S0–S3 ladder gave only 12 eligible criterion items; S4 gives 20, of which 15 are used across 6 tasks.
- The attacker sees the task's Python source (intent), the incumbent, its score and earlier outcomes (with Lean error summaries); never gold, judge prompt, reference or labels.
- Outcome uses fresh post-loop repeats (3 attacked-judge, 3 × 2 reference) rather than in-loop maxima.
- Transport: benchmark `certjudge43-gaming`, port 9431, experiment 103 service + `vb103_judge` (bundle PASS); service reloaded between batches on a fixed tunnel.

## Next actions
- Watch the pilot; check gates in `results/pilot.json`; the full run follows automatically on PASS.
- After the full run: `scripts/analyze.py`, `REPORT.md`, ledger DONE, land (Trigger Rule 46), email, `touch private/DONE`.
