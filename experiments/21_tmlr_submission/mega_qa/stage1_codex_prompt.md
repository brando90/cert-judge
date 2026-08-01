# MEGA QA Stage 1 (Codex gpt-5.6-sol xhigh) — TMLR desk-reject postmortem + resubmission audit

You are stage 1 of a 3-stage Mega QA chain (Codex → Claude Code → Antigravity). Work from repo root `/Users/brandomiranda/cert-judge`. You have authority to FIX files directly (except: never touch `paper_latex/TMLR_2026_submission/` — that is the frozen submitted record). Write your full report to `experiments/21_tmlr_submission/mega_qa/stage1_codex_report.md`.

## Ground truth (verified facts — do not re-litigate, but flag if you find contradicting evidence)

- TMLR submission 10994 (`paper_latex/TMLR_2026_submission/main.pdf`) was desk-rejected 31 Jul 2026 by the Editors-in-Chief with the generic triage comment: "A preliminary assessment indicates that this paper is unlikely to meet the TMLR acceptance criteria. Some reasons may include insufficient evidence to support the claims made, the quality of writing may not be up to the standards of TMLR, or limited interest within the TMLR audience. Due to extremely limited reviewer capacity, we are unable to send this submission for full review."
- Ruled out with evidence: anonymity (PDF page 1 anonymous), stylefile (tmlr.sty byte-identical to official JmlrOrg file), main-content length (ends p.11 ≤ 12), overlap (not cited; TMLR policy permits non-archival workshop overlap; AI4Math is non-archival), quota (not cited).
- Known contributor: the OpenReview **abstract form field** rendered with `\(\mathrm{TI}_{\mathrm{var}}\)` stripped (OpenReview needs `$...$`), so it reads "a variance-aware trust index, , which provides..." — plus internal refs "(Appendix G)", "(Section 5.1)" in the standalone abstract. The triage-facing landing page looked broken.
- Hypothesis to assess: the abstract/paper reads at skim as "n=8 validation correlations + held-out test failed" → triage-kill under 2026 volume pressure.

## Your tasks

1. **Postmortem verification**: Re-verify the ruled-out causes yourself (read `paper_latex/TMLR_2026_submission/main.tex` + PDF structure). Report anything additionally desk-reject-relevant we missed (e.g., anonymity leaks in bibliography/self-citations, metadata, broken rendering, figure quality).
2. **EiC triage simulation** — the core task. Act as a maximally skeptical TMLR Editor-in-Chief with 3 minutes per paper, on BOTH candidates:
   - Candidate A′: `paper_latex/TMLR_2026_resubmission/main.tex` (submitted version + format overrides removed + new title + differentiated abstract opening).
   - Candidate B: `paper_latex/TMLR_2026/main.tex` (full rewrite: measurement-instrument framing, audit narrative, pre-registered negative as headline contribution).
   For each: would you desk-reject under "unlikely to meet TMLR criteria"? Why, concretely — first-page impressions, claim-evidence coherence at skim, audience-interest case. Verdict + top-5 fixes each.
3. **Claims-vs-artifacts audit of candidate B** (it is the likely resubmission base but no human has read it): B's tex has `% source:` comments naming artifact files. Spot-verify AT LEAST the 10 highest-stakes numeric claims against the named artifacts in `experiments/` (also see `experiments/21_tmlr_submission/evidence_map.md`). Report per claim: CONFIRMED / MISMATCH (with both values) / ARTIFACT-MISSING. Known-good anchors you can calibrate against: abstract trio 0.833/0.905/0.738 ← `experiments/04_veribench_validation/results_exp28_varaware_codex_*/summary.json` field `rho_TI_vs_human`; cross-protocol drift ρ=0.1314 n=63 (recomputed 2026-08-01 from raw TSVs); EXP46 screen: strongest |ρ|=0.3911 Holm 0.2484, LOO 0.2416 p 0.4908, verdict "b" ← `experiments/24_expanded_panel_cli/results/pass2_full_screen_results.json`.
4. **Form-field kit review**: `experiments/21_tmlr_submission/resubmission_kit.md` (if present) — check the plain-text abstract has NO LaTeX `\(...\)`, no internal section/appendix refs, and matches the paper's claims.
5. **Fixes**: apply safe mechanical fixes directly (typos, broken refs, form-kit text). For judgment calls (framing, claims), list them as recommendations — do NOT rewrite scientific content.

Rank everything most-severe-first. Be adversarial; the last QA that mattered here was the one that caught a fabricated number (+0.055 → −0.642). End the report with: verdict on which candidate to resubmit (A′ / B / neither-fix-first) + the minimal fix list to survive EiC triage.
