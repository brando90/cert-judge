#!/bin/bash
# TLDR: Sherlock: pack the harvests, raw outputs and meta into $B/e58_results.tgz with MANIFEST.sha256 and the tarball sha256.
# usage: bash collect.sh   (dev srun is fine: it only reads and tars)
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd $B
e58_py $CODE/scripts/harvest_lib.py --run $RUN > $RUN/harvest_summary.jsonl
cp -f jobs.txt $RUN/jobs.txt 2>/dev/null || true
mkdir -p $RUN/logs && cp -f logs/*.log $RUN/logs/ 2>/dev/null || true
( cd $RUN && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 sha256sum > MANIFEST.sha256 )
tar czf e58_results.tgz -C $B runs/$(basename $RUN)
sha256sum e58_results.tgz | tee e58_results.tgz.sha256
