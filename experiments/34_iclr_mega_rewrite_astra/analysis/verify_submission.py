#!/usr/bin/env python3
"""Check the built active manuscript without inference or network access."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / 'paper_latex/ICLR_2027_submission'
OUT = Path(__file__).resolve().parent / 'results'


def run(args, cwd=ROOT):
    return subprocess.check_output(args, cwd=cwd, text=True)


def uncomment(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


def main():
    build_command = ['latexmk', '-pdf', '-interaction=nonstopmode', 'main.tex']
    build = subprocess.run(build_command, cwd=PAPER, capture_output=True, text=True)
    (OUT / 'latexmk_receipt.txt').write_text((build.stdout + build.stderr).rstrip() + '\n')
    assert build.returncode == 0, 'latexmk failed; inspect latexmk_receipt.txt'
    source = (PAPER / 'main.tex').read_text()
    inputs = re.findall(r'\\input\{([^}]+)\}', source)
    files = [PAPER / (name + '.tex') for name in inputs]
    texts = {p.name: uncomment(p.read_text()) for p in files}
    active = '\n'.join(texts.values())
    main_text = '\n'.join(texts[p.name] for p in files if p.name[:2] in [f'{i:02d}' for i in range(8)])
    labels = re.findall(r'\\label\{([^}]+)\}', active)
    refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', active)
    missing_refs = sorted(set(refs) - set(labels))
    duplicate_labels = sorted({x for x in labels if labels.count(x) > 1})
    bibliography = (PAPER / 'refs.bib').read_text()
    bibkeys = re.findall(r'@\w+\s*\{\s*([^,]+),', bibliography)
    cites = [key.strip() for block in re.findall(r'\\cite\w*(?:\[[^\]]*\])*\{([^}]+)\}', active) for key in block.split(',')]
    missing_cites = sorted(set(cites) - set(bibkeys))
    uncited_bib = sorted(set(bibkeys) - set(cites))
    figures = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', active)
    missing_figures = [f for f in figures if not (PAPER / f).is_file()]
    archive_references = [x for x in inputs + figures if x.startswith('archive/')]
    appendix_reachability = {}
    for p in files:
        if not p.name.startswith('99'):
            continue
        section_label = re.search(r'\\section\{[^\n]+?\\label\{([^}]+)\}', texts[p.name])
        if not section_label:
            raise AssertionError('Appendix has no section label: ' + p.name)
        label = section_label.group(1)
        appendix_reachability[p.name] = label in re.findall(r'\\ref\{([^}]+)\}', main_text)
    forbidden = re.findall(r'(?i)calibrat\w*|development\s+(?:set|panel)|\bdev\s+set|DSPy|Trace\+|Claude\s+3\.7|\bPTI(?:[-_\s]|$)|predict\w*', active)
    log = (PAPER / 'main.log').read_text(errors='replace')
    blg = (PAPER / 'main.blg').read_text(errors='replace')
    log_errors = [line for line in log.splitlines() if re.search(r'^!|undefined|Overfull|LaTeX Warning|Package .* Warning', line)]
    bib_warnings = [line for line in blg.splitlines() if re.search(r'Warning--|I couldn.t open|error message', line)]
    run(['python3', str(Path.home() / 'agents-config/scripts/latex_sentence_lines.py'), '--check', *[str(p) for p in sorted(PAPER.glob('*.tex'))]])
    pdf_text = run(['pdftotext', '-layout', str(PAPER / 'main.pdf'), '-'])
    pages = pdf_text.split('\f')
    if not pages[-1].strip():
        pages.pop()
    def page_of(pattern):
        return next(i + 1 for i, page in enumerate(pages) if re.search(pattern, page, re.I | re.M))
    statements_page = page_of(r'R\s*EPRODUCIBILITY\s+S\s*TATEMENT')
    references_page = page_of(r'^\s*R\s*EFERENCES\s*$',)
    conclusion_page = page_of(r'\b7\s+C\s*ONCLUSION')
    abstract_generated = run(['python3', 'experiments/33b_or_ledger/make_openreview_form_abstract.py'])
    abstract_saved = (ROOT / 'experiments/33b_or_ledger/openreview_form_abstract.txt').read_text()
    assert abstract_generated == abstract_saved
    assert '\\(' not in abstract_saved and '\\ref' not in abstract_saved
    # Archived sources and inherited figures preserve the bytes from the pre-rewrite commit.
    archive_checks = {}
    prefix = 'paper_latex/ICLR_2027_submission/'
    for p in sorted((PAPER / 'archive').rglob('*')):
        if not p.is_file() or p.name in ['README.md', 'figure_moves.json', '.gitattributes']:
            continue
        old_path = prefix + str(p.relative_to(PAPER / 'archive'))
        frozen = subprocess.check_output(['git', 'show', '8d2e005:' + old_path], cwd=ROOT)
        archive_checks[str(p.relative_to(PAPER))] = p.read_bytes() == frozen
    result = {
        'build_command': ' '.join(build_command), 'build_cwd': str(PAPER),
        'latexmk_exit_code': build.returncode,
        'active_inputs': inputs, 'missing_references': missing_refs,
        'duplicate_labels': duplicate_labels, 'missing_citations': missing_cites,
        'uncited_bibliography_entries': uncited_bib, 'missing_figures': missing_figures,
        'archive_references': archive_references, 'appendix_main_text_links': appendix_reachability,
        'forbidden_word_matches': forbidden, 'latex_errors_or_warnings': log_errors,
        'bibtex_warnings': bib_warnings, 'sentence_layout': 'PASS (all top-level .tex files)',
        'openreview_abstract_matches': True,
        'pdf_total_pages': len(pages), 'conclusion_page': conclusion_page,
        'main_text_pages': statements_page - 1, 'statements_start_page': statements_page,
        'references_start_page': references_page,
        'archive_byte_preservation': archive_checks,
        'pdf_sha256': hashlib.sha256((PAPER / 'main.pdf').read_bytes()).hexdigest(),
        'scope': 'Active compiled manuscript; excluded archive is preserved verbatim and is not subject to wording cleanup.',
    }
    (OUT / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    (OUT / 'paper_text.txt').write_text(pdf_text)
    assert not any([missing_refs, duplicate_labels, missing_cites, uncited_bib, missing_figures, archive_references, forbidden, log_errors, bib_warnings]), result
    assert all(appendix_reachability.values()) and all(archive_checks.values()), result
    assert statements_page - 1 <= 9, result
    print(json.dumps({k: v for k, v in result.items() if k not in ['archive_byte_preservation', 'active_inputs']}, indent=2))


if __name__ == '__main__':
    main()
