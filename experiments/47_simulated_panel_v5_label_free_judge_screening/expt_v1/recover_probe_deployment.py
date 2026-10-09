"""Finish a timed-out pre-admission deployment using its unchanged live processes.

Explicit recovery only: requires a saved process observation, no probe admissions
or callback binding, current exact identities, source hashes and four health
codes. Executes only the frozen deployer's final local config/receipt writer.
Never launches processes, replaces a URL or performs inference.
"""
import argparse
import ast
from pathlib import Path
import re
import sys
import time
import types
from e47_adapter import ROOT, PRIVATE, RESULTS, RUN_ID, VENDOR, read, write, sha, verify_dependencies, phase_context
from callback_watch import MODELS, process, health
from deploy_e47 import BASE_IMAGE


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',choices=MODELS,required=True);ap.add_argument('--evidence',type=Path,required=True);args=ap.parse_args()
    verify_dependencies();e,*_=phase_context('probes');model=args.model;private=e.PRIVATE;port=9044+MODELS.index(model)
    if (ROOT/'runtime/callback_binding.json').exists():raise ValueError('bound callbacks cannot be recovered with this adapter')
    ledger=private/'judge/state.json'
    if ledger.exists() and read(ledger).get('runs'):raise ValueError('probe admission already exists')
    receipt_path=private/f'deployment_{model}.json'
    if receipt_path.exists():raise ValueError('existing deployment must be adopted through status, not rewritten')
    evidence=read(args.evidence);observed={k:process(int((private/f'{k}_{model}.pid').read_text())) for k in ('service','tunnel')}
    if any(observed[k]!=evidence[k] for k in observed):raise ValueError('partial deployment process changed')
    source=(VENDOR/'deploy_service.py').read_bytes();tree=ast.parse(source)
    main_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    starts=[i for i,n in enumerate(main_node.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='target' for t in n.targets)]
    if len(starts)!=1:raise ValueError('frozen finalization seam changed')
    namespace={'__name__':'e47_partial_deploy','__file__':str(VENDOR/'deploy_service.py')}
    exec(compile(tree,str(VENDOR/'deploy_service.py'),'exec'),namespace)
    service_dir=namespace['SERVICE_DIR'];service=observed['service'];tunnel=observed['tunnel']
    if service['cwd']!=str(service_dir) or service['argv'][-5:]!=['main:app','--host','127.0.0.1','--port',str(port)]:raise ValueError('partial service identity differs')
    if not any(Path(a).name=='uvicorn' for a in service['argv'][:2]):raise ValueError('partial service executable differs')
    if tunnel['cwd']!=str(ROOT.parents[2]) or len(tunnel['argv'])!=5 or Path(tunnel['argv'][0]).name!='cloudflared' or tunnel['argv'][1:]!=['tunnel','--no-autoupdate','--url',f'http://127.0.0.1:{port}']:raise ValueError('partial tunnel identity differs')
    wanted={'VB_TASK_PACK':str(private/'packs'/model),'VB_SERVICE_KEY_FILE':str(private/'service_bearer'),'VB_COLLECT_ONLY':'1','VB_NO_COMPILER':'1'}
    env={}
    for entry in (Path('/proc')/str(service['pid'])/'environ').read_bytes().split(b'\0'):
        k,_,v=entry.partition(b'=');name=k.decode(errors='replace')
        if name in {*wanted,'VB_BASE_IMAGE'}:env[name]=v.decode()
    if {k:env.get(k) for k in wanted}!=wanted:raise ValueError('partial service environment differs')
    if model.startswith('t2_') and env.get('VB_BASE_IMAGE')!=BASE_IMAGE:raise ValueError('partial agent base image differs')
    urls=set(re.findall(r'https://[a-z0-9-]+\.trycloudflare\.com',(private/f'tunnel_{model}.log').read_text()))
    if len(urls)!=1:raise ValueError('original tunnel URL is ambiguous')
    url=urls.pop();bearer=(private/'service_bearer').read_text().strip()
    codes=[health(endpoint+'/health',auth) for endpoint in (f'http://127.0.0.1:{port}',url) for auth in (bearer,None)]
    if codes!=[200,401,200,401]:raise RuntimeError('partial deployment is not currently healthy')
    if any(process(observed[k]['pid'])!=observed[k] for k in observed):raise ValueError('process changed during checks')
    benchmark='certjudge47-v5-a1-probes-'+model.replace('_','-')
    import yaml
    config=yaml.safe_load((private/'valkyrie.yaml').read_text());existing=config.get('custom_benchmark_services',{}).get(benchmark)
    if existing is not None and existing!=url:raise ValueError('existing namespace has another URL')
    namespace.update(args=types.SimpleNamespace(model=model),benchmark=benchmark,port=port,pack=private/'packs'/model,
                     receipt_path=receipt_path,service=types.SimpleNamespace(pid=service['pid']),tunnel=types.SimpleNamespace(pid=tunnel['pid']),url=url,bearer=bearer,unauth=401,env=env)
    body=ast.FunctionDef(name='finish_original_deployment',args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=main_node.body[starts[0]:],decorator_list=[])
    exec(compile(ast.fix_missing_locations(ast.Module(body=[body],type_ignores=[])),'<frozen-deployment-finalization>','exec'),namespace)
    namespace['finish_original_deployment']()
    write(ROOT/'runtime'/f'probe_deployment_recovery_{model}.json',{'run_id':RUN_ID,'epoch':time.time(),'model':model,'state':'ORIGINAL_LIVE_PROCESSES_ADOPTED','frozen_source_sha256':sha(source),'process_evidence_sha256':sha(args.evidence.read_bytes()),'processes':observed,'health_codes':codes,'original_timeout_log_sha256':sha((ROOT/'runtime/prepare_probes_2.log').read_bytes()),'deployment_receipt_sha256':sha(receipt_path.read_bytes()),'new_processes':0,'new_urls':0,'new_inference_calls':0})

if __name__=='__main__':main()
