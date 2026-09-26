#!/usr/bin/env python3
"""Verify the delivered revision and write a receipt; never build or stage files.

Run after the actual rendered manuscript has been inspected and copied back.
Visual assertions are read from a separate human/agent inspection receipt, not
inferred from compilation. Scientific diagnostics are checked against frozen
inputs, independently derived outputs, and manuscript table displays.
"""
from pathlib import Path
from collections import Counter
import csv
import datetime
import hashlib
import json
import re
import subprocess

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'py_src/cert_judge').is_dir() and (p / 'pyproject.toml').is_file())
HERE = Path(__file__).resolve().parents[1]
OUT = HERE / 'results'
PAPER = ROOT / 'paper_latex/ICLR_2027_submission'
EXPERIMENT = HERE.parent
CHECKS = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((OUT / name).read_text())


def command(args, cwd=ROOT):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    CHECKS.append({'command': args, 'cwd': str(cwd.relative_to(ROOT)) or '.',
                   'exit_code': result.returncode,
                   'output': result.stdout + result.stderr})
    assert result.returncode == 0, CHECKS[-1]
    return result.stdout


def table(text, label):
    blocks = re.findall(r'\\begin\{table\}.*?\\end\{table\}', text, re.S)
    matches = [b for b in blocks if '\\label{' + label + '}' in b]
    assert len(matches) == 1, label
    return matches[0]


def main():
    initial = read('initial_state.json')
    base = initial['base_commit']
    assert command(['git', 'rev-parse', 'HEAD']).strip() == base
    assert command(['git', 'branch', '--show-current']).strip() == 'codex/paper-feedback'
    command(['git', 'diff', '--cached', '--quiet'])
    command(['git', 'diff', '--check'])
    command(['/usr/local/bin/python3', 'py_src/cert_judge/experiment_layout.py', '--check'])
    sentence_files = ['main.tex'] + sorted({p.name for glob in ['0*.tex', '99*.tex'] for p in PAPER.glob(glob)})
    command(['/usr/local/bin/python3', str(Path.home() / 'agents-config/scripts/latex_sentence_lines.py'),
             '--check', *sentence_files], PAPER)
    command(['git', 'diff', '--quiet', base, '--', 'experiments/archive', 'data', 'py_src'])
    assert all(r['matches'] for r in initial['manuscript_hash_comparison'])

    manuscript_changes = {
        '02_related_work.tex', '03_problem_setup.tex', '04_property_protocol.tex',
        '05_experiments.tex', '06_limitations.tex', '990_appendix_additional_results.tex',
        '996_appendix_judge_cert_plots.tex', '997_appendix_human_alignment.tex',
        'refs.bib', 'main.pdf'}
    allowed = {str((PAPER / p).relative_to(ROOT)) for p in manuscript_changes}
    protected = []
    for path, expected in initial['paper_files_before'].items():
        if path not in allowed:
            assert sha(ROOT / path) == expected, path
            protected.append(path)
    changes = command(['git', 'diff', '--name-only', base]).splitlines()
    allowed_tracked = allowed | {str((EXPERIMENT / p).relative_to(ROOT)) for p in
                                 ['results.md', 'CKPT_feedback_revision.md']}
    assert set(changes) <= allowed_tracked, set(changes) - allowed_tracked
    new_files = command(['git', 'ls-files', '--others', '--exclude-standard']).splitlines()
    for path in new_files:
        assert path.startswith(str(EXPERIMENT.relative_to(ROOT)) + '/') or path == \
            str((PAPER / 'figures/expanded_panel_v2_vs_geometric.pdf').relative_to(ROOT)), path
    old_section = command(['git', 'show', base + ':paper_latex/ICLR_2027_submission/05_experiments.tex'])
    old_table = table(old_section, 'tab:tivar_cross_model_results')
    new_table = table((PAPER / '05_experiments.tex').read_text(), 'tab:tivar_cross_model_results')
    assert old_table == new_table

    diagnostic = read('diagnostic_provenance.json')
    assert diagnostic['script_sha256'] == sha(HERE / 'scripts/derive_diagnostics.py')
    for path, info in diagnostic['inputs'].items():
        assert sha(ROOT / path) == info['sha256'], path
    assert (diagnostic['expected_rows'], diagnostic['observed_rows'], diagnostic['exact_tests'],
            diagnostic['undefined_correlations']) == (36, 36, 9, 0)
    rows = list(csv.DictReader((OUT / 'diagnostics.csv').open()))
    assert len(rows) == len({(r['family'], r['label_view'], r['subset']) for r in rows}) == 36
    expected_sizes = {'full_panel_8': 8, 'semantic_5': 5, 'target_semantic_3': 3}
    assert all(int(r['n_configurations']) == expected_sizes[r['subset']] for r in rows)
    assert sum(bool(r['exact_two_sided_p']) for r in rows) == 9
    for r in rows:
        if r['exact_two_sided_p']:
            assert int(r['total_permutations']) == 40320
            assert float(r['exact_two_sided_p']) == int(r['extreme_permutations']) / 40320
    membership = read('subset_membership.json')
    assert len(membership) == 36
    for r in membership:
        if r['subset'] != 'full_panel_8':
            assert all(not (x.startswith(('editdist', 'random')) or 'BAD_STRINGY' in x) for x in r['members'])
    # Independent display check: each family/view's LaTeX row must match the
    # derived full-panel component/probability and two semantic-subset values.
    lookup = {(r['family'], r['label_view'], r['subset']): r for r in rows}
    appendix = (PAPER / '990_appendix_additional_results.tex').read_text()
    family = None
    checked_displays = 0
    for line in table(appendix, 'tab:subset-diagnostics').splitlines():
        fields = [x.strip().replace('$', '').rstrip('\\').strip() for x in line.split('&')]
        if len(fields) != 7 or fields[1] not in ['avg', 'pass1', 'pass2']:
            continue
        family = fields[0] or family
        full = lookup[(family, fields[1], 'full_panel_8')]
        expected = [full['rho_TI_vs_human'], full['rho_Cf_vs_human'], full['exact_two_sided_p'],
                    lookup[(family, fields[1], 'semantic_5')]['rho_TI_vs_human'],
                    lookup[(family, fields[1], 'target_semantic_3')]['rho_TI_vs_human']]
        assert fields[2:] == [f'{float(v):.3f}' if v else '---' for v in expected], (fields, expected)
        checked_displays += 1
    assert checked_displays == 12
    audit = read('panel_audit.json')
    assert sum(r['rows'] for r in audit) == 9216
    assert sum(len(r['configurations']) for r in audit) == 32
    assert all(c['ladders'] == 24 and c['identity_rows'] == 96 and
               c['unedited_self_comparison_bug_level_0_rows'] == 24
               for r in audit for c in r['configurations'])

    figure = read('figure_provenance.json')
    assert sha(ROOT / figure['source']) == figure['source_sha256']
    assert sha(HERE / 'scripts/plot_expanded_panel.py') == figure['script_sha256']
    assert sha(ROOT / figure['output']) == figure['output_sha256']
    assert figure['points_per_panel'] == 13 and len(figure['rendered_points']) == 26
    assert not figure['estimates_recomputed'] and figure['coordinates_checked_against_artists']
    original = json.loads((ROOT / figure['source']).read_text())
    for key, value in figure['archived_estimates'].items():
        assert original[key] == value

    disposition = read('final_dispositions.json')
    assert disposition['total_items'] == len(disposition['items']) == 41
    assert len({r['id'] for r in disposition['items']}) == 41
    assert disposition['counts'] == {'APPLY': 12, 'ALREADY_ADDRESSED': 16, 'REMOVED': 8,
                                     'FUTURE_EVIDENCE': 3, 'REJECT': 2}
    assert set(disposition['implemented_actions']) == {f'A{i}' for i in range(1, 13)}
    consultation = read('claude_fable_dispositions.json')
    assert {r['id'] for r in consultation['items']} == {r['id'] for r in disposition['items']}
    assert not disposition['scientific_gaps_closed']
    for issue in disposition['items']:
        path, line = issue['current_source'].rsplit(':', 1)
        assert 1 <= int(line) <= len((ROOT / path).read_text().splitlines())

    build = read('build_receipt.json')
    visual = read('visual_inspection.json')
    assert build['build_exit_code'] == 0 and build['pages'] == 19
    assert build['main_body_end_page'] <= build['main_body_limit'] == 9
    assert build['statements_start_page'] == 10
    assert not build['latex_errors'] and not build['unresolved_references_or_citations']
    assert build['question_mark_placeholders'] == 0
    assert not any('Overfull' in s for s in build['warnings'])
    assert build['copied_to_manuscript'] and visual['result'] == 'PASS'
    assert sha(PAPER / 'main.pdf') == build['pdf_sha256'] == visual['final_pdf_sha256']
    assert visual['all_final_pages_covered'] == list(range(1, 20))
    for path, expected in build['source_hashes'].items():
        assert sha(ROOT / path) == expected
    assert sha(PAPER / 'refs.bib') == build['bibliography_sha256']
    assert sha(PAPER / 'figures/expanded_panel_v2_vs_geometric.pdf') == build['figure_sha256']
    for path, expected in visual['rendered_page_sha256'].items():
        assert sha(ROOT / path) == expected
    active_sections = re.findall(r'\\input\{([^}]+)\}', (PAPER / 'main.tex').read_text())
    active_text = '\n'.join((PAPER / (n if n.endswith('.tex') else n + '.tex')).read_text()
                            for n in active_sections)
    bib = (PAPER / 'refs.bib').read_text()
    keys = re.findall(r'@\w+\s*\{\s*([^,]+),', bib)
    assert len(keys) == len(set(keys))
    cited = {key.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^]]*\])*\{([^}]+)\}', active_text)
             for key in group.split(',')}
    assert cited <= set(keys), cited - set(keys)
    assert 'poiroux2025beq' in cited
    assert initial['artifact_marker']['invocations'] == 1 and initial['artifact_marker']['exit_code'] == 0
    assert (OUT / 'RESULTS_feedback_revision.md').is_file()

    # Review exact deliverable paths without printing potential secret values.
    secret_patterns = [r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                       r'\b(?:sk-proj-|sk-ant-|sk_live_)[A-Za-z0-9_-]{20,}',
                       r'\bgh[pousr]_[A-Za-z0-9]{30,}', r'\bAKIA[A-Z0-9]{16}\b']
    findings = []
    text_files = 0
    for path in sorted(set(changes + new_files)):
        raw = (ROOT / path).read_bytes()
        if b'\0' in raw:
            continue
        try:
            contents = raw.decode('utf-8')
        except UnicodeDecodeError:
            continue
        text_files += 1
        for pattern in secret_patterns:
            if re.search(pattern, contents):
                findings.append({'path': path, 'pattern': pattern})
    assert not findings, findings
    manifest = {}
    for path in sorted(set(changes + new_files)):
        if path != str((OUT / 'verification.json').relative_to(ROOT)):
            manifest[path] = sha(ROOT / path)
    receipt = {
        'experiment': '37_openreview_feedback_current_iclr_revision',
        'checked_at': datetime.datetime.now().astimezone().isoformat(),
        'base_commit': base, 'branch': 'codex/paper-feedback', 'result': 'PASS',
        'checks': CHECKS, 'consultation_inputs_matched': 18,
        'preserved_paper_artifacts': len(protected), 'preserved_paper_paths': protected,
        'frozen_data_and_code_diff': 'unchanged against base commit',
        'frozen_primary_table_sha256': hashlib.sha256(old_table.encode()).hexdigest(),
        'diagnostic_input_files_hashed': len(diagnostic['inputs']),
        'diagnostic_rows': 36, 'exact_tests': 9, 'permutations_per_test': 40320,
        'undefined_subset_correlations': 0, 'manuscript_numeric_rows_checked': 12,
        'score_rows_audited': 9216, 'configurations_audited': 32,
        'figure_points_per_panel': 13, 'figure_estimates_recomputed': False,
        'dispositions': disposition['counts'], 'all_actions_implemented': disposition['implemented_actions'],
        'bibliography_entries': len(keys), 'cited_keys': len(cited),
        'document': {k: build[k] for k in ['pages', 'main_body_end_page', 'main_body_limit',
                      'statements_start_page', 'pdf_sha256', 'latex_errors',
                      'unresolved_references_or_citations', 'warnings']},
        'visual_result': visual['result'], 'visual_pages_covered': visual['all_final_pages_covered'],
        'artifact_marker': initial['artifact_marker'],
        'secret_pattern_scan': {'text_files_scanned': text_files, 'findings': findings,
             'scope': 'all changed and untracked nonignored deliverable text; not a claim of universal secret detection'},
        'index': 'no staged changes', 'commit_or_push': False, 'new_model_evaluations': 0,
        'scientific_gaps_closed': False,
        'manifest_excludes_self_and_ignored_build_private_files': True,
        'artifact_sha256': manifest}
    (OUT / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ['result', 'preserved_paper_artifacts',
                     'diagnostic_rows', 'score_rows_audited', 'manuscript_numeric_rows_checked',
                     'bibliography_entries', 'cited_keys', 'dispositions']}, indent=2))


if __name__ == '__main__':
    main()
