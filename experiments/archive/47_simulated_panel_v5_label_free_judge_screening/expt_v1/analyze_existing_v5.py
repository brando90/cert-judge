"""Cached v5 procedures remain separate, including each rebuilt learned fold."""
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import json
from e47_adapter import ROOT,RESULTS,PRIVATE,read,sha
from analyze_campaign import save,clean
from statistics_v5 import Panel,DRAWS

def one(proc,values,targets):
    out=RESULTS/'existing_descriptive'/f'{sha(proc.encode())[:20]}.json'
    input_hash=sha(json.dumps({'procedure':proc,'values':values,'targets':targets},sort_keys=True).encode())
    if out.exists() and read(out).get('input_hash')==input_hash:return proc,str(out)
    items=[r for r in targets if r['item'] in values and not r['blank']]
    ensemble='ENSEMBLE' in proc
    own='T_excluding_Anthropic_OpenAI' if ensemble else 'T_excluding_Anthropic' if 'opus55' in proc else 'T_excluding_OpenAI'
    scores=[[values[r['item']]['value']] for r in items];views={}
    for target in ['T_all','T_C0','T_common_excluding_Anthropic_Alibaba',own]:
        p=Panel(items,[proc],scores,[r[target] for r in items],base_models=['Opus+Sol ensemble' if ensemble else 'Opus' if 'opus55' in proc else 'Sol'],provider_families=['Anthropic+OpenAI' if ensemble else 'Anthropic' if 'opus55' in proc else 'OpenAI'])
        views[target]=p.criterion(DRAWS)[proc]
    save(str(out.relative_to(RESULTS)),{'procedure':proc,'input_hash':input_hash,'draws':DRAWS,'seed':47,'views':views,'interpretation':'fold-specific learned evaluation procedure' if proc.startswith('L|') else 'fixed source configuration or explicitly named ensemble','primary_pool_member':not ensemble and proc in ('F|H2_opus55_max','Z|H0_opus55_max')})
    return proc,str(out)

def main():
    scores=read(RESULTS/'existing_v5_scores.json');targets=read(RESULTS/'targets_reconstructed.json');paths={}
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(one,proc,values,targets) for proc,values in scores.items()]
        for future in as_completed(futures):
            proc,path=future.result();paths[proc]=str(Path(path).relative_to(ROOT));save('existing_descriptive_index.json',{'completed':len(paths),'declared':len(scores),'procedures':paths,'pooled_rebuilt_judge':False});print('cached procedure analyzed',proc,flush=True)

if __name__=='__main__':main()
