"""Durable declared-cell-only Valkyrie controller; adopts runs and never retries.

The unmodified historical transport executes only inside Vals-funded Valkyrie.
This controller uses the authenticated Valkyrie CLI, never provider credentials.
"""
from __future__ import annotations
import argparse
from collections import Counter
import fcntl
import json
import os
from pathlib import Path
import threading
import time
from e47_adapter import ROOT,RESULTS,PRIVATE,RUN_ID,POOL,read,write,sha,phase_context,verify_dependencies
from receipt_validation import accepted
from harvest_transport import install as install_harvest_transport
from run_offline import identity,update_job

def reconcile_ambiguous_admission(ctl,cfg,part,phase,suffix=''):
    """Read-only recovery of a lost start receipt; never issue another start."""
    key=cfg+'@'+part+suffix;state=ctl.load_state();entry=state['runs'].get(key)
    if not entry or entry.get('run_id') or entry.get('phase') in ('admission_failed_verified_absent','admission_blocked_before_transport'):return
    argv=entry.get('actual_command') or entry['command'];label=entry.get('actual_label') or argv[argv.index('--label')+1].replace('cj39-','cj47-'+phase+'-',1)
    entry['phase']='admission_unresolved';ctl.save_state(state)
    for attempt in range(3):
        query=['run','list','--benchmark-name',entry['benchmark'],'--agent-name',entry['agent'],'--model',entry['selector'],'--label',label,'--format','json','--all']
        result=ctl.cli(query,timeout=600)
        if result.returncode:raise RuntimeError('cannot resolve ambiguous admission; query failed; start is never replayed')
        payload=json.loads(result.stdout);rows=payload.get('runs',[])
        write(ctl.JUDGE/'admission_resolution'/f"{cfg.replace('|','__')}__{part}__{attempt}.json",payload)
        if len(rows)>1:raise RuntimeError('multiple server runs match an ambiguous admission; preserve all and reconcile explicitly')
        if rows:
            row=rows[0];run_id=row.get('run_id') or row.get('id')
            if not isinstance(run_id,str) or not ctl.UUID_RE.fullmatch(run_id):raise ValueError('server run identity unresolved')
            entry.update(run_id=run_id,phase='running',adoption='matched unique exact benchmark/agent/model/label via authenticated read-only run list; no repeated start')
            ctl.save_state(state);return
        if attempt<2:time.sleep(30)
    entry.update(phase='admission_failed_verified_absent',adoption='three read-only exact-filter inventories found no server run; no repeated start');ctl.save_state(state)

def strict_harvest(ctl,phase,cfg,part,suffix=''):
    blob=ctl.harvested(cfg,part,suffix) if suffix else ctl.harvested(cfg,part)
    if blob is None:raise RuntimeError('harvest is unavailable; recover existing run receipts before classifying this condition')
    meta={r['cell']:r for r in ctl.pack_rows(cfg,part)}
    is_agent=ctl.unit_of(cfg)['pack_flavor']=='agent'
    receipts={}
    artifacts=ctl.RAW/f"{(cfg+'@'+part+suffix).replace('|','__').replace('@','_')}_artifacts"
    for path in sorted(artifacts.rglob('receipt.json')):
        raw=read(path);task_id=raw.get('task_id') or path.parent.name
        digest=sha(path.read_bytes())
        if task_id in receipts and receipts[task_id][1]!=digest:raise ValueError('conflicting raw transport receipts '+task_id)
        receipts[task_id]=(raw,digest)
    for cell in blob['cells']:
        expected=meta[cell['cell']]
        raw,digest=receipts.get(cell['task_id'],({},None))
        cell.update(raw_transport_receipt_sha256=digest)
        for field in ('http_status','requests_sent','attempt','error_kind','error_type'):
            if field in raw:cell[field]=raw[field]
        ok,why=accepted(cell,expected['prompt_sha256'],expected.get('instruction_sha256'))
        if not is_agent and cell.get('agent_status')!='measured':ok,why=False,'UNCLEAN_TRANSPORT_STATUS'
        if not is_agent and cell.get('requests_sent',0)>2:ok,why=False,'EXCEEDS_FROZEN_TRANSPORT_ATTEMPT_LIMIT'
        cell.update(accepted=ok,acceptance_reason=why,phase=phase,part=part)
        if not ok and cell.get('status')=='measured':cell['status']='unmeasured_infra'
    blob['accepted_count']=sum(c['accepted'] for c in blob['cells'])
    write(ctl.JUDGE/'strict_harvests'/f"{cfg.replace('|','__')}__{part}.json",blob)
    return blob

def merge_phase(ctl,phase):
    final={};summary={}
    for cfg in POOL:
        cells=read(RESULTS/phase/'cells'/f"{cfg.replace('|','__')}.json")['cells']
        path=ctl.JUDGE/'strict_harvests'/f"{cfg.replace('|','__')}__main.json"
        measured={c['cell']:c for c in read(path)['cells']} if path.exists() else {}
        merged=[]
        for c in cells:
            r=dict(c)
            if c['status']=='cached_measured':r.update(accepted=True,acceptance_reason='exact_fresh_cache_identity',source_run_id=c['cache_receipt']['run_id'])
            elif c['status']=='deterministic':r.update(accepted=True,acceptance_reason='frozen_deterministic_rule')
            elif c['cell'] in measured:
                m=measured[c['cell']]
                if m['prompt_sha256']!=c['prompt_sha256']:raise ValueError('harvest identity differs')
                r.update(m)
            else:r.update(accepted=False,acceptance_reason=c.get('reason','no accepted verdict; see phase/run receipts'))
            merged.append(r)
        if len({c['cell'] for c in merged})!=len(merged):raise ValueError('duplicate final cell')
        final[cfg]={'run_id':RUN_ID,'phase':phase,'config':cfg,'cells':merged}
        write(PRIVATE/phase/'final_harvest'/f"{cfg.replace('|','__')}.json",final[cfg])
        summary[cfg]={'declared':len(merged),'accepted':sum(r['accepted'] for r in merged),'status_counts':dict(Counter(r['status'] for r in merged))}
        # Analysis consumes the union of disjoint criterion/probe phases.
        other='probes' if phase=='criterion' else 'criterion';otherpath=PRIVATE/other/'final_harvest'/f"{cfg.replace('|','__')}.json"
        union=merged+(read(otherpath)['cells'] if otherpath.exists() else [])
        if len({r['cell'] for r in union})!=len(union):raise ValueError('phases overlap; refusing duplicate measurement')
        write(PRIVATE/'final_harvest'/f"{cfg.replace('|','__')}.json",{'run_id':RUN_ID,'config':cfg,'cells':union})
    write(RESULTS/phase/'harvest_summary.json',{'run_id':RUN_ID,'phase':phase,'per_config':summary,'whole_experiment_complete':False})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['criterion','probes'],required=True);args=ap.parse_args();phase=args.phase
    dependency_hashes=verify_dependencies()
    e,_,_,ctl=phase_context(phase);install_harvest_transport(ctl);runtime=ROOT/'runtime';name='judge_'+phase
    lock=(runtime/(name+'.lock')).open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    admission=read(e.RESULTS/'admission_manifest.json');quote=read(e.RESULTS/'QUOTE.json');packs=read(e.RESULTS/'packs.json')
    if admission['state']!='FROZEN' or set(admission['configurations'])!=set(POOL):raise ValueError('incomplete frozen admission')
    if quote['admission_manifest_sha256']!=sha((e.RESULTS/'admission_manifest.json').read_bytes()) or quote['packs_sha256']!=sha((e.RESULTS/'packs.json').read_bytes()):raise ValueError('quote is not bound to admission')
    if admission.get('transport_policy_sha256') and sha((e.RESULTS/'transport_policy.json').read_bytes())!=admission['transport_policy_sha256']:raise ValueError('frozen transport policy changed')
    for cfg,digest in admission['cells_sha256'].items():
        if sha((e.RESULTS/'cells'/f"{cfg.replace('|','__')}.json").read_bytes())!=digest:raise ValueError('frozen cell bytes changed')
    selection_path=e.RESULTS/'task_selection_transport.json'
    selection=read(selection_path) if selection_path.exists() else None
    if selection:
        if selection['run_id']!=RUN_ID or selection['phase']!=phase or selection['admission_manifest_sha256']!=quote['admission_manifest_sha256'] or selection['packs_sha256']!=quote['packs_sha256']:raise ValueError('task selection transport identity mismatch')
        for cfg,selected in selection['configurations'].items():
            ids=[r['task_id'] for r in ctl.pack_rows(cfg,'main')]
            if selected['task_ids_sha256']!=sha(('\n'.join(sorted(ids))+'\n').encode()) or selected['expected_cells']!=len(ids) or not selected['remote_verified_equal']:raise ValueError('slice differs from full declared task list')
    def suffix_for(cfg,part):return (selection or {}).get('suffixes',{}).get(cfg,'') if part=='main' else ''
    # Exact historical selectors are the sole allowed selectors. All scientific
    # harness settings come from the already verified panel/harness receipts.
    write(e.RESULTS/'selectors.json',{u['model_key']:{'selector':u['selectors'][0],'source':'frozen historical E39 harvest'} for u in read(e.RESULTS/'panel.json')['units']})
    original_cli=ctl.cli
    def cli(argv,timeout=1800):
        original=list(argv);argv=list(argv)
        if '--label' in argv:
            i=argv.index('--label')+1;argv[i]=argv[i].replace('cj39-','cj47-'+phase+'-',1)
        if argv[:2]==['run','start']:
            if phase=='probes':
                from callback_gate import before_probe_transport
                gate=before_probe_transport(ctl,ROOT,quote['admission_manifest_sha256'],original)
                write(runtime/'callback_last_transport_gate.json',gate)
            if selection and '--task-ids-file' in argv:
                for cfg,selected in selection['configurations'].items():
                    if Path(argv[argv.index('--task-ids-file')+1]).name==f"task_ids_{(cfg+'@main'+suffix_for(cfg,'main')).replace('|','__').replace('@','_')}.txt":
                        index=argv.index('--task-ids-file');argv[index:index+2]=['--slice',selected['slice']];break
            label=argv[argv.index('--label')+1]
            write(ctl.JUDGE/'actual_admission_commands'/(label+'.json'),{'argv':argv,'recorded_before_call':True,'recorded_epoch':time.time()})
            state=ctl.load_state()
            for entry in state['runs'].values():
                if entry.get('phase')=='admitting' and entry.get('command')==original:
                    entry['actual_command']=argv;entry['actual_label']=argv[argv.index('--label')+1]
            ctl.save_state(state)
        return original_cli(argv,timeout)
    ctl.cli=cli
    state={'run_id':RUN_ID,'phase':phase,'driver':identity(os.getpid()),'state':'RUNNING','started_epoch':time.time(),'route':'Vals-funded Valkyrie','admission_manifest_sha256':quote['admission_manifest_sha256'],'verified_frozen_dependency_count':len(dependency_hashes),'executor_code_sha256':sha(Path(__file__).read_bytes())}
    stop=threading.Event()
    def beat():
        while not stop.is_set():
            state['heartbeat_epoch']=time.time();write(runtime/(name+'.json'),dict(state));update_job(name,dict(state));stop.wait(30)
    heartbeat=threading.Thread(target=beat,daemon=True);heartbeat.start()
    try:
        unavailable={}
        for part in ('smoke','main'):
            state['stage']=part
            if part=='smoke' and phase=='probes':
                receipts={}
                for cfg in POOL:
                    path=PRIVATE/'criterion/judge/strict_harvests'/f"{cfg.replace('|','__')}__smoke.json"
                    blob=read(path) if path.exists() else None
                    if not blob or not blob['cells'] or blob['accepted_count']!=len(blob['cells']):
                        unavailable[cfg]='original distinct criterion smoke did not pass; probe condition retained unavailable'
                    else:receipts[cfg]={'run_id':blob['run_id'],'sha256':sha(path.read_bytes()),'reused_without_new_call':True}
                write(e.RESULTS/'smoke_reuse.json',{'run_id':RUN_ID,'receipts':receipts,'unavailable':unavailable})
                continue
            for cfg in POOL:
                if cfg in unavailable:continue
                if not ctl.pack_rows(cfg,part):continue
                suffix=suffix_for(cfg,part)
                if phase=='probes':
                    from callback_gate import admit_probe
                    admit_probe(ctl,ROOT,quote['admission_manifest_sha256'],cfg,part,suffix)
                else:ctl.admit(cfg,part,concurrency=20,suffix=suffix)
                ledger=ctl.load_state();entry=ledger['runs'][cfg+'@'+part+suffix]
                argv=entry['command'];label=argv[argv.index('--label')+1].replace('cj39-','cj47-'+phase+'-',1)
                actual=ctl.JUDGE/'actual_admission_commands'/(label+'.json')
                if actual.exists():entry.update(actual_command=read(actual)['argv'],actual_label=label);ctl.save_state(ledger)
                reconcile_ambiguous_admission(ctl,cfg,part,phase,suffix)
            while True:
                ctl.poll(publish=True);runs=ctl.load_state()['runs'];pending=[]
                changed=False
                for key,entry in runs.items():
                    if entry.get('phase')!='terminal' and entry.get('run_status') in ctl.TERMINAL_RUN:
                        entry.update(phase='terminal',e47_terminal_resolution='server terminal state; missing task rows retained unavailable',terminal_shortfall=max(0,entry['expected_cells']-entry.get('cells_terminal',0)));changed=True
                if changed:
                    current=ctl.load_state();current['runs']=runs;ctl.save_state(current)
                for cfg in POOL:
                    entry=runs.get(cfg+'@'+part+suffix_for(cfg,part))
                    if entry and entry.get('run_id') and entry.get('phase')!='terminal':pending.append(cfg)
                state['pending_configurations']=pending
                if not pending:break
                time.sleep(30)
            for cfg in POOL:
                suffix=suffix_for(cfg,part);entry=ctl.load_state()['runs'].get(cfg+'@'+part+suffix)
                if entry and entry.get('run_id') and entry.get('phase')=='terminal':
                    strict_path=ctl.JUDGE/'strict_harvests'/f"{cfg.replace('|','__')}__{part}.json"
                    if not strict_path.exists():
                        ctl.harvest(cfg,part,suffix);blob=strict_harvest(ctl,phase,cfg,part,suffix)
                    else:blob=read(strict_path)
                    if part=='smoke' and (blob is None or blob['accepted_count']!=len(blob['cells'])):unavailable[cfg]='smoke transport/parser failed; main condition retained unavailable, no silent retry'
                elif part=='smoke':unavailable[cfg]='no successful smoke admission; inspect recorded admission failure'
            write(e.RESULTS/'unavailable_conditions.json',{'run_id':RUN_ID,'phase':phase,'conditions':unavailable})
        merge_phase(ctl,phase)
        charges=[]
        for path in sorted((ctl.JUDGE/'strict_harvests').glob('*.json')):
            b=read(path);charges.append({'config':b['config'],'part':b['part'],'run_id':b['run_id'],'known_reported_sum_usd':b['charges_usd'],'unknown_charge_cells':sum(c.get('cost_usd') is None for c in b['cells']),'cells':b['n_cells'],'accepted':b['accepted_count']})
        total=sum(r['known_reported_sum_usd'] for r in charges);unknown=sum(r['unknown_charge_cells'] for r in charges)
        write(e.RESULTS/'charges.json',{'route':'Vals-funded Valkyrie','runs':charges,'reported_total_usd':None if unknown else total,'known_reported_sum_usd':total,'unknown_charge_cells':unknown,'source':'Valkyrie agent receipts and exported trajectory final_metrics; missing billing is not zero'})
        state['state']='RECONCILED';write(runtime/(name+'_RECONCILED.json'),state)
    except BaseException as exc:
        state.update(state='DRIVER_ERROR',error_type=type(exc).__name__,error=str(exc)[:400]);raise
    finally:
        stop.set();heartbeat.join(timeout=2);state['heartbeat_epoch']=time.time();write(runtime/(name+'.json'),state)
        # Retain a job requiring adoption if remote runs are still live or their
        # admission outcome is ambiguous, even when this coordinator exits.
        active=any(r.get('phase') in ('running','admitting','admission_unresolved') for r in ctl.load_state()['runs'].values())
        update_job(name,state if active else None)

if __name__=='__main__':main()
