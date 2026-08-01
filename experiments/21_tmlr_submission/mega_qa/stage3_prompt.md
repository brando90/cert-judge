# MEGA QA Stage 3 (clean-eyes final pass) — revised Candidate B before TMLR resubmission

You are stage 3 of a Mega QA chain (stage 1 = Codex gpt-5.6-sol: `experiments/21_tmlr_submission/mega_qa/stage1_codex_report.md`; stage 2 = the building Claude session, which applied stage-1's blocker fixes). You are the fresh-eyes reviewer: assume NOTHING the earlier stages claim is true until you check it. Repo root: `/Users/brandomiranda/cert-judge`. Write your report to `experiments/21_tmlr_submission/mega_qa/stage3_report.md`, findings ranked most-severe-first.

Target: `paper_latex/TMLR_2026/main.tex` + `main.pdf` (29 pages) — the ONLY resubmission base. Do NOT touch `paper_latex/TMLR_2026_submission/` (frozen desk-rejected record) or `paper_latex/TMLR_2026_resubmission/` (deprecated candidate A′).

## Tasks

1. **EiC 3-minute triage simulation on the revised paper**: read title, abstract, and pages 1–2 as a skeptical TMLR Editor-in-Chief under extreme volume. Desk-reject or send to review? Be honest, not polite. The prior version was desk-rejected with the generic "unlikely to meet TMLR acceptance criteria" triage.
2. **Overclaim sweep**: stage 2 replaced "powered"/"adequate power"/"closes the question" and softened deployment promises ("amortizes"→"aims to amortize", "extends"→"is designed to extend", contribution 1 reframed). Search for ANY residual claim that (a) asserts amortized/label-free screening as achieved rather than tested, (b) asserts statistical power without a power analysis, (c) states the n=32 null as proof of no signal. Also check the NEW abstract and title (question-form) are consistent with the body.
3. **Numeric spot-check of stage-2 insertions**: the abstract/contribution/appendix now carry: trio 0.833/0.905/0.738; bootstrap CIs [0.24,1.00]/[0.41,1.00]/[0.11,1.00]; permutation p 0.017/0.005/0.045 (seed 42, 10k resamples); EXP46: strongest ρ=−0.3911 Holm p=0.2484, LOO ρ=+0.2416 p=0.4908, verdict (b); drift ρ≈0.13 n=63; pool ceiling 0.87, relabel 0.90; screens n=14 then n=32. Verify tex consistency everywhere these appear (no stale variants left), and verify the trio against `experiments/04_veribench_validation/results_exp28_varaware_codex_*/summary.json` (`rho_TI_vs_human`).
4. **Anonymity + compliance**: page 1 anonymous; no emails/author names/identifying URLs in body; unmodified tmlr.sty; no global layout overrides in the preamble; References start ≤ page 12 (verify the actual page).
5. **Rendering**: no broken figures/refs/overfull disasters in the PDF (check main.log + spot-view pages if you can).

You may fix mechanical defects directly (typos, stale numbers, missing labels) — recompile with `latexmk -g -pdf` if you edit. Do NOT change scientific framing, and do NOT resolve these OPEN items (they are Brando's decisions, listed for the record): 343-vs-345 label inclusion policy; author-list reconciliation; human-subjects form answer; the two % PROVENANCE-TODO tables (P4 rewrite table; downstream VeriBench table).

End the report with: SHIP / FIX-FIRST verdict for handing to Brando for his human read + co-author window.
