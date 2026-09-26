#!/usr/bin/env python3
"""Compile only in an experiment-owned scratch copy; retain verification evidence.

This does not copy main.pdf back. Inspect the rendered pages and then copy the
successful scratch build to the manuscript, as described in the results report.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tempfile

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'py_src/cert_judge').is_dir() and (p / 'pyproject.toml').is_file())
HERE=Path(__file__).resolve().parents[1]
PAPER=ROOT/'paper_latex/ICLR_2027_submission'
RESULTS=HERE/'results'


def command(args,cwd=None):
    result=subprocess.run(args,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    return {'command':args,'exit_code':result.returncode,'output':result.stdout}


def main():
    tmp=HERE/'tmp'; tmp.mkdir(exist_ok=True)
    snapshot=HERE/'source_snapshot'; snapshot.mkdir(exist_ok=True)
    if not (snapshot/'main_before.pdf').exists():
        shutil.copy2(PAPER/'main.pdf',snapshot/'main_before.pdf')
    scratch=Path(tempfile.mkdtemp(prefix='manuscript-',dir=tmp))
    shutil.copytree(PAPER,scratch,dirs_exist_ok=True,
        ignore=shutil.ignore_patterns('*.aux','*.bbl','*.blg','*.fdb_latexmk','*.fls','*.log','*.out','*.synctex.gz','_build','main.pdf'))
    built=command(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','main.tex'],scratch)
    (RESULTS/'build_transcript.txt').write_text(built['output'])
    assert built['exit_code']==0, built['output'][-4000:]
    log=(scratch/'main.log').read_text(errors='replace')
    (RESULTS/'build_final_log.txt').write_text(log)
    info=command(['pdfinfo',str(scratch/'main.pdf')])
    assert info['exit_code']==0
    text=command(['pdftotext','-layout',str(scratch/'main.pdf'),'-'])['output']
    (RESULTS/'manuscript_text.txt').write_text(text)
    pages=text.split('\f')
    if not pages[-1].strip(): pages.pop()
    conclusion=[i+1 for i,p in enumerate(pages) if 'Human judgment then becomes a reusable foundation' in p]
    statements=[i+1 for i,p in enumerate(pages) if 'The anonymous supplement contains' in p]
    errors=re.findall(r'^!.*$',log,re.M)
    unresolved=re.findall(r'^.*(?:undefined|multiply defined|Citation.*undefined|Reference.*undefined).*$' ,log,re.M|re.I)
    warnings=re.findall(r'^.*(?:Warning:|Overfull|Underfull).*$' ,log,re.M)
    assert not errors and not unresolved and '??' not in text
    assert len(conclusion)==1 and conclusion[0]<=9 and statements[0]>conclusion[0],(conclusion,statements)
    assert not re.search(r'EXP\d|Bavaresco et al\. \(Bavaresco|Wood-Doughty \(Schroeder',text)
    old=command(['pdftotext','-layout',str(snapshot/'main_before.pdf'),'-'])['output'].split('\f')
    changed=[i+1 for i,p in enumerate(pages) if i>=len(old) or p!=old[i]]
    render=HERE/'rendered'; render.mkdir(exist_ok=True)
    result=command(['pdftoppm','-r','115','-png',str(scratch/'main.pdf'),str(render/'page')])
    assert result['exit_code']==0,result
    receipt={'scratch_directory':str(scratch.relative_to(ROOT)),'build_exit_code':built['exit_code'],
      'pdf_sha256':hashlib.sha256((scratch/'main.pdf').read_bytes()).hexdigest(),
      'pdfinfo':info['output'],'pages':len(pages),'main_body_end_page':conclusion[0],
      'main_body_limit':9,'statements_start_page':statements[0],
      'latex_errors':errors,'unresolved_references_or_citations':unresolved,'warnings':warnings,
      'question_mark_placeholders':text.count('??'),'changed_text_pages':changed,
      'rendered_pages':len(pages),'visual_inspection':'pending','copied_to_manuscript':False,
      'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(PAPER.glob('*.tex'))},
      'bibliography_sha256':hashlib.sha256((PAPER/'refs.bib').read_bytes()).hexdigest(),
      'figure_sha256':hashlib.sha256((PAPER/'figures/expanded_panel_v2_vs_geometric.pdf').read_bytes()).hexdigest(),
      'tools':{name:command([name,'-v' if name in ['pdfinfo','pdftoppm'] else '-version'])['output'].splitlines()[:3]
               for name in ['latexmk','pdfinfo','pdftoppm']}}
    (RESULTS/'build_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['scratch_directory','pages','main_body_end_page','statements_start_page','latex_errors','unresolved_references_or_citations','warnings','changed_text_pages']},indent=2))


if __name__=='__main__':
    main()
