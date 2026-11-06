# Experiment 66 protocol: does the behavioral index select judges that agree with a fixed formal prover?

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/66_prover_target_judge_selection_by_behavioral_index/PROTOCOL.md>

**TLDR:** Two retrospective zero-call conditions and one prepared prospective condition. They test whether cert-judge's label-free behavioral index predicts each judge configuration's agreement with a fixed proving procedure, and whether choosing a judge by the index gives low prover-outcome error. Committed 11-06-2026 with the scripts and configurations, before any association, criterion or selection result of this experiment was computed.

## Question and the two levels

Brando's request (11-06-2026, relayed by Codex): test whether the behavioral index predicts per-judge agreement with a frozen AI-assisted formal prover and selects judges with low prover-outcome prediction error. This experiment keeps that operational target separate from the human-grounded `TI_m`, frozen `PTI_v0`, legacy `TI_var` and experiment 39's `C_ms_gold`.

- **Artifact** `z = (x, y_pred, y_gold)`: original Python, candidate formal specifications (unproved theorem statements in the candidate file) and gold-reference specifications, identified by file hashes.
- **Target** `Y_P(z)`: the recorded binary outcome of a fixed proving procedure `P` with its budget. A checked success establishes the implication. A failure is an operational 0, not proof of non-coverage. An infrastructure failure is missing, never 0.
- **Level 1 (artifact):** for configuration `theta` with probability `q_theta(z)`, `L_P(theta) = mean_z (q_theta(z) - Y_P(z))^2` and `G_P(theta) = 1 - L_P(theta)`. Normalized 0–1 judge scores are not elicited probabilities. The primary condition fits a logistic map from score to probability on training tasks only; the raw score is a separately named condition. The rank-agreement criterion (area under the receiver operating characteristic curve and Spearman between score and outcome) is reported as a separately named analysis.
- **Level 2 (judge):** across configurations, the association of a frozen label-free index with `G_P`, then selection: the `G_P` of the index-selected configuration, its regret against the pool's best (a diagnostic), and fixed-rubric, random and constant-judge baselines. A good single judge or a pooled artifact correlation does not answer this level.

## Conditions

### R1: experiment 42's fixed Lean reverse-implication procedure (constructed probes; primary two-level test)

- **Artifacts:** the 194 Lean-valid probes of `42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges` (manifest sha256 `aded29b8…`). Candidate = probe file, gold = annotation-era reference, built from 24 VeriBench references.
- **Procedure `P_E42`:** `scripts/semantic_probes.py` (sha256 `959ada93…`), Lean 4.22 with Mathlib, data-valued implementations replaced by axioms of the same signature. Its fixed `auto_tactic` automation attempts each changed theorem's reverse implication (probe statement implies reference statement). `Y = 1` for identity and formatting probes, whose coverage is certified by identical elaborated declarations. `Y = 0` for weakening, over-constraint and vacuity probes, whose reverse implication was not proved. Probes whose every reverse implication was proved were excluded as equivalent before any judge saw them, so on this set `Y_P` is constant within each probe family. This is a theorem-level target on constructed edits, not a file-level natural-output target.
- **Secondary target:** the pre-call file-level audit labels (`probe_edits/audit/`): a redundant weakening or over-constraint counts as covered, strict as not covered, unclear as missing. These are readings by Claude auditors, not prover outcomes.
- **Judges:** the 56 LLM configurations and 4 deterministic controls in experiment 42's committed harvests (3 repeats, median), with experiment 39's judge-model split (train: GPT-6 Sol, Claude Sonnet 5; validation: GPT-6 Luna, Gemini 3.1, Terminus 2 Luna; test: Claude Opus 5.5, Qwen3.6, Terminus 2 Sonnet 5, Terminus 2 Qwen). Judge family is the judge model.
- **Task split:** experiment 75's task split from `items.jsonl` (`ad9ed552…`). The score map is fitted on train-task probes (logistic, slope ridge 0.01, no selection); `G_P` is computed on validation and test tasks (14 tasks, as in experiment 39's held-out criterion). Criterion coverage must be at least 90%.
- **Indices, frozen and label-free:** primary `C_ms_gold` as committed in experiment 39's `units_*.json`. Secondary: `C_ms_gold_fit_tasks_only` (recomputed with experiment 39's code on ladders from the 10 train tasks only, so the index and the criterion share no task), `TI_var_trainnorm` and `PTI_v0_frozen`. No index weight, normalizer or threshold is fitted to prover outcomes.
- **Pools:** primary = experiment 39's test LLM configurations; train+validation and all LLM configurations are reported descriptively.

### R2: VeriBench experiment 106 v5 natural outputs with recorded Lean entailment outcomes (artifact level)

- **Artifacts:** the 99 candidate files of groups G01 (Claude Code, Opus 5) and G02 (Codex, GPT-5.6 Sol) in `106_simulated_expert_raters_icl_from_human_labels_leave_one_agent_out_fsc_judge/expt_v5`, VeriBench revision `ec1f9b2a44`, joined by exact candidate sha256 to the solver manifests of experiments 138 (Tiny-256), 144, 147, 150 and 151 (Core-614). No join uses row position or task name alone.
- **Procedure:** the historical agent-written bridge pipeline with the experiment 145 rules (bridge compiles, every gold theorem proved, standard axioms in the bridge and every named solver theorem, gold unedited, non-vacuity witness), first-pass outcomes (experiment 150's retry conversion `S077` scored 0). The Gemini prover of experiment 158 on the Tiny-256 subset is a prover-sensitivity row. This target has known integrity gaps; see the source audit.
- **Judges:** 32 committed configurations: frozen H2 and H0 judges (GPT-6 Sol high, Claude Opus 5.5 max), four fold-rebuilt recipe judges, and six simulated-rater models × four frames. Six model-provider families. Recovery runs (`*_rec1*`) are excluded. Scores are per-item medians over complete cells, judges on 0–1 and raters on 0–5 divided by 5.
- **Score map:** two-fold task cross-fitting (fold = SHA-256 of `e66-r2-crossfit-v1:<task>` mod 2), so no artifact's own outcome enters its forecast.
- **Level 2 in R2 is limited.** These configurations never scored cert-judge's deletion ladders, so `C_ms_gold` exists only for the 4 frozen H2/H0 configurations that share model, effort and prompt name with experiment 39 units; those 4 are reported descriptively (fewer than 8 units, so no correlation). A separately labeled teacher-assisted label-free signal is tested instead: each configuration's Spearman agreement with the mean of all configurations from other model families on the 99 items. It reads no prover outcome but depends on the other judges' calls. It is not the cert-judge behavioral index.

### P1: prospective condition (prepared, not run)

A fresh run needs a validated frozen target. VeriBench experiment `169_natural_output_prover_fsc_validation_11-06-2026` is stopped with 14/100 statement-only contexts emitted and 0 measured outcomes. Trustworthy-theorem-judges experiment `05_fresh_local_prover_target_judges` (owned by a Codex worker) does not exist yet. When either releases a frozen target with kernel-replayed outcomes, P1 scores its artifacts with the experiment 58 open-weight panel (13 models × 9 prompts, local vLLM on SNAP, $0 API) using `experiments/58_open_weight_judges_on_e39_e42_probes/scripts/judge_vllm.py`. The experiment 58 indices (`C_ms_gold` for 117 configurations) are already frozen, and the R1 analysis code is applied unchanged with the new target. See `PROSPECTIVE_P1.md`.

## Property review for a prover target (before use)

| Behavioral property | Expected response under a statement-only prover target | Use here |
|---|---|---|
| Gold statement deletion (`C_ms_gold`, `P_ms`) | Removing statements cannot add coverage, so outcomes are non-increasing; a redundant deletion may leave full coverage unchanged, so ties are expected | Semantically justified; primary index |
| Bug monotonicity (`P_bm`, `bm_gold`) | Changing only implementation definitions leaves statement coverage unchanged | Not justified for this target; `PTI_v0_frozen` and `TI_var` contain it and are reported as secondary |
| Identity (`ident`) and blank | Gold against itself is covered; an empty candidate is not | Justified |
| Alpha-renaming invariance | Renaming a bound variable preserves statements | Justified |
| Repeat stability | A reliability property, independent of the target | Justified as reliability only |
| Search randomness and budget | `P_E42` is deterministic; the R2 bridge authoring was not budget-fixed | Disclosed; no monotone response to budget is assumed |

Controls: the 4 deterministic configurations (edit distance, random, theorem-count ratio, name overlap) are included as judges. The theorem-count ratio is deliberately misleading on vacuity probes, which keep every theorem. The lexical prompt `LEX` is a lexical control.

## Statistics

Spearman (primary), Pearson and Kendall are reported individually. Intervals come from a two-level bootstrap with 10,000 draws (seed 66): resample judge families, then evaluation tasks, recomputing `G_P` from per-artifact errors with the fitted maps held fixed. One-sided permutation p-values (10,000 draws) are given across configurations and within judge families. Prior exposure makes every result retrospective. These designs set no sample size; no threshold is transplanted from the human study. Results are descriptive (`p-val` as computed, no confirmatory claim).

## Predictions (written before running)

| Quantity | Prediction |
|---|---|
| R1 constant-judge `G_P` | about 0.78 (held-out covered share near 0.32) |
| R1 best configurations' `G_P` (fitted) | above 0.9 for configurations that pass experiment 42's semantic screen |
| R1 primary association, `C_ms_gold` vs `G_P`, test configurations | positive, Spearman between 0.3 and 0.7, wide interval (about 16 configurations, 4 models) |
| R1 within-family association | weaker than pooled (experiment 48 found the human-criterion association was not resolved within judge models) |
| R1 `C_ms_gold` selection regret | under 0.05, with the picked configuration above the fixed-H2 mean |
| R1 theorem-count control | `G_P` near or below the constant judge |
| R1 `PTI_v0_frozen`, `TI_var` | weaker association than `C_ms_gold` (bug monotonicity is misaligned) |
| R2 frozen H2/H0 judges' `G_P` (cross-fitted) | 0.80–0.88 versus a constant judge near 0.77 |
| R2 consensus signal vs `G_P` | positive, Spearman 0.2–0.6 |
| R2 prover dependence | the U and Gemini provers disagree on a substantial share of the Tiny-256 subset, so rank agreement differs by prover |

## Reading

- **Supported if** R1's primary association is positive with an interval above zero and index selection beats the fixed-rubric and random baselines: on this constructed theorem-level target the behavioral index selects prover-agreeing judges. It would not establish natural-output, file-level or semantic validity.
- **Not supported if** the interval includes zero or selection does no better than random; report it as such.
- R2 informs whether label-free selection works on natural outputs under a historical target; it cannot test `C_ms_gold` across judges.

## Prior exposure

- Experiment 42 already reported per-configuration directional accuracies on these probes and their association with the human criterion, and tested adding them to `C_ms_gold` for predicting human agreement. It did not compute prover-outcome Brier criteria or their association with any index.
- The H2 recipe's aggregate was already fitted against the R2 prover outcomes (trustworthy-theorem-judges experiments 03 and 04), so the frozen H2 configurations are exposed. No other R2 configuration had been compared with prover outcomes. During inventory, two rows of a joined table were displayed; no association was computed.

## Funding and compute

0 model calls and $0 for R1 and R2 (cached data on Brando's Mac). P1 uses local open-weight models on SNAP, allowed under the Vals pause. No Valkyrie or provider-key call is admitted.

**TLDR-end:** [cj: experiments/66_prover_target_judge_selection_by_behavioral_index] Frozen protocol for a two-level test of whether cert-judge's behavioral index selects prover-agreeing judges: R1 on experiment 42's fixed Lean procedure, R2 at the artifact level on 99 natural outputs, and a prepared local prospective run gated on a validated target.
