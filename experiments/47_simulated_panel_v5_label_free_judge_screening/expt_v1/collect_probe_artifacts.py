"""Collect each terminal probe run once through authenticated Valkyrie output.

Collection is read-only. This file does not infer task outcomes or submit calls.
The offline reconciler separately verifies every frozen request and used byte.
"""
import json
import time
from e47_adapter import RUN_ID, read, write, sha
from harvest_original_artifacts import require, verified_files


def collect(ctl, key):
    entry=ctl.load_state()['runs'][key];run_id=entry['run_id']
    require(entry['phase']=='terminal' and entry['run_status'] in ctl.TERMINAL_RUN,'NONTERMINAL_RUN')
    name=key.replace('|','__').replace('@','_');directory=ctl.RAW/(name+'_artifacts')
    certificate=ctl.RAW/(name+'_probe_collection.json');ctl.RAW.mkdir(parents=True,exist_ok=True)
    frozen_entry=sha(json.dumps(entry,sort_keys=True).encode())
    if certificate.exists():
        evidence=read(certificate)
        require(evidence['scientific_run_id']==RUN_ID and evidence['run_id']==run_id and evidence['ledger_entry_sha256']==frozen_entry,'COLLECTION_RUN_BINDING')
        for filename,field in [('files_sha256.json','inventory_sha256'),('collection_command.json','command_sha256'),('identity_receipt.json','identity_sha256')]:
            require(sha((directory/filename).read_bytes())==evidence[field],'COLLECTION_CERTIFICATE:'+filename)
        return directory,verified_files(directory),evidence
    command=directory/'collection_command.json'
    # Adopt an earlier successful owned harvest_transport download even when its
    # server final view was absent. Never download that original run a second time.
    if directory.exists():
        require(command.exists(),'PARTIAL_COLLECTION_REQUIRES_EXPLICIT_RECOVERY')
        prior=read(command)
        require(prior.get('run_id')==run_id and prior.get('returncode')==0,'UNSUCCESSFUL_COLLECTION')
        origin='adopted successful owned harvest_transport collection command'
    else:
        staging=ctl.RAW/(name+'_download_'+str(time.time_ns()));staging.mkdir()
        argv=['run','output',run_id,'-o',str(staging)]
        done=ctl.cli(argv,timeout=5400)
        write(staging/'collection_command.json',{'scientific_run_id':RUN_ID,'run_id':run_id,'command':argv,'returncode':done.returncode,'stdout':done.stdout,'stderr':done.stderr})
        if done.returncode:raise RuntimeError('read-only collection failed; preserve '+str(staging))
        staging.rename(directory);origin='authenticated valk run output'
    require(not (directory/'files_sha256.json').exists() and not (directory/'identity_receipt.json').exists(),'INCOMPLETE_CERTIFICATE_REQUIRES_EXPLICIT_RECOVERY')
    snapshot_path=directory/'terminal_snapshot.json'
    if not snapshot_path.exists():
        command_argv=['run','status','--ids',run_id,'--format','json']
        status=ctl.cli(command_argv,timeout=600)
        write(directory/'terminal_snapshot_command.json',{'command':command_argv,'returncode':status.returncode,'stdout':status.stdout,'stderr':status.stderr})
        require(status.returncode==0,'TERMINAL_METADATA_READ_FAILED')
        write(snapshot_path,json.loads(status.stdout))
    snapshot=read(snapshot_path)
    require(snapshot.get('missing_run_ids')==[] and snapshot.get('requested_count')==snapshot.get('returned_count')==1 and len(snapshot.get('runs',[]))==1,'TERMINAL_SNAPSHOT_MASK')
    row=snapshot['runs'][0]
    require(row.get('run_id')==run_id and str(row.get('status','')).lower() in ctl.TERMINAL_RUN and row.get('total_tasks')==entry['expected_cells'],'TERMINAL_SNAPSHOT_BINDING')
    inventory=[]
    for path in sorted(directory.rglob('*')):
        require(not path.is_symlink(),'LINKED_COLLECTION_FILE')
        if path.is_file() and path.name not in ('files_sha256.json','identity_receipt.json'):
            data=path.read_bytes();inventory.append({'path':str(path.relative_to(directory)),'bytes':len(data),'sha256':sha(data)})
    write(directory/'files_sha256.json',inventory)
    write(directory/'identity_receipt.json',{'scientific_run_id':RUN_ID,'key':key,'ledger_entry':entry,'ledger_entry_sha256':frozen_entry})
    evidence={'scientific_run_id':RUN_ID,'run_id':run_id,'key':key,'ledger_entry_sha256':frozen_entry,'route':origin,'new_inference_calls':0,
              'inventory_sha256':sha((directory/'files_sha256.json').read_bytes()),'command_sha256':sha(command.read_bytes()),
              'identity_sha256':sha((directory/'identity_receipt.json').read_bytes()),'files':len(inventory),'bytes':sum(x['bytes'] for x in inventory)}
    write(certificate,evidence)
    return directory,verified_files(directory),evidence
