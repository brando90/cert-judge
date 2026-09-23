#!/usr/bin/env python3
"""Inventory printed numeric source lines and their reviewed evidence groups.

This is an audit index, not an automatic proof that a source supports a claim.
The mapping was reviewed against the archived scripts and outputs; hashes lock
the cited evidence. New main-text numeric lines require reviewing this mapping.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / 'paper_latex/ICLR_2027_submission'
OUT = Path(__file__).resolve().parent / 'results'
B = 'experiments/archive/04_veribench_validation/'
REV = '8d2e005'


def expand(patterns):
    result = []
    for pattern in patterns:
        matches = sorted(ROOT.glob(pattern))
        assert matches, pattern
        result.extend(str(p.relative_to(ROOT)) for p in matches if p.is_file())
    return sorted(set(result))


GROUPS = {
 'panel': ('Panel sizes, scales, repeats, models, prompts and label passes', [
    B+'results_exp16_final_robust_r9_median/summary.json', B+'results_exp16_final_robust_r9_median/detail_rows.csv',
    B+'results_exp16_opus47_r3_median/summary.json',
    'experiments/archive/13_qwen_replication_exp16_exp19/results/exp16_qwen_r3_median/summary.json',
    'experiments/archive/26_human_label_dataset_audit/ethan_slack_confirmation.md',
    'experiments/archive/26_human_label_dataset_audit/results/PANEL_TRACE.md',
    B+'exp16_multi_judge_human_sets.py']),
 'fixed': ('Fixed-index associations and all primary configuration values', [
    B+'results_exp28_varaware_codex_pass1/summary.json',
    B+'results_exp28_varaware_codex_*_newindex/summary.json',
    B+'results_exp28_varaware_codex_avg_newindex/judge_trust_vector.csv',
    B+'results_exp28_varaware_opus_*_newindex/summary.json',
    B+'results_exp28_varaware_opus_avg_newindex/judge_trust_vector.csv',
    B+'results_exp28_varaware_qwen_*/summary.json',
    B+'results_exp28_varaware_qwen_avg/judge_trust_vector.csv']),
 'ci': ('Codex confidence intervals, permutation probabilities, seed and repetitions', [
    'experiments/archive/21_tmlr_submission/ci_provenance/headline_cis.json']),
 'human': ('Human-human statistics and rating scale', [
    B+'results_final_stat_reliability_suite/exp18_human_label_reliability/summary.json']),
 'checks': ('Recorded rewrite scores and local bug reversal counts', [
    B+'results_exp16_final_robust_r9_median/detail_rows.csv',
    B+'results_exp19_low_variance_replot/bug_reversal_rates.csv',
    'experiments/archive/02_neurips_reviews/utils/variant_generator.py']),
 'proxy': ('Alpha score-replacement proxy, not rescored canonicalized text', [
    B+'results_exp24_alpha_canonicalized_identity/summary.json']),
 'definitions': ('Property identifiers, score domains and fixed numerical constants', [
    B+'exp28_variance_aware_trust_index.py', B+'exp16_multi_judge_human_sets.py',
    'experiments/archive/02_neurips_reviews/utils/veribench_variance_utils.py']),
 'comparisons': ('Arithmetic and pass1-selected geometric comparison', [
    B+'results_exp16_final_robust_r9_median/summary.json', B+'results_exp16_opus47_r3_median/summary.json',
    'experiments/archive/13_qwen_replication_exp16_exp19/results/exp16_qwen_r3_median/summary.json',
    B+'results_exp22_geometric_trust_index/median_mono_stab_40_60/summary.json',
    B+'results_exp22_geometric_trust_index/opus47_r3_median_mono_stab_40_60_avg/summary.json',
    'experiments/archive/13_qwen_replication_exp16_exp19/results/exp25_geometric_qwen_r3_median_mono_stab_40_60_avg/summary.json']),
 'tuned': ('Separate fitted geometric variant and expanded configuration panel', [
    B+'results_exp23_cross_pass_calibration/summary_fit_pass*.json',
    B+'results_exp22_expanded_judges_stable/exp25_geom_avg/summary.json']),
 'leanstral': ('Negative fixed-index replication', [B+'results_exp28_varaware_leanstral_*/summary.json']),
 'components': ('Diagnostic associations; historical P3 field is a bug statistic', [
    B+'results_exp17_final_robust_*/per_property_correlations.csv', B+'exp17_property_human_analysis.py']),
 'threshold': ('Artifact threshold, decision flips and pass rates; mean aggregation', [
    'experiments/archive/02_neurips_reviews/results/threshold_calibration_sweep/threshold_metrics.csv',
    'experiments/archive/02_neurips_reviews/results/threshold_calibration_sweep/summary.json']),
 'pool': ('Different-rubric pool and two registered screens', [
    'experiments/archive/22_pooled_heldout_and_noise_ceiling/results/results.json',
    'experiments/archive/22_pooled_heldout_and_noise_ceiling/REPORT.md',
    'experiments/archive/23_reanchored_calibration/results/results.json',
    'experiments/archive/24_expanded_panel_cli/results/pass2_full_screen_results.json']),
 'derived': ('New zero-inference recomputation: Pearson/Kendall, plots and local weight sensitivity', [
    'experiments/34_iclr_mega_rewrite_astra/analysis/rebuild_paper_evidence.py',
    'experiments/34_iclr_mega_rewrite_astra/analysis/results/summary.json',
    'experiments/34_iclr_mega_rewrite_astra/analysis/results/weight_sensitivity_summary.csv',
    'experiments/34_iclr_mega_rewrite_astra/analysis/results/scatter_coordinates.csv',
    'experiments/34_iclr_mega_rewrite_astra/analysis/results/clean_rewrite_statistics.csv',
    'experiments/34_iclr_mega_rewrite_astra/analysis/results/bug_curve_statistics.csv']),
}


def evidence_for(filename, context, line):
    if filename.startswith(('00', '01')):
        return ['panel', 'fixed', 'ci', 'definitions']
    if filename.startswith('02'):
        return ['panel']
    if filename.startswith(('03', '04')):
        return ['definitions', 'panel']
    if filename.startswith('06'):
        return ['pool', 'panel', 'definitions']
    if filename.startswith('07'):
        return ['fixed']
    if 'Data and human panel' in context:
        return ['panel', 'human']
    if 'canonicalization proxy' in context:
        return ['proxy', 'definitions']
    if 'Coverage of P3' in context:
        return ['panel', 'definitions']
    if 'Property checks' in context:
        return ['checks', 'derived', 'panel']
    if 'Human agreement alone' in context:
        return ['fixed', 'checks', 'panel']
    if 'Choice of index' in context:
        return ['comparisons', 'tuned', 'leanstral', 'fixed']
    if 'Weight and normalization' in context:
        return ['derived', 'fixed']
    if 'Which measured' in context:
        return ['components', 'definitions']
    if 'Artifact-score threshold' in context:
        return ['threshold']
    return ['fixed', 'comparisons', 'ci', 'derived', 'panel']


def main():
    groups = {}
    for key, (description, patterns) in GROUPS.items():
        sources = []
        for relative in expand(patterns):
            data = (ROOT / relative).read_bytes()
            generated = relative.startswith('experiments/34_')
            if not generated:
                frozen = subprocess.check_output(['git', 'show', REV+':'+relative], cwd=ROOT)
                assert frozen == data, relative
            sources.append({'path': relative, 'sha256': hashlib.sha256(data).hexdigest(),
                            'kind': 'new committed reanalysis' if generated else 'frozen committed evidence'})
        groups[key] = {'description': description, 'sources': sources}
    inventory = []
    for file in sorted(PAPER.glob('0[0-7]_*.tex')):
        context = ''
        for n, raw in enumerate(file.read_text().splitlines(), 1):
            line = re.sub(r'(?<!\\)%.*', '', raw).strip()
            if re.match(r'\\(?:subsection|paragraph)\{', line):
                context = line
            line = re.sub(r'\\(?:label|ref|eqref|cite\w*)\{[^}]*\}', '', line)
            if line.startswith('\\node'):
                match = re.search(r'\{([^{}]*)\};$', line)
                line = match.group(1) if match else ''
            if not line or line.startswith(('\\begin', '\\end', '\\includegraphics', '\\cmidrule', '\\draw', '\\node', 'box/.style', 'flow/.style')):
                continue
            line = re.sub(r'\\tfrac(\d)(\d)', r'\1/\2', line)
            numerals = re.findall(r'[-+]?\d+(?:\.\d+)?', line)
            if not numerals:
                continue
            inventory.append({'file':file.name, 'line':n, 'numerals':' ; '.join(numerals),
                              'evidence_groups': ', '.join(evidence_for(file.name, context, line)),
                              'source_text':raw})
    with (OUT/'number_inventory.csv').open('w', newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(inventory[0]),lineterminator="\n");writer.writeheader();writer.writerows(inventory)
    (OUT/'number_provenance.json').write_text(json.dumps(groups,indent=2)+'\n')
    md='## Number-provenance table\n\nEvery printed numeric source line in main sections 00–07 is indexed below. Property labels, model versions, index names and equation constants are identifiers or definitions, not empirical estimates. Cross-reference numbers are generated by LaTeX. Axis ticks are plotting coordinates; all plotted observations are retained in the figure CSVs. Written-out counts are additionally covered in the panel/protocol rows of the summary table above.\n\n'
    md+='### Evidence groups\n\n'
    for key, value in groups.items():
        md+=f'**{key} — {value["description"]}.**\n\n'
        for source in value['sources']:
            md+=f'- `{source["path"]}`\n'
        md+='\n'
    md+='### Exhaustive main-text numeric source lines\n\n| Source | Numerals (in source order) | Evidence groups |\n|---|---|---|\n'
    for row in inventory:
        md+=f'| `{row["file"]}:{row["line"]}` | {row["numerals"]} | {row["evidence_groups"]} |\n'
    md+='\nThe CSV preserves each full source line; the JSON records exact paths and SHA-256 hashes. Values are rounded to the precision shown in the manuscript; no direction or scale was changed. The approximate pool association (0.13 on 63 shared pairs) is supported by the corrected committed experiment-22 report, not by an exact field in its JSON.\n'
    (OUT/'number_inventory.md').write_text(md)
    print(f'Inventoried {len(inventory)} numeric source lines in {len(groups)} evidence groups.')


if __name__ == '__main__':
    main()
