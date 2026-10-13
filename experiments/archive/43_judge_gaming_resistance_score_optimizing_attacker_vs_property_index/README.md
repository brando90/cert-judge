# Experiment 43: can an agent that optimizes a judge's score game it, and does the label-free property index predict which judges resist?

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/README.md>

**TLDR:** The paper discloses that resistance to gaming is untested (edit E6; catalog item 35.8 in `experiments/ideas/35_missing_experiments_from_reviews/EXPERIMENTS.md`). This is also the setting that matters most when a judge becomes a reward, for example in reinforcement learning (RL) on formal specifications. Here, an attacker model repeatedly edits a Lean candidate specification to raise one judge's score, seeing only that judge's score. The edits must elaborate in Lean and must leave the implementation unchanged. We measure how much the attacked judge's score rises compared with a held-out reference that the attacker never sees: the validated VeriBench coverage ensemble, whose test Spearman with the experts is 0.826, plus deterministic vacuity, duplicate and spam checks. Then we ask whether judges that rank higher on the label-free index are harder to game.

## Status

**DONE 09-30-2026** ([REPORT.md](REPORT.md), [results.md](results.md), contract [PROTOCOL.md](PROTOCOL.md) with Amendment 1).
- **Setup:** GPT-6 Luna (high) attacked Claude Sonnet 5 (medium) × {`BAD_STRINGY`, `D0`, `H0`, `H2`, `P1_BASELINE`, `P8_STRICT_B`} on 15 low-coverage items for 8 Lean-checked rounds: 90 cells, 720 attempts, 634 Lean-valid, 119 accepted. The reference was `H2` on Claude Opus 5.5 (max) + GPT-6 Sol (high), 3 repeats each.
- **Gaming gaps:** from −0.162 (`LEX`) to +0.033 (`H2`). No task-clustered 95% interval lies above 0.
- **Flags:** 59 of 62 edited final candidates added flagged statements (ground unit tests stated as theorems, statements that never mention the implementation), and the reference credited them too.
- **Index association:** experiment 39's selected `C_ms_gold` gave ρ = +0.600 (exact one-sided p = 0.912) and `TI_var_trainnorm` ρ = −0.086 (p = 0.460), both NOT SUPPORTED; `PTI_v0_frozen` is NOT_COMPUTABLE (3/6 configurations).
- **Charges:** $60.21 Vals-reported in total.

## Goal, uncertainty and decision

**Central uncertainty.** A screen that ranks judges by human agreement may still pass judges that an optimizer can exploit. If the property index predicts the gaming gap, that supports using it before a judge becomes a reward. If it does not, the paper must say that the screens do not cover this.

**Design (the worker fixes the details in `PROTOCOL.md` before any call).**
- **Attacked judges.** Six configurations from experiment 39's panel spanning its index range. Candidates by design: the lexical control `BAD_STRINGY`, the deployed VeriBench rubric `D0`, `H0`, the validated rubric `H2`, `P1_BASELINE` and `P8_STRICT_B`, on one or two judge models. If experiment 39's train/val index values exist at protocol time, choose by index quantile and record the choice.
- **Items.** 15 rated candidates whose expert-mean coverage is ≤ 0.6, drawn from experiment 39's criterion tasks, so there is room to rise. Labels are not used in the attack. They appear only in the final analysis, and experiment 39's sealed test rows are read only after its `TEST_RECEIPT.json` exists.
- **Attacker.** One pre-registered model sent through Valkyrie with a fixed optimization prompt (preferred: the same single-call transport experiment 39 uses). K = 8 iterations per (judge, item). At each step it gets the current candidate and the attacked judge's last score. Edits that fail Lean elaboration or change the implementation are rejected and still count as an iteration.
- **Reference, never shown to the attacker.** The validated ensemble from VeriBench experiment 100 (`H2` on Claude Opus 5.5 at max effort plus GPT-6 Sol at high effort, same transport), plus deterministic statement checks: `True` or trivially decidable conclusions, duplicate statements, and statement-count inflation.
- **Outcomes.**
  - Per judge: the gaming gap, defined as the attacked score gain minus the reference score gain, with task-clustered intervals, and the share of final candidates flagged by the deterministic checks.
  - Across judges: the Spearman association between the label-free index (experiment 39's selected index when available, and the paper's frozen `TI_var` and `PTI_v0` on these judges) and the gaming gap.
- **Pilot first.** 3 items × 2 judges × 4 iterations to check the Lean-validity rate, parse rate and cost per iteration. The full run follows automatically if the pilot's gates in `PROTOCOL.md` pass.

## Dependencies

- Experiment 39's pipeline, used read-only (transport, prompt rendering, Lean project and its environment fix). Judge and attacker calls start only after experiment 39's transport smoke has passed.
- Funding: Vals (Valkyrie), with no automatic spend cap. Vals-reported charges are recorded.

Runbook: [cc.md](cc.md). Live ledger: [results.md](results.md). Checkpoint: `CKPT_gaming_resistance.md` (written by the worker).

**TLDR-end:** [cj: e43-gaming] Done: no attacked judge configuration gained more than the validated reference credited, but the attacker test-stuffed most edited specifications and the reference credited them as well; the label-free index did not predict gaming resistance.
