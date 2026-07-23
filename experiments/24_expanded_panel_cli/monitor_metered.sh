#!/bin/bash
# Waits (up to ~9 min) for all 12 metered configs to write detail_rows.csv, then reports.
# Absolute paths, no arg-passing — robust in background context.
D="$HOME/cert-judge/experiments/24_expanded_panel_cli/results"
META="codex_P2_FORMAL codex_P3_CONCISE codex_P7_STRICT_A codex_P13_HUMAN_ALIGN_STRICT codex_P14_HUMAN_ALIGN_V2 codex_P16_ERIC_COMPARATIVE_TRACKED 4omini_P2_FORMAL 4omini_P3_CONCISE 4omini_P7_STRICT_A 4omini_P13_HUMAN_ALIGN_STRICT 4omini_P14_HUMAN_ALIGN_V2 4omini_P16_ERIC_COMPARATIVE_TRACKED"
for i in $(seq 1 12); do
  dc=0
  for t in $META; do [ -f "$D/cfg_$t/detail_rows.csv" ] && dc=$((dc+1)); done
  if [ "$dc" -ge 12 ]; then echo "ALL 12 METERED DONE $(date +%H:%M:%S)"; exit 0; fi
  if [ "$(ps aux | grep -c '[e]xp16_multi_judge')" -eq 0 ]; then echo "PROCS EXITED, $dc/12 done $(date +%H:%M:%S)"; exit 0; fi
  sleep 42
done
echo "CHECKPOINT $(date +%H:%M:%S): $dc/12 detail_rows written (still scoring)"
