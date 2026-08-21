# PREFLIGHT PROMPT — Phase 0, no-spend, report-and-stop

Repository: `brando90/cert-judge`. Read `AGENTS.md`, then `AMENDMENTS-R41-R48.md`, then the
addendum and reconciliation. This run produces exactly one artifact —
`docs/PREFLIGHT_REPORT.md` on a branch `preflight-2026-08` — and then stops. **No API or
model calls, no bridge numbers, no property values on real data, no manuscript edits, no
other branches, no PRs beyond the single preflight-report PR (draft).** Every finding is
labeled DOCUMENTED (path) / DERIVED (command shown) / UNKNOWN.

Answer all of the following, verdict-first per item:

1. **Repo topology.** Current branch, HEAD, remote branches (confirm the `iclr2027-port`
   collision), presence/absence of `SYNC.md`, location and build status of
   `paper_latex/ICLR_2027_submission/main.tex` (compile it once; record the command and
   result), and the state of `TMLR_2026_resubmission/` (untouched baseline).
2. **α-transform validity (R41).** Locate `variant_generator.py` (and any successors).
   Reproduce its α output on ≥ 5 real artifacts; for each, report
   `(changed?, compiles/elaborates?, error, binder-occurrence-consistency?)`. Confirm or
   refute: the `:=:=` defect, signature-only renaming, and the comment-append fallback.
   Determine **which generator version produced the cached ALPHA/RENAME/REORDER/STYLE
   variants** behind the workshop self-pair numbers (0.399 etc.), and whether those cached
   variants compile — this decides whether the paper's standing ALPHA failure mode is clean
   or contaminated. Do the same spot-validation for 5 bug ladders and 5 spec ladders
   (diff-nonempty per rung, compiles, genuine cumulative degradation) per R47.4.
3. **Label repair scope (R42).** Reproduce the audit: which avg rows fail
   avg = (strict+lenient)/2, which keys are stale, where the lenient duplicates are, and
   exactly which files/scripts consume the precomputed avg TSV. Output the precise repair
   diff plan (no repairs executed in this phase).
4. **Cache coverage.** Per judge × probe family: what exists on disk (paths, counts, repeat
   depth), including `experiments/27_ti_plot_like_scatter_plots` contents; whether eq/bm/ms
   are fully computable from cache; whether ANY transformed-vs-gold scores exist.
5. **Split cost sheet (R48.1).** α-only missing-call count and price; rename/reorder/style
   diagnostics as a separate line; cite the price source; charge only missing
   transformed-vs-gold calls. No purchase.
6. **Judge manifest draft.** The 8-configuration panel with roles per Table-10 conventions;
   whether panel scores exist for the expanded 13.
7. **Statistical pins check (R47).** Confirm the bootstrap and SESOI-DGP policies are
   implementable as pinned; report expected invalid-resample modes at n = 8 with ties.
8. **Bridge-figure inputs.** What per-judge criterion values 27 already caches (and whether
   they are TI_2'-decomposed or plain), for the R45-corrected figure.
9. **Blockers list.** Anything that would trip a HARD gate in Phase 1, each with the
   smallest fix.

End the report with a GO / NO-GO recommendation per phase and the exact human decisions
required (expected: the α validity/funding decision and the Phase-1 review). Then stop.

---
END OF AGENT INSTRUCTIONS

```
TL;DR (for the human reader; the agent should ignore this block):
The no-spend reconnaissance run: verify the repo facts the plan now depends on (branch
collisions, missing SYNC.md, the existing ICLR draft and whether it builds), reproduce
the α-generator defects and check whether the workshop's ALPHA-0.399 result was computed
on broken probes, map the exact 75-item label repair, inventory the cache, price the
α-only run separately from the diagnostics, and hand back one report with GO/NO-GO per
phase — touching no money, no bridge numbers, and no paper.
```
