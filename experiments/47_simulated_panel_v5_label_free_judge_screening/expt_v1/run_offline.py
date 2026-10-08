"""Durable ordinary-code heartbeat for deterministic commands; never retries."""
import argparse
import fcntl
import os
from pathlib import Path
import subprocess
import time
from e47_adapter import ROOT,RUN_ID,write,read

def identity(pid):
    try:return {'pid':pid,'start_ticks':Path(f'/proc/{pid}/stat').read_text().split()[21],'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
    except FileNotFoundError:return None

def update_job(name,job):
    rt=ROOT/'runtime'
    with (rt/'active_jobs.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        p=rt/'active_jobs.json';state=read(p) if p.exists() else {'run_id':RUN_ID,'jobs':[]}
        state['jobs']=[j for j in state.get('jobs',[]) if j.get('name')!=name]
        if job:state['jobs'].append({'name':name,**job})
        state['observed_epoch']=time.time();state.pop('observed_at',None)
        state['note']='Run-bound owned jobs; terminal jobs are removed. The isolated probe owner tracks its compiler separately.'
        write(p,state)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--name',required=True);ap.add_argument('command',nargs=argparse.REMAINDER);args=ap.parse_args()
    command=args.command[1:] if args.command[0]=='--' else args.command
    runtime=ROOT/'runtime';lock=(runtime/(args.name+'.lock')).open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    log=(runtime/(args.name+'.log')).open('ab',buffering=0)
    proc=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,cwd=ROOT)
    state={'run_id':RUN_ID,'kind':'deterministic_offline','driver':identity(os.getpid()),'child':identity(proc.pid),'command':command,'started_epoch':time.time(),'state':'RUNNING'}
    while proc.poll() is None:
        state['heartbeat_epoch']=time.time();write(runtime/(args.name+'.json'),state);update_job(args.name,state);time.sleep(30)
    state.update(state='FINISHED' if proc.returncode==0 else 'FAILED',exit_code=proc.returncode,heartbeat_epoch=time.time());write(runtime/(args.name+'.json'),state);update_job(args.name,None)
    return proc.returncode

if __name__=='__main__':raise SystemExit(main())
