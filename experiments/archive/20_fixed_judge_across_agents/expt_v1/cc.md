# Expt V1 Fixed Judge Across Agents
**TLDR:** Generate a TMLR-ready cross-agent table for one frozen VeriBench judge. Use one fixed judge across Codex, Claude Code, and Mistral Vibe/LeanStral agent outputs first, record exact observed agent model IDs, and report Pearson/Spearman/Kendall for judge-human agreement per agent. Do not claim trust-index-to-alignment correlations until you define a non-constant agent-conditioned trust index; do not claim success unless real results clear approximately `0.6` on the requested correlation metrics.

Follow `~/agents-config/INDEX_RULES.md` before running anything.

## Objective

Create the result Brando wants for `experiments/20_fixed_judge_across_agents/`:

- One frozen judge across multiple agent CLI/model rows.
- Rows are agent CLI/model runs that solve VeriBench tasks.
- Every row records the exact observed model used by the agent CLI.
- Per row, compute fixed-judge score vs human score correlations: Pearson, Spearman, Kendall.
- Secondary: define an agent-conditioned trust index, then compute trust-index vs judge-human-alignment correlations across rows. Do not reuse a constant per-judge cert index as a per-agent value.
- Target: approximately `>= 0.6` for each correlation type.

## Fixed Judge

Default frozen candidate:

- Judge ID: `labs-leanstral-2603|P1_BASELINE`
- Prompt path: `experiments/02_reviewer_response_neurips_math_ai_2026/utils/sensitivity_sweep.py`
- Prompt key: `PROMPT_VARIANTS["P1_BASELINE"]`
- Cached-score source / starting scorer: `experiments/04_veribench_validation/exp16_multi_judge_human_sets.py`
- Runtime caller: `experiments/02_reviewer_response_neurips_math_ai_2026/utils/judge_caller.py`

Important: the legacy scorer emits pooled rows per judge and Spearman-only human correlations. Add a per-agent grouping/join layer that uses manifests or candidate filenames, joins human labels, and computes Pearson/Spearman/Kendall for each agent row.

If you change the judge, freeze the replacement before final evaluation and update both `README.md` and `results.md`.

## Agent Rows

Start with:

1. `codex`: Codex CLI + exact observed GPT model.
2. `claude_code`: Claude Code + exact observed Claude model.
3. `vibe_leanstral`: Mistral Vibe / LeanStral CLI + exact observed Mistral model.

Optional expansion:

4. `gemini_cli`: Gemini CLI + exact observed Gemini model.
5. `qwen_agent`: Qwen/Coder stack + exact checkpoint/API model ID.

## Required Manifest Per Agent

Write a manifest per agent output directory:

```json
{
  "agent_row": "TODO",
  "agent_cli": "TODO",
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

The `observed_model` must be taken from CLI logs/config/transcripts.

## Deliverables

Update:

- `experiments/20_fixed_judge_across_agents/results.md`
- `experiments/20_fixed_judge_across_agents/README.md` if the fixed judge, agent panel, or source paths change.

The final `results.md` must include:

- Primary per-agent table with Pearson/Spearman/Kendall.
- Trust-index cross-agent table with Pearson/Spearman/Kendall only after defining an agent-conditioned trust-index value.
- Exact paths to prompts, code, manifests, generated artifacts, and result CSVs/JSONs.
- A clear pass/fail line for the `>= 0.6` target.

## Guardrails

- Do not run direct LLM-provider API calls silently. If a script loads API keys or would spend LLM budget, surface the script path, estimated cost, and exact experiments before running.
- Do not use test labels to select the fixed judge.
- Do not tune the judge per agent.
- Do not compute cross-agent trust-index correlations from the existing per-judge `cert_index` / `cert_index_v2`; that is constant for one fixed judge.
- Do not report oracle/per-task calibrated results as held-out generalization.
- If the result fails, write the failure clearly.
