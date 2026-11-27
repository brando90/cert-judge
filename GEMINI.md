# Gemini / Antigravity (Agy) — cert-judge

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/GEMINI.md>

**TLDR:** Work in a numbered experiment folder on `main`. Do not open a git branch. The rest of the project policy is `AGENTS.md` (same text as `CLAUDE.md`).

## Experiment folders on `main`

Prefer a numbered experiment folder on `main` over a separate git branch. This repository stays one `main` so Cursor, Claude Code, Gemini Antigravity (Agy), Codex, and collaborators see the same tree and build on each other's work. A new experiment is a new folder.

- Put each experiment in `experiments/NN_<setup_name>/`. Register it in `experiments/archive/layout.json` with its current task, and add its row to `experiments/README.md`. If two efforts pick the same number, keep the folder already on `main` and renumber the new folder to the next free number, updating its internal references.
- Commit and push straight to `main`. Fetch and fast-forward `main` before editing, so another agent's folder is already in your tree. Do not open a branch or a pull request for an experiment, a paper edit, or an agent session.
- Coordinate with the other agents on this repo. One writer per experiment folder. Read that folder's `README.md` and `CKPT_*.md` before changing it, and put your own run in the next free numbered folder. Name the agent and the date in the folder README (for this client, Gemini Antigravity / Agy). Cursor reads `AGENTS.md` and `.cursor/rules/experiment-folders-on-main.mdc`. Claude Code reads `CLAUDE.md`. All three state this same rule.
- When a leftover branch turns up, bring its unique files onto `main` and keep them. A branch that is a separate experiment becomes `experiments/NN_<setup_name>/`. A branch that is an interim paper draft becomes `paper_latex/interim_drafts/<date>_<name>/` and leaves the active manuscript `paper_latex/ICLR_2027_submission/` in place. Live experiment folders and the active manuscript stay as they are when the branch would move or rewrite them. After the files are on `origin/main`, delete the leftover branch. No force-push.
- Run deterministic checks before marking an experiment folder done or deleting a leftover branch: run `python3 py_src/cert_judge/experiment_layout.py --check`, verify file and byte parity of any files copied from a branch against the branch tip (confirming no retired experiment roots, secrets, or personal data are reintroduced), and run the affected experiment test suites before pushing to `origin/main`. Run a model-reviewer quality assurance (QA) pass when requested under `~/agents-config` Hard Rule 3.
- The 10-13-2026 framing draft is the worked example. It lives at `paper_latex/interim_drafts/framing_10-13-2026/` (copy of `paper/framing-10-13-2026` at `5ac4c03`, closed pull request 64). It is an interim draft. It is not the paper's claims, and it does not replace the active manuscript. The same branch also archived experiments 39, 41, 42 and 43; that move stays off `main` while those folders are still the live paths later experiments use.

## Also load

Read `AGENTS.md` before preparing ratings, judging Lean, choosing a model, or launching a run. It holds human-rating identity, the four judge-learning formulations, the label-free proxy versus the human-grounded criterion, the no-internet evaluation default, and the Vals spending pause.

Experiment 69A is `experiments/69_proxy_target_proper_score/` (read `experiments/69_proxy_target_proper_score/COORDINATION.md` before editing or starting a competing scorer) and Experiment 70 is `experiments/70_proper_scoring_proxy_target_alignment_and_selection_start_26Nov2026/`. `trustworthy-theorem-judges` `experiments/09_prepare_packets_and_collect_human_ratings_start_28Sep2026` owns the canonical ratings. Do not start a correlation-maximization sweep.
