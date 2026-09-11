# Proxy validation follow-up results

**TLDR-start:** [cert-judge: proxy-followups] RUNNING: recompute the human-grounded target from repeated scores, diagnose zero handling, and check the limits of family transfer. These are exploratory analyses of previously inspected data, not a fresh held-out test.

**Status:** RUNNING (started 2026-09-10 22:39 PDT)
**Last updated:** 2026-09-10 22:39 PDT

| Phase | Status | Evidence |
|---|---|---|
| Read pull requests 41 and 42 | DONE | Both merged; experiment 30 uses human agreement alone. |
| Verify input coverage | DONE | 8 judges × 72 candidates × 3 repeats; 24 problems. |
| Combined target and zero-handling analyses | IN PROGRESS | Protocol in expt_v2/PROTOCOL.md. |
| Shared-problem uncertainty and family diagnostics | PENDING | Five primary configurations span two judge-model families. |
| Independent review and publication | PENDING | Preserve all frozen experiment-29 artifacts. |

Source pull requests: [41](https://github.com/brando90/cert-judge/pull/41) and [42](https://github.com/brando90/cert-judge/pull/42).

**TLDR-end:** [cert-judge: proxy-followups] The saved data support the next diagnostic experiments without model inference; additional independent families cannot be manufactured by relabeling controls or generations.
