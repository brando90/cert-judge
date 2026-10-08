#!/usr/bin/env python3
"""Read-only inventory. Reuses the audited parser; emits no held-out outcome values."""
import argparse
import collections
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EXP.parents if (p / 'pyproject.toml').exists())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load_module(p):
    spec = importlib.util.spec_from_file_location('audited_labels', p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def build(vb):
    e75 = vb / 'experiments/75_J1_validating_formal_spec_judge_train_val_test'
    e100 = vb / 'experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test'
    parser_path = e75 / 'scripts/audit_human_judgment_data.py'
    parser = load_module(parser_path)
    human = vb / 'veribench_dataset/human_labels'
    split_path = e75 / 'results/splits.json'
    split = json.loads(split_path.read_text())
    assignment = {t:s for s in ('train','val','test') for t in split[s+'_tasks']}
    assert len(assignment) == 25 and sum(len(split[s+'_tasks']) for s in ('train','val','test')) == 25
    rows = {n:parser.read_rows(human/n) for n in parser.PARTICIPANTS+parser.OLD+parser.AGGREGATES}
    keys = {r['candidate'] for r in rows[parser.PARTICIPANTS[0]]}
    for n in parser.PARTICIPANTS+parser.OLD:
        assert len(rows[n]) == len(keys) == 75
        assert {r['candidate'] for r in rows[n]} == keys
    assert parser.pairs(rows[parser.AGGREGATES[0]]) == sum((parser.pairs(rows[n]) for n in parser.PARTICIPANTS[:3]), [])
    expected = parser.pairs(rows[parser.OLD[0]]) + [r for r in parser.pairs(rows[parser.OLD[1]]) if not r[0].startswith('1_unsafeMultiply_safe__')] + parser.pairs(rows[parser.PARTICIPANTS[3]]) + parser.pairs(rows[parser.PARTICIPANTS[4]])
    assert parser.pairs(rows[parser.AGGREGATES[1]]) == expected
    task = lambda c: c.rsplit('__agent',1)[0]
    files = {n:{'sha256':sha(human/n),'rows':len(rs),'usable':sum(r['score'] is not None for r in rs),'missing':sum(r['score'] is None for r in rs),'embedded_score_repairs':[{'line':r['line'],'candidate':r['candidate']} for r in rs if r['embedded_score'] is not None]} for n,rs in rows.items()}
    item_rows=[]
    for c in sorted(keys):
        t=task(c); current=[next(r for r in rows[n] if r['candidate']==c) for n in parser.PARTICIPANTS]
        item_rows.append({'item':c.removesuffix('.lean'),'candidate':c,'task':t,'split':assignment[t],'domain':split['tasks'][t]['stratum'],'current_raters_present':[i+1 for i,r in enumerate(current) if r['score'] is not None],'historical_auxiliary_eligible':assignment[t]=='train'})
    counts={s:{'tasks':len(split[s+'_tasks']),'items':sum(r['split']==s for r in item_rows),'current5_observations':sum(len(r['current_raters_present']) for r in item_rows if r['split']==s),'current3_observations':sum(sum(i<=3 for i in r['current_raters_present']) for r in item_rows if r['split']==s),'historical_auxiliary_observations':60 if s=='train' else 0,'historical_excluded_observations':0 if s=='train' else (30 if s=='val' else 60)} for s in ('train','val','test')}
    manifest=json.loads((e100/'inputs/MANIFEST.json').read_text())
    checked=[]
    for name,digest in manifest['files'].items():
        p=e100/name
        assert p.exists() and sha(p)==digest, name
        checked.append({'path':str(p.relative_to(vb)),'sha256':digest})
    assert sha(split_path)==manifest['sources']['splits_sha256']
    items=[json.loads(s) for s in (e100/'inputs/items.jsonl').read_text().splitlines()]
    assert len(items)==75 and len({x['item'] for x in items})==75
    for x in items:
        assert x['split']==assignment[x['task']]
    generation=json.loads((human/'calibration/generated_agents/generation_manifest.json').read_text())
    selected=[x for x in generation if Path(x['output_path']).name in keys]
    assert len(selected)==75
    generation_counts=collections.Counter(x.get('model','unrecorded') for x in selected)
    for c in keys:
        agent='agent'+c.rsplit('__agent',1)[1].split('.')[0]
        assert sha(human/'calibration/generated_agents'/agent/c)==sha(e100/'inputs/candidates'/c)
    # Pin import snapshots; these are not annotation-session receipts.
    history=[]
    ann=manifest['sources']['annotation_rev']; snap=manifest['sources']['snapshot_rev']
    for x in sorted({x['task']:x for x in items}.values(),key=lambda x:x['task']):
        t=x['task']; a=e100/'inputs/references/annotation'/f'{t}.lean'; b=e100/'inputs/references/snapshot'/f'{t}.lean'
        history.append({'task':t,'split':assignment[t],'annotation_reconstruction_sha256':sha(a),'snapshot_sha256':sha(b),'same_bytes':a.read_bytes()==b.read_bytes(),'ref_status':x['ref_status'],'placeholder':x['ref_placeholder_at_annotation'],'ambiguous_in_window':x['ref_ambiguous_in_window'],'annotation_session_provenance':'unavailable'})
    caches=[]
    for prefix in ('39_','42_','43_'):
        e=next((ROOT/'experiments').glob(prefix+'*'))
        paths=list((e/'results/harvest').glob('*.json')) if prefix!='43_' else [e/'results/full/cells.json']
        caches.append({'experiment':e.name,'files':len(paths),'bytes':sum(p.stat().st_size for p in paths),'sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}})
    report={'schema_version':1,'source_revision':subprocess.check_output(['git','-C',str(vb),'rev-parse','HEAD'],text=True).strip(),'parser':{'path':str(parser_path),'sha256':sha(parser_path)},'source_files':files,'split_sha256':sha(split_path),'split_assignments':{s:split[s+'_tasks'] for s in ('train','val','test')},'counts':counts,'current5_total':sum(v['current5_observations'] for v in counts.values()),'current3_total':sum(v['current3_observations'] for v in counts.values()),'pool_items':75,'task_groups':25,'compiled_files_are_duplicates':True,'generation_model_counts':dict(generation_counts),'generation_unrecorded_candidates':[Path(x['output_path']).name for x in selected if not x.get('model')],'candidate_byte_matches':75,'verified_manifest_files':len(checked),'annotation_reconstruction_revision':ann,'later_snapshot_revision':snap,'reference_summary':dict(collections.Counter(x['ref_status'] for x in history)),'historical_policy':'Only 60 old-pass observations on 30 training items may enter auxiliary fitting. No historical val/test scores enter main analysis or evaluation.','known_conflicts':['Repository instruction 343 labels / 78 pairs is obsolete: audited current files have 345 usable / 75 items.','Prior reports call reconstructed reference bytes rater-seen; there is no per-rating snapshot receipt.','Seven rating files are five current identifiers plus two old passes, not seven people.'],'cache_inventory':caches}
    out=EXP/'results';out.mkdir(exist_ok=True)
    for name,obj in [('inventory.json',report),('coverage_by_item.json',item_rows),('reference_provenance.json',history),('input_files.json',checked)]:
        (out/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--veribench',type=Path,default=Path.home()/'veribench');a=p.parse_args();r=build(a.veribench)
    print(json.dumps({k:r[k] for k in ('counts','current5_total','current3_total','candidate_byte_matches','verified_manifest_files','reference_summary')},indent=2))
