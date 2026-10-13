# Run experiment 43 on SNAP: judge-gaming resistance, a score-optimizing attacker against the label-free property index (worker runbook)

**TLDR:** You build an attack harness in which one pre-registered attacker model, called through Valkyrie, edits Lean candidate specifications for K = 8 iterations to raise one judge's score. Edits must elaborate in Lean and keep the implementation unchanged. You run it against six judge configurations from experiment 39's panel on 15 low-coverage candidates, and measure each judge's gaming gap against a held-out reference (the validated VeriBench coverage ensemble plus deterministic vacuity, duplicate and spam checks). Then you test whether the label-free index predicts the gap. Success means the protocol is locked before any call, the pilot gates pass (or the failure is documented), every declared (judge, item, iteration) cell has a verdict or a labelled failure, and `REPORT.md` gives the gaming gaps with intervals and the index association. Deliverable: `PROTOCOL.md`, `results.md`, `REPORT.md` and receipts, landed on `main` through a PR with an email receipt. Load-bearing constraints: Valkyrie only for model calls, the attacker never sees the reference or any labels, experiment 39's sealed test rows are read only after its `TEST_RECEIPT.json` exists, and nothing is ever written into experiment 39's folder or checkout.

Read `~/agents-config/INDEX_RULES.md` (pull it first) and the repository `CLAUDE.md` (including "Valkyrie runs have no automatic caps").

SNAP PRE-APPROVAL (Brando, 2026-09-14): you run with full access (permission prompts and sandbox bypassed). Every command, install, Docker/GPU use, file and git operation (branch, commit, push, PR, merge per Rule 46) and every budgeted experiment call needed for this task is already approved. Never stop to ask for permission or confirmation; treat any approval step as granted, proceed, and log what you did. Pause only for a real blocker (missing credential, exhausted budget, a human-only login step).

```
APPROVED_SPEND_USD: none              # Valkyrie, no automatic cap; record Vals-reported charges
BRANCH: e43-gaming-resistance         # your task branch in your own cert-judge clone
TMUX: cj-e43-gaming-resistance        # your session name (Rule 42)
```

## Read first

1. This folder's `README.md` (design).
2. Experiment 39 on `main` and its live branch `origin/e39-proxy-index-search` (read-only): `README.md`, `PROTOCOL.md`, `cc.md`, `results.md`, `scripts/` (panel, prompt families, Valkyrie transport, Lean handling).
3. VeriBench (read-only): `experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/{README.md,JUDGE_EXPLAINER.md,scripts/prompts.py,configs/,inputs/}`, the source of the validated `H2` reference judge.
4. `py_src/cert_judge/probe_validation.py` for fail-closed Lean checks.

## Where things are

- **Host:** `skampere1`. Run `bash ~/agents-config/scripts/snap_health.sh --node skampere1` first.
- **Clones (node-local):** `git clone https://github.com/brando90/cert-judge.git /lfs/skampere1/0/brando9/cert-judge_e43 && cd /lfs/skampere1/0/brando9/cert-judge_e43 && git switch -c e43-gaming-resistance origin/main`; `git clone https://github.com/brando90/veribench.git /lfs/skampere1/0/brando9/veribench_e43` (read-only).
- **Lean:** experiment 39's project `/lfs/skampere1/0/brando9/vb90_grading/lean_project` (do not modify it). If it lacks the `VeriBench` module and experiment 39 has not solved that yet, build your own copy under `/lfs/skampere1/0/brando9/cj_e43_lean_project` and record how.
- **Valkyrie:** `~/.config/valkyrie/valkyrie.yaml` (never print or copy it). Use your own benchmark name (for example `certjudge43-gaming`) and ports that do not collide with experiments 39 (8990–8998) or 42.
- **Experiment dir:** `experiments/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/`; `private/` is git-ignored scratch.

## Steps

1. **Checkpoint and ledger.** Create `CKPT_gaming_resistance.md` (refresh `Last updated:` from `date "+%m-%d-%Y %H:%M %Z"` at every step); set `results.md` to RUNNING; commit with explicit paths; push the branch.
2. **Harness, zero calls.**
   - `scripts/attack.py`: the loop state machine, with resumable per-cell state under `private/`.
   - `scripts/lean_guard.py`: elaboration, an implementation-bytes-unchanged check, and statement extraction.
   - `scripts/reference_checks.py`: vacuity, trivially decidable statements, duplicates and statement-count inflation.
   - Offline tests with a fake judge and a fake attacker (for example, an attacker that appends duplicate theorems must be flagged by the reference checks).
3. **Protocol lock.** Write `PROTOCOL.md` before any call, covering:
   - the attacked configurations and why;
   - the item list and its rule;
   - the attacker model, selector and optimization prompt (bytes hashed);
   - K, repeats of the reference scoring, and the outcome metrics;
   - intervals (task-clustered bootstrap), pilot gates (at least a 60% Lean-valid edit rate, at least a 95% judge parse rate), and the reading rule for the index association.

   Commit it and note the hash in the checkpoint. Any later change is a numbered amendment.
4. **Wait gate.** Start model calls only once experiment 39's `results.md` shows its transport smoke passed. Poll every 20 minutes with no model calls while you wait.
5. **Pilot.** 3 items × 2 judges × 4 iterations. Check the gates. If they pass, continue automatically. If they fail, fix the harness (not the protocol's scientific choices), record an amendment, and re-pilot once.
6. **Full run.** 6 judges × 15 items × K = 8, then score each item's start and final candidate with the reference ensemble (3 repeats) and the deterministic checks. Never re-admit a cell that has a verdict. HTTP 429 is an infrastructure failure. Record Vals-reported charges after every merge.
7. **Analysis and report.** `scripts/analyze.py`: per-judge gaming gap with intervals, the flagged share, example trajectories, and the index association across judges (experiment 39's selected index when available, plus the frozen `TI_var` and `PTI_v0`). Write `REPORT.md` (Trigger Rule 16 header) with drafted paper sentences for §6 (text only; do not edit `paper_latex/`). Set `results.md` to DONE and update the README status and this experiment's row in `experiments/README.md`.
8. **Land (Trigger Rule 46).**
   - Commit with explicit paths, push the branch, `export GH_TOKEN=$(cat ~/keys/.brando90_github_token.txt)`, and run `gh pr create`. The PR body has: TLDR, what changed, verification commands with exit codes, `QA: not requested`, the attacker and judge selectors actually used, total Vals-reported charges, and the paths of `results.md` and `CKPT_gaming_resistance.md`.
   - Fetch `origin/main`, back up your tip, rebase, re-run the tests, push with `--force-with-lease` on your branch only, and merge with `gh pr merge --rebase --delete-branch` (never force-update `main`).
   - Email a short receipt to `brando.science@gmail.com`, no CC, via `uutils.emailing.send_email_smtp()` (`smtp_pass_file=~/keys/gmail_app_password.txt`).
   - Then `touch private/DONE`.

## Completion requirement

Finish the whole declared manifest: pilot, all 6 × 15 × 8 attack cells (or a documented `NOT_RUN_ROUTE` for a judge the transport cannot serve), all reference scorings, the analysis, the report and the landing. A pilot alone is not completion. After any interruption, re-read `CKPT_gaming_resistance.md`, `results.md` and your per-cell state, and continue without re-admitting scored cells. Stop only for a real blocker (for example, the Valkyrie route is unavailable); then record it with evidence, land what exists, and stop.

Naming: "judge–human agreement", "formal specification" as defined in `CLAUDE.md`; never "calibrate" or "certified" about judges or the index.

TL;DR: Build a Lean-guarded attack loop in which an attacker model raises one judge's score using only that score, lock the protocol, wait for experiment 39's transport smoke, run a pilot and then 6 judges × 15 low-coverage candidates × 8 iterations through Valkyrie, measure each judge's gain against the held-out validated VeriBench ensemble and deterministic vacuity/spam checks, test whether the label-free index predicts gaming resistance, and land the results through a merged PR with an email receipt.
