"""Task-paired estimators for the frozen simulated-panel experiment (seed 47).

All missing/constant values remain NaN internally and become JSON null at output.
Task draws are lists, never sets: sampled multiplicity is retained everywhere.
"""
from __future__ import annotations
from collections import Counter
from itertools import combinations
import hashlib
import math
import warnings
from functools import lru_cache
import numpy as np
from scipy.stats import rankdata, kendalltau

SEED=47
DRAWS=10000
METRICS=('spearman','pearson','kendall','mae','bias','judge_mean','panel_mean','judge_sd','panel_sd')
PRIMARY=('C_ms_gold','C_ident','C_bm_gold','C_blank','GM_mono2')
PROPERTIES=PRIMARY+('repeat_tvd','deletion_tvd','semantic_auc')

@lru_cache(maxsize=1)
def frozen_candidate_value():
    import sys
    from e47_adapter import ROOT,REPO,module
    sys.path.insert(0,str(REPO/'py_src'))
    return module('e47_frozen_analysis',ROOT/'vendor/e39/analysis_lib.py').candidate_value

def corr(x,y,kind='spearman'):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    keep=np.isfinite(x)&np.isfinite(y);x=x[keep];y=y[keep]
    if len(x)<2 or np.ptp(x)==0 or np.ptp(y)==0:return float('nan')
    if kind=='kendall':return float(kendalltau(x,y).statistic)
    if kind=='spearman':x=rankdata(x);y=rankdata(y)
    a=x-x.mean();b=y-y.mean()
    return float(np.dot(a,b)/np.sqrt(np.dot(a,a)*np.dot(b,b)))

def metrics(x,y):
    x=np.asarray(x,float);y=np.asarray(y,float)
    keep=np.isfinite(x)&np.isfinite(y);x=x[keep];y=y[keep]
    if not len(x):return np.full(len(METRICS),np.nan)
    return np.array([corr(x,y,k) for k in ('spearman','pearson','kendall')]+[
        np.abs(x-y).mean(),(x-y).mean(),x.mean(),y.mean(),
        x.std(ddof=1) if len(x)>1 else np.nan,y.std(ddof=1) if len(y)>1 else np.nan])

def interval(values,point=np.nan):
    a=np.asarray(values,float);a=a[np.isfinite(a)]
    return {'estimate':float(point),'interval_95':np.quantile(a,[.025,.975]).tolist() if len(a) else None,
            'finite_draws':len(a),'undefined_draws':len(values)-len(a),'draws':len(values),'p_val':None,
            'test':'none; descriptive percentile task bootstrap'}

def target_excluding(families,excluded):
    eligible=[v for k,v in families.items() if k not in excluded]
    values=[v for v in eligible if v is not None and math.isfinite(v)]
    need=max(3,math.ceil(2*len(eligible)/3))
    return sum(values)/len(values) if len(values)>=need else None

def task_folds(tasks):
    ordered=sorted(set(tasks),key=lambda t:hashlib.sha256((str(t)+'47').encode()).hexdigest())
    return {t:i%5 for i,t in enumerate(ordered)}

def draw_indices(task_ids,draw):
    """Expand each occurrence, even repeated tasks, and retain all paired rows."""
    task_ids=np.asarray(task_ids)
    return np.concatenate([np.flatnonzero(task_ids==task) for task in draw]) if len(draw) else np.array([],int)

def select_weights(values,tolerance=0.):
    a=np.asarray(values,float);w=np.zeros(len(a));ok=np.isfinite(a)
    if not ok.any():return w
    best=np.max(a[ok]);ties=ok&(np.abs(a-best)<=tolerance);w[ties]=1/ties.sum();return w

def expected(weights,values):
    selected=np.asarray(weights)>0;v=np.asarray(values,float)
    if not selected.any() or not np.isfinite(v[selected]).all():return np.nan
    return float(np.dot(np.asarray(weights)[selected],v[selected]))

def selection_statistics(properties,quality,h2,fixed=None,tolerance=0.):
    quality=np.asarray(quality,float);n=len(quality)
    weights=select_weights(properties,tolerance) if fixed is None else np.asarray(fixed,float)
    selected=expected(weights,quality)
    random=expected(np.ones(n)/n,quality)
    h2=np.asarray(h2,bool);hw=h2/h2.sum() if h2.any() else np.zeros(n)
    reference=expected(hw,quality)
    # A missing member does not disappear from the oracle's denominator.
    oracle=np.max(quality) if np.isfinite(quality).all() else np.nan
    return np.array([selected,oracle-selected,selected-reference,selected-random]),weights

SELECTION_METRICS=('selected_spearman','regret','gain_vs_H2','gain_vs_random')

class Panel:
    """Rows are declared items; columns are the complete declared judge pool.

    `property_records` holds config/component/task/item/value/eligible records.
    A missing value with eligible=True contributes to the coverage denominator.
    Every task occurrence in a bootstrap reweights numerator AND denominator.
    """
    def __init__(self,items,configs,scores,targets,property_records=(),base_models=None,provider_families=None):
        self.items=items;self.configs=configs;self.scores=np.asarray(scores,float);self.targets=np.asarray(targets,float)
        if len({r['item'] for r in items})!=len(items):raise ValueError('duplicate item')
        if len(set(configs))!=len(configs):raise ValueError('duplicate config')
        if self.scores.shape!=(len(items),len(configs)):raise ValueError('score shape')
        if self.targets.shape!=(len(items),):raise ValueError('target shape')
        self.task_ids=np.array([r['task'] for r in items]);self.tasks=sorted(set(self.task_ids));self.records=list(property_records)
        self.h2=np.array([c.endswith('|H2') for c in configs]);self.base=np.array(base_models if base_models is not None else [{'opus55x':'Opus','qwen36':'Qwen','t2_qwen':'Qwen','t2_sonnet5':'Sonnet'}[c.split('|')[0]] for c in configs])
        self.family=np.array(provider_families if provider_families is not None else ['Alibaba' if b=='Qwen' else 'Anthropic' for b in self.base])
        self.record_index={}
        self.aggregate_cache={}
        self.weighted_quality_cache={}
        seen=set()
        for r in self.records:
            key=(r['config'],r['component'],r['task'],r.get('item'))
            if key in seen:raise ValueError('duplicate property unit '+str(key))
            seen.add(key);self.record_index.setdefault((r['config'],r['component'],r['task']),[]).append(r)

    def property_values(self,task_draw=None,exclude_group=None):
        tasks=self.tasks if task_draw is None else list(task_draw)
        components=('ident','blank','ms_gold','ms_cand','bm_gold','repeat_tvd','deletion_tvd','semantic_auc')
        if exclude_group not in self.aggregate_cache:
            sums=np.zeros((8,len(self.configs),len(self.tasks)));obs=sums.copy();den=sums.copy()
            for j,cfg in enumerate(self.configs):
                for k,comp in enumerate(components):
                    for ti,t in enumerate(self.tasks):
                        rows=[r for r in self.record_index.get((cfg,comp,t),[]) if r.get('eligible',True) and (exclude_group is None or r.get('group')!=exclude_group)]
                        values=[r['value'] for r in rows if r.get('value') is not None and np.isfinite(r['value'])]
                        sums[k,j,ti]=sum(values);obs[k,j,ti]=len(values);den[k,j,ti]=len(rows)
            self.aggregate_cache[exclude_group]=(sums,obs,den)
        counts=Counter(tasks);multiplicity=np.array([counts[t] for t in self.tasks])
        sums,obs,den=[a@multiplicity for a in self.aggregate_cache[exclude_group]]
        with np.errstate(invalid='ignore',divide='ignore'):v=np.where((den>0)&(obs>=np.ceil(.8*den)),sums/obs,np.nan)
        result={p:v[k].copy() for p,k in [('C_ident',0),('C_blank',1),('C_ms_gold',2),('C_bm_gold',4),('repeat_tvd',5),('deletion_tvd',6),('semantic_auc',7)]}
        compose=frozen_candidate_value()
        result['GM_mono2']=np.array([compose('GM_mono2',{'ms_gold':{'value':float(a) if np.isfinite(a) else None},'ms_cand':{'value':float(b) if np.isfinite(b) else None}}, {}) for a,b in zip(v[2],v[3])],float)
        coverage={(cfg,comp):(int(obs[k,j]),int(den[k,j])) for j,cfg in enumerate(self.configs) for k,comp in enumerate(components)}
        return result,coverage

    def support(self,indices=None,columns=None):
        idx=np.arange(len(self.items)) if indices is None else np.asarray(indices,int)
        cols=np.arange(len(self.configs)) if columns is None else np.asarray(columns,int)
        mask=np.isfinite(self.targets[idx])&np.isfinite(self.scores[np.ix_(idx,cols)]).all(axis=1)
        common=idx[mask]
        return common,{'declared':len(idx),'observed':len(common),'coverage':len(common)/len(idx) if len(idx) else 0.,
                       'status':'COMPUTED' if len(idx) and len(common)>=math.ceil(.9*len(idx)) else 'NOT_COMPUTABLE'}

    def qualities(self,idx,columns):
        return np.array([corr(self.scores[idx,j],self.targets[idx]) for j in columns])

    def weighted_task_qualities(self,task_draw,columns):
        """Exactly retain sampled task multiplicity without expanding repeated rows.

        Weighted midranks equal ordinary midranks of the expanded multiset,
        including ties. This accelerates larger-task-count power simulations.
        """
        cols=tuple(int(j) for j in columns)
        if cols not in self.weighted_quality_cache:
            mask=np.isfinite(self.targets)&np.isfinite(self.scores[:,cols]).all(axis=1)
            matrix=np.column_stack((self.scores[mask][:,cols],self.targets[mask]))
            inverse=[np.unique(matrix[:,j],return_inverse=True)[1] for j in range(matrix.shape[1])]
            self.weighted_quality_cache[cols]=(mask,inverse)
        mask,inverse=self.weighted_quality_cache[cols];counts=Counter(task_draw)
        weights=np.array([counts[t] for t in self.task_ids],float);declared=weights.sum();w=weights[mask];observed=w.sum()
        support={'declared':int(declared),'observed':int(observed),'status':'COMPUTED' if declared and observed>=math.ceil(.9*declared) else 'NOT_COMPUTABLE'}
        q=np.full(len(cols),np.nan)
        if support['status']!='COMPUTED' or observed<2:return q,support
        ranks=[]
        for inv in inverse:
            mass=np.bincount(inv,weights=w);ranks.append((np.cumsum(mass)-(mass-1)/2)[inv])
        centered=[r-(observed+1)/2 for r in ranks];target=centered[-1];yv=np.dot(w,target*target)
        for j,x in enumerate(centered[:-1]):
            xv=np.dot(w,x*x)
            if xv>0 and yv>0:q[j]=np.dot(w,x*target)/np.sqrt(xv*yv)
        return q,support

    def criterion(self,draws=DRAWS,seed=SEED):
        rng=np.random.default_rng(seed);task_draws=[rng.choice(self.tasks,len(self.tasks),replace=True) for _ in range(draws)]
        out={}
        for j,cfg in enumerate(self.configs):
            available=np.isfinite(self.targets)&np.isfinite(self.scores[:,j]);n=int(available.sum())
            ok=n>=math.ceil(.9*len(self.items));point=metrics(self.scores[available,j],self.targets[available]) if ok else np.full(len(METRICS),np.nan)
            samples=np.full((draws,len(METRICS)),np.nan)
            if ok:
                for b,td in enumerate(task_draws):
                    ix=draw_indices(self.task_ids,td);keep=available[ix]
                    if keep.sum()>=math.ceil(.9*len(ix)):samples[b]=metrics(self.scores[ix[keep],j],self.targets[ix[keep]])
            out[cfg]={'declared':len(self.items),'observed':n,'tasks':len(set(self.task_ids[available])),'coverage':n/len(self.items) if len(self.items) else 0.,'status':'COMPUTED' if ok else 'NOT_COMPUTABLE',
                      'metrics':{k:interval(samples[:,i],point[i]) for i,k in enumerate(METRICS)}}
        return out

    def evaluate(self,draws=DRAWS,seed=SEED,columns=None,train_tasks=None,test_indices=None,exclude_group=None):
        cols=np.arange(len(self.configs)) if columns is None else np.asarray(columns,int)
        train=self.tasks if train_tasks is None else list(train_tasks)
        test=np.arange(len(self.items)) if test_indices is None else np.asarray(test_indices,int)
        common,support=self.support(test,cols);props,_=self.property_values(train,exclude_group)
        qualities=self.qualities(common,cols) if support['status']=='COMPUTED' else np.full(len(cols),np.nan)
        fixed={p:select_weights(v[cols],1e-12 if p in ('repeat_tvd','deletion_tvd','semantic_auc') else 0.) for p,v in props.items()}
        assoc_point={p:[corr(v[cols],qualities,k) if (np.isfinite(v[cols])&np.isfinite(qualities)).sum()>=3 else np.nan for k in ('spearman','pearson','kendall')] for p,v in props.items()}
        select_point={p:selection_statistics(v[cols],qualities,self.h2[cols],fixed[p])[0] for p,v in props.items()}
        def control_values(q):
            h=self.h2[cols];hw=h/h.sum() if h.any() else np.zeros(len(cols))
            return [expected(np.ones(len(cols))/len(cols),q),expected(hw,q),float(np.max(q)) if np.isfinite(q).all() else np.nan]
        control_point=control_values(qualities);control_samples=np.full((draws,3),np.nan);random_draws=np.full((draws,2),np.nan)
        control_rng=np.random.default_rng(np.random.SeedSequence(seed,spawn_key=(1,)))
        samples={p:np.full((draws,4),np.nan) for p in PROPERTIES};conditional={p:np.full((draws,4),np.nan) for p in PROPERTIES};assoc={p:np.full((draws,3),np.nan) for p in PROPERTIES}
        rng=np.random.default_rng(seed);test_tasks=sorted(set(self.task_ids[test]));bases=sorted(set(self.base[cols]))
        paired_universe=sorted(set(train)|set(test_tasks));overlap=bool(set(train)&set(test_tasks))
        for b in range(draws):
            # Pooled/group analyses share exactly the same task draw in both
            # properties and criterion. Disjoint task-fold splits resample each
            # partition separately while retaining pairings within each.
            if overlap:
                td=rng.choice(paired_universe,len(paired_universe),replace=True)
                tr=[t for t in td if t in train]
            else:
                td=rng.choice(test_tasks,len(test_tasks),replace=True)
                tr=rng.choice(train,len(train),replace=True)
            ix=draw_indices(self.task_ids[test],td);indices=test[ix]
            observed,coverage=self.support(indices,cols)
            q=self.qualities(observed,cols) if coverage['status']=='COMPUTED' else np.full(len(cols),np.nan)
            control_samples[b]=control_values(q);random_draws[b,0]=q[control_rng.integers(len(cols))]
            h2_positions=np.flatnonzero(self.h2[cols])
            if len(h2_positions):random_draws[b,1]=q[control_rng.choice(h2_positions)]
            pv,_=self.property_values(tr,exclude_group)
            cluster_draw=rng.choice(bases,len(bases),replace=True)
            clustered=np.concatenate([np.flatnonzero(self.base[cols]==base) for base in cluster_draw])
            for p,v in pv.items():
                tolerance=1e-12 if p in ('repeat_tvd','deletion_tvd','semantic_auc') else 0.
                samples[p][b]=selection_statistics(v[cols],q,self.h2[cols],tolerance=tolerance)[0]
                conditional[p][b]=selection_statistics(v[cols],q,self.h2[cols],fixed[p])[0]
                x,y=v[cols][clustered],q[clustered]
                if (np.isfinite(x)&np.isfinite(y)).sum()>=3:assoc[p][b]=[corr(x,y,k) for k in ('spearman','pearson','kendall')]
        result={'support':support,'configs':[self.configs[j] for j in cols],'base_models':bases,'base_model_count':len(bases),'provider_family_count':len(set(self.family[cols])),'properties':{}}
        result['controls']={'exact_expectations':{k:interval(control_samples[:,i],control_point[i]) for i,k in enumerate(('uniform_random','uniform_H2','hindsight_oracle'))},
                            'seeded_single_judge_variability':{k:{**interval(random_draws[:,i],control_point[i]),'interpretation':'95% distribution interval combining task resampling and one uniformly sampled judge; not a confidence interval for the exact expectation','test':'none; seeded selector variability'} for i,k in enumerate(('uniform_random','uniform_H2'))},
                            'declared_pool_size':len(cols),'declared_H2_count':int(self.h2[cols].sum()),'seed':seed}
        for p in PROPERTIES:
            finite=np.isfinite(props[p][cols])&np.isfinite(qualities)
            result['properties'][p]={'values':props[p][cols].tolist(),'weights':fixed[p].tolist(),'eligible_configurations':int(np.isfinite(props[p][cols]).sum()),
                'finite_association_configurations':int(finite.sum()),'finite_association_base_models':len(set(self.base[cols][finite])),'finite_association_provider_families':len(set(self.family[cols][finite])),
                'association':{k:interval(assoc[p][:,i],assoc_point[p][i]) for i,k in enumerate(('spearman','pearson','kendall'))},
                'unconditional_selection':{k:interval(samples[p][:,i],select_point[p][i]) for i,k in enumerate(SELECTION_METRICS)},
                'conditional_fixed_selection':{k:interval(conditional[p][:,i],select_point[p][i]) for i,k in enumerate(SELECTION_METRICS)}}
        return result

def planning(panel,property_name,draws=DRAWS,seed=SEED,subset_draws=100):
    """Nested pool/task resampling; fixed +.10 alternative shifts centered gains.

    Uses all feasible subsets when <=100, otherwise 100 seeded distinct subsets.
    Each task draw reruns selection. No new scores/families are simulated.
    """
    rng=np.random.default_rng(seed);result=[];n=len(panel.configs)
    component={'C_ms_gold':'ms_gold','C_ident':'ident','C_bm_gold':'bm_gold','C_blank':'blank','GM_mono2':'ms_cand'}.get(property_name,property_name)
    if not any(r['component']==component and r.get('eligible',True) and r.get('value') is not None and np.isfinite(r['value']) for r in panel.records):
        return {'status':'NOT_COMPUTABLE','reason':'no accepted eligible property measurement; resampling cannot create one','draws':draws,'finite_draws':0,'new_family_requirement':'NOT_IDENTIFIABLE'}
    for size in (4,6,8,12):
        if size>n:continue
        feasible=list(combinations(range(n),size))
        if len(feasible)>subset_draws:feasible=[feasible[i] for i in sorted(rng.choice(len(feasible),subset_draws,replace=False))]
        for task_count in (25,50,100,200,400):
            gains=[];bases=[];subset_ids=[]
            for b in range(draws):
                cols=np.array(feasible[b%len(feasible)]);td=rng.choice(panel.tasks,task_count,replace=True)
                q,support=panel.weighted_task_qualities(td,cols)
                if support['status']!='COMPUTED':continue
                p,_=panel.property_values(td)
                tolerance=1e-12 if property_name in ('repeat_tvd','deletion_tvd','semantic_auc') else 0.
                gain=selection_statistics(p[property_name][cols],q,panel.h2[cols],tolerance=tolerance)[0][2]
                if np.isfinite(gain):gains.append(gain);bases.append(len(set(panel.base[cols])));subset_ids.append(b%len(feasible))
            a=np.array(gains);row={'pool_size':size,'tasks':task_count,'subset_count':len(feasible),'draws':draws,'finite_draws':len(a),'status':'COMPUTED' if len(a) else 'NOT_COMPUTABLE','new_family_requirement':'NOT_IDENTIFIABLE'}
            if len(a):
                # Center within each fixed subpool before mixing null draws;
                # differences in observed subpool effects are not null noise.
                labels=np.array(subset_ids);centered=a.copy()
                for label in np.unique(labels):centered[labels==label]-=a[labels==label].mean()
                critical=float(np.quantile(centered,.975));success=int(np.sum(centered+.10>critical));power=success/len(a)
                # Wilson Monte Carlo interval, distinct from scientific uncertainty.
                z=1.959963984540054;den=1+z*z/len(a);mid=(power+z*z/(2*len(a)))/den;half=z*math.sqrt(power*(1-power)/len(a)+z*z/(4*len(a)**2))/den
                row.update(power=power,mc_interval_95=[mid-half,mid+half],rejections=success,centered_null_threshold_975=critical,alternative_shift=.10,target_power=.80,base_model_counts=dict(Counter(bases)))
            result.append(row)
    return result

def equal_group_transfer(panels,draws=DRAWS,seed=SEED):
    """Equal weight per held-out group, paired across a common task bootstrap.

    Each panel's property records must already exclude its held-out candidates.
    Missing group statistics stay missing in the equal-group average.
    """
    groups=sorted(panels);tasks=sorted(set.intersection(*(set(p.tasks) for p in panels.values())))
    if not groups or not tasks:raise ValueError('groups and shared tasks required')
    fixed={};indices={};point_rows={p:[] for p in PROPERTIES}
    for group,panel in panels.items():
        indices[group]=np.array([i for i,r in enumerate(panel.items) if r['group']==group])
        props,_=panel.property_values(tasks,group);common,support=panel.support(indices[group])
        q=panel.qualities(common,np.arange(len(panel.configs))) if support['status']=='COMPUTED' else np.full(len(panel.configs),np.nan)
        fixed[group]={}
        for prop in PROPERTIES:
            tol=1e-12 if prop not in PRIMARY else 0.
            value,weights=selection_statistics(props[prop],q,panel.h2,tolerance=tol)
            fixed[group][prop]=weights;point_rows[prop].append(value)
    samples={p:np.full((draws,4),np.nan) for p in PROPERTIES};conditional={p:a.copy() for p,a in samples.items()}
    rng=np.random.default_rng(seed)
    for b in range(draws):
        td=rng.choice(tasks,len(tasks),replace=True);values={p:[] for p in PROPERTIES};cond={p:[] for p in PROPERTIES}
        for group,panel in panels.items():
            original=indices[group];ix=original[draw_indices(panel.task_ids[original],td)]
            common,support=panel.support(ix);q=panel.qualities(common,np.arange(len(panel.configs))) if support['status']=='COMPUTED' else np.full(len(panel.configs),np.nan)
            props,_=panel.property_values(td,group)
            for prop in PROPERTIES:
                values[prop].append(selection_statistics(props[prop],q,panel.h2,tolerance=1e-12 if prop not in PRIMARY else 0.)[0])
                cond[prop].append(selection_statistics(props[prop],q,panel.h2,fixed[group][prop])[0])
        for prop in PROPERTIES:
            samples[prop][b]=np.mean(values[prop],axis=0);conditional[prop][b]=np.mean(cond[prop],axis=0)
    return {'groups':groups,'group_count':len(groups),'tasks':len(tasks),'resampling':'same task draw across every group; group selectors recomputed; equal weights; any undefined group makes its mean undefined',
            'properties':{p:{'unconditional_selection':{k:interval(samples[p][:,i],np.mean(point_rows[p],axis=0)[i]) for i,k in enumerate(SELECTION_METRICS)},
                             'conditional_fixed_selection':{k:interval(conditional[p][:,i],np.mean(point_rows[p],axis=0)[i]) for i,k in enumerate(SELECTION_METRICS)}} for p in PROPERTIES}}

def recommendation(primary,common,prop,declared=12):
    a=primary['properties'][prop];b=common['properties'][prop]
    if min(a['eligible_configurations'],b['eligible_configurations'])<math.ceil(.9*declared):return 'DROP_UNCOMPUTABLE'
    if np.nanstd(np.asarray(a['values'],float))==0:return 'DROP_CONSTANT'
    gains=[x['unconditional_selection']['gain_vs_H2'] for x in (a,b)]
    if any(g['interval_95'] is not None and g['interval_95'][1]<=0 for g in gains):return 'DROP_NONPOSITIVE_GAIN'
    if all(x['association']['spearman']['estimate'] is not None and x['association']['spearman']['estimate']>0 for x in (a,b)) and all(g['estimate'] is not None and g['estimate']>0 for g in gains):
        return 'STRONG_FOLLOWUP' if all(g['interval_95'] is not None and g['interval_95'][0]>0 for g in gains) else 'INCONCLUSIVE_POSITIVE_POINT_ESTIMATE'
    return 'INCONCLUSIVE'
