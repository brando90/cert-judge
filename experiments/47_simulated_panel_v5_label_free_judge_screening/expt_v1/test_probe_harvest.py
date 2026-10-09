"""Probe bindings, certified submission bytes, and zero-transport collection adoption."""
import base64
import copy
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import harvest_original_artifacts as h
import harvest_probe_artifacts as probes
from collect_probe_artifacts import collect
from e47_adapter import phase_context, prompts, sha, write

class ProbeHarvestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        h.verify_dependencies();cls.e,cls.renderer,cls.pack,cls.ctl=phase_context('probes')
        cls.writer=h.module('e47_offline_original_writer',h.WRITER);cls.prompt=prompts();cls.unit=cls.ctl.unit_of('opus55x|D0')
    def fixture(self,kind='ms_gold',repeat=2):
        cell={'kind':kind,'key':'fixture','task':'fixture','item':None,'level':1,'repeat':repeat,'status':'render','valid':True,'prompt_sha256':sha(b'system\n\nuser')}
        cell['cell']=self.renderer.cell_id(kind,cell['key'],1,repeat)
        meta={**cell,'queue_index':1,'task_id':self.pack.task_id_of('cj47','D0','q00001__'+cell['cell'])}
        instruction=self.pack.task_file(cell['cell'],cell['key'],repeat,kind,self.unit['rubric'],'system','user').encode()
        meta.update(instruction_bytes=len(instruction),instruction_sha256=sha(instruction))
        return meta,cell,instruction,{'system':'system','user':'user'}
    def check(self,meta,cell,instruction,rendered,unit=None):
        return h.verify_request(meta,cell,unit or self.unit,instruction,rendered,self.pack,self.writer,'probes')
    def test_frozen_probe_kinds_and_supplemental_repeat(self):
        for kind,info in self.e.KINDS.items():
            if kind!='crit':self.check(*self.fixture(kind,2 if kind=='ms_gold' else info['repeats']))
        for kind,repeat in [('crit',1),('unknown',1),('ms_gold',3),('blank',2)]:
            with self.assertRaises(h.InvalidEvidence):self.check(*self.fixture(kind,repeat))
    def test_every_probe_binding_mutation(self):
        meta,cell,instruction,rendered=self.fixture()
        for field in (*h.IDENTITY_FIELDS,'task_id','instruction_bytes','instruction_sha256'):
            bad=copy.deepcopy(meta);bad[field]='wrong'
            with self.subTest(field=field),self.assertRaises(h.InvalidEvidence):self.check(bad,cell,instruction,rendered)
        for field,value in [('valid',False),('status','deterministic')]:
            bad=copy.deepcopy(cell);bad[field]=value
            with self.assertRaises(h.InvalidEvidence):self.check(meta,bad,instruction,rendered)
        unit=copy.deepcopy(self.unit);unit['rubric']='wrong'
        with self.assertRaises(h.InvalidEvidence):self.check(meta,cell,instruction,rendered,unit)
        for field in ('system','user'):
            bad=dict(rendered);bad[field]+=' altered'
            with self.assertRaises(h.InvalidEvidence):self.check(meta,cell,instruction,bad)
    def test_missing_task_remains_unresolved_without_transport(self):
        meta,cell,instruction,rendered=self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);task=root/'packs'/meta['task_id'];task.mkdir(parents=True);(task/'instruction.md').write_bytes(instruction)
            write(root/'probes/cells'/self.unit['config'].replace('|','__')/(cell['cell']+'.json'),rendered)
            artifacts=root/'artifacts';artifacts.mkdir()
            with patch.object(h,'PRIVATE',root),patch.object(self.ctl,'cli',side_effect=AssertionError('transport')):
                rows=h.harvest_run({'frozen_task_ids':[meta['task_id']]},{'run_id':'r','expected_cells':1},self.unit,{meta['task_id']:meta},{cell['cell']:cell},{'pack':str(root/'packs')},self.pack,self.writer,lambda *a:self.fail('parse absent artifact'),artifacts,{},phase='probes')
            self.assertEqual(rows[0]['phase'],'probes');self.assertFalse(rows[0]['accepted']);self.assertFalse(rows[0]['prior_verdict_absence_established'])
            self.assertEqual(rows[0]['acceptance_reason'],'ARTIFACT_ABSENT_UNRESOLVED')
    def test_agent_requires_certified_exact_server_bytes(self):
        meta,*_=self.fixture();data=b'{"score":7,"reason":"fixture"}'
        row={'frozen_instruction_sha256':meta['instruction_sha256'],'acceptance_reason':'SUBMITTED_VERDICT_BYTES_UNCERTIFIED','accepted':False}
        server={'task_id':meta['task_id'],'instruction_sha256':meta['instruction_sha256'],'submission_status':'ok','solution_b64':base64.b64encode(data).decode(),'solution_bytes':len(data),'solution_sha256':sha(data)}
        parse=lambda u,t:self.ctl.parse_verdict(u,t,self.prompt)
        valid=copy.deepcopy(row);probes.certify_agent(valid,server,meta,self.unit,parse);self.assertTrue(valid['accepted']);self.assertEqual(valid['score'],.7)
        for field,value in [('task_id','wrong'),('instruction_sha256','wrong'),('solution_bytes',1),('solution_sha256','wrong'),('solution_b64','not base64')]:
            bad=copy.deepcopy(server);bad[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):probes.certify_agent(copy.deepcopy(row),bad,meta,self.unit,parse)
        bad=copy.deepcopy(row);bad['acceptance_reason']='TRAJECTORY_AGENT_BINDING'
        with self.assertRaisesRegex(h.InvalidEvidence,'CONFLICTING'):probes.certify_agent(bad,server,meta,self.unit,parse)
        invalid=b'{"score":999,"reason":"invalid"}';bad={**server,'solution_b64':base64.b64encode(invalid).decode(),'solution_bytes':len(invalid),'solution_sha256':sha(invalid)}
        with self.assertRaises(ValueError):probes.certify_agent(copy.deepcopy(row),bad,meta,self.unit,parse)
    def test_collection_adopts_success_without_final_view_idempotently(self):
        with tempfile.TemporaryDirectory() as directory:
            raw=Path(directory);entry={'run_id':'original','phase':'terminal','run_status':'error','expected_cells':1};key='cfg@main';out=raw/'cfg_main_artifacts';out.mkdir()
            write(out/'collection_command.json',{'run_id':'original','returncode':0,'stdout':'original download','stderr':''});write(out/'terminal_snapshot.json',{'missing_run_ids':[],'requested_count':1,'returned_count':1,'runs':[{'run_id':'original','status':'ERROR','total_tasks':1}]});(out/'task').mkdir();(out/'task/bytes').write_bytes(b'evidence')
            ctl=SimpleNamespace(RAW=raw,load_state=lambda:{'runs':{key:entry}},TERMINAL_RUN={'error'},cli=lambda *a,**k:self.fail('transport repeated'))
            a=collect(ctl,key);b=collect(ctl,key);self.assertEqual(a,b);self.assertEqual(a[2]['new_inference_calls'],0)
            entry['run_id']='changed'
            with self.assertRaises(h.InvalidEvidence):collect(ctl,key)
            entry['run_id']='original';(out/'task/bytes').write_bytes(b'changed')
            with self.assertRaisesRegex(h.InvalidEvidence,'HASH'):collect(ctl,key)
    def test_collection_refuses_failed_partial_wrong_run(self):
        for command in [None,{'run_id':'other','returncode':0},{'run_id':'original','returncode':1}]:
            with tempfile.TemporaryDirectory() as directory:
                raw=Path(directory);out=raw/'cfg_main_artifacts';out.mkdir()
                if command:write(out/'collection_command.json',command)
                ctl=SimpleNamespace(RAW=raw,load_state=lambda:{'runs':{'cfg@main':{'run_id':'original','phase':'terminal','run_status':'error'}}},TERMINAL_RUN={'error'},cli=lambda *a,**k:self.fail('transport'))
                with self.assertRaises(h.InvalidEvidence):collect(ctl,'cfg@main')


class ExistingRunAdoptionTests(unittest.TestCase):
    def test_only_complete_original_run_mask_is_adoptable(self):
        import re
        from campaign_driver import require_existing_runs
        from e47_adapter import POOL
        state={'runs':{c+'@main':{'run_id':f'00000000-0000-0000-0000-{i:012d}','config':c,'part':'main','expected_cells':1,'task_ids':None} for i,c in enumerate(POOL)}}
        ctl=SimpleNamespace(load_state=lambda:state,pack_rows=lambda c,p:[{'task_id':'original'}],UUID_RE=re.compile(r'[0-9a-f-]{36}'))
        self.assertEqual(len(require_existing_runs(ctl)),12)
        key=POOL[0]+'@main';original=copy.deepcopy(state['runs'][key])
        for field,value in [('run_id',None),('expected_cells',2),('task_ids',['other']),('config','other')]:
            state['runs'][key]={**original,field:value}
            with self.assertRaises(ValueError):require_existing_runs(ctl)
        del state['runs'][key]
        with self.assertRaises(ValueError):require_existing_runs(ctl)

class ConcurrentCollectionTests(unittest.TestCase):
    def test_two_collectors_download_original_run_once(self):
        import json,threading,time
        from concurrent.futures import ThreadPoolExecutor
        with tempfile.TemporaryDirectory() as directory:
            raw=Path(directory);calls=[];started=threading.Event();release=threading.Event()
            entry={'run_id':'original','phase':'terminal','run_status':'error','expected_cells':1}
            def cli(argv,**kwargs):
                calls.append(argv[:2])
                if argv[:2]==['run','output']:
                    started.set();release.wait(5);(Path(argv[-1])/'original-bytes').write_bytes(b'evidence')
                    return SimpleNamespace(returncode=0,stdout='collected',stderr='')
                self.assertEqual(argv[:2],['run','status'])
                return SimpleNamespace(returncode=0,stdout=json.dumps({'missing_run_ids':[],'requested_count':1,'returned_count':1,'runs':[{'run_id':'original','status':'ERROR','total_tasks':1}]}),stderr='')
            ctl=SimpleNamespace(RAW=raw,load_state=lambda:{'runs':{'cfg@main':entry}},TERMINAL_RUN={'error'},cli=cli)
            with ThreadPoolExecutor(max_workers=2) as pool:
                first=pool.submit(collect,ctl,'cfg@main');self.assertTrue(started.wait(2));second=pool.submit(collect,ctl,'cfg@main');time.sleep(.05);release.set()
                self.assertEqual(first.result(),second.result())
            self.assertEqual(calls,[['run','output'],['run','status']])

if __name__=='__main__':unittest.main()
