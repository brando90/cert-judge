#!/usr/bin/env bash
# TLDR: Experiment 43's durable worker on hosted Valkyrie (10-14-2026): runs `transport_hosted.py attack all`
# (`attack.py all` on the hosted transport: pilot -> gates -> full run -> post) until it finishes, resuming after a
# crash (every batch is idempotent; a request with a verdict is never re-admitted). Stops on private/STOP, on a failed
# pilot gate (exit 3), or when private/ATTACK_DONE exists. worker_loop.sh is kept as run on 09-30-2026 (pre-hosted).
set -u
cd "$(dirname "$0")/.."
PY=${E43_PYTHON:-/lfs/skampere1/0/brando9/vb103_venv/bin/python}
mkdir -p private/tmp
export PYTHONDONTWRITEBYTECODE=1 PATH="$HOME/.elan/bin:$PATH" TMPDIR="$PWD/private/tmp"   # the shared root disk (/tmp) can fill up
mkdir -p private/logs
while [ ! -e private/STOP ] && [ ! -e private/ATTACK_DONE ]; do
  echo "$(date -u +%FT%TZ) worker: transport_hosted.py attack all" >> private/logs/worker.log
  "$PY" scripts/transport_hosted.py attack all >> private/logs/worker.log 2>&1
  rc=$?
  echo "$(date -u +%FT%TZ) worker: exit $rc" >> private/logs/worker.log
  if [ $rc -eq 0 ]; then touch private/ATTACK_DONE; break; fi
  if [ $rc -eq 3 ]; then echo "pilot gates failed; see results/pilot.json" >> private/logs/worker.log; break; fi
  sleep 120
done
