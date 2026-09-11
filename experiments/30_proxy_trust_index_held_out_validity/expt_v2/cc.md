# Reproduce the proxy follow-up experiments

**TLDR:** Run the recorded exploratory analyses from frozen local experiment-29 artifacts, verify exact reconstruction, and report the combined agreement-and-stability target. Preserve the frozen proxy and labels, report negative and undefined results, and keep primary judges separate from controls. No language-model calls, credentials, new labels, or graphics processors are needed for the analyses; publish reviewed results through the project workflow.

Read PROTOCOL.md in this directory and the experiment-root README.md. Execute
run_diagnostics.py with its recorded default seed and 2,000 draws, then
render_report.py. Run tests/test_ti_validation.py and tests/test_proxy_followups.py
from the repository root using the existing .venv environment. Check the run
manifest source hashes, source-input preservation, undefined bootstrap draws,
and all negative or extrapolating family-calibration results.

Keep the experiment-root results.md live: update it at launch and after each
meaningful phase, with status, actual timestamp, phase table, results and their
limits; commit and push the ledger as progress lands. Keep
CKPT_proxy_followups.md resumable with actual Created and Last updated stamps,
current state and next commands. Do not treat the observed panel as an unopened
test set. Generation slots do not establish generator-model families, and
controls do not add independent primary judge families.

Run one independent acceptance review using the configured authenticated
subscription command-line interface, apply findings and verify deterministically.
Publish a new report only after review; never resume or rewrite experiment-29
report runs. Commit and synchronize main without rewriting shared history.

TL;DR: Reproduce the offline diagnostic experiments, test and review them, then publish their files and report while preserving the frozen data and explicit limitations.
