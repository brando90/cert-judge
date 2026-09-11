# Folder 20 - PROTOCOL (LOCKED before any expensive run)

This file freezes the protocol before any LLM-budget-spending run begins. It is written PRIOR to seeing cross-agent results for this experiment. Any deviation observed during execution is documented in `results.md` under "Open questions for reviewer", not by silently editing this file after results are known.

## Scientific question (locked)

Can one fixed Lean theorem judge score VeriBench solutions from multiple SOTA agent CLIs such that judge scores align with human judgments for each agent row? Secondary question: after defining a non-constant agent-conditioned trust-index value, does that value predict judge-human alignment across agent rows?

Operational pass criterion: at least three agent CLI/model rows should report Pearson, Spearman, and Kendall correlations of approximately `>= 0.6` between fixed-judge scores and human scores. Treat this 3-row panel as a smoke result; for a TMLR-facing cross-agent trend claim, prefer at least five agent rows plus uncertainty estimates. The trust-index criterion is blocked until the experiment defines an agent-conditioned trust-index value; the existing per-judge `cert_index` / `cert_index_v2` is constant under one fixed judge and must not be correlated across agent rows.

## Locked metrics & thresholds

- Per-agent judge-human Pearson `r`: target `>= 0.6`
- Per-agent judge-human Spearman `rho`: target `>= 0.6`
- Per-agent judge-human Kendall `tau`: target `>= 0.6`
- Across-agent Pearson `r(agent_conditioned_trust_index, judge_human_alignment)`: blocked until definition exists; target `>= 0.6` once defined
- Across-agent Spearman `rho(agent_conditioned_trust_index, judge_human_alignment)`: blocked until definition exists; target `>= 0.6` once defined
- Across-agent Kendall `tau(agent_conditioned_trust_index, judge_human_alignment)`: blocked until definition exists; target `>= 0.6` once defined
- Minimum smoke panel: `3` agent rows (`codex`, `claude_code`, `vibe_leanstral`)
- Preferred paper-facing panel: `5` or more agent rows if optional agent outputs are available

## Locked analysis params

- Fixed judge must remain fixed across agent rows.
- Default fixed judge candidate: `labs-leanstral-2603|P1_BASELINE`.
- Prompt source: `experiments/02_reviewer_response_neurips_math_ai_2026/utils/sensitivity_sweep.py`.
- Repeats and aggregation should be recorded exactly. If using the existing Exp16 convention, use `judge-repeats=3` and `repeat-agg=median`.
- Agent model IDs must be observed from CLI logs/config/transcripts and stored in per-agent manifests.
- No per-agent judge prompt tuning is allowed.
- A per-agent grouping/join layer is required. `exp16_multi_judge_human_sets.py` emits pooled per-judge rows and Spearman-only human correlations, so it cannot directly produce the required per-agent Pearson/Spearman/Kendall table.
- Do not compute trust-index correlations across agent rows from the existing per-judge `cert_index` / `cert_index_v2` values.

## Scale verification (no further normalization)

Human labels may appear on `0`-`5`, `1`-`4`, or normalized `0`-`1` scales depending on the upstream file. Before computing correlations, record which input columns are used and whether they are normalized. Do not divide a column twice.

Judge scores from `P1_BASELINE` are already on `[0, 1]`.

## Verified data schema

Expected per-item result schema for the primary table:

- `agent_row`
- `agent_cli`
- `agent_cli_version`
- `requested_model`
- `observed_model`
- `task_id`
- `gold_file`
- `candidate_file`
- `human_score`
- `fixed_judge_score`
- `agent_conditioned_trust_index` or blank if no valid definition exists yet

Existing legacy schema references:

- `experiments/04_veribench_validation/run_veribench_validation.py` writes `human_judgments.csv`.
- `experiments/04_veribench_validation/exp16_multi_judge_human_sets.py` writes `detail_rows.csv`, `judge_rows.csv`, and `summary.json`.
- `judge_rows.csv` is pooled by judge, not split by agent row.

## Pre-conditions for run

- Veribench gold files exist at `data/veribench_dataset/lean_src/veribench/`.
- Generated agent outputs exist for each target agent row.
- Each agent row has a manifest with exact observed model ID.
- Human-label files are available under `experiments/human_labels/`, `experiments/ethan_hand_labels/`, or `experiments/04_veribench_validation/data/`.
- Before any direct API-key script is run, surface the script path, estimated call count/cost, model IDs, and output directories to Brando for explicit approval.

## Estimated wall-clock

- Offline manifest/table assembly: minutes.
- Fixed-judge scoring over cached rows: minutes if fully cached; otherwise potentially hours depending on model rate limits.
- New agent generation over VeriBench: unknown; must be estimated per agent CLI before launch.

## Pass/fail / abort rules

Smoke test passes if one task per agent row produces a manifest, a generated artifact, a fixed-judge score, and a joined human score.

Abort and document if:

- An agent row lacks an exact observed model ID.
- The fixed judge changes after test outputs are seen.
- Test labels are used to choose the fixed judge.
- The analysis tries to treat a per-judge cert index as a per-agent trust index.
- Correlations cannot be computed because the row count or score variance is too low.
- A script would spend LLM/API budget without explicit approval.

## Identity / contact crib (verified)

_(N/A for this handoff; no PR assignment or external contact is required.)_
