"""Bind complete analysis outputs to immutable admissions and actual score bytes."""
from pathlib import Path
import json
from e47_adapter import ROOT,RESULTS,PRIVATE,RUN_ID,POOL,FAMILY,read,write,sha,verify_dependencies
from statistics_v5 import PROPERTIES,METRICS,task_folds,recommendation

PROTOCOL_COMMIT='d38359a673dbc762e18488f3b9d6e6bd45622ecd'
PROTOCOL_SHA256='513f394cfdf00f1fbc45b84026746af11e40cd003a639246ae354eacb29eb174'
TARGETS=('T_all','T_C0','T_common_excluding_Anthropic_Alibaba')
SCOPES=('pooled','original_G01_G13','late_G16_G17','all_declared_blank_zero')
GROUPS=tuple(f'G{i:02d}' for i in range(1,14))+('G16','G17')

class StaleCriterionProvenance(ValueError):
    """A valid same-run receipt predates the current bound input revision."""
    pass

def fingerprint(identity):return sha(json.dumps(identity,sort_keys=True).encode())

def current_job(job,digest):
    return job.get('run_id')==RUN_ID and job.get('input_sha256')==digest and job.get('draws')==10000 and job.get('seed')==47 and 'result' in job

def keyed_cells(rows):
    cells={r['cell']:r for r in rows}
    if len(cells)!=len(rows):raise ValueError('duplicate final score cell')
    return cells

def capture_inputs(mode,probe_manifest=None):
    if mode not in ('criterion','full'):raise ValueError('unknown analysis mode')
    if sha((ROOT.parent/'PROTOCOL.md').read_bytes())!=PROTOCOL_SHA256:raise ValueError('immutable protocol changed')
    dependencies=verify_dependencies();phases=('criterion',) if mode=='criterion' else ('criterion','probes')
    identity={'schema_version':1,'run_id':RUN_ID,'mode':mode,'protocol_commit':PROTOCOL_COMMIT,'protocol_sha256':PROTOCOL_SHA256,'admissions':{},'files':{},'frozen_dependencies':dependencies}
    def bind(path):identity['files'][str(path.relative_to(ROOT))]=sha(path.read_bytes())
    for path in (RESULTS/'targets_reconstructed.json',PRIVATE/'accepted_cached_primary_scores.json'):bind(path)
    codes=['e47_adapter.py','analyze_campaign.py','statistics_v5.py','analysis_provenance.py']
    if mode=='criterion':codes.append('analyze_criterion_only.py')
    for name in codes:bind(ROOT/name)
    phase_cells={cfg:{} for cfg in POOL}
    for phase in phases:
        path=RESULTS/phase/'admission_manifest.json';admission=read(path);digest=sha(path.read_bytes())
        marker=read(ROOT/'runtime'/f'judge_{phase}_RECONCILED.json')
        if admission.get('run_id')!=RUN_ID or admission.get('phase')!=phase or admission.get('state')!='FROZEN' or set(admission['configurations'])!=set(POOL):raise ValueError('analysis admission identity differs '+phase)
        if marker.get('run_id')!=RUN_ID or marker.get('phase')!=phase or marker.get('state')!='RECONCILED' or marker.get('admission_manifest_sha256')!=digest:raise ValueError('analysis phase is not reconciled '+phase)
        identity['admissions'][phase]=digest
        for name,expected in admission['contract_hashes'].items():
            if sha((ROOT.parent/name).read_bytes())!=expected:raise ValueError('frozen protocol amendment changed '+name)
        if phase=='probes':
            if probe_manifest is None:raise ValueError('full analysis requires the actual structural manifest')
            manifest=Path(probe_manifest).resolve()
            if not manifest.is_relative_to(ROOT.resolve()) or sha(manifest.read_bytes())!=admission.get('probe_manifest_sha256'):raise ValueError('structural manifest differs from reconciled probe admission')
            bind(manifest);identity['probe_manifest_sha256']=admission['probe_manifest_sha256']
        for cfg in POOL:
            name=cfg.replace('|','__')+'.json';frozen_path=RESULTS/phase/'cells'/name
            if sha(frozen_path.read_bytes())!=admission['cells_sha256'][cfg]:raise ValueError('frozen admission cell bytes changed')
            declared=keyed_cells(read(frozen_path)['cells']);path=PRIVATE/phase/'final_harvest'/name;blob=read(path)
            if blob.get('run_id')!=RUN_ID or blob.get('phase')!=phase or blob.get('config')!=cfg:raise ValueError('final phase score identity differs')
            final=keyed_cells(blob['cells'])
            if set(final)!=set(declared):raise ValueError('final score universe differs from complete frozen admission')
            for cell,row in final.items():
                if any(row.get(k)!=declared[cell].get(k) for k in ('kind','key','task','item','level','repeat','prompt_sha256')):raise ValueError('final score request identity differs '+cell)
            if set(phase_cells[cfg])&set(final):raise ValueError('criterion/probe phases overlap')
            phase_cells[cfg].update(final);bind(path)
    if mode=='full':
        for cfg in POOL:
            path=PRIVATE/'final_harvest'/(cfg.replace('|','__')+'.json');blob=read(path)
            if blob.get('run_id')!=RUN_ID or blob.get('config')!=cfg or keyed_cells(blob['cells'])!=phase_cells[cfg]:raise ValueError('analysis score union differs from reconciled phases')
            bind(path)
    return identity

def required_artifacts():
    names={'per_task_properties.json','repeat_variability.json','selection_association.json','recommendations.json'}
    for target in TARGETS:
        names.update(f'{kind}_{target}.json' for kind in ('criterion','sensitivity','transfers','planning'))
        names.update(f'criterion_{target}_{scope}.json' for scope in ('original_G01_G13','late_G16_G17'))
        names.add('criterion_all_declared_blank_zero'+('' if target=='T_all' else '_'+target)+'.json')
    names.update(f'criterion_excluding_{family}.json' for family in ('Anthropic','Alibaba'))
    return names

def require_keys(value,keys,label):
    if not isinstance(value,dict) or set(value)!=set(keys):raise ValueError('missing or extra required keys: '+label)

def is_unavailable(value):
    return isinstance(value,dict) and value.get('status') in ('NOT_COMPUTABLE','INCONCLUSIVE')

def validate_evaluation(value,label):
    if is_unavailable(value):return
    if not isinstance(value,dict):raise ValueError('invalid analysis view '+label)
    require_keys(value.get('properties'),PROPERTIES,label+' properties')
    for prop,row in value['properties'].items():
        if is_unavailable(row):continue
        for kind in ('unconditional_selection','conditional_fixed_selection'):
            require_keys(row.get(kind),('selected_spearman','regret','gain_vs_H2','gain_vs_random'),label+' '+prop+' '+kind)
        if 'association' in row:require_keys(row['association'],('spearman','pearson','kendall'),label+' association')

def validate_criterion(value,configs,label):
    require_keys(value,configs,label)
    for row in value.values():
        require_keys(row.get('metrics'),METRICS,label+' metrics')
        if row.get('status') not in ('COMPUTED','NOT_COMPUTABLE'):raise ValueError('invalid criterion status')

def validate_full_shapes(artifacts,items):
    require_keys(artifacts,required_artifacts(),'full analysis files')
    tasks={r['task'] for r in items};groups={r['group'] for r in items}
    if len(items)!=750 or len(tasks)!=50 or groups!=set(GROUPS):raise ValueError('analysis target universe differs')
    require_keys(artifacts['selection_association.json'],TARGETS,'pooled target views')
    require_keys(artifacts['recommendations.json'],PROPERTIES,'recommendations')
    allowed={'DROP_UNCOMPUTABLE','DROP_CONSTANT','DROP_NONPOSITIVE_GAIN','STRONG_FOLLOWUP','INCONCLUSIVE_POSITIVE_POINT_ESTIMATE','INCONCLUSIVE'}
    if any(v not in allowed for v in artifacts['recommendations.json'].values()):raise ValueError('unknown screening decision')
    for target in TARGETS:
        validate_evaluation(artifacts['selection_association.json'][target],target+' pooled')
        for scope in ('', '_original_G01_G13','_late_G16_G17'):
            validate_criterion(artifacts[f'criterion_{target}{scope}.json'],POOL,'criterion '+target+scope)
        blank='criterion_all_declared_blank_zero'+('' if target=='T_all' else '_'+target)+'.json'
        validate_criterion(artifacts[blank],POOL,blank)
        sensitivities=artifacts[f'sensitivity_{target}.json']
        expected={f'exclude_base_{b}' for b in ('Opus','Qwen','Sonnet')}|{f'exclude_provider_{f}' for f in ('Anthropic','Alibaba')}|{'original_G01_G13','late_G16_G17','same_eligible_pool'}
        require_keys(sensitivities,expected,'base/provider/scope sensitivities')
        for view,value in sensitivities.items():validate_evaluation(value,view)
        transfers=artifacts[f'transfers_{target}.json']
        if transfers.get('assignment')!=task_folds(tasks):raise ValueError('task-fold assignment differs from protocol')
        expected={f'agent_group_{g}' for g in GROUPS}|{'equal_group_mean'}|{f'task_fold_{i}' for i in range(5)}
        require_keys(transfers.get('results'),expected,'group/task transfers')
        for view,value in transfers['results'].items():validate_evaluation(value,view)
        planning=artifacts[f'planning_{target}.json'];require_keys(planning,PROPERTIES,'power properties')
        grid={(pool,tasks) for pool in (4,6,8,12) for tasks in (25,50,100,200,400)}
        for prop,rows in planning.items():
            if is_unavailable(rows):
                if rows.get('draws')!=10000 or not rows.get('reason'):raise ValueError('unavailable power entry lacks an explicit result')
                continue
            if not isinstance(rows,list) or len(rows)!=len(grid) or {(r['pool_size'],r['tasks']) for r in rows}!=grid:raise ValueError('incomplete or duplicate power grid '+prop)
            for row in rows:
                if row.get('draws')!=10000 or row.get('status') not in ('COMPUTED','NOT_COMPUTABLE') or row.get('new_family_requirement')!='NOT_IDENTIFIABLE':raise ValueError('power-grid protocol differs')
    for family in ('Anthropic','Alibaba'):
        expected=[c for c in POOL if FAMILY[c.split('|')[0]]==family]
        validate_criterion(artifacts[f'criterion_excluding_{family}.json'],expected,'own-family-excluded criterion')

def expected_job_results(artifacts):
    """Each aggregate entry must equal its individually bound derivation result."""
    result={}
    for target in TARGETS:
        result['selection_'+target]=artifacts['selection_association.json'][target]
        for scope in ('','_original_G01_G13','_late_G16_G17'):
            name='criterion_'+target+scope;result[name]=artifacts[name+'.json']
        for name,value in artifacts['sensitivity_'+target+'.json'].items():
            result[target+'_'+name]=value
        for name,value in artifacts['transfers_'+target+'.json']['results'].items():
            result[target+'_'+name.replace('agent_group_','group_')]=value
        for prop,value in artifacts['planning_'+target+'.json'].items():result[target+'_planning_'+prop]=value
        name='criterion_all_declared_blank_zero'+('' if target=='T_all' else '_'+target)
        result[name]=artifacts[name+'.json']
    for family in ('Anthropic','Alibaba'):
        name='criterion_excluding_'+family;result[name]=artifacts[name+'.json']
    return result

def check_full_derivation(artifacts,digest,names):
    expected=expected_job_results(artifacts);require_keys(dict.fromkeys(names),expected,'derivation job inventory')
    hashes={}
    for name,value in expected.items():
        path=RESULTS/'analysis_jobs'/f'{name}.json';job=read(path)
        if not current_job(job,digest) or job['result']!=value:raise ValueError('stale or mismatched analysis derivation '+name)
        hashes[name]=sha(path.read_bytes())
    selections=artifacts['selection_association.json']
    actual={p:recommendation(selections['T_all'],selections['T_common_excluding_Anthropic_Alibaba'],p) for p in PROPERTIES}
    if artifacts['recommendations.json']!=actual:raise ValueError('recommendations differ from bound selection results')
    return hashes

def publish_full_receipt(identity,probe_manifest,jobs):
    if capture_inputs('full',probe_manifest)!=identity:raise ValueError('analysis inputs changed during computation')
    artifacts={name:read(RESULTS/name) for name in required_artifacts()};items=read(RESULTS/'targets_reconstructed.json')
    validate_full_shapes(artifacts,items);digest=fingerprint(identity)
    if len(jobs)!=len(set(jobs)):raise ValueError('duplicate derivation job')
    job_hashes=check_full_derivation(artifacts,digest,jobs)
    receipt={'run_id':RUN_ID,'state':'FULL_ANALYSIS_VERIFIED','protocol_commit':PROTOCOL_COMMIT,'protocol_sha256':PROTOCOL_SHA256,'inputs':identity,'input_sha256':digest,
             'artifacts':{name:sha((RESULTS/name).read_bytes()) for name in required_artifacts()},'analysis_jobs':job_hashes,'whole_experiment_complete':False}
    write(RESULTS/'full_analysis_provenance.json',receipt);return receipt

def verify_full_receipt(probe_manifest):
    receipt=read(RESULTS/'full_analysis_provenance.json');identity=capture_inputs('full',probe_manifest)
    if receipt.get('run_id')!=RUN_ID or receipt.get('state')!='FULL_ANALYSIS_VERIFIED' or receipt.get('inputs')!=identity or receipt.get('input_sha256')!=fingerprint(identity):raise ValueError('stale full analysis: current measurements/admissions/code differ')
    require_keys(receipt.get('artifacts'),required_artifacts(),'analysis receipt artifact inventory')
    for name,digest in receipt['artifacts'].items():
        if sha((RESULTS/name).read_bytes())!=digest:raise ValueError('analysis artifact changed after derivation '+name)
    artifacts={name:read(RESULTS/name) for name in required_artifacts()}
    validate_full_shapes(artifacts,read(RESULTS/'targets_reconstructed.json'))
    hashes=check_full_derivation(artifacts,receipt['input_sha256'],receipt.get('analysis_jobs',{}))
    if hashes!=receipt['analysis_jobs']:raise ValueError('analysis derivation receipt changed')
    return receipt

def criterion_specs():
    return {(cfg+'|'+target+'|'+scope):(cfg,target,scope) for cfg in POOL for target in (*TARGETS,'own_family_excluded') for scope in SCOPES}

def repeat_job_names():
    views={'pooled','equal_group_mean','planning'}|{'exclude_base_'+b for b in ('Opus','Qwen','Sonnet')}|{'exclude_provider_'+f for f in ('Anthropic','Alibaba')}|{'group_'+g for g in GROUPS}|{'task_fold_'+str(f) for f in range(5)}
    return {t+'_'+v for t in TARGETS for v in views}

def criterion_artifact_hashes(digest):
    index=read(RESULTS/'criterion_descriptive_index.json');specs=criterion_specs()
    if index.get('run_id')!=RUN_ID or index.get('expected')!=192 or index.get('completed')!=192:raise ValueError('criterion index incomplete or wrong run')
    require_keys(index.get('results'),specs,'criterion target/scope views');hashes={}
    def bind(path):hashes[str(path.relative_to(ROOT))]=sha(path.read_bytes())
    for label,(cfg,target,scope) in specs.items():
        expected=RESULTS/'criterion_descriptive'/f'{sha(label.encode())[:24]}.json'
        if (ROOT/index['results'][label]).resolve()!=expected.resolve():raise ValueError('criterion view path differs')
        job=read(expected);actual_target='T_excluding_'+FAMILY[cfg.split('|')[0]] if target=='own_family_excluded' else target
        if not current_job(job,digest) or (job.get('config'),job.get('target'),job.get('scope'))!=(cfg,actual_target,scope):raise ValueError('stale or mismatched criterion derivation '+label)
        validate_criterion({cfg:job['result']},[cfg],label);bind(expected)
    for name in repeat_job_names():
        path=RESULTS/'repeat_only_analysis'/f'{name}.json';job=read(path)
        if not current_job(job,digest):raise ValueError('stale or missing repeat-only derivation '+name)
        if not name.endswith('_planning'):require_keys(job['result'].get('properties'),('repeat_tvd',),'repeat-only property')
        bind(path)
    for name in ('criterion_descriptive_index.json','repeat_only_task_properties.json','repeat_variability_criterion.json','criterion_only_analysis_complete.json'):bind(RESULTS/name)
    return hashes

def publish_criterion_receipt(identity):
    if capture_inputs('criterion')!=identity:raise ValueError('criterion inputs changed during computation')
    digest=fingerprint(identity);artifacts=criterion_artifact_hashes(digest)
    write(RESULTS/'criterion_analysis_provenance.json',{'run_id':RUN_ID,'state':'CRITERION_ANALYSIS_VERIFIED','inputs':identity,'input_sha256':digest,'artifacts':artifacts,'whole_experiment_complete':False})

def verify_criterion_receipt():
    receipt=read(RESULTS/'criterion_analysis_provenance.json');identity=capture_inputs('criterion');digest=fingerprint(identity)
    if receipt.get('run_id')!=RUN_ID or receipt.get('state')!='CRITERION_ANALYSIS_VERIFIED':raise ValueError('criterion provenance identity/state differs')
    if receipt.get('inputs')!=identity or receipt.get('input_sha256')!=digest:raise StaleCriterionProvenance('stale criterion analysis: current measurements/admissions/code differ')
    if criterion_artifact_hashes(digest)!=receipt.get('artifacts'):raise ValueError('criterion artifact changed after derivation')
    return receipt
