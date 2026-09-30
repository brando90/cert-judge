#!/usr/bin/env bash
# TLDR: Make the Valkyrie CLI usable in a Claude Code cloud container: install `valk` with uv and write
# ~/.config/valkyrie/valkyrie.yaml from the environment secret VALKYRIE_YAML_B64 (the base64 of Brando's own
# valkyrie.yaml, stored in the cloud environment's settings, never pasted into chat or committed). Verified
# 09-30-2026: `uv tool install git+https://github.com/vals-ai/Valkyrie@prod` and `valk --help` work through the
# container proxy; docs.valkyrie.vals.ai and model-gateway.vals.ai are reachable. This makes admit/poll/harvest
# possible from a cloud session; the pack services (a tunnel that must stay up for the whole campaign) and Lean
# probe validation still belong on an always-on host such as SNAP.
set -euo pipefail
if ! command -v valk >/dev/null 2>&1; then
  uv tool install --quiet "git+https://github.com/vals-ai/Valkyrie@prod"
fi
export PATH="$HOME/.local/bin:$PATH"
cfg="$HOME/.config/valkyrie/valkyrie.yaml"
if [ -f "$cfg" ]; then
  echo "valkyrie.yaml already present at $cfg (left unchanged)"
elif [ -n "${VALKYRIE_YAML_B64:-}" ]; then
  umask 077
  mkdir -p "$(dirname "$cfg")"
  printf '%s' "$VALKYRIE_YAML_B64" | base64 -d > "$cfg"
  chmod 600 "$cfg"
  echo "wrote $cfg from VALKYRIE_YAML_B64 ($(wc -c < "$cfg") bytes; contents never printed)"
else
  echo "no VALKYRIE_YAML_B64 in the environment and no $cfg: add the secret in the cloud environment settings" >&2
  exit 2
fi
valk --help >/dev/null && echo "valk OK"
# Read-only checks that spend nothing: list runs and agents (both fail loudly on a bad key or bucket access).
VALKYRIE_ENV="${VALKYRIE_ENV:-bench}" valk run list 2>&1 | tail -3 || true
VALKYRIE_ENV="${VALKYRIE_ENV:-bench}" valk agent list --all 2>&1 | tail -5 || true
