# TODO Before Submission
- [ ] Add held-out test result (frozen protocol, no retuning)
- [ ] Add second annotator / frozen R2 labels and inter-annotator report
- [ ] Add compute accounting (hardware, wall-clock, API calls, approximate cost)
- [ ] Add license/accounting table (VeriBench, Lean/Mathlib, model/API terms)
- [ ] Final anonymized code/data release package with exact reproduction commands

## What Was Migrated (2025 -> 2026 canonical)
- Kept NeurIPS 2026 template as canonical base and created a clean canonical directory: `paper/neurips2026/`.
- Preserved and reused 2026 framing around amortized validation and validation-vs-test distinction.
- Restored/kept core P1-P4 protocol and primary JTI-v1 framing in the main narrative.
- Added/retained key evidence blocks:
  - Exp16 validation-set trend (JTI-v1 -> human alignment)
  - Exp17 property decomposition
  - Cross-pass no-overfitting check (explicitly labeled as calibration-side robustness)
  - Robustness material (Opus + expanded panel) framed as robustness/ablation, not primary claim.
- Added explicit judge-unit definition (model + prompt/rubric + repeats + aggregation + threshold).
- Added explicit 8-judge panel table with judge roles.
- Added explicit falsifiability paragraph (what would falsify the calibration hypothesis).

## What Was Deleted / Compressed
- Removed date-based section titles from the main body.
- Compressed chronological “lab log” flow into argument-driven sections.
- Kept index variants out of primary claim language; primary claim now centered on JTI-v1.
- Marked non-primary index behavior as legacy/ablation where still referenced by existing figures.

## What Remains TODO (Substantive)
- Freeze and run held-out test protocol (independent annotator(s), unseen judge family/items).
- Normalize all main-text results to one primary index in all sections/figures; move all variants fully to appendix.
- Finish compute + license checklist details in paper/checklist.
- Add final anonymized reproducibility appendix with exact commands and model API settings.

## Validation-Only Claims (Current Main Paper)
- Main reported alignment numbers are validation-set evidence.
- Cross-pass results are anti-overfitting checks, not final out-of-sample proof.
- No broad generalization claim is made until held-out test results are added.

## Canonical Paths
- Canonical paper source: `paper/neurips2026/main.tex`
- Canonical bibliography: `paper/neurips2026/refs.bib`
- Canonical style/checklist: `paper/neurips2026/neurips_2026.sty`, `paper/neurips2026/checklist.tex`
- Figure directory symlink: `paper/neurips2026/figures` -> `paper_latex/NeurIPS_2026/paper/figures`

## Branch
- Working branch created: `paper-neurips2026-clean-migration`
- Note: requested slash branch name `paper/neurips2026-clean-migration` could not be created in this environment due ref-lock constraints.
