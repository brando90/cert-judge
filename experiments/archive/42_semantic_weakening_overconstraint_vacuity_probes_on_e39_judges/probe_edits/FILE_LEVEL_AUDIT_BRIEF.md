# Experiment 42 file-level audit brief

**TLDR:** Instructions for the Claude Code subagents (claude-opus-5-5, subscription) that labelled every valid weakening and over-constraint probe as file-level strict or redundant before any judge call; the labels define a pre-registered sensitivity view, not probe validity.

## Why

Lean proves each changed theorem statement of a probe is implied by (is weaker than) its reference counterpart. That is theorem-level weakening. A file can still guarantee as much as the reference overall when another, unchanged theorem restates what was dropped (for example, `Post` drops the right-partition conjunct but `bisect_right_partition_thm` still states it). The audit labels each probe at the file level.

## Definition

The guarantee of a file is the conjunction of all its theorem/lemma statements, read as a formal specification about an arbitrary implementation (implementation definitions are uninterpreted; `Prop` definitions keep their meaning; proofs, unit tests and docstrings are ignored).

- **strict**: at least one guarantee of the reference is not implied by the probe file's theorem statements taken together (name the dropped guarantee and why nothing in the probe restates it).
- **redundant**: every guarantee the reference states is still implied by the probe file's theorem statements taken together (name which theorem restates each dropped piece).
- **unclear**: you cannot decide confidently; explain.

Compare each probe with the **reference**, not with the previous level (levels are cumulative). Over-constraint probes add an unsatisfiable hypothesis to some theorems; they are strict unless every such theorem's content is restated by a theorem without the added hypothesis.

## Files

- Reference: `/lfs/skampere1/0/brando9/veribench_e42/experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/references/annotation/<task>.lean`
- Probes: `/lfs/skampere1/0/brando9/cert-judge_e42/experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges/private/probes/{weak,overc}/<task>__L<k>.lean` (diff them against the reference)
- Edit descriptions: `probe_edits/<task>.json`

## Output

Write `probe_edits/audit/<task>.json`:

```json
{"task": "<task>", "auditor": "claude-opus-5-5 (Claude Code subagent; subscription)",
 "labels": {"weak__<task>__L1": {"label": "strict|redundant|unclear", "dropped": "...", "restated_by": "... or none", "why": "one or two sentences"},
            "overc__<task>__L1": {...}}}
```

Label every valid probe listed for your tasks. Write only those files. Do not run git or modify anything else.
