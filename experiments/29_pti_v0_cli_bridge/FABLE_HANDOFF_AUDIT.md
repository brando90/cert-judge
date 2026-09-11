# Audit of the Fable/Claude Code handoff

## Verdict

**Not ready to execute end-to-end as written.** The package has a good decomposition and many correct numerical details, but it contains several scientific and repository-state errors that can change the result or overwrite newer work. It is suitable as source material after the overrides in `03-SPEC-OVERRIDES-R41-R49.md`.

## What the plan gets right

- It separates the human-grounded target from the label-free proxy.
- It freezes median repeat aggregation, `(1-rho)/2`, `2*sd(ddof=0)`, and stable log-domain products.
- It requires pre-bridge freezing and disallows relabeling legacy TIvar results as PTI-v0.
- It identifies alpha-vs-gold as the potentially missing headline property.
- It includes uncertainty, a smallest effect size of interest, and manuscript compliance work.

## Blocking corrections

### 1. Constant ladders cannot be removed based on judge outputs

The handoff's R26/R36 panel-cleaning rule removes ladders that are constant under every current primary judge, then excludes judge-specific constant ladders. This can erase a shared failure mode and uses the evaluated judges to define the test set.

The corrected rule is:

- validate the **probe itself** without using judge scores;
- globally exclude only objectively invalid probes: duplicate/no-op artifacts, malformed or misordered transformations, failed compilation/elaboration, missing files, or a documented construction failure;
- once a probe is structurally valid, a constant judge-score ladder is a behavioral failure and receives `C=0`;
- report the constant-ladder fraction separately;
- coverage failures can yield `NOT_COMPUTABLE/DEFER`, but behavioral constants are not missing data.

This prevents both failure erasure and the opposite mistake of letting a malformed probe zero every judge.

### 2. The outer bridge figure must not use `y=x` or `|PTI-TI|`

`PTI_v0 in [0,1]` and raw `TI_m1 in [-1,1]` are not calibrated measurements on the same level scale. A `y=x` diagonal and mean absolute level gap imply a claim the metric does not make.

Use one point per judge, Spearman/Kendall association, uncertainty, family/role encodings, and an optional non-causal trend guide. No identity line; no level MAE.

### 3. The ICLR port is already complete

The live repository already contains `paper_latex/ICLR_2027_submission/main.tex`. The task must revise this file in place and preserve newer audited disclosures. Re-porting TMLR risks overwriting the current construct/criterion/instrument narrative and negative-transfer results.

### 4. Experiment 27 already exists

Open cert-judge PR #38 contains `experiments/27_ti_plot_like_scatter_plots`, tests, and an item-level TI_2' diagnostic built from audited cached data. It depends on ultimate-utils PR #44.

The new work must:

- review and consume those PRs;
- not recreate the utility;
- use Exp27 for the **inner**, item-level criterion diagnostic;
- create a separate **outer**, judge-level PTI-v0 vs TI_m1 bridge plot.

### 5. The alpha approval is too broad

The original cost formula bundles four transformations. PTI-v0 only requires alpha for the top-level invariance factor. The approval gate must quote:

- alpha-only missing calls and cost;
- optional RENAME/REORDER/STYLE diagnostic calls and cost separately.

Declining optional diagnostics must not block the headline alpha factor.

### 6. “Exactly one pause” is an unsafe promise

The repository's global rules require independent QA and explicit approval for potentially costly compute. A real alpha-transform bug, unresolved PR dependency, dirty worktree, or invalid panel mapping can legitimately block execution.

The corrected workflow has one **planned** inference gate, but permits evidence-backed blockers. It never promises that no other human decision can arise.

### 7. Necessity language must be scoped

For a correlational human criterion, local monotonicity and invariance do not follow as unconditional mathematical necessities. Use either:

- Route A: define trustworthiness to include the behavioral requirements; or
- Route B: state explicit metamorphic-validity and margin assumptions that make large violations falsifying.

Otherwise call them pre-specified falsifiable behavioral diagnostics/requirements, not universally necessary conditions.

### 8. The existing AGENTS/CLAUDE guidance is stale

`AGENTS.md` still describes P1–P7 and JTI. The execution should update the local project description after loading the global rules, while preserving environment and safety instructions.

## Recommended use of Claude Fable 5

Fable 5 is appropriate as an independent reviewer of the completed Codex work. Give it the frozen spec, the diffs, raw outputs, and manuscript; ask it to recompute the headline statistics and attack the claims. Do not let it inherit the builder's result summary as ground truth.
