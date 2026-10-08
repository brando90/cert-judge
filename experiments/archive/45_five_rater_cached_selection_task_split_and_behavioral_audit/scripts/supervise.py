#!/usr/bin/env python3
"""Ordinary-code job supervisor; one writer, heartbeat, bounded notification, no model client."""
import argparse,json,os,subprocess,time,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone

def now():return datetime.now(timezone.utc).isoformat()
def atomic(p,x):
    tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(x,indent=2)+'\n');tmp.replace(p)
def monitor(command,out,notify=True,interval=10):
    out.mkdir(parents=True,exist_ok=True)
    lock=out/'job.lock'
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    identity={'supervisor_pid':os.getpid(),'started_utc':now(),'command':command,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip() if Path('/proc/sys/kernel/random/boot_id').exists() else 'local-test','reboot_recovery':'not installed; /tmp and tmux do not survive reboot','notification_recipient':'brando.science@gmail.com'}
    try:
        with (out/'job.log').open('w') as log:
            p=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);identity['pid']=p.pid
            stat=Path(f'/proc/{p.pid}/stat');identity['process_start_ticks']=stat.read_text().split()[21] if stat.exists() else None
            atomic(out/'launch.json',identity)
            while p.poll() is None:
                atomic(out/'heartbeat.json',{**identity,'updated_utc':now(),'state':'RUNNING','log_bytes':(out/'job.log').stat().st_size});time.sleep(interval)
            code=p.returncode
        result={**identity,'finished_utc':now(),'exit_code':code,'state':'COMPUTATION_COMPLETE' if code==0 else 'FAILED','log_sha256':hashlib.sha256((out/'job.log').read_bytes()).hexdigest()}
        atomic(out/'completion.json',result)
        if notify:
            body=f"CertJudge five-rater deterministic recovery: {result['state']}, exit {code}.\nHost: {os.uname().nodename}\nRuntime: {out}\nPublication/interpretation remains with the local recovery owner; this is a computation receipt, not a main landing.\n"
            mail=subprocess.run(['/usr/bin/mail','-s',f"[cert-judge] cached recovery {result['state']}",'brando.science@gmail.com'],input=body,text=True,capture_output=True,timeout=30)
            atomic(out/'notification.json',{'time':now(),'exit_code':mail.returncode,'state':'ACCEPTED_BY_LOCAL_MAIL_COMMAND' if mail.returncode==0 else 'FAILED','delivery_to_inbox':'not independently verified','stderr':mail.stderr[:500]})
        return code
    finally:lock.unlink(missing_ok=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--no-notify',action='store_true');p.add_argument('--interval',type=float,default=10);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args();cmd=a.command[1:] if a.command and a.command[0]=='--' else a.command;sys.exit(monitor(cmd,a.out,not a.no_notify,a.interval))
