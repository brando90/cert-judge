# Experiment 66: does the behavioral index select judges that agree with a fixed formal prover?

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/66_prover_target_judge_selection_by_behavioral_index/README.md>

**TLDR:** This is a two-level, zero-call retrospective study.
- **Constructed probes:** on 194 probes checked by experiment 42's fixed Lean procedure, cert-judge's label-free index `C_ms_gold` tracks per-judge prover agreement across the 16 held-out language-model judge configurations: Spearman 0.705 [0.593, 0.880], one-sided permutation p 0.0016. Index selection lands within 0.0025 of the best configuration. Deterministic theorem-count controls nonetheless reach the maximal index with only constant-level agreement.
- **Natural outputs:** on 99 natural solver outputs with historical Lean entailment outcomes, the index cannot be tested across judges, a consensus signal fails to select, and the two available provers rank judges differently.

**Status, 11-06-2026:** retrospective conditions R1 and R2 done; prospective condition P1 prepared and blocked on a validated fresh prover target. 0 model calls, $0.

| File | What |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | Frozen before analysis at commit `e13b133`: estimands, conditions, splits, property review, predictions |
| [RESULTS_prover_target_selection.md](RESULTS_prover_target_selection.md) | Results, deviations, predictions versus observations |
| [SOURCE_AUDIT.md](SOURCE_AUDIT.md) | Target integrity audit, joins, prior exposure |
| [PROSPECTIVE_P1.md](PROSPECTIVE_P1.md) | Prepared local open-weight run and its blocking condition |
| [MANIFEST.json](MANIFEST.json) | Inputs, revisions and hashes |
| [config_r1.json](config_r1.json), [config_r2.json](config_r2.json) | Frozen configurations |
| [scripts/](scripts/) | `analyze66_r1.py` (constructed target, two levels), `analyze66_r2.py` (natural target) |
| [results/](results/) | `r1_e42_target.json`, `r2_natural_target.json` (aggregate and per-configuration; no task-level rows) |
| [paper_addition/](paper_addition/) | Proposed appendix fragment and a scratch-built PDF with it included; not in the paper's `\input` list |
| [prompts/README.md](prompts/README.md) | Prompt provenance (no new prompts) |
| [results.md](results.md), [CKPT_prover_target_selection.md](CKPT_prover_target_selection.md) | Ledger and checkpoint |

Reproduce from the repository root on a checkout with `~/veribench` at `ec1f9b2a44` or later:

```bash
python3 experiments/66_prover_target_judge_selection_by_behavioral_index/scripts/analyze66_r1.py
python3 experiments/66_prover_target_judge_selection_by_behavioral_index/scripts/analyze66_r2.py
```

Both scripts use only the Python standard library plus experiment 39's pure-Python `analysis_lib.py`; R1 takes about 7 minutes and R2 about 30 seconds on a laptop.

**TLDR-end:** [cj: experiments/66_prover_target_judge_selection_by_behavioral_index] On a constructed fixed-procedure target, `C_ms_gold` selects prover-agreeing judges within a language-model pool (Spearman 0.705, regret 0.0025) but is fooled by deterministic controls. On natural outputs the index could not be tested and the prover choice reorders judges, so a validated fresh target remains the next step.
