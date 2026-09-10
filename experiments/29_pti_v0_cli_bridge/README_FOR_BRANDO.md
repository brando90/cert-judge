# CertJudge PTI-v0 handoff v4 — what to run

> Historical execution guide. Current integration status is recorded in
> `STATUS_PTI_V0_V4.md`: ultimate-utils PR #44 has been repaired and merged,
> ultimate-utils 0.10.9 is public, and cert-judge PR #40 has merged both
> Experiment 27 and Experiment 29 into `main`.

**Date:** 20 August 2026  
**Target repository:** `brando90/cert-judge`

## Recommendation

Use **GPT-5.6 Sol with reasoning effort `max`** for the main implementation run.

Do **not** use `ultra` as the primary writer for this handoff. `ultra` is a multi-agent orchestration mode; this task has a strict dependency graph, shared files, frozen statistical choices, and sequential commits. Parallel writers increase the chance of branch drift, duplicate implementations, or a manuscript written before the experiment is frozen. Use `ultra` for the final read-only mega-QA pass, where parallel independent audits are genuinely useful.

Use **Claude Fable 5 as the independent reviewer**, not as the sole executor of the original Fable handoff. The original plan is strong in ambition but not ready as written; `FABLE_HANDOFF_AUDIT.md` lists the blockers.

## Current repository facts that change the plan

1. The ICLR draft already exists at `paper_latex/ICLR_2027_submission/main.tex`. Revise it in place; do not port TMLR again.
2. `experiments/27_ti_plot_like_scatter_plots` is preserved on `main`; cert-judge PRs **#38** and **#40** are merged.
3. The repaired `brando90/ultimate-utils` PR **#44** is merged to `master`, and [release 0.10.9](https://pypi.org/project/ultimate-utils/0.10.9/) is public.
4. The repository `AGENTS.md` distinguishes PTI-v0 from the historical P1–P7/JTI pipeline; the frozen PTI-v0 specification remains authoritative.

## Execution order

### Step 1 — resolve the existing figure dependency

Review dependency PRs in this order:

1. `brando90/ultimate-utils#44`
2. `brando90/cert-judge#38`

Merge them only after review. If they remain open, the preflight must treat them as dependencies and must not recreate their code.

### Step 2 — run the zero-spend preflight

Open Codex in a clean checkout of `cert-judge`, select **GPT-5.6 Sol**, set effort to **max**, attach this directory, and paste:

`00-CODEX-SOL-MAX-PREFLIGHT.md`

The preflight produces `PREFLIGHT_PTI_V0_V4.md` and stops. It must not load keys, spend money, compute a bridge, or edit the paper.

### Step 3 — review the preflight

Proceed only if the report says `READY` or `READY AFTER FIXES` and the fixes are resolved. In particular, confirm:

- the alpha transform is real, semantics-preserving, and compiles;
- the 72→75 panel repair is evidence-backed;
- the exact alpha-only call count and cost;
- the current PR/branch topology;
- no structurally valid constant ladder is silently excluded.

Approve or decline the **alpha-only** inference spend. `RENAME`, `REORDER`, and `STYLE` are optional diagnostics with their own separately stated cost; they are not bundled into the alpha approval.

### Step 4 — run the implementation

Paste:

`01-CODEX-SOL-MAX-EXECUTE.md`

Recommended PR topology:

- PR A: `codex/pti-v0-final` — specification, panel repair, implementation, tests, experiment, outer bridge figure, results.
- PR B: `codex/iclr2027-final` — stacked on PR A; current ICLR manuscript revision only.

The existing Exp27 work remains PR #38 rather than becoming a third duplicate PR.

### Step 5 — independent Fable review

In a fresh Claude Code session using **Claude Fable 5**, check out the completed Codex branches and paste:

`02-FABLE-5-INDEPENDENT-REVIEW.md`

Fable should review and independently recompute; it should not inherit Codex's conclusions or silently edit the branch during the first pass.

### Step 6 — optional Codex Ultra mega-QA

After Fable's report is addressed, use GPT-5.6 Sol `ultra` for a final read-only multi-agent audit of statistics, software, figures, and manuscript. This is where `ultra` adds value.

## The frozen mathematical headline

For structurally valid bug/spec ladders, with increasing level meaning greater degradation:

\[
\widetilde s_{f,T,\ell}=\operatorname{median}_{r\in[K_{aj}]}s_{f,T,\ell,r},
\qquad
\rho_{f,T}=\operatorname{Spearman}(\ell,\widetilde s_{f,T,\ell}),
\qquad
C_{f,T}=\frac{1-\rho_{f,T}}{2}.
\]

If repeats exist,

\[
\sigma_{f,T}=\frac{1}{L_f+1}\sum_{\ell=0}^{L_f}2\operatorname{sd}_{r,\mathrm{ddof}=0}(s_{f,T,\ell,r}),
\qquad
\mu_{f,T}=\sqrt{C_{f,T}(1-\sigma_{f,T})}.
\]

For `K_aj=1`, `mu=C`, not `sqrt(C)`.

The PTI-v0 factors are

\[
P_{\mathrm{eq}},\quad P_{\mathrm{bm}},\quad P_{\mathrm{ms}},\quad P_{\mathrm{eq}\alpha},
\qquad
\mathrm{PTI}_{\mathrm{v0}}=\operatorname{GM}(P_{\mathrm{eq}},P_{\mathrm{bm}},P_{\mathrm{ms}},P_{\mathrm{eq}\alpha}).
\]

Every geometric mean is evaluated in log space with exact-zero preservation and no epsilon floor in the headline metric.
