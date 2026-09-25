> **Superseded 2026-09-22:** this file describes the 09-17 verbatim port. The paper has since been rewritten for ICLR
> (abstract, intro, §4–§6, §5.4 removed); consult `git log -- paper_latex/ICLR_2027_submission/` and
> `experiments/archive/31_final_iclr_paper_writing/notes.md` instead.

# CHANGES — ICLR 2027 submission = the accepted ICML 2026 DL4C paper, reformatted

**TLDR:** `paper_latex/ICLR_2027_submission/main.tex` is now a verbatim content port of the accepted
ICML 2026 DL4C workshop paper (`paper_latex/ICML_2026_DL4C/main.tex`, *"Certifying the Judge:
Falsifiable Properties for LLM-Based Evaluation of Formal Code"*) wrapped in the ICLR 2027
single-column double-blind style. No scientific claim, number, table, figure, or appendix section
was added, removed, or reworded. The previous ICLR draft (*"The Surrogate Gap …"*, PTI-v0 /
Experiment-29 negative result) is **not** deleted — it is preserved byte-for-byte at
`paper_latex/archive/ICLR_2027_submission_old_09162026/`.

## Why

The ICML DL4C paper is the accepted result; the ICLR 2027 submission is its resubmission. The
active tree previously held an unrelated manuscript (the PTI-v0 surrogate-gap negative), so the
active paper did not match the intended submission.

## Content authority

- **Source of truth:** `paper_latex/ICML_2026_DL4C/main.tex`
- **Ported region:** everything after `\printAffiliationsAndNotice{}` — abstract, §1–§7, bibliography
  call, and appendices A–G. Body line count is identical: 1372 lines in, 1372 lines out.
- Historical P1–P4 / `TI_var` framing is retained **as-is**. Per `CLAUDE.md`, these outputs are
  *not* PTI-v0 and are not relabeled as such anywhere in this port.

## Complete diff of the ported body (26 hunks, verified line by line)

Format-only (24 hunks):

| Change | Count | Reason |
| --- | --- | --- |
| `\begin{figure*}` / `\end{figure*}` → `figure` | 9 pairs (1 commented) | ICLR 2027 is single column; two-column floats do not exist |
| `\columnwidth` → `\linewidth` | 7 | identical in one column; portable name |
| `title={\parbox{\linewidth}{\centering …}}` → `title={…}` | 3 | the full-width parbox title overhung the pgfplots axis box; this was the source of the 3 overfull hboxes inherited from the ICML build |
| `\bibliographystyle{icml2025}` → `{iclr2027_conference}` | 1 | ICLR author-year `.bst` |

Prose (2 hunks, both venue-wrapper corrections, no claim changed):

1. `a core \emph{DL4C} bottleneck` → `a core deep-learning-for-code bottleneck` — the workshop
   acronym named the other venue inside an ICLR submission. Meaning unchanged.
2. `Section~5.3` → `Section~\ref{sec:validation-human-alignment}` — the hard-coded number happens to
   resolve identically under ICLR numbering, but the `\ref` cannot drift.

## Preamble (rewritten, not ported)

`\usepackage[accepted]{icml2026}` → `\PassOptionsToPackage{dvipsnames}{xcolor}` +
`\usepackage{iclr2027_conference,times}`. The `\twocolumn[ \icmltitle … \icmlauthorlist … ]` block
and `\printAffiliationsAndNotice{}` were replaced by `\title` / `\author` / `\maketitle`;
`\icmltitlerunning` and the `\ICML@appearing` copyright override were dropped. `natbib` is loaded by
the ICLR style file, so it is not loaded again. Every other ICML package line was carried over
verbatim (amsmath family, graphicx/subcaption/float/booktabs/adjustbox/arydshln, listings with the
same `promptstyle`, tikz/pgfplots at `compat=1.18`); `url`/`hyperref` + `darkblue` link colors follow
the ICLR convention.

**Anonymity.** `\iclrfinalcopy` is commented out, so `iclr2027_conference.sty` prints
"Anonymous authors / Paper under double-blind review". The real ICML author list (9 authors,
Stanford + Harvard, equal-contribution mark on Hersch and Miranda) sits in the `\author{}` block and
appears only when `\iclrfinalcopy` is uncommented for camera-ready.

## Build verification

```bash
cd paper_latex/ICLR_2027_submission
SOURCE_DATE_EPOCH=1758067200 FORCE_SOURCE_DATE=1 TZ=UTC \
  latexmk -g -pdf -interaction=nonstopmode -file-line-error main.tex
```

Clean build from a wiped `main.aux`/`main.bbl`:

| Check | Result |
| --- | --- |
| TeX errors | **0** |
| Overfull `\hbox` | **0** (ICML build had 6) |
| Overfull `\vbox` | **0** |
| Undefined references / citations | **0** |
| BibTeX warnings | **0** |
| Total pages | 28 |
| Figures / tables / bib entries | 14 / 12 / 40 |

All 22 `\includegraphics` calls (21 distinct files) already resolved under `ICLR_2027_submission/figures/`; no figure
file was copied, moved, or regenerated.

The stale `ICML_2026_DL4C/main.bbl` (dated 2026-05-27) still cites a dropped
`anonymous2026veribench` key. The regenerated ICLR `.bbl` reflects the *current* `main.tex`, which
cites `miranda2026veribench`; that is why the ICLR bibliography has one fewer entry.

## Page budget — ACTION REQUIRED

| Region | Pages |
| --- | --- |
| Main text (§1 Introduction → §7 Conclusion) | **1–11** |
| References (uncounted) | 11–12 |
| Appendix A–G (uncounted) | 13–28 |

ICLR counts main text only. An 11-page main text **exceeds the 9-page ICLR limit by ~2 pages** — the
expected consequence of moving a workshop-length two-column paper into the wider single-column
measure while keeping every word. Trimming is a content decision and was deliberately *not* done
here. Re-check after any edit:

```bash
python3 -c "from pypdf import PdfReader; r=PdfReader('main.pdf'); \
print('Conclusion on page(s):', [i+1 for i,p in enumerate(r.pages) \
if 'CONCLUSION' in (p.extract_text() or '').upper().replace(' ','')])"
```

(The space-stripping matters: the ICLR style sets headings in small caps, so raw extraction yields
`7 C ONCLUSION`.) Current output: `[11]`.

## Not added (ICLR-format items still open)

No Ethics Statement, Reproducibility Statement, or LLM-usage statement was written. The ICML paper
has none, and authoring them requires facts about the authors' own tooling and process that are not
recoverable from the repository — so nothing was fabricated. Versions written for the superseded
draft exist at `paper_latex/archive/ICLR_2027_submission_old_09162026/main.tex` but describe the
PTI-v0 experiment, not this one, and must not be pasted across unmodified.

## Known issues inherited verbatim from the accepted ICML paper

- Appendix E prose says "Figures A.1–A.3"; under ICLR numbering these are Appendix F figures.
  Left unchanged because picking the right `\ref` targets is a content judgment, not a format fix.
- The `TI_var` display equation still carries the two-line `aligned` break that was needed for the
  narrow ICML column. It typesets correctly, just loosely, in the wider ICLR measure.
