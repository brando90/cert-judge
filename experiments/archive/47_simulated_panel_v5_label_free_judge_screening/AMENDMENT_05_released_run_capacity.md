# Reuse capacity released by completed probe runs

**Doc link:** [Frozen protocol](PROTOCOL.md)
**TLDR:** Apply at most one concurrency update to each of four existing probe runs after named original runs become terminal; preserve every task, result and scientific setting.

Written 10-08-2026 before any scheduling update, during the already admitted probe campaign.
Original criterion results and some probe outputs have been inspected; this is an operational scheduling amendment, not a blinded scientific amendment.
The reason is observed execution latency; selection of these four targets depends only on the original harness groups and terminal execution states, never scores, property values or criterion associations.

- The original 12 probe runs each began at concurrency 20: five Anthropic runs (100 task slots) and seven Alibaba runs (140 task slots).
  These are observed admission totals, not protocol-mandated ceilings or request-rate guarantees.
- Once original Opus D0 and both original Sonnet runs are terminal, set each still-active original Opus H0/H2 run to 50 task slots.
- Once all five original single-call Qwen runs are terminal, set each still-active original Terminus2 Qwen D0/H2 run to 70 task slots.
- Skip a target that is already terminal, leaving that capacity unused.
  Do not redistribute again, update any other run, or exceed the original provider totals of 100 and 140 simultaneous task slots.
- Freeze the exact original run identifiers and identity bindings before updates.
  Use only the installed authenticated `valk run update UUID --concurrency N` command, whose dedicated operation updates the existing run's concurrency.
  It does not start, resume or retry a run.
  Preserve original admission commands and ledger concurrency 20 as historical evidence; record actual scheduling updates separately.
- Before each update, verify original benchmark, agent, model, label, task count and run identifier through the supported authenticated run-list command, plus the complete frozen local task mask and healthy callback gate.
  Write a durable mutation intent first, record its exact command and result, and never automatically replay a missing or failed acknowledgement.
- The supported live fetch returned `metadata_available=false` and no concurrency value before this amendment.
  Do not pretend that independent concurrency read succeeded.
  The installed update command prints the concurrency returned by the server's dedicated update response; preserve and require that explicit acknowledgement, then verify the original run identifier and task count through a fresh status read.
  A target becoming terminal during the operation may return its old value; retain that terminal no-op explicitly.
  Any other mismatch is unresolved and stops further scheduling updates without stopping healthy scientific work.
- Models, prompts, efforts, per-cell limits (including Terminus2's 20-turn limit), parser, task slices, probe validity, pool, analysis and declared call counts remain frozen.
  Preserve every infrastructure error, HTTP 429 and charge; no failed cell is readmitted.
  This condition adds zero runs, zero tasks, zero retries and no spending cap.
