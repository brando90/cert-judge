#!/usr/bin/env python3
"""Frozen, offline five-rater analysis. No inference, credentials or network clients."""
from __future__ import annotations
import argparse
from collections import defaultdict, Counter
import importlib.util
import hashlib
import json
import math
import platform
import statistics
import sys
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import scipy
from scipy.stats import rankdata, spearmanr
from inventory import EXP, ROOT, sha, load_module
OUT = EXP/'results'
E39 = next((ROOT/'experiments').glob('39_*'))
E42 = next((ROOT/'experiments').glob('42_*'))
E43 = next((ROOT/'experiments').glob('43_*'))
E44 = ROOT/'experiments/archive/44_cached_score_judge_selection_utility'

def module(name, path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
U=module('utility44',E44/'scripts/analyze_selection_utility.py')
A=module('analysis39',E39/'scripts/analysis_lib.py')

def read(p): return json.loads(p.read_text())
def clean(x):
    if isinstance(x,dict): return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,(float,np.floating)): return float(x) if math.isfinite(x) else None
    if isinstance(x,np.integer):return int(x)
    return x

def write(name,x):
    p=OUT/name;p.write_text(json.dumps(clean(x),indent=2,sort_keys=True,allow_nan=False)+'\n')

def fingerprint():
    paths=[EXP/'PROTOCOL.md',E44/'inputs/items.jsonl']
    for e, names in [(E39,['panel.json','units_train_val.json','units_test.json','probe_manifest.json','FINALISTS.json','TEST_RECEIPT.json']),(E42,['semantic_probe_manifest.json','semantic_screen.json']),(E43,['full/cells.json','analysis.json'])]:
        paths += [e/'results'/n for n in names]
        paths += sorted((e/'results/harvest').glob('*.json'))
    paths += sorted((E42/'probe_edits/audit').glob('*.json'))
    # Keep the frozen protocol's logical key stable when its completed home is archived.
    return {('experiments/'+EXP.name+'/PROTOCOL.md' if p==EXP/'PROTOCOL.md' else str(p.relative_to(ROOT))):sha(p) for p in paths}

def load(vb, allowed=('train','val','test')):
    inventory=read(OUT/'inventory.json');p=Path(inventory['parser']['path'])
    p=vb/'experiments/75_J1_validating_formal_spec_judge_train_val_test/scripts/audit_human_judgment_data.py'
    assert sha(p)==inventory['parser']['sha256']
    parser=load_module(p);h=vb/'veribench_dataset/human_labels'
    for n,info in inventory['source_files'].items():assert sha(h/n)==info['sha256'],n
    meta_items=read(OUT/'coverage_by_item.json');item_map={r['candidate']:r for r in meta_items}
    targets={};ratings={n:parser.read_rows(h/n) for n in parser.PARTICIPANTS}
    old={n:{r['candidate']:r['score'] for r in parser.read_rows(h/n) if item_map[r['candidate']]['split']=='train'} for n in parser.OLD}
    assert all(len(x)==30 for x in old.values())
    raw_by={n:{r['candidate']:r['score'] for r in rs} for n,rs in ratings.items()}
    for r in meta_items:
        if r['split'] not in allowed:continue
        c=r['candidate'];v=[raw_by[n][c] for n in parser.PARTICIPANTS]
        targets[r['item']]={'all5':statistics.mean(x for x in v if x is not None)/5,'three':statistics.mean(x for x in v[:3] if x is not None)/5,'raters':v}
        if r['split']=='train':
            targets[r['item']]['aux']=.5*targets[r['item']]['all5']+.5*statistics.mean(old[n][c] for n in parser.OLD)/5
    # Labels embedded in historical items are never used for selection; retain metadata only.
    items=[{k:v for k,v in r.items() if k not in {'p1','p2','p3','p4','p5','target_expert','target_all5','expert_n'}} for r in map(json.loads,(E44/'inputs/items.jsonl').read_text().splitlines())]
    panel=read(E39/'results/panel.json');meta={u['config']:u for u in panel['units'] if u['kind']=='llm'}
    units={u['config']:u for f in ['units_train_val.json','units_test.json'] for u in read(E39/'results'/f)['units']}
    harvest={};scores={};raw={}
    for c in meta:
        h=read(E39/'results/harvest'/f"{c.replace('|','__')}.json")
        assert h['config']==c
        harvest[c]=h;scores[c]=U.median_scores(h,{r['item']:r for r in items});reps=defaultdict(list)
        for z in h['cells']:
            if z['kind']=='crit' and z['level']==0 and z['status'] in ('measured','deterministic') and z.get('score') is not None:reps[z['key']].append(z['score'])
        assert all(len(v)<=3 for v in reps.values());raw[c]=dict(reps)
    return items,targets,meta,units,harvest,scores,raw

def semantic_rows():
    labels={pid:lab['label'] for p in sorted((E42/'probe_edits/audit').glob('*.json')) for pid,lab in read(p).get('labels',{}).items()}
    rows=[{**r,'strictness':labels.get(r['probe_id'])} for r in read(E42/'results/semantic_probe_manifest.json')['rows'] if r['valid'] is True]
    return rows

def semantic(h,rows):
    b=defaultdict(list);seen=set()
    for c in h['cells']:
        assert c['cell'] not in seen;seen.add(c['cell'])
        if c['status'] in ('measured','deterministic') and c.get('score') is not None:
            assert 0<=c['score']<=1;b[(c['kind'],c['task'],c['level'])].append(c['score'])
    sc={k:statistics.median(v) for k,v in b.items() if len(v)>=2}
    out=[]
    for r in rows:
        if r['kind']=='ident':continue
        ident=sc.get(('ident',r['task'],1));v=sc.get((r['kind'],r['task'],r['level']));valid=ident is not None and v is not None
        out.append({'task':r['task'],'family':r['family'],'probe_id':r['probe_id'],'strictness':r['strictness'],'directional':float(v<ident) if valid else None,'gap':abs(v-ident) if valid else None})
    return out

def measure_rows(rows,key):
    vals=[r[key] for r in rows if r[key] is not None]
    return {'value':statistics.mean(vals) if vals and len(vals)>=.8*len(rows) else None,'observed':len(vals),'declared':len(rows),'tasks':len({r['task'] for r in rows})}

def support(items,configs,scores):return [r for r in items if all(r['item'] in scores[c] for c in configs)]
def utilities(configs,rows,scores,targets,target):
    return {c:U.corr([scores[c][r['item']] for r in rows],[targets[r['item']][target] for r in rows]) for c in configs}
def value(weights,utility,metric='spearman'):
    if not weights or any(utility[c][metric] is None for c in weights):return None
    return sum(w*utility[c][metric] for c,w in weights.items())

def selection(vb):
    before=fingerprint();items,targets,meta,units,harvest,scores,raw=load(vb,('train','val'))
    configs=U.pools(meta)['primary_full_context'];train_tasks={r['task'] for r in items if r['split']=='train'}
    train=[r for r in items if r['split']=='train'];val=[r for r in items if r['split']=='val']
    tr=support(train,configs,scores);va=support(val,configs,scores)
    training_ok=len(tr)>=math.ceil(.9*len(train)); validation_ok=len(va)>=math.ceil(.9*len(val))
    assert training_ok, 'training support insufficient'
    probes=A.valid_probes(read(E39/'results/probe_manifest.json'));probes={k:[r for r in rs if r['task'] in train_tasks] for k,rs in probes.items()}
    sr=[r for r in semantic_rows() if r['task'] in train_tasks]
    details={};rule_values={n:{} for n in ('train_deletion','train_strict_weakening','train_joint')}
    for c in configs:
        h={**harvest[c],'cells':[z for z in harvest[c]['cells'] if z['task'] in train_tasks]}
        delete=A.components(A.Scores(h),probes)['ms_gold']
        sem=semantic(read(E42/'results/harvest'/f"{c.replace('|','__')}.json"),sr)
        strict=measure_rows([r for r in sem if r['family']=='weakening' and r['strictness']=='strict'],'directional')
        fmt=measure_rows([r for r in sem if r['family']=='formatting'],'directional')
        d=delete['value'];w=None if strict['value'] is None or fmt['value'] is None else max(0,strict['value']-fmt['value'])
        rule_values['train_deletion'][c]=d;rule_values['train_strict_weakening'][c]=w;rule_values['train_joint'][c]=None if d is None or w is None else math.sqrt(d*w)
        details[c]={'deletion':delete,'strict_weakening':strict,'format_false_alarm':fmt}
    weights={k:U.weights_max(configs,v) for k,v in rule_values.items()}
    vu=utilities(configs,va,scores,targets,'all5')
    validation={k:(value(w,vu) if validation_ok else None) for k,w in weights.items()}
    eligible=[k for k in weights if validation[k] is not None];chosen=sorted(eligible,key=lambda k:(-validation[k],k))[0] if eligible else None
    supervised={}
    for target in ('all5','aux'):
        tu=utilities(configs,tr,scores,targets,target)
        best=sorted([c for c in configs if tu[c]['spearman'] is not None],key=lambda c:(-tu[c]['spearman'],c))[:3]
        eligible=[c for c in best if validation_ok and vu[c]['spearman'] is not None]
        winner=sorted(eligible,key=lambda c:(-vu[c]['spearman'],c))[0] if eligible else None
        supervised[target]={'train':tu,'shortlist':best,'validation':{c:vu[c] for c in best},'winner':winner,'weights':{winner:1.0} if winner else None}
    result={'written_utc':datetime.now(timezone.utc).isoformat(),'protocol_sha256':sha(EXP/'PROTOCOL.md'),'source_hashes':before,'train_tasks':sorted(train_tasks),'selection_item_ids':[r['item'] for r in tr+va],'test_labels_used':False,'selection_status':'COMPUTED' if validation_ok else 'UNAVAILABLE_VALIDATION_SHARED_SUPPORT','validation_required_items':math.ceil(.9*len(val)),'historical_train_observations':60,'historical_val_test_observations_used':0,'pool':configs,'common_train_items':len(tr),'common_validation_items':len(va),'behavioral_details':details,'rule_values':rule_values,'weights':weights,'validation_spearman':validation,'selected_rule':chosen,'selected_weights':weights.get(chosen),'supervised_controls':supervised}
    assert before==fingerprint();write('SELECTION.json',result)
    print(json.dumps({k:result[k] for k in ('selected_rule','selected_weights','validation_spearman','common_train_items','common_validation_items')},indent=2))

METRICS=('spearman','pearson','kendall','mae','bias','judge_mean','human_mean')
def stat_matrix(matrix,y,idx):
    r=U.draw_correlations(matrix,y,idx);x=matrix[:,idx];yy=y[idx];delta=x-yy
    return np.array([r['spearman'],r['pearson'],r['kendall'],np.abs(delta).mean(axis=1),delta.mean(axis=1),x.mean(axis=1),np.repeat(yy.mean(),len(matrix))]).T

def interval(point,draws):
    z=np.asarray(draws);good=z[np.isfinite(z)];lo,hi=np.percentile(good,[2.5,97.5]) if len(good) else (None,None)
    return {'value':point,'lo':lo,'hi':hi,'valid_draws':len(good),'undefined_draws':len(z)-len(good),'p_value':None}

def evaluate(configs,rows,scores,targets,weights,draws,seed=45):
    ids=[r['item'] for r in rows];matrix=np.array([[scores[c][i] for i in ids] for c in configs]);names=list(weights)
    # Explicit member slicing avoids NaN*0 poisoning expectations for unrelated constant judges.
    locations={n:[(configs.index(c),w) for c,w in (weights[n] or {}).items()] for n in names}
    def reduce(arr):return np.array([sum(w*arr[i] for i,w in locations[n]) if locations[n] else np.full(len(METRICS),np.nan) for n in names])
    group=defaultdict(list)
    for i,r in enumerate(rows):group[r['task']].append(i)
    groups=[np.array(group[k],int) for k in sorted(group)]
    rng=np.random.default_rng(seed);samples=rng.integers(0,len(groups),(draws,len(groups)))
    out={};boots={};idx0=np.arange(len(ids))
    for target in ('all5','three'):
        y=np.array([targets[i][target] for i in ids]);point=stat_matrix(matrix,y,idx0);bs=np.empty((draws,len(names),len(METRICS)));byjudge=np.empty((draws,len(configs),3))
        for b,g in enumerate(samples):
            idx=np.concatenate([groups[j] for j in g]);m=stat_matrix(matrix,y,idx);bs[b]=reduce(m);byjudge[b]=m[:,:3]
        ps=reduce(point);result={}
        for j,n in enumerate(names):
            result[n]={'weights':weights[n],'metrics':{metric:interval(ps[j,k],bs[:,j,k]) for k,metric in enumerate(METRICS)}}
        contrasts={}
        for left in names:
            for right in ('human_mirror_H2','random'):
                if left==right or right not in names:continue
                a,b=names.index(left),names.index(right);contrasts[left+'-'+right]=interval(ps[a,0]-ps[b,0],bs[:,a,0]-bs[:,b,0])
        perjudge={c:{m:interval(point[j,k],byjudge[:,j,k]) for k,m in enumerate(METRICS[:3])} for j,c in enumerate(configs)}
        out[target]={'selectors':result,'contrasts':contrasts,'per_judge':perjudge};boots[target]=bs
    out['target_sensitivity']={n:interval(out['all5']['selectors'][n]['metrics']['spearman']['value']-out['three']['selectors'][n]['metrics']['spearman']['value'],boots['all5'][:,j,0]-boots['three'][:,j,0]) for j,n in enumerate(names)}
    return clean(out)

def evaluation(vb,draws):
    seal=read(OUT/'SELECTION.json');before=fingerprint();assert before==seal['source_hashes'];items,targets,meta,units,harvest,scores,raw=load(vb)
    # Reproduce frozen criterion exactly, before interpreting five-rater outcomes.
    reproduction=[]
    for c in meta:
        own=[r for r in items if r['split'] in ('val','test') and r['item'] in scores[c]]
        u=utilities([c],own,scores,targets,'three')[c];stored=units[c]['criteria']['heldout']
        assert stored['n_items']==len(own) and stored['n_declared']==45
        if stored['status']=='COMPUTED':
            for m in METRICS[:3]:assert (u[m] is None and stored[m] is None) or abs(u[m]-stored[m])<1e-10,(c,m,u[m],stored[m])
        reproduction.append({'config':c,'n_items':len(own),'status':stored['status'],'recomputed':u})
    write('frozen_reproduction.json',reproduction)
    pools=U.pools(meta);proxy={c:units[c]['indices'].get('C_ms_gold') for c in meta};ident={c:units[c]['indices'].get('C_ident') for c in meta}
    views={s:[r for r in items if r['split']==s] for s in ('train','val','test')}
    views['original45']=[r for r in items if r['split'] in ('val','test')]
    views['no_placeholder36']=[r for r in views['original45'] if not r['ref_placeholder_at_annotation']]
    views['no_ambiguity36']=[r for r in views['original45'] if not r['ref_ambiguous_in_window']]
    views['neither27']=[r for r in views['original45'] if not r['ref_placeholder_at_annotation'] and not r['ref_ambiguous_in_window']]
    results={};(OUT/'comparisons').mkdir(exist_ok=True)
    for pname,pool in pools.items():
      for eligible in (False,True):
        configs=[c for c in pool if proxy[c] is not None] if eligible else pool
        weight=U.selector_weights(configs,meta,proxy,ident,None);weight.pop('transferred_prompt')
        if pname=='primary_full_context' and not eligible:
            weight.update(seal['weights']);weight['validation_selected_behavior']=seal['selected_weights']
            weight.update({'supervised_'+k:v['weights'] for k,v in seal['supervised_controls'].items()})
        for vname,declared in views.items():
            key=f'{pname}__{"proxy_eligible" if eligible else "declared"}__{vname}';path=OUT/'comparisons'/f'{key}.json'
            common=support(declared,configs,scores)
            result={'pool':pname,'proxy_eligible_only':eligible,'view':vname,'configs':configs,'declared_items':len(declared),'common_items':len(common),'common_tasks':len({r['task'] for r in common}),'item_ids':[r['item'] for r in common],'missing_item_ids':[r['item'] for r in declared if r not in common],'draws':draws,'seed':45,'resampling_unit':'tasks with all within-task item rows and multiplicity','selection_uncertainty_included':False}
            if len(common)<math.ceil(.9*len(declared)):
                result['status']='UNAVAILABLE_SHARED_SUPPORT'
            else:
                result['status']='COMPUTED';result['analysis']=evaluate(configs,common,scores,targets,weight,draws)
                result['repeats']={c:{'counts':dict(Counter(len(raw[c][r['item']]) for r in common)),'available':sum(len(raw[c][r['item']]) for r in common),'expected':3*len(common),'mean_within_item_sample_sd':statistics.mean(statistics.stdev(raw[c][r['item']]) for r in common if len(raw[c][r['item']])>=2)} for c in configs}
            write('comparisons/'+key+'.json',result);results[key]={'status':result['status'],'common_items':len(common),'common_tasks':result['common_tasks'],'sha256':sha(path)}
            print(key,result['status'],len(common),flush=True)
    assert before==fingerprint()
    write('analysis_receipt.json',{'status':'COMPLETE','source_hashes':before,'selection_sha256':sha(OUT/'SELECTION.json'),'draws':draws,'seed':45,'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'comparisons':results,'reproduced_frozen_configs':len(reproduction),'inference_calls':0})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['select','evaluate']);p.add_argument('--veribench',type=Path,default=Path.home()/'veribench');p.add_argument('--draws',type=int,default=10000);a=p.parse_args()
    selection(a.veribench) if a.phase=='select' else evaluation(a.veribench,a.draws)
