"""Construct the complete declared campaign; structural evidence gates final freeze."""
from __future__ import annotations
import argparse
from collections import Counter
import copy
import json
from pathlib import Path
import random
from e47_adapter import ROOT,PRIVATE,RESULTS,RUN_ID,POOL,read,write,sha,load_items,panel,frozen,prompts,module,phase_context

def build(probe_manifest=None,probe_root=None,freeze=False):
    e,renderer,packer,ctl=frozen();p=prompts();items=load_items();byitem={r['item']:r for r in items};bytask={r['task']:r for r in items}
    units=panel();write(RESULTS/'panel.json',{'run_id':RUN_ID,'units':units})
    cache=read(PRIVATE/'accepted_cached_primary_scores.json')
    structural=read(probe_manifest) if probe_manifest else {'rows':[]}
    probe_root=Path(probe_root or ROOT)
    if freeze and not probe_manifest:raise ValueError('full structural manifest required')
    if freeze and any(r.get('valid') is None for r in structural['rows']):raise ValueError('pending structural evidence')
    artifacts={(a['kind'],a['key'],a['level']):a for a in structural.get('private_artifacts',[])}
    probes=[]
    for item in items:
        probes.append({'probe_id':'crit__'+item['item']+'__L0','kind':'crit','key':item['item'],'task':item['task'],'item':item['item'],'level':0,'sha256':item['cand_sha256'],'valid':True,'path':item['candidate_path_abs']})
    for original in structural['rows']:
        if original['kind']=='crit':continue
        r=dict(original);r['source_key']=r['key'];r['key']=r['key'].replace('/','__')
        base=byitem[r['item']] if r.get('item') else bytask[r['task']]
        if r['kind']=='ident':r['path']=base['ref_ann_path_abs']
        elif r['kind']=='blank':r['path']=None
        elif r['valid']:
            a=artifacts[(r['kind'],original['key'],r['level'])];r['path']=str(probe_root/a['private_relpath'])
            if sha(Path(r['path']).read_bytes())!=r['sha256']:raise ValueError('probe artifact hash mismatch')
        probes.append(r)
    if freeze:
        if len({r['task'] for r in probes if r['kind']=='ident'})!=50:raise ValueError('missing reference tasks')
        if len({r['item'] for r in probes if r['kind']=='crit'})!=750:raise ValueError('missing criterion items')
    manifests={};all_counts={}
    for unit in units:
        cells=[];cfg=unit['config']
        for r in probes:
            n=2 if r['kind']=='ms_gold' else e.KINDS[r['kind']]['repeats']
            base=byitem[r['item']] if r.get('item') else bytask[r['task']]
            common={'kind':r['kind'],'key':r['key'],'task':r['task'],'item':r.get('item'),'level':r['level'],'probe_id':r['probe_id'],'candidate_sha256':r.get('sha256'),'valid':r['valid']}
            if not r['valid']:
                rendered=[dict(common,repeat=k,cell=renderer.cell_id(r['kind'],r['key'],r['level'],k),status='structurally_invalid',reason=r.get('reason')) for k in range(1,n+1)]
            elif r['kind']=='crit' and base['blank']:
                rendered=[dict(common,repeat=k,cell=renderer.cell_id('crit',r['key'],0,k),status='deterministic',score=0.,reason='source declared blank; excluded from nonblank primary',structural_blank=True) for k in range(1,n+1)]
            else:
                row={**r,'base_item':base,'candidate_name':base['candidate_file'] if r.get('item') else base['ref_name'].removesuffix('.lean')+'__agent3.lean'}
                # Only the supplement changes repeat construction. No prompt or
                # scientific selector/harness setting is modified.
                old=e.KINDS[r['kind']]['repeats'];e.KINDS[r['kind']]['repeats']=n
                try:rendered=renderer.render_unit(unit,[row],p,False)['cells']
                finally:e.KINDS[r['kind']]['repeats']=old
                for c in rendered:c['valid']=True
            for cell in rendered:
                cell['config']=cfg;cell['supplemental_repeat']=r['kind']=='ms_gold' and cell['repeat']==2
                if r['kind']=='crit' and not base['blank'] and cfg in cache:
                    receipt=next((x for x in cache[cfg][r['item']]['repeats'] if x['repeat']==cell['repeat']),None)
                    if receipt is not None:
                        if cell.get('prompt_sha256')!=receipt['prompt_sha256']:raise ValueError('render/cache hash mismatch')
                        cell.update(status='cached_measured' if receipt['accepted'] else 'cached_unavailable',cache_receipt=receipt)
                        if receipt['accepted']:cell['score']=receipt['score']
            cells.extend(rendered)
        if len({c['cell'] for c in cells})!=len(cells):raise ValueError('duplicate E47 cell')
        blob={'run_id':RUN_ID,'config':cfg,'n_cells':len(cells),'n_calls':sum(c['status']=='render' for c in cells),'cells':cells}
        write(RESULTS/'cells'/f"{cfg.replace('|','__')}.json",blob);manifests[cfg]=blob;all_counts[cfg]=dict(Counter(c['status'] for c in cells))
    hashes={str(p.relative_to(ROOT.parent)):sha(p.read_bytes()) for p in [ROOT.parent/'PROTOCOL.md',*sorted(ROOT.parent.glob('AMENDMENT_*.md'))]}
    receipt={'run_id':RUN_ID,'state':'FROZEN' if freeze else 'DRAFT_PENDING_STRUCTURAL_EVIDENCE','configurations':list(POOL),'counts':all_counts,'contract_hashes':hashes,'probe_manifest_sha256':sha(Path(probe_manifest).read_bytes()) if probe_manifest else None,'cells_sha256':{cfg:sha((RESULTS/'cells'/f"{cfg.replace('|','__')}.json").read_bytes()) for cfg in manifests},'route':'Vals-funded Valkyrie only; no host provider keys','recovery':'No automatic retries or re-admission of any cached receipt, including failed receipts.'}
    target=RESULTS/'admission_manifest.json'
    if target.exists() and read(target).get('state')=='FROZEN' and read(target)!=receipt:raise ValueError('refusing to rewrite frozen admission')
    write(target,receipt)
    print(json.dumps({'state':receipt['state'],'counts':all_counts}))

def build_packs(phase='criterion'):
    e,_,pack,_=phase_context(phase);out=e.RESULTS;private=e.PRIVATE
    admission=read(out/'admission_manifest.json');assert admission['state']=='FROZEN'
    units=read(out/'panel.json')['units'];result={'run_id':RUN_ID,'phase':phase,'packs':{},'verdict':'PASS'}
    # Import parser only; its network entry points are never invoked on host.
    parser=module('e47_frozen_transport_parser',e.X103/'scripts/valkyrie_judge_agent/judge_call.py').parse_task_file
    for model in sorted({u['model_key'] for u in units}):
        directory=private/'packs'/model;per_config={}
        for unit in [u for u in units if u['model_key']==model]:
            cfg=unit['config'];cp=out/'cells'/f"{cfg.replace('|','__')}.json"
            if sha(cp.read_bytes())!=admission['cells_sha256'][cfg]:raise ValueError('admission hash changed')
            cells=read(cp)['cells'];pending=[c for c in cells if c['status']=='render'];random.Random(f'47|{cfg}').shuffle(pending)
            rows=[];smokes=[]
            def emit(c,tid):
                blob=read(private/'cells'/cfg.replace('|','__')/(c['cell']+'.json'))
                if sha((blob['system']+'\n\n'+blob['user']).encode())!=c['prompt_sha256']:raise ValueError('prompt changed')
                row=pack.emit(directory,tid,c,unit['rubric'],blob,unit['pack_flavor'])
                body=(directory/tid/'instruction.md').read_text();h,system,user=(pack.parse_agent_task_file if unit['pack_flavor']=='agent' else parser)(body)
                if sha((system+'\n\n'+user).encode())!=c['prompt_sha256']:raise ValueError('transport roundtrip')
                return row
            for i,c in enumerate(pending):rows.append({**emit(c,pack.task_id_of('cj47',unit['prompt_key'],f'q{i:05d}__'+c['cell'])),'queue_index':i})
            smoke=next((c for c in sorted(cells,key=lambda c:c['cell']) if c['kind']=='crit' and c['repeat']==1 and c.get('prompt_sha256') and c['status'] in ('render','cached_measured')),None)
            if smoke:smokes.append(emit(smoke,pack.task_id_of('cj47smoke',unit['prompt_key'],smoke['cell'])))
            per_config[cfg]={'rubric':unit['rubric'],'prompt_key':unit['prompt_key'],'flavor':unit['pack_flavor'],'harness':unit['harness'],'n_tasks':len(rows),'n_smoke_tasks':len(smokes),'cells':rows,'smoke_cells':smokes,'round_trip_failures':[]}
        result['packs'][model]={'model_key':model,'pack':str(directory),'benchmark':'certjudge47-v5-a1-'+phase+'-'+model.replace('_','-'),'per_config':per_config,'n_tasks_total':sum(x['n_tasks']+x['n_smoke_tasks'] for x in per_config.values())}
    write(out/'packs.json',result)
    print('Frozen packs round-trip PASS:',sum(x['n_tasks_total'] for x in result['packs'].values()),'declared tasks including distinct smoke conditions')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--probe-manifest',type=Path);ap.add_argument('--probe-root',type=Path);ap.add_argument('--freeze',action='store_true');ap.add_argument('--packs',action='store_true');ap.add_argument('--phase',default='criterion');args=ap.parse_args()
    if args.packs:build_packs(args.phase)
    else:build(args.probe_manifest,args.probe_root,args.freeze)
