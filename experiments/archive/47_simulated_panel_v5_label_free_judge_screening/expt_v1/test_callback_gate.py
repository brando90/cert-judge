"""Decisive callback admission cases, with transport forbidden on rejection."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import callback_gate as g
from e47_adapter import POOL, RUN_ID, sha, write

class CallbackAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.rt=self.root/'runtime'; self.rt.mkdir()
        self.admission=self.root/'results/probes/admission_manifest.json'
        write(self.admission,{'run_id':RUN_ID,'phase':'probes','state':'FROZEN','configurations':list(POOL)})
        self.digest=sha(self.admission.read_bytes())
        config=self.root/'private/probes/valkyrie.yaml';config.parent.mkdir(parents=True);config.write_text('fixture')
        (self.root/'callback_watch.py').write_text('fixture observer')
        observer=sha((self.root/'callback_watch.py').read_bytes())
        self.identities={}; rows=[]
        for i,m in enumerate(g.MODELS):
            deployment=config.parent/('deployment_'+m+'.json');deployment.write_text('{}')
            ids={k:{'pid':1+i*2+n,'boot_id':'boot','start_ticks':'42','cwd':'/fixture','argv':['fixture']} for n,k in enumerate(('service','tunnel'))}
            self.identities.update({v['pid']:v for v in ids.values()})
            rows.append({'model':m,'healthy':True,'codes':{'local_authenticated':200,'local_unauthenticated':401,'tunnel_authenticated':200,'tunnel_unauthenticated':401},'identity':{'deployment_sha256':sha(deployment.read_bytes()),**ids}})
        self.binding={'run_id':RUN_ID,'phase':'probes','initial_observed_epoch':900,'files':{str(self.admission):self.digest,str(config):sha(config.read_bytes())},'models':{r['model']:r['identity'] for r in rows},'observer_sha256':observer}
        write(self.rt/'callback_binding.json',self.binding)
        self.observation={'run_id':RUN_ID,'phase':'probes','state':'HEALTHY','bound':True,'observed_epoch':990,'observation_kind':'monitor','models':rows,'binding_sha256':sha((self.rt/'callback_binding.json').read_bytes()),'observer_sha256':observer}
        write(self.rt/'callback_observation.json',self.observation)
        self.proc=patch.object(g,'process',side_effect=lambda pid:self.identities[pid]);self.proc.start();self.addCleanup(self.proc.stop)
    def run_gate(self):return g.require_callback_ready(self.root,self.digest,now=1000)
    def test_valid_complete_bound_observation(self):
        self.assertEqual(self.run_gate()['processes_verified'],8)
    def test_all_observation_bindings_fail_closed(self):
        mutations=[('run_id','other'),('phase','criterion'),('state','CALLBACK_ATTENTION'),('bound',False),('observed_epoch',0),('observed_epoch',1001),('observed_epoch',float('nan')),('observed_epoch',float('inf')),('observed_epoch',900),('observation_kind','bind'),('binding_sha256','wrong'),('observer_sha256','wrong')]
        for key,value in mutations:
            with self.subTest(key=key,value=value):
                row=copy.deepcopy(self.observation);row[key]=value
                (self.rt/'callback_observation.json').write_text(json.dumps(row))
                with self.assertRaises((ValueError,KeyError)):self.run_gate()
        write(self.rt/'callback_observation.json',self.observation)
    def test_missing_corrupt_and_duplicate_models(self):
        for rows in [[],self.observation['models'][:3],[self.observation['models'][0]]*4]:
            row=copy.deepcopy(self.observation);row['models']=rows;write(self.rt/'callback_observation.json',row)
            with self.assertRaises(ValueError):self.run_gate()
        (self.rt/'callback_observation.json').write_text('invalid')
        with self.assertRaises(ValueError):self.run_gate()
        (self.rt/'callback_observation.json').unlink()
        with self.assertRaises(FileNotFoundError):self.run_gate()
    def test_health_and_identity_mutations(self):
        for field in ('local_authenticated','local_unauthenticated','tunnel_authenticated','tunnel_unauthenticated'):
            row=copy.deepcopy(self.observation);row['models'][0]['codes'][field]=530;write(self.rt/'callback_observation.json',row)
            with self.assertRaises(ValueError):self.run_gate()
        row=copy.deepcopy(self.observation);row['models'][0]['identity']['service']['boot_id']='other';write(self.rt/'callback_observation.json',row)
        with self.assertRaises(ValueError):self.run_gate()
        write(self.rt/'callback_observation.json',self.observation)
        self.identities[1]={**self.identities[1],'start_ticks':'43'}
        with self.assertRaises(ValueError):self.run_gate()
    def test_changed_frozen_bytes(self):
        for path in [self.admission,self.root/'callback_watch.py',self.root/'private/probes/valkyrie.yaml',self.root/'private/probes/deployment_opus55x.json']:
            before=path.read_bytes();path.write_bytes(before+b' ')
            with self.assertRaises(ValueError):self.run_gate()
            path.write_bytes(before)
    def test_invalid_manifest_even_when_hashes_agree(self):
        row=json.loads(self.admission.read_text());row['configurations']=list(POOL)[:-1];write(self.admission,row)
        self.digest=sha(self.admission.read_bytes());self.binding['files'][str(self.admission)]=self.digest;write(self.rt/'callback_binding.json',self.binding)
        self.observation['binding_sha256']=sha((self.rt/'callback_binding.json').read_bytes());write(self.rt/'callback_observation.json',self.observation)
        with self.assertRaises(ValueError):self.run_gate()
    def test_late_rejection_is_proven_no_transport(self):
        argv=['run','start'];entry={'phase':'admitting','command':argv};ctl=Mock();ctl.load_state.return_value={'runs':{'x':entry}}
        transport=Mock(side_effect=AssertionError('transport must never run'))
        with patch.object(g,'require_callback_ready',side_effect=ValueError('stale')):
            with self.assertRaises(ValueError):
                g.before_probe_transport(ctl,self.root,self.digest,argv);transport(argv)
        transport.assert_not_called();ctl.save_state.assert_called_once()
        self.assertEqual(entry['phase'],'admission_blocked_before_transport');self.assertFalse(entry['transport_called'])
    def test_new_admission_stops_after_changed_guard_but_existing_run_adopts(self):
        state={'runs':{}};ctl=Mock();ctl.load_state.return_value=state
        def admit(cfg,part,**kwargs):state['runs'].setdefault(cfg+'@'+part,{'run_id':'existing','phase':'running'})
        ctl.admit.side_effect=admit
        with patch.object(g.time,'time',return_value=1000):
            g.admit_probe(ctl,self.root,self.digest,POOL[0],'main')
            row=copy.deepcopy(self.observation);row['state']='CALLBACK_ATTENTION';write(self.rt/'callback_observation.json',row)
            with self.assertRaises(ValueError):g.admit_probe(ctl,self.root,self.digest,POOL[1],'main')
            self.assertNotIn(POOL[1]+'@main',state['runs'])
            g.admit_probe(ctl,self.root,self.digest,POOL[0],'main')
        self.assertEqual(ctl.admit.call_count,2)
    def test_blocked_pretransport_never_queries_server_or_replays(self):
        import campaign_driver
        state={'runs':{POOL[0]+'@main':{'phase':'admission_blocked_before_transport','transport_called':False}}}
        ctl=Mock();ctl.load_state.return_value=state
        campaign_driver.reconcile_ambiguous_admission(ctl,POOL[0],'main','probes')
        ctl.cli.assert_not_called()
        with self.assertRaises(RuntimeError):g.admit_probe(ctl,self.root,self.digest,POOL[0],'main')
        ctl.admit.assert_not_called()

if __name__=='__main__':unittest.main()
