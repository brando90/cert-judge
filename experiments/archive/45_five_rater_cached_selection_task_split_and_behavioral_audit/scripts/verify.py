"""Verify complete artifacts against frozen sources and independent SciPy statistics."""
import argparse
import math
import statistics
from collections import Counter
import numpy as np
from scipy.stats import spearmanr, pearsonr, kendalltau
import analyze as a


def run(vb):
    seal=a.read(a.OUT/'SELECTION.json')
    assert a.fingerprint()==seal['source_hashes']
    assert seal['selected_rule'] is None and seal['selected_weights'] is None
    assert seal['selection_status']=='UNAVAILABLE_VALIDATION_SHARED_SUPPORT'
    assert seal['common_validation_items']==13 and seal['validation_required_items']==14
    assert seal['historical_train_observations']==60 and seal['historical_val_test_observations_used']==0
    inventory=a.read(a.OUT/'inventory.json')
    for r in a.read(a.OUT/'input_files.json'):
        assert a.sha(vb/r['path'])==r['sha256']
    items,targets,meta,units,harvest,scores,raw=a.load(vb)
    individuals=a.read(a.OUT/'individual_current_ratings.json')
    assert len(individuals)==75 and sum(v is not None for r in individuals for v in r['ratings_0_to_5'].values())==345
    for r in individuals:
        v=targets[r['item']]
        assert list(r['ratings_0_to_5'].values())==v['raters']
        assert r['current5_mean_0_to_1']==v['all5'] and r['current3_mean_0_to_1']==v['three']
    receipt=a.read(a.OUT/'analysis_receipt.json');assert len(receipt['comparisons'])==42
    counts=Counter();points=0
    for key,info in receipt['comparisons'].items():
        path=a.OUT/'comparisons'/f'{key}.json';assert a.sha(path)==info['sha256'];r=a.read(path);counts[r['status']]+=1
        assert r['common_items']+len(r['missing_item_ids'])==r['declared_items']
        assert r['draws']==10000 and r['seed']==45
        if r['status']!='COMPUTED':
            assert r['common_items']<math.ceil(.9*r['declared_items']);continue
        ids=r['item_ids'];assert len(ids)==r['common_items']
        for target in ('all5','three'):
            y=np.array([targets[i][target] for i in ids]);per={}
            for c in r['configs']:
                x=np.array([scores[c][i] for i in ids]);delta=x-y
                corr=[spearmanr(x,y).statistic,pearsonr(x,y).statistic,kendalltau(x,y).statistic]
                per[c]=dict(zip(a.METRICS,[*corr,np.abs(delta).mean(),delta.mean(),x.mean(),y.mean()]))
            for name,z in r['analysis'][target]['selectors'].items():
                for metric,stored in z['metrics'].items():
                    expected=sum(w*per[c][metric] for c,w in z['weights'].items()) if z['weights'] else float('nan')
                    assert (stored['value'] is None and not math.isfinite(expected)) or abs(stored['value']-expected)<1e-10,(key,target,name,metric)
                    assert stored['valid_draws']+stored['undefined_draws']==10000
                    points+=1
    assert counts=={'COMPUTED':34,'UNAVAILABLE_SHARED_SUPPORT':8}
    for name in ('legacy_receipt.json','supplement_receipt.json'):
        r=a.read(a.OUT/name);assert r['status']=='COMPLETE' and r['draws']==10000
        for path,digest in r['source_hashes'].items():
            p=a.ROOT/path
            if path=='experiments/'+a.EXP.name+'/PROTOCOL.md':p=a.EXP/'PROTOCOL.md'
            assert a.sha(p)==digest
    assert len(a.read(a.OUT/'legacy_receipt.json')['views'])==15
    assert len(a.read(a.OUT/'proxy_associations.json')['comparisons'])==24
    assert len(a.read(a.OUT/'rater_agreement.json')['entries'])==20
    semantic=a.read(a.OUT/'semantic_audit.json');assert semantic['reproduced_configurations']==60 and semantic['maximum_point_difference']<1e-10
    gaming=a.read(a.OUT/'gaming_audit.json');assert gaming['cells']==90 and gaming['attempts']==720 and gaming['partition_cells']=={'test':54,'val':36}
    proposal=a.read(a.OUT/'followup_manifest.json');assert proposal['new_calls_made']==0 and proposal['admission_authorized'] is False
    print(f'PASS: {points} independent point-statistic checks; 177 input hashes; 42 views (34 computed, 8 unavailable); 345 individual ratings; 24 proxy views; 15 historical views; 20 rater views; 60 semantic configurations; 90 attack cells.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--veribench',type=a.Path,required=True);run(p.parse_args().veribench)
