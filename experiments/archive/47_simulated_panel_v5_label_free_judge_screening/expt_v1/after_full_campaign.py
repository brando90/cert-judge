"""Follow already admitted scoring through full analysis and report verification.

Run under run_offline.py only after the complete probe admission is frozen.
This ordinary-code continuation never admits, retries, publishes or marks the
whole experiment complete. Publication remains a separately verified action.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import time
from e47_adapter import ROOT,RESULTS,RUN_ID,read,write,sha
from run_offline import identity
from analysis_provenance import capture_inputs,verify_full_receipt,verify_criterion_receipt,StaleCriterionProvenance


def criterion_ready():
    """Wait only for absence/staleness while the exact owned producer lives."""
    provenance=RESULTS/'criterion_analysis_provenance.json'
    if provenance.exists():
        try:
            verify_criterion_receipt()
            return True
        except StaleCriterionProvenance:
            pass
    state=read(ROOT/'runtime/criterion_followthrough.json')
    command=state.get('command',[])
    if (state.get('run_id')!=RUN_ID or state.get('kind')!='deterministic_offline'
            or state.get('state')!='RUNNING' or len(command)!=2
            or (ROOT/command[1]).resolve()!=(ROOT/'after_criterion.py').resolve()):
        raise ValueError('criterion dependency ownership/command differs')
    for field in ('driver','child'):
        process=state.get(field,{})
        if not process.get('pid') or identity(process['pid'])!=process:
            raise RuntimeError('criterion report dependency needs explicit recovery')
        if Path(f"/proc/{process['pid']}/stat").read_text().rsplit(')',1)[1].split()[0]=='Z':
            raise RuntimeError('criterion report dependency needs explicit recovery; producer exited')
        if Path(f"/proc/{process['pid']}/cwd").resolve()!=ROOT.resolve():
            raise ValueError('criterion dependency working directory differs')
        argv=Path(f"/proc/{process['pid']}/cmdline").read_bytes().split(b'\0')
        expected='run_offline.py' if field=='driver' else 'after_criterion.py'
        if len(argv)<2 or (ROOT/argv[1].decode()).resolve()!=(ROOT/expected).resolve():
            raise ValueError('criterion dependency process command differs')
    return False


def phase_ready(phase,digest):
    marker=ROOT/'runtime'/f'judge_{phase}_RECONCILED.json'
    if marker.exists():
        r=read(marker)
        if (r.get('run_id'),r.get('phase'),r.get('state'),r.get('admission_manifest_sha256'))!=(RUN_ID,phase,'RECONCILED',digest):raise ValueError('unbound scoring reconciliation '+phase)
        return True
    path=ROOT/'runtime'/f'judge_{phase}.json'
    if not path.exists():raise RuntimeError('start the owned scoring driver before its full continuation: '+phase)
    r=read(path)
    if (r.get('run_id'),r.get('phase'),r.get('admission_manifest_sha256'))!=(RUN_ID,phase,digest):raise ValueError('scoring driver identity differs '+phase)
    if identity(r['driver']['pid'])!=r['driver']:raise RuntimeError('scoring driver needs explicit adoption; continuation never retries '+phase)
    return False


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--probe-manifest',type=Path,required=True);args=ap.parse_args();manifest=args.probe_manifest.resolve()
    admissions={p:read(RESULTS/p/'admission_manifest.json') for p in ('criterion','probes')}
    if any(a.get('run_id')!=RUN_ID or a.get('phase')!=p or a.get('state')!='FROZEN' for p,a in admissions.items()):raise ValueError('both current admissions must be frozen')
    if sha(manifest.read_bytes())!=admissions['probes']['probe_manifest_sha256']:raise ValueError('wrong structural manifest')
    digests={p:sha((RESULTS/p/'admission_manifest.json').read_bytes()) for p in admissions}
    stage=ROOT/'runtime/full_followthrough_stage.json'
    def note(value,**extra):write(stage,{'run_id':RUN_ID,'stage':value,'epoch':time.time(),'admission_sha256':digests,'inference_calls':0,'whole_experiment_complete':False,**extra})
    while True:
        pending=[p for p,d in digests.items() if not phase_ready(p,d)]
        if not pending:break
        note('WAITING_FOR_EXISTING_SCORING_RUNS',pending=pending);time.sleep(30)
    capture_inputs('full',manifest);note('FULL_ANALYSIS')
    subprocess.run([sys.executable,'run_offline.py','--name','full_analysis','--',sys.executable,'analyze_campaign.py','--probe-manifest',str(manifest)],cwd=ROOT,check=True)
    verify_full_receipt(manifest)
    while not criterion_ready():
        note('WAITING_FOR_EXISTING_CRITERION_ANALYSIS');time.sleep(30)
    verify_criterion_receipt();note('FULL_REPORT')
    subprocess.run([sys.executable,'report_campaign.py','--probe-manifest',str(manifest)],cwd=ROOT,check=True)
    report=read(RESULTS/'campaign_report_receipt.json')
    if report.get('run_id')!=RUN_ID or report.get('scope')!='full_scientific_report':raise ValueError('full report receipt differs')
    note('FULL_ANALYSIS_AND_REPORT_READY_FOR_PUBLICATION')
    write(ROOT/'runtime/FULL_ANALYSIS_READY_FOR_PUBLICATION.json',{'run_id':RUN_ID,'state':'READY_FOR_PUBLICATION','admission_sha256':digests,'report_receipt_sha256':sha((RESULTS/'campaign_report_receipt.json').read_bytes()),'whole_experiment_complete':False})

if __name__=='__main__':main()
