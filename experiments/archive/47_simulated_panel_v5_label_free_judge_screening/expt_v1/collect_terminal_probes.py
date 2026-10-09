"""Preserve terminal probe archives while other original runs remain active.

Read-only collection; no admission, inference, retry loop or score publication.
Run under run_offline.py for durable process ownership and heartbeat records.
"""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from e47_adapter import ROOT, RESULTS, RUN_ID, read, write, verify_dependencies, phase_context
from campaign_driver import require_existing_runs
from collect_probe_artifacts import collect


def collect_wave(ctl, entries, record, workers=3):
    """At most three distinct original downloads; drain healthy peers on error.

    No new wave begins after any failure. Per-run intent/locks in collect() also
    fence concurrent final harvesting and any later invocation of this worker.
    """
    if len(entries)>workers:raise ValueError('collection wave exceeds worker bound')
    failures=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending={pool.submit(collect,ctl,key):entry['config'] for key,entry in entries}
        for future in as_completed(pending):
            try:
                _,_,certificate=future.result();record(pending[future],certificate)
            except Exception as error:failures.append(error)
    if failures:raise failures[0]


def main():
    verify_dependencies();_,_,_,ctl=phase_context('probes')
    expected=require_existing_runs(ctl)
    admitted=read(RESULTS/'probes/admission_receipt.json')
    if admitted['scientific_run_id']!=RUN_ID or expected!={r['config']:r['run_id'] for r in admitted['configurations']}:
        raise ValueError('original admitted run identities differ')
    complete={};path=ROOT/'runtime/terminal_probe_collection_progress.json'
    def record(config,certificate):
        complete[config]=certificate
        write(path,{'run_id':RUN_ID,'state':'COLLECTING_OR_WAITING_FOR_TERMINAL_RUNS','collected':complete,'epoch':time.time(),'new_inference_calls':0,'collection_workers':3})
    while True:
        if require_existing_runs(ctl)!=expected:raise ValueError('original run identity changed during collection')
        ready=[(key,entry) for key,entry in ctl.load_state()['runs'].items() if entry['config'] not in complete and entry['phase']=='terminal']
        # Adopt all completed certificates before starting another download wave.
        ready.sort(key=lambda pair:not (ctl.RAW/(pair[0].replace('|','__').replace('@','_')+'_probe_collection.json')).exists())
        collect_wave(ctl,ready[:3],record)
        state='ALL_ORIGINAL_ARCHIVES_COLLECTED' if len(complete)==len(expected) else 'COLLECTING_OR_WAITING_FOR_TERMINAL_RUNS'
        write(path,{'run_id':RUN_ID,'state':state,'collected':complete,'epoch':time.time(),'new_inference_calls':0})
        if len(complete)==len(expected):return
        time.sleep(30)


if __name__=='__main__':main()
