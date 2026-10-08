"""Reject incomplete/stale same-run reports using synthetic receipts only."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import analysis_provenance as P
from e47_adapter import write,read,sha


def synthetic():
    interval={'estimate':None,'interval_95':None,'draws':10000,'finite_draws':0}
    selection={'properties':{p:{'eligible_configurations':0,'unconditional_selection':{k:interval for k in ('selected_spearman','regret','gain_vs_H2','gain_vs_random')},'conditional_fixed_selection':{k:interval for k in ('selected_spearman','regret','gain_vs_H2','gain_vs_random')}} for p in P.PROPERTIES}}
    criterion={c:{'status':'NOT_COMPUTABLE','metrics':{m:interval for m in P.METRICS}} for c in P.POOL}
    items=[{'item':g+'_'+str(t),'group':g,'task':str(t)} for g in P.GROUPS for t in range(50)]
    artifacts={'per_task_properties.json':{'records':[]},'repeat_variability.json':{},'selection_association.json':{t:selection for t in P.TARGETS},'recommendations.json':{p:'DROP_UNCOMPUTABLE' for p in P.PROPERTIES}}
    for target in P.TARGETS:
        for scope in ('','_original_G01_G13','_late_G16_G17'):artifacts['criterion_'+target+scope+'.json']=criterion
        blank='criterion_all_declared_blank_zero'+('' if target=='T_all' else '_'+target)+'.json';artifacts[blank]=criterion
        artifacts['sensitivity_'+target+'.json']={k:selection for k in ['exclude_base_Opus','exclude_base_Qwen','exclude_base_Sonnet','exclude_provider_Anthropic','exclude_provider_Alibaba','original_G01_G13','late_G16_G17','same_eligible_pool']}
        artifacts['transfers_'+target+'.json']={'assignment':P.task_folds(str(t) for t in range(50)),'results':{k:selection for k in [*('agent_group_'+g for g in P.GROUPS),'equal_group_mean',*('task_fold_'+str(f) for f in range(5))]}}
        artifacts['planning_'+target+'.json']={p:{'status':'NOT_COMPUTABLE','reason':'no eligible synthetic measurement','draws':10000} for p in P.PROPERTIES}
    for family in ('Anthropic','Alibaba'):artifacts['criterion_excluding_'+family+'.json']={c:criterion[c] for c in P.POOL if P.FAMILY[c.split('|')[0]]==family}
    return copy.deepcopy(artifacts),items


class ProvenanceTests(unittest.TestCase):
    def test_explicit_missingness_allowed_but_missing_required_scopes_rejected(self):
        good,items=synthetic();P.validate_full_shapes(good,items)
        cases=[('selection_association.json','T_C0'),('criterion_T_all.json',P.POOL[0]),('sensitivity_T_all.json','exclude_base_Qwen'),('sensitivity_T_all.json','exclude_provider_Alibaba'),('transfers_T_all.json','agent_group_G17'),('transfers_T_all.json','task_fold_4'),('planning_T_all.json','semantic_auc')]
        for filename,key in cases:
            with self.subTest(filename=filename,key=key):
                bad=copy.deepcopy(good);mapping=bad[filename]['results'] if filename.startswith('transfers_') else bad[filename];del mapping[key]
                with self.assertRaises(ValueError):P.validate_full_shapes(bad,items)
        bad=copy.deepcopy(good);bad['transfers_T_all.json']['results']={}
        with self.assertRaises(ValueError):P.validate_full_shapes(bad,items)

    def test_power_grid_duplicate_cannot_replace_missing_condition(self):
        artifacts,items=synthetic();grid=[{'pool_size':p,'tasks':t,'draws':10000,'status':'NOT_COMPUTABLE','new_family_requirement':'NOT_IDENTIFIABLE'} for p in (4,6,8,12) for t in (25,50,100,200,400)]
        artifacts['planning_T_all.json']['repeat_tvd']=grid;P.validate_full_shapes(artifacts,items)
        grid[-1]=dict(grid[0])
        with self.assertRaisesRegex(ValueError,'power grid'):P.validate_full_shapes(artifacts,items)

    def test_all_current_derivation_jobs_required_and_bound_to_aggregate_values(self):
        artifacts,_=synthetic();expected=P.expected_job_results(artifacts)
        self.assertEqual(len(expected),128)
        with tempfile.TemporaryDirectory() as directory,patch.object(P,'RESULTS',Path(directory)):
            for name,value in expected.items():write(P.RESULTS/'analysis_jobs'/f'{name}.json',{'run_id':P.RUN_ID,'input_sha256':'fresh','seed':47,'draws':10000,'result':value})
            P.check_full_derivation(artifacts,'fresh',expected)
            with self.assertRaisesRegex(ValueError,'inventory'):P.check_full_derivation(artifacts,'fresh',list(expected)[1:])
            name='T_all_task_fold_4';path=P.RESULTS/'analysis_jobs'/f'{name}.json';job=read(path);job['input_sha256']='old-same-run';write(path,job)
            with self.assertRaisesRegex(ValueError,'stale'):P.check_full_derivation(artifacts,'fresh',expected)
            job['input_sha256']='fresh';job['result']={'status':'NOT_COMPUTABLE'};write(path,job)
            with self.assertRaisesRegex(ValueError,'mismatched'):P.check_full_derivation(artifacts,'fresh',expected)

    def test_stale_actual_scores_and_substituted_probe_manifest_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'expt_v1';root.mkdir();results=root/'results';private=root/'private'
            protocol=root.parent/'PROTOCOL.md';protocol.write_text('synthetic protocol')
            patches=[patch.object(P,'ROOT',root),patch.object(P,'RESULTS',results),patch.object(P,'PRIVATE',private),patch.object(P,'PROTOCOL_SHA256',sha(protocol.read_bytes())),patch.object(P,'verify_dependencies',return_value={})]
            for p in patches:p.start()
            self.addCleanup(lambda:[p.stop() for p in reversed(patches)])
            for name in ('e47_adapter.py','analyze_campaign.py','statistics_v5.py','analysis_provenance.py'): (root/name).write_text('synthetic code')
            write(results/'targets_reconstructed.json',[]);write(private/'accepted_cached_primary_scores.json',{})
            manifest=root/'probe_manifest.json';write(manifest,{'rows':[]});other=root/'other_probe_manifest.json';write(other,{'rows':[{'wrong':True}]})
            for phase in ('criterion','probes'):
                admission={'run_id':P.RUN_ID,'phase':phase,'state':'FROZEN','configurations':P.POOL,'cells_sha256':{},'contract_hashes':{},'probe_manifest_sha256':sha(manifest.read_bytes())}
                for cfg in P.POOL:
                    name=cfg.replace('|','__')+'.json';row={'cell':cfg+phase,'kind':'crit' if phase=='criterion' else 'ident','key':'item','task':'task','item':'item','level':0,'repeat':1,'prompt_sha256':'exact','score':.5,'accepted':True}
                    path=results/phase/'cells'/name;write(path,{'cells':[row]});admission['cells_sha256'][cfg]=sha(path.read_bytes())
                    write(private/phase/'final_harvest'/name,{'run_id':P.RUN_ID,'phase':phase,'config':cfg,'cells':[row]})
                path=results/phase/'admission_manifest.json';write(path,admission);write(root/'runtime'/f'judge_{phase}_RECONCILED.json',{'run_id':P.RUN_ID,'phase':phase,'state':'RECONCILED','admission_manifest_sha256':sha(path.read_bytes())})
            for cfg in P.POOL:
                name=cfg.replace('|','__')+'.json';rows=[r for phase in ('criterion','probes') for r in read(private/phase/'final_harvest'/name)['cells']];write(private/'final_harvest'/name,{'run_id':P.RUN_ID,'config':cfg,'cells':rows})
            identity=P.capture_inputs('full',manifest)
            with self.assertRaisesRegex(ValueError,'structural manifest differs'):P.capture_inputs('full',other)
            write(results/'full_analysis_provenance.json',{'run_id':P.RUN_ID,'state':'FULL_ANALYSIS_VERIFIED','inputs':identity,'input_sha256':P.fingerprint(identity)})
            name=P.POOL[0].replace('|','__')+'.json'
            for path in (private/'criterion/final_harvest'/name,private/'final_harvest'/name):
                payload=read(path);payload['cells'][0]['score']=.8;write(path,payload)
            with self.assertRaisesRegex(ValueError,'stale full analysis'):P.verify_full_receipt(manifest)

    def test_criterion_scope_and_repeat_derivation_inventory_are_complete(self):
        self.assertEqual(len(P.criterion_specs()),192);self.assertEqual(len(P.repeat_job_names()),84)
        self.assertIn('T_all_exclude_base_Qwen',P.repeat_job_names())
        self.assertIn('T_C0_task_fold_4',P.repeat_job_names())

    def test_criterion_report_rejects_missing_or_stale_same_run_view(self):
        artifacts,_=synthetic();criterion=artifacts['criterion_T_all.json']
        with tempfile.TemporaryDirectory() as directory,patch.object(P,'ROOT',Path(directory)),patch.object(P,'RESULTS',Path(directory)/'results'):
            index={'run_id':P.RUN_ID,'expected':192,'completed':192,'results':{}}
            for label,(cfg,target,scope) in P.criterion_specs().items():
                path=P.RESULTS/'criterion_descriptive'/f'{sha(label.encode())[:24]}.json';index['results'][label]=str(path.relative_to(P.ROOT))
                target='T_excluding_'+P.FAMILY[cfg.split('|')[0]] if target=='own_family_excluded' else target
                write(path,{'run_id':P.RUN_ID,'input_sha256':'current','seed':47,'draws':10000,'config':cfg,'target':target,'scope':scope,'result':criterion[cfg]})
            write(P.RESULTS/'criterion_descriptive_index.json',index)
            for name in P.repeat_job_names():write(P.RESULTS/'repeat_only_analysis'/f'{name}.json',{'run_id':P.RUN_ID,'input_sha256':'current','seed':47,'draws':10000,'result':{'properties':{'repeat_tvd':{}}}})
            for name in ('repeat_only_task_properties.json','repeat_variability_criterion.json','criterion_only_analysis_complete.json'):write(P.RESULTS/name,{})
            self.assertEqual(len(P.criterion_artifact_hashes('current')),280)
            label=next(iter(index['results']));path=P.ROOT/index['results'][label];job=read(path);job['input_sha256']='old-same-run';write(path,job)
            with self.assertRaisesRegex(ValueError,'stale'):P.criterion_artifact_hashes('current')
            del index['results'][label];write(P.RESULTS/'criterion_descriptive_index.json',index)
            with self.assertRaisesRegex(ValueError,'required keys'):P.criterion_artifact_hashes('current')

if __name__=='__main__':unittest.main()
