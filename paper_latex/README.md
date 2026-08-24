# Paper LaTeX Sources

| Submission | Main file |
|---|---|
| COLM 2026 | `COLM_2026/00_colm2026.tex` |
| ICML 2026 | `ICML_2026/main.tex` |
| NeurIPS 2025 | `NeurIPS_2025/mathai_neurips2025_template/neurips_2025.tex` |
| Trustworthy Notes (ICLR 2027 shell, not a submission) | `TrustWorthy_Notes/main.tex` |

Each paper directory contains a compiled **PDF committed to the repo** — no need to rebuild locally just to read the paper. To edit, save the `.tex` (LaTeX Workshop recompiles) or run `tectonic --keep-logs <main_file.tex>`.

## Overleaf-style workflow in Cursor

This Mac has **tectonic**, not MacTeX (`pdflatex` / `latexmk` are missing). Cursor does not compile LaTeX by itself.

1. Install the **LaTeX Workshop** extension (`James-Yu.latex-workshop`)
2. Use the `tectonic` recipe (set in user settings and `bm-cert-judge.code-workspace`)
3. Open the root `.tex` — **save to compile**, `Cmd+Alt+V` to open the PDF beside the source

That's it. Edit → save → PDF updates automatically, just like Overleaf.

> **Tip:** If LaTeX Workshop doesn't find the root file, open the root `.tex` first or add `% !TEX root = main.tex` at the top of any sub-file. After installing the extension, reload the window once (`Cmd+Shift+P` → Developer: Reload Window).
