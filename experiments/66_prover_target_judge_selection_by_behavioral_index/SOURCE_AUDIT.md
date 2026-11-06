# Experiment 66 source audit: prover targets, judge caches and joins

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/66_prover_target_judge_selection_by_behavioral_index/SOURCE_AUDIT.md>

**TLDR:** R1's target is a fixed, deterministic Lean procedure on constructed probes; it is sound for theorem-level implications but constant within each probe family. R2's target covers natural outputs but comes from agent-written bridges without a trusted replay, and a second prover reorders the judges. No validated fresh target exists yet, so the prospective condition is prepared, not run.

Source commits read on 11-06-2026:
- cert-judge `main` `71023c1`; this experiment's protocol was frozen at `e13b133`.
- VeriBench `origin/main` `ec1f9b2a44`, read with `git show`; the local VeriBench working tree, which has another owner's uncommitted change, was not touched.
- trustworthy-theorem-judges `main` `a1d0231`.

Exact file hashes are in `results/r1_e42_target.json` (configuration and script hashes) and `results/r2_natural_target.json` (`source_sha256` for every VeriBench file read).

## R1 target: experiment 42's fixed reverse-implication procedure

| Requirement | Finding |
|---|---|
| Exact intended implication | Per changed theorem, `(∀ binders, probe statement) → (∀ binders, reference statement)`, built by `scripts/semantic_probes.py` (`959ada93…`) from the probe and reference texts; identity and formatting probes need no implication because `#print` shows identical declarations |
| Interface transport | Probes edit only theorem statements and `Prop` definitions and may not add, remove or rename declarations, so the interface is the reference's own; no adapter |
| Candidate-premise consistency | Over-constraint probes carry a hypothesis proved unsatisfiable; they are rightly not covered (`Y = 0`), since a vacuous statement cannot carry the reference's content |
| Forbidden axioms, `sorryAx` | Every forward check is proved without `sorryAx`; data-valued implementations are axioms of the same signature in the check file, which is the abstraction the target intends |
| Wrong goals, reference-proof leakage | The goal is generated from the reference statement text; reference proofs are `sorry` in the check file and cannot discharge it |
| Forged success receipts | The outcome is the compiler status parsed per check block in the probe build, not a model-written claim |
| Determinism and budget | Fixed `auto_tactic`, a fixed Lean 4.22 + Mathlib project and a 900-second timeout; no search randomness |
| Selection effect | Probes whose every reverse implication was proved were excluded as equivalent before judging (10 vacuity probes), so on the scored set `Y_P` equals 1 exactly for identity and formatting probes |
| Theorem level versus file level | 31 of 57 weakenings and 16 of 37 over-constraints are redundant at the file level by the pre-call audit (another unchanged theorem restates what was dropped); the theorem-level procedure still scores them 0. The file-level audit target is reported as a secondary reading |

## R2 target: historical Lean entailment acceptance on natural outputs

- **Join.** All 99 candidate files of VeriBench experiment 106 v5 groups G01 and G02 match a prover-tested solver file by exact sha256 (Tiny-256 manifest of experiment 138; Core-614 manifests of experiments 144, 147, 150, 151). 0 artifacts have more than one source, and 4 have no prover row (two tasks per solver), so they are missing rather than 0.
- **Gold.** Experiment 106 pins each reference's sha256. Its gold files differ from the prover-era files only by a comment-removal commit, per the inventory in this experiment's working notes, so the statements are equal.
- **Procedure.** Helper agents wrote one bridge per run with at most two repair rounds. The bridge makes the solver's theorems hypotheses over abstract functions and transports each gold theorem through an adapter. Checks: Lean 4.22.0 with Mathlib, `#print axioms` limited to the three standard axioms, no `sorry`/`native_decide` in the bridge, gold unedited, and a non-vacuity witness from the solver's real definitions.
- **Integrity gaps.**
  - Statement transport is checked by theorem name, not structurally.
  - Adapter faithfulness is a reading.
  - The Core-614 bridges (59 of the 95 outcomes) have no trusted kernel replay.
  - VeriBench experiment `168_harsh_prover_pd_pf_detection_controls_tiny256_11-04-2026` found that the names-and-axioms gate accepted 155 of 212 constructed invalid bridges and that a forged-audit weakness applied to this pipeline.
  - A pass is therefore operational acceptance, not verified semantic coverage. A fail is "not proved".
- **Prover dependence.** On the 36 Tiny-256 artifacts, the Gemini prover of experiment 158 passes 11 and disagrees with the main prover on 15.
- **Budget.** Bridge authoring had no fixed token or time budget. One retry conversion (experiment 150 `S077`) is scored 0 as first-pass.
- **Judges.** 32 committed configurations; 26 meet the 90% coverage rule. The Grok and Qwen P2/P3 frames have most cells only in recovery runs, which are excluded as a separate condition.

## Why historical acceptance is not admitted as a validated fresh target

The prompt's requirement and VeriBench experiment `169_natural_output_prover_fsc_validation_11-06-2026` both demand structural transport, kernel replay and an independent non-vacuity certificate before a natural-output outcome is treated as validated. Experiment 169 has built that checker (kernel replay of 94 archived control proofs, rejection of two audit bypasses) but has 0 measured natural outcomes. R2 therefore stays a retrospective, historical-target condition.

## Prior exposure checked

- Experiment 42 `REPORT.md` reports these judges' directional accuracies and their association with the human criterion; no prover Brier criterion and no index–prover association.
- Trustworthy-theorem-judges experiments 03 and 04 fitted the H2 recipe's aggregate rating against the R2 outcomes, so the frozen H2 configurations are exposed. No other R2 configuration was compared with prover outcomes before this experiment.

**TLDR-end:** [cj: experiments/66_prover_target_judge_selection_by_behavioral_index source audit] R1's fixed Lean procedure is trustworthy at the theorem level but family-determined. R2's natural-output target is historical and prover-dependent. A validated fresh target is still missing.
