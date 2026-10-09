"""Freeze the full criterion submanifest under prospective Amendment 04."""
import shutil
from collections import Counter
from e47_adapter import ROOT,PRIVATE,RESULTS,POOL,RUN_ID,read,write,sha

def main():
    draft=read(RESULTS/'admission_manifest.json')
    if read(RESULTS/'render_memo_equality.json')['verdict']!='PASS':raise ValueError('render memo equivalence not verified')
    if read(RESULTS/'fresh_prompt_proof.json')['exact']!=1382:raise ValueError('fresh cache proof incomplete')
    if set(draft['configurations'])!=set(POOL):raise ValueError('incomplete pool')
    out=RESULTS/'criterion';private=PRIVATE/'criterion';private.mkdir(parents=True,exist_ok=True)
    out.mkdir(parents=True,exist_ok=True)
    if (out/'admission_manifest.json').exists():raise ValueError('criterion already frozen; adopt it')
    counts={};hashes={}
    for cfg in POOL:
        path=RESULTS/'cells'/f"{cfg.replace('|','__')}.json"
        if sha(path.read_bytes())!=draft['cells_sha256'][cfg]:raise ValueError('draft changed')
        blob=read(path);cells=blob['cells']
        if len(cells)!=2250 or any(c['kind']!='crit' for c in cells):raise ValueError('criterion must declare 750 x 3 cells per config')
        if len({c['item'] for c in cells})!=750:raise ValueError('criterion item coverage')
        dest=out/'cells'/path.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(path,dest);hashes[cfg]=sha(dest.read_bytes());counts[cfg]=dict(Counter(c['status'] for c in cells))
    for name in ('panel.json','agent_bundle_check.json','agent_harness.json','transport_policy.json'):
        src=RESULTS/name
        if name in ('agent_bundle_check.json','agent_harness.json') and read(src)['verdict']!='PASS':raise ValueError('transport check failed')
        shutil.copyfile(src,out/name)
    for name,target in [('cells',PRIVATE/'cells'),('valkyrie.yaml',PRIVATE/'valkyrie.yaml')]:
        dest=private/name
        if not dest.exists():dest.symlink_to(target)
    receipt={'run_id':RUN_ID,'phase':'criterion','state':'FROZEN','configurations':list(POOL),'counts':counts,'cells_sha256':hashes,
             'transport_policy_sha256':sha((out/'transport_policy.json').read_bytes()),
             'contract_hashes':{p.name:sha(p.read_bytes()) for p in [ROOT.parent/'PROTOCOL.md',*sorted(ROOT.parent.glob('AMENDMENT_*.md'))]},
             'pending_required_phase':'complete structurally resolved probes, all properties and all analyses remain required','smoke_conditions':'one distinct first-renderable criterion repeat-1 smoke task per configuration, never substituted for measured criterion'}
    write(out/'admission_manifest.json',receipt);print('Criterion frozen: 27000 declared cells, twelve configurations, no new call yet.')

if __name__=='__main__':main()
