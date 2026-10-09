"""Bounded Amendment 05 scheduling of existing runs; never admission or retry."""
import fcntl
import json
import os
import re
import time
from e47_adapter import ROOT,RESULTS,RUN_ID,POOL,read,write,sha,phase_context,verify_dependencies
from campaign_driver import require_existing_runs

GROUPS=(
    (('opus55x|D0','t2_sonnet5|D0','t2_sonnet5|H2'),('opus55x|H0','opus55x|H2'),50),
    (('qwen36|D0','qwen36|H0','qwen36|H1','qwen36|H2','qwen36|R4'),('t2_qwen|D0','t2_qwen|H2'),70),
)

def eligible(runs,release,target):
    return all(runs[c+'@main']['phase']=='terminal' for c in release) and runs[target+'@main']['phase']!='terminal'

def check_identity(row,entry):
    for field,expected in [('run_id',entry['run_id']),('benchmark_name',entry['benchmark']),('agent_name',entry['agent']),('model',entry['selector']),('label',entry['actual_label']),('total_tasks',entry['expected_cells'])]:
        if row.get(field)!=expected:raise ValueError('scheduling identity mismatch: '+field)

def update_once(ctl,entry,slots,directory,health_check):
    directory.mkdir(parents=True,exist_ok=True);intent=directory/'intent.json'
    if intent.exists():raise ValueError('prior scheduling intent requires explicit reconciliation; never replay')
    query=['run','list','--benchmark-name',entry['benchmark'],'--agent-name',entry['agent'],'--model',entry['selector'],'--label',entry['actual_label'],'--format','json','--all']
    before=ctl.cli(query,timeout=600)
    write(directory/'identity_command.json',{'argv':query,'returncode':before.returncode,'stdout':before.stdout,'stderr':before.stderr})
    if before.returncode:raise ValueError('scheduling identity query failed')
    rows=json.loads(before.stdout)['runs']
    if len(rows)!=1:raise ValueError('scheduling identity is not unique')
    check_identity(rows[0],entry)
    if rows[0]['status'].lower() in ctl.TERMINAL_RUN:return {'state':'SKIPPED_ALREADY_TERMINAL','run_id':entry['run_id'],'new_tasks':0}
    health_check()
    argv=['run','update',entry['run_id'],'--concurrency',str(slots)]
    write(intent,{'run_id':RUN_ID,'original_run_id':entry['run_id'],'argv':argv,'epoch':time.time(),'recorded_before_call':True,'automatic_retry_permitted':False})
    with intent.open('rb') as durable:os.fsync(durable.fileno())
    parent_fd=os.open(directory,os.O_DIRECTORY)
    try:os.fsync(parent_fd)
    finally:os.close(parent_fd)
    result=ctl.cli(argv,timeout=600)
    write(directory/'update_result.json',{'argv':argv,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    if result.returncode:raise ValueError('scheduling update failed; preserve intent')
    values=re.findall(r'Run concurrency updated to (\d+)\.',result.stdout)
    if len(values)!=1:raise ValueError('scheduling acknowledgement missing')
    acknowledged=int(values[0])
    status_argv=['run','status','--ids',entry['run_id'],'--format','json']
    after=ctl.cli(status_argv,timeout=600)
    write(directory/'status_command.json',{'argv':status_argv,'returncode':after.returncode,'stdout':after.stdout,'stderr':after.stderr})
    if after.returncode:raise ValueError('post-update status unavailable')
    payload=json.loads(after.stdout)
    if payload.get('missing_run_ids')!=[] or payload.get('requested_count')!=1 or payload.get('returned_count')!=1:raise ValueError('post-update mask differs')
    row=payload['runs'][0]
    if row['run_id']!=entry['run_id'] or row['total_tasks']!=entry['expected_cells']:raise ValueError('post-update task universe differs')
    terminal=str(row['status']).lower() in ctl.TERMINAL_RUN
    if acknowledged!=slots and not (terminal and acknowledged==20):raise ValueError('concurrency acknowledgement differs')
    receipt={'state':'ACKNOWLEDGED' if acknowledged==slots else 'TERMINAL_NOOP','run_id':entry['run_id'],'requested_concurrency':slots,'server_acknowledged_concurrency':acknowledged,'independent_concurrency_read_available':False,'task_count':row['total_tasks'],'server_status':row['status'],'new_tasks':0,'new_runs':0,'new_inference_retries':0}
    write(directory/'complete.json',receipt);return receipt

def main():
    verify_dependencies();_,_,_,ctl=phase_context('probes');original=require_existing_runs(ctl)
    rt=ROOT/'runtime';lock=(rt/'probe_capacity.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    plan_path=RESULTS/'probes/capacity_condition.json';plan=read(plan_path)
    if plan['run_id']!=RUN_ID or plan['original_run_ids']!=original or plan['amendment_sha256']!=sha((ROOT.parent/'AMENDMENT_05_released_run_capacity.md').read_bytes()):raise ValueError('scheduling plan binding differs')
    if plan['groups']!=[{'release':list(release),'targets':list(targets),'target_concurrency':slots} for release,targets,slots in GROUPS]:raise ValueError('scheduling groups changed')
    if plan['executor_sha256']!=sha((ROOT/'reallocate_probe_capacity.py').read_bytes()):raise ValueError('scheduling implementation changed')
    if any(e['concurrency']!=20 for e in ctl.load_state()['runs'].values()):raise ValueError('original concurrency evidence differs')
    path=RESULTS/'probes/capacity_receipt.json';receipts=read(path) if path.exists() else {'run_id':RUN_ID,'condition_sha256':sha(plan_path.read_bytes()),'configurations':{}}
    if receipts['run_id']!=RUN_ID or receipts['condition_sha256']!=sha(plan_path.read_bytes()):raise ValueError('existing scheduling receipt binding differs')
    while len(receipts['configurations'])<4:
        if require_existing_runs(ctl)!=original:raise ValueError('original run mask changed')
        runs=ctl.load_state()['runs']
        for release,targets,slots in GROUPS:
            for cfg in targets:
                if cfg in receipts['configurations']:continue
                entry=runs[cfg+'@main']
                if entry['phase']=='terminal':
                    receipts['configurations'][cfg]={'state':'SKIPPED_ALREADY_TERMINAL','run_id':entry['run_id'],'new_tasks':0};write(path,receipts);continue
                if not eligible(runs,release,cfg):continue
                from callback_gate import require_callback_ready
                receipt=update_once(ctl,entry,slots,ctl.JUDGE/'capacity_updates'/cfg.replace('|','__'),lambda:require_callback_ready(ROOT,plan['admission_manifest_sha256']))
                receipt['release_run_ids']={c:original[c] for c in release}
                receipts['configurations'][cfg]=receipt;write(path,receipts)
        if len(receipts['configurations'])<4:time.sleep(30)

if __name__=='__main__':main()
