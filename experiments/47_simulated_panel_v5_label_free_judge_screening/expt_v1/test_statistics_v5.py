"""Decisive synthetic controls for admission, missingness and selection uncertainty."""
import unittest
import numpy as np
import statistics_v5 as S
from receipt_validation import accepted,unique_repeats
from e47_adapter import module,ROOT
I=module('e47_owner_information',ROOT/'vendor/information_properties_addeba2.py')

class StatisticsTests(unittest.TestCase):
    def test_composition_calls_frozen_candidate_deletion_formula(self):
        cfg='opus55x|H2';rows=[{'item':'i','task':'t'}]
        records=[{'config':cfg,'component':comp,'task':'t','value':value} for comp,value in [('ms_gold',.8),('ms_cand',.3),('bm_gold',1.)]]
        p=S.Panel(rows,[cfg],[[.5]],[.5],records)
        got=p.property_values()[0]['GM_mono2'][0]
        self.assertEqual(got,S.frozen_candidate_value()('GM_mono2',{'ms_gold':{'value':.8},'ms_cand':{'value':.3}},{}))
        self.assertNotEqual(got,np.sqrt(.8))

    def test_weighted_bootstrap_matches_literal_repeated_rows_with_ties(self):
        rng=np.random.default_rng(47);rows=[{'item':str(i),'task':str(i//4)} for i in range(40)]
        scores=rng.choice([0.,.2,.7,1.],size=(40,3));scores[0,1]=np.nan;target=rng.choice([0.,.5,1.],size=40)
        p=S.Panel(rows,['opus55x|H2','qwen36|D0','t2_qwen|H2'],scores,target)
        for count in (5,10,40):
            for _ in range(10):
                td=rng.choice(p.tasks,count,replace=True);cols=np.array([0,1,2]);weighted,support=p.weighted_task_qualities(td,cols)
                expanded=S.draw_indices(p.task_ids,td);common,reference=p.support(expanded,cols)
                self.assertEqual(support['observed'],reference['observed']);self.assertEqual(support['status'],reference['status'])
                expected=p.qualities(common,cols) if reference['status']=='COMPUTED' else np.full(3,np.nan)
                np.testing.assert_allclose(weighted,expected,atol=1e-14,equal_nan=True)

    def test_group_missing_tasks_preserves_property_criterion_bootstrap_pairing(self):
        from collections import Counter
        rows=[{'item':t,'task':t} for t in ('a','b','c')]
        p=S.Panel(rows,['opus55x|H2','qwen36|D0'],[[0,1],[1,0],[.5,.5]],[0,1,.5])
        property_draws=[];criterion_draws=[];old_property=p.property_values;old_support=p.support
        def prop(draw=None,exclude_group=None):
            property_draws.append(list(draw));return old_property(draw,exclude_group)
        def support(indices=None,columns=None):
            criterion_draws.append(list(p.task_ids[indices]));return old_support(indices,columns)
        p.property_values=prop;p.support=support;p.evaluate(draws=30,test_indices=[0,1])
        for properties,criterion in zip(property_draws[1:],criterion_draws[1:]):
            self.assertEqual(Counter(t for t in properties if t in ('a','b')),Counter(criterion))

    def test_random_baseline_uses_expectation_and_separate_draw_variability(self):
        rows=[{'item':f'{t}{i}','task':t} for t in ('a','b') for i in range(3)]
        p=S.Panel(rows,['opus55x|H2','qwen36|D0'],[[0,1],[.5,.5],[1,0]]*2,[0,.5,1]*2)
        controls=p.evaluate(draws=100)['controls']
        self.assertAlmostEqual(controls['exact_expectations']['uniform_random']['estimate'],0.)
        self.assertAlmostEqual(controls['exact_expectations']['uniform_H2']['estimate'],1.)
        self.assertEqual(controls['seeded_single_judge_variability']['uniform_random']['interval_95'],[-1.,1.])

    def test_equal_group_mean_does_not_weight_large_groups_more(self):
        configs=['opus55x|H2','qwen36|D0'];rows=[];scores=[];targets=[]
        for group,repetitions in [('small',1),('large',4)]:
            for t in range(3):
                for k in range(repetitions):
                    rows.append({'item':f'{group}{t}{k}','task':str(t),'group':group});targets.append(t/2)
                    scores.append([t/2,1-t/2])
        panels={}
        for group in ['small','large']:
            records=[{'config':cfg,'component':'ident','task':str(t),'value':int((group=='small')==(j==1))} for j,cfg in enumerate(configs) for t in range(3)]
            panels[group]=S.Panel(rows,configs,scores,targets,records)
        result=S.equal_group_transfer(panels,draws=20)['properties']['C_ident']['unconditional_selection']
        self.assertAlmostEqual(result['selected_spearman']['estimate'],0.)
        self.assertAlmostEqual(result['gain_vs_H2']['estimate'],-1.)

    def test_unavailable_semantic_planning_does_not_invent_draws(self):
        p=S.Panel([{'item':'a','task':'a'}],['opus55x|H2'],[[.2]],[.2])
        result=S.planning(p,'semantic_auc')
        self.assertEqual(result['status'],'NOT_COMPUTABLE');self.assertEqual(result['finite_draws'],0);self.assertEqual(result['draws'],10000)

    def test_task_multiplicity_and_pairing(self):
        self.assertEqual(S.draw_indices(['a','a','b','c'],['b','a','b']).tolist(),[2,0,1,2])
        rows=[{'item':str(i),'task':t} for i,t in enumerate(['a','b'])]
        records=[{'config':'qwen36|H2','component':'ms_gold','task':t,'value':v} for t,v in [('a',1),('b',0)]]
        panel=S.Panel(rows,['qwen36|H2'],[[.2],[.9]],[.2,.9],records)
        self.assertAlmostEqual(panel.property_values(['a','a','b'])[0]['C_ms_gold'][0],2/3)

    def test_qwen_harness_is_one_cluster(self):
        p=S.Panel([{'item':'a','task':'a'}],['qwen36|H2','t2_qwen|H2'],[[.1,.2]],[.3])
        self.assertEqual(set(p.base),{'Qwen'})

    def test_shift_changes_agreement_not_rank(self):
        m=S.metrics([.2,.4,.6],[.1,.3,.5]);self.assertAlmostEqual(m[0],1);self.assertAlmostEqual(m[3],.1);self.assertAlmostEqual(m[4],.1)

    def test_constant_is_undefined(self):
        self.assertTrue(np.isnan(S.corr([1,1],[0,1])))
        self.assertEqual(I.repeat_tvd_task({'a':{1:.1,2:.1,3:.1},'b':{1:.1,2:.1,3:.1}}),0)

    def test_ties_expected_selection_and_regret(self):
        v,w=S.selection_statistics([1,1,0],[.2,.8,.5],[True,False,True])
        np.testing.assert_equal(w,[.5,.5,0]);self.assertAlmostEqual(v[0],.5);self.assertAlmostEqual(v[1],.3);self.assertAlmostEqual(v[2],.15)

    def test_missing_oracle_member_is_not_dropped(self):
        v,w=S.selection_statistics([1,0,np.nan],[.7,.3,np.nan],[True,False,False])
        self.assertAlmostEqual(v[0],.7);self.assertTrue(np.isnan(v[1]));self.assertTrue(np.isnan(v[3]))

    def test_common_mask_preserves_declared_pool(self):
        rows=[{'item':str(i),'task':str(i)} for i in range(10)]
        scores=np.zeros((10,2));scores[:2,1]=np.nan
        p=S.Panel(rows,['opus55x|H2','qwen36|H2'],scores,np.arange(10)/10)
        self.assertEqual(p.support()[1]['status'],'NOT_COMPUTABLE');self.assertEqual(p.support(columns=[0])[1]['status'],'COMPUTED')

    def test_repeat_tvd_two_complete_candidates_suffice(self):
        complete,excluded=I.complete_repeat_candidates({'a':{1:.1,2:.1,3:.1},'b':{1:.9,2:.9,3:.9},'c':{1:.5}})
        self.assertEqual(excluded,['c']);self.assertEqual(I.repeat_tvd_task(complete),.5)

    def test_exact_bin_permutation_invariance(self):
        values={'a':{1:.01,2:.21,3:.01},'b':{1:.41,2:.81,3:.61},'c':{1:.81,2:.41,3:.61}}
        permutation=[2,4,1,0,3]
        permuted={c:{r:(permutation[I.score_bin(v)]+.5)/5 for r,v in rs.items()} for c,rs in values.items()}
        self.assertAlmostEqual(I.repeat_tvd_task(values),I.repeat_tvd_task(permuted))

    def test_deletion_information_orientation(self):
        self.assertAlmostEqual(I.deletion_tvd_task({0:[1,1],1:[0,0]})['value'],1)
        self.assertEqual(I.deletion_tvd_task({0:[0,0],1:[1,1]})['value'],0)
        with self.assertRaises(ValueError):I.deletion_tvd_task({0:[1,1],1:[0]})

    def test_delivered_hash_is_required(self):
        r={'category':'COMPLETE','score':.4}
        self.assertFalse(accepted(r,'expected')[0]);r['prompt_sha256_delivered']='different';self.assertFalse(accepted(r,'expected')[0])
        r['prompt_sha256_delivered']='expected';self.assertTrue(accepted(r,'expected')[0]);r['http_status']=429;self.assertFalse(accepted(r,'expected')[0])

    def test_explicit_alternative_transport(self):
        r={'category':'COMPLETE','score':.4,'instruction_sha256_served':'i'}
        self.assertFalse(accepted(r,'p')[0]);self.assertTrue(accepted(r,'p','i')[0])

    def test_duplicate_repeats_and_items_fail(self):
        with self.assertRaises(ValueError):unique_repeats([{'repeat':1},{'repeat':1}])
        with self.assertRaises(ValueError):S.Panel([{'item':'a','task':'a'}]*2,['qwen36|H2'],[[.1],[.2]],[.2,.3])

    def test_family_exclusion_needs_three(self):
        self.assertIsNone(S.target_excluding({'A':0,'B':1,'C':1},{'A'}))
        self.assertAlmostEqual(S.target_excluding({'A':0,'B':1,'C':1,'D':0},{'A'}),2/3)

    def test_unconditional_reselects(self):
        # Opposite property winners on two tasks; fixed and reselected weights
        # must produce different selected utilities after task resampling.
        rows=[{'item':f'{t}{i}','task':t} for t in ('a','b') for i in range(3)]
        scores=np.array([[0,1],[.5,.5],[1,0],[1,0],[.5,.5],[0,1]])
        records=[{'config':c,'component':'ident','task':t,'value':float((t=='a')==(j==0))} for j,c in enumerate(['opus55x|H2','qwen36|H2']) for t in ('a','b')]
        p=S.Panel(rows,['opus55x|H2','qwen36|H2'],scores,[0,.5,1]*2,records)
        a=p.evaluate(draws=100)['properties']['C_ident']
        self.assertGreater(a['unconditional_selection']['selected_spearman']['interval_95'][1],a['conditional_fixed_selection']['selected_spearman']['interval_95'][1])

    def test_group_fold_rebuilds_repeat_joint(self):
        from analyze_campaign import property_records
        items=[{'item':str(i),'task':'t','blank':False,'group':g} for i,g in enumerate(['keep','keep','hold'])]
        rows=[{'config':'opus55x|H2','kind':'crit','key':str(i),'item':str(i),'level':0,'repeat':rep,'score':value} for i,value in enumerate([.1,.1,.9]) for rep in [1,2,3]]
        pooled,_=property_records(rows,items);held,_=property_records(rows,items,exclude_group='hold')
        p=next(r['value'] for r in pooled if r['config']=='opus55x|H2' and r['component']=='repeat_tvd')
        h=next(r['value'] for r in held if r['config']=='opus55x|H2' and r['component']=='repeat_tvd')
        self.assertGreater(p,0);self.assertEqual(h,0)

    def test_supplement_does_not_change_historical_primary(self):
        import tempfile,json
        from pathlib import Path
        from analyze_campaign import property_records
        items=[{'item':'i','task':'t','blank':False,'group':'g'}]
        probes={'rows':[{'kind':'ms_gold','key':'t','task':'t','item':None,'level':i,'valid':True} for i in [1,2]]}
        rows=[{'config':'opus55x|H2','kind':'ident','key':'t','level':0,'repeat':r,'score':1.} for r in [1,2,3]]
        rows += [{'config':'opus55x|H2','kind':'ms_gold','key':'t','level':lv,'repeat':1,'score':v} for lv,v in [(1,.5),(2,1.)]]
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'probes.json';p.write_text(json.dumps(probes))
            before,_=property_records(rows,items,p)
            rows += [{'config':'opus55x|H2','kind':'ms_gold','key':'t','level':lv,'repeat':2,'score':0.} for lv in [1,2]]
            after,_=property_records(rows,items,p)
        get=lambda records:next(r['value'] for r in records if r['config']=='opus55x|H2' and r['component']=='ms_gold')
        self.assertEqual(get(before),get(after))

    def test_watchdog_detects_pid_reuse_and_preserves_healthy_driver(self):
        from watch_campaign import classify
        ident={'pid':123,'start_ticks':'4','boot_id':'a'};receipt={'driver':ident}
        self.assertEqual(classify(receipt,ident,False),'DRIVER_ALIVE')
        self.assertEqual(classify(receipt,{**ident,'start_ticks':'5'},False),'ADOPT_DEAD_DRIVER')
        self.assertEqual(classify(receipt,None,True),'RECONCILED')

    def test_repeat_variability_weights_units_and_retains_task_pairing(self):
        from analyze_campaign import repeat_variability
        items=[{'item':'a1','task':'a'},{'item':'a2','task':'a'},{'item':'b1','task':'b'}]
        rows=[{'config':'opus55x|H2','kind':'crit','key':item['item'],'item':item['item'],'task':item['task'],'level':0,'repeat':rep,'score':score}
              for item in items for rep,score in enumerate(([0.,1.] if item['task']=='a' else [0.,0.]),1)]
        result=repeat_variability(rows,items)['opus55x|H2']['crit'];stat=result['mean_within_unit_sample_sd_interval']
        self.assertAlmostEqual(stat['estimate'],2/3*(.5**.5));self.assertEqual(stat['finite_draws'],10000)
        self.assertAlmostEqual(stat['interval_95'][0],0.);self.assertAlmostEqual(stat['interval_95'][1],.5**.5)
        self.assertEqual(result['units_with_repeat_variability'],3)

    def test_repeat_only_analysis_matches_full_estimator_exactly(self):
        from analyze_campaign import clean
        cfgs=['opus55x|H2','qwen36|D0','t2_sonnet5|H2']
        items=[{'item':str(i),'task':str(i//3)} for i in range(9)]
        rng=np.random.default_rng(17);scores=rng.random((9,3));target=rng.random(9)
        records=[{'config':cfg,'component':'repeat_tvd','task':str(t),'value':float(rng.random())} for cfg in cfgs for t in range(3)]
        p=S.Panel(items,cfgs,scores,target,records)
        full=clean(p.evaluate(draws=40));focused=clean(p.evaluate(draws=40,property_names=('repeat_tvd',)))
        self.assertEqual(full['properties']['repeat_tvd'],focused['properties']['repeat_tvd'])
        self.assertEqual(full['controls'],focused['controls'])

if __name__=='__main__':unittest.main()
