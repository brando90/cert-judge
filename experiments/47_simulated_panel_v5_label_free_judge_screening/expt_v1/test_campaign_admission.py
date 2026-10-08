"""Exercise real frozen admission with a fake CLI; no network/model calls."""
import contextlib
import io
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from e47_adapter import frozen,write,read
from campaign_driver import strict_harvest,reconcile_ambiguous_admission

class AdmissionTests(unittest.TestCase):
    def test_collection_failure_is_not_a_scientific_failure(self):
        ctl=SimpleNamespace(harvested=lambda *args:None)
        with self.assertRaisesRegex(RuntimeError,'recover existing run receipts'):
            strict_harvest(ctl,'criterion','cfg','smoke')

    def test_archived_final_view_adopts_without_network_and_rejects_wrong_run(self):
        from harvest_transport import install
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);entry={'run_id':'owned-run','benchmark':'owned-benchmark','config':'cfg','part':'smoke'}
            original=root/'cfg_smoke_artifacts/owned-benchmark.json'
            write(original,{'benchmark_id':'owned-run','benchmark_name':'owned-benchmark','status':'FINISHED','evaluation_results':{'task':{'score':.8}}})
            (root/'cfg_smoke_download.log').write_text('run output owned-run rc=0\n')
            ctl=SimpleNamespace(RAW=root,load_state=lambda:{'runs':{'cfg@smoke':entry}},TERMINAL_RUN={'finished'},pack_rows=lambda *a:[{'task_id':'task'}],rows_of=lambda p:read(p)['evaluation_results'])
            install(ctl);results,artifacts=ctl.download('cfg@smoke','owned-run')
            self.assertEqual(results.read_bytes(),original.read_bytes())
            payload=read(original);payload['benchmark_id']='different-run';write(original,payload)
            with self.assertRaisesRegex(ValueError,'identity mismatch'):ctl.download('cfg@smoke','owned-run')

    def test_lost_start_receipt_adopts_exact_remote_run_without_new_start(self):
        import re,json
        with tempfile.TemporaryDirectory() as directory:
            entry={'phase':'admitting','benchmark':'owned','agent':'pinned','selector':'pinned-model','command':['run','start','--label','cj39-main-test']}
            state={'runs':{'cfg@main':entry}};commands=[]
            def cli(args,timeout=600):
                commands.append(args)
                return SimpleNamespace(returncode=0,stdout=json.dumps({'runs':[{'run_id':'11111111-1111-1111-1111-111111111111'}]}))
            ctl=SimpleNamespace(JUDGE=Path(directory),UUID_RE=re.compile(r'[a-f0-9-]{36}'),load_state=lambda:state,save_state=lambda state:None,cli=cli)
            reconcile_ambiguous_admission(ctl,'cfg','main','criterion')
            self.assertEqual(entry['phase'],'running');self.assertEqual(len(commands),1)
            self.assertEqual(commands[0][:2],['run','list']);self.assertIn('cj47-criterion-main-test',commands[0])

    def test_admission_is_written_before_cli_and_never_replayed(self):
        e,_,_,ctl=frozen();cfg='opus55x|H2';calls=[]
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);out=root/'results';private=root/'private';judge=private/'judge'
            unit={'config':cfg,'model_key':'opus55x','pack_flavor':'single_call','harness':'vb103_judge','max_tokens':32000,'kwargs':{},'selectors':['exact-selector'],'substitutes':[]}
            write(out/'panel.json',{'units':[unit]});write(out/'agent_bundle_check.json',{'verdict':'PASS','downloaded_now_sha256':{'judge_call.py':'frozen'}})
            write(out/'packs.json',{'verdict':'PASS','packs':{'opus55x':{'per_config':{cfg:{'cells':[{'task_id':'declared-only'}]}}}}})
            write(private/'deployment_opus55x.json',{'benchmark':'owned-benchmark','service_pid':1})
            def fake_cli(args,timeout=1800):
                state=read(judge/'state.json');self.assertEqual(state['runs'][cfg+'@main']['phase'],'admitting')
                self.assertEqual((judge/'task_ids_opus55x__H2_main.txt').read_text(),'declared-only\n');calls.append(args)
                return SimpleNamespace(returncode=0,stdout='11111111-1111-1111-1111-111111111111',stderr='')
            with patch.multiple(e,PRIVATE=private,RESULTS=out),patch.multiple(ctl,JUDGE=judge,STATE=judge/'state.json',RAW=judge/'raw',cli=fake_cli),contextlib.redirect_stdout(io.StringIO()):
                ctl.admit(cfg,'main',20);ctl.admit(cfg,'main',20)
            self.assertEqual(len(calls),1);self.assertIn('exact-selector',calls[0])

    def test_raw_429_remains_infrastructure_after_parseable_second_response(self):
        cfg='opus55x|H2'
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);raw=root/'raw';judge=root/'judge'
            write(raw/'opus55x__H2_main_artifacts/task/receipt.json',{'task_id':'task','status':'measured','requests_sent':2,'http_status':429})
            blob={'cells':[{'cell':'c','task_id':'task','status':'measured','score':.5,'prompt_sha256_delivered':'p','agent_status':'measured'}]}
            ctl=SimpleNamespace(RAW=raw,JUDGE=judge,harvested=lambda *args:blob,pack_rows=lambda *args:[{'cell':'c','prompt_sha256':'p'}],unit_of=lambda *args:{'pack_flavor':'single_call'})
            result=strict_harvest(ctl,'criterion',cfg,'main')
            self.assertEqual(result['accepted_count'],0);cell=result['cells'][0]
            self.assertEqual(cell['status'],'unmeasured_infra');self.assertEqual(cell['acceptance_reason'],'HTTP_429_INFRASTRUCTURE_FAILURE')
            self.assertEqual(cell['requests_sent'],2);self.assertTrue(cell['raw_transport_receipt_sha256'])

    def test_watchdog_respects_driver_lock_before_new_receipt_arrives(self):
        import fcntl
        from watch_campaign import driver_lock_held
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'driver.lock'
            with path.open('a') as held:
                fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
                self.assertTrue(driver_lock_held(path))
            self.assertFalse(driver_lock_held(path))

if __name__=='__main__':unittest.main()
