"""Verify exact existing Valkyrie bundles without inference or provider keys."""
import os
from pathlib import Path
import shutil
import sys
from e47_adapter import ROOT,PRIVATE,RESULTS,VENDOR,read,write,frozen,module,sha

def main():
    e,_,_,ctl=frozen()
    config=PRIVATE/'valkyrie.yaml'
    if not config.exists():
        source=Path('/dfs/scratch0/brando9/.config/valkyrie/valkyrie.yaml')
        shutil.copyfile(source,config);config.chmod(0o600)
    bundle=module('e47_verify_bundle',VENDOR/'verify_bundle.py')
    sys.argv=['verify_bundle'];rc=bundle.main()
    if rc:raise RuntimeError('single-call bundle differs from frozen validated transport')
    old=read(VENDOR/'agent_harness.json');harness=module('e47_verify_agent_harness',VENDOR/'verify_agent_harness.py')
    sys.argv=['verify_agent_harness','--candidates',old['agent']];rc=harness.main()
    got=read(RESULTS/'agent_harness.json')
    equal=got.get('contract_sha256')==old['contract_sha256'] and got.get('bundle_sha256')==old['bundle_sha256']
    got.update(historical_contract_sha256=old['contract_sha256'],identical_to_historical_bundle=equal)
    if not equal:got['verdict']='FAIL'
    write(RESULTS/'agent_harness.json',got)
    if rc or not equal:raise RuntimeError('agent harness differs from historical bytes; no replacement is authorized')
    print('Exact historical single-call and Terminus2 bundles PASS; zero inference calls.')

if __name__=='__main__':main()
