"""Incomplete/tampered ladder fixtures must fail even with valid=True rows."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from e47_adapter import ROOT, VENDOR, sha, module
import verify_probe_artifacts as gate

BUILDER=ROOT/'probe_builder_schema_snapshot.py.txt'


class ProbeArtifactTests(unittest.TestCase):
    def fixture(self, root):
        transforms=gate.load_transforms()
        good='theorem a : True := by trivial\ntheorem b : True := by trivial\n'
        bad='-- deliberate timeout fixture\ntheorem c : True := by trivial\n'
        reference={'task':'task','harbor':'task','actual_sha256':sha(good.encode()),'code':good}
        candidates=[{'item':'G01__task','task':'task','group':'G01','harbor':'task','blank':False,'source_status':'verified','actual_sha256':sha(good.encode()),'code':good},
                    {'item':'G02__task','task':'task','group':'G02','harbor':'task','blank':False,'source_status':'verified','actual_sha256':sha(bad.encode()),'code':bad},
                    {'item':'G03__task','task':'task','group':'G03','harbor':'task','blank':True,'source_status':'declared_blank','actual_sha256':None}]
        inputs=root/'private/probes_worker/input_bytes';(inputs/'references').mkdir(parents=True);(inputs/'references/task.lean').write_text(good)
        for row in candidates[:2]:
            folder=inputs/'candidates'/row['group'];folder.mkdir(parents=True);(folder/'task.lean').write_text(row['code'])
        records={};artifacts=[]
        class FixtureCompiler:
            def compile(self, code):
                digest=sha(code.encode());failed='deliberate timeout fixture' in code
                row={'sha256':digest,'ok':not failed,'returncode':124 if failed else 0,'output':'TIMEOUT after 900s' if failed else '',
                     'output_sha256':sha(b'terminal diagnostics'),'finished_utc':'fixture-time','environment':'pinned','reused':False}
                records[digest]=row;return row
        def artifact(kind,key,level,code):
            relative=f'private/probes_worker/artifacts/{kind}/{key}__L{level}.lean';p=root/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(code)
            row={'kind':kind,'key':key,'level':level,'sha256':sha(code.encode()),'private_relpath':relative};artifacts.append(row);return row
        builder=gate.frozen_builder_functions(BUILDER.read_bytes(),transforms,artifact)
        rows,_=builder['build_one']('task',reference,candidates,FixtureCompiler())
        manifest={'run_id':gate.PROBE_RUN_ID,'frozen_transform':{'sha256':sha((VENDOR/'probes.py').read_bytes()),'kinds':{'ident':0,'blank':0,'ms_gold':4,'ms_cand':3,'bm_gold':4}},
                  'rows':rows,'counts':builder['counts'](rows),'private_artifacts':artifacts}
        source={'references':[{k:v for k,v in reference.items() if k!='code'}],'candidates':[{k:v for k,v in c.items() if k!='code'} for c in candidates]}
        return source,manifest,list(records.values())

    def verify(self, root, source, manifest, cache):
        with patch('subprocess.run',side_effect=AssertionError('compiler/transport must not run')):
            return gate.verify_transformed_artifacts(source,manifest,cache,'pinned',root,BUILDER)

    def test_full_outcome_includes_terminal_failure_and_unavailable_levels(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source,manifest,cache=self.fixture(root)
            result=self.verify(root,source,manifest,cache)
            self.assertEqual(result['expected_rows'],15);self.assertEqual(result['verified_artifacts'],4)
            self.assertEqual(result['compiler_calls'],0);self.assertEqual(result['unavailable_rows'],6)
            failed=next(r for r in manifest['rows'] if r['kind']=='crit' and r['item']=='G02__task')
            self.assertTrue(failed['valid']);self.assertEqual(failed['candidate_compile']['returncode'],124)

    def test_omitted_duplicate_swapped_or_forged_level_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source,manifest,cache=self.fixture(root)
            bad=copy.deepcopy(manifest);bad['rows']=[r for r in bad['rows'] if not (r['kind']=='ms_cand' and r['item']=='G01__task' and r['level']==2)]
            with self.assertRaisesRegex(ValueError,'incomplete'):self.verify(root,source,bad,cache)
            bad=copy.deepcopy(manifest);bad['rows'].append(copy.deepcopy(bad['rows'][0]))
            with self.assertRaisesRegex(ValueError,'duplicate'):self.verify(root,source,bad,cache)
            for field,value in [('level',99),('source_sha256','wrong'),('valid',False),('item','G99__task')]:
                bad=copy.deepcopy(manifest);row=next(r for r in bad['rows'] if r['kind']=='ms_cand' and r['item']=='G01__task');row[field]=value
                with self.subTest(field=field),self.assertRaises(ValueError):self.verify(root,source,bad,cache)

    def test_tampered_missing_artifact_wrong_environment_and_diagnostic(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source,manifest,cache=self.fixture(root)
            path=root/manifest['private_artifacts'][0]['private_relpath'];original=path.read_bytes();path.write_bytes(original+b'-- tampered\n')
            with self.assertRaisesRegex(ValueError,'bytes differ'):self.verify(root,source,manifest,cache)
            path.unlink()
            with self.assertRaises(FileNotFoundError):self.verify(root,source,manifest,cache)
            path.write_bytes(original)
            bad=copy.deepcopy(cache)
            for row in bad:row['environment']='other compiler'
            with self.assertRaises(gate.MissingCompileEvidence):self.verify(root,source,manifest,bad)
            bad=copy.deepcopy(manifest);bad['rows'][0]['compile']['output_sha256']='forged'
            with self.assertRaisesRegex(ValueError,'terminal cache chain'):self.verify(root,source,bad,cache)


if __name__=='__main__':unittest.main()
