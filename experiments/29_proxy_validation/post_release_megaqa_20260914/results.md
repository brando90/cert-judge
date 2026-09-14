# Experiment 29 post-release review

**TLDR-start:** [cj: release-mega-qa] The published Experiment 29 release is intact, but the bounded Vals AI Opus 5/max advisory dispatch was rejected by the host before any remote clone or model call; the mandatory three-stage acceptance chain remains pending.

**Status:** BLOCKED (host rejected private-repository reviewer transmission at 2026-09-14 15:29 PDT)

**Last updated:** 2026-09-14 15:29 PDT

| Phase | State | Evidence |
|---|---|---|
| Release landing and lineage | DONE | `c20027dc2b10758b8128adca5d5b93eeacba2653` is an ancestor of current main |
| Local deterministic recheck | DONE | 89 targeted tests passed; the single detached-worktree Lean setup failure passed with the prepared pinned cache; exact publisher tests passed 2/2 |
| Fresh mercury1 health audit | DONE | Vals client/authentication, Git, Lean, and shared storage usable; 339 GiB local free |
| Opus 5/max advisory review | BLOCKED | Host rejected dispatch before remote clone, persistent-terminal creation, or model call |
| Mandatory Fable/Codex/Fable acceptance | PENDING | `0/3`; Opus 5 cannot substitute silently for Fable 5.1 |

## Immutable review range

- Base: `03946b83d85af2530971322ec6dfcdba80e0bacd`
- Release: `c20027dc2b10758b8128adca5d5b93eeacba2653`
- Dispatch main: `0fa83475fc0f8e147ca281b7bfbc6a2f8652990c`
- Release-patch Secure Hash Algorithm 256-bit digest: `e720c9042bc65b0c7179fb7b1aeffdc67e9b1c1dc00aa8c6b6ea63627f00dc64`

## Current review result

- Role: advisory
- Requested model: `claude-opus-5`
- Requested effort: `max`
- Actual model: NOT RUN
- Actual effort: NOT RUN
- Verdict: NOT RUN
- Critical issues: not assessed
- Major issues: not assessed
- Accepted Mega quality assurance stages: `0/3`

## Exact blocker

The host rejected the prepared `ssh-submit.sh --direct` action because it would clone the private repository to `mercury1.stanford.edu` and transmit its contents to the external Vals AI/Anthropic `claude-opus-5` reviewer with paid model usage without explicit authorization for that payload and destination. No session, process, remote checkout, or model invocation was created. Policy forbids retrying through a workaround.

No Experiment 30 file, completed measurement, publication target, or duplicate Weights & Biases report is in scope.

**TLDR-end:** [cj: release-mega-qa] The release is done and locally verified, but the Opus 5 advisory launch is NOT RUN due to the host's destination-specific private-repository gate. Formal post-release acceptance remains `0/3`.
