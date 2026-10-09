"""Retrieve only exact named frozen Git blobs into ignored dependency storage."""
from pathlib import Path
import subprocess
from e47_adapter import ROOT,REPO,VENDOR,RESULTS,read,sha,write

def main():
    receipt=read(RESULTS/'frozen_dependency_hashes.json');rows=[]
    for name,digest in receipt['files'].items():
        if name=='../information_properties_addeba2.py':
            commit=receipt['owner_commit'];source='py_src/cert_judge/information_properties.py'
        else:
            commit=receipt['e39_commit'];source='experiments/39_label_free_proxy_index_train_val_test_over_judge_families/'+('scripts/' if name.endswith('.py') else 'results/')+name
        data=subprocess.check_output(['git','show',commit+':'+source],cwd=REPO)
        if sha(data)!=digest:raise ValueError('frozen source mismatch '+source)
        path=VENDOR/name;path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and path.read_bytes()!=data:raise ValueError('existing frozen file differs; investigate before replacing '+name)
        if not path.exists():path.write_bytes(data)
        rows.append({'source_commit':commit,'source_path':source,'sha256':digest})
    quote_source='experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results/QUOTE.json'
    data=subprocess.check_output(['git','show',receipt['e39_commit']+':'+quote_source],cwd=REPO);path=VENDOR/'QUOTE.json'
    if path.exists() and path.read_bytes()!=data:raise ValueError('historical quote differs')
    if not path.exists():path.write_bytes(data)
    rows.append({'source_commit':receipt['e39_commit'],'source_path':quote_source,'sha256':sha(data)})
    write(RESULTS/'frozen_vendor_retrieval.json',{'files':rows,'verdict':'PASS','provider_calls':0,'source_traversal':'exact named Git blobs only'})
    print('Verified frozen Git blobs:',len(rows))

if __name__=='__main__':main()
