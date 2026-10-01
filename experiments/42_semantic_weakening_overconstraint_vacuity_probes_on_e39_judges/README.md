# Experiment 42: do judges catch vacuous, weakened, or over-constrained formal specifications? Lean-validated semantic probes scored by experiment 39's judges

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/README.md>

**TLDR:** Reviewers at three venues asked whether a judge notices a formal specification that looks right but guarantees less: theorem statements replaced by `True`, a dropped conjunct or loosened bound, or a hypothesis that makes the theorem vacuous (review rows A26-c7ev-5, c7ev-11, c7ev-12 and N25-ivJs-1; catalog items 35.4 and 35.6 in `experiments/ideas/35_missing_experiments_from_reviews/EXPERIMENTS.md`). Experiment 39's probes cover deletion, blank candidates, spam, `sorry`, renaming, reordering and implementation bugs, but none of these semantic edits. This experiment builds such probes from the 25 VeriBench references, validates every one in Lean, and scores them with experiment 39's judge panel through Valkyrie. The question is which judges move in the required direction, and whether these components add to a label-free index's agreement with the expert criterion.

## Goal, uncertainty and decision

**Central uncertainty.** A coverage judge is most useful exactly where it must separate a correct specification from a subtly weaker one. If judges that score well on human agreement still reward weakened specifications, the paper's property set is missing the failure that matters most; if the property index already predicts this, the paper can say so with numbers.

**Probe families (expected direction fixed by construction).** Built from the annotation-era references (`veribench/experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/references/`):
- **Vacuity:** each theorem statement replaced by `True`, plus a variant that keeps the hypotheses and makes the conclusion trivially true. The score must drop.
- **Weakening** (up to 3 cumulative levels): drop a conjunct, relax `=` to `≤`/`≥` where meaningful, or add a disjunctive escape. Each level must come with a Lean proof that the original statement implies the weakened one; the reverse implication is recorded as disproved (counterexample), unproved, or proved. Proved-equivalent edits are excluded. The score must not increase with level and must fall below the reference.
- **Over-constraint** (up to 2 levels): add an unsatisfiable or strictly stronger hypothesis (for example `h : n < 0` over `Nat`), with the vacuity or strengthening shown in Lean. The score must drop.
- **Formatting only:** whitespace, comment and layout edits that elaborate to the same declarations. The score must stay the same.

Validity is decided only by Lean, fail-closed, following `py_src/cert_judge/probe_validation.py`. A model may propose candidate edits (subscription CLI or Valkyrie), but an edit enters the probe set only after the Lean checks pass.

**Pre-registration.** Before any judge call, the worker commits `PROTOCOL.md`. It fixes the probe counts, the judge configurations (all of experiment 39's 56 LLM configurations plus its 4 controls, unless reuse of its rendered prompt families is impossible, in which case a stated subset), 3 repeats per cell, per-judge metrics, and the decision rule:
- **Per-judge metrics:** directional accuracy against the identity score, Kendall τ with weakening level, and the formatting invariance gap.
- **Decision rule:** a judge *passes* the semantic screen if its directional accuracy is ≥ 0.8 on vacuity, weakening and over-constraint and its formatting gap is ≤ 0.05.
- **Index analysis:** the association of these components with experiment 39's criterion is computed on experiment 39's train and val judge units only. Experiment 39's sealed test rows are read only after its `results/TEST_RECEIPT.json` exists, and that analysis is labelled post hoc.

## Dependencies

- Experiment 39's pipeline, used read-only by import from your own clone: Valkyrie transport through experiment 103's `vb103_judge` agent, prompt rendering, the Lean project, and its fix for the missing `VeriBench` module. Judge calls start only after experiment 39's `results.md` shows that its transport smoke passed.
- Funding: Vals (Valkyrie), with no automatic spend cap (repository `CLAUDE.md`). Vals-reported charges are recorded.

**Status:** DONE 09-30-2026. Report: [REPORT.md](REPORT.md); 15 of 56 judge configurations pass the semantic screen; weakening directional accuracy has Spearman 0.73 with experiment 39's criterion on its train and val units (0.72 on test, post hoc).

Runbook: [cc.md](cc.md). Live ledger: [results.md](results.md). Checkpoint: `CKPT_semantic_probes.md` (written by the worker).

**TLDR-end:** [cj: e42-semantic-probes] Planned: Lean-validated vacuity, weakening, over-constraint and formatting probes, scored by experiment 39's judges through Valkyrie, to test whether judges catch specifications that look right but guarantee less.
