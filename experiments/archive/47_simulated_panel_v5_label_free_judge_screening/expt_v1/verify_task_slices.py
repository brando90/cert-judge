"""Verify exact complete task selection through read-only benchmark endpoints."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import time
import urllib.parse
import urllib.request
from e47_adapter import ROOT,RESULTS,PRIVATE,phase_context,read,write,sha,RUN_ID,POOL


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['criterion','probes'],required=True);args=parser.parse_args();phase=args.phase
    _,_,_,ctl=phase_context(phase);private=PRIVATE/phase;results=RESULTS/phase
    token=(private/'service_bearer').read_text().strip()
    def verify(model):
        deployment=read(private/f'deployment_{model}.json')
        def query(params):
            url=deployment['tunnel_url']+'/verify-task-ids?'+urllib.parse.urlencode(params)
            with urllib.request.urlopen(urllib.request.Request(url,headers={'Authorization':'Bearer '+token}),timeout=60) as response:return json.loads(response.read())['task_ids']
        all_ids=query({'dataset':'default'})
        if len(set(all_ids))!=len(all_ids):raise ValueError('duplicate served task IDs')
        positions={task:i for i,task in enumerate(all_ids)};output={}
        expected={r['task_id'] for cfg in POOL if cfg.split('|')[0]==model for part in ('main','smoke') for r in ctl.pack_rows(cfg,part)}
        if set(all_ids)!=expected:raise ValueError('served task universe differs from frozen packs '+model)
        for cfg in POOL:
            if cfg.split('|')[0]!=model:continue
            desired=[r['task_id'] for r in ctl.pack_rows(cfg,'main')]
            if not desired:continue
            indices=sorted(positions[i] for i in desired)
            if indices!=list(range(indices[0],indices[-1]+1)):raise ValueError('task block is not contiguous '+cfg)
            value=f'{indices[0]}:{indices[-1]+1}';returned=query({'dataset':'default','slice':value})
            if set(returned)!=set(desired) or len(returned)!=len(desired):raise ValueError('slice differs from exact declared task IDs '+cfg)
            output[cfg]={'slice':value,'expected_cells':len(desired),'task_ids_sha256':sha(('\n'.join(sorted(desired))+'\n').encode()),'remote_verified_equal':True,'benchmark':deployment['benchmark']}
        return output
    blocks=list(ThreadPoolExecutor(4).map(verify,['opus55x','qwen36','t2_qwen','t2_sonnet5']));configs={k:v for b in blocks for k,v in b.items()}
    binding={'run_id':RUN_ID,'phase':phase,'state':'FROZEN','configurations':configs,'admission_manifest_sha256':sha((results/'admission_manifest.json').read_bytes()),'packs_sha256':sha((results/'packs.json').read_bytes())}
    path=results/'task_selection_transport.json'
    if path.exists():
        existing=read(path)
        if any(existing.get(k)!=v for k,v in binding.items()):raise ValueError('existing frozen selection transport differs; preserve it and resolve explicitly')
    else:
        write(path,{**binding,'recorded_epoch':time.time(),'condition':'compact dataset slices select exactly every declared task; avoids observed long-query transport limit',
                    'suffixes':{},'new_scientific_cells':0,'no_repeated_verdicts':True})
    write(ROOT/'runtime'/f'{phase}_slice_reverification.json',{'run_id':RUN_ID,'epoch':time.time(),'selection_transport_sha256':sha(path.read_bytes()),'configurations_verified':len(configs),'total_main_tasks':sum(v['expected_cells'] for v in configs.values()),'inference_calls':0})
    print({k:(v['slice'],v['expected_cells']) for k,v in configs.items()})

if __name__=='__main__':main()
