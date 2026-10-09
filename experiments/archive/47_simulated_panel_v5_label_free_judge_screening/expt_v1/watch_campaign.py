"""Process-bound ordinary-code watchdog; at most one driver adoption per phase."""
import argparse
import fcntl
import os
from pathlib import Path
import shlex
import subprocess
import time
from e47_adapter import ROOT,RESULTS,RUN_ID,read,write,sha
from run_offline import identity

def classify(receipt,current,done):
    if done:return 'RECONCILED'
    if not receipt:return 'AWAITING_DRIVER_RECEIPT'
    expected=receipt.get('driver')
    if expected and current==expected:return 'DRIVER_ALIVE'
    return 'ADOPT_DEAD_DRIVER'

def driver_lock_held(path):
    with path.open('a') as handle:
        try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return True
        fcntl.flock(handle,fcntl.LOCK_UN);return False

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',required=True,choices=['criterion','probes']);args=ap.parse_args()
    rt=ROOT/'runtime';phase=args.phase;name='judge_'+phase;lock=(rt/(name+'_watch.lock')).open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    path=rt/(name+'_watch.json');state=read(path) if path.exists() else {'run_id':RUN_ID,'phase':phase,'adopted_incidents':[]}
    digest=sha((RESULTS/phase/'admission_manifest.json').read_bytes())
    if state.get('run_id')!=RUN_ID or state.get('phase')!=phase:raise ValueError('watch receipt identity mismatch')
    started=time.monotonic()
    while True:
        p=rt/(name+'.json');receipt=read(p) if p.exists() else None
        driver=(receipt or {}).get('driver');current=identity(driver['pid']) if driver else None
        if receipt and (receipt.get('run_id')!=RUN_ID or receipt.get('phase')!=phase or receipt.get('admission_manifest_sha256')!=digest):raise ValueError('driver receipt identity mismatch')
        marker=rt/(name+'_RECONCILED.json');completion=read(marker) if marker.exists() else None
        done=bool(completion and completion.get('run_id')==RUN_ID and completion.get('phase')==phase and completion.get('admission_manifest_sha256')==digest)
        if completion and not done:raise ValueError('reconciliation receipt identity mismatch')
        status=classify(receipt,current,done)
        if status=='ADOPT_DEAD_DRIVER' and (time.monotonic()-started<90 or driver_lock_held(rt/(name+'.lock'))):status='AWAITING_FRESH_DRIVER_RECEIPT'
        state.update(state=status,heartbeat_epoch=time.time(),watchdog=identity(os.getpid()))
        if status=='ADOPT_DEAD_DRIVER':
            incident=str(driver)
            if not state['adopted_incidents']:
                state['adopted_incidents'].append(incident);write(path,state)
                command='cd '+shlex.quote(str(ROOT))+' && exec python3 campaign_driver.py --phase '+phase+' >> '+shlex.quote(str(rt/(name+'.log')))+' 2>&1'
                proc=subprocess.run(['tmux','new-session','-d','-s','cj47-'+phase+'-adopt-'+str(int(time.time())),command],capture_output=True,text=True)
                state['last_adoption_returncode']=proc.returncode
            else:state['state']='RESUMPTION_REQUIRED_AFTER_BOUNDED_ADOPTION'
        write(path,state)
        if done:return
        time.sleep(60)

if __name__=='__main__':main()
