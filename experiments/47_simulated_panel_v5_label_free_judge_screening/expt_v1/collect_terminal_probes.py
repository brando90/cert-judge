"""Preserve terminal probe archives while other original runs remain active.

Read-only collection; no admission, inference, retry loop or score publication.
Run under run_offline.py for durable process ownership and heartbeat records.
"""
import time
from e47_adapter import ROOT, RESULTS, RUN_ID, read, write, verify_dependencies, phase_context
from campaign_driver import require_existing_runs
from collect_probe_artifacts import collect


def main():
    verify_dependencies();_,_,_,ctl=phase_context('probes')
    expected=require_existing_runs(ctl)
    admitted=read(RESULTS/'probes/admission_receipt.json')
    if admitted['scientific_run_id']!=RUN_ID or expected!={r['config']:r['run_id'] for r in admitted['configurations']}:
        raise ValueError('original admitted run identities differ')
    complete={};path=ROOT/'runtime/terminal_probe_collection_progress.json'
    while True:
        if require_existing_runs(ctl)!=expected:raise ValueError('original run identity changed during collection')
        for key,entry in ctl.load_state()['runs'].items():
            if entry['config'] in complete or entry['phase']!='terminal':continue
            directory,indexed,certificate=collect(ctl,key)
            complete[entry['config']]=certificate
            write(path,{'run_id':RUN_ID,'state':'COLLECTING_OR_WAITING_FOR_TERMINAL_RUNS','collected':complete,'epoch':time.time(),'new_inference_calls':0})
        state='ALL_ORIGINAL_ARCHIVES_COLLECTED' if len(complete)==len(expected) else 'COLLECTING_OR_WAITING_FOR_TERMINAL_RUNS'
        write(path,{'run_id':RUN_ID,'state':state,'collected':complete,'epoch':time.time(),'new_inference_calls':0})
        if len(complete)==len(expected):return
        time.sleep(30)


if __name__=='__main__':main()
