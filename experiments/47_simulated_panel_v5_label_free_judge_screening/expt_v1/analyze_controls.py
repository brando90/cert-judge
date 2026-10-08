"""Frozen structural controls and private-panel coverage/agreement diagnostics."""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
import gzip
import json
from pathlib import Path
import numpy as np
from e47_adapter import ROOT,RESULTS,PRIVATE,RUN_ID,read,write,sha,load_items,module,frozen
from analyze_campaign import clean
from analyze_cached import resolve_receipts,complete_first,target_excluding
from statistics_v5 import Panel

def structural_values(items):
    frozen()
    parser=module('e47_control_probes',ROOT/'vendor/e39/probes.py').theorem_decls
    rows=[];counts={}
    for r in items:
        if not Path(r['candidate_path_abs']).is_file():
            rows.append({'item':r['item'],'byte_length':None,'candidate_theorems':None,'reference_theorems':None,'length_score':None,'count_ratio':None,'reason':'source candidate file absent; no invented empty file'})
            continue
        candidate=Path(r['candidate_path_abs']).read_bytes();reference=Path(r['ref_ann_path_abs']).read_bytes()
        def count(data):
            key=sha(data)
            if key not in counts:counts[key]=len(parser(data.decode('utf-8',errors='replace')))
            return counts[key]
        nc,nr=count(candidate),count(reference)
        rows.append({'item':r['item'],'byte_length':len(candidate),'candidate_theorems':nc,'reference_theorems':nr,
                     'length_score':len(candidate)/(1+len(candidate)),'count_ratio':min(1.,nc/nr) if nr else None})
    return rows

def diagnostic_values():
    source=ROOT/'inputs/veribench_v5';meta=read(source/'manifest.json');late=read(source/'late/manifest_G16_G17.json')
    declared={r['cell']:r for r in json.loads(gzip.decompress((source/'manifest_cells.json.gz').read_bytes()))['S2']+late['cells']['S2']}
    raw=[]
    for path in sorted((PRIVATE/'raw_v5_cells').glob('*/*cells.jsonl')):
        for line in path.read_text().splitlines():
            if line.strip():
                r=json.loads(line)
                if r['cell'] in declared:raw.append((path.parent.name,r))
    resolved,_=resolve_receipts(raw,declared);slots=complete_first(resolved)
    models={r['key']:r['family'] for r in read(source/'panel.json')['members']}
    targets=read(PRIVATE/'targets_with_family_values.json');out={}
    for model,family in models.items():
        for frame in ('P1','P2','P3','C0'):
            out[family+'|'+frame]={r['item']:(slots[(r['item'],frame,model)]['score_0_5_parser_v2']/5 if (r['item'],frame,model) in slots else None) for r in targets}
        for frame,key in [('persona_mean','family_values'),('C0_mean','c0_values')]:out[family+'|'+frame]={r['item']:r[key].get(family) for r in targets}
    return out,targets

def one_analysis(job):
    label,rows,score,target,kind=job
    digest=sha(json.dumps(job,sort_keys=True).encode());path=RESULTS/'controls_diagnostics'/f'{sha(label.encode())[:20]}.json'
    if path.exists() and read(path).get('input_sha256')==digest:return label,str(path.relative_to(ROOT))
    panel=Panel(rows,[label],[[score.get(r['item'])] for r in rows],[target.get(r['item']) for r in rows],[],base_models=[kind],provider_families=[kind])
    result=panel.criterion(10000)[label]
    write(path,clean({'run_id':RUN_ID,'label':label,'kind':kind,'input_sha256':digest,'seed':47,'draws':10000,'result':result,
                      'cross_judge_ranking':'UNDEFINED: deterministic item scorer is constant across judge configurations' if kind=='structural_control' else 'not a primary judge configuration'}))
    return label,str(path.relative_to(ROOT))

def main():
    items=load_items();features=structural_values(items);write(RESULTS/'structural_controls.json',{'run_id':RUN_ID,'rows':features,'parser':'frozen E39 probes.theorem_decls','parser_sha256':sha((ROOT/'vendor/e39/probes.py').read_bytes())})
    diagnostic,private_targets=diagnostic_values();targets=read(RESULTS/'targets_reconstructed.json');rows=[r for r in targets if not r['blank']];jobs=[]
    for control in ('length_score','count_ratio'):
        scores={r['item']:r[control] for r in features}
        for target in ('T_all','T_C0','T_common_excluding_Anthropic_Alibaba'):
            jobs.append((control+'|'+target,rows,scores,{r['item']:r[target] for r in targets},'structural_control'))
    coverage={}
    for label,values in diagnostic.items():
        family=label.split('|')[0];coverage[label]={'declared_nonblank':len(rows),'accepted_nonblank':sum(values.get(r['item']) is not None for r in rows),
                                                'by_group':{g:{'declared':sum(r['group']==g for r in rows),'accepted':sum(r['group']==g and values.get(r['item']) is not None for r in rows)} for g in sorted({r['group'] for r in rows})}}
        for target in ('T_all','T_excluding_own_family'):
            target_values={r['item']:(r['T_all'] if target=='T_all' else target_excluding(r['family_values'],{family})) for r in private_targets}
            jobs.append((label+'|'+target,rows,values,target_values,'panel_diagnostic'))
    # Only aggregate diagnostics are published. Individual panel ratings stay private.
    write(RESULTS/'panel_coverage_diagnostics.json',{'run_id':RUN_ID,'per_family_frame':coverage,'blank_items':sum(r['blank'] for r in targets),'nonblank_items':len(rows)})
    index={}
    with ProcessPoolExecutor(max_workers=4) as executor:
        for future in as_completed([executor.submit(one_analysis,j) for j in jobs]):
            label,path=future.result();index[label]=path
            write(RESULTS/'controls_diagnostics_index.json',{'run_id':RUN_ID,'expected':len(jobs),'completed':len(index),'results':index});print('control/diagnostic completed',label,flush=True)

if __name__=='__main__':main()
