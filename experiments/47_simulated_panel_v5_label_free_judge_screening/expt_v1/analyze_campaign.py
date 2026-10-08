"""Offline statistical report over accepted scores, frozen probes and v5 targets."""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
import math
from pathlib import Path
import statistics
import sys
import numpy as np
from e47_adapter import ROOT,REPO,RESULTS,PRIVATE,POOL,RUN_ID,BASE_MODEL,FAMILY,read,write,module,sha
sys.path.insert(0,str(REPO/'py_src'))
import statistics_v5 as S
I=module('e47_owner_information',ROOT/'vendor/information_properties_addeba2.py')
A=module('e47_frozen_analysis',ROOT/'vendor/e39/analysis_lib.py')

def clean(value):
    if isinstance(value,dict):return {str(k):clean(v) for k,v in value.items()}
    if isinstance(value,(list,tuple,np.ndarray)):return [clean(v) for v in value]
    if isinstance(value,(float,np.floating)):return float(value) if math.isfinite(value) else None
    if isinstance(value,np.integer):return int(value)
    return value

def save(name,value):write(RESULTS/name,clean(value))

def accepted_scores():
    cache=read(PRIVATE/'accepted_cached_primary_scores.json')
    byconfig={c:{} for c in POOL};repeat_rows=[]
    for cfg,items in cache.items():
        for iid,r in items.items():
            byconfig[cfg][iid]=r['value']
            for raw in r['repeats']:
                if raw['accepted']:repeat_rows.append({'config':cfg,'kind':'crit','key':iid,'item':iid,'level':0,'repeat':raw['repeat'],'score':raw['score'],'source':'cached','cell':raw['cell']})
    for cfg in POOL:
        path=PRIVATE/'final_harvest'/f"{cfg.replace('|','__')}.json"
        if not path.exists():continue
        # Final harvest is the authoritative merged collection, including cache;
        # replace cached rows for this config instead of counting them twice.
        repeat_rows=[r for r in repeat_rows if r['config']!=cfg]
        rows=read(path)['cells'];accepted=[r for r in rows if r.get('accepted') and not r.get('structural_blank')]
        repeat_rows.extend(accepted);grouped=defaultdict(list)
        for r in accepted:
            if r['kind']=='crit':grouped[r['item']].append(r['score'])
        for iid,vals in grouped.items():byconfig[cfg][iid]=statistics.median(vals) if len(vals)>=2 else None
        for r in rows:
            if r.get('structural_blank'):byconfig[cfg][r['item']]=0.
    seen=set()
    for r in repeat_rows:
        key=(r['config'],r['kind'],r['key'],r['level'],r['repeat'])
        if key in seen:raise ValueError('duplicate accepted measurement '+str(key))
        seen.add(key)
    return byconfig,repeat_rows

def property_records(repeat_rows,items,manifest=None,exclude_group=None):
    """Historical components use original repeat counts; owner deletion uses supplement."""
    lookup=defaultdict(dict);item_by={r['item']:r for r in items};task_items=defaultdict(list)
    for r in items:
        if not r['blank'] and r['group']!=exclude_group:task_items[r['task']].append(r['item'])
    for r in repeat_rows:
        lookup[(r['config'],r['kind'],r['key'],r['level'])][r['repeat']]=r['score']
    probes=read(manifest)['rows'] if manifest else []
    valid=[r for r in probes if r.get('valid') is True];result=[];details=[]
    for cfg in POOL:
        def reps(kind,key,level):
            # New reference cell keys replace / with __; old probe schema keeps /.
            return lookup.get((cfg,kind,key,level),lookup.get((cfg,kind,key.replace('/','__'),level),{}))
        def median(kind,key,level):
            rs=reps(kind,key,level)
            if kind in ('ms_gold','ms_cand','blank'):vals=[rs[1]] if 1 in rs else []
            else:vals=list(rs.values()) if len(rs)>=2 else []
            return statistics.median(vals) if vals else None
        def add(comp,task,value,item=None,eligible=True,**extra):
            result.append({'config':cfg,'component':comp,'task':task,'item':item,'group':item_by[item]['group'] if item else None,'value':value,'eligible':eligible,**extra})
        for kind in ('ident','blank'):
            for r in [r for r in valid if r['kind']==kind]:
                m=median(kind,r['key'],0);add(kind,r['task'],(1-m if kind=='blank' else m) if m is not None else None)
        for kind,base in [('ms_gold','ident'),('bm_gold','ident'),('ms_cand','crit')]:
            grouped=defaultdict(list)
            for r in valid:
                if r['kind']==kind and (not r.get('item') or item_by[r['item']]['group']!=exclude_group):grouped[(r['key'],r['task'],r.get('item'))].append(r['level'])
            for (key,task,item),levels in grouped.items():
                levels=[0]+sorted(levels);meds=[median(base if lv==0 else kind,key,lv) for lv in levels]
                value=A.ladder_quality(levels,meds) if all(v is not None for v in meds) else None
                add(kind,task,value,item=item)
                if kind=='ms_gold':
                    rs={lv:list(reps('ident' if lv==0 else 'ms_gold',key,lv).values()) for lv in levels}
                    info=I.deletion_tvd_task(rs) if all(len(v)>=2 for v in rs.values()) else {'value':None,'information':None,'orientation':None}
                    add('deletion_tvd',task,info['value']);details.append({'config':cfg,'task':task,'property':'deletion_tvd',**info,'repeat_counts':{k:len(v) for k,v in rs.items()}})
        for task,iids in task_items.items():
            eligible=len(iids)>=2
            complete,excluded=I.complete_repeat_candidates({iid:reps('crit',iid,0) for iid in iids})
            value=I.repeat_tvd_task(complete) if len(complete)>=2 else None
            add('repeat_tvd',task,value,eligible=eligible)
            details.append({'config':cfg,'task':task,'property':'repeat_tvd','complete_candidates':len(complete),'declared_candidates':len(iids),'excluded_candidates':len(excluded)})
        # Explicit unresolved semantic slot; zero eligible audited tasks.
        for task in task_items:add('semantic_auc',task,None,eligible=False,reason='no independently audited strict-weakening and formatting probes')
    return result,details

def repeat_variability(rows):
    grouped=defaultdict(list)
    for r in rows:grouped[(r['config'],r['kind'],r['key'],r['level'])].append(r['score'])
    result={}
    for cfg in POOL:
        d={kind:[] for kind in {r['kind'] for r in rows}}
        for (c,kind,key,level),vals in grouped.items():
            if c==cfg:d[kind].append(vals)
        result[cfg]={kind:{'units':len(values),'accepted_raw_repeats':sum(map(len,values)),'repeat_count_distribution':dict(Counter(map(len,values))),
                          'mean_within_unit_sample_sd':np.mean([statistics.stdev(v) for v in values if len(v)>=2]) if any(len(v)>=2 for v in values) else None,
                          'aggregate_repeatability':'not estimable from one median-of-repeats aggregate per unit'} for kind,values in d.items()}
    return result

def make_panel(items,scores,target_key,records,configs=POOL):
    target=[]
    for r in items:
        target.append(r.get(target_key))
    return S.Panel(items,list(configs),[[scores[c].get(r['item']) for c in configs] for r in items],target,records)

def cached_analysis(draws):
    targets=read(RESULTS/'targets_reconstructed.json');scores,repeats=accepted_scores();nonblank=[r for r in targets if not r['blank']]
    configs=[c for c in POOL if scores[c]];result={}
    for key in ('T_all','T_C0','T_common_excluding_Anthropic_Alibaba','T_excluding_Anthropic'):
        for scope,rows in [('pooled',nonblank),('original_G01_G13',[r for r in nonblank if r['group'] not in ('G16','G17')]),('late_G16_G17',[r for r in nonblank if r['group'] in ('G16','G17')])]:
            p=make_panel(rows,scores,key,[],configs)
            result[key+'|'+scope]=p.criterion(draws)
            save('cached_descriptive.json',{'run_id':RUN_ID,'draws':draws,'seed':47,'status':'CACHED_SUBSET_ONLY','views':result,'declared_primary_configurations':12,'available_configurations':len(configs),'repeat_variability':repeat_variability(repeats)})
            print('cached descriptive complete',key,scope,flush=True)
    return result

def full_analysis(manifest,draws):
    targets=read(RESULTS/'targets_reconstructed.json');scores,repeats=accepted_scores();rows=[r for r in targets if not r['blank']]
    fingerprint=sha(json.dumps({'manifest':sha(Path(manifest).read_bytes()),'targets':targets,'scores':scores,'repeats':repeats,
                               'code':{p:sha((ROOT/p).read_bytes()) for p in ('analyze_campaign.py','statistics_v5.py')}},sort_keys=True).encode())
    def job(name,compute):
        path=RESULTS/'analysis_jobs'/f'{name}.json'
        if path.exists() and read(path).get('input_sha256')==fingerprint:return read(path)['result']
        result=clean(compute());write(path,{'run_id':RUN_ID,'input_sha256':fingerprint,'draws':draws,'seed':47,'result':result})
        print('analysis completed',name,flush=True);return result
    records,details=property_records(repeats,targets,manifest)
    save('per_task_properties.json',{'records':records,'details':details,'semantic_auc':'NOT_COMPUTABLE: no independent strict-weakening/formatting audit'})
    save('repeat_variability.json',repeat_variability(repeats));analyses={}
    for key in ('T_all','T_C0','T_common_excluding_Anthropic_Alibaba'):
        p=make_panel(rows,scores,key,records);analyses[key]=job('selection_'+key,lambda:p.evaluate(draws));save('selection_association.json',analyses)
        save('criterion_'+key+'.json',job('criterion_'+key,lambda:p.criterion(draws)))
        sensitivity={}
        for base in sorted(set(p.base)):
            sensitivity['exclude_base_'+base]=job(key+'_exclude_base_'+base,lambda:p.evaluate(draws,columns=np.flatnonzero(p.base!=base)))
        for family in sorted(set(p.family)):
            sensitivity['exclude_provider_'+family]=job(key+'_exclude_provider_'+family,lambda:p.evaluate(draws,columns=np.flatnonzero(p.family!=family)))
        for name,mask in [('original_G01_G13',[r['group'] not in ('G16','G17') for r in rows]),('late_G16_G17',[r['group'] in ('G16','G17') for r in rows])]:
            sensitivity[name]=job(key+'_'+name,lambda:p.evaluate(draws,test_indices=np.flatnonzero(mask)))
        # Same-eligible-pool sensitivity is additive; full-pool result above stays.
        eligible=[j for j,c in enumerate(POOL) if np.isfinite(p.scores[:,j]).sum()>=math.ceil(.9*len(rows))]
        sensitivity['same_eligible_pool']=job(key+'_same_eligible_pool',lambda:p.evaluate(draws,columns=eligible)) if eligible else {'status':'NOT_COMPUTABLE'}
        save('sensitivity_'+key+'.json',sensitivity)
        transfers={};folds=S.task_folds(p.tasks);group_panels={}
        for group in sorted({r['group'] for r in rows}):
            group_records,_=property_records(repeats,targets,manifest,exclude_group=group)
            q=make_panel(rows,scores,key,group_records)
            group_panels[group]=q
            transfers['agent_group_'+group]=job(key+'_group_'+group,lambda:q.evaluate(draws,test_indices=np.array([i for i,r in enumerate(rows) if r['group']==group]),exclude_group=group))
        transfers['equal_group_mean']=job(key+'_equal_group_mean',lambda:S.equal_group_transfer(group_panels,draws))
        for fold in range(5):
            train=[t for t in p.tasks if folds[t]!=fold];test=np.array([i for i,r in enumerate(rows) if folds[r['task']]==fold])
            transfers['task_fold_'+str(fold)]=job(key+'_task_fold_'+str(fold),lambda:p.evaluate(draws,train_tasks=train,test_indices=test))
        save('transfers_'+key+'.json',{'assignment':folds,'results':transfers,'agent_group_interpretation':'conditional on known shared references; not task transfer'})
        save('planning_'+key+'.json',{prop:job(key+'_planning_'+prop,lambda:S.planning(p,prop,draws)) for prop in S.PROPERTIES})
    # Judge-family-specific targets are sensitivities, never a shared comparator.
    for family in ('Anthropic','Alibaba'):
        configs=[c for c in POOL if FAMILY[c.split('|')[0]]==family]
        p=make_panel(rows,scores,'T_excluding_'+family,records,configs)
        save('criterion_excluding_'+family+'.json',job('criterion_excluding_'+family,lambda:p.criterion(draws)))
    allrows=make_panel(targets,scores,'T_all',records)
    save('criterion_all_declared_blank_zero.json',job('criterion_all_declared_blank_zero',lambda:allrows.criterion(draws)))
    recommendations={p:S.recommendation(analyses['T_all'],analyses['T_common_excluding_Anthropic_Alibaba'],p) for p in S.PROPERTIES}
    save('recommendations.json',recommendations)
    return analyses

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--cached-only',action='store_true');ap.add_argument('--probe-manifest',type=Path);ap.add_argument('--draws',type=int,default=10000);args=ap.parse_args()
    if args.draws!=10000:raise SystemExit('published campaign uses protocol 10000 draws')
    if args.cached_only:cached_analysis(args.draws)
    elif args.probe_manifest:full_analysis(args.probe_manifest,args.draws)
    else:raise SystemExit('--probe-manifest is required for full analysis')
