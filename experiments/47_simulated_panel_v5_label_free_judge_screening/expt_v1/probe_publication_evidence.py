"""Reverify every original probe archive offline before final publication."""
from collections import Counter
from unittest.mock import patch
from e47_adapter import ROOT,RESULTS,RUN_ID,POOL,read,write,sha,phase_context
from collect_probe_artifacts import collect
from harvest_probe_artifacts import verify
from harvest_original_artifacts import offline_only

PUBLIC_REASONS = frozenset((
    'equal_delivered_prompt_hash',
    'delivered_hash_unavailable; exact served instruction hash and frozen pack round-trip',
    'parse_error', 'MISSING_RESPONSE_BYTES', 'ARTIFACT_ABSENT_UNRESOLVED',
    'SUBMITTED_VERDICT_BYTES_UNCERTIFIED', 'UNCLEAN_TRANSPORT_STATUS',
))

def public_reason_counts(cells):
    """Publish fixed categories, never parser exception text or response payloads.

    Full original reasons remain in the hash-bound private strict harvest.
    Unknown reasons are counted without guessing their cause.
    """
    counts=Counter()
    for cell in cells:
        reason=cell.get('acceptance_reason')
        if isinstance(reason,str) and reason in PUBLIC_REASONS:category=reason
        elif isinstance(reason,str) and (reason.startswith('Invalid TC judge response:')
                or reason == "no valid integer 0-5 'final_score_0_5' in response"):
            category='FROZEN_PARSER_INVALID_RESPONSE'
        else:category='UNCLASSIFIED_PRIVATE_REASON'
        counts[category]+=1
    return dict(counts)

def verify_all():
    _,_,_,ctl=phase_context('probes');rows=[]
    for config in POOL:
        name=(config+'@main').replace('|','__').replace('@','_')
        if not (ctl.RAW/(name+'_probe_collection.json')).exists():raise ValueError('original probe collection incomplete: '+config)
    with patch.object(ctl,'cli',offline_only):
        for config in POOL:
            key=config+'@main';name=key.replace('|','__').replace('@','_')
            directory,indexed,certificate=collect(ctl,key)
            fresh=verify(ctl,config,key,directory,indexed,certificate)
            stored=ctl.JUDGE/'strict_harvests'/(config.replace('|','__')+'__main.json')
            if read(stored)!=fresh:raise ValueError('strict probe result changed: '+config)
            row={k:fresh[k] for k in ('run_id','config','n_cells','accepted_count','status_counts','charges_usd','server_run_status','server_task_state_counts','server_final_view_sha256','dependencies_verified')}
            row.update(strict_harvest_sha256=sha(stored.read_bytes()),collection_certificate_sha256=sha((ctl.RAW/(name+'_probe_collection.json')).read_bytes()),collection=certificate,
                       unknown_cost_cells=sum(c.get('cost_usd') is None for c in fresh['cells']),
                       acceptance_reasons=public_reason_counts(fresh['cells']),
                       http_status_counts=dict(Counter(str(c.get('http_status','unreported')) for c in fresh['cells'])))
            rows.append(row)
    evidence={'run_id':RUN_ID,'phase':'probes','state':'ALL_ORIGINAL_PROBE_ARCHIVES_REVERIFIED_OFFLINE','runs':rows,
              'expected_task_occurrences':sum(r['n_cells'] for r in rows),'accepted_task_occurrences':sum(r['accepted_count'] for r in rows),
              'verified_files':sum(r['collection']['files'] for r in rows),'verified_bytes':sum(r['collection']['bytes'] for r in rows),
              'known_reported_sum_usd':sum(r['charges_usd'] for r in rows),'unknown_cost_cells':sum(r['unknown_cost_cells'] for r in rows),
              'source_hashes':{name:sha((ROOT/name).read_bytes()) for name in ('probe_publication_evidence.py','harvest_probe_artifacts.py','harvest_original_artifacts.py','collect_probe_artifacts.py','receipt_validation.py','artifact_paths.py')},
              'transport_commands':0,'new_inference_calls':0,'whole_experiment_complete':False}
    path=RESULTS/'probes/original_artifact_reconciliation.json';write(path,evidence)
    return evidence,path
