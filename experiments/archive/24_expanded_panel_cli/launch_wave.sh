#!/bin/bash
# launch_wave.sh <wave1|wave2>
# Fans out expanded-panel scoring as parallel single-config exp16 runs.
# wave1 (now): 12 metered (OpenAI: gpt-5.3-codex + gpt-4o-mini x6 prompts) + 4 cli-fable.
# wave2 (after Codex quota reset ~21:15): 2 cli-fable + 6 cli-sol.
set -u
WAVE="${1:?usage: launch_wave.sh wave1|wave2}"
RC="$HOME/cert-judge/experiments/24_expanded_panel_cli/run_config.sh"
PROMPTS=(P2_FORMAL P3_CONCISE P7_STRICT_A P13_HUMAN_ALIGN_STRICT P14_HUMAN_ALIGN_V2 P16_ERIC_COMPARATIVE_TRACKED)
launch() { echo "launch $1:$2 -> $3"; nohup bash "$RC" "$1" "$2" "$3" >/dev/null 2>&1 < /dev/null & }

if [ "$WAVE" = "wave1" ]; then
  for p in "${PROMPTS[@]}"; do
    launch "gpt-5.3-codex" "$p" "codex_${p}"
    launch "gpt-4o-mini"   "$p" "4omini_${p}"
  done
  for p in P2_FORMAL P3_CONCISE P7_STRICT_A P13_HUMAN_ALIGN_STRICT; do
    launch "cli-fable" "$p" "fable_${p}"
  done
elif [ "$WAVE" = "wave2" ]; then
  for p in P14_HUMAN_ALIGN_V2 P16_ERIC_COMPARATIVE_TRACKED; do
    launch "cli-fable" "$p" "fable_${p}"
  done
  for p in "${PROMPTS[@]}"; do
    launch "cli-sol" "$p" "sol_${p}"
  done
fi
sleep 3
echo "WAVE $WAVE dispatched $(date +%H:%M:%S)"
