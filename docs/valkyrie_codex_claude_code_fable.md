# Valkyrie: Codex and Claude Code (and Fable)

**TLDR:** Codex and Claude Code are allowed in Valkyrie by design, and the Fable model exists there, but as of 2026-10-28 neither agent can run for us: the org has no raw Anthropic or OpenAI key secret and neither agent is installed. Waiting on Jaewon Jeung (Vals) to restore the keys. Nothing here has been run since the Oct 14 migration.

## Status (2026-10-28)

| Question | Answer | Evidence |
| - | - | - |
| Are Claude Code and Codex allowed in Valkyrie? | Yes, by design | Jaewon's agent list names `claude_code`, `codex`, `codex_lean`. The public agent registry ships `claude_code-v1.0.0` and `codex-v1.0.0` contracts. |
| Does Fable exist there? | Yes | Vals model library lists `anthropic/claude-fable-5-1` and `-low`, `-medium`, `-high`, `-xhigh`, `-max`, `-no-fallback` variants. |
| Has Claude Code on Fable run on Valkyrie? | Yes, before the migration | Run `2f33f21e-65dc-4011-9ef1-256ec1decb17` (agent `vb107_claude_code`, model `anthropic/claude-fable-5-1`, veribench107-preflight) finished with score 1.0 on Oct 5. |
| Can it run now? | No, blocked | Org `BrandoMiranda-fellow` has no Anthropic or OpenAI key secret (`valkyrie secret list` shows only `brandoModelGatewayApiKey`, `daytona` and per-task auth secrets). The 39 installed agents include no `claude_code` or `codex`. |
| Does the Vals model gateway cover them? | No | Jaewon, Oct 6 email: the gateway "doesn't support 3p agents (codex, claude) at the moment". So these agents need raw provider keys. |
| Is the Oct 14 403 ("Managed AWS access is not available") still blocking? | No | `daytona` provider is mapped and 400+ runs have finished since Oct 15. |
| Does Fable work with Codex? | No | The Codex contract lists only GPT models (default `gpt-5.3-codex`). Fable applies to Claude Code only. |

Not tested: a fresh end-to-end Claude Code or Codex run since the migration.

## Route (what makes it work)

Reference: [Valkyrie agent contract](https://docs.valkyrie.vals.ai/agents/agent-contract.md) and [Package an agent](https://docs.valkyrie.vals.ai/agents/package-an-agent.md).

Two routes to the key exist. Jaewon's own route (Slack DM) is to create a secret in Secrets Manager under `fellows/brandomiranda/*` and point the agent contract yaml's `secrets` at it. The Valkyrie docs' route is `valkyrie secret set <name>`, which stores an org secret and prints its reference. Both are untested here since the migration, and which one is right is an open question to Jaewon. The secret names below (`anthropic-api-key`, `openai-api-key`) are placeholders taken from the docs' example, not names that exist in our org.

1. Jaewon (jaewon@vals.ai) provides a raw key per provider. Do not store or paste key values in any repo.
2. Store each key as a secret, by either route. With the Valkyrie CLI (the command prompts for the value and prints the reference):
   `valkyrie secret set anthropic-api-key` and `valkyrie secret set openai-api-key` (placeholder names)
3. Install the agent from the public registry (on skampere, `PATH=/dfs/scratch0/brando9/bin`). The path below is from the registry README and is unchecked:
   `valkyrie agent install https://github.com/vals-ai/public-agent-registry/tree/jf/agent-checkpoint/examples/claude_code-v1.0.0`
   (Codex: same registry, `examples/codex-v1.0.0`.)
4. Start a one-task test run first:
   `valkyrie run start --benchmark <bench> --agent claude_code-v1.0.0 --model anthropic/claude-fable-5-1-xhigh -s ANTHROPIC_API_KEY <anthropic-secret-ref> --slice :1 --concurrency 1`
   For Codex use `-s OPENAI_API_KEY <openai-secret-ref>` and a GPT model from the contract's list.

Contract facts: the Claude Code contract runs `claude -p --verbose --output-format stream-json`, reads `ANTHROPIC_API_KEY`, and defaults to sonnet-4, so always pass `--model`. The Codex contract reads `OPENAI_API_KEY`. Secrets map to environment variables through the contract's `secrets` field, and `-s ENV_VAR SECRET` overrides it for one run.

## Bucket check (2026-10-28)

Jaewon's Oct 6 note said he would put `grok_build` in the bucket `fellow-brando-miranda`. A read-only listing shows the bucket holds agent bundles, not keys: `agents/claude_code.zip`, `claude_code_no_internet.zip`, `codex.zip`, `codex_no_internet.zip`, `grok_build.zip` and `pi_agent.zip` (uploaded Sep 30), plus benchmark outputs. No Anthropic or OpenAI key is in it. In the `claude_code` and `codex` bundles' `contract.yaml`, the key comes from the Valkyrie secret `prodBenchmarksInfraApiKeys` (`ANTHROPIC_API_KEY` and `OPENAI_API_KEY` respectively), and our org has no secret by that name. The fellow AWS user cannot list or describe Secrets Manager secrets (AccessDenied), so the key cannot be read from there either. The agent bundles are not installed (`valkyrie agent list --all` shows 39 agents, none of them `claude_code` or `codex`).

What is left: a raw key stored as an org secret (`valkyrie secret set`), then install the agent (bundle from the bucket or the public registry) and point `-s ANTHROPIC_API_KEY <secret>` at that secret. Jaewon's Oct 6 mail gave a 1Password share link for a $1k Anthropic key valid until Brando's last Vals day or Dec 31; using it needs Brando's yes.

## Rules for our repos

* Never commit key values, secret values, 1Password share links or Slack message links to any repo.
* No paid Valkyrie runs without Brando's yes.
* Sign in to `valkyrie` as brando@vals.ai (org `BrandoMiranda-fellow`); on skampere the binary is under `/dfs/scratch0/brando9/bin`.

## Who to ask

Jaewon Jeung, jaewon@vals.ai (Vals). Brando emailed him on 2026-10-28 16:29 PDT in the existing Gmail thread "Native Claude Code / Codex in Valkyrie: Anthropic key returns 401", asking whether the gateway supports these agents now or how to restore the keys as org secrets. Update this doc when he answers.
