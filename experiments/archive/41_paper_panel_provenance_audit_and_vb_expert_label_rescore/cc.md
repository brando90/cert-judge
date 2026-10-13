# Run experiment 41 on SNAP: provenance audit of the paper's validation set and re-score against VeriBench expert labels (worker runbook)

**TLDR:** You determine, task by task, whether the gold/reference file the paper's frozen judges were given matches the reference participant 1 saw when rating, confirm that the paper's two label passes are VeriBench participant 1's old-prompt passes, and recompute the paper's judge-level association under five label/item views (paper labels on all or matched items; VeriBench's corrected three-expert mean on matched or all items; participant 1's corrected pass). Success means Gate G0 reproduces the paper's nine judge-level Spearman values to 3 decimals and every view in `README.md` is reported with Spearman, Kendall, Pearson, task-clustered intervals and exact permutation p. Deliverable: `REPORT.md`, `results.md` and the `results/` tables, landed on `main` through a PR with an email receipt. Load-bearing constraints: zero model calls, frozen artifacts are read-only, and nothing under `paper_latex/` or any other experiment folder is written.

Read `~/agents-config/INDEX_RULES.md` (pull it first) and the repository `CLAUDE.md`.

SNAP PRE-APPROVAL (Brando, 2026-09-14): you run with full access (permission prompts and sandbox bypassed). Every command, install, Docker/GPU use, file and git operation (branch, commit, push, PR, merge per Rule 46) and every budgeted experiment call needed for this task is already approved. Never stop to ask for permission or confirmation; treat any approval step as granted, proceed, and log what you did. Pause only for a real blocker (missing credential, exhausted budget, a human-only login step).

```
APPROVED_SPEND_USD: 0            # zero model calls; this is an analysis of committed files
BRANCH: e41-provenance-audit     # your task branch in your own cert-judge clone
TMUX: cj-e41-provenance-audit    # your session name (Rule 42)
```

## Read first

1. This folder's `README.md`: the locked analysis plan (gate G0, views V1–V5, secondary S1–S4). Do not change it; record any deviation in `results.md`.
2. VeriBench (read-only): `experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/{README.md,REPORT.md,scripts/phase0_audit.py,inputs/provenance.json}` and `experiments/75_J1_validating_formal_spec_judge_train_val_test/{HUMAN_JUDGMENT_DATA.md,PROMPT_DIRECTION_AUDIT.md}`.
3. cert-judge: `experiments/archive/38_iclr_body_rewrite_to_trust_artifact_abstract/analysis/exact_permutation_and_subsets.py`, `experiments/archive/34_iclr_mega_rewrite_astra/analysis/number_provenance.py`, `experiments/archive/04_veribench_validation/exp16_multi_judge_human_sets.py`, and `experiments/archive/22_pooled_heldout_and_noise_ceiling/`.

## Where things are

- **Host:** `skampere1`. Run `bash ~/agents-config/scripts/snap_health.sh --node skampere1` first.
- **Your clones (node-local):** `git clone https://github.com/brando90/cert-judge.git /lfs/skampere1/0/brando9/cert-judge_e41 && cd /lfs/skampere1/0/brando9/cert-judge_e41 && git switch -c e41-provenance-audit origin/main`; `git clone https://github.com/brando90/veribench.git /lfs/skampere1/0/brando9/veribench_e41` (read-only; use `git log` / `git show <rev>:<path>` for history, never commit there).
- **Python:** `/lfs/skampere1/0/brando9/vb103_venv/bin/python` if it has numpy, scipy and pandas; otherwise create `uv venv /lfs/skampere1/0/brando9/venvs/cj_e41 && uv pip install --python /lfs/skampere1/0/brando9/venvs/cj_e41/bin/python numpy scipy pandas` and record which you used.
- **Experiment dir:** `experiments/41_paper_panel_provenance_audit_and_vb_expert_label_rescore/`; code under `scripts/`, outputs under `results/`, scratch under `private/` (add a `.gitignore` for `private/`).

## Steps

1. **Checkpoint and ledger at once.** Create `CKPT_provenance_audit.md` (refresh `Last updated:` from `date "+%m-%d-%Y %H:%M %Z"` at every step); set `results.md` to `**Status:** RUNNING (started <ts>)`; commit both with explicit paths (`git commit -- <paths>`, never `git add -A`) and push the branch.
2. **Label identity (S2 part 1).** Match the paper's three label files to VeriBench's participant files item by item (key: gold file name + candidate file name); write `results/label_identity.json` (per file: best-matching VeriBench series, identical-score counts, the pass-name mapping). Known so far: paper `pass1` (`ethan_human_scores_20260425.tsv`) = participant 1 `old_prompt/participant1_data_pass_2.tsv` on 75/75 items; paper `pass2` (`ethan_human_scores_ORIGINAL.tsv`) = participant 1 `old_prompt/participant1_data_pass_1.tsv` on 72/75.
3. **Rating dates and rater-seen references.** From VeriBench git history, date each participant-1 pass (old pass 1, old pass 2, corrected pass) and every other participant file; for each date, record the reference file bytes (hash) that were live on the mainline for each of the 25 tasks. Experiment 100's `inputs/provenance.json` already gives the 04-21→05-06-2026 annotation window; extend it if the old passes predate that window.
4. **Judge-seen references.** Establish the exact reference bytes the paper's frozen judges received for each task (the per-item scores behind the `judge_trust_vector.csv` files). Prefer direct evidence (cached prompt/request files, stored gold paths with hashes); otherwise reconstruct the pipeline's resolution at the run's commit and say so. Write `results/provenance_by_task.csv` (task, judged-reference hash, source of that fact, rater-seen hash per label series, matched yes/no). Unresolvable tasks count as unmatched.
5. **Gate G0.** Reproduce the paper's nine judge-level Spearman values from the committed vectors to 3 decimals; write `results/G0_reproduction.json`. If it fails, write the discrepancy to `results.md`, land what you have, and stop the re-analysis.
6. **Views V1–V5 and S1, S3, S4.** Implement in `scripts/rescore.py` (task-clustered bootstrap 10,000 draws with a fixed seed; exact permutation over the 8! orderings); write `results/judge_level_views.csv`, `results/per_judge_agreement.csv`, `results/lofo_loco.csv`, `results/label_agreement_matrix.csv`, and a short check for S4. Add offline tests in `scripts/test_rescore.py` (at least: Spearman/Kendall/Pearson against scipy, bootstrap reproducibility with the seed, permutation p for a known ordering).
7. **Report.** `REPORT.md` (Trigger Rule 16 header): the reading under the pre-registered rule, a table per view, which tasks were mismatched and why, the label-identity finding, drafted replacement sentences for the paper's §5.1 and §6 (text only; do not edit `paper_latex/`). Mark every unmeasured quantity as unmeasured. Update `results.md` to `**Status:** DONE`, the README status line, and this experiment's row in `experiments/README.md`.
8. **Land (Trigger Rule 46).** Commit with explicit paths; push the branch; `export GH_TOKEN=$(cat ~/keys/.brando90_github_token.txt)`; `gh pr create` with body = TLDR, what changed, verification commands with exit codes, `QA: not requested`, `Model calls: none`, the worker model actually used, and the paths of `results.md` and `CKPT_provenance_audit.md`. Then fetch `origin/main`, back up your tip (`git branch e41-backup-<ts> HEAD`), rebase, re-run the tests, push with `--force-with-lease` on your task branch only, and merge the PR with `gh pr merge --rebase --delete-branch` (squash only if the branch is work-in-progress noise; never force-update `main`). Email a short receipt (PR URL, verdict, three key numbers) to `brando.science@gmail.com`, no CC, with `uutils.emailing.send_email_smtp()` from `~/ultimate-utils` (`smtp_pass_file=~/keys/gmail_app_password.txt`). Finally `touch private/DONE`.

## Completion requirement

Finish every step: all 25 tasks classified matched / unmatched / unresolvable, G0, all five views for all three families, S1–S4, the report and the landing. A partial table is not completion. If your session is interrupted, re-read `CKPT_provenance_audit.md` and `results.md` and continue. Stop only for a real blocker (for example, the per-item judge scores behind a family's vector are missing from the repository); then write the blocker with evidence to the checkpoint and `results.md`, land what exists, and stop.

Naming: say "validation set" (never "development set"), "judge–human agreement", and never "calibrate" or "certified" about the judges or the index.

TL;DR: With zero model calls, find out whether the paper's judges saw the same reference files the rater saw, confirm that the paper's labels are VeriBench participant 1's old-prompt passes, reproduce the paper's nine judge-level correlations, then recompute them on matched items and against VeriBench's corrected three-expert labels, and land a report with drafted paper sentences through a merged PR plus an email receipt.
