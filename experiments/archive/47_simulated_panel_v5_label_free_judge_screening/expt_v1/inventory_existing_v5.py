"""Inventory F/Z and each learned fold as a distinct evaluation procedure."""
from collections import defaultdict,Counter
import gzip
import statistics
import json
from e47_adapter import ROOT,PRIVATE,RESULTS,RUN_ID,read,write,sha,source_items
from receipt_validation import accepted,unique_repeats

def main():
    inputs=ROOT/'inputs/veribench_v5';main=read(inputs/'manifest.json');late=read(inputs/'late/manifest_G16_G17.json');learned=json.loads(gzip.decompress((inputs/'manifest_L.json.gz').read_bytes()))
    fixed=json.loads(gzip.decompress((inputs/'manifest_cells.json.gz').read_bytes()))
    allrows=fixed['F']+fixed['Z']+learned['cells']+late['cells']['F']+late['cells']['Z']+late['cells']['L']
    fresh={r['item']:r for r in source_items()};declared={r['cell']:r for r in allrows if r['item'] in fresh}
    if len(declared)!=sum(r['item'] in fresh for r in allrows):raise ValueError('duplicate declared judge cell')
    receipts={};hashes={}
    for arm,members in [('F',['H2_opus55_max','H2_sol_high']),('Z',['H0_opus55_max','H0_sol_high']),('L_persona',['H2_opus55_max','H2_sol_high']),('L_c0',['H2_opus55_max','H2_sol_high'])]:
        for member in members:
            for prefix in ('','LATE_'):
                run=prefix+arm+'_'+member;path=PRIVATE/'raw_v5_cells'/run/'cells.jsonl'
                if not path.exists():continue
                hashes[run]=sha(path.read_bytes())
                for line in path.read_text().splitlines():
                    r=json.loads(line);e=declared.get(r['cell'])
                    if e is None:continue
                    for key in ('item','repeat','group','prompt_sha256'):
                        if r.get(key)!=e.get(key):raise ValueError('receipt identity '+key+' '+r['cell'])
                    if r['cell'] in receipts:raise ValueError('duplicate receipt '+r['cell'])
                    ok,reason=accepted(r,e['prompt_sha256'])
                    receipts[r['cell']]={**r,'accepted':ok,'acceptance_reason':reason,'source_run':run}
    procedures=defaultdict(list)
    for e in declared.values():
        key=e['arm']+'|'+e['member']
        if e['arm']=='L':key+='|world='+e['world']+'|fold='+e['fold']
        procedures[key].append(e)
    outputs={};inventory=[]
    for proc,rows in sorted(procedures.items()):
        byitem=defaultdict(list);settings={};counts=Counter();runids=set();hashset=set()
        for e in rows:
            r=receipts.get(e['cell'],{'category':'MISSING','repeat':e['repeat'],'accepted':False,'acceptance_reason':'MISSING'})
            byitem[e['item']].append(r);counts[r['category']]+=1
            if r.get('run_id'):runids.add(r['run_id'])
            if e.get('prompt_sha256'):hashset.add(e['prompt_sha256'])
        scores={}
        for iid,rs in byitem.items():
            unique_repeats(rs);vals=[r['score'] for r in rs if r['accepted']];blank=fresh[iid]['blank']
            scores[iid]={'value':0. if blank else statistics.median(vals) if len(vals)>=2 else None,'complete_repeats':len(vals),'structural_blank':blank,
                         'repeats':[{k:r.get(k) for k in ('cell','repeat','run_id','source_run','score','category','accepted','acceptance_reason','prompt_sha256','prompt_sha256_delivered','verdict_sha256')} for r in rs]}
        e=rows[0];member=e['member'];settings=(main['judges']['F' if e['arm']=='L' else e['arm']][member])
        inventory.append({'procedure':proc,'arm':e['arm'],'world':e.get('world'),'fold':e.get('fold'),'member':member,'harness':'vb103_judge','settings':settings,'parser':'frozen experiment100 prompts.parse; normalized score_0_5 / 5','aggregation':'median of >=2 accepted of 3 declared repeats','source_run_ids':sorted(runids),'prompt_hash_count':len(hashset),'status_counts':dict(counts),'declared_items':len(scores),'nonblank':sum(not r['structural_blank'] for r in scores.values()),'observed_nonblank':sum(r['value'] is not None and not r['structural_blank'] for r in scores.values()),'primary_pool_overlap':({'F|H2_opus55_max':'opus55x|H2','Z|H0_opus55_max':'opus55x|H0'}.get(proc)),
                          'fitting_scope':'fixed historical prompt' if e['arm']!='L' else 'all original groups; late G16/G17 excluded from build' if e['fold']=='ALL' else 'rebuilt independently excluding '+e['fold'],
                          'target_views':['persona','C0','common-family-excluded','own-provider-family-excluded'],'all_groups_provenance':late['all_groups_judges'].get(e.get('world')) if e.get('fold')=='ALL' else None})
        outputs[proc]=scores
    # Ensembles are explicitly their own procedures and require both members.
    for proc in list(outputs):
        if 'opus55_max' not in proc:continue
        other=proc.replace('opus55_max','sol_high')
        if other not in outputs:continue
        key=proc.replace('opus55_max','opus55_max_plus_sol_high_ENSEMBLE')
        outputs[key]={iid:{'value':(r['value']+outputs[other][iid]['value'])/2 if r['value'] is not None and outputs[other][iid]['value'] is not None else None,'members':[proc,other],'structural_blank':r['structural_blank']} for iid,r in outputs[proc].items()}
    write(RESULTS/'existing_v5_inventory.json',{'run_id':RUN_ID,'procedures':inventory,'raw_hashes':hashes,'learned_procedures_are_fold_specific':True,'ensemble_procedures':[p for p in outputs if 'ENSEMBLE' in p],'original_all_groups_fitted_prediction_availability':'No additional all-groups original-group score stream was declared in the inspected main manifest; late ALL procedures are retained separately.'})
    write(PRIVATE/'existing_v5_scores.json',outputs)
    public={proc:{iid:{**{k:v for k,v in row.items() if k!='repeats'},'raw_repeats_sha256':sha(json.dumps(row.get('repeats',[]),sort_keys=True).encode()),
                     'raw_repeat_sample_sd':statistics.stdev([x['score'] for x in row.get('repeats',[]) if x['accepted']]) if row.get('complete_repeats',0)>=2 else None} for iid,row in rows.items()} for proc,rows in outputs.items()}
    write(RESULTS/'existing_v5_scores.json',public)
    print('Inventoried',len(inventory),'member procedures and',len(outputs)-len(inventory),'separate ensemble procedures')

if __name__=='__main__':
    import json
    main()
