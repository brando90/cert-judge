#!/usr/bin/env python3
"""Supplementary fixed historical judge-panel reanalysis; never reads old outcome labels."""
import argparse,csv,statistics
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
import analyze as a

def run(vb,draws):
    items,targets,meta,units,h,scores,raw=a.load(vb)
    itemmap={r['item']:r for r in items}
    e41=next((a.ROOT/'experiments').glob('41_*'))
    matched={r['gold_file'].removesuffix('.lean').replace('0_unsafeMultiply_safe','1_unsafeMultiply_safe') for r in csv.DictReader((e41/'results/provenance_by_task.csv').open()) if r['matched_pass1']=='yes'}
    v4=a.ROOT/'experiments/archive/04_veribench_validation';v13=a.ROOT/'experiments/archive/13_qwen_replication_exp16_exp19'
    files={'Codex':(v4/'results_exp16_final_robust_r9_median/detail_rows.csv',v4/'results_exp28_varaware_codex_avg_newindex/judge_trust_vector.csv'),'Claude_Opus':(v4/'results_exp16_opus47_r3_median/detail_rows.csv',v4/'results_exp28_varaware_opus_avg_newindex/judge_trust_vector.csv'),'Qwen3_Coder':(v13/'results/exp16_qwen_r3_median/detail_rows.csv',v4/'results_exp28_varaware_qwen_avg/judge_trust_vector.csv')}
    output={};hashes={}
    for family,(detail,trust) in files.items():
        hashes[str(detail.relative_to(a.ROOT))]=a.sha(detail);hashes[str(trust.relative_to(a.ROOT))]=a.sha(trust)
        scores=defaultdict(dict);repeats=defaultdict(dict)
        for r in csv.DictReader(detail.open()):
            if r['row_type']!='human_eval_union':continue
            gold,cand=r['item_key'].split('::',1);i=cand.removesuffix('.lean').replace('0_unsafeMultiply_safe','1_unsafeMultiply_safe');assert i in itemmap
            c=r['judge_id'];assert i not in scores[c];scores[c][i]=float(r['score_mean']);assert 0<=scores[c][i]<=1
            repeats[c][i]={'score_std':float(r['score_std']),'repeat_scores':r['repeat_scores']}
        trustrows=list(csv.DictReader(trust.open()));configs=[r['judge_id'] for r in trustrows];ti=np.array([float(r['TI_variance_aware']) for r in trustrows]);assert len(configs)==8
        for view in ('all','matched','train','val','test'):
            declared=[r for r in items if view=='all' or (view=='matched' and r['task'] in matched) or r['split']==view]
            rows=a.support(declared,configs,scores);ids=[r['item'] for r in rows]
            group=defaultdict(list)
            for j,r in enumerate(rows):group[r['task']].append(j)
            groups=[np.array(v,int) for k,v in sorted(group.items())];rng=np.random.default_rng(45);samples=rng.integers(0,len(groups),(draws,len(groups)))
            matrix=np.array([[scores[c][i] for i in ids] for c in configs]);report={}
            for target in ('all5','three'):
                y=np.array([targets[i][target] for i in ids]);point=a.stat_matrix(matrix,y,np.arange(len(ids)));boot=np.empty((draws,8,7));assoc=[]
                for j,g in enumerate(samples):
                    idx=np.concatenate([groups[k] for k in g]);boot[j]=a.stat_matrix(matrix,y,idx)
                    v=boot[j,:,0]
                    z=a.U.draw_correlations(ti[None,:],v,np.arange(len(ti))) if np.isfinite(v).all() else None
                    assoc.append([z[k][0] if z is not None else np.nan for k in ('spearman','pearson','kendall')])
                assoc=np.array(assoc,float);ap=a.U.corr(ti,point[:,0]);report[target]={'index_vs_agreement':{k:a.interval(ap[k],assoc[:,j]) for j,k in enumerate(('spearman','pearson','kendall'))},'per_judge':{c:{k:a.interval(point[j,m],boot[:,j,m]) for m,k in enumerate(a.METRICS)} for j,c in enumerate(configs)}}
            key=family+'__'+view;output[key]={'family':family,'view':view,'declared_items':len(declared),'common_items':len(rows),'tasks':len(groups),'item_ids':ids,'missing_item_ids':[r['item'] for r in declared if r not in rows],'coverage_gate_pass':len(rows)>=.9*len(declared),'interpretation':'Descriptive reference-matched and split sensitivity; preserve missing denominator. Historical reference match means repository reconstruction, not rater-session proof.','analysis':report,'repeat_evidence':{c:{i:repeats[c][i] for i in ids} for c in configs}}
            a.write('legacy/'+key+'.json',output[key]);print('legacy',key,len(ids),len(groups),flush=True)
    a.write('legacy_receipt.json',{'status':'COMPLETE','views':list(output),'source_hashes':hashes,'draws':draws,'seed':45,'historical_val_test_labels_used':0,'method':'Historical score_mean aggregation and TI_variance_aware fixed; paired task bootstrap; post-protocol supplementary descriptive analysis, not selection.'})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--veribench',type=Path,required=True);p.add_argument('--draws',type=int,default=10000);x=p.parse_args();(a.OUT/'legacy').mkdir(exist_ok=True);run(x.veribench,x.draws)
