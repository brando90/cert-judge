"""Owned E47 paths around byte-frozen E39 rendering, packing and parsing functions.

No driver, historical item loader, historical label reader, or provider client is
executed here. All outputs are confined to this experiment's owned directories.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
PRIVATE = ROOT/'private'
RESULTS = ROOT/'results'
VENDOR = ROOT/'vendor/e39'
DEPENDENCIES = PRIVATE/'dependencies'
POOL = ('opus55x|D0','opus55x|H0','opus55x|H2','qwen36|D0','qwen36|H0','qwen36|H1','qwen36|H2','qwen36|R4','t2_qwen|D0','t2_qwen|H2','t2_sonnet5|D0','t2_sonnet5|H2')
BASE_MODEL = {'opus55x':'Opus','qwen36':'Qwen','t2_qwen':'Qwen','t2_sonnet5':'Sonnet'}
FAMILY = {'opus55x':'Anthropic','qwen36':'Alibaba','t2_qwen':'Alibaba','t2_sonnet5':'Anthropic'}
RUN_ID = 'cj-e47-v5-10-08-2026-a1'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read(path):
    return json.loads(Path(path).read_text())

def write(path, value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n');temp.replace(path)

def module(name, path):
    if name in sys.modules:
        existing=sys.modules[name]
        if Path(existing.__file__).resolve()!=Path(path).resolve():
            raise RuntimeError('module namespace collision: '+name)
        return existing
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj)
    return obj

def frozen():
    sys.path.insert(0,str(REPO/'py_src'))
    e=module('e39',VENDOR/'e39.py')
    # Bind before any dependent import captures mutable globals.
    e.E=ROOT; e.REPO=REPO; e.PRIVATE=PRIVATE; e.RESULTS=RESULTS
    e.PROMPT_DIR=VENDOR; e.EXPERIMENT='certjudge47-v5-a1';e.BENCHMARK='certjudge47-v5-a1';e.SEED=47
    e.VB_REPO=DEPENDENCIES
    e.X100=DEPENDENCIES/'experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test'
    e.X103=DEPENDENCIES/'experiments/103_single_call_baselines_all_models_vbv1_vbv2_valkyrie_validated_fsc_judge'
    e.load_items=load_items
    e.x100_modules=lambda:(None,prompts(),None)
    legacy=module('legacy',VENDOR/'legacy.py')
    render=module('render_cells',VENDOR/'render_cells.py');render.CELL_DIR=PRIVATE/'cells'
    pack=module('pack',VENDOR/'pack.py');pack.PACK_ROOT=PRIVATE/'packs'
    ctl=module('judge_controller',VENDOR/'judge_controller.py')
    ctl.JUDGE=PRIVATE/'judge';ctl.STATE=ctl.JUDGE/'state.json';ctl.RAW=ctl.JUDGE/'raw'
    return e,render,pack,ctl

def phase_context(phase):
    if phase not in ('criterion','probes'):raise ValueError('unknown phase')
    e,render,pack,ctl=frozen()
    e.RESULTS=RESULTS/phase;e.PRIVATE=PRIVATE/phase
    render.CELL_DIR=e.PRIVATE/'cells';pack.PACK_ROOT=e.PRIVATE/'packs'
    ctl.JUDGE=e.PRIVATE/'judge';ctl.STATE=ctl.JUDGE/'state.json';ctl.RAW=ctl.JUDGE/'raw'
    return e,render,pack,ctl

def prompts():
    x100=DEPENDENCIES/'experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test'
    common=module('common',x100/'scripts/common.py')
    common.REPO=DEPENDENCIES;common.EXPT=x100
    common.ITEMS=PRIVATE/'FORBIDDEN_historical_items'
    def no_labels(*args,**kwargs):
        raise RuntimeError('historical label/item loading is forbidden')
    common.load_items=no_labels
    common.GATEWAY_DIR=DEPENDENCIES/'experiments/95_full_vb_860ish_agent_gpt6_luna_llm_judge_gpt6_sol/tc_gateway'
    module('kernel_axioms',DEPENDENCIES/'scripts/scsc/kernel_axioms.py')
    p=module('prompts',x100/'scripts/prompts.py')
    if not getattr(p,'_e47_memoized',False):
        # Pure frozen extraction is repeated for the same 50 references and
        # identical prompt variants. Memoization changes no output bytes.
        p.extract_public_obligations=lru_cache(maxsize=4096)(p.extract_public_obligations)
        p.rater_instructions=lru_cache(maxsize=1)(p.rater_instructions)
        p._exp75_constant=lru_cache(maxsize=4)(p._exp75_constant)
        p._e47_memoized=True
    # The exact historical examples are a frozen prompt resource, not an input
    # dataset. Fresh requests prove the entire system+user hash against v5.
    system=read(PRIVATE/'frozen_h2_prompt.json')['system']
    match=re.search(r'<rated_examples>.*?</rated_examples>',system,re.S)
    if match is None:raise ValueError('missing frozen H2 examples')
    p.demo_block=lambda item:match.group(0)
    return p

def source_items():
    base=ROOT/'inputs/veribench_v5'
    rows=[x for x in read(base/'manifest.json')['items'] if x['group']!='G00']+read(base/'late/manifest_G16_G17.json')['items']
    if len(rows)!=750 or len({r['item'] for r in rows})!=750:raise ValueError('frozen item population changed')
    return rows

def candidate_path(row):
    if row['group']=='G16': return PRIVATE/'late_candidates/G16'/f"{row['harbor']}.lean"
    if row['group']=='G17': return PRIVATE/'late_candidates'/row['source']['file'].split('/outputs/',1)[1]
    return ROOT/'inputs/veribench_v5/inputs/candidates'/row['group']/f"{row['harbor']}.lean"

def load_items():
    rows=[]
    for r in source_items():
        taskroot=ROOT/'inputs/veribench_v5/inputs/tasks'/r['harbor']
        ref=taskroot/r['ref_name']; py=taskroot/r['py_name'];cand=candidate_path(r)
        for path,digest in ((ref,r['ref_sha256']),(py,r['py_sha256'])):
            if sha(path.read_bytes())!=digest:raise ValueError('source hash mismatch '+str(path))
        available=cand.is_file()
        if available and sha(cand.read_bytes())!=r['cand_sha256']:raise ValueError('candidate hash mismatch '+r['item'])
        rows.append({**r,'candidate_path_abs':str(cand),'candidate_file':r['cand_name'],'ref_ann_path_abs':str(ref),'ref_ann_path':str(ref),
                     'ref_snap_path':str(ref),'py_ann_path_abs':str(py),'py_ann_path':str(py),'gold_file_name':r['ref_name'],'source_available':available})
    return rows

def panel():
    e,*_=frozen()
    historical=read(RESULTS/'historical_primary_pool_inventory.json')
    h={r['config']:r for r in historical['pool']}
    units=[]
    for u in e.panel_units():
        if u['config'] not in POOL:continue
        record=h[u['config']]
        u.update(selectors=[record['selector']],substitutes=[],base_model=BASE_MODEL[u['model_key']],provider_family=FAMILY[u['model_key']])
        if u['pack_flavor']=='agent':u['kwargs']=record['kwargs']
        units.append(u)
    assert len(units)==12
    return units

def prove_fresh_prompts():
    e,render,_,_=frozen();p=prompts()
    expected={**read(ROOT/'inputs/veribench_v5/manifest.json')['judge_prompts'],**read(ROOT/'inputs/veribench_v5/late/manifest_G16_G17.json')['judge_prompts']}
    rows=[]
    for item in load_items():
        if item['blank']:continue
        for prompt in ('H0','H2'):
            key=prompt+'__'+item['item']
            row={'item':item['item'],'prompt':prompt,'candidate_sha256':item['cand_sha256'],'reference_sha256':item['ref_sha256'],'python_sha256':item['py_sha256'],'expected':expected[key]['prompt_sha256']}
            if not item['source_available']:
                row.update(status='SOURCE_UNAVAILABLE');rows.append(row);continue
            system,user=p.render(e.PROMPTS[prompt]['rubric'],item,Path(item['candidate_path_abs']).read_text(encoding='utf-8',errors='replace'),item['candidate_file'])
            digest=sha((system+'\n\n'+user).encode());row.update(rendered=digest,status='EXACT' if digest==row['expected'] else 'MISMATCH')
            write(PRIVATE/'fresh_prompts'/f'{key}.json',{'system':system,'user':user})
            rows.append(row)
    receipt={'run_id':RUN_ID,'rows':rows,'exact':sum(r['status']=='EXACT' for r in rows),'expected':len(rows),'unavailable':sum(r['status']=='SOURCE_UNAVAILABLE' for r in rows),'mismatches':sum(r['status']=='MISMATCH' for r in rows)}
    write(RESULTS/'fresh_prompt_proof.json',receipt)
    print({k:v for k,v in receipt.items() if k!='rows'})
    if receipt['mismatches']:raise ValueError('fresh prompt bytes differ')

if __name__=='__main__':
    prove_fresh_prompts()
