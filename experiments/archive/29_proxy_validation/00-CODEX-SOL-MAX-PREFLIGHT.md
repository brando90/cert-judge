# CertJudge PTI-v0 v4 — GPT-5.6 Sol `max` preflight

You are the primary engineering/research agent in `brando90/cert-judge`. This is a **read-only, zero-spend preflight**. Follow repository `AGENTS.md`, but first load the current global rules from `brando90/agents-config`. Treat stale P1–P7/JTI descriptions as historical, not as the current scientific specification.

Read all files in this handoff, especially `03-SPEC-OVERRIDES-R41-R49.md`. The overrides win over conflicting Fable v2/v3 language.

## Hard boundaries

- Do not load API keys or use paid model inference.
- Do not edit source, labels, manuscript, branches, or PRs.
- Do not compute or reveal a PTI-vs-TI bridge result.
- Do not merge, close, rebase, or push anything.
- You may create exactly one uncommitted report: `PREFLIGHT_PTI_V0_V4.md`.

## A. Repository and dependency audit

Record current branch, HEAD, dirty state, default branch, Python/Lean/LaTeX environment, and current global rules revision.

Inspect:

- open ultimate-utils PR #44;
- open cert-judge PR #38;
- `experiments/27_trust_plots` on the PR head and in the current checkout;
- `paper_latex/ICLR_2027_submission/main.tex`;
- overlapping branches/PRs such as `iclr2027-port`, `pti-v0`, or bridge branches;
- stale `AGENTS.md`/`CLAUDE.md` guidance.

Propose the exact dependency and branch plan. Do not recreate Exp27.

## B. Canonical pipeline audit

Locate and cite file:line evidence for:

- current property computations;
- repeat-score schema and cache keys;
- human panel loaders and duplicate handling;
- legacy TIvar/JTI outputs;
- figure/table generators;
- tests and build commands.

State where PTI-v0 should be integrated rather than creating an orphan implementation.

## C. Structural probe audit

Separate probe validity from judge behavior.

For bug and spec ladders, verify from files/metadata/source generation:

- distinct artifacts and intended level ordering;
- no duplicate/no-op levels;
- successful Lean parsing/compilation/elaboration where required;
- a documented semantic degradation at each step.

List objectively invalid probes. Do **not** inspect score constancy to decide whether a probe is valid.

For alpha-renaming, inspect the transformer and run no-cost local samples:

- rename binders and every bound occurrence consistently;
- distinguish real transforms from no-op/comment fallbacks;
- detect malformed tokens;
- compile/elaborate transformed artifacts;
- produce original/transformed hashes and a validity manifest.

If alpha is not demonstrably semantics-preserving, mark `P_eqalpha` HARD BLOCKED and do not estimate spend.

## D. 72→75 panel audit

Reconstruct Option B in memory/temp only:

- verify each stale `0_unsafeMultiply_safe` key maps to the intended `1_unsafeMultiply_safe` gold using content/hash/metadata evidence;
- preserve the three agent generations;
- apply the declared duplicate rule;
- recompute strict, lenient, and average views deterministically;
- compare with checked-in files;
- verify 75 unique aligned pairs = 25 problems x 3 generations;
- report all changed historical statistics.

Do not edit labels.

## E. Cache and spend audit

Inventory cached coverage by judge and property. Quote separately:

1. missing **alpha-only** calls and estimated cost;
2. optional RENAME/REORDER/STYLE diagnostic calls and estimated cost.

Subtract cached original/base calls. Give exact commands but run none.

## F. Statistical freeze audit

Verify or mark unresolved:

- exact judge manifest and primary/control roles;
- `f=(i,a,q)`, repeat `r`, human pass/rater `u`, level `ell`;
- median repeat aggregation;
- Spearman primary and Kendall tau-b robustness;
- `(1-rho)/2` orientation;
- `2*sd(ddof=0)` instability;
- `K_aj=1 => factor=C`;
- log-domain zero-first GM;
- structurally valid constant score ladders receive `C=0`;
- missing/coverage threshold and DEFER policy;
- property, PTI, criterion, and bridge bootstrap units and CI method;
- SESOI simulation DGP;
- whether per-property screen thresholds exist. If not, prohibit claims about human-validations saved.

## G. Figure and manuscript audit

Confirm:

- outer bridge has no `y=x` and no `|PTI-TI_m1|` level metric;
- Exp27 is the inner item-level diagnostic;
- active ICLR draft is revised in place;
- legacy values cannot be renamed PTI-v0;
- current abstract claims are compatible with Route A/B and the new metric.

## Output

Write `PREFLIGHT_PTI_V0_V4.md` with:

1. verdict: `READY`, `READY AFTER FIXES`, or `BLOCKED`;
2. HARD blockers with evidence;
3. SOFT issues;
4. dependency/branch plan;
5. canonical integration points;
6. structural probe manifest summary;
7. panel-repair findings;
8. alpha-only and optional-diagnostic spend estimates;
9. frozen statistical decisions and unresolved decisions;
10. exact execution command list;
11. human approvals required.

Then stop.
