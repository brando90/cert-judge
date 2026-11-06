# Experiment 66 prompts

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/66_prover_target_judge_selection_by_behavioral_index/prompts/README.md>

**TLDR:** R1 and R2 made no new model calls, so this experiment adds no prompt. Their judge prompts are the ones already committed by the experiments that produced the cached scores; P1 will reuse the experiment 58 prompt set.

- **R1:** experiment 39's nine judge prompts (D0, R4, H0, H1, H2, P1, P4, P8, LEX) as rendered by `experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges`. Per-cell `prompt_sha256` values are in its `results/harvest/*.json`.
- **R2:** VeriBench experiment 106 v5's H2 and H0 judge prompts and simulated-rater frames P1, P2, P3 and C0. Per-cell `prompt_sha256` values are in its `expt_v5/runs/*/cells.jsonl`.
- **P1 (prepared):** experiment 58's nine prompts, rebuilt by `experiments/58_open_weight_judges_on_e39_e42_probes/scripts/rebuild_prompts.py` conventions for the admitted target's artifacts. Each rendered prompt's sha256 is recorded before any call.

**TLDR-end:** [cj: experiments/66_prover_target_judge_selection_by_behavioral_index prompts] No new prompts; cached-score sources and P1's reuse are listed with their hash locations.
