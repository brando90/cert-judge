import contextlib
import copy
import http.server
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('watch',Path(__file__).with_name('callback_watch.py'))
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

class GuardTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.e=Path(self.tmp.name)/'experiments/47_simulated_panel_v5_label_free_judge_screening/expt_v1'
  self.r=self.e/'runtime';self.r.mkdir(parents=True)
  private=self.e/'private/probes';private.mkdir(parents=True)
  (private/'valkyrie.yaml').write_text('fixture: no credentials\n')
  self.manifest=self.e/'admission.json';self.manifest.write_text('{"fixture":true}')
  self.rows=[{'model':m,'healthy':True,'codes':{'local_authenticated':200,'local_unauthenticated':401,'tunnel_authenticated':200,'tunnel_unauthenticated':401},'identity':{'service':{'pid':i+1,'start_ticks':'10','boot_id':'a'},'tunnel':{'pid':i+5,'start_ticks':'11','boot_id':'a'}}} for i,m in enumerate(w.MODELS)]
 def main(self,*args):
  with patch('sys.argv',['watch','--experiment',str(self.e),*args]),contextlib.redirect_stdout(io.StringIO()):return w.main()
 def bind(self):
  with patch.object(w,'observe',return_value=copy.deepcopy(self.rows)):
   self.assertEqual(self.main('--bind','--admission',str(self.manifest)),0)
 def test_missing_binding_is_not_a_pass(self):
  self.assertEqual(self.main(),2)
  self.assertFalse((self.r/'callback_binding.json').exists())
 def test_tunnel_530_never_binds(self):
  self.rows[0]['codes']['tunnel_authenticated']=530
  self.rows[0]['healthy']=w.healthy_codes(self.rows[0]['codes'])
  with patch.object(w,'observe',return_value=self.rows):self.assertEqual(self.main('--bind','--admission',str(self.manifest)),1)
  self.assertFalse((self.r/'callback_binding.json').exists())
 def test_unauthenticated_200_is_rejected(self):
  codes=copy.deepcopy(self.rows[0]['codes']);codes['tunnel_unauthenticated']=200
  self.assertFalse(w.healthy_codes(codes))
 def test_changed_manifest_keeps_binding_and_alerts_once(self):
  self.bind();before=(self.r/'callback_binding.json').read_bytes();self.manifest.write_text('{}')
  with patch.object(w,'observe',return_value=self.rows),patch.object(w,'notify') as notify:
   self.assertEqual(self.main('--notify'),1);self.assertEqual(self.main('--notify'),1)
   self.assertEqual(notify.call_count,1)
  self.assertEqual(before,(self.r/'callback_binding.json').read_bytes())
 def test_changed_error_alerts_without_rebinding(self):
  self.bind();rows=copy.deepcopy(self.rows);rows[0]={'model':w.MODELS[0],'healthy':False,'error_type':'ProcessLookupError'}
  with patch.object(w,'observe',return_value=rows),patch.object(w,'notify') as notify:
   self.assertEqual(self.main('--notify'),1);self.assertEqual(notify.call_count,1)
  self.assertEqual(self.main('--bind','--admission',str(self.manifest)),1)
 def test_notification_failure_is_persisted_and_not_retried(self):
  self.bind();self.rows[0]['healthy']=False
  with patch.object(w,'observe',return_value=self.rows),patch.object(w,'notify',side_effect=RuntimeError('fixture private secret')) as notify:
   self.main('--notify');self.main('--notify');self.assertEqual(notify.call_count,1)
  output=(self.r/'callback_observation.json').read_text()
  self.assertIn('RuntimeError',output);self.assertNotIn('fixture private secret',output)
 def test_corrupt_binding_is_durable_sanitized_failure(self):
  (self.r/'callback_binding.json').write_text('private invalid json value')
  with patch.object(w,'notify') as notify:
   self.assertEqual(self.main('--notify'),1);self.assertEqual(self.main('--notify'),1)
   self.assertEqual(notify.call_count,1)
  output=(self.r/'callback_observation.json').read_text()
  self.assertIn('CALLBACK_MONITOR_ERROR',output);self.assertNotIn('private invalid json value',output)
 def test_partial_model_set_cannot_pass(self):
  binding={'files':{}};self.assertEqual(w.verdict(binding,self.rows[:3],{}),'CALLBACK_ATTENTION')
 def test_real_http_redirect_does_not_forward_bearer(self):
  seen=[]
  class Handler(http.server.BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_GET(self):
    seen.append(self.path)
    if self.path=='/health':self.send_response(302);self.send_header('Location','/leak');self.end_headers()
    else:self.send_response(200);self.end_headers()
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
  thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:self.assertEqual(w.health('http://127.0.0.1:'+str(server.server_port)+'/health','fixture-only'),302)
  finally:server.shutdown();server.server_close();thread.join()
  self.assertEqual(seen,['/health'])
 def test_proc_start_identity_and_zombie_detection(self):
  proc=Path(self.tmp.name)/'proc';p=proc/'42';p.mkdir(parents=True);boot=proc/'boot';boot.write_text('boot-a')
  (p/'cwd').symlink_to(self.e);(p/'cmdline').write_bytes(b'python\0fixture\0')
  def stat(start,state='S'):(p/'stat').write_text('42 (worker (safe)) '+state+' '+' '.join(['0']*18+[str(start)]+['0']*4))
  stat(101);a=w.process(42,proc,boot);stat(202);b=w.process(42,proc,boot)
  self.assertNotEqual(a,b);self.assertEqual(b['start_ticks'],'202')
  stat(202,'Z')
  with self.assertRaises(RuntimeError):w.process(42,proc,boot)

if __name__=='__main__':unittest.main()
