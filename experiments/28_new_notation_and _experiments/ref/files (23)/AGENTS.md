# AGENTS.md — cert-judge standing rules (all coding agents; Codex-native)

These rules apply to every agent session and every subagent in this repository. They are
guidance the agent must follow, not sandbox enforcement — the sandbox/approval layers are
configured separately by the human.

## Authority order

1. `docs/spec/certjudge-memo-addendum-R23-R35.md` + `docs/spec/RECONCILIATION-R36-R40.md`
2. `docs/certjudge-revision-memo.md`
3. `PTI_V0_CANONICAL_SPEC.md` + `DECISION_LOG.md` (numerics/notation where not superseded —
   known supersessions: constant-ladder C=0 → exclusion machinery (R36); absolute no-spend →
   the single gated α run (R37); its source-of-truth order is inverted)
4. Task prompts (`agent-prompt-*-v2.md`, `CODEX_AGENT_PROMPT_CERT_JUDGE.md`), then code
   comments.

Any unenumerated conflict: stop that thread, write `BLOCKED.md` (what is wrong, what it
affects, what you propose, what evidence settles it), continue independent work. Never choose
silently, never silently fix.

## Non-negotiables

- **No paid model calls from any agent phase, ever.** The one sanctioned inference (the α
  variant-vs-gold run) is prepared as a script + call count + cost estimate for the human to
  execute; the agent never loads or prints API keys or secrets.
- **No fabricated numbers.** Missing values are `TBD`, `NOT RECOMPUTED`, or
  `LEGACY TIvar RESULT — NOT PTI-v0`. Every reported number is DOCUMENTED (path) / DERIVED
  (command) / UNKNOWN. TI_var-era results never appear as PTI-v0 results.
- **Freeze.** PTI-v0 (properties, estimators, σ̃ = mean over levels of 2·sd(ddof=0), (1−ρ)/2,
  exclusion + θ = 0.20, two-level log-space GM, no floor) changes for no reason after any
  bridge number exists. Properties are never reselected or reweighted on results.
- **Determinism.** Seeds fixed (0); 10,000 bootstrap iterations; iteration sorted by item id;
  zero-first log-domain GMs; endpoint snapping per the canonical spec.
- **Git.** Stacked branches `pti-v0` → `bridge-plot` / `iclr2027-port`; one PR per branch; no
  merges; no pushes to `main`; no OpenReview submission; legacy outputs never overwritten;
  every new output row carries `metric_version = "PTI_v0"`.
- **Conformance gate.** The PTI-v0 implementation must pass `PTI_V0_TEST_VECTORS_v2.json`
  (1e-12) and the amended unit tests before any property is computed on real data.

## Serialization invariants (binding on ALL subagents — Ultra runs cooperating subagents)

These are global orderings, not per-agent suggestions. No subagent may cross them even if
another subagent's work appears to unblock it:

1. Conformance tests pass → only then any real property computation.
2. Panel cleaning (label-free) → only then the Step-3 property-table + GATES commit.
3. The Step-3 commit exists in history AND `ALPHA_RUN: funded(outputs committed) | declined`
   is recorded in `RESULTS.md` → only then may **any** agent compute **any** bridge number.
   The bridge is computed exactly once, by exactly one agent, on exactly one branch.
4. One writer per branch at a time; subagents coordinate through committed artifacts, not
   shared working trees.
5. `bridge-plot` and `iclr2027-port` branch only from a committed head of `pti-v0`.

Parallelism that IS allowed: repo audit ∥ oracle implementation ∥ probe-set generation;
manuscript work that consumes no PTI-v0 numbers ∥ everything above; figure scaffolding on the
synthetic generator ∥ Task A. When in doubt, serialize.

## Repository specifics

- Staging directory `experiments/28_new_notation_and _experiments/` (note the SPACE — quote
  all paths) holds the handoff payload; it is staging only: never an experiment to run, never
  committed (targeted `git add` only), never renamed or deleted by an agent.
- `experiments/27_ti_plot_like_scatter_plots` is the existing item-level TI scatter work: the
  figure task revises it in place; the run task inventories it and cross-checks TI values
  against it (expected deltas: 72→75 Option-B rename; TI_2' decomposition vs plain TI_m1).
- Experiment number 28 is taken; new experiment directories start at the next free number.
- Historical workshop/submission trees are archival: never bulk-edited.
