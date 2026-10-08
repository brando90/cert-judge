"""Complete all criterion/repeat-only analyses while structural compilation runs."""
from concurrent.futures import ProcessPoolExecutor,as_completed
from multiprocessing import get_context
import numpy as np
from e47_adapter import ROOT,RESULTS,PRIVATE,POOL,FAMILY,RUN_ID,read,write,sha
from analyze_campaign import accepted_scores,property_records,make_panel,clean,repeat_variability
import statistics_v5 as S
import analysis_provenance as P

_ITEMS=None
_SCORES=None
_INPUT_DIGEST=None

def criterion_job(spec):
    cfg,target,scope=spec
    rows=[r for r in _ITEMS if scope=='all_declared_blank_zero' or not r['blank']]
    if scope=='original_G01_G13':rows=[r for r in rows if r['group'] not in ('G16','G17')]
    if scope=='late_G16_G17':rows=[r for r in rows if r['group'] in ('G16','G17')]
    key='T_excluding_'+FAMILY[cfg.split('|')[0]] if target=='own_family_excluded' else target
    label=cfg+'|'+target+'|'+scope
    fingerprint=_INPUT_DIGEST
    path=RESULTS/'criterion_descriptive'/f'{sha(label.encode())[:24]}.json'
    if path.exists() and P.current_job(read(path),fingerprint):return label,str(path.relative_to(ROOT))
    panel=make_panel(rows,_SCORES,key,[],[cfg]);result=panel.criterion(10000)[cfg]
    write(path,clean({'run_id':RUN_ID,'config':cfg,'target':key,'scope':scope,'input_sha256':fingerprint,'seed':47,'draws':10000,'result':result}))
    return label,str(path.relative_to(ROOT))

def repeat_target(args):
    target,repeats,records,digest=args
    fingerprint=digest
    def job(label,compute):
        path=RESULTS/'repeat_only_analysis'/f'{label}.json'
        if path.exists() and P.current_job(read(path),fingerprint):return
        result=compute()
        if isinstance(result,dict) and 'properties' in result:result={**result,'properties':{'repeat_tvd':result['properties']['repeat_tvd']}}
        write(path,clean({'run_id':RUN_ID,'input_sha256':fingerprint,'result':result,'seed':47,'draws':10000,'primary_probe_properties':'pending complete structural/scoring campaign; no shortlist conclusion'}));print('repeat-only analysis completed',label,flush=True)
    rows=[r for r in _ITEMS if not r['blank']]
    panel=make_panel(rows,_SCORES,target,records);job(target+'_pooled',lambda:panel.evaluate(10000,property_names=('repeat_tvd',)))
    for base in sorted(set(panel.base)):job(target+'_exclude_base_'+base,lambda:panel.evaluate(10000,property_names=('repeat_tvd',),columns=np.flatnonzero(panel.base!=base)))
    for family in sorted(set(panel.family)):job(target+'_exclude_provider_'+family,lambda:panel.evaluate(10000,property_names=('repeat_tvd',),columns=np.flatnonzero(panel.family!=family)))
    groups={}
    for group in sorted({r['group'] for r in rows}):
        group_records,_=property_records(repeats,_ITEMS,exclude_group=group);q=make_panel(rows,_SCORES,target,group_records);groups[group]=q
        job(target+'_group_'+group,lambda:q.evaluate(10000,property_names=('repeat_tvd',),test_indices=np.array([i for i,r in enumerate(rows) if r['group']==group]),exclude_group=group))
    job(target+'_equal_group_mean',lambda:S.equal_group_transfer(groups,10000,property_names=('repeat_tvd',)))
    folds=S.task_folds(panel.tasks)
    for fold in range(5):
        train=[t for t in panel.tasks if folds[t]!=fold];test=np.array([i for i,r in enumerate(rows) if folds[r['task']]==fold])
        job(target+'_task_fold_'+str(fold),lambda:panel.evaluate(10000,property_names=('repeat_tvd',),train_tasks=train,test_indices=test))
    job(target+'_planning',lambda:S.planning(panel,'repeat_tvd',10000))
    return target

def main():
    global _ITEMS,_SCORES,_INPUT_DIGEST
    identity=P.capture_inputs('criterion');_INPUT_DIGEST=P.fingerprint(identity)
    _ITEMS=read(RESULTS/'targets_reconstructed.json');_SCORES,repeats=accepted_scores('criterion')
    for cfg in POOL:
        path=PRIVATE/'criterion/final_harvest'/f"{cfg.replace('|','__')}.json"
        if not path.exists() or len(read(path)['cells'])!=2250:raise ValueError('incomplete declared criterion '+cfg)
    jobs=[(cfg,target,scope) for cfg in POOL for target in ('T_all','T_C0','T_common_excluding_Anthropic_Alibaba','own_family_excluded') for scope in ('pooled','original_G01_G13','late_G16_G17','all_declared_blank_zero')]
    results={}
    with ProcessPoolExecutor(max_workers=4,mp_context=get_context("fork")) as pool:
        for future in as_completed([pool.submit(criterion_job,spec) for spec in jobs]):
            label,path=future.result();results[label]=path
            write(RESULTS/'criterion_descriptive_index.json',{'run_id':RUN_ID,'expected':len(jobs),'completed':len(results),'results':results,'whole_experiment_complete':False});print('criterion descriptive completed',label,flush=True)
    records,details=property_records(repeats,_ITEMS)
    write(RESULTS/'repeat_only_task_properties.json',clean({'records':[r for r in records if r['component']=='repeat_tvd'],'details':details}))
    write(RESULTS/'repeat_variability_criterion.json',clean(repeat_variability(repeats,_ITEMS)))
    with ProcessPoolExecutor(max_workers=3,mp_context=get_context("fork")) as workers:
        futures=[workers.submit(repeat_target,(target,repeats,records,_INPUT_DIGEST)) for target in P.TARGETS]
        for future in as_completed(futures):print('repeat target complete',future.result(),flush=True)
    write(RESULTS/'criterion_only_analysis_complete.json',{'run_id':RUN_ID,'criterion_views':len(jobs),'repeat_property_analyses':'pooled, base/provider exclusions, every agent group, equal-group mean, five task folds and conditional planning for all three shared targets','whole_experiment_complete':False})
    P.publish_criterion_receipt(identity)

if __name__=='__main__':main()
