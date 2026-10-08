# Read-only source lookup notes

**Doc link:** [Protocol](../PROTOCOL.md)
**TLDR:** The v5 sources have committed ordinary-model receipts, but the early-access Google raw ratings intentionally live in private storage. Exact seven-family reconstruction must retrieve authorized v5 private cells or report the gap; never silently omit a family.

- `scripts/v5_phaseb.py`: receipts at line 38; main_cells at 53; world_state at 101.
- `scripts/v5_aggregate.py`: load_cells at 29; rater_slots at 49; targets at 85; leave_family_out_target at 120.
- `scripts/x106v5.py`: panel_models at 116 applies frozen exclusions; manifest at 174 joins compressed cells.
- `scripts/v5_infra.py` routes early-access raw cells to `private/v5/runs_private/<run>/cells.jsonl`. This exact v5 private path is permitted for read-only retrieval; do not enumerate private siblings. Keep raw private cells ignored in this experiment's `expt_v1/private/`, with sanitized digest manifests only committed.
- `S1_argon`, `S2_argon`, `LATE_S2_argon` are summary-only in Git. Other S1/S2, F/Z/L and recovery runs carry cells.jsonl; late ordinary-model receipts use cells_G17.jsonl.
- Source receipt validity field is `category`, not `status`; successful parser-v2 score field is `score_0_5_parser_v2`. Distinguish response receipts from deduplicated cells.
- `results/targets.csv` has rounded six-decimal targets; exact matching needs full-precision raw reconstruction. Do not instantiate v5_analysis.Data only for targets, because it also loads old human labels.
- Exact primary pool: opus55x D0/H0/H2; qwen36 D0/H0/H1/H2/R4; t2_qwen D0/H2; t2_sonnet5 D0/H2. Historical identity and blank components were constant; new v5 results must be measured rather than assumed.
- Metadata inventory read no criterion values and computed no criterion statistics. Source revision is ccd86d467fd7577826c4b549df2c532bf43b1892.
