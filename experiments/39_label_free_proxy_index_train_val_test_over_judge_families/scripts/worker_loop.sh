#!/usr/bin/env bash
# TLDR: Experiment 39's durable execution owner — run the stage driver once a minute inside its tmux session
# until it writes private/DONE, so a coordinator session ending never stops a healthy judging campaign.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${E39_PYTHON:-/lfs/skampere1/0/brando9/vb103_venv/bin/python}"
mkdir -p private/logs
while true; do
  if [ -f private/DONE ]; then
    echo "$(date -u +%FT%TZ) DONE marker present; worker exiting" | tee -a private/logs/worker.log
    exit 0
  fi
  if [ -f private/STOP ]; then
    echo "$(date -u +%FT%TZ) STOP marker present; worker exiting" | tee -a private/logs/worker.log
    exit 0
  fi
  "$PY" scripts/driver.py --once --concurrency "${E39_CONCURRENCY:-20}" >> private/logs/worker.log 2>&1
  tail -1 private/logs/worker.log
  sleep 60
done
