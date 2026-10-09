"""Strict probe reconciliation from original artifacts and an optional real final view.

No inferred submission, synthetic server view, transport retry or new admission.
Collection is separate from the offline verifier and every expected task survives.
"""
import base64
from collections import Counter
from contextlib import ExitStack
import json
from pathlib import Path
from unittest.mock import patch
from e47_adapter import ROOT, RESULTS, RUN_ID, POOL, read, write, sha, phase_context, verify_dependencies, panel, prompts, module
import harvest_original_artifacts as h
from receipt_validation import accepted
from collect_probe_artifacts import collect


def certify_agent(row, served, meta, unit, parse):
    h.require(served.get('task_id')==meta['task_id'],'SERVER_TASK_BINDING')
    h.require(served.get('instruction_sha256')==meta['instruction_sha256'],'SERVER_INSTRUCTION_BINDING')
    row.update(server_submission_status=served.get('submission_status'),instruction_sha256_served=served['instruction_sha256'])
    if served.get('submission_status')!='ok':return
    h.require(row.get('frozen_instruction_sha256')==meta['instruction_sha256'],'REQUEST_NOT_VERIFIED')
    # Never use a final view to hide contradictory archive or trajectory evidence.
    h.require(row['acceptance_reason'] in ('SUBMITTED_VERDICT_BYTES_UNCERTIFIED','ARTIFACT_ABSENT_UNRESOLVED','MISSING_TRAJECTORY_ACCOUNTING'),'CONFLICTING_ARTIFACT_EVIDENCE')
    data=base64.b64decode(served['solution_b64'],validate=True)
    h.require(len(data)==served.get('solution_bytes') and sha(data)==served.get('solution_sha256'),'SERVER_VERDICT_BYTES')
    raw,normalized,verdict=parse(unit,data.decode('utf-8'))
    row.update(status='measured',score_raw=raw,score=normalized,verdict_sha256=sha(data),verdict_bytes=len(data),
               submission_evidence='original authenticated benchmark final view; exact submitted bytes/size/hash and served instruction',
               rationale=str(verdict.get('rationale') or verdict.get('reasoning') or verdict.get('reason') or '')[:300])
    row['accepted'],row['acceptance_reason']=accepted(row,meta['prompt_sha256'],meta['instruction_sha256'])


def verify(ctl, config, key, directory, indexed, collection):
    """Offline only. Transport entry points and provider functions must fail closed."""
    dependencies=verify_dependencies();units=h.unique(panel(),'config');e,_,pack,ctl=phase_context('probes')
    state=ctl.load_state();entry=state['runs'][key];unit=units[config]
    h.require(collection['scientific_run_id']==RUN_ID and collection['run_id']==entry['run_id']
              and collection['ledger_entry_sha256']==sha(json.dumps(entry,sort_keys=True).encode()),'COLLECTION_LEDGER_BINDING')
    admission=read(e.RESULTS/'admission_manifest.json');quote=read(e.RESULTS/'QUOTE.json');packs=read(e.RESULTS/'packs.json')
    h.require(admission['run_id']==RUN_ID and admission['phase']=='probes' and admission['state']=='FROZEN' and set(admission['configurations'])==set(POOL),'ADMISSION_IDENTITY')
    h.require(sha((e.RESULTS/'admission_manifest.json').read_bytes())==quote['admission_manifest_sha256'] and sha((e.RESULTS/'packs.json').read_bytes())==quote['packs_sha256'],'QUOTE_BINDING')
    h.require(sha((ROOT/'probes/probe_manifest.json').read_bytes())==admission['probe_manifest_sha256'],'STRUCTURAL_MANIFEST_BINDING')
    for name,digest in admission['contract_hashes'].items():h.require(sha((ROOT.parent/name).read_bytes())==digest,'CONTRACT_CHANGED:'+name)
    h.require(sha((e.RESULTS/'transport_policy.json').read_bytes())==admission['transport_policy_sha256'],'TRANSPORT_POLICY_CHANGED')
    h.require(h.unique(read(e.RESULTS/'panel.json')['units'],'config')==units,'FROZEN_PANEL_CHANGED')
    packed=packs['packs'][unit['model_key']];per=packed['per_config'][config]
    h.require(entry['config']==config and entry['part']=='main' and entry['phase']=='terminal' and entry['run_status'] in ctl.TERMINAL_RUN,'TERMINAL_RUN_BINDING')
    h.require(entry['selector']==unit['selectors'][0] and entry['harness']==unit['harness'] and entry['benchmark']==packed['benchmark'],'LEDGER_MODEL_BINDING')
    h.require(per['rubric']==unit['rubric'] and per['flavor']==unit['pack_flavor'] and per['harness']==unit['harness'],'PACK_CONFIG_BINDING')
    kwargs=dict(unit['kwargs'])
    if unit['pack_flavor']!='agent':kwargs.update(judge_config=config,max_tokens=str(unit['max_tokens']),benchmark=entry['benchmark'])
    h.require(entry['kwargs']==kwargs,'LEDGER_KWARGS')
    harness=read(e.RESULTS/('agent_harness.json' if unit['pack_flavor']=='agent' else 'agent_bundle_check.json'))
    h.require(harness['verdict']=='PASS' and entry['agent']==harness['agent'] and entry['judge_agent_sha256']==(harness['contract_sha256'] if unit['pack_flavor']=='agent' else h.WRITER_SHA),'HARNESS_BINDING')
    cells_path=e.RESULTS/'cells'/(config.replace('|','__')+'.json');h.require(sha(cells_path.read_bytes())==admission['cells_sha256'][config],'CELL_BYTES_CHANGED')
    cells=h.unique(read(cells_path)['cells'],'cell');metas=h.unique(per['cells'],'task_id');wanted=list(metas)
    h.require({m['cell'] for m in metas.values()}=={c['cell'] for c in cells.values() if c['status']=='render'} and len({m['cell'] for m in metas.values()})==len(metas),'PACK_CELL_MASK')
    h.require(entry['task_ids'] is None or entry['task_ids']==wanted,'LEDGER_TASK_MASK')
    h.require(Path(entry['task_ids_file']).read_text().splitlines()==wanted,'ADMITTED_TASK_FILE')
    selection=read(e.RESULTS/'task_selection_transport.json');selected=selection['configurations'][config]
    h.require(selection['run_id']==RUN_ID and selection['phase']=='probes' and selection['admission_manifest_sha256']==quote['admission_manifest_sha256'] and selection['packs_sha256']==quote['packs_sha256'],'SELECTION_BINDING')
    h.require(selected['expected_cells']==len(wanted) and selected['remote_verified_equal'] and selected['benchmark']==entry['benchmark'] and selected['task_ids_sha256']==sha(('\n'.join(sorted(wanted))+'\n').encode()),'SELECTION_MASK')
    argv=entry['actual_command']
    for flag,value in [('--slice',selected['slice']),('--benchmark',entry['benchmark']),('--agent',entry['agent']),('--model',entry['selector']),('--label',entry['actual_label'])]:h.require(argv[argv.index(flag)+1]==value,'ACTUAL_COMMAND_BINDING:'+flag)
    h.require(sha(h.WRITER.read_bytes())==h.WRITER_SHA,'WRITER_CHANGED');writer=module('e47_offline_original_writer',h.WRITER);prompt_module=prompts();parse=lambda u,t:ctl.parse_verdict(u,t,prompt_module)
    with ExitStack() as stack:
        for name in ('cli','admit','poll','download','harvest','save_state'):stack.enter_context(patch.object(ctl,name,h.offline_only))
        for name in ('gateway_request','registry_entry'):stack.enter_context(patch.object(writer,name,h.offline_only))
        rows=h.harvest_run({'frozen_task_ids':wanted},entry,unit,metas,cells,packed,pack,writer,parse,directory,indexed,phase='probes')
        original=directory/(entry['benchmark']+'.json');final_digest=None
        if original.exists():
            payload=h.json_bytes(original.read_bytes());h.require(payload.get('benchmark_id')==entry['run_id'] and payload.get('benchmark_name')==entry['benchmark'] and str(payload.get('status','')).lower() in ctl.TERMINAL_RUN,'FINAL_VIEW_IDENTITY')
            final_digest=sha(original.read_bytes());served=ctl.rows_of(original);h.require(set(served)<=set(metas),'UNDECLARED_SERVER_TASK')
            for row in rows:
                if row['task_id'] not in served:continue
                server=served[row['task_id']];meta=metas[row['task_id']]
                try:
                    h.require(server.get('task_id')==row['task_id'] and server.get('instruction_sha256')==meta['instruction_sha256'],'SERVER_REQUEST_BINDING')
                    if unit['pack_flavor']=='agent':certify_agent(row,server,meta,unit,parse)
                    elif server.get('submission_status')=='ok':
                        data=base64.b64decode(server['solution_b64'],validate=True)
                        h.require(len(data)==server.get('solution_bytes') and sha(data)==server.get('solution_sha256')==row.get('verdict_sha256'),'CONFLICTING_SERVER_VERDICT')
                    row['server_submission_status']=server.get('submission_status')
                except (ValueError,KeyError) as exc:row.update(accepted=False,status='unmeasured_infra',acceptance_reason=str(exc)[:250])
    return {'scientific_run_id':RUN_ID,'run_id':entry['run_id'],'config':config,'part':'main','phase':'probes','selector':entry['selector'],'kwargs':entry['kwargs'],
            'n_cells':len(rows),'cells':rows,'accepted_count':sum(r['accepted'] for r in rows),'status_counts':dict(Counter(r['status'] for r in rows)),
            'charges_usd':sum(r.get('cost_usd') or 0 for r in rows),'evidence_kind':'original_probe_artifacts_and_optional_real_final_view','server_final_view_sha256':final_digest,
            'server_run_status':entry['run_status'],'server_task_state_counts':entry['task_state_counts'],'collection':collection,'dependencies_verified':len(dependencies)}


def harvest(ctl,config,part,suffix=''):
    h.require(part=='main','PROBE_MAIN_ONLY');key=config+'@'+part+suffix
    directory,indexed,certificate=collect(ctl,key)
    blob=verify(ctl,config,key,directory,indexed,certificate)
    path=ctl.JUDGE/'strict_harvests'/(config.replace('|','__')+'__main.json')
    if path.exists():h.require(read(path)==blob,'EXISTING_STRICT_HARVEST_DIFFERS')
    else:write(path,blob)
    return blob
