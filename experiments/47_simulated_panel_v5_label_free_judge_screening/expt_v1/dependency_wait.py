"""Run-bound probe dependency guard; no executor or measured-call launch."""
import argparse
import json
from pathlib import Path
import subprocess
import time
from e47_adapter import ROOT,RUN_ID,read,write,sha,source_items
from run_offline import identity,update_job

HELPER=Path('/dfs/scratch0/brando9/cert-judge-e47-probes')
REL=Path('experiments/47_simulated_panel_v5_label_free_judge_screening/expt_v1/probes')
BRANCH='codex/cj-e47-v5-probes'
FILES=('source_manifest.json','probe_manifest.json','compile_summary.json')
NAME='external_probe_dependency'
COMPILER_PROJECT='/lfs/skampere1/0/brando9/vb90_grading/lean_project'
COMPILER_HASHES=('8f6680f8389e8adee06cb2bd44372c6d60dce0e8301630b61a99a5642d1bd71b','de7f8927e00e1cc9b4585e9ea382a8a55bd616692b7a1e90125f9f5f3cdb128f','df25409ddea390271687e3296ffae15d2efbae339b58f78f7aca023917ee354f')
COMPILER_ENVIRONMENT=':'.join((COMPILER_PROJECT,*COMPILER_HASHES))

def verify_terminal_sources(source,manifest,cache_rows,expected,environment):
    """Match terminal compilation evidence to exact declared candidate bytes."""
    def unique(rows,key):
        result={r[key]:r for r in rows}
        if len(result)!=len(rows):raise ValueError('duplicate '+key+' in terminal source evidence')
        return result
    frozen=unique(expected,'item');originals=unique(source['candidates'],'item')
    criteria=unique([r for r in manifest['rows'] if r['kind']=='crit'],'item')
    if len(frozen)!=750 or set(originals)!=set(frozen) or set(criteria)!=set(frozen):raise ValueError('terminal candidate universe differs from frozen inventory')
    tasks={r['task'] for r in expected};references=unique(source['references'],'task')
    if len(tasks)!=50 or set(references)!=tasks:raise ValueError('terminal reference universe differs')
    for task,reference in references.items():
        expected_hashes={r['ref_sha256'] for r in expected if r['task']==task}
        if expected_hashes!={reference['actual_sha256']}:raise ValueError('reference source hash differs')
    g01={r['item'] for r in expected if r['group']=='G01'}
    if len(g01)!=50 or {r['item'] for r in source['candidates'] if r['group']=='G01'}!=g01:raise ValueError('G01 source identities differ')
    nonblank=[r for r in expected if not r['blank']]
    if len(nonblank)!=691:raise ValueError('nonblank universe differs')
    cache={}
    for row in cache_rows:
        if row.get('environment')==environment:cache.setdefault(row['sha256'],[]).append(row)
    for item,f in frozen.items():
        original=originals[item];criterion=criteria[item]
        if original['cand_sha256']!=f['cand_sha256'] or original['blank']!=f['blank'] or criterion['task']!=f['task']:raise ValueError('candidate provenance differs '+item)
        if f['blank']:continue
        digest=f['cand_sha256']
        if original['source_status']!='verified' or original['actual_sha256']!=digest:raise ValueError('nonblank source not verified '+item)
        if criterion.get('source_sha256')!=digest or criterion.get('sha256')!=digest:raise ValueError('terminal criterion source hash differs '+item)
        terminal=criterion.get('candidate_compile') or {}
        fields=('ok','returncode','output_sha256','finished_utc')
        if not all(k in terminal for k in fields) or not isinstance(terminal['ok'],bool) or terminal['ok']!=(terminal['returncode']==0):raise ValueError('missing or inconsistent terminal candidate receipt '+item)
        if not any(all(terminal[k]==record.get(k) for k in fields) for record in cache.get(digest,[])):raise ValueError('terminal candidate receipt has no matching preserved compilation '+item)
    return {'candidate_ids':750,'verified_nonblank':691,'g01_ids_and_terminal_receipts':50,'references':50}

def observe():
    probes=HELPER/REL;state={'run_id':RUN_ID,'dependency_run_id':'cj-e47-probes-10-08-2026-a1','observed_epoch':time.time(),'state':'WAITING_STRUCTURAL_EVIDENCE'}
    active=read(probes/'runtime/active_jobs.json');pid=active.get('driver',{}).get('pid')
    if active.get('run_id')!=state['dependency_run_id']:raise ValueError('probe dependency run identity differs')
    process=identity(pid) if pid else None
    if process:
        if any(active['driver'].get(k)!=process[k] for k in ('pid','boot_id','start_ticks')):raise ValueError('probe process boot/start identity differs')
        if Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[0]=='Z':process=None
    if process:
        command=Path(f'/proc/{pid}/cmdline').read_bytes()
        if b'/probes/build_probes_v5.py' not in command or Path(f'/proc/{pid}/cwd').resolve()!=HELPER.resolve():raise ValueError('probe process ownership mismatch')
    state['external_compiler']=process
    if not all((probes/name).is_file() for name in FILES):
        if not process:state['state']='ACTIONABLE_DEPENDENCY_FAILURE'
        return state
    source=read(probes/FILES[0]);manifest=read(probes/FILES[1]);summary=read(probes/FILES[2]);hashes={name:sha((probes/name).read_bytes()) for name in FILES}
    state['hashes']=hashes
    if summary['source_manifest_sha256']!=hashes[FILES[0]] or summary['probe_manifest_sha256']!=hashes[FILES[1]]:raise ValueError('terminal probe hash mismatch')
    if source['declared']!={'rows':750,'nonblank':691,'blank':59,'unique_tasks':50}:raise ValueError('probe universe differs')
    if any(not isinstance(r.get('valid'),bool) for r in manifest['rows']):raise ValueError('structural rows incomplete')
    cache_path=HELPER/REL.parent/'private/probes_worker/compile_cache.jsonl'
    cache_rows=[json.loads(line) for line in cache_path.read_text().splitlines()]
    toolchain=summary['toolchain']
    if tuple(toolchain[k] for k in ('lean_toolchain_sha256','lake_manifest_sha256','lake_sha256'))!=COMPILER_HASHES:raise ValueError('terminal compiler environment differs from pinned live-worker receipts')
    state['terminal_source_correspondence']=verify_terminal_sources(source,manifest,cache_rows,source_items(),COMPILER_ENVIRONMENT)
    from verify_probe_artifacts import verify_transformed_artifacts
    state['transformed_artifact_correspondence']=verify_transformed_artifacts(source,manifest,cache_rows,COMPILER_ENVIRONMENT,probes.parent,probes/'build_probes_v5.py')
    state['compiler_environment_sha256']=sha(COMPILER_ENVIRONMENT.encode())
    state['compile_cache_sha256']=sha(cache_path.read_bytes())
    state['state']='WAITING_PROBE_PUBLICATION'
    if process:return state
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HELPER,text=True).strip()
    for name in FILES:
        blob=subprocess.run(['git','show',commit+':'+str(REL/name)],cwd=HELPER,capture_output=True)
        if blob.returncode or sha(blob.stdout)!=hashes[name]:return state
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/'+BRANCH],cwd=HELPER,text=True).split()
    if not remote or remote[0]!=commit:return state
    marker=probes/'runtime/COMPLETE.json'
    if not marker.exists():return state
    completion=read(marker)
    if completion.get('run_id')!=state['dependency_run_id'] or completion.get('role')!='probe_subtask_only':raise ValueError('probe completion marker identity differs')
    state.update(state='READY_FOR_INTEGRATION',verified_published_commit=commit);return state

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--describe',action='store_true');ap.add_argument('--enter',action='store_true');ap.add_argument('--clear',action='store_true');args=ap.parse_args();rt=ROOT/'runtime'
    if args.describe:
        write(rt/'dependency_wait_contract.json',{'schema_version':1,'run_id':RUN_ID,'receipt':'runtime/dependency_wait.json','waiting_state':'dependency_waiting','active_jobs_entry_name':NAME,
              'legacy_supervisor_guard':'Nonempty active_jobs.jobs makes already-loaded supervisor exit adoption_required without launching another executor; root must honor the wait receipt before stale FINISHED jobs.',
              'new_supervisor_guard':'Read run-bound dependency_wait.json before active_jobs; return dependency_waiting without consuming a launch.',
              'observe_command':'python3 expt_v1/dependency_wait.py','ready_states':['READY_FOR_INTEGRATION','ACTIONABLE_DEPENDENCY_FAILURE'],
              'resume_command':'python3 expt_v1/dependency_wait.py --clear; then root resumes the existing serial supervisor within attempts4–6',
              'readiness':'Exact750 candidate identities/691 verified nonblank source hashes/50 G01 terminal receipt matches in the pinned compiler environment;50 references;complete structural rows;matching terminal summary hashes;all three files equal published helper HEAD;matching scoped helper COMPLETE receipt.',
              'whole_experiment_complete':False});print('Dependency contract written; waiting is not active.');return
    observed=observe()
    if args.enter:
        jobs=read(rt/'active_jobs.json').get('jobs',[])
        if any(j.get('name')!=NAME for j in jobs):raise ValueError('active main jobs must be adopted; do not enter dependency-only wait')
        if observed['state'] not in ('WAITING_STRUCTURAL_EVIDENCE','WAITING_PROBE_PUBLICATION'):raise ValueError('dependency already actionable; continue useful work')
        for name in ('existing_analysis','controls_analysis','criterion_only_analysis'):
            if read(rt/(name+'.json'))['state']!='FINISHED':raise ValueError('independent analysis remains '+name)
        if not (rt/'judge_criterion_RECONCILED.json').exists():raise ValueError('criterion campaign remains')
        receipt={'schema_version':1,'run_id':RUN_ID,'state':'dependency_waiting','created_epoch':time.time(),'dependency':observed,'whole_experiment_complete':False}
        write(rt/'dependency_wait.json',receipt);update_job(NAME,{'run_id':RUN_ID,'kind':'external_dependency_wait','state':'dependency_waiting','driver':observed['external_compiler'],'never_terminate_external_owner':True,'receipt':'runtime/dependency_wait.json'})
    elif args.clear:
        if observed['state'] not in ('READY_FOR_INTEGRATION','ACTIONABLE_DEPENDENCY_FAILURE'):raise ValueError('unchanged healthy dependency must not consume an executor launch')
        receipt=read(rt/'dependency_wait.json');assert receipt['run_id']==RUN_ID
        receipt.update(state='actionable_dependency',resumed_epoch=time.time(),dependency=observed);write(rt/'dependency_wait.json',receipt);update_job(NAME,None)
    write(rt/'dependency_observation.json',observed);print(observed['state'])

if __name__=='__main__':main()
