# Five-rater cached selection and behavioral audit

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex-cj-five-rater-recovery/experiments/45_five_rater_cached_selection_task_split_and_behavioral_audit/README.md>

**TLDR:** Execute the recovery runbook using existing labels and judge scores, preserving task groups and historical-label regimes. The question is whether behavioral screening selects a judge that agrees better with humans than the fixed human-rating rubric.

Protocol: [PROTOCOL.md](PROTOCOL.md). Live ledger: [results.md](results.md). Sources and hashes: [inventory.json](results/inventory.json). Reproduction: `uv run --no-project --with numpy --with scipy --with pytest python experiments/45_five_rater_cached_selection_task_split_and_behavioral_audit/scripts/inventory.py`.

Runtime and exact continuation are in [the owned checkpoint](../../CKPT_codex-cj-five-rater-recovery.md). All inference is forbidden for this recovery; no manuscript or benchmark reference is changed. Prior source experiments and VeriBench are read-only dependencies.
