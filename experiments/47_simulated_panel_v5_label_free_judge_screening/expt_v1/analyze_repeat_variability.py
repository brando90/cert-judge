"""Task-bootstrap uncertainty for observed within-item repeat variability."""
from collections import Counter
import numpy as np
from e47_adapter import RESULTS,read,write,RUN_ID
from statistics_v5 import interval
from analyze_campaign import clean

def summarize(items,values,draws=10000):
    tasks=sorted({r['task'] for r in items});lookup={r['item']:r for r in items};index={t:i for i,t in enumerate(tasks)}
    sums=np.zeros(len(tasks));counts=np.zeros(len(tasks));repeat_counts=Counter()
    for iid,value in values.items():
        if iid not in lookup or lookup[iid]['blank']:continue
        repeat_counts[value.get('complete_repeats','not_a_repeated_member')]+=1
        sd=value.get('raw_repeat_sample_sd')
        if sd is not None:
            i=index[lookup[iid]['task']];sums[i]+=sd;counts[i]+=1
    rng=np.random.default_rng(47);samples=rng.integers(0,len(tasks),(draws,len(tasks)))
    numerator=sums[samples].sum(axis=1);denominator=counts[samples].sum(axis=1)
    boot=np.divide(numerator,denominator,out=np.full(draws,np.nan),where=denominator>0)
    return {'declared_nonblank_units':sum(not r['blank'] and r['item'] in values for r in items),'units_with_repeat_variability':int(counts.sum()),'tasks':len(tasks),
            'accepted_repeat_count_distribution':dict(repeat_counts),'mean_within_item_sample_sd':interval(boot,sums.sum()/counts.sum() if counts.sum() else np.nan),
            'resampling':'tasks with all included items and raw-repeat units kept together; intervals condition on accepted repeats',
            'median_repeatability':'NOT_IDENTIFIABLE from one median aggregate per item; no invented independent aggregate repetitions'}

def main():
    items=read(RESULTS/'targets_reconstructed.json');values=read(RESULTS/'existing_v5_scores.json')
    result={proc:summarize([r for r in items if r['item'] in scores],scores) for proc,scores in values.items()}
    write(RESULTS/'existing_repeat_variability_intervals.json',clean({'run_id':RUN_ID,'seed':47,'draws':10000,'procedures':result}))
    print('Task intervals for raw-repeat variability:',len(result))

if __name__=='__main__':main()
