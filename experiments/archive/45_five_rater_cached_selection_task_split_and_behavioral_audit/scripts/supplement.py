"""Descriptive completion: frozen proxy association and individual current raters."""
import argparse
from collections import defaultdict
import math
import numpy as np
import analyze as a


def samples(rows,draws):
    groups=defaultdict(list)
    for j,r in enumerate(rows):groups[r['task']].append(j)
    groups=[np.array(v,int) for k,v in sorted(groups.items())]
    picks=np.random.default_rng(45).integers(0,len(groups),(draws,len(groups)))
    return [np.concatenate([groups[k] for k in draw]) for draw in picks]


def run(vb,draws):
    before=a.fingerprint()
    items,targets,meta,units,harvest,scores,raw=a.load(vb)
    individual=[{'item':r['item'],'task':r['task'],'split':r['split'],
        'ratings_0_to_5':dict(zip(('participant1','participant2','participant3','participant4','participant5'),targets[r['item']]['raters'])),
        'current5_mean_0_to_1':targets[r['item']]['all5'],
        'current3_mean_0_to_1':targets[r['item']]['three']} for r in items]
    a.write('individual_current_ratings.json',individual)
    output={}
    for view in ('original45','test'):
        rows=[r for r in items if r['split'] in ('val','test')] if view=='original45' else [r for r in items if r['split']=='test']
        ids=[r['item'] for r in rows];draw_indices=samples(rows,draws)
        groups=defaultdict(list)
        for c in meta:
            mask=tuple(i in scores[c] for i in ids)
            if sum(mask)>=math.ceil(.9*len(ids)):groups[mask].append(c)
        criterion={};coverage={}
        for mask,configs in groups.items():
            valid=np.array(mask,bool);positions=np.flatnonzero(valid);matrix=np.array([[scores[c].get(i,np.nan) for i in ids] for c in configs])
            for target in ('all5','three'):
                y=np.array([targets[i][target] for i in ids]);point=a.U.draw_correlations(matrix,y,positions)['spearman']
                boot=np.array([a.U.draw_correlations(matrix,y,idx[valid[idx]])['spearman'] for idx in draw_indices])
                for j,c in enumerate(configs):criterion[c,target]=(point[j],boot[:,j])
            for c in configs:coverage[c]={'n':int(sum(mask)),'declared':len(ids),'missing':[i for i,m in zip(ids,mask) if not m]}
        for split in ('train','val','test'):
            pool=[c for c in meta if meta[c]['split']==split]
            for index in ('C_ms_gold','C_ident','PTI_v0_frozen','TI_var_trainnorm'):
                selected=[c for c in pool if units[c]['indices'].get(index) is not None and (c,'all5') in criterion and np.isfinite(criterion[c,'all5'][0]) and np.isfinite(criterion[c,'three'][0])]
                proxy=np.array([units[c]['indices'][index] for c in selected]);result={};bs={}
                for target in ('all5','three'):
                    point=np.array([criterion[c,target][0] for c in selected]);boot=np.array([criterion[c,target][1] for c in selected]).T
                    corr=a.U.corr(proxy,point);b=a.U.draw_correlations(boot,proxy,np.arange(len(proxy)))
                    result[target]={k:a.interval(corr[k],b[k]) for k in ('spearman','pearson','kendall')};bs[target]=b
                    if view=='original45' and target=='three':
                        frozen=a.U.corr(proxy,[units[c]['criteria']['heldout']['spearman'] for c in selected])
                        for k in frozen:
                            assert (corr[k] is None and frozen[k] is None) or abs(corr[k]-frozen[k])<1e-10
                key=f'{view}__judge_{split}__{index}'
                output[key]={'criterion_task_view':view,'judge_model_split':split,'index':index,'declared_judges':len(pool),'included_judges':len(selected),'included':selected,'excluded':[c for c in pool if c not in selected],'criterion_support':{c:coverage[c] for c in selected},'association':result,'target_difference':{k:a.interval(None if result['all5'][k]['value'] is None or result['three'][k]['value'] is None else result['all5'][k]['value']-result['three'][k]['value'],bs['all5'][k]-bs['three'][k]) for k in bs['all5']}}
        print('proxy associations',view,flush=True)
    a.write('proxy_associations.json',{'draws':draws,'seed':45,'conditional_on_fixed_judge_panel':True,'comparisons':output})
    human={}
    for view in ('train','val','test','all'):
        for rater in range(5):
            rows=[r for r in items if (view=='all' or r['split']==view) and targets[r['item']]['raters'][rater] is not None]
            ratings=[targets[r['item']]['raters'] for r in rows]
            x=np.array([[v[rater]/5 for v in ratings]]);y=np.array([np.mean([s/5 for j,s in enumerate(v) if j!=rater and s is not None]) for v in ratings])
            point=a.stat_matrix(x,y,np.arange(len(rows)))[0];boot=np.array([a.stat_matrix(x,y,idx)[0] for idx in samples(rows,draws)])
            human[f'{view}__participant{rater+1}']={'items':len(rows),'tasks':len({r['task'] for r in rows}),'metrics':{k:a.interval(point[j],boot[:,j]) for j,k in enumerate(a.METRICS)},'bias_definition':'rater minus mean of other current raters; positive means lenient'}
        print('individual raters',view,flush=True)
    a.write('rater_agreement.json',{'draws':draws,'seed':45,'resampling_unit':'task','entries':human})
    assert before==a.fingerprint()
    a.write('supplement_receipt.json',{'status':'COMPLETE','draws':draws,'seed':45,'source_hashes':before,'script_sha256':a.sha(a.EXP/'scripts/supplement.py'),'individual_items':len(individual),'current_observations':sum(v is not None for r in individual for v in r['ratings_0_to_5'].values()),'historical_val_test_labels_used':0,'inference_calls':0})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--veribench',type=a.Path,required=True);p.add_argument('--draws',type=int,default=10000);args=p.parse_args();run(args.veribench,args.draws)
