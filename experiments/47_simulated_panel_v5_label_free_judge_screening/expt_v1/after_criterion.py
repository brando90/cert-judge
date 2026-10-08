"""Durably run independent analyses immediately after verified reconciliation.

No admission or retry path exists here. Run under run_offline.py for a heartbeat.
"""
import subprocess
import sys
import time
from e47_adapter import ROOT,RESULTS,RUN_ID,read,sha,write
from run_offline import identity

def main():
    runtime=ROOT/'runtime';digest=sha((RESULTS/'criterion/admission_manifest.json').read_bytes())
    while True:
        path=runtime/'judge_criterion_RECONCILED.json'
        if path.exists():
            receipt=read(path)
            if receipt.get('run_id')!=RUN_ID or receipt.get('phase')!='criterion' or receipt.get('state')!='RECONCILED' or receipt.get('admission_manifest_sha256')!=digest:raise ValueError('unbound criterion reconciliation marker')
            break
        driver=read(runtime/'judge_criterion.json')
        if driver.get('run_id')!=RUN_ID or driver.get('admission_manifest_sha256')!=digest:raise ValueError('criterion driver identity differs')
        if driver.get('state')=='DRIVER_ERROR' and identity(driver['driver']['pid'])!=driver['driver']:raise RuntimeError('criterion driver needs explicit recovery; this continuation never admits or retries')
        write(runtime/'criterion_followthrough_stage.json',{'run_id':RUN_ID,'stage':'WAITING_FOR_EXISTING_CRITERION_RUNS','epoch':time.time(),'admission_manifest_sha256':digest,'inference_calls':0})
        time.sleep(30)
    write(runtime/'criterion_followthrough_stage.json',{'run_id':RUN_ID,'stage':'ANALYSIS','epoch':time.time(),'inference_calls':0})
    subprocess.run([sys.executable,'run_offline.py','--name','criterion_only_analysis','--',sys.executable,'analyze_criterion_only.py'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'report_campaign.py','--criterion-only'],cwd=ROOT,check=True)
    write(runtime/'criterion_followthrough_stage.json',{'run_id':RUN_ID,'stage':'CRITERION_ANALYSIS_AND_REPORT_FINISHED','epoch':time.time(),'whole_experiment_complete':False})

if __name__=='__main__':main()
