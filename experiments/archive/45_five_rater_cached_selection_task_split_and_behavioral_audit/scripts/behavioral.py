#!/usr/bin/env python3
"""Reproduce existing semantic/gaming evidence and stratify by frozen task split."""
from collections import defaultdict,Counter
import argparse
import statistics
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
import analyze as a

def cluster_summary(rows,key,draws=10000):
    valid=[r for r in rows if r.get(key) is not None]
    if not valid:return {'value':None,'n':0,'declared':len(rows),'tasks':0}
    groups=defaultdict(list)
    for r in valid:groups[r['task']].append(r[key])
    totals=np.array([sum(groups[t]) for t in sorted(groups)]);ns=np.array([len(groups[t]) for t in sorted(groups)])
    ids=np.random.default_rng(45).integers(0,len(groups),(draws,len(groups)))
    boot=totals[ids].sum(1)/ns[ids].sum(1)
    return {**a.interval(sum(totals)/sum(ns),boot),'n':len(valid),'declared':len(rows),'tasks':len(groups)}

def run(vb,draws):
    before=a.fingerprint();splits={r['task']:r['split'] for r in a.read(a.OUT/'coverage_by_item.json')}
    sr=a.semantic_rows();old={u['config']:u for u in a.read(a.E42/'results/semantic_screen.json')['units']};semout={};maxerr=0
    for p in sorted((a.E42/'results/harvest').glob('*.json')):
        h=a.read(p);c=h['config'];rows=a.semantic(h,sr)
        for fam in ('vacuity','weakening','overconstraint','formatting'):
            key='gap' if fam=='formatting' else 'directional';rs=[r for r in rows if r['family']==fam]
            vals=[r[key] for r in rs if r[key] is not None];got=statistics.mean(vals) if vals else None;stored=old[c]['metrics'][fam]['value']
            assert (got is None and stored is None) or abs(got-stored)<1e-10,(c,fam,got,stored)
            if got is not None:maxerr=max(maxerr,abs(got-stored))
        views={}
        for split in ('train','val','test','all'):
            rs=[r for r in rows if split=='all' or splits[r['task']]==split];v={}
            for fam in ('vacuity','weakening','overconstraint','formatting'):
                z=[r for r in rs if r['family']==fam];v[fam]=cluster_summary(z,'gap' if fam=='formatting' else 'directional',draws)
                if fam in ('weakening','overconstraint'):
                    for strict in ('strict','redundant','unclear'):v[fam+'_'+strict]=cluster_summary([r for r in z if r['strictness']==strict],'directional',draws)
            v['format_false_alarm']=cluster_summary([r for r in rs if r['family']=='formatting'],'directional',draws);views[split]=v
        semout[c]=views
    a.write('semantic_audit.json',{'reproduced_configurations':len(semout),'maximum_point_difference':maxerr,'probe_strictness_counts':dict(Counter((r['family']+':'+str(r['strictness'])) for r in sr)),'valid_probe_partition_counts':dict(Counter(splits[r['task']] for r in sr)),'configurations':semout,'warning':'Existing file-level strict labels are audited judgments, not newly proved countermodels. No Lean compilation rerun.'})
    cells=a.read(a.E43/'results/full/cells.json')['cells'];old=a.read(a.E43/'results/analysis.json');assert len(cells)==90 and len({c['cell'] for c in cells})==90
    for c in cells:
        def mean(x):return statistics.mean(v for v in x if v is not None)
        start=mean(c['rescore_start']);final=start if c['final_is_start'] else mean(c['rescore_final']);gain=final-start
        ref=lambda z:statistics.mean(mean(m['scores']) for m in z['members'].values())
        rg=ref(c['reference_final'])-ref(c['reference_start']);gap=gain-rg
        assert abs(gain-c['attacked_gain'])<1e-10 and abs(rg-c['reference_gain'])<1e-10 and abs(gap-c['gaming_gap'])<1e-10
    gaming={}
    for judge in sorted({c['judge'] for c in cells}):
        rs=[c for c in cells if c['judge']==judge];views={}
        for split in ('train','val','test','all'):
            z=[c for c in rs if split=='all' or splits[c['task']]==split]
            views[split]={m:cluster_summary(z,m,draws) for m in ('attacked_gain','reference_gain','gaming_gap')}
            edited=[c for c in z if not c['final_is_start']]
            views[split].update(cells=len(z),edited=len(edited),flagged_edited=sum(c['checks']['flagged'] for c in edited))
        gaming[judge]=views
    edited=[c for c in cells if not c['final_is_start']]
    a.write('gaming_audit.json',{'cells':90,'attempts':sum(c['n_attempts'] for c in cells),'edited':len(edited),'flagged_edited':sum(c['checks']['flagged'] for c in edited),'partition_cells':dict(Counter(splits[c['task']] for c in cells)),'partition_tasks':{s:sorted({c['task'] for c in cells if splits[c['task']]==s}) for s in ('train','val','test')},'per_judge':gaming,'human_labels_for_edited_candidates':'unavailable','training_selector_status':'UNAVAILABLE_NO_TRAINING_TASK_ATTACKS','warning':'Human ratings of originals cannot score modified or repaired starts/finals; reference agreement does not establish attack validity.'})
    assert before==a.fingerprint();print('semantic configurations',len(semout),'gaming cells',len(cells),'edited',len(edited),'flagged',sum(c['checks']['flagged'] for c in edited),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--veribench',type=Path,required=True);p.add_argument('--draws',type=int,default=10000);args=p.parse_args();run(args.veribench,args.draws)
