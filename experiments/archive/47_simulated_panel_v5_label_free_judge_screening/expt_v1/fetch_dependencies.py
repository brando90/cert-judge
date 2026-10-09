"""Read only exact named, pinned prompt/transport dependencies; never load labels."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parent
REV = 'ccd86d467fd7577826c4b549df2c532bf43b1892'
X100 = 'experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test'
X103 = 'experiments/103_single_call_baselines_all_models_vbv1_vbv2_valkyrie_validated_fsc_judge'
X75 = 'experiments/75_J1_validating_formal_spec_judge_train_val_test'
GATE = 'experiments/95_full_vb_860ish_agent_gpt6_luna_llm_judge_gpt6_sol/tc_gateway/canonical'
ALLOWLIST = [X100+'/scripts/'+n for n in ('common.py','prompts.py')]+[
    GATE+'/rubric.py', GATE+'/lean_public_context.py', 'scripts/scsc/kernel_axioms.py',
    'py_src/veribench_prompts/human_judgements_prompt.md',
    X75+'/scripts/run_stage_a.py', X75+'/scripts/run_judge_tranche.py',
    X103+'/scripts/valkyrie_judge_agent/judge_call.py',
    X103+'/scripts/judge_pack.py',
    X103+'/scripts/vb_service_single_call/main.py',
    X103+'/scripts/vb_service_single_call/single_call_service.py',
    X103+'/scripts/vb_service_single_call/veribench_valkyrie_service.py',
    X103+'/scripts/valkyrie_judge_agent/contract.yaml',
    X103+'/scripts/valkyrie_judge_agent/setup.sh',
    X103+'/results/agent_bundle_judge.json',
]

def fetch(paths=ALLOWLIST):
    manifest_path = ROOT/'results/dependency_allowlist.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'source_commit':REV,'files':{}}
    for name in paths:
        assert name in ALLOWLIST
        data = subprocess.check_output(['git','-C',str(ROOT/'sources/veribench_v5'),'show',REV+':'+name])
        path = ROOT/'private/dependencies'/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        manifest['files'][name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'purpose':'exact frozen renderer/parser/transport dependency; no historical item loader is invoked'}
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    print('Retrieved',len(paths),'exact pinned dependency files; zero calls.')

if __name__ == '__main__':
    fetch()
