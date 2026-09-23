# Prompt 01 — Collect every OpenReview complaint about the CertJudge paper into one ledger

**TLDR:** Make the agent find every OpenReview round this paper has been through (all titles, all venues), capture each review verbatim into `experiments/33_openreview_complaints_all_venues_to_iclr2027_paper/reviews/`, and extract one ledger row per complaint in `complaints_ledger.md` with a status against the current ICLR 2027 manuscript. Success: every venue found by the OpenReview search API has a review file (verbatim text or an explicitly empty skeleton plus a `fetch_attempts.md` log), and every complaint has an ID, a status, and an action. Deliverable: the folder above, committed and pushed to `main`. Load-bearing constraint: never fabricate or paraphrase-as-verbatim any review text; if a fetch fails, log it and leave a marked placeholder.

Follow `~/agents-config/INDEX_RULES.md` (Hard Rules 1, 4, 9, 10, 11; Trigger Rules 36, 37, 39, 57, 58).

## Context

Repository `/Users/brandomiranda/cert-judge`. The active manuscript is `paper_latex/ICLR_2027_submission/main.tex`, a reformatting of the accepted ICML 2026 DL4C paper. Known prior rounds and where their text already lives:

- NeurIPS 2025 MATH-AI, "Trusting the Formal Judge…", forum `9WAWDdwqpC`: `experiments/archive/02_neurips_reviews/or_neurips_2025_math_ai_workshop/or_reviews.md`.
- ICML 2026 AI4Math, "CertJudge…", forum `xmHP3UhGQ8`: `experiments/18_icml_2026_reviews/pre_prompt.md` (do not duplicate the analysis in `18_icml_2026_reviews/agent_prompt.md`; cross-reference it).
- ICML 2026 DL4C, "Certifying the Judge…", forum `gGR1gE7x3a`: not captured anywhere.
- TMLR 2026 desk reject, forum `WKVtlskjeQ`: `experiments/archive/21_tmlr_submission/`.

## Steps

1. Search OpenReview anonymously with the public API: `curl -s 'https://api2.openreview.net/notes/search?term=<title words>&source=forum&limit=20'` for each title variant ("CertJudge", "Certifying the Judge", "Trusting the Formal Judge", "Falsifiable Properties LLM judge Lean"). Record every forum id, venue tag, and submission number.
2. For each forum, try `https://api2.openreview.net/notes?forum=<id>`; expect `ChallengeRequiredError` (login wall) for reviews. Log each attempt (time, URL, method, outcome) in `reviews/fetch_attempts.md`.
3. Copy already-captured reviews verbatim into `reviews/<venue>_<forum>.md` with a provenance header (source path, capture date, decision, ratings).
4. For any forum whose reviews are unreachable, write a skeleton file with the reachable metadata and `[[PASTE …]]` placeholders; state in bold that it is empty.
5. Read the manuscript end to end (per-section files under `paper_latex/ICLR_2027_submission/`; `main.tex` is only the `\input` list). For each complaint, write one ledger row: ID (`<venue>-<reviewer>-<n>`), verbatim-anchored paraphrase, status (Addressed / Disclosed / Partial → E# / Deferred / Superseded / Unknown), evidence (`main.tex` line or artifact path), action.
6. Register the experiment in `experiments/archive/layout.json` (active) and `experiments/README.md`; run `python3 py_src/cert_judge/experiment_layout.py --check`.
7. Create `results.md` at launch with `**Status:** RUNNING`, update it as rows land, and close it with a `**TLDR-end:** [cj: or-complaints] …` line.
8. Commit with explicit paths (`git add experiments/33_…`), `git pull --rebase --autostash`, push to `main`.

## Guardrails

- No LLM-provider API calls, no scripts that read `~/keys/*`, no judge scoring: this is a documentation task.
- Do not edit `paper_latex/` in this prompt; paper edits belong to prompt 02.
- Other sessions edit the repo concurrently: stage only your own paths, rebase before pushing, never force-push.

TL;DR: Locates every OpenReview forum for this paper with the public search API, stores each review verbatim (or a logged, clearly empty skeleton), and produces `complaints_ledger.md` plus `results.md` in experiment 33; runs no model calls and touches no paper source.
