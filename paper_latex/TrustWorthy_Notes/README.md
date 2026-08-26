# Trustworthy Notes (ICLR 2027 shell)

**TLDR:** ICLR 2027 notes draft for the Trust Index. `main.tex` has a notation table, TW/TI/PTI definitions, then a section on preference vs the scoring target. This is not a submission.

## Files

| File | Role |
|---|---|
| `main.tex` | Empty notes document (start writing here) |
| `iclr2027_conference.sty` / `.bst` | Official ICLR 2027 style |
| `iclr2027_conference.bib` | Empty bibliography |
| `math_commands.tex` | Optional Deep Learning Book notation |

## Compile

```bash
cd paper_latex/TrustWorthy_Notes
tectonic --keep-logs --outdir _build main.tex
# or, if MacTeX is installed:
latexmk -pdf -interaction=nonstopmode main.tex
```

PDF: `_build/main.pdf` (and a copy at `main.pdf`). In Cursor: open `main.tex`, save to compile, `Cmd+Alt+V` for PDF preview. Empty bibliography is expected until you add `\citep{...}` entries.
