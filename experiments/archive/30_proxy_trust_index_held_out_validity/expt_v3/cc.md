# Reproduce the within-problem criterion audit

**TLDR:** Reproduce the bounded audit of existing human labels and judge scores, and prepare the deterministic six-problem request inventory. Success means exact validated input joins, declared within-problem metrics and shared-bootstrap intervals, preserved frozen evidence, and a readable result; no inference or new labeling is permitted.

Read PROTOCOL.md before running. From the repository root, run run_audit.py in this version with the project's existing Python environment and CUDA_VISIBLE_DEVICES=''. Render the saved figure with expt_v3/render_plot.py. Run tests/test_criterion_audit.py plus tests/test_proxy_followups.py and tests/test_ti_validation.py. Keep the original protocol and version2/experiment29 files immutable. Store results in this version's results directory and update the experiment-root results.md and CKPT_criterion_audit.md with actual timestamps. Do not turn this diagnostic into a claim of human-label validity or transfer to unseen families. A new model identity requires a separate locked panel and reviewed runner.

Review findings must be reconciled before publication. Use the existing published report receipt if one exists; do not duplicate reports or mutate older runs. Commit scanned task-owned material and follow the repository's main-landing workflow.

TL;DR: Use deterministic Python to reproduce the existing-data audit and cached-pilot inventory; report uncertainty and leave new-family inference unstarted.
