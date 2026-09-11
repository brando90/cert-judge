# THE ONE PROMPT — CertJudge end-to-end (Codex, single-agent)

Model/reasoning: chosen by the human in the picker — GPT-5.6 Sol at **Extra High** (escalate
to **Max** only for Phase 4, the manuscript). **Ultra is not used**: this pipeline's critical
path is intentionally serial, so parallel subagents buy cost and race risk, not quality.

## Where everything lives

All inputs are in the staging directory
`experiments/29_pti_v0_cli_bridge/` — **the directory name contains a space and
the payload zip name contains parentheses: quote every path in every command.** If
`certjudge-FINAL.zip` (or `files (22).zip`) is present and not yet extracted, unzip it in
place first, then inventory the contents.

Read in this order before acting: `AGENTS.md` → `AMENDMENTS-R41-R48.md` →
`RECONCILIATION-R36-R40.md` → `certjudge-memo-addendum-R23-R35.md` → `PREFLIGHT-PROMPT.md`.
Authority: amendments > reconciliation + addendum > `certjudge-revision-memo.md` >
`PTI_V0_CANONICAL_SPEC.md`/`DECISION_LOG.md` > task prompts > code comments. Any
unenumerated conflict ⇒ `BLOCKED.md` (what's wrong, what it affects, proposal, settling
evidence), then continue independent work.

## Standing rules (non-negotiable)

`AGENTS.md` binds this session (commit it to the repo root in Phase 1). No paid or remote
model calls, ever, from this agent — `ALPHA_RUN` starts as `declined (probe invalid)` per
R41 and changes only by a human message. No fabricated numbers: `TBD` /
`LEGACY TIvar RESULT — NOT PTI-v0` / DOCUMENTED-DERIVED-UNKNOWN labels throughout. PTI-v0 is
frozen; nothing about it changes after any bridge number exists. Branch names per R43:
`pti-v0-run` → `pti-v0-bridge-figure` → `iclr2027-pti-v0-refresh` (linear stack, R44); one
draft PR at a time; no merges; no pushes to `main`; no OpenReview actions.

## Execution: phase-gated, one thread

**Start now with Phase 0** exactly per `PREFLIGHT-PROMPT.md`: branch `preflight-2026-08`,
produce `docs/PREFLIGHT_REPORT.md` (repo topology incl. the `iclr2027-port` branch collision
and missing `SYNC.md`; α-transform validity reproduction and whether the cached workshop
ALPHA variants are contaminated; the exact 75-item label-repair diff plan; cache coverage;
split α-only vs diagnostics cost sheet; judge-manifest draft; statistical-pin check;
bridge-figure inputs from `experiments/27_ti_plot_like_scatter_plots`; blockers with
smallest fixes; GO/NO-GO per phase). Open one draft PR for the report. **Then stop.**

**Phase gating:** proceed to a later phase ONLY when the human sends "Proceed to Phase N" in
this thread. Never continue on your own initiative, even if every mechanical gate passed —
the Phase-1→2 boundary is a human *scientific* review by design (R48).

- **Phase 1** (`pti-v0-run`): per `agent-prompt-pti-v0-run-v2.md` as amended — spec commits
  incl. creating `SYNC.md` (R43), the full R42 label repair with 75/75 verification,
  conformance gate on `PTI_V0_TEST_VECTORS_v2.json` + amended tests, manifests, cached
  properties (eq/bm/ms) with all diagnostics and sensitivity columns, R47.4 probe-validity
  audit, Step-3 property-table + gates commit, α validity manifest + split cost sheet. One
  draft PR. Stop for human review.
- **Phase 2**: α decision — only a human message funds it (R41 conditions must hold); the
  default declined record otherwise stands.
- **Phase 3** (same branch): the single bridge computation + SESOI per the run prompt's
  Step 4/5 as pinned by R47 (percentile bootstrap with counted invalid resamples;
  Gaussian-copula DGP + permutation sensitivity; primaries-only lead and pooled, τ_b, per-
  property exploratory; 27-cross-check with explained deltas). Stop.
- **Phase 4a** (`pti-v0-bridge-figure`): the figure per `agent-prompt-bridge-plot-v2.md` as
  amended by R45 (no y=x, no level gap), anchored to `experiments/27_…`. Stop.
- **Phase 4b** (`iclr2027-pti-v0-refresh`): the manuscript per
  `agent-prompt-iclr2027-port-v2.md` as amended by R39/R43/R46/R47.3 — revise the existing
  `paper_latex/ICLR_2027_submission/main.tex` in place; corrected abstract skeleton fills
  only from `RESULTS.md`; screen/τ_k claims demoted per R47.3; no literal `\todo{}`
  survives; ≤ 9 pages; anonymization grep; AI-use + reciprocal-reviewing statements from the
  prefetched CFP text; build with latexmk; `STATUS.md` with everything outstanding.

Environment notes (cloud): dependencies and prefetches go in the environment **setup
script** (block in `00-CODEX-ULTRA-MASTER-PROMPT-v4.md`); agent-phase internet stays off;
never configure an inference key anywhere this agent can see.

Human touchpoints, in order: review the Phase-0 report (the α-contamination answer and the
label-repair diff are the two items that need your eyes) → "Proceed to Phase 1" → scientific
review of the Phase-1 PR → α decision → "Proceed to Phase 3" → review → Phases 4a/4b →
OpenReview abstract Sep 18, paper Sep 25 2026 AoE → reciprocal-reviewer registration.

---
END OF AGENT INSTRUCTIONS

```
TL;DR (for the human reader; the agent should ignore this block):
This is the only thing you paste. It starts the no-spend preflight immediately and then
holds at every phase boundary until you literally type "Proceed to Phase N" in the same
Codex thread — so one paste drives the whole pipeline (preflight → cached metric → your
review → α decision → single bridge → figure → paper on the existing ICLR draft) without
ever letting the agent spend money, fabricate a number, or blow through a
pre-registration boundary on its own. Picker: Sol + Extra High now, Max only for the
paper phase, no Ultra.
```
