"""Process-bound ordinary-code watchdog; one driver adoption per dead incident."""
import argparse
import fcntl
import os
from pathlib import Path
import shlex
import subprocess
import time
from e47_adapter import ROOT,RUN_ID,read,write
from run_offline import identity

def classify(receipt,current,done):
    if done:return 'RECONCILED'
    if not receipt:return 'AWAITING_DRIVER_RECEIPT'
    expected=receipt.get('driver')
    if expected and current==expected:return 'DRIVER_ALIVE'
    return 'ADOPT_DEAD_DRIVER'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',required=True,choices=['criterion','probes']);args=ap.parse_args()
    rt=ROOT/'runtime';phase=args.phase;name='judge_'+phase;lock=(rt/(name+'_watch.lock')).open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    path=rt/(name+'_watch.json');state=read(path) if path.exists() else {'run_id':RUN_ID,'phase':phase,'adopted_incidents':[]}
    while True:
        p=rt/(name+'.json');receipt=read(p) if p.exists() else None
        driver=(receipt or {}).get('driver');current=identity(driver['pid']) if driver else None
        done=(rt/(name+'_RECONCILED.json')).exists();status=classify(receipt,current,done)
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
