#!/usr/bin/env bash
set -euo pipefail
cd /tmp/brando9-cj-recovery-1007/cert-judge
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
# Serialize scientific jobs; do not duplicate the running cached comparison.
while [ ! -f /tmp/brando9-cj-recovery-1007/job-cached-1/completion.json ]; do sleep 5; done
python3 - <<'PY'
import json
assert json.load(open('/tmp/brando9-cj-recovery-1007/job-cached-1/completion.json'))['exit_code']==0
PY
python3 experiments/45_five_rater_cached_selection_task_split_and_behavioral_audit/scripts/legacy.py --veribench /tmp/brando9-cj-recovery-1007/veribench
