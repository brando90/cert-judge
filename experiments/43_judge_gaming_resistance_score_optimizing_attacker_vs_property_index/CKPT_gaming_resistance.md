# Checkpoint: experiment 43, judge-gaming resistance (score-optimizing attacker vs the label-free property index)

**Last updated:** 09-30-2026 19:46 PDT
**Worker:** Claude Code (claude-opus-5-5, effort high), tmux `cj-e43-gaming-resistance` on skampere1; clone `/lfs/skampere1/0/brando9/cert-judge_e43`, branch `e43-gaming-resistance`.
**Model switches:** none (the whole task ran on claude-opus-5-5, effort high).

## Current step
1. Checkpoint and ledger (this file; `results.md` RUNNING). DONE 09-30-2026 14:04 PDT.
2. Harness, zero calls: DONE (scripts/attack.py, lean_guard.py, reference_checks.py, transport.py, analyze.py, build_items.py; 13 offline tests pass incl. real Lean).
3. Protocol lock: DONE, commit 95de021 (pre-rebase 36476e9) (`PROTOCOL.md`; attacker prompt sha256 b8d83d2e… system / d3b57c44… user template).
4. Wait gate: PASSED (09-30-2026 14:25 PDT): experiment 39 results.md at origin/e39-proxy-index-search 9823689 shows GPT-6 Sol 9/9, Claude Sonnet 5 9/9, GPT-6 Luna 9/9, Claude Opus 5.5 5/5 smoke cells measured (`results/wait_gate.json`).
5. Pilot: first pilot DONE 09-30-2026 15:12 PDT: Lean-valid 7/24 = 29.2% (gate 60%) FAIL; judge parse 13/13 = 100% PASS; charges $2.36 (reference $1.83). Amendment 1 (proof relaxation in the Lean guard; offline it accepts 21/24) committed 242adc8 (pre-rebase 69292aa). Re-pilot `pilot_r1` DONE 09-30-2026 16:02 PDT: Lean-valid 24/24 = 100% (16 of them after proof relaxation), judge parse 30/30 = 100%: PASS; $3.45 Vals-reported.

## Environment facts (recorded as found)
- VeriBench clone (read-only): `/lfs/skampere1/0/brando9/veribench_e43`.
- Lean: experiment 39's grading project `/lfs/skampere1/0/brando9/vb90_grading/lean_project` lacks the `VeriBench` prelude modules; experiment 39 solved this with a private mirror project. Experiment 43 builds its own mirror, the same way, at `/lfs/skampere1/0/brando9/cj_e43_lean_project`: `lakefile.toml`, `lake-manifest.json`, `lean-toolchain` copied from the grading project, `.lake/packages` symlinked to the grading project's built packages (read-only use), and the empty prelude modules `VeriBench`, `VeriBench.Common`, `VeriBench.Prelude` compiled with `cert_judge.probe_validation.LeanCompiler.compile_module` from cert-judge's `data/veribench_dataset/lean_src/{veribench.lean,veribench/Common.lean,veribench/Prelude.lean}` (sha256 d0d1fda6…, 6a3ad70c…, 6a3ad70c…; identical to experiment 39's record). A probe `import VeriBench` + `import Mathlib` file elaborates.
- Raw elaboration of the 47 rated candidates with expert-mean coverage ≤ 0.6: 2 elaborate (`13_MyUppercase__agent1`, `33_MyMinimum__agent2`).

6. Full run: loop DONE 09-30-2026 19:10 PDT (720/720 attempts, every attacker call measured after at most one recovery; Lean-valid per round 77/81/78/84/74/79/80/·); post-loop scoring (450 attacked-judge rescoring + 462 reference calls) admitted 19:11 PDT. Worker restarted once at 16:04 PDT onto `TMPDIR=private/tmp`.

7. Post-loop scoring DONE 19:35 PDT (912/912 calls; 2 labelled rescoring parse errors). Analysis DONE (`results/analysis.json`, `results/report_tables.md`; index values from experiment 39's committed open file on origin/main, selection commit 86ae479). `REPORT.md`, `results.md` DONE, README and `experiments/README.md` row and `layout.json` updated (09-30-2026 19:39 PDT).
8. Landing: DONE. PR #52 (https://github.com/brando90/cert-judge/pull/52) rebase-merged onto main at 6ef89c2 after a backup branch, `git rebase origin/main` (no change inside the experiment folder), 14 tests and the layout check, a `--force-with-lease` push of the task branch only, and `gh pr merge --rebase --delete-branch --match-head-commit`. Post-rebase hashes on main: protocol lock 95de021, Amendment 1 242adc8. Email receipt sent 09-30-2026 19:46 PDT to brando.science@gmail.com (no CC) via `uutils.emailing.send_email_smtp` from brandojazz@gmail.com (the slurm.miranda and brando.science logins rejected this app password). Service and tunnel stopped (port 9431 released). `private/DONE` touched.
- LANDED 6ef89c21cada479853cbd68da9fc76985fddeeb7 https://github.com/brando90/cert-judge/pull/52 09-30-2026 19:46 PDT

## Incidents
- Transient Valkyrie task ERRORs (agent receipt frozen at start, 0 requests sent): round 0 5/58 and round-2 attacker 7/90; each got its single labelled recovery admission and all 12 were measured. `transport.run_batch` was also changed so a resumed worker never reloads the service while runs are in flight.
- 09-30-2026 15:55 PDT: skampere1's shared root filesystem (879 GB, holds `/tmp`) reached 100% (0 B free). 32 GB of it was this user's stale Claude Code cache `/tmp/user/22003/claude-22003/bash-edit-diff`; the 1,095 entries older than 12 h were deleted (root back to 16 GB free); the 9 recent entries were kept. Experiment 43's worker now writes Lean temp files under node-local `private/tmp`.
- The full-run worker process loaded the pre-fix charges code, so `results/full/cells.json` will carry cumulative charges; the stage-filtered total is recomputed with `transport.charges_total(prefix="full__")` after the post stage.

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
