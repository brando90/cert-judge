# 32_veribench_ranking_certified_judge — runbook

**Goal (Brando, 2026-09-22, "option 3"):** re-score the VeriBench downstream agent-ranking table
(`paper_latex/ICLR_2027_submission/main.tex` §5.4, `tab:theorem_quality_table_split`: Baseline 0.470,
DSPy ReAct 0.615, Trace+ , Trace++ 0.588 — currently produced by an *uncertified* Claude 3.7 judge) with a
**certified judge configuration** from §5.3, so the paper can say the same property-checked judge ranks the agents.
Reviewer DeJF (ICML, `experiments/18_icml_reviews/pre_prompt.md:175`) flagged the uncertified judge.

## Hard constraints (non-negotiable)
- **CLI-only inference (Hard Rule 9).** Use `codex exec` (subscription) or `claude -p` (subscription). Never author or run
  code that calls `openai`/`anthropic`/`litellm`/raw provider HTTP; never load `~/keys/*`. Scrub `*_API_KEY` from every
  subprocess env (`OPENAI_API_KEY` is exported in the login shell). If the only path forward needs an API key: STOP,
  write the blocker in CKPT.md, and report.
- Quote first: before the first inference call, write the exact call count (items × agents × repeats) and the
  CLI/model to `CKPT.md`. Brando pre-approved subscription-CLI runs ("go!"); he did not approve API spend.
- Record the exact model ID the CLI actually used (from the CLI's own output/log) in every results file.
- Do not edit `paper_latex/**`. Do not run `latexmk` in `paper_latex/ICLR_2027_submission` (another session builds there).
- Commit + push only your own paths (`experiments/32_*`, `experiments/archive/layout.json`, `experiments/README.md`),
  explicit `git add <path>`, never `git add -A`, `git pull --rebase` only if `git status` shows no other dirty tracked
  files; never force-push. Other sessions are editing this repo concurrently.
- Never fabricate. If an input artifact cannot be found, write `fetch_attempts.md` with every attempt and stop.

## Facts already established
- Certified configurations (exp16, `experiments/archive/04_veribench_validation/results_exp16_final_robust_r9_median/summary.json`,
  `judge_rows[].judge_id`): `gpt-5.3-codex|P8_STRICT_B`, `gpt-5.3-codex|P4_CHECKLIST`, `gpt-5.3-codex|P1_BASELINE`,
  `gpt-5.3-codex|BAD_STRINGY` (control), `gpt-4o-mini|P8_STRICT_B`, `gpt-4o-mini|P4_CHECKLIST`, `editdist_e1`, `random_r1`.
  Pick the certified configuration with the highest TI_var among the primaries (read the TI_var field in that summary and
  in `paper_latex/ICLR_2027_submission/main.tex` §5.3 tables); record why.
- Prompt templates: `main.tex` appendix `\label{app:judge-prompts}` and `experiments/archive/04_veribench_validation/exp16_multi_judge_human_sets.py`
  (`JudgeSpec(judge_id, kind, model, prompt_name)`, line ~176; prompt bodies live in that script or `py_src/cert_judge/`).
  The exp16 script is API-based — read it for the prompt/scoring/aggregation contract, do NOT execute it.
- A subscription-CLI judge runner already exists from Experiment 29 (`experiments/archive/29_proxy_validation/`, "774 CLI tasks",
  memory note: runners must scrub `*_API_KEY`). Reuse it or its pattern.
- CLIs on this Mac: `/usr/local/bin/codex` (codex-cli 0.155.1), `~/.local/bin/claude`; `clauded` = `claude --dangerously-skip-permissions`.
  Check `codex exec -m gpt-5.3-codex` availability first; if the exact certified model is gone, see Fallback.
- Inputs to score: the four agents' generated Lean specifications behind `tab:theorem_quality_table_split`. They are NOT
  obviously in cert-judge (`data/generated_agents/` holds `<idx>_<problem>__agent{0,1,2}.lean`, three agents). Look in
  `~/veribench` (results dirs for baseline / DSPy ReAct / Trace+ / Trace++ on the theorem-quality split) and in the
  VeriBench paper's artifact list (`\citet{miranda2026veribench}`). Confirm the split names in the table header
  (Easy, HumanEval, Security, RealCode, …) match what you find. If not found locally: `fetch_attempts.md`, stop, report.
- Gold references: resolved by the frozen precedence policy (see `CLAUDE.md` "PTI-v0 Data Layout").

## Steps
1. Register the experiment: add `"32_veribench_ranking_certified_judge": "<current task>"` to `experiments/archive/layout.json`
   `active`, add a row to `experiments/README.md`; run `python3 py_src/cert_judge/experiment_layout.py --check`
   (pre-existing failures for `18_icml_reviews`/`20` are Brando's uncommitted moves — ignore those two).
2. Locate inputs (agents' specs + golds), write the manifest `inputs_manifest.json` (item, agent, path, sha256, split).
3. Choose the certified judge config; write `judge_config.json` (model, prompt_name, n_repeats=3 like §5.3, aggregation).
4. Write `CKPT.md` with the call quote; then run via CLI with parallelism ≤8, caching every raw response to
   `results/raw/<item>__<agent>__r<k>.json`, resumable.
5. Aggregate: per-agent normalized score per split and overall, same normalization as the table (score/10, mean over
   repeats and items). Write `results/ranking.json` + `results/ranking_table.md` with 95% bootstrap CIs over items.
6. Compare with the Claude 3.7 table: same ordering? Write `REPORT.md` (TLDR, method, exact model ID, counts, table,
   ordering agreement, caveats). Draft the 1–2 sentence §5.4 replacement and a candidate abstract line — as text in
   REPORT.md only; do not edit the paper.
7. Commit + push results progressively (every ~20 min or every completed agent), own paths only.

## Fallback if `gpt-5.3-codex` is unavailable in the CLI
Use the closest available Codex model (record the exact ID), and ALSO run the four property checks (P1 identity,
P2 bug ladder, P3 missing-spec ladder, P4 stability) for that substitute so it becomes a certified configuration in
its own right — that is the paper's protocol. Reuse the exp16/exp29 ladder construction (`py_src/cert_judge/probe_validation.py`,
`hsj_scoring.py`); quote the extra calls in CKPT.md before running. If the budget is too large for ~2 h, do the ranking
first, then the property suite, checkpointing so another agent can resume.

## Reporting
Final report = `REPORT.md` + the git SHAs pushed. Keep `CKPT.md` current so any agent (`clauded`, `codex`) can resume.
