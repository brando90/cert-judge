# Checkpoint: Experiment 29 post-release Mega quality assurance

Created: 2026-09-14 15:24 PDT
Last updated: 2026-09-14 15:29 PDT

- Run identifier: `cj-exp29-release-megaqa-20260914-opus5-a1`
- Coordinator: root Codex task on Brando's MacBook Pro; sole recovery owner.
- Phase: BLOCKED before remote clone or model invocation.
- Published release: `c20027dc2b10758b8128adca5d5b93eeacba2653` from base `03946b83d85af2530971322ec6dfcdba80e0bacd`.
- Dispatch base: `0fa83475fc0f8e147ca281b7bfbc6a2f8652990c` on `origin/main`.
- Task branch: `codex/exp29-release-megaqa-20260914`.
- Target: `mercury1.stanford.edu`; dedicated remote directory `/dfs/scratch0/brando9/cj-exp29-release-megaqa-20260914/cert-judge`.
- Planned persistent-terminal prefix: `cj-exp29-release-opus5`; no session was created because the host rejected dispatch before execution.
- Requested executor: Vals AI Claude Code, `claude-opus-5`, effort `max`, one bounded invocation.
- Acceptance: advisory only; mandatory fresh Fable 5.1/max -> Codex GPT-6 Astra/ultra -> fresh Fable 5.1/max remains `0/3`.
- Fresh health evidence: direct worker audit on `mercury1.stanford.edu` passed Vals authentication/client, Kerberos, Andrew File System token, Lean 4.22.0, Git access, and shared storage. Local-disk use warned at 95% with 339 GiB free. The personal-Claude `.claude` layout failure is unrelated to `clauded-vals`.
- Completed: historical release lineage, hashes, 12-path survival, 89 passing targeted tests plus the separately passing cached Lean fixture, two exact-version publisher tests, and lock dry-run were previously verified locally.
- Forbidden: Experiment 30 changes; new measurements; publication; report deletion; provider keys; purchases; automatic recharge; postpaid/on-demand spillover; weakening the Fable acceptance floor.
- Dispatch attempt: rejected by the host at 2026-09-14 15:29 PDT as private-repository transmission to `mercury1.stanford.edu` and the external Vals AI/Anthropic reviewer with paid model usage. Remote clone, persistent-terminal session, and model calls all remain zero.
- Exact next step: obtain explicit user authorization for that private repository payload, named SNAP host, named Vals AI/Anthropic model destination, and bounded paid invocation; then retry the same immutable job once. Do not use an alternate route or workaround.
- Reboot recovery: none; the named tmux session survives disconnects but not a node reboot. Root owns observation and restart from this checkpoint.
