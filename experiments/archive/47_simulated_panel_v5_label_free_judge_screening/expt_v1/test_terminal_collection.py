import threading
import unittest
from unittest.mock import patch
import collect_terminal_probes as collector

class CollectionWaveTests(unittest.TestCase):
    def test_failure_preserves_healthy_parallel_collections_without_more_dispatch(self):
        barrier=threading.Barrier(3);seen=[];recorded={}
        def collect(ctl,key):
            seen.append(key);barrier.wait(timeout=5)
            if key=='failed':raise RuntimeError('preserved failure')
            return None,None,{'run_id':key}
        entries=[(key,{'config':key}) for key in ('failed','healthy1','healthy2')]
        with patch.object(collector,'collect',collect),self.assertRaisesRegex(RuntimeError,'preserved failure'):
            collector.collect_wave(None,entries,lambda cfg,receipt:recorded.update({cfg:receipt}))
        self.assertEqual(set(seen),{'failed','healthy1','healthy2'})
        self.assertEqual(set(recorded),{'healthy1','healthy2'})
        with patch.object(collector,'collect',side_effect=AssertionError('must not dispatch')),self.assertRaises(ValueError):
            collector.collect_wave(None,entries+[('extra',{'config':'extra'})],lambda *a:None)

if __name__=='__main__':unittest.main()
