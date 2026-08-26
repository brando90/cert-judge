# CertJudge PTI-v0 v4 overrides — R41–R49

These rulings supersede conflicting language in the Fable v2/v3 handoff. All non-conflicting PTI-v0 numerical decisions remain in force.

## R41 — Builder and reviewer roles

- Primary builder: GPT-5.6 Sol, reasoning `max`.
- Independent reviewer: Claude Fable 5 in a fresh session.
- Optional final mega-QA: GPT-5.6 Sol `ultra`, read-only first.
- `ultra` is not the primary writer because implementation, experiment freezing, and manuscript updates are sequential and share state.

## R42 — Repository topology and Exp27

- `paper_latex/ICLR_2027_submission/main.tex` is the active manuscript and is revised in place.
- `experiments/27_ti_plot_like_scatter_plots` is existing work on cert-judge PR #38.
- PR #38 depends on ultimate-utils PR #44.
- Review dependency order: #44, then #38.
- Do not duplicate, relocate, or silently rewrite Exp27.
- Exp27 is the inner item-level `TI_2'` diagnostic. The new PTI-v0 bridge is the outer judge-level figure.

## R43 — Structural probe validity versus constant judge behavior

A probe is excluded globally only if its construction is objectively invalid independently of judge outputs, including:

- no-op or duplicate artifacts;
- malformed or misordered ladders;
- failed Lean parsing, compilation, or elaboration when the probe contract requires it;
- missing files or a documented transformation failure;
- a base/transformed pair that is not the intended semantic relation.

After structural validation, a constant median score ladder is a judge failure:

\[
\widetilde s_{f,T,0}=\cdots=\widetilde s_{f,T,L_f}
\quad\Longrightarrow\quad
C_{f,T}=0.
\]

Do not estimate an undefined Spearman value and do not exclude the ladder. Report `constant_score_ladder=True` and the per-judge fraction.

Coverage failure is distinct. If required scores are missing or unparsable beyond a pre-frozen coverage threshold, mark the property `NOT_COMPUTABLE` and the screen `DEFER`; never substitute zero.

## R44 — Bridge scale semantics

The raw human criterion is

\[
\mathrm{TI}_{m_1}(aj)=\operatorname{Spearman}_{i\in I}(\widetilde s_{aj,i},s^*_{H,i})\in[-1,1].
\]

The outer bridge asks whether PTI ranks judges similarly:

\[
\widehat\rho_{\mathrm{bridge}}
=\operatorname{Spearman}_{aj\in AJ_{\mathrm{test}}}
(\mathrm{PTI}_{\mathrm{v0}}(aj),\mathrm{TI}_{m_1}(aj)).
\]

Because the axes are not a common calibrated level scale:

- no `y=x` line;
- no `mean |PTI-TI_m1|`;
- no “distance to perfect level agreement” language.

Report Spearman, Kendall tau-b, bootstrap CI over judges, number of judges, and role/family sensitivity analyses.

## R45 — Alpha-only spend gate

The headline fourth property uses alpha-renaming only:

\[
P_{\mathrm{eq}\alpha}
=\operatorname{GM}_f\left(1-|\widetilde s_f^{\mathrm{orig}}-\widetilde s_f^{\alpha}|\right).
\]

Before any paid run:

1. prove the transform changes the intended binders and all bound occurrences consistently;
2. compile/elaborate transformed artifacts;
3. inventory cached original and alpha scores;
4. quote missing alpha-only calls and cost.

`RENAME`, `REORDER`, and `STYLE` remain diagnostics. Quote them separately; do not include them in the alpha approval.

If alpha is declined or structurally blocked, the pre-declared headline is the labeled three-property proxy
`PTI_{eq,bm,ms}`; never silently call it four-property PTI-v0.

## R46 — Panel repair is evidence-driven

The 72→75 repair is permitted only after verifying that the three stale `0_unsafeMultiply_safe` keys map to the intended `1_unsafeMultiply_safe` gold and preserve the three agent generations. Reconstruct strict, lenient, and average views deterministically; do not edit labels merely to hit 75.

Commit an audit manifest with old key, new key, content/hash evidence, affected rows, duplicate policy, and before/after statistics.

## R47 — Claim language

Do not state that P1–P4 are unconditionally necessary for a merely correlational criterion.

Approved language:

- “pre-specified falsifiable behavioral diagnostics”; or
- “behavioral requirements under our scoped operational definition”; or
- “conditional falsification tests under the stated metamorphic-validity and margin assumptions.”

Passing PTI is a screen result, not proof of trustworthiness. Low PTI is logically disqualifying only under Route A or the explicit assumptions of Route B.

## R48 — Branch and PR plan

After dependencies are resolved:

1. `codex/pti-v0-final` from updated `main`: spec, implementation, tests, panel audit, experiment, outer bridge figure, results.
2. `codex/iclr2027-final` stacked on PR 1: manuscript and paper-only assets.

Do not recreate an `iclr2027-port` branch. Do not create a separate bridge PR unless a real review boundary requires it. Do not push to `main` or merge PRs automatically.

## R49 — Project guidance refresh

Load the global `agents-config` rules first. Then update stale project-level descriptions in `AGENTS.md` and `CLAUDE.md` so they distinguish:

- construct: `TW_m`;
- human criterion: `TI_m`;
- proxy instrument: `PTI_p` / `PTI_v0`;
- legacy JTI/TIvar pipelines as historical compatibility code.

Preserve correct environment, testing, secret, and Git safety instructions.
