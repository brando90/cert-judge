#!/usr/bin/env bash
# TLDR: Make the hosted Valkyrie CLI usable in a Claude Code cloud container: install `valkyrie` with uv and check
# that the environment secret VALKYRIE_API_KEY (an access key from `valkyrie token create <name> --expires-in-days 90`
# on Brando's machine, stored in the cloud environment's settings, never pasted into chat or committed) reaches his
# organization. Since 10-13-2026 Valkyrie runs in Vals' cloud and the CLI reads only a saved login, VALKYRIE_API_KEY
# and VALKYRIE_URL; the former VALKYRIE_YAML_B64 / ~/.config/valkyrie/valkyrie.yaml route is ignored and no longer
# written. An access key can admit, poll and harvest runs and download agents, but cannot register a benchmark
# service (`valkyrie benchmark service set` needs `valkyrie login`). The pack services (a tunnel that must stay up
# for the whole campaign) and Lean probe validation still belong on an always-on host such as SNAP: a cloudflared
# quick tunnel needs outbound TCP 7844, which the container network blocks (443 is open).
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
if ! valkyrie whoami --help >/dev/null 2>&1; then
  uv tool install --quiet --force "git+https://github.com/vals-ai/Valkyrie@prod"
fi
if [ -n "${VALKYRIE_YAML_B64:-}" ] || [ -n "${VALKYRIE_CONFIG_PATH:-}" ] || [ -n "${VALKYRIE_ENV:-}" ]; then
  echo "note: VALKYRIE_YAML_B64 / VALKYRIE_CONFIG_PATH / VALKYRIE_ENV are ignored by hosted Valkyrie; remove them from the environment settings" >&2
fi
if [ -z "${VALKYRIE_API_KEY:-}" ]; then
  echo "no VALKYRIE_API_KEY in the environment: create one with 'valkyrie token create cj-cloud --expires-in-days 90' and add it to the cloud environment settings" >&2
  exit 2
fi
unset VALKYRIE_ENV VALKYRIE_CONFIG_PATH
# Read-only checks that spend nothing: identity (organization and credential kind), the default sandbox provider,
# and the agent list (all fail loudly on a bad or expired key).
valkyrie whoami
valkyrie provider list
valkyrie agent list --all 2>&1 | tail -5 || true
