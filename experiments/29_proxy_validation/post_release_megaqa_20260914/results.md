# Experiment 29 post-release review

**TLDR-start:** [cj: release-mega-qa] The published Experiment 29 release is intact; one bounded Vals AI Opus 5/max advisory review is being launched on mercury1, while the mandatory three-stage acceptance chain remains explicitly pending.

**Status:** RUNNING (started 2026-09-14 15:24 PDT)

**Last updated:** 2026-09-14 15:24 PDT

| Phase | State | Evidence |
|---|---|---|
| Release landing and lineage | DONE | `c20027dc2b10758b8128adca5d5b93eeacba2653` is an ancestor of current main |
| Local deterministic recheck | DONE | 89 targeted tests passed; the single detached-worktree Lean setup failure passed with the prepared pinned cache; exact publisher tests passed 2/2 |
| Fresh mercury1 health audit | DONE | Vals client/authentication, Git, Lean, and shared storage usable; 339 GiB local free |
| Opus 5/max advisory review | IN PROGRESS | Dispatch prepared; actual session/process/model evidence pending |
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
- Actual model: pending runtime evidence
- Actual effort: pending runtime evidence
- Verdict: pending
- Critical issues: pending
- Major issues: pending
- Accepted Mega quality assurance stages: `0/3`

No Experiment 30 file, completed measurement, publication target, or duplicate Weights & Biases report is in scope.

**TLDR-end:** [cj: release-mega-qa] The release is done and locally verified; the Opus 5 advisory review is the only admitted continuation, and formal post-release acceptance remains `0/3` until the required strongest-family stages run.
