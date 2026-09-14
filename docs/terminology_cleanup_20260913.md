# Terminology cleanup and paper rebuild record

**TLDR:** Replaced ambiguous scientific shorthand with the actual operation throughout all stored manuscript versions, paper notes, and active guidance. All 13 paper documents were rebuilt; numerical results, equations, citation keys, original figures, and frozen experimental evidence were preserved.

**Verified:** 2026-09-13 20:44 PDT

**Quality assurance verdict:** PASS for this wording-only scope. This is not a new scientific acceptance review or a new experiment.

**Published:** [Pull request 44](https://github.com/brando90/cert-judge/pull/44) merged at `17a49522bf2ffe2919b4438b4a38ec2401251488`; the canonical checkout was synchronized to that paper landing on 2026-09-13 20:48 PDT. The merged topic branch and owned worktree were removed.

## Wording decisions

| Context | Wording used |
|---|---|
| Human labels used to develop choices | Human-labeled development panel; trust-index selection |
| Association with artifact ratings | Human agreement; development-set evidence of human agreement |
| Behavioral tests of a judge | Property checks; behavioral screening |
| Selecting a pass/fail cutoff | Threshold selection; threshold sweep |
| Isotonic or other learned mapping | Fitted score mapping; monotone score mapping |
| Human reliance on a system | Appropriate reliance |

The property suite is linked to human agreement on the development panel. Selecting the index on development data remains distinct from fitting a mapping between score scales, and neither is presented as evidence of generalization by itself. Existing historical claims and numbers were not re-adjudicated in this edit.

## Verified scope

- All 23 changed existing TeX sources preserve 9,913 numerical tokens outside comments, mathematical expressions, citation keys, labels and cross-references. The exact per-file comparison counts are in the sibling machine-readable record.
- Every original figure path is preserved after expanding the two wording layers. Every tracked paper PNG image is byte-identical to the original revision. `overview_wording.tex` covers only three prose labels; `threshold_sweep_wording.tex` replaces only the plot title, retaining its stated 95% uncertainty level.
- All 13 builds exited 0. Final TeX logs contain no errors, missing characters, undefined citations or undefined references. Covers, poster pages, and changed diagram labels were visually inspected. Existing font-shape substitutions and box-spacing warnings are typesetting warnings, not new scientific findings.
- The oldest draft was missing four already-cited bibliography entries. `veribench_icml25`, `miranda2025veribench`, `uq2025` and `miranda2026formaloversight` were copied verbatim from `paper/neurips2026/refs.bib`; no citation command or external title was rewritten.
- Paper migration notes, change notes, the historical paper prompt and copied table prose were included in the wording pass. Their numerical values and split descriptions remain unchanged.
- No scoring implementation, tests, model configuration, raw data, archived experiment authority, or versioned experiment-30 run evidence changed. No inference, training, new labels or numerical rerun was performed.

## Rebuilt documents

| PDF (Portable Document Format) artifact | Pages | SHA-256 prefix |
|---|---:|---|
| [paper/neurips2026/main.pdf](../paper/neurips2026/main.pdf) | 32 | `d5c37d254b83` |
| [paper_latex/COLM_2026/00_colm2026.pdf](../paper_latex/COLM_2026/00_colm2026.pdf) | 26 | `efd30b9b6c51` |
| [paper_latex/ICLR_2027_submission/main.pdf](../paper_latex/ICLR_2027_submission/main.pdf) | 22 | `d1b86f1001fd` |
| [paper_latex/ICML_2026_AI4Math/main.pdf](../paper_latex/ICML_2026_AI4Math/main.pdf) | 22 | `94d141f8aec6` |
| [paper_latex/ICML_2026_AI4Math_poster/main.pdf](../paper_latex/ICML_2026_AI4Math_poster/main.pdf) | 1 | `1bb70d9d962a` |
| [paper_latex/ICML_2026_AI4Math_poster/main_visual.pdf](../paper_latex/ICML_2026_AI4Math_poster/main_visual.pdf) | 1 | `9c8ab0f20483` |
| [paper_latex/ICML_2026_DL4C/main.pdf](../paper_latex/ICML_2026_DL4C/main.pdf) | 21 | `fa8d8a732043` |
| [paper_latex/ICML_2026_Poster_Final/main.pdf](../paper_latex/ICML_2026_Poster_Final/main.pdf) | 1 | `7e9c935ed05e` |
| [paper_latex/NeurIPS_2025/mathai_neurips2025_template/neurips_2025.pdf](../paper_latex/NeurIPS_2025/mathai_neurips2025_template/neurips_2025.pdf) | 26 | `520ed23e5452` |
| [paper_latex/NeurIPS_2026/paper/neurips_2026.pdf](../paper_latex/NeurIPS_2026/paper/neurips_2026.pdf) | 36 | `4ceaba50314f` |
| [paper_latex/TMLR_2026/main.pdf](../paper_latex/TMLR_2026/main.pdf) | 29 | `e5f6c5f221a6` |
| [paper_latex/TMLR_2026_resubmission/main.pdf](../paper_latex/TMLR_2026_resubmission/main.pdf) | 30 | `4689dc146252` |
| [paper_latex/TMLR_2026_submission/main.pdf](../paper_latex/TMLR_2026_submission/main.pdf) | 29 | `a491282b0056` |

Full file hashes, source hashes, build exit codes and wording exceptions are in [the verification record](terminology_cleanup_20260913.json).

## Exact retained identifiers and records

The full manuscript/notes text scan leaves only literal provenance identifiers:

- `results_exp31_stacked_calibration/exp31_stacked_calibration_effect_sizes.csv` is printed in `paper/neurips2026/main.pdf`, page 22. It is the only extracted-PDF text match; it is a filename, not scientific shorthand.
- `figures/threshold_calibration_sweep/threshold_stability_curve.png` remains the underlying plot filename in the title wording layer. Its original raster title is covered in each rebuilt paper that uses it.
- `experiments/archive/23_reanchored_calibration/PREREG.md`, `experiments/archive/23_reanchored_calibration/results/results.json`, and `CALIBRATION_STATUS.md` remain literal provenance paths in source comments.
- The mathematical identifier `f_{\mathrm{cal}}` is unchanged. Compatibility identifiers such as `compute_calibration_gap`, `show_calibration_gap`, `exp12_split_calibration.py` and `results/split_calibration/` retain their names.
- The frozen numerical contract `docs/spec/PTI_V0.md`, original experiment overrides, dated handoff/audit records, archived experiment packets, and versioned experiment-30 protocols/reports retain their recorded wording. Current guidance supplies the precise terminology without rewriting their identity.
- No bibliographic title in the tracked bibliography files contains the retired term. External public copies were not edited.

## Build reproduction notes

Builds used Tectonic 0.16.9 with two concurrent document builds and a six-minute timeout per document. The working checkout was `/private/tmp/cj-terminology-20260913`; final files are published in the canonical `/Users/sanmikoyejo-mba-1/cert-judge` checkout.

From each paper directory, a temporary `_cj_build_<main>.tex` prepended the following compatibility declarations before `\input{<main>.tex}`:

```tex
\PassOptionsToPackage{dvipsnames}{xcolor}
\RequirePackage{newunicodechar}
\newunicodechar{’}{'}
\newunicodechar{“}{``}
\newunicodechar{”}{''}
\newunicodechar{–}{--}
\newunicodechar{—}{---}
\newunicodechar{‑}{\mbox{-}}
```

The build command was `tectonic -k --keep-logs --outdir <paper-dir>/_build/<main-stem> _cj_build_<main>.tex`; the successful output was copied to the ordinary PDF sibling, and the temporary wrapper removed. These declarations pass the existing color options before venue styles load them and render Unicode punctuation with the legacy fonts. They do not change the scientific source or replace missing references with placeholders.

The 2025 template loads Font Awesome without invoking any icon commands. Its local Tectonic build crashed while loading that unused package, so its build-only prelude additionally supplied `\expandafter\def\csname ver@fontawesome5.sty\endcsname{2026/09/13 unused-package build compatibility}`. The source package declaration remains intact.

The poster theme required Raleway and Lato fonts. Raleway was installed from the tracked `paper_latex/ICML_2026_Poster_Final/fonts/` files; Lato Light, LightItalic, Regular, Italic, Bold and BoldItalic came from the Google Fonts `ofl/lato` directory. Font Awesome 5 fonts were also checked during diagnosis; that installation did not resolve the unused-package crash.

The old `paper/neurips2026` source records `../../../experiments/...` paths although its current directory is two levels below the repository root. It was built in a temporary compatibility tree at `/private/tmp/cj-historical-build-layout/paper/legacy/neurips2026`, with source files linked from the checkout, `experiments` and `data` at the temporary root linked to the corresponding repository buckets, and `paper/paper_latex` linked to the shared wording-layer directory. This resolves the original recorded paths without renaming archived evidence. No temporary compatibility tree, fonts, logs or wrapper files are committed.
