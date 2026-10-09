"""Compare full frozen D0 outputs with and without adapter memoization."""
from pathlib import Path
from e47_adapter import prompts,load_items,RESULTS,write,sha,RUN_ID

def main():
    p=prompts();cached=p.extract_public_obligations;plain=cached.__wrapped__
    items=sorted((r for r in load_items() if not r['blank']),key=lambda r:Path(r['candidate_path_abs']).stat().st_size)
    chosen=[items[0],items[len(items)//2],items[-1]];rows=[]
    for item in chosen:
        text=Path(item['candidate_path_abs']).read_text(encoding='utf-8',errors='replace')
        outputs=[]
        for extractor in (plain,cached,cached):
            p.extract_public_obligations=extractor
            try:
                system,user=p.render('D0_deployed_tc_v1',item,text,item['candidate_file'])
                outputs.append(('render',sha((system+'\n\n'+user).encode())))
            except p.Unmeasured as exc:outputs.append(('unmeasured',str(exc)))
        assert outputs[0]==outputs[1]==outputs[2],item['item']
        rows.append({'item':item['item'],'bytes':len(text.encode()),'equal':True,'outcome':outputs[0]})
        print(item['item'],'exact',flush=True)
    p.extract_public_obligations=cached
    write(RESULTS/'render_memo_equality.json',{'run_id':RUN_ID,'verdict':'PASS','cases':rows,'method':'full system+user bytes or exact Unmeasured message; uncached, cold cached and warm cached; minimum/median/maximum candidate byte lengths','cache_hits':cached.cache_info().hits})

if __name__=='__main__':main()
