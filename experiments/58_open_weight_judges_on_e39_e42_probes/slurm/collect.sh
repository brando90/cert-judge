#!/bin/bash
# TLDR: collect experiment 58's results for download: harvests (E39 schema), raw model outputs, meta (engine, sampling, timing), job
# ids and the logs, into ~/e58/e58_results.tgz with a sha256 per file (MANIFEST.sha256) and the tarball's own .sha256.
# usage: bash collect.sh        (safe to run while jobs still run: it packs what exists and says what is missing)
set -euo pipefail
source "$(dirname "$0")/env.sh"
source $FS_HF/bin/activate
cd $E58_HOME
python $CODE/scripts/harvest_lib.py --run $RUN > $RUN/harvest_summary.jsonl
python - <<PY
import glob, json, os
sys_path = "$CODE/scripts"
import sys; sys.path.insert(0, sys_path)
import e58
miss = [(x, m, p) for x in e58.EXPS for m in e58.MODEL_ORDER for p in e58.PROMPT_ORDER
        if not os.path.exists("$RUN/harvest/%s/%s.json" % (x, e58.fs(e58.config_id(m, p))))]
print("harvests present: %d of %d; missing: %d" % (len(e58.EXPS) * len(e58.MODEL_ORDER) * len(e58.PROMPT_ORDER) - len(miss), len(e58.EXPS) * 117, len(miss)))
json.dump(miss, open("$RUN/MISSING.json", "w"))
PY
cp -f job_ids.txt $RUN/job_ids.txt 2>/dev/null || true
mkdir -p $RUN/logs && cp -f logs/*.log $RUN/logs/ 2>/dev/null || true
( cd $RUN && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 sha256sum > MANIFEST.sha256 )
tar czf e58_results.tgz -C $E58_HOME runs/$(basename $RUN)
sha256sum e58_results.tgz | tee e58_results.tgz.sha256
ls -l e58_results.tgz
