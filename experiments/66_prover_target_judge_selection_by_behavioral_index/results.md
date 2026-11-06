# Experiment 66 results ledger

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/66_prover_target_judge_selection_by_behavioral_index/results.md>

**Status:** R1 DONE; R2 DONE; P1 PREPARED, BLOCKED on a validated fresh prover target.
**Last updated:** 11-06-2026 15:26 PST

| Condition | State | Result |
|---|---|---|
| R1: experiment 42's fixed Lean procedure, 194 probes, 56 configurations + 4 controls | DONE 11-06-2026 | Test pool `C_ms_gold` vs `G_P`: Spearman 0.705 [0.593, 0.880], permutation p 0.0016, 16 configurations / 4 models; selection regret 0.0025 (pick 0.904, random 0.859, fixed H2 0.876, constant 0.782). Post hoc: rubric prompts only 0.170 [−0.327, 0.842]; with controls the index picks the theorem-count control (regret 0.129) |
| R2: 99 natural VeriBench experiment 106 v5 outputs, historical Lean outcomes, 32 configurations | DONE 11-06-2026 | 26 computable configurations, `G_P` 0.752–0.819 versus constant 0.743; consensus signal −0.213 (p 0.85); index testable on 4 configurations only; judge rankings unrelated across two provers (Spearman −0.126 on 36 shared outputs) |
| P1: open-weight panel on a validated fresh target | BLOCKED | VeriBench experiment 169 stopped with 0 measured outcomes; trustworthy-theorem-judges experiment 05 not yet created. See [PROSPECTIVE_P1.md](PROSPECTIVE_P1.md) |

Run receipts:
- Protocol commit `e13b133`.
- R1: `python3 .../scripts/analyze66_r1.py`, about 7 minutes.
- R2: `python3 .../scripts/analyze66_r2.py`, about 30 seconds, VeriBench `ec1f9b2a44`.
- Both ran on Brando's Mac as cached-data analyses with 0 model calls, $0.
- One code fix to R1's rank-criterion bootstrap was rerun; see the deviations in [the results report](RESULTS_prover_target_selection.md).

**TLDR-end:** [cj: experiments/66_prover_target_judge_selection_by_behavioral_index] Both retrospective conditions are done; the prospective run waits for a validated fresh prover target.
