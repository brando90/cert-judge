"""Durable declared-cell-only Valkyrie controller; adopts runs and never retries.

The unmodified historical transport executes only inside Vals-funded Valkyrie.
This controller uses the authenticated Valkyrie CLI, never provider credentials.
"""
from __future__ import annotations
import argparse
from collections import Counter
import fcntl
import os
from pathlib import Path
import threading
import time
from e47_adapter import ROOT,RESULTS,PRIVATE,RUN_ID,POOL,read,write,sha,phase_context
from receipt_validation import accepted
from run_offline import identity,update_job

def strict_harvest(ctl,phase,cfg,part):
    blob=ctl.harvested(cfg,part)
    if blob is None:return None
    meta={r['cell']:r for r in ctl.pack_rows(cfg,part)}
    is_agent=ctl.unit_of(cfg)['pack_flavor']=='agent'
    for cell in blob['cells']:
        expected=meta[cell['cell']]
        ok,why=accepted(cell,expected['prompt_sha256'],expected.get('instruction_sha256'))
        if not is_agent and cell.get('agent_status')!='measured':ok,why=False,'UNCLEAN_TRANSPORT_STATUS'
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
    e,_,_,ctl=phase_context(phase);runtime=ROOT/'runtime';name='judge_'+phase
    lock=(runtime/(name+'.lock')).open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    admission=read(e.RESULTS/'admission_manifest.json');quote=read(e.RESULTS/'QUOTE.json');packs=read(e.RESULTS/'packs.json')
    if admission['state']!='FROZEN' or set(admission['configurations'])!=set(POOL):raise ValueError('incomplete frozen admission')
    if quote['admission_manifest_sha256']!=sha((e.RESULTS/'admission_manifest.json').read_bytes()) or quote['packs_sha256']!=sha((e.RESULTS/'packs.json').read_bytes()):raise ValueError('quote is not bound to admission')
    for cfg,digest in admission['cells_sha256'].items():
        if sha((e.RESULTS/'cells'/f"{cfg.replace('|','__')}.json").read_bytes())!=digest:raise ValueError('frozen cell bytes changed')
    # Exact historical selectors are the sole allowed selectors. All scientific
    # harness settings come from the already verified panel/harness receipts.
    write(e.RESULTS/'selectors.json',{u['model_key']:{'selector':u['selectors'][0],'source':'frozen historical E39 harvest'} for u in read(e.RESULTS/'panel.json')['units']})
    original_cli=ctl.cli
    def cli(argv,timeout=1800):
        argv=list(argv)
        if '--label' in argv:
            i=argv.index('--label')+1;argv[i]=argv[i].replace('cj39-','cj47-'+phase+'-',1)
        return original_cli(argv,timeout)
    ctl.cli=cli
    state={'run_id':RUN_ID,'phase':phase,'driver':identity(os.getpid()),'state':'RUNNING','started_epoch':time.time(),'route':'Vals-funded Valkyrie','admission_manifest_sha256':quote['admission_manifest_sha256']}
    stop=threading.Event()
    def beat():
        while not stop.is_set():
            state['heartbeat_epoch']=time.time();write(runtime/(name+'.json'),dict(state));update_job(name,dict(state));stop.wait(30)
    heartbeat=threading.Thread(target=beat,daemon=True);heartbeat.start()
    try:
        unavailable={}
        for part in ('smoke','main'):
            state['stage']=part
            for cfg in POOL:
                if cfg in unavailable:continue
                if not ctl.pack_rows(cfg,part):continue
                ctl.admit(cfg,part,concurrency=20)
            while True:
                ctl.poll(publish=True);runs=ctl.load_state()['runs'];pending=[]
                for cfg in POOL:
                    entry=runs.get(cfg+'@'+part)
                    if entry and entry.get('run_id') and entry.get('phase')!='terminal':pending.append(cfg)
                state['pending_configurations']=pending
                if not pending:break
                time.sleep(30)
            for cfg in POOL:
                entry=ctl.load_state()['runs'].get(cfg+'@'+part)
                if entry and entry.get('run_id') and entry.get('phase')=='terminal':
                    strict_path=ctl.JUDGE/'strict_harvests'/f"{cfg.replace('|','__')}__{part}.json"
                    if not strict_path.exists():
                        ctl.harvest(cfg,part);blob=strict_harvest(ctl,phase,cfg,part)
                    else:blob=read(strict_path)
                    if part=='smoke' and (blob is None or blob['accepted_count']!=len(blob['cells'])):unavailable[cfg]='smoke transport/parser failed; main condition retained unavailable, no silent retry'
                elif part=='smoke':unavailable[cfg]='no successful smoke admission; inspect recorded admission failure'
            write(e.RESULTS/'unavailable_conditions.json',{'run_id':RUN_ID,'phase':phase,'conditions':unavailable})
        merge_phase(ctl,phase)
        charges=[]
        for path in sorted((ctl.JUDGE/'strict_harvests').glob('*.json')):
            b=read(path);charges.append({'config':b['config'],'part':b['part'],'run_id':b['run_id'],'reported_charges_usd':b['charges_usd'],'cells':b['n_cells'],'accepted':b['accepted_count']})
        write(e.RESULTS/'charges.json',{'route':'Vals-funded Valkyrie','runs':charges,'reported_total_usd':sum(r['reported_charges_usd'] for r in charges)})
        state['state']='RECONCILED';write(runtime/(name+'_RECONCILED.json'),state)
    except BaseException as exc:
        state.update(state='DRIVER_ERROR',error_type=type(exc).__name__,error=str(exc)[:400]);raise
    finally:
        stop.set();heartbeat.join(timeout=2);state['heartbeat_epoch']=time.time();write(runtime/(name+'.json'),state)
        # Retain a job requiring adoption if remote runs are still live or their
        # admission outcome is ambiguous, even when this coordinator exits.
        active=any(r.get('phase') in ('running','admitting') for r in ctl.load_state()['runs'].values())
        update_job(name,state if active else None)

if __name__=='__main__':main()
