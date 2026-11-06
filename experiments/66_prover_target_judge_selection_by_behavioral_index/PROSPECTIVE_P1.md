# Experiment 66 prospective condition P1: open-weight judges on a validated fresh prover target

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/66_prover_target_judge_selection_by_behavioral_index/PROSPECTIVE_P1.md>

**TLDR:** P1 is prepared but not run, because no validated fresh prover target exists yet. When one is released, it scores the target's artifacts with the frozen experiment 58 open-weight judge panel on SNAP at $0 API cost, then reruns this experiment's two-level analysis unchanged.

## Blocking condition (verified 11-06-2026)

- VeriBench `169_natural_output_prover_fsc_validation_11-06-2026`, VeriBench `origin/main` `ec1f9b2a44`: stopped. 14/100 statement-only contexts emitted, 0 measured prover outcomes, Daytona sandbox credits depleted. Its owner and $500 cap are unchanged.
- Trustworthy-theorem-judges `05_fresh_local_prover_target_judges` (Codex worker's lane): absent at that repository's `a1d0231`.
- Historical experiment 145 or Core-614 acceptance is not a validated substitute: agent-written bridges, statement correspondence by name, and no trusted kernel replay for the Core-614 bridges.

## Admission rule for a target

Use the first released target that has all of these:
- exact goal construction with structural statement transport;
- a non-vacuity certificate;
- trusted kernel replay with standard axioms only;
- positive, negative and adversarial controls passed;
- a frozen prover identity, budget and retry rule;
- outcomes sealed from the judge side until the judges are fixed.

Its artifacts must share no task family with experiments 39 and 42, so the frozen `C_ms_gold` values and the new criterion share no task.

## Execution once admitted

1. Render the target's artifacts into the experiment 58 prompt set (9 prompts) with `experiments/58_open_weight_judges_on_e39_e42_probes/scripts/rebuild_prompts.py` conventions, recording every prompt sha256.
2. Run the 13 pinned open-weight models with `scripts/judge_vllm.py` under `slurm/run_model.sbatch` (FarmShare, or skampere1/mercury free GPUs), 3 repeats, the experiment 58 sampling and seeds. Estimate GPU hours with `slurm/estimate_gpu_hours.py` before launch and record the host.
3. Keep every cell, including parse errors and timeouts, in the full denominator.
4. Freeze the judge harvests by hash, then unseal outcomes and run `scripts/analyze66_r1.py` logic with the new target: index = experiment 58's committed `C_ms_gold` per configuration; criterion = `G_P` with the map fitted on the target's training families; association and selection on the held-out judge models.
5. Send `[RUN START]` and `[RUN DONE]` emails and keep `results.md` live.

No paid inference is part of P1. A frontier-judge extension would need Brando's named per-run cap under the Vals pause.

**TLDR-end:** [cj: experiments/66_prover_target_judge_selection_by_behavioral_index P1] Prepared local prospective run, blocked until a validated fresh prover target is released.
