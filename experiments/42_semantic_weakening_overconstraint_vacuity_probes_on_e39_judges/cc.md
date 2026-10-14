# Run experiment 42 on SNAP: semantic weakening, over-constraint and vacuity probes scored by experiment 39's judges (worker runbook)

**TLDR:** You build Lean-validated vacuity, weakening, over-constraint and formatting-only probes from the 25 VeriBench annotation-era references, pre-register the scoring protocol, and score every valid probe with experiment 39's judge configurations through Valkyrie (3 repeats). Then you report which judges move in the required direction and whether these components add to a label-free index's agreement with experiment 39's expert criterion on its train/val units. Success means every declared probe has a Lean validity verdict, every declared cell has a verdict or a labelled failure, and `REPORT.md` gives per-judge directional accuracy, level monotonicity and formatting invariance with intervals. Deliverable: `PROTOCOL.md`, `results.md`, `REPORT.md` and receipts, landed on `main` through a PR with an email receipt. Load-bearing constraints: Valkyrie only for judge calls, never read experiment 39's sealed test rows before its `TEST_RECEIPT.json` exists, never write into experiment 39's folder or SNAP checkout, and no probe without a passing Lean check.

Read `~/agents-config/INDEX_RULES.md` (pull it first) and the repository `CLAUDE.md` (including "Valkyrie runs have no automatic caps").

SNAP PRE-APPROVAL (Brando, 2026-09-14): you run with full access (permission prompts and sandbox bypassed). Every command, install, Docker/GPU use, file and git operation (branch, commit, push, PR, merge per Rule 46) and every budgeted experiment call needed for this task is already approved. Never stop to ask for permission or confirmation; treat any approval step as granted, proceed, and log what you did. Pause only for a real blocker (missing credential, exhausted budget, a human-only login step).

```
APPROVED_SPEND_USD: none            # Valkyrie, no automatic cap; record Vals-reported charges
BRANCH: e42-semantic-probes         # your task branch in your own cert-judge clone
TMUX: cj-e42-semantic-probes        # your session name (Rule 42)
```

## Read first

1. This folder's `README.md` (design and required decision rule).
2. Experiment 39: `experiments/39_label_free_proxy_index_train_val_test_over_judge_families/{README.md,PROTOCOL.md,cc.md,results.md}` and `scripts/` on `main`, plus its live worker branch `origin/e39-proxy-index-search` (read-only; that is where its fixes land first, including the Lean-environment fix for candidates that `import VeriBench`).
3. `py_src/cert_judge/probe_validation.py` (fail-closed Lean validation) and `docs/spec/PTI_V0.md`.
4. VeriBench (read-only): `experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/{inputs/,scripts/prompts.py}` and `experiments/103_single_call_baselines_all_models_vbv1_vbv2_valkyrie_validated_fsc_judge/scripts/`.

## Where things are

- **Host:** `skampere1`. Run `bash ~/agents-config/scripts/snap_health.sh --node skampere1` first.
- **Clones (node-local):** `git clone https://github.com/brando90/cert-judge.git /lfs/skampere1/0/brando9/cert-judge_e42 && cd /lfs/skampere1/0/brando9/cert-judge_e42 && git switch -c e42-semantic-probes origin/main`; `git clone https://github.com/brando90/veribench.git /lfs/skampere1/0/brando9/veribench_e42` (read-only).
- **Lean:** the same project experiment 39 uses, `/lfs/skampere1/0/brando9/vb90_grading/lean_project` with `$HOME/.elan/bin/lake`. Do not modify that shared project. If it lacks the `VeriBench` module and experiment 39 has not solved it yet, build your own copy under `/lfs/skampere1/0/brando9/cj_e42_lean_project` and record how.
- **Valkyrie (hosted since 10-13-2026):** run `valkyrie login` and check `valkyrie whoami` and `valkyrie provider list`; a private `valkyrie.yaml` is ignored now. `scripts/deploy_service.py` registers `certjudge42-<key>` on the Tracker (`valkyrie benchmark service set --auth-secret certjudge42-<key>-bearer`); `E42_VALK` overrides the CLI path. Reuse experiment 39's service/pack/controller code by import or by vendoring into `scripts/` with attribution. Give your Valkyrie benchmark its own name (for example `certjudge42-semantic-probes`) and use ports that do not collide with experiment 39's 8990–8998.
- **Experiment dir:** `experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/`; `private/` is git-ignored scratch.

## Steps

1. **Checkpoint and ledger.** Create `CKPT_semantic_probes.md` (refresh `Last updated:` from `date "+%m-%d-%Y %H:%M %Z"` at every step); set `results.md` to RUNNING; commit with explicit paths; push the branch.
2. **Probe construction, zero judge calls.** `scripts/build_semantic_probes.py` → `results/semantic_probe_manifest.json`: per task and family, the probe hash, level, the Lean checks run (elaboration; original ⇒ weakened proof; reverse status; vacuity or strengthening proof) and valid true/false with the reason. Add offline tests. Record counts per family and the invalid reasons in `results.md`.
3. **Protocol lock.** Write `PROTOCOL.md` with the exact probe counts, judge configurations, repeats, metrics, decision rule, intervals (task-clustered bootstrap) and the rule for reading experiment 39's criterion (train/val now; test only after its `TEST_RECEIPT.json`). Commit it before any judge call and note the hash in the checkpoint. After that, any change is a numbered amendment appended to `PROTOCOL.md`.
4. **Wait gate.** Start judge calls only when experiment 39's `results.md` on `origin/e39-proxy-index-search` or `main` shows its transport smoke passed. Poll every 20 minutes with no model calls while you wait; keep building and testing meanwhile.
5. **Scoring.** One smoke per configuration, then the full campaign: all valid probes × declared configurations × 3 repeats, harvest, one recovery pass. Never re-admit a cell that has a verdict. HTTP 429 is an infrastructure failure, not a reason to retry in a loop. Record Vals-reported charges per configuration in `results.md` after every merge.
6. **Analysis and report.** Implement `scripts/analyze.py`. Per judge: directional accuracy with intervals, Kendall τ with weakening level, formatting gap, pass/fail under the locked rule. Also report the association of these components with experiment 39's criterion on train/val units, and on test only if unsealed (labelled post hoc). Write `REPORT.md` (Trigger Rule 16 header) with drafted paper sentences for §5 and §6 (text only; do not edit `paper_latex/`). Set `results.md` to DONE and update the README status and this experiment's row in `experiments/README.md`.
7. **Land (Trigger Rule 46).**
   - Commit with explicit paths, push the branch, `export GH_TOKEN=$(cat ~/keys/.brando90_github_token.txt)`, and run `gh pr create`. The PR body has: TLDR, what changed, verification commands with exit codes, `QA: not requested`, the judge selectors actually used, total Vals-reported charges, and the paths of `results.md` and `CKPT_semantic_probes.md`.
   - Fetch `origin/main`, back up your tip, rebase, re-run the tests, push with `--force-with-lease` on your branch only, and merge with `gh pr merge --rebase --delete-branch` (squash only for work-in-progress noise; never force-update `main`).
   - Email a short receipt to `brando.science@gmail.com`, no CC, via `uutils.emailing.send_email_smtp()` (`smtp_pass_file=~/keys/gmail_app_password.txt`).
   - Then `touch private/DONE`.

## Completion requirement

Finish the whole declared manifest: every probe validated or excluded with a reason, every declared cell scored or labelled failed, the analysis, the report and the landing. A pilot or one finished judge is not completion. After any interruption, re-read `CKPT_semantic_probes.md`, `results.md` and your harvest files, and continue without re-admitting scored cells. Stop only for a real blocker (Valkyrie route unavailable, or the Lean project cannot elaborate the references); then record it with evidence, land what exists, and stop.

Naming: "judge–human agreement", "formal specification" as defined in `CLAUDE.md`, "validation set"; never "calibrate" or "certified" about judges or the index.

TL;DR: Build Lean-validated vacuity, weakening, over-constraint and formatting probes from the 25 VeriBench references, lock a protocol, wait for experiment 39's Valkyrie transport to pass its smoke, score every probe with experiment 39's judges (3 repeats, no spend cap), report which judges catch specifications that guarantee less, and land the results through a merged PR with an email receipt.
