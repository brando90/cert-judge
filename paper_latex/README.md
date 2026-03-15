# Paper LaTeX Sources

This directory contains LaTeX source files for two versions of the paper.

## Directory Structure

```
paper_latex/
├── ICML_2026/                          # ICML 2026 submission
│   ├── main.tex                        # Main document
│   ├── refs.bib                        # Bibliography
│   ├── icml2025.sty                    # ICML style file
│   ├── icml2025.bst                    # ICML bibliography style
│   ├── algorithm.sty / algorithmic.sty # Algorithm packages
│   ├── fancyhdr.sty                    # Header/footer style
│   ├── sections/                       # Section files (abstract, methodology, appendix)
│   └── figures/                        # Paper figures
│
├── NeurIPS_2025/                       # NeurIPS 2025 submission
│   ├── mathai_neurips2025_template/
│   │   ├── neurips_2025.tex            # Main document
│   │   ├── neurips_2025.sty            # NeurIPS style file
│   │   └── refs.bib                    # Bibliography
│   └── figures/                        # Paper figures
│
├── Certifying_LLM_Judges__ICML_2026_.zip
└── VeriBench_Certifying_LLM_Judge__NeurIPS_2025_.zip
```

## Compiling PDFs

### Prerequisites

Install a LaTeX distribution if you don't have one:

- **macOS**: [MacTeX](https://www.tug.org/mactex/) — `brew install --cask mactex`
- **Linux**: `sudo apt install texlive-full` (Debian/Ubuntu)

Verify installation: `pdflatex --version`

---

### ICML 2026

```bash
cd paper_latex/ICML_2026

# Full build (runs BibTeX for references)
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Output: main.pdf
```

---

### NeurIPS 2025

```bash
cd paper_latex/NeurIPS_2025/mathai_neurips2025_template

# Full build (runs BibTeX for references)
pdflatex neurips_2025.tex
bibtex neurips_2025
pdflatex neurips_2025.tex
pdflatex neurips_2025.tex

# Output: neurips_2025.pdf
```

---

### One-liner builds (from paper_latex root)

```bash
# ICML 2026
(cd ICML_2026 && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex)

# NeurIPS 2025
(cd NeurIPS_2025/mathai_neurips2025_template && pdflatex neurips_2025.tex && bibtex neurips_2025 && pdflatex neurips_2025.tex && pdflatex neurips_2025.tex)
```

---

### Using `latexmk` (recommended — handles reruns automatically)

```bash
# ICML 2026
cd paper_latex/ICML_2026
latexmk -pdf main.tex

# NeurIPS 2025
cd paper_latex/NeurIPS_2025/mathai_neurips2025_template
latexmk -pdf neurips_2025.tex

# Clean auxiliary files after build
latexmk -c
```

Install latexmk if needed: `brew install latexmk` or it is included with most TeX distributions.
