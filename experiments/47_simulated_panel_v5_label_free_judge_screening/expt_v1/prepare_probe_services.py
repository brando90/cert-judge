"""Finish deterministic probe preparation and bind callback health; zero inference.

Run once under run_offline.py after starting the owned renderer. Every subprocess
failure stops this continuation. Existing deployment receipts are checked rather
than redeployed, and an existing callback binding is never replaced.
"""
from pathlib import Path
import subprocess
import sys
import time
from e47_adapter import ROOT, REPO, RESULTS, PRIVATE, RUN_ID, read, write, sha, verify_dependencies
from run_offline import identity
from callback_watch import MODELS
from callback_gate import require_callback_ready


def main():
    runtime=ROOT/'runtime';out=RESULTS/'probes';admission=out/'admission_manifest.json'
    def note(stage,**extra):
        write(runtime/'probe_preparation_stage.json',{'run_id':RUN_ID,'phase':'probes','stage':stage,
              'observed_epoch':time.time(),'inference_calls':0,'whole_experiment_complete':False,**extra})
    def run(script,*args,cwd=ROOT):
        subprocess.run([sys.executable,str(ROOT/script),*map(str,args)],cwd=cwd,check=True)
    integration=read(RESULTS/'probe_integration.json')
    if integration.get('run_id')!=RUN_ID or integration.get('state')!='VERIFIED':raise ValueError('probe integration is not verified')
    for name,digest in integration['hashes'].items():
        if sha((ROOT/'probes'/name).read_bytes())!=digest:raise ValueError('integrated probe evidence changed')
    verify_dependencies()
    settling_since=None
    while True:
        producer=read(runtime/'render_probes.json')
        if producer.get('run_id')!=RUN_ID or producer.get('kind')!='deterministic_offline' or producer.get('command')!=['python3','render_campaign.py','--phase','probes','--probe-manifest','probes/probe_manifest.json','--probe-root','.','--freeze']:
            raise ValueError('renderer dependency identity differs')
        if producer.get('state')=='FINISHED' and producer.get('exit_code')==0:break
        if producer.get('state')!='RUNNING':raise RuntimeError('renderer did not finish successfully')
        for key in ('driver','child'):
            expected=producer[key]
            current=identity(expected['pid'])
            p=Path('/proc')/str(expected['pid'])
            exited=current is None or (p/'stat').read_text().rsplit(')',1)[1].split()[0] in ('Z','X')
            if exited and key=='child':
                # run_offline publishes exit status on its 30-second tick.
                settling_since=time.monotonic() if settling_since is None else settling_since
                if time.monotonic()-settling_since>45:raise RuntimeError('renderer exit status not published')
                continue
            if current!=expected:raise RuntimeError('owned renderer stopped without completion')
            if exited:raise RuntimeError('renderer wrapper exited')
            cwd=(p/'cwd').resolve()
            allowed={ROOT} if key=='child' else {ROOT,REPO}
            argv=(p/'cmdline').read_bytes().split(b'\0')
            script='render_campaign.py' if key=='child' else 'run_offline.py'
            if cwd not in allowed or len(argv)<2 or (cwd/argv[1].decode()).resolve()!=ROOT/script:
                raise ValueError('renderer dependency cwd/argv differs')
        note('WAITING_FOR_OWNED_RENDERER');time.sleep(10)
    if read(admission).get('state')!='FROZEN':raise ValueError('probe admission not frozen')
    note('PACKING_FULL_DECLARED_PROBE_UNIVERSE');run('render_campaign.py','--packs','--phase','probes')
    note('EXACT_COUNT_QUOTE');run('quote_campaign.py','--phase','probes')
    for model in MODELS:
        note('DEPLOYMENT',model=model)
        if not (PRIVATE/'probes'/('deployment_'+model+'.json')).exists():
            run('deploy_e47.py','--phase','probes','--model',model,cwd=REPO)
        proc=subprocess.run([sys.executable,str(ROOT/'deploy_e47.py'),'--phase','probes','--model',model,'--status'],cwd=REPO,capture_output=True,text=True,check=True)
        import json
        status=json.loads(proc.stdout)
        if not all(status.get(k) is True for k in ('service_alive','tunnel_alive')) or any(status.get(k)!=200 for k in ('local_health_now','tunnel_health_now')):
            raise RuntimeError('current deployment health failed '+model)
        write(runtime/('probe_deployment_status_'+model+'.json'),status)
    note('VERIFYING_COMPLETE_TASK_SLICES');run('verify_task_slices.py','--phase','probes')
    note('BINDING_PASSIVE_CALLBACK_OBSERVER')
    if not (runtime/'callback_binding.json').exists():
        run('callback_watch.py','--experiment',ROOT,'--bind','--admission',admission)
    # The already installed minute cron must provide a distinct useful action.
    # A bind receipt alone is never unattended-readiness evidence.
    deadline=time.monotonic()+180
    while True:
        observation=read(runtime/'callback_observation.json')
        if observation.get('observation_kind')=='monitor':
            gate=require_callback_ready(ROOT,sha(admission.read_bytes()));break
        if time.monotonic()>deadline:raise RuntimeError('scheduled callback observation not received')
        note('WAITING_FOR_SCHEDULED_CALLBACK_OBSERVATION');time.sleep(5)
    write(runtime/'probe_pre_admission_pass.json',{**gate,'task_selection_transport_sha256':sha((out/'task_selection_transport.json').read_bytes()),'packs_sha256':sha((out/'packs.json').read_bytes()),'quote_sha256':sha((out/'QUOTE.json').read_bytes())})
    note('READY_FOR_REVIEW_AND_ADMISSION',new_calls=read(out/'QUOTE.json')['new_calls'])

if __name__=='__main__':main()
