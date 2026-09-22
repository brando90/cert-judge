#!/usr/bin/env python3
"""Extract the abstract of the ICLR 2027 main.tex as plain text for the OpenReview form.

TLDR: OpenReview strips \\(...\\) math and renders only $...$; internal references such as
"Section 5" or "Appendix G" are meaningless on the landing page (the TMLR 2026 desk reject
was triggered partly by exactly this). This script converts the LaTeX abstract to the plain
text the form needs and warns about any leftover LaTeX or internal reference.

Usage: python3 make_openreview_form_abstract.py [path/to/main.tex] > openreview_form_abstract.txt
"""
import re
import sys
from pathlib import Path

TEX = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / 'paper_latex/ICLR_2027_submission/main.tex'


def main() -> int:
    src = TEX.read_text(encoding='utf-8')
    m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', src, re.S)
    if not m:
        sys.stderr.write('no abstract environment found\n')
        return 1
    lines = []
    for raw in m.group(1).splitlines():
        line = re.sub(r'(?<!\\)%.*$', '', raw).strip()  # drop comments
        if line:
            lines.append(line)
    text = ' '.join(lines)
    # LaTeX -> plain text (order matters)
    text = re.sub(r'\\\((.*?)\\\)', lambda mm: '$' + mm.group(1) + '$', text)
    text = re.sub(r'\\mathrm\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\(?:textsc|emph|textbf|textit|text)\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\cite[tp]?\*?(?:\[[^\]]*\])*\{[^}]*\}', '', text)
    text = text.replace('~', ' ').replace('\\%', '%').replace('``', '"').replace("''", '"')
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\s+([,.;:])', r'\1', text)
    sys.stdout.write(text + '\n')
    warnings = []
    if re.search(r'\\[A-Za-z]+', text):
        warnings.append('leftover LaTeX command: ' + ', '.join(sorted(set(re.findall(r'\\[A-Za-z]+', text)))))
    if re.search(r'\b(Section|Appendix|Table|Figure|Sec\.|App\.)\s*\d|\\ref', text):
        warnings.append('internal reference in the abstract (remove it for the form)')
    if '\\(' in text or '\\)' in text:
        warnings.append('\\( \\) delimiters remain; OpenReview drops them')
    for w in warnings:
        sys.stderr.write('WARNING: ' + w + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
