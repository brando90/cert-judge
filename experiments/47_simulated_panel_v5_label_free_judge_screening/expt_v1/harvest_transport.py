"""Read-only Valkyrie artifact collection, preserving existing run evidence.

The current CLI's results response validator rejects these completed runs.
The authenticated output command downloads their original archived final view.
No provider client, completion callback, or run admission is used here.
"""
import json
import shutil
import time
from e47_adapter import read,write,sha,RUN_ID

def install(ctl):
    def download(key,run_id):
        entry=ctl.load_state()['runs'][key]
        if entry['run_id']!=run_id:raise ValueError('download run identity differs')
        name=key.replace('|','__').replace('@','_');ctl.RAW.mkdir(parents=True,exist_ok=True)
        artifacts=ctl.RAW/(name+'_artifacts');results=ctl.RAW/(name+'_results.json')
        original=artifacts/(entry['benchmark']+'.json')
        receipt=ctl.RAW/(name+'_artifact_collection.json')
        # Adopt the already successful frozen download only when its recorded
        # output command succeeded. All other partial directories are retained.
        log=ctl.RAW/(name+'_download.log')
        prior_success=log.exists() and any('run output '+run_id+' rc=0' in line for line in log.read_text().splitlines())
        collected=read(receipt) if receipt.exists() else None
        if collected and (collected.get('run_id')!=run_id or collected.get('scientific_run_id')!=RUN_ID):raise ValueError('collection receipt identity mismatch')
        if not (original.exists() and (collected or prior_success)):
            staging=ctl.RAW/(name+'_download_'+str(time.time_ns()));staging.mkdir()
            done=ctl.cli(['run','output',run_id,'-o',str(staging)],timeout=5400)
            write(staging/'collection_command.json',{'run_id':run_id,'returncode':done.returncode,'stdout':done.stdout,'stderr':done.stderr})
            if done.returncode:raise RuntimeError('read-only artifact collection failed; partial evidence retained at '+str(staging))
            if artifacts.exists():artifacts.rename(ctl.RAW/(name+'_preserved_partial_'+str(time.time_ns())))
            staging.rename(artifacts)
        if not original.exists():raise RuntimeError('archived final view unavailable; no scientific failure inferred')
        payload=read(original)
        if payload.get('benchmark_id')!=run_id or payload.get('benchmark_name')!=entry['benchmark']:raise ValueError('archived final view identity mismatch')
        if str(payload.get('status','')).lower() not in ctl.TERMINAL_RUN:raise ValueError('archived final view is not terminal')
        rows=ctl.rows_of(original);cfg=entry['config'];part=entry['part']
        wanted=set(entry.get('task_ids') or [r['task_id'] for r in ctl.pack_rows(cfg,part)])
        if set(rows)-wanted:raise ValueError('archived final view has undeclared task IDs')
        for task_id,row in rows.items():
            if row.get('task_id',task_id)!=task_id:raise ValueError('task identity differs inside archived result')
        digest=sha(original.read_bytes())
        if collected and collected['archived_final_view_sha256']!=digest:raise ValueError('archived final view changed after collection')
        if results.exists() and sha(results.read_bytes())!=digest:results.rename(ctl.RAW/(name+'_preserved_results_'+str(time.time_ns())+'.json'))
        shutil.copyfile(original,results)
        write(receipt,{'scientific_run_id':RUN_ID,'run_id':run_id,'route':'authenticated valk run output; archived terminal benchmark final view',
                      'archived_final_view_sha256':digest,'expected_tasks':len(wanted),'returned_tasks':len(rows),'missing_tasks':sorted(wanted-set(rows)),
                      'new_measured_calls':0,'collected_epoch':time.time()})
        return results,artifacts
    ctl.download=download
