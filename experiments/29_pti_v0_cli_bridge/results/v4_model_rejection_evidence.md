# v4 exact-model CLI rejection evidence

Observed 2026-08-25 before any benchmark score was requested. These were
subscription-CLI model-availability probes with synthetic text only.

```text
$ codex exec -s read-only -m gpt-5.3-codex -c 'model_reasoning_effort="low"' \
    'Reply with exactly: MODEL_OK_53'
model: gpt-5.3-codex
provider: openai
ERROR 400: The 'gpt-5.3-codex' model is not supported when using Codex with a ChatGPT account.

$ codex exec -s read-only -m gpt-4o-mini -c 'model_reasoning_effort="low"' \
    'Reply with exactly: MODEL_OK_4OMINI'
model: gpt-4o-mini
provider: openai
ERROR 400: The 'gpt-4o-mini' model is not supported when using Codex with a ChatGPT account.
```

Both commands exited nonzero. No benchmark artifact was supplied and no score
was produced. The original login shell had an inherited provider-key variable,
but both errors explicitly identified ChatGPT-account authentication; the v5
runner now removes all such variables before every auth check and child launch.
The v4 protocol therefore remains `NOT_RUN`; experiment 29 preregisters the
distinct CLI v5 execution/model panel rather than silently substituting models.
