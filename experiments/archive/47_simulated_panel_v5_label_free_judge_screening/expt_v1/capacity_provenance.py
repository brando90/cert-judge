"""Offline final-publication bindings for the additive scheduling condition."""
import json
import re
from e47_adapter import ROOT,RESULTS,RUN_ID,read,write,sha,phase_context
from reallocate_probe_capacity import GROUPS,check_identity

def verify_capacity():
    _,_,_,ctl=phase_context('probes')
    plan_path=RESULTS/'probes/capacity_condition.json';receipt_path=RESULTS/'probes/capacity_receipt.json'
    plan=read(plan_path);receipt=read(receipt_path);amendment=ROOT.parent/'AMENDMENT_05_released_run_capacity.md'
    if plan['run_id']!=RUN_ID or receipt['run_id']!=RUN_ID or receipt['condition_sha256']!=sha(plan_path.read_bytes()):raise ValueError('capacity condition identity differs')
    if plan['amendment_sha256']!=sha(amendment.read_bytes()) or plan['executor_sha256']!=sha((ROOT/'reallocate_probe_capacity.py').read_bytes()):raise ValueError('capacity frozen bytes changed')
    runs=ctl.load_state()['runs']
    if {e['config']:e['run_id'] for e in runs.values()}!=plan['original_run_ids']:raise ValueError('capacity original run universe differs')
    expected={cfg:(release,slots) for release,targets,slots in GROUPS for cfg in targets}
    if set(receipt['configurations'])!=set(expected):raise ValueError('capacity condition unfinished')
    verified={}
    for cfg,value in receipt['configurations'].items():
        entry=runs[cfg+'@main'];release,slots=expected[cfg]
        if entry['concurrency']!=20 or value['run_id']!=entry['run_id'] or value['new_tasks']!=0:raise ValueError('capacity historical admission changed')
        if value['state']=='SKIPPED_ALREADY_TERMINAL':
            if entry['phase']!='terminal':raise ValueError('skipped run is not terminal')
            verified[cfg]={'state':value['state'],'original_run_id':entry['run_id']};continue
        if value['release_run_ids']!={c:plan['original_run_ids'][c] for c in release}:raise ValueError('capacity release mask differs')
        if any(runs[c+'@main']['phase']!='terminal' for c in release):raise ValueError('capacity release state differs')
        directory=ctl.JUDGE/'capacity_updates'/cfg.replace('|','__')
        names=('intent.json','identity_command.json','update_result.json','status_command.json','complete.json')
        records={n:read(directory/n) for n in names}
        intent=records['intent.json'];command=['run','update',entry['run_id'],'--concurrency',str(slots)]
        if intent['run_id']!=RUN_ID or intent['original_run_id']!=entry['run_id'] or intent['argv']!=command or intent['recorded_before_call'] is not True:raise ValueError('capacity intent differs')
        update=records['update_result.json']
        if update['argv']!=command or update['returncode']!=0 or re.findall(r'Run concurrency updated to (\d+)\.',update['stdout'])!=[str(value['server_acknowledged_concurrency'])]:raise ValueError('capacity acknowledgement differs')
        identity=records['identity_command.json']
        rows=json.loads(identity['stdout'])['runs']
        if identity['returncode']!=0 or len(rows)!=1:raise ValueError('capacity original identity absent')
        check_identity(rows[0],entry)
        status=records['status_command.json'];payload=json.loads(status['stdout'])
        if status['argv']!=['run','status','--ids',entry['run_id'],'--format','json']:raise ValueError('capacity status command differs')
        if status['returncode']!=0 or payload.get('missing_run_ids')!=[] or payload.get('requested_count')!=1 or payload.get('returned_count')!=1:raise ValueError('capacity post-update status absent')
        row=payload['runs'][0]
        if row['run_id']!=entry['run_id'] or row['total_tasks']!=entry['expected_cells']:raise ValueError('capacity post-update universe differs')
        if value['requested_concurrency']!=slots or value['new_runs']!=0 or value['new_inference_retries']!=0:raise ValueError('capacity mutation scope differs')
        acknowledged=value['server_acknowledged_concurrency']
        if not ((value['state']=='ACKNOWLEDGED' and acknowledged==slots) or (value['state']=='TERMINAL_NOOP' and acknowledged==20 and str(row['status']).lower() in ctl.TERMINAL_RUN)):raise ValueError('capacity acknowledged value exceeds condition')
        if records['complete.json']!={k:v for k,v in value.items() if k!='release_run_ids'}:raise ValueError('capacity public receipt differs from original result')
        verified[cfg]={'state':value['state'],'original_run_id':entry['run_id'],'requested_concurrency':slots,'server_acknowledged_concurrency':value['server_acknowledged_concurrency'],'private_receipt_hashes':{n:sha((directory/n).read_bytes()) for n in names}}
    evidence={'run_id':RUN_ID,'state':'VERIFIED_OFFLINE','amendment_sha256':sha(amendment.read_bytes()),'condition_sha256':sha(plan_path.read_bytes()),'receipt_sha256':sha(receipt_path.read_bytes()),'verifier_sha256':sha((ROOT/'capacity_provenance.py').read_bytes()),'original_terminal_ledger_sha256':sha(ctl.STATE.read_bytes()),'configurations':verified,'independent_concurrency_read_available':False,'transport_commands':0}
    output=RESULTS/'probes/capacity_provenance.json';write(output,evidence)
    return evidence,[amendment,plan_path,receipt_path,output,ROOT/'capacity_provenance.py',ROOT/'reallocate_probe_capacity.py']
