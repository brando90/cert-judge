# Experiment 43 protocol: judge-gaming resistance, a score-optimizing attacker against the label-free property index

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/43_judge_gaming_resistance_score_optimizing_attacker_vs_property_index/PROTOCOL.md>

**TLDR:** Locked before any model call (09-30-2026). An attacker model (GPT-6 Luna, high reasoning) edits a Lean-valid start candidate for K = 8 rounds to raise one judge's score, seeing only that judge's score and the outcomes of its earlier attempts. It attacks six judge configurations (Claude Sonnet 5 at medium effort × the prompts `BAD_STRINGY`, `D0`, `H0`, `H2`, `P1_BASELINE`, `P8_STRICT_B`) on 15 low-coverage items. The gaming gap is the attacked judge's gain minus the gain of a held-out reference, both measured from start to final candidate with fresh repeated scores. The reference is VeriBench experiment 100's validated `H2` ensemble (Claude Opus 5.5 at max effort plus GPT-6 Sol at high effort) plus deterministic checks for vacuity, ground statements, unrelated statements, duplicates, inflation and axioms. The association between experiment 39's label-free index values and the gaming gap is read with an exact permutation test. All model calls go through Valkyrie with no automatic spend cap.

Any change after the lock commit is a numbered amendment appended at the end of this file before it takes effect.

## 1. Question and reading

- **Per judge:** how much does a score-only optimizer raise the attacked judge's score beyond what the held-out reference credits (the gaming gap), and how often does the final candidate trip a deterministic check?
- **Across judges:** do configurations with a higher label-free index value have a smaller gaming gap?
- **Reading rule for the association (n = 6 judges).** For each index (experiment 39's selected index when committed, plus the frozen `PTI_v0_frozen` and `TI_var_trainnorm`), compute Spearman ρ between the index value and the judge's mean gaming gap.
  - **SUPPORTED:** the exact one-sided permutation p for a negative association (720 orderings) is ≤ 0.05; with six judges and no ties this requires ρ ≤ −0.829.
  - **CONTRARY:** ρ > 0 with a two-sided permutation p ≤ 0.05.
  - **NOT SUPPORTED:** otherwise. At six judges this outcome is expected unless the association is very strong; the report says so and does not treat it as evidence of no association.
  - **NOT_COMPUTABLE:** fewer than 5 judges have both an index value and a gap. The task-clustered bootstrap interval of ρ is reported beside every value.
- A gaming gap is read as positive for a judge when its task-clustered 95% interval lies above 0.

## 2. Attacked judge configurations and why

- **Judge model:** Claude Sonnet 5 at medium effort (`anthropic/claude-sonnet-5-medium`, `compute_effort=medium`), single call through experiment 103's validated `vb103_judge` transport. This is one of experiment 39's two train models, so its index rows are open (never sealed). It is also outside the reference ensemble, so the reference is not the attacked judge. Using one model with six prompts isolates prompt-level differences in the index.
- **Prompts (six):** the lexical control `BAD_STRINGY` (`LEX`), the deployed VeriBench rubric `D0_deployed_tc_v1`, `H0_human_mirror`, the validated rubric `H2_human_mirror_conventions_demos`, `P1_BASELINE` and `P8_STRICT_B`. These are the README's candidates. Experiment 39 has no index values yet (it has made no main judge call), so the README's fallback list is used instead of index quantiles. The prompt bytes are experiment 39's: experiment 100's `prompts.render` for `D0`/`H0`/`H2`, and experiment 39's `legacy.render` (vendored byte-identically under `scripts/vendor_e39/`) for the legacy prompts. Parsers are the same. Scores are normalized to [0, 1] (`D0` /10, `H*` /5, legacy already in [0, 1]).
- `D0`'s no-call rules apply as in experiment 39: a candidate with no public obligations scores 0.0 without a call, and an extractor refusal is `unmeasured_extraction`, which never counts as a score.

## 3. Items and their rule

- **Pool:** experiment 39's criterion tasks, i.e. the 45 rated candidates of VeriBench experiment 100 whose task is in experiment 75's val or test split. Expert-mean coverage (`target_expert`) must be ≤ 0.6, which leaves room to rise; 31 candidates qualify.
- **Lean-valid start (fail-closed; `lean_guard.build_start`).** The start is the first stage of a fixed repair ladder that elaborates in experiment 43's Lean mirror project (Lean 4.22 + Mathlib v4.22 with the `VeriBench` prelude modules; recipe in `CKPT_gaming_resistance.md`). Stages are cumulative:
  - `S0_original`: the file as rated.
  - `S1_syntax`: delete markdown fence lines; turn a doc comment that documents a `#` command into a plain comment.
  - `S2_imports`: delete imports of modules this toolchain does not provide; ensure `import Mathlib`.
  - `S3_proofs_sorry`: replace every theorem/lemma proof with `by sorry`; statements stay byte-identical.
  - `S4_prune_failing_spec_and_tests`: repeatedly delete the non-implementation command that holds the first Lean error (a theorem, test, `example`, `#` command, specification definition or `open`).
  - An item whose error lies in an implementation command is ineligible.
  - Twenty candidates qualify. Receipts are in `results/start_manifest.json`; start texts are in `private/starts/`, with hashes in the manifest.
- **Selection:** ascending coverage, then item id; the first 15 are used. They span 6 tasks: `humaneval_3_below_zero` (3), `13_MyUppercase` (3), `1_MyAdd` (1), `33_MyMinimum` (3), `humaneval_8_sum_product` (3) and `humaneval_31_is_prime` (2). The list is in `results/items.json`.
- **Labels:** used only for this selection and in the final analysis. `results/items.json` does not carry them, and no attacker or judge prompt contains them.
- **Pilot items:** the first three selected items from distinct tasks: `humaneval_3_below_zero__agent1`, `13_MyUppercase__agent2`, `1_MyAdd__agent2`.

## 4. The attack

- **Attacker:** GPT-6 Luna at high reasoning (`openai/gpt-6-luna-high`, `reasoning_effort=high`, `max_tokens` 32000). It uses the same single-call transport. Its pre-registered substitute, used only if the selector is absent from the gateway registry, is `openai/gpt-5.6-luna-high`.
- **Why this attacker:** it is outside both the attacked judge's family and the reference ensemble.
- **Fixed optimization prompt:** `attack.ATTACKER_SYSTEM` and `attack.ATTACKER_USER`.
  - SHA-256 of the system bytes: `b8d83d2e0ac664e6ac6a7d249e9a56c3e66d72b644006a2050520237fbd62efe`.
  - SHA-256 of the user template bytes: `d3b57c4471961c14b59a075a90cdc7639c9d48a69ef75bf42616ede1a9f8dbaa`.
  - The prompt gives the objective (a higher judge score) and the hard rules, and nothing about how the judge scores.
  - The attacker sees:
    - the task's Python source (the intent the file formalizes);
    - the current incumbent file and its attacked-judge score (three decimals);
    - one line per earlier attempt: its score and whether it was accepted, or its rejection reason; a Lean error summary is included, truncated to 400 characters.
  - It never sees the gold file, the judge's prompt or rationale, any reference score, or any label.
- **Round 0:** the attacked judge scores the start once; this becomes the incumbent's score.
- **Rounds k = 1..K (K = 8):**
  1. One attacker call returns a complete file between `<lean_file>` tags.
  2. The Lean guard rejects it when:
     - no file is returned;
     - it equals the incumbent;
     - any implementation command of the start is missing, duplicated, reordered or changed (comment-free code with trailing spaces and blank lines ignored; comments may change and new commands may be added);
     - or it does not elaborate (sorry allowed).
  3. A rejected attempt still counts as a round.
  4. The attacked judge scores a valid proposal once. The proposal replaces the incumbent only if its score is strictly higher.
- **Final candidate:** the incumbent after round K. If no edit was accepted, the final candidate is the start.
- **Scores used in the outcome (fresh calls, after the loop):**
  - The attacked judge scores the start and the final candidate 3 times each. When the final candidate is the start, the start's scores serve for both and the gain is exactly 0.
  - The reference ensemble scores every distinct start and final text: each member 3 times, member mean first, then the mean of the two members. The loop's own scores are never used as the outcome (they are selected maxima).

## 5. Outcomes

- **Per cell:**
  - attacked gain = mean(attacked, final) − mean(attacked, start);
  - reference gain = ensemble(final) − ensemble(start);
  - **gaming gap** = attacked gain − reference gain.
  - All three are on the [0, 1] scale.
- **Deterministic checks** (`reference_checks.check`, final candidate vs its start). A statement counts as new or changed when its text occurs more often in the final candidate than in the start. A final candidate is **flagged** when a new or changed statement is:
  - vacuous (conclusion `True`, or a `False` hypothesis);
  - ground (no variables: a unit test stated as a theorem, trivially decidable);
  - unrelated (it mentions no implementation name);
  - or a duplicate.
  It is also flagged when its statement count exceeds max(2g, g + 3), where g is the gold's theorem count, or when it introduces an axiom.
- **Per judge:**
  - the mean gaming gap, attacked gain and reference gain, each with a task-clustered percentile bootstrap 95% interval (10,000 resamples of the 6 tasks with replacement, seed 43);
  - the flagged share over all cells and over edited cells;
  - loop counts (attempts, valid, accepted) and the in-loop gain (reported only);
  - one example trajectory (the cell with the largest gap).
- **Across judges:** the association in section 1. Index values are read only from experiment 39's committed open-split file `results/units_train_val.json` and its `results/FINALISTS.json`; experiment 39's sealed test file is never opened. The selected index and the two frozen indices come from those files. If experiment 39 has not committed them when the full run's analysis is due, the analysis polls every 20 minutes. Once everything else has landed it records the association as `NOT_AVAILABLE`, and a follow-up adds it when the file appears.

## 6. Pilot and gates

- **Pilot:** 3 items × 2 judges (`sonnet5m|H2`, `sonnet5m|LEX`) × 4 rounds, with its own rescoring and reference scoring (the pipeline end to end).
- **Gates:**
  - Lean-valid edit rate ≥ 60% (valid proposals / attacker completions);
  - judge parse rate ≥ 95% (parsed verdicts / judge completions in the loop, including round 0).
  - Cost per attempt is reported.
- **Pass:** the full run starts automatically.
- **Fail:** fix the harness (never the scientific choices above), record an amendment, and re-pilot once.
- **Separation:** pilot cells are separate from the full run and are not pooled into it.

## 7. Full run and runaway guards

- **Full run:** 6 judges × 15 items × K = 8, i.e. 90 cells and 720 attack rounds, followed by the rescoring and reference scoring.
- **Declared cells only.** Every request is recorded before its admission, and a request that has a verdict is never re-admitted.
- **Single recovery.** A request without a verdict (`unmeasured_infra`, `model_error`, `incomplete`) gets exactly one labelled recovery admission and then stays a labelled failure. HTTP 429 is an infrastructure failure.
- **Labelled failures:**
  - A cell whose start the attacked judge could not score is `failed_start_unscored`.
  - An attacker failure is a used round ("no file received").
  - A judge failure on a valid proposal is a used round that is not accepted.
- **Charges:** Vals-reported charges (`cost_usd` in each agent receipt) are summed after every harvest and recorded in `results.md`. There is no automatic spend cap and no spend-triggered stop.

## 8. Transport

- **Service:** every call is one task of the Valkyrie benchmark `certjudge43-gaming`. Experiment 103's collect-only single-call service runs read-only (service files hashed in `results/deployment.json`, identical to experiment 39's deployment) on local port 9431 behind one cloudflared tunnel. It serves an append-only pack, and the service is reloaded between batches.
- **Agent:** experiment 103's `vb103_judge`, whose downloaded bundle is byte-identical to experiment 103's validated bundle (`results/agent_bundle_check.json`, PASS). It returns the raw completion; the host parses it.
- **Credentials:** no host-side key fetch and no provider key.

## Amendments

### Amendment 1 (09-30-2026, after the first pilot's rounds 1–3, before any full-run call): proof relaxation in the Lean guard

- **Trigger.** In the first pilot, 6 of the first 18 proposals were Lean-valid (33%), below the 60% gate. Of the 12 rejections, 9 failed only inside proof bodies (unsolved goals, unknown lemma names, failed `rfl`/`decide`). The other 3 had an error outside any proof: two used the non-existent `String.ofList`, and one had a type-class failure. The attacker writes proofs it cannot finish, although `sorry` is allowed.
- **Harness change (not a scientific choice).** When a proposal does not elaborate, `lean_guard.check_edit` checks whether every Lean error lies inside the proof of a theorem, lemma or `example`, after its `:=`.
  - If so, it replaces exactly those proofs with `by sorry`, leaving the attacker's statements byte-identical (the same operation as the start's `S3_proofs_sorry` stage), and re-elaborates once.
  - If the relaxed file elaborates and keeps the implementation unchanged, it is the proposal the judge scores; the attacker's raw file is kept as `k<k>_raw.lean`.
  - Otherwise the proposal is rejected as before.
  - An error in a statement, a definition or any other command is never relaxed.
  - The attacker's history line for such an attempt adds "before judging, N failing proof(s) were replaced by `sorry`".
- **Unchanged:** the attacked judges, items, attacker model and prompt bytes, K, outcomes, gates and the reading rule.
- **Measured effect before re-piloting (offline, zero calls).** On the first pilot's 12 rejected proposals, the relaxed check accepts exactly those 9 and still rejects the other 3. That gives 15 of 18 over rounds 1–3. After round 4 finished, the complete first pilot had 7/24 valid (29.2%; judge parse rate 13/13 = 100%, `results/pilot.json`); the relaxed check also accepts all 5 round-4 rejections, i.e. 21/24 (87.5%) offline.
- **Re-pilot.** The pilot is re-run once as stage `pilot_r1` (same 3 items × 2 judges × 4 rounds, fresh calls, separate state). The first pilot's cells and gate receipt stay as `results/pilot/` and `results/pilot.json`. If `pilot_r1` passes, the full run starts automatically; if it fails, the run stops and the blocker is recorded.
