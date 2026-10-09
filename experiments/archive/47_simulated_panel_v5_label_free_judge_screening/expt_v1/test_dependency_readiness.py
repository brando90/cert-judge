"""Reject false structural completion independently of probe valid=True."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import dependency_wait as wait
from dependency_wait import verify_terminal_sources

class ReadinessTests(unittest.TestCase):
    def fixture(self):
        rows=[];criteria=[];cache=[]
        for i in range(750):
            group='G%02d'%(i//50+1);task='task%02d'%(i%50);item=group+'__'+task;digest='candidate-'+item
            row={'item':item,'group':group,'task':task,'blank':i>=691,'cand_sha256':digest,'ref_sha256':'reference-'+task}
            rows.append(row);terminal={'ok':i%2==0,'returncode':0 if i%2==0 else 124,'output_sha256':'diagnostic-'+item,'finished_utc':'fixed-terminal-time'}
            criteria.append({'kind':'crit','item':item,'task':task,'valid':True,'source_sha256':digest,'sha256':digest,'candidate_compile':terminal})
            cache.append({'sha256':digest,'environment':'pinned',**terminal})
        source={'candidates':[{**r,'source_status':'verified','actual_sha256':r['cand_sha256']} for r in rows],
                'references':[{'task':'task%02d'%i,'actual_sha256':'reference-task%02d'%i} for i in range(50)]}
        return source,{'rows':criteria},cache,rows

    def test_real_terminal_failure_is_evidence_but_valid_flag_alone_is_not(self):
        source,manifest,cache,expected=self.fixture()
        self.assertEqual(verify_terminal_sources(source,manifest,cache,expected,'pinned')['verified_nonblank'],691)
        manifest['rows'][1].pop('candidate_compile')
        with self.assertRaisesRegex(ValueError,'terminal candidate receipt'):verify_terminal_sources(source,manifest,cache,expected,'pinned')

    def test_unique_count_cannot_hide_duplicate_or_swapped_g01_artifact(self):
        source,manifest,cache,expected=self.fixture()
        original=copy.deepcopy(manifest);manifest['rows'][1]=copy.deepcopy(manifest['rows'][0])
        with self.assertRaisesRegex(ValueError,'duplicate'):verify_terminal_sources(source,manifest,cache,expected,'pinned')
        original['rows'][0]['sha256']=original['rows'][1]['sha256']
        with self.assertRaisesRegex(ValueError,'source hash differs'):verify_terminal_sources(source,original,cache,expected,'pinned')

    def test_receipt_must_match_preserved_compile_cache(self):
        source,manifest,cache,expected=self.fixture();cache[0]['output_sha256']='different-diagnostic'
        with self.assertRaisesRegex(ValueError,'matching preserved compilation'):verify_terminal_sources(source,manifest,cache,expected,'pinned')

    def test_identical_receipt_from_different_toolchain_cannot_establish_readiness(self):
        source,manifest,cache,expected=self.fixture();cache[0]['environment']='different-toolchain'
        with self.assertRaisesRegex(ValueError,'matching preserved compilation'):verify_terminal_sources(source,manifest,cache,expected,'pinned')

    def test_dependency_cannot_wait_on_reused_pid_or_another_run(self):
        with tempfile.TemporaryDirectory() as directory:
            helper=Path(directory);runtime=helper/wait.REL/'runtime';runtime.mkdir(parents=True)
            driver={'pid':99999999,'boot_id':'old-boot','start_ticks':'10'}
            active={'run_id':'cj-e47-probes-10-08-2026-a1','driver':driver}
            path=runtime/'active_jobs.json';path.write_text(json.dumps(active))
            with patch.object(wait,'HELPER',helper),patch.object(wait,'identity',return_value={**driver,'boot_id':'new-boot'}):
                with self.assertRaisesRegex(ValueError,'boot/start identity'):wait.observe()
            active['run_id']='different-study';path.write_text(json.dumps(active))
            with patch.object(wait,'HELPER',helper):
                with self.assertRaisesRegex(ValueError,'run identity'):wait.observe()
            active['run_id']='cj-e47-probes-10-08-2026-a1';path.write_text(json.dumps(active))
            with patch.object(wait,'HELPER',helper),patch.object(wait,'identity',return_value=None):
                self.assertEqual(wait.observe()['state'],'ACTIONABLE_DEPENDENCY_FAILURE')

if __name__=='__main__':unittest.main()
