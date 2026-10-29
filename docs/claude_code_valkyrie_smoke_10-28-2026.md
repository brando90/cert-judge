# Claude Code through Valkyrie: credential-blocked smoke

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/docs/claude_code_valkyrie_smoke_10-28-2026.md>

**TLDR:** On 10-28-2026, actual Claude Code installed and executed inside Valkyrie, but the Vals Anthropic credential returned HTTP 401. Successful Claude Code evaluation is not yet established with that credential.

## Shared integration result

- Canonical run: `eb111e90-db74-411e-be65-731ee834dee9`; one task launched from SNAP skampere2 into hosted Valkyrie/Daytona; terminal status `ERROR`.
- Actual harness: Claude Code `2.1.312`, not Terminus 2. Requested model: `claude-sonnet-4-6`; successful provider inference was not established.
- Task: write an addition function and execute two assertions. Claude exited **1** with **HTTP 401**, `Invalid API key · Fix external API key`. No successful generated artifact was established; smoke **FAIL**, 0/1 successful tasks.
- CLI-reported model cost: **USD 0**, zero input/output tokens. Sandbox charges are separate and not reconciled.
- Bounds: USD 1 CLI model budget, three turns, 180-second CLI timeout, concurrency one, no task retries. The full-access flag was present; no permission denials were reported.

This is shared transport/harness evidence, **not a cert-judge experiment, judge validation or benchmark score**. The existing VeriBench carrier task's solver instruction was not scored. No cert-judge metric, reference or scientific condition was modified.

User instruction, 10-28-2026: **“smoke tests are always fine.”** This permits bounded smoke checks without lifting broader spending limits. No pause or allowlist file was changed.

[Canonical report, exact source bundle and native evidence](https://github.com/brando90/veribench/blob/main/experiments/coordination/claude_code_valkyrie_smoke_10-28-2026/results.md).

Next: replace/reissue the rejected Vals-owned Anthropic credential securely, then perform a separate passing retest before real evaluations. No personal credential fallback is installed or authorized by this diagnostic.

**TLDR-end:** [Vals: Claude Code smoke] The native harness runs inside Valkyrie, but invalid provider authentication prevents inference. This does not change existing scientific results or protocols.
