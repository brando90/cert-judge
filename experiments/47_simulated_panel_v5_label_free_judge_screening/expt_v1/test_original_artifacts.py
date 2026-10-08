"""Adversarial offline fixtures: request identity and certified file bytes."""
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import harvest_original_artifacts as h
from e47_adapter import phase_context, prompts, sha, read, write, RUN_ID


def encoded(value):
    return (json.dumps(value, sort_keys=True)+'\n').encode()


class OriginalArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        h.verify_dependencies()
        _, _, cls.pack, cls.ctl = phase_context('criterion')
        cls.writer = h.module('e47_offline_original_writer', h.WRITER)
        cls.prompts = prompts()
        cls.unit = cls.ctl.unit_of('opus55x|D0')

    def fixture(self, response=b'{"score":7,"reason":"synthetic fixture"}'):
        unit=copy.deepcopy(self.unit)
        cell={'cell':'crit__G01__fixture__L0__r1','kind':'crit','key':'G01__fixture',
              'task':'fixture','item':'G01__fixture','level':0,'repeat':1,
              'prompt_sha256':sha(b'system\n\nuser')}
        meta={**cell,'queue_index':0,'task_id':self.pack.task_id_of('cj47','D0','q00000__'+cell['cell'])}
        instruction=self.pack.task_file(cell['cell'],cell['item'],1,'crit',unit['rubric'],'system','user').encode()
        meta.update(instruction_bytes=len(instruction),instruction_sha256=sha(instruction))
        rendered={'system':'system','user':'user'}
        header,hashes=h.verify_request(meta,cell,unit,instruction,rendered,self.pack,self.writer)
        entry={'selector':unit['selectors'][0],'benchmark':'frozen-benchmark','run_id':'original-run'}
        submitted=response if response.endswith(b'\n') else response+b'\n'
        receipt={'condition':'expt103-judge-transport-v1','task_id':meta['task_id'],'selector':entry['selector'],
                 'judge_config':unit['config'],'benchmark':entry['benchmark'],'cell':cell['cell'],
                 'output_path':header['output_path'],'expected':hashes,
                 **{k+'_sha256':v for k,v in hashes.items()},
                 'config':{'max_tokens':16384,'compute_effort':'max'},'requests_sent':1,'attempt':1,
                 'status':'measured','finish_reason':{'reason':'stop'},'fallback':None,'cost_usd':0.01,
                 'output_text_bytes':len(response),'output_text_sha256':sha(response),
                 'written_file':{'path':header['output_path'],'bytes':len(submitted),'sha256':sha(submitted)}}
        return meta,cell,unit,instruction,rendered,header,hashes,entry,receipt,response

    def recover(self, fixture, receipt=None, outer=None, response=None):
        meta,cell,unit,instruction,rendered,header,hashes,entry,original,original_response=fixture
        receipt=original if receipt is None else receipt;raw=encoded(receipt)
        members={'logs/vb103/receipt.json':raw,'logs/vb103/response.txt':original_response if response is None else response}
        with patch.object(self.ctl,'cli',side_effect=AssertionError('transport called')),patch.object(self.ctl,'download',side_effect=AssertionError('download called')):
            return h.recover_single(meta,unit,entry,header,hashes,raw if outer is None else outer,members,
                     lambda u,t:self.ctl.parse_verdict(u,t,self.prompts))

    def test_frozen_parser_valid_fixture_newline_and_idempotence(self):
        for suffix in (b'',b'\n',b'\n\n'):
            fixture=self.fixture(b'{"score":7,"reason":"fixture"}'+suffix)
            a=self.recover(fixture);b=self.recover(fixture)
            self.assertEqual(a,b);self.assertTrue(a['accepted']);self.assertEqual(a['score'],.7)
            self.assertEqual(a['verdict_sha256'],fixture[-2]['written_file']['sha256'])

    def test_every_receipt_binding_mutation_is_rejected(self):
        fixture=self.fixture()
        mutations={'condition':'wrong','task_id':'wrong','selector':'wrong','judge_config':'wrong',
                   'benchmark':'wrong','cell':'wrong','output_path':'wrong','system_sha256':'wrong',
                   'user_sha256':'wrong','prompt_sha256':'wrong','expected':{},'config':{},
                   'output_text_bytes':1,'output_text_sha256':'wrong','written_file':{},
                   'requests_sent':None,'attempt':None,'fallback':'unapproved'}
        for field,value in mutations.items():
            with self.subTest(field=field):
                receipt=copy.deepcopy(fixture[-2]);receipt[field]=value
                with self.assertRaises(h.InvalidEvidence):self.recover(fixture,receipt)
        for field in ('path','bytes','sha256'):
            receipt=copy.deepcopy(fixture[-2]);receipt['written_file'][field]='wrong'
            with self.assertRaises(h.InvalidEvidence):self.recover(fixture,receipt)

    def test_cell_repeat_item_rubric_task_instruction_and_prompt_bindings(self):
        fixture=self.fixture();meta,cell,unit,instruction,rendered,*_=fixture
        for field in h.IDENTITY_FIELDS:
            bad=copy.deepcopy(meta);bad[field]='wrong'
            with self.subTest(field=field),self.assertRaises(h.InvalidEvidence):
                h.verify_request(bad,cell,unit,instruction,rendered,self.pack,self.writer)
        for field in ('task_id','instruction_sha256','instruction_bytes'):
            bad=copy.deepcopy(meta);bad[field]='wrong'
            with self.assertRaises(h.InvalidEvidence):h.verify_request(bad,cell,unit,instruction,rendered,self.pack,self.writer)
        bad=copy.deepcopy(unit);bad['rubric']='H0_human_mirror'
        with self.assertRaises(h.InvalidEvidence):h.verify_request(meta,cell,bad,instruction,rendered,self.pack,self.writer)
        for kind in ('system','user'):
            bad=copy.deepcopy(rendered);bad[kind]+=' changed'
            with self.assertRaises(h.InvalidEvidence):h.verify_request(meta,cell,unit,instruction,bad,self.pack,self.writer)
        with self.assertRaises(h.InvalidEvidence):h.verify_request(meta,cell,unit,instruction+b' ',rendered,self.pack,self.writer)

    def test_conflicting_outer_receipt_and_response_hash(self):
        fixture=self.fixture()
        with self.assertRaisesRegex(h.InvalidEvidence,'CONFLICT'):self.recover(fixture,outer=b'{}')
        with self.assertRaisesRegex(h.InvalidEvidence,'RESPONSE'):self.recover(fixture,response=b'forged')

    def test_invalid_rubric_and_429_cannot_be_rescued_by_parseable_score(self):
        result=self.recover(self.fixture(b'{"score":999,"reason":"invalid"}'))
        self.assertFalse(result['accepted']);self.assertEqual(result['status'],'parse_error')
        fixture=self.fixture();receipt=copy.deepcopy(fixture[-2]);receipt.update(requests_sent=2,attempt=2,http_status=429,error_kind='HTTPError')
        result=self.recover(fixture,receipt);self.assertFalse(result['accepted'])
        self.assertEqual(result['acceptance_reason'],'HTTP_429_INFRASTRUCTURE_FAILURE')
        self.assertEqual(result['score'],.7);self.assertEqual(result['http_status'],429)
        self.assertEqual(result['cost_usd'],.01)

    def test_missing_excess_inconsistent_requests_and_nonclean_finish(self):
        fixture=self.fixture()
        for requests in (None,0,3,True,1.0):
            receipt=copy.deepcopy(fixture[-2]);receipt['requests_sent']=requests
            with self.assertRaises(h.InvalidEvidence):self.recover(fixture,receipt)
        receipt=copy.deepcopy(fixture[-2]);receipt.update(requests_sent=2,attempt=2)
        with self.assertRaisesRegex(h.InvalidEvidence,'SECOND_REQUEST'):self.recover(fixture,receipt)
        receipt=copy.deepcopy(fixture[-2]);receipt['finish_reason']={'reason':'length'}
        self.assertFalse(self.recover(fixture,receipt)['accepted'])

    def test_duplicate_archive_members_json_keys_and_task_ids(self):
        out=io.BytesIO()
        with tarfile.open(fileobj=out,mode='w:gz') as archive:
            for payload in (b'first',b'conflict'):
                member=tarfile.TarInfo('logs/vb103/receipt.json');member.size=len(payload)
                archive.addfile(member,io.BytesIO(payload))
        with self.assertRaisesRegex(h.InvalidEvidence,'DUPLICATE_ARCHIVE'):h.archive_members(out.getvalue())
        with self.assertRaisesRegex(h.InvalidEvidence,'DUPLICATE_JSON'):h.json_bytes(b'{"task_id":1,"task_id":2}')
        with self.assertRaisesRegex(h.InvalidEvidence,'DUPLICATE_TASK'):h.unique([{'task_id':'a'},{'task_id':'a'}],'task_id')

    def test_missing_artifact_retained_without_inference(self):
        fixture=self.fixture();meta,cell,unit,instruction,rendered,header,hashes,entry,*_=fixture
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);task=root/'packs'/meta['task_id'];task.mkdir(parents=True);(task/'instruction.md').write_bytes(instruction)
            write(root/'criterion/cells'/unit['config'].replace('|','__')/(cell['cell']+'.json'),rendered)
            artifacts=root/'artifacts';artifacts.mkdir();entry['expected_cells']=1
            with patch.object(h,'PRIVATE',root),patch.object(self.ctl,'cli',side_effect=AssertionError('transport')):
                rows=h.harvest_run({'frozen_task_ids':[meta['task_id']]},entry,unit,{meta['task_id']:meta},{cell['cell']:cell},
                     {'pack':str(root/'packs')},self.pack,self.writer,lambda *a: self.fail('parser used without artifact'),artifacts,{})
            self.assertEqual(len(rows),1);self.assertFalse(rows[0]['accepted'])
            self.assertFalse(rows[0]['prior_verdict_absence_established'])
            self.assertEqual(rows[0]['acceptance_reason'],'ARTIFACT_ABSENT_UNRESOLVED')
            (artifacts/meta['task_id']/'other').mkdir(parents=True)
            paths=[meta['task_id']+'/receipt.json',meta['task_id']+'/other/receipt.json']
            for name in paths:(artifacts/name).write_bytes(b'{}')
            with patch.object(h,'PRIVATE',root):
                rows=h.harvest_run({'frozen_task_ids':[meta['task_id']]},entry,unit,{meta['task_id']:meta},{cell['cell']:cell},
                     {'pack':str(root/'packs')},self.pack,self.writer,lambda *a:self.fail('parser called'),artifacts,dict.fromkeys(paths))
            self.assertEqual(rows[0]['acceptance_reason'],'DUPLICATE_OR_UNSUPPORTED_OUTER_RECEIPT')

    def test_trajectory_cost_is_not_a_verdict_and_partial_cost_is_unknown(self):
        trajectory={'session_id':'t','trajectory_id':'t:terminus-offline','agent':{'name':'terminus-2','model_name':'m'},
                    'final_metrics':{'total_cost_usd':.2,'extra':{'metric_availability':{'cost_usd':{'reported_responses':2,'total_responses':2}}}}}
        result=h.recover_trajectory('t',{'selector':'m'},encoded(trajectory))
        self.assertEqual(result['cost_usd'],.2);self.assertFalse(result['accepted']);self.assertNotIn('score',result)
        trajectory['final_metrics']['extra']['metric_availability']['cost_usd']['reported_responses']=1
        self.assertIsNone(h.recover_trajectory('t',{'selector':'m'},encoded(trajectory))['cost_usd'])
        for field in ('session_id','trajectory_id','agent'):
            bad=copy.deepcopy(trajectory);bad[field]={} if field=='agent' else 'wrong'
            with self.assertRaises(h.InvalidEvidence):h.recover_trajectory('t',{'selector':'m'},encoded(bad))

    def test_collection_hashes_run_mask_and_immutable_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);ledger=root/'ledger';ledger.write_bytes(b'original-ledger');packs=root/'packs';packs.write_bytes(b'frozen-packs')
            manifest={'scientific_run_id':RUN_ID,'new_measured_calls':0,'source_ledger_sha256':sha(ledger.read_bytes()),
                      'frozen_packs_sha256':sha(packs.read_bytes()),'runs':[{'run_id':'r','key':'cfg@main','config':'cfg'}]}
            progress={'scientific_run_id':RUN_ID,'stage':'RAW_COLLECTION_COMPLETE_STRICT_HARVEST_PENDING_NOT_EXPERIMENT_COMPLETE','completed':[{'run_id':'r'}]}
            metadata={'rows':[{'run_id':'r'}]}
            completion={'scientific_run_id':RUN_ID,'new_inference_calls':0,'runs':1}
            for key,name,value in [('manifest_sha256','collection_manifest.json',manifest),('progress_sha256','progress.json',progress),('metadata_summary_sha256','metadata_summary.json',metadata)]:
                write(root/name,value);completion[key]=sha((root/name).read_bytes())
            write(root/'collection_completion_receipt.json',completion)
            h.verify_collection(root,ledger,packs)
            for path in (ledger,packs,root/'collection_manifest.json',root/'progress.json',root/'metadata_summary.json'):
                original=path.read_bytes();path.write_bytes(original+b' ')
                with self.subTest(path=path.name),self.assertRaises(h.InvalidEvidence):h.verify_collection(root,ledger,packs)
                path.write_bytes(original)
            metadata['rows']=[{'run_id':'other'}];write(root/'metadata_summary.json',metadata)
            completion['metadata_summary_sha256']=sha((root/'metadata_summary.json').read_bytes());write(root/'collection_completion_receipt.json',completion)
            with self.assertRaisesRegex(h.InvalidEvidence,'RUN_MASK'):h.verify_collection(root,ledger,packs)

    def test_indexed_files_missing_duplicate_changed_and_unindexed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);artifact=root/'receipt.json';artifact.write_bytes(b'original')
            row={'path':'receipt.json','bytes':8,'sha256':sha(b'original')}
            write(root/'files_sha256.json',[row]);write(root/'identity_receipt.json',{})
            h.verified_files(root)
            artifact.unlink()
            with self.assertRaisesRegex(h.InvalidEvidence,'MISSING'):h.verified_files(root)
            artifact.write_bytes(b'changed!')
            with self.assertRaisesRegex(h.InvalidEvidence,'HASH'):h.verified_files(root)
            artifact.write_bytes(b'original');write(root/'files_sha256.json',[row,row])
            with self.assertRaisesRegex(h.InvalidEvidence,'DUPLICATE'):h.verified_files(root)
            write(root/'files_sha256.json',[row]);(root/'extra').write_text('unknown')
            with self.assertRaisesRegex(h.InvalidEvidence,'UNINDEXED'):h.verified_files(root)


class CriterionDependencyTests(unittest.TestCase):
    def test_stale_live_waits_then_valid_finishes_dead_mismatch_and_substantive_fail(self):
        import after_full_campaign as continuation
        from run_offline import identity
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);results=root/'results';results.mkdir()
            write(results/'criterion_analysis_provenance.json',{'old':'same-run receipt'})
            processes=[]
            try:
                for name in ('run_offline.py','after_criterion.py'):
                    (root/name).write_text('import time\ntime.sleep(30)\n')
                    processes.append(subprocess.Popen([sys.executable,name],cwd=root))
                state={'run_id':RUN_ID,'kind':'deterministic_offline','state':'RUNNING',
                       'command':[sys.executable,'after_criterion.py'],'driver':identity(processes[0].pid),'child':identity(processes[1].pid)}
                write(root/'runtime/criterion_followthrough.json',state)
                with patch.multiple(continuation,ROOT=root,RESULTS=results),patch.object(continuation,'verify_criterion_receipt') as verify:
                    verify.side_effect=continuation.StaleCriterionProvenance('old inputs')
                    self.assertFalse(continuation.criterion_ready())
                    verify.side_effect=None;self.assertTrue(continuation.criterion_ready())
                    verify.side_effect=ValueError('substantive corrupt evidence')
                    with self.assertRaisesRegex(ValueError,'substantive'):continuation.criterion_ready()
                    verify.side_effect=continuation.StaleCriterionProvenance('old inputs')
                    wrong=copy.deepcopy(state);wrong['run_id']='other';write(root/'runtime/criterion_followthrough.json',wrong)
                    with self.assertRaisesRegex(ValueError,'ownership'):continuation.criterion_ready()
                    write(root/'runtime/criterion_followthrough.json',state)
                    processes[1].terminate();processes[1].wait()
                    with self.assertRaisesRegex(RuntimeError,'explicit recovery'):continuation.criterion_ready()
            finally:
                for process in processes:
                    if process.poll() is None:process.terminate()
                    process.wait()


if __name__=='__main__':unittest.main()
