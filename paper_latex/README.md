# Paper LaTeX Sources

| Submission | Main file |
|---|---|
| COLM 2026 | `COLM_2026/00_colm2026.tex` |
| ICML 2026 | `ICML_2026/main.tex` |
| NeurIPS 2025 | `NeurIPS_2025/mathai_neurips2025_template/neurips_2025.tex` |

Each paper directory contains a compiled **PDF committed to the repo** — no need to rebuild locally just to read the paper. To edit, rebuild with `latexmk -pdf <main_file.tex>` and commit the updated PDF.

## Overleaf-style workflow in Cursor

1. Install **MacTeX**: `brew install --cask mactex`
2. Install the **LaTeX Workshop** extension in Cursor
3. Open a `.tex` file — **save to compile**, `Cmd+Alt+V` to open PDF preview side-by-side

That's it. Edit → save → PDF updates automatically, just like Overleaf.

> **Tip:** If LaTeX Workshop doesn't find the root file, open the root `.tex` first or add `% !TEX root = main.tex` at the top of any sub-file.
