# Experiment 42 weakening-edit proposer brief

**TLDR:** Instructions given to the Claude Code subagents (model claude-opus-5-5, subscription) that proposed the cumulative weakening edits in `probe_edits/<task>.json`; an edit enters the probe set only if `scripts/build_semantic_probes.py` validates it in Lean (fail-closed).

## Task

For each assigned VeriBench task, write `probe_edits/<task>.json` with up to three cumulative weakening levels of the annotation-era reference
`/lfs/skampere1/0/brando9/veribench_e42/experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/references/annotation/<task>.lean`.
Level k applies the edits of levels 1..k in order. Each level adds exactly one new semantic weakening of the formal specification, so the file guarantees strictly less at each level.

Allowed operations (one per level): drop a conjunct from a conclusion-side predicate (`Post`, `Post_prop`, a `*_prop` definition used as a conclusion, or a theorem's conclusion); relax `=` to `≤` or `≥` where meaningful; add a disjunctive escape (`C` becomes `C ∨ <plausible side condition>`).

Rules:

- Edit only theorem statements and `Prop`-valued definitions (and a theorem's proof only if the edited statement no longer elaborates with it; never introduce `sorry` where the reference has a complete proof). Never edit implementation definitions, unit tests (`example`, `#eval`), docstrings or comments, and never add, remove or rename declarations.
- Weaken only on the conclusion side. Dropping a conjunct from a precondition (`Pre`) or a hypothesis strengthens the theorem and fails the Lean forward check.
- The edited file must read naturally: no comments about the edit, no suspicious names, and the same layout style.
- Prefer the guarantees that matter most: level 1 removes one conjunct of the main postcondition or correctness theorem (for example the permutation half of a sorting specification, or one partition side of a search); levels 2 and 3 weaken different guarantees.

## File format

```json
{"task": "<task>", "proposer": "claude-opus-5-5 (Claude Code subagent of the experiment 42 worker; subscription)",
 "levels": [
  {"level": 1, "op": "drop_conjunct|relax_eq|disjunctive_escape", "description": "one line",
   "edits": [{"decl": "<declaration name>", "old": "<exact text, unique inside that declaration>", "new": "<replacement>"}],
   "proofs": {"<theorem name>": "<optional tactic block for the forward check>"}}
 ],
 "no_more_levels_reason": "<only if fewer than 3 levels are possible: why>"}
```

## Validation

Run `cd /lfs/skampere1/0/brando9/cert-judge_e42/experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges && /lfs/skampere1/0/brando9/vb103_venv/bin/python scripts/build_semantic_probes.py --tasks <task> --only weakening --out private/proposer/<task>.json`, then read the `weak` rows of `private/proposer/<task>.json` (`valid`, `reason`, `checks`). Check files are in `private/checks/<task>/weak_L<k>.lean` and Lean's output is in `.out`.

What the builder checks for each level:

1. The weakened file elaborates (Lean 4.22 + Mathlib, `sorry` warnings allowed).
2. For every theorem whose statement changed, or that mentions an edited definition, the check file proves `(∀ binders, reference statement) → (∀ binders, weakened statement)` with no `sorryAx`. In the check file, every data-valued implementation definition is an `axiom`, so a proof cannot compute through the implementation; the original version of each edited definition is available as `<name>_e42o`. The default proof tries `intro H; intros` followed by `trivial`, `simp_all [<edited defs and their _e42o copies>]`, `omega`, `apply H <;> assumption`, `left/right; apply H <;> assumption`, `tauto` and `aesop`. If none works, give a tactic block in `proofs` for that theorem, for example `intro H α _ _ xs h\nhave := H xs h\nsimp only [Post, Post_e42o] at this ⊢\nexact ⟨this.1, this.2.2⟩`.
3. The reverse implication is attempted with the same automatic tactics. If it is proved for every changed theorem, the level is excluded as proved-equivalent. Choose a genuinely weaker statement instead.

Iterate until every level is `valid: true`, or record in `no_more_levels_reason` why fewer levels are possible. Do not edit anything except `probe_edits/<task>.json` (and your own files under `private/proposer/`). Do not run git.
