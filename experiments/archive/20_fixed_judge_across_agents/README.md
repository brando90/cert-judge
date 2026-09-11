# Fixed Judge Across VeriBench Agents
**TLDR:** Brando wants one frozen judge to work across as many VeriBench-solving agent CLIs as possible, with every row recording the exact agent CLI and model ID used to generate the Lean artifact. The primary sign-off table is per-agent judge-human agreement, with Pearson, Spearman, and Kendall targeted at approximately `>= 0.6`. A trust-index-vs-alignment table is desired, but it needs an explicit agent-conditioned trust-index definition because the existing cert index is per judge, not per agent.

## Goal

Generate a TMLR-ready table where each row is an agent CLI/model that solves VeriBench tasks, scored by the same fixed Lean theorem judge. The fixed judge should be chosen once, frozen, and then applied to all agent outputs without per-agent retuning. Brando can then use this folder to pick up the paper claim: a single certified judge generalizes across multiple SOTA agent families.

## What Brando Wants

The desired headline is:

> One fixed judge scores VeriBench solutions from several SOTA agent CLIs, and its scores agree with human judgments across agents. If an agent-conditioned trust-index definition is added, that value should also track human agreement across agent rows.

Operationally:

1. Rows are agent CLI/model runs, not prompt variants.
2. Each row must state the exact agent CLI, CLI version, requested model, and observed model ID used to generate the VeriBench solution.
3. The judge is fixed across rows: same judge model, same prompt, same scoring script, same repeat count, same aggregation.
4. For each agent row, fixed judge scores vs human scores should have Pearson, Spearman, and Kendall correlations around `>= 0.6`.
5. Across agent rows, trust-index values should only be correlated with judge-human alignment after defining a non-constant agent-conditioned trust index. The current `cert_index` / `cert_index_v2` values are per judge, so a single fixed judge makes them constant across agent rows.
6. More passing rows are better. Use 3 rows as a smoke panel, then expand to at least 5 before making a paper-facing cross-agent trend claim.

## Structure

```text
experiments/20_fixed_judge_across_agents/
|-- README.md
|-- PROTOCOL.md
|-- results.md
|-- writing.tex
`-- expt_v1/
    `-- cc.md
```

## Starting Agent Panel

Use this as the initial panel. Exact model IDs must be recorded at run time; do not rely on memory or marketing names.

| Agent row | CLI / system | Required model logging | Status |
| --- | --- | --- | --- |
| `codex` | Codex CLI | CLI version, requested GPT model, observed GPT model in transcript/config | TODO |
| `claude_code` | Claude Code | CLI version, requested Claude model, observed Claude model in transcript/config | TODO |
| `vibe_leanstral` | Mistral Vibe / LeanStral agent | CLI version, requested Mistral/LeanStral model, observed Mistral model ID | TODO |
| `gemini_cli` | Gemini CLI or comparable Google coding agent | CLI version, requested Gemini model, observed model ID | Optional |
| `qwen_agent` | Qwen/Coder agent or local coding stack | exact checkpoint/API model ID and serving backend | Optional |

Existing legacy generated-agent files use `agent0`, `agent1`, and `agent2` under `data/generated_agents/`, with `agent0 -> codex`, `agent1 -> claude`, `agent2 -> llama` in `experiments/04_veribench_validation/run_veribench_validation.py`. For this experiment, prefer an explicit manifest over implicit numeric names.

## Fixed Judge Candidate

Start with the current best simple fixed judge:

- Judge ID: `labs-leanstral-2603|P1_BASELINE`
- Prompt path: `experiments/02_reviewer_response_neurips_math_ai_2026/utils/sensitivity_sweep.py`
- Prompt key: `PROMPT_VARIANTS["P1_BASELINE"]`
- Cached-score source / starting scorer: `experiments/04_veribench_validation/exp16_multi_judge_human_sets.py`
- Runtime caller: `experiments/02_reviewer_response_neurips_math_ai_2026/utils/judge_caller.py`
- Existing cached source: `experiments/04_veribench_validation/results_exp16_leanstral_r3_median`

Important: `exp16_multi_judge_human_sets.py` emits one pooled row per judge and only computes Spearman in `judge_rows.csv`. This experiment still needs a per-agent grouping/join layer that parses candidate filenames or manifests, computes Pearson/Spearman/Kendall within each agent row, and writes the primary result table.

If a different fixed judge is selected, freeze it before reporting test numbers and update both `README.md` and `results.md` with the new prompt/model/code paths.

## Required Manifest

Each generated agent row should write a manifest next to its generated Lean files:

```json
{
  "agent_row": "codex",
  "agent_cli": "codex",
  "agent_cli_version": "TODO",
  "requested_model": "TODO",
  "observed_model": "TODO",
  "generation_command": "TODO",
  "repo_commit": "TODO",
  "veribench_split": "TODO",
  "output_dir": "TODO",
  "notes": "TODO"
}
```

The `observed_model` field is load-bearing. It must come from the CLI transcript/config/logs, not from a default assumption.

## Method

1. Generate or collect VeriBench Lean artifacts from each agent CLI/model row.
2. Record the agent manifest for every row, including exact observed model ID.
3. Run the same fixed judge over all agent outputs against the same gold references.
4. Join judge scores to human labels.
5. For each agent row, compute Pearson, Spearman, and Kendall between human scores and fixed-judge scores.
6. If Brando wants the trust-index trend, define and justify an agent-conditioned trust-index value before computing it. Do not reuse a constant per-judge cert index as a per-agent value.
7. Across rows, compute Pearson, Spearman, and Kendall between the agent-conditioned trust index and judge-human alignment only after step 6 is satisfied.
8. Promote the per-agent table only if the fixed judge clears approximately `0.6` on each target correlation, or document the failure honestly.

## Dependencies

- VeriBench gold Lean files: `data/veribench_dataset/lean_src/veribench/`
- Existing generated-agent baseline artifacts: `data/generated_agents/`
- Existing human labels: `experiments/human_labels/`, `experiments/ethan_hand_labels/`, and `experiments/04_veribench_validation/data/`
- Existing VeriBench validation loader/scorer: `experiments/04_veribench_validation/run_veribench_validation.py`
- Existing fixed-judge panel scorer: `experiments/04_veribench_validation/exp16_multi_judge_human_sets.py`
- Existing property/trust-index analysis scripts: `experiments/04_veribench_validation/exp28_variance_aware_trust_index.py`, `experiments/04_veribench_validation/exp30_specialist_judge_task_split.py`, `experiments/04_veribench_validation/exp40_train_test_calibration_sweep.py`, `experiments/04_veribench_validation/exp43_frozen_tivar_heldout.py`
- Existing prior-result references: `experiments/04_veribench_validation/results_exp39_autometrics_autoti/REPORT.md`, `experiments/04_veribench_validation/results_exp41_honest_train_test/HONEST_TABLE.md`, `experiments/04_veribench_validation/results_exp43_frozen_tivar_heldout/HELD_OUT_PAPER_TABLE.md`

## Status

| Step | Status | Notes |
| --- | --- | --- |
| Handoff goal captured | Done | See `results.md`. |
| Locked protocol drafted | Done | See `PROTOCOL.md`; update before any expensive run if Brando changes the contract. |
| Fixed judge candidate named | Done | Starts with `labs-leanstral-2603|P1_BASELINE`. |
| Agent panel defined | Done | Codex, Claude Code, Vibe/LeanStral first; optional Gemini/Qwen. |
| Exact agent model manifests | TODO | Must be generated with the agent outputs. |
| Cross-agent fixed-judge result table | TODO | Do not claim success until filled from real runs. |
| Per-agent grouping/join script | TODO | Needed because the legacy scorer emits pooled judge rows, not agent rows. |
| Trust-index correlation table | Blocked | Needs an agent-conditioned trust-index definition; current cert index is per judge. |
