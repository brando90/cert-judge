# Interim paper draft, 10-13-2026 (closed pull request 64)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/paper_latex/interim_drafts/framing_10-13-2026/README.md>

**TLDR:** This folder is the interim, result-consistent framing draft from branch `paper/framing-10-13-2026` at `5ac4c032acc4aed937857e235fb97f2e1425a60d`. It is not the paper's claims. The active manuscript stays `paper_latex/ICLR_2027_submission/`.

Copied onto `main` on 11-26-2026 so every agent can read the draft without checking out a branch. The decision record, with every number, interval, denominator and source file, is `docs/PAPER_FRAMING_DECISION_10-13-2026.md`. The pull-request text is `docs/PR64_INTERIM_FRAMING_DRAFT_RECORD_11-11-2026.md`.

Brando, 10-13-2026: the plan of record is more human data, and the framing is his call after that round. Do not submit this draft, and do not copy it over the active manuscript.

## What was brought onto `main`

- The branch's `paper_latex/ICLR_2027_submission/` tree, including `999_appendix_validation_set_72_pairs.tex`, `figures/make_c_ms_gold_vs_criterion.py`, the two figure PDFs, and `main.pdf`.
- `CKPT_MASTER_branch_5ac4c03.md`, the master checkpoint as it stood on that branch. The live file `experiments/CKPT_MASTER_tmux1_cc_6043a46f.md` is unchanged.

## What was left as it stands on `main`

Commit `c9963c1` on the branch moved experiments 39, 41, 42 and 43 into `experiments/archive/` and retargeted readers in experiments 46 and 47 and in `experiments/ideas/35_missing_experiments_from_reviews/EXPERIMENTS.md`. Those four folders are still the live paths under `experiments/` (later experiments import them there), and `experiments/archive/layout.json` still lists them as active. That move is not applied. `docs/PAPER_FRAMING_DECISION_10-13-2026.md` was already on `main` and matches the branch copy.
