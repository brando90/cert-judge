#!/usr/bin/env bash
# Dispatch experiment 34 to Codex (GPT-6 Astra, ultra) inside the worktree. No API keys: subscription CLI only.
set -euo pipefail
REPO="$HOME/cert-judge"; WT="$HOME/cert-judge-astra"; EXP="experiments/34_iclr_mega_rewrite_astra"
mkdir -p "$REPO/$EXP/results"
if [ ! -d "$WT" ]; then git -C "$REPO" worktree add "$WT" -b astra/iclr-mega-rewrite main; fi
PROMPT="$(cat "$WT/$EXP/PROMPT.md")"
# scrub provider keys so the CLI can only use its subscription login
env -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u GEMINI_API_KEY -u GOOGLE_API_KEY \
  nohup codex exec --approve-for-me --disable code_mode_host --cd "$WT" -m gpt-6-astra -c 'model_reasoning_effort="ultra"' "$PROMPT" \
  > "$REPO/$EXP/results/astra_run.log" 2>&1 < /dev/null &
echo $! > "$REPO/$EXP/results/astra_pid"
echo "started codex pid $(cat "$REPO/$EXP/results/astra_pid"); log: $REPO/$EXP/results/astra_run.log"
