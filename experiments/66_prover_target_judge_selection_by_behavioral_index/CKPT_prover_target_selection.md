# Experiment 66 checkpoint: prover-target judge selection

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/66_prover_target_judge_selection_by_behavioral_index/CKPT_prover_target_selection.md>

**TLDR:** The retrospective conditions R1 and R2 are complete and published. The prospective condition P1 is prepared and waits for a validated fresh prover target, so nothing is running.

Created: 11-06-2026 15:26 PST
Last updated: 11-06-2026 15:26 PST

## State
- **Owner:** Claude Code (Opus 5.5) in Brando's Claude desktop chat "AI judge prover outcome prediction plan", working from Codex's handoff `trustworthy-theorem-judges/private/handoffs/cert-judge-prover-target-prompt-11-06-2026.md` (sha256 `ceb7723a…`).
- **Done:** protocol frozen at `e13b133`; R1 and R2 analyses; source audit; manifest; proposed paper appendix, which is not in the paper's `\input` list.
- **Running:** nothing. No watcher was created.
- **Blocked:** P1, which needs a frozen target with kernel replay. It will come from VeriBench experiment `169_natural_output_prover_fsc_validation_11-06-2026` (sandbox credits) or trustworthy-theorem-judges experiment `05_fresh_local_prover_target_judges` (Codex worker; not yet created).
- **Notifier:** this chat sends the results email; no other owner sends one for this experiment.

## Next commands
- Reproduce: `python3 experiments/66_prover_target_judge_selection_by_behavioral_index/scripts/analyze66_r1.py`, then `.../analyze66_r2.py`.
- When a target is released: follow [PROSPECTIVE_P1.md](PROSPECTIVE_P1.md) steps 1–5 on SNAP free GPUs.

## Brando to-do
- None required for R1/R2. Restoring the Valkyrie sandbox credits unblocks VeriBench experiment 169 and therefore P1.

## Log
- 11-06-2026 15:26 PST — R1 and R2 complete; P1 prepared and blocked; publishing.

**TLDR-end:** [cj: experiments/66_prover_target_judge_selection_by_behavioral_index checkpoint] Retrospective work is complete; P1 waits on a validated target.
