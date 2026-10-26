# E58 partial result: the 4 finished open-weight judges (2026-10-26)

**TLDR:** the frozen E58 analysis (`scripts/analyze58.py`, unchanged) run on the 4 judges that finished (Qwen3 4B, 8B, 14B, Llama 3.1 8B; 36 units = 4 models x 9 prompts; 72 of 234 harvests; the other 9 models are not run yet). Gate on this partial panel: plain FAIL (Spearman 0.433, p 0.0052, n=35, bar 0.45 and p<0.05), model-clustered FAIL (p 0.328, only 3 models with all prompts). The panel is incomplete, so this is a preliminary reading, not the E58 verdict.

Source: `~/e58/runs/main` on FarmShare, collected with `slurm/collect.sh` (tarball sha256 `3fd6e86cb2b1b68de79c9c7dfb31e0b63dbf111ae210eddea5c4fc0767c486d7`, MANIFEST verified, 0 failures). Full output: `ANALYSIS.json`, `RESULTS_open_weight_judges.md`. No model call, nothing resubmitted or cancelled. Analysis with 10,000 draws.

Harness for every row: vLLM offline single call, no tools, each model's own chat template and generation_config defaults (PROTOCOL.md section 4). Criterion = Spearman of the unit's per-item median score vs `target_expert` over the held-out val+test items (about 42 of 45 scored). `C_ms_gold` = the frozen label-free index. Each cell is mean [min, max] over the 9 prompt configurations.

| harness | model | units | criterion Spearman | C_ms_gold | E42 semantic screen PASS | cells measured / parse_error / incomplete (E39) |
|---|---|---:|---|---|---:|---|
| vLLM single call, no tools | Qwen3 4B | 9 (criterion n=9, C_ms_gold n=9) | 0.293 [-0.150, 0.512] | 0.715 [0.519, 0.966] | 1/9 | 4621 / 0 / 3 |
| vLLM single call, no tools | Qwen3 8B | 9 (criterion n=9, C_ms_gold n=9) | 0.174 [-0.389, 0.648] | 0.770 [0.436, 0.985] | 2/9 | 4610 / 12 / 2 |
| vLLM single call, no tools | Qwen3 14B | 9 (criterion n=9, C_ms_gold n=9) | 0.349 [-0.246, 0.659] | 0.864 [0.654, 0.992] | 2/9 | 4623 / 1 / 0 |
| vLLM single call, no tools | Llama 3.1 8B Instruct | 9 (criterion n=9, C_ms_gold n=8) | 0.219 [-0.112, 0.574] | 0.545 [0.348, 0.967] | 0/9 | 4506 / 97 / 21 |

Notes: Llama 3.1 8B has 97 parse_error and 21 incomplete cells (about 2.5% of 4,689), the highest of the four; one Llama unit has no C_ms_gold and one has no E42 verdict (NOT_COMPUTABLE). Per-unit rows are in `ANALYSIS.json` (`units`). Not computed: the 9 other judges (3 timed out at the 2-day cap and are resumable, 2 running, 4 pending).
