# Run the Certification Judge Vals smoke on SNAP

**TLDR:** Execute the frozen one-call protocol, preserve every artifact and report the real terminal outcome in this experiment.

Every agent working on SNAP runs with full access (`clauded`/ccdp, `clauded-vals`/ccdv, `codexd`/codexdp or `codex exec --dangerously-bypass-approvals-and-sandbox`) and never stops to ask permission; Brando pre-approves all task work there. Budgets, secrets and shared-node safety still apply.

Read PROTOCOL.md and manifest.json. Verify the exact input hashes, runtime, Vals-owned route and preflight price bound. Launch scripts/run_smoke.py with the private host settings path using durable execution. The reservation file prevents repeat admission; never remove it to rerun a failed cell.

Complete the entire frozen manifest of one cell through its declared terminal procedure. Do not stop healthy work at coordinator boundaries. Preserve final output, finish reason, model, effort, usage, cost and errors. Never substitute a model, retry a score, weaken the criterion, or claim a successful model judgment from a metadata listing. Update results.md, the checkpoint and the readable results report. Keep raw routing/configuration/response material private and ignored.
