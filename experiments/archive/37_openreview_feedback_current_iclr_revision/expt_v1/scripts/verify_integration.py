#!/usr/bin/env python3
"""Check the integrated manuscript, fixed inputs and archived experiment layout."""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess
import sys

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'py_src/cert_judge').is_dir() and (p / 'pyproject.toml').is_file())
HERE = Path(__file__).resolve().parents[1]
OUT = HERE / 'results'
PAPER = ROOT / 'paper_latex/ICLR_2027_submission'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((OUT / name).read_text())


def main():
    receipt = read('integration_receipt.json')
    for name, expected in receipt['source_hashes_after'].items():
        assert sha(PAPER / name) == expected, name
    assert sha(PAPER / 'main.pdf') == receipt['pdf_sha256']
    assert sha(PAPER / 'figures/expanded_panel_v2_vs_geometric.pdf') == receipt['figure_sha256']
    for name in receipt['protected_concurrent_sources_unchanged']:
        assert receipt['source_hashes_before'][name] == receipt['source_hashes_after'][name]
    provenance = read('diagnostic_provenance.json')
    for name, meta in provenance['inputs'].items():
        assert sha(ROOT / name) == meta['sha256'], name
    independent = read('coordinator_numerical_verification.json')
    assert independent['all_match'] and independent['rows_checked'] == 36
    assert independent['component_and_index_correlations_checked'] == 72
    assert independent['exact_tests_checked'] == 9
    assert sha(OUT / 'diagnostics.csv') == independent['worker_csv_sha256']
    with (OUT / 'diagnostics.csv').open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 36
    assert sum(bool(row['exact_two_sided_p']) for row in rows) == 9
    issues = read('final_dispositions.json')
    assert issues['total_items'] == len(issues['items']) == 41
    assert len(issues['implemented_actions']) == 12
    for item in issues['items']:
        name, line = item['current_source'].rsplit(':', 1)
        assert 0 < int(line) <= len((ROOT / name).read_text().splitlines())
    text = subprocess.check_output(['pdftotext', '-layout', str(PAPER / 'main.pdf'), '-'], text=True)
    pages = text.split('\f')[:-1]
    assert len(pages) == 19 and 'C ONCLUSION' in pages[8]
    assert 'anonymous supplement contains' in pages[9] and '??' not in text
    assert receipt['visual_inspected_pages'] == list(range(1, 20))
    assert not receipt['latex_errors'] and not receipt['unresolved_references'] and not receipt['overfull_boxes']
    commands = [
        [sys.executable, 'py_src/cert_judge/experiment_layout.py', '--check'],
        ['git', 'diff', '--check'],
        [sys.executable, str(Path.home() / 'agents-config/scripts/latex_sentence_lines.py'),
         '--check', *[str(p.relative_to(ROOT)) for p in sorted(PAPER.glob('*.tex'))
                      if re.match(r'(main|0\d.*|99\d.*)\.tex$', p.name)]],
    ]
    checks = []
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        assert result.returncode == 0, result.stdout + result.stderr
        checks.append({'command': command, 'exit_code': result.returncode,
                       'output': result.stdout + result.stderr})
    result = {'status': 'PASS', 'source_files_checked': len(receipt['source_hashes_after']),
              'frozen_inputs_checked': len(provenance['inputs']), 'diagnostic_rows': 36,
              'independent_correlations': 72, 'independent_exact_tests': 9,
              'issues': 41, 'repairs': 12, 'pages': 19, 'main_text_pages': 9,
              'visual_pages': 19, 'pdf_sha256': receipt['pdf_sha256'], 'checks': checks}
    (OUT / 'integration_verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'checks'}, indent=2))


if __name__ == '__main__':
    main()
