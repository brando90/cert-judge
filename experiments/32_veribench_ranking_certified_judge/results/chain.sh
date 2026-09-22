#!/bin/bash
# exp32 chain: run the ranking runner to completion, then the property suite. Detached via setsid so tool-shell
# cleanup cannot kill it. Resume-safe: both runners skip cached cells.
cd /Users/brandomiranda/cert-judge || exit 1
PY=/Users/brandomiranda/uv_envs/cert-judge/bin/python3
E=experiments/32_veribench_ranking_certified_judge
echo "$(date -u +%FT%TZ) chain start pid $$"
$PY $E/run_ranking_cli.py --workers 8 >> $E/results/run_stdout.log 2>&1
echo "$(date -u +%FT%TZ) ranking runner exited rc=$?"
$PY $E/run_property_suite_cli.py --workers 8 >> $E/results/property_stdout.log 2>&1
echo "$(date -u +%FT%TZ) property suite exited rc=$?"
