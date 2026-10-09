"""Run the frozen benchmark service in an owned E47 namespace; zero inference."""
import argparse
import socket
import sys
import types
from e47_adapter import ROOT,PRIVATE,RESULTS,VENDOR,phase_context,sha,write

BASE_IMAGE='python@sha256:1aaa65a85fda306ffb8b910824d4e93bdce61e212c7e87168123ea3073b41a1a'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['criterion','probes'],required=True);ap.add_argument('--model',required=True);ap.add_argument('--status',action='store_true');args=ap.parse_args()
    e,*_=phase_context(args.phase)
    source=(VENDOR/'deploy_service.py').read_text()
    old='benchmark = f"certjudge39-{args.model.replace(\'_\', \'-\')}"'
    new='benchmark = f"certjudge47-v5-a1-'+args.phase+'-{args.model.replace(\'_\', \'-\')}"'
    if source.count(old)!=1:raise ValueError('frozen deployment namespace seam changed')
    adapted=source.replace(old,new)
    mod=types.ModuleType('e47_frozen_deploy');mod.__file__=str(VENDOR/'deploy_service.py');sys.modules[mod.__name__]=mod
    exec(compile(adapted,mod.__file__,'exec'),mod.__dict__)
    mod.MODEL_KEYS=['opus55x','qwen36','t2_qwen','t2_sonnet5'];mod.BASE_PORT=9040+(4 if args.phase=='probes' else 0);mod.AGENT_BASE_IMAGE=BASE_IMAGE
    if not args.status:
        with socket.socket() as s:s.bind(('127.0.0.1',mod.port_of(args.model)))
    write(e.RESULTS/'deployment_adapter.json',{'frozen_source_sha256':sha(source.encode()),'adapted_source_sha256':sha(adapted.encode()),'only_source_replacement':{'old':old,'new':new},'base_port':mod.BASE_PORT,'base_image':BASE_IMAGE,'provider_client_changes':False})
    sys.argv=['deploy_service','--model',args.model]+(['--status'] if args.status else [])
    return mod.main()

if __name__=='__main__':raise SystemExit(main())
