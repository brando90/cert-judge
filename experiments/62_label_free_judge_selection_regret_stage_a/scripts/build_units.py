"""TLDR: One-off builder of results/units_90.json inputs: recomputes the 26 new E60 units and the 9 hosted qwen36 units (and the 36 seed-1 replicates)
from the E60 harvest tarballs. The 54 older E59 units are copied from E59's ANALYSIS.json part1.unit_table (their harvests live on the cluster).
Usage: ~/.venvs/e59/bin/python build_units.py --h0 <dir with seed0/harvest/e39> --h1 <dir with seed1/harvest/e39> --out units_new_and_qwen36.json
(extract experiments/60_*/results/final_2026-10-25/harvest/e60_harv{0,1}.tgz first; then merge with E59's table as in README.)"""
import sys, json, copy, argparse
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('--h0',type=Path,required=True); ap.add_argument('--h1',type=Path,required=True); ap.add_argument('--out',type=Path,required=True)
args=ap.parse_args()
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'60_open_weight_proxy_index_rigor_round/scripts'), str(R/'59_open_weight_proxy_index_and_frontier_fit/scripts')]
import analyze60 as T
M=T.M; AN=T.AN; e58=T.e58
items=AN.load_items(); manifest=e58.read_json(e58.E39_DIR/'results/probe_manifest.json')
hosted=M.load_hosted()
new=T.load_dirs([args.h0/'seed0'])
rep=T.load_dirs([args.h1/'seed1'] ,rename=T.OTHER_REP_SFX) if list(args.h1.rglob('e39')) else {}
print(len(new),len(rep))
allh={**hosted,**new,**rep}
units=M.build_units_from(allh,items,manifest,2000)
M.part1(units,items,hosted,{**new,**rep},2000)
out=[]
for u in units:
    if u['config'] in new or u['config'] in rep or u['model_key']=='qwen36':
        c=u['criteria']['heldout']
        out.append({'config':u['config'],'family':u['model_key'],'seed':'s1' if u['config'] in rep else 's0','criterion':c.get('spearman'),'criterion_ci':c.get('ci'),'status':c.get('status'),
                    **{k:u['indices'].get(k) for k in ('C_ms_gold','F1_probe','F2_item','F12')}})
json.dump(out,open(args.out,'w'),indent=1,default=float)
print(len(out)); print(out[0]); print(json.dumps(units[0]['criteria']['heldout'])[:400])
