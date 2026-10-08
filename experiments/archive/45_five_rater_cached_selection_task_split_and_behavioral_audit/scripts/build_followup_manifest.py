#!/usr/bin/env python3
"""Enumerate a proposal; no inference imports or admission capability."""
import json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
s=json.loads((E/'results/SELECTION.json').read_text())
items=json.loads((E/'results/coverage_by_item.json').read_text())
tasks={x['task']:x['split'] for x in items}
variants=['identity','weak1','weak2','weak3','alpha','format','vacuity','overconstraint','redundant_tests','duplicates','irrelevant_tautologies','score_comments']
rows=[{'task':t,'split':split,'configuration':c,'status':'BLOCKED_PRECONDITIONS','fixed_variants':variants,'repeats':3,'adaptive_rounds':8} for t,split in sorted(tasks.items()) for c in s['pool']]
r={'status':'PROPOSED_NOT_RUN','admission_authorized':False,'task_configuration_cells':len(rows),'fixed_probe_calls':len(rows)*12*3,'adaptive_attacker_calls':len(rows)*8,'adaptive_proposal_judge_calls_max':len(rows)*8,'adaptive_initial_judge_calls':len(rows),'adaptive_fresh_outcome_calls_max':len(rows)*6,'total_calls_max':len(rows)*(36+8+8+1+6),'new_calls_made':0,'cost_usd':None,'cost_status':'UNQUOTED','missing_evidence':['correct nonvacuous baseline per task','whole-file strictness countermodels','equivalent-attack relation checker','prospective extraction contract','exact route/model/token/cost quote and authorization'],'cells':rows}
assert r['total_calls_max']==17700 and len(rows)==300
(E/'results/followup_manifest.json').write_text(json.dumps(r,indent=2)+'\n')
print('PROPOSED_NOT_RUN: 300 cells, 17700 maximum calls, 0 calls made')
