"""Prospective scheduling never changes the task mask or repeats a mutation."""
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from reallocate_probe_capacity import eligible,check_identity,update_once

class CapacityTests(unittest.TestCase):
    entry={'run_id':'original','benchmark':'benchmark','agent':'agent','selector':'model','actual_label':'label','expected_cells':4}
    row={'run_id':'original','benchmark_name':'benchmark','agent_name':'agent','model':'model','label':'label','total_tasks':4,'status':'IN_PROGRESS'}
    def test_release_gate_and_every_identity_field(self):
        runs={'release@main':{'phase':'running'},'target@main':{'phase':'running'}}
        self.assertFalse(eligible(runs,['release'],'target'));runs['release@main']['phase']='terminal'
        self.assertTrue(eligible(runs,['release'],'target'));runs['target@main']['phase']='terminal'
        self.assertFalse(eligible(runs,['release'],'target'))
        for field in set(self.row)-{'status'}:
            with self.subTest(field=field),self.assertRaises(ValueError):check_identity({**self.row,field:None},self.entry)
    def test_one_mutation_acknowledges_server_value_and_preserves_universe(self):
        for failure in (None,'lost_response','wrong_value','wrong_tasks'):
            with self.subTest(failure=failure),tempfile.TemporaryDirectory() as d:
                calls=[];directory=Path(d)
                def cli(argv,**kwargs):
                    calls.append(argv)
                    if argv[:2]==['run','list']:payload={'runs':[self.row]}
                    elif argv[:2]==['run','update']:
                        self.assertTrue((directory/'intent.json').exists());self.assertEqual(argv,['run','update','original','--concurrency','50'])
                        if failure=='lost_response':raise TimeoutError('ambiguous mutation')
                        return SimpleNamespace(returncode=0,stdout='✓ Run concurrency updated to '+('20' if failure=='wrong_value' else '50')+'.',stderr='')
                    elif argv[:2]==['run','status']:payload={'missing_run_ids':[],'requested_count':1,'returned_count':1,'runs':[{'run_id':'original','total_tasks':5 if failure=='wrong_tasks' else 4,'status':'IN_PROGRESS'}]}
                    else:self.fail('unauthorized command')
                    return SimpleNamespace(returncode=0,stdout=json.dumps(payload),stderr='')
                ctl=SimpleNamespace(cli=cli,TERMINAL_RUN={'finished','error'})
                if failure:
                    with self.assertRaises((ValueError,TimeoutError)):update_once(ctl,self.entry,50,directory,lambda:None)
                else:self.assertEqual(update_once(ctl,self.entry,50,directory,lambda:None)['server_acknowledged_concurrency'],50)
                with self.assertRaisesRegex(ValueError,'prior scheduling intent'):update_once(ctl,self.entry,50,directory,lambda:None)
                self.assertEqual(sum(c[:2]==['run','update'] for c in calls),1)

if __name__=='__main__':unittest.main()
