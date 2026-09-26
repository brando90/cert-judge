#!/usr/bin/env python3
"""Render the complete evidence-based disposition record (41 stable issue IDs)."""
from pathlib import Path
from collections import Counter
import json

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'py_src/cert_judge').is_dir() and (p / 'pyproject.toml').is_file())
HERE=Path(__file__).resolve().parents[1]
OUT=HERE/'results'
PAPER=ROOT/'paper_latex/ICLR_2027_submission'
# Each entry supplies a current-source anchor, the implemented decision, and
# the verification artifact or the smallest missing evidence. No model calls.
DETAILS={
'F01':('04_property_protocol.tex','The scalar omits',
 'Keep the distinction between four proposed properties and the bug-only variance-aware index; its floor precludes the old exact-collapse interpretation.',
 'Equation 1 and Appendix B match exp28 code; all 96 family/pass/configuration vectors reconstructed from the recorded bug arrays.'),
'F02':('998_appendix_index_definitions.tex','For each file',
 'Retain population variances, median repeats, family-panel normalization, clipping and exclusion of undefined correlations.',
 'derive_diagnostics.py independently reconstructs the components, normalization and index to absolute tolerance 1e-12; 24 included ladders in every primary vector.'),
'F03':('996_appendix_judge_cert_plots.tex','In each of the Codex',
 'A6: add 24 ladders × 5 levels and 96 rewrite rows per configuration; distinguish unchecked compilation from semantic damage.',
 'panel_audit.json: all 9,216 rows across Codex, Opus, Qwen and Leanstral checked; each configuration has levels 0–4 and four rewrite types. Generator inspected read-only.'),
'F04':('997_appendix_human_alignment.tex','The passes reflect',
 'Keep one annotator/two strictness passes and reject a numerical human-agreement ceiling.',
 'Frozen reliability table reports Spearman 0.249, interval [-0.015,0.489], and mean absolute error 0.771; PANEL_TRACE.md documents duplicate-row averaging. No optional extra prose needed.'),
'F05a':('03_problem_setup.tex','When a candidate shares',
 'A10: add the aligned-interface or specified-correspondence boundary, both human-alignment error types for BEq+, proof/intent distinction, failed-search limitation and absence of our own baseline benchmark.',
 'Poiroux publisher metadata and primary paper §3 and Appendix A.6 independently checked; verified citation added. No claim that differing representations categorically prevent comparison.'),
'F05b':('03_problem_setup.tex','We did not benchmark',
 'Retain an explicit empirical gap; a literature scope clarification is not a symbolic-baseline result.',
 'Future evidence: freeze correspondences, assumptions, obligations and search budgets, then compare successes and unresolved failures against the same human criterion.'),
'F06':('05_experiments.tex','Excluding random',
 'A2: use five semantic configurations after removing random, edit distance and BAD_STRINGY; also report three target-family semantic prompts. Omit the unnecessary six/four subsets that retain the lexical control.',
 'diagnostics.csv and subset_membership.json: 4 families × 3 label views × 3 subsets = 36 rows. Five-configuration avg rho: 0.900/0.600/0.900/-0.900; fixed normalization, average ranks, post-hoc interpretation.'),
'F07':('990_appendix_additional_results.tex','The exact tests enumerate',
 'A1: add nine exact two-sided permutation tests; leave the historical Codex resampling table unchanged and explicitly leave Opus/Qwen historical bootstrap intervals unavailable.',
 'Each exact test uses all 40,320 labeled permutations and an inclusive absolute-rho tail. Nine tests are unadjusted; shared controls and protocol selection remain limitations. Exact Codex values differ from historical p-values by less than 0.002.'),
'F08':('997_appendix_human_alignment.tex','The plotted geometric index',
 'Reject promotion of the 13-configuration panel as added power for the primary fixed index; it plots a separately tuned geometric object on reused labels.',
 'Archived expanded-panel JSON identifies mono/stability weights 0.4/0.6, not TI_var. Preserved in appendix.'),
'F09':('06_limitations.tex','The protocol could be instantiated',
 'Retain cross-benchmark and cross-assistant transfer as unmeasured.',
 'Future evidence: freeze the full protocol and normalization reference, then collect matched-rubric labels and scores on a genuinely new benchmark.'),
'F10':('main.tex','\\input{05_experiments}',
 'Do not restore the removed downstream agent table or make a deployment claim.',
 'All built sections inspected: downstream DSPy/Trace/Claude 3.7 table and its associated averaging, self-evaluation, compiler and caption claims are absent.'),
'F11a':('05_experiments.tex','Its score drops therefore cannot',
 'Keep withdrawal of the malformed-alpha result as evidence of valid renaming sensitivity; the artifact threshold is a repeatability statistic.',
 'Historical string generator inspected; current sections 5.2, 5.3 and Appendix E retain the explicit limitation. No canonicalization or Lean validity result invented.'),
'F11b':('05_experiments.tex','A real fix must rescore',
 'Keep the score-replacement proxy separate from canonicalization of input text.',
 'Future evidence: validated syntax-tree or binder canonicalization, elaboration checks and a new rescore under frozen scoring settings; no new inference performed.'),
'F12':('06_limitations.tex','The language-model configurations',
 'A11: state that language-model configurations use one rubric call per repeat; do not call random or edit-distance controls prompts.',
 'Four main-panel templates and _score_once call structure inspected. Structured multi-stage judges remain future evidence, not an implemented experiment.'),
'F13':('05_experiments.tex','The two-component geometric comparison',
 'Retain the existing admission that geometric point correlations exceed the fixed index for Codex and Opus.',
 'Frozen table: 0.857 versus 0.833 for Codex; 0.714 versus 0.643 for Opus. No superiority test or causal claim added.'),
'F14':('05_experiments.tex','The bug-monotonicity component alone',
 'A3: report the component-only correlations with a descriptive interpretation; explicitly retain the absent four-property comparison.',
 'All primary rho(C_f,human) values reproduce frozen summaries; full-index point rho is higher in 8/9 cells, with Qwen pass2 declining from 0.904762 to 0.857143.'),
'F15':('990_appendix_additional_results.tex','The source searches for weights',
 'A5: specify objective, four starts and uniform Dirichlet search, exact component order, rounded six-decimal pass2 weights, and the unrecovered historical seed/draw count.',
 'cross_pass_audit.json: saved full-precision weights reproduce every stored score within 1e-12 and correlations 0.880952/0.809524 and 0.857143/0.785714. Six-decimal pass2 weights change scores by up to 4.86149e-7; script defaults are not asserted as run facts.'),
'F16a':('990_appendix_additional_results.tex','The raw bug-level ranking',
 'Keep the pre-threshold ranking as mathematically independent of the artifact threshold.',
 'Threshold record gives raw bug rho -0.789689 at each threshold; no robustness-discovery claim.'),
'F16b':('990_appendix_additional_results.tex','The sweep covers six',
 'Keep the four selected table rows and add the explicit six-point sweep range and spacing.',
 'threshold_audit.json preserves all six rows: 0.60 through 0.85, step 0.05.'),
'F16c':('05_experiments.tex','No paired difference test',
 'A4: report interval overlap and no paired difference test or unique optimality; remove the caption’s inferential reduction implication.',
 'All six intervals overlap the 0.85 interval. Observed flip rates at 0.60 and 0.85 are 0.058081 and 0.046086; overlap is not a significance test.'),
'F17':('995_appendix_judge_prompts.tex','All model prompts request',
 'Retain direct [0,1] model output and separate [0,5] human scale.',
 'Prompt templates and full repeat arrays checked; no discrete 0–10 claim in built sources.'),
'F18':('990_appendix_additional_results.tex','pass1 & 0.881',
 'Do not restore the removed 0.881 headline claim.',
 '0.881 remains only the separately tuned pass1 fitting correlation; main fixed-index Codex avg remains 0.833.'),
'F19':('06_limitations.tex','We also collected 343',
 'Retain negative different-rubric pool results without treating them as a matched-rubric transfer test.',
 'Archived reports support 343 labels/78 pairs, about 0.13 on 63 shared pairs; exact JSON verifies n=32 screen rho=-0.3911, Holm p=0.2484, leave-one-out rho=0.2416 and p=0.4908. The 0.13 value remains report-level evidence, not a new exact recomputation.'),
'F20':('main.tex','\\input{994_appendix_tests_as_ground_theorems}',
 'Leave the removed Rice-theorem argument removed.',
 'No Rice claim occurs in built section prose; historical manuscript files preserved.'),
'F21':('main.tex','\\input{994_appendix_tests_as_ground_theorems}',
 'Leave the removed Verus kernel comparison removed.',
 'No Verus claim occurs in built section prose; historical manuscript files preserved.'),
'F22':('main.tex','\\input{994_appendix_tests_as_ground_theorems}',
 'Leave the removed Dafny execution claim removed.',
 'No Dafny claim occurs in built section prose; historical manuscript files preserved.'),
'F23':('998_appendix_index_definitions.tex',"$\\mathrm{anti}$ is",
 'Retain explicit anti-string and first-level-drop definitions.',
 'Definitions and clipping checked against the archived exp16 component code; no renamed frozen fields.'),
'F24':('997_appendix_human_alignment.tex','It uses \\texttt{labs-',
 'A7: add labs-leanstral-2603, eight-configuration composition, three recorded scores per row and median aggregation.',
 'panel_audit.json: 2,304 Leanstral rows, all with length-three repeat arrays; eight saved identifiers checked against expected membership.'),
'F25':('refs.bib','@INPROCEEDINGS{poiroux2025beq',
 'Leave the removed editorial-note bibliography entry removed.',
 'Current bibliography inspected: no Liu 2025 editorial-note entry; the verified Poiroux entry is retained in the integrated bibliography.'),
'F26':('997_appendix_human_alignment.tex','figures/expanded_panel_v2_vs_geometric.pdf',
 'A9: replace the publication figure with descriptive labels, a shared key, and readable layout; preserve the old image.',
 'figure_provenance.json verifies all 26 plotted coordinate pairs (13 in each panel) against the original JSON, both stored correlations and all four interval endpoints. No estimates recomputed; rendered figure inspected.'),
'F27':('997_appendix_human_alignment.tex','The two panels compare',
 'Keep the repaired LaTeX formula; A9 also removes the malformed legacy image title.',
 'New vector figure and caption visually checked on final page 17; formula and delimiters render correctly.'),
'F28':('995_appendix_judge_prompts.tex','BAD\\_STRINGY negative control',
 'Retain non-floating prompt listings; do not rewrite frozen prompt text.',
 'Final pages 13–14 inspected: BAD_STRINGY appears intact on page 14 with no intervening figure; the strict prompt continues across a page boundary without a float.'),
'F29':('main.tex','\\input{996_appendix_judge_cert_plots}',
 'Leave the removed broken figure references removed.',
 'Final log has zero undefined references/citations and extracted document has zero ?? placeholders.'),
'F30':('04_property_protocol.tex','\\mathrm{TI}_{\\mathrm{var}}=\\exp',
 'Keep the existing proper variance accents.',
 'Equation 1 visually checked on page 5; no trailing-circumflex defect in current source or rendering.'),
'F31':('998_appendix_index_definitions.tex','Here $\\mathrm{ident}$',
 'Keep mono as the manuscript notation; preserve frozen code identifiers.',
 'All active index-definition prose uses mono; no mono_rank alias introduced into prose.'),
'F32':('03_problem_setup.tex','An artifact is a Lean source',
 'Reject automatic removal of ordinary line-end hyphenation based on extracted text.',
 'Current source words and rendered pages checked; no literal thresh-old/specifica-tion/proto-col typos require edits.'),
'F33':('04_property_protocol.tex','theorem statements and unit tests',
 'Leave deleted or rewritten old prose removed, preserving historical sources.',
 'Built-source search and visual review confirm the old typo/caption targets are absent; the surviving duplicated author citations are repaired separately under X01.'),
'F34':('05_experiments.tex','One gold filename could not',
 'Retain 75 rated pairs/25 problems and 72 analyzed pairs/24 problems; do not adopt the feedback’s duplicate-pair explanation for the discrepancy.',
 'PANEL_TRACE.md and each family’s saved n_union_rows/n_skipped_pairs/row keys checked: three dropped candidate pairs share the unresolved gold name.'),
'F35':('990_appendix_additional_results.tex','Pass supplying weights',
 'Retain the already clarified table scope, with details completed under A5 and A4.',
 'Cross-pass associations and all six thresholds checked against frozen records; no frozen table values changed.'),
'X01':('02_related_work.tex','\\citet{Kocmi2024HumanVsLLM}',
 'A8: replace two duplicated author-name citation constructions with textual citations.',
 'Final page 2 and extracted text checked: both citations render once with year; no duplicate author strings.'),
'X02':('04_property_protocol.tex','In the recorded panels',
 'A12: correct the consultation: identity-summary rows use four rewrites, but literal unedited self-comparisons DO exist at bug-ladder level 0.',
 'All four families: 96 rewrite identity rows and 24 level-0 bug rows per configuration. The generator begins ladder=[code] and the driver passes gold versus cand; no new scores or claims of independent identity measurement.'),
}


def main():
    original=json.loads((OUT/'claude_fable_dispositions.json').read_text())
    assert set(DETAILS)=={r['id'] for r in original['items']} and len(DETAILS)==41
    items=[]
    for source in original['items']:
        row=dict(source)
        filename,anchor,decision,verification=DETAILS[row['id']]
        lines=(PAPER/filename).read_text().splitlines()
        matches=[i+1 for i,line in enumerate(lines) if anchor in line]
        assert matches,(row['id'],filename,anchor)
        row.update({'current_source':f'paper_latex/ICLR_2027_submission/{filename}:{matches[0]}',
                    'final_decision':decision,'verification':verification,
                    'implementation_status':'IMPLEMENTED' if row['disposition']=='APPLY' else 'RETAINED',
                    'resolution_scope':'reporting repaired; evidence gaps remain' if row['disposition']=='APPLY' else row['disposition']})
        items.append(row)
    counts=dict(Counter(r['disposition'] for r in items))
    output={'experiment':'37_openreview_feedback_current_iclr_revision','phase':'integrated',
       'base_commit':'fee091524293dffa1e74c67b247f13d2fd235ad7','counts':counts,'total_items':41,
       'implemented_actions':sorted({r['action'] for r in items if r.get('action')},key=lambda v:int(v[1:])),
       'items':items,'scientific_gaps_closed':False}
    (OUT/'final_dispositions.json').write_text(json.dumps(output,indent=2)+'\n')
    header='''# Experiment 37: complete feedback disposition and verification table

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/archive/37_openreview_feedback_current_iclr_revision/expt_v1/results/final_issue_table.md>

**TLDR:** All 41 issues have an independently checked disposition: 12 supported repairs implemented, 16 already addressed, 8 removed, 3 requiring future evidence, and 2 rejected. The implemented changes repair reporting; they do not close the missing experiments or establish transfer.

Locations below refer to the integrated manuscript. The original isolated-worker table is preserved as worker_final_issue_table.md; see FINAL_REPORT.md for integration provenance. `APPLY` means the warranted repair was implemented, including any narrower interpretation recorded here. The original consultation remains unchanged in adjacent files.

| Issue | Original concern | Disposition / action | Current source | Final decision | Verification / remaining evidence |
|---|---|---|---|---|---|
'''
    def clean(s): return str(s).replace('|','\\|').replace('\n',' ')
    rows=[]
    for r in items:
        fields=[r['id'],r['concern'],r['disposition']+(' / '+r['action'] if r.get('action') else ''),
                '`'+r['current_source']+'`',r['final_decision'],r['verification']]
        rows.append('| '+' | '.join(clean(x) for x in fields)+' |')
    (OUT/'final_issue_table.md').write_text(header+'\n'.join(rows)+'\n')
    print(counts)


if __name__=='__main__':
    main()
