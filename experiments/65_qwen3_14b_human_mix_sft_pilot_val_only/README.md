# E65: Qwen3-14B human-mix SFT pilot (3 seeds), frozen on validation only, no test read

Follow-up of E63/E64 (cert judge, AT-2184). Question: does the E63 human-mix recipe (LoRA r16, lr 2e-4, 4 epochs, `--human_mix 0.5`, soft-CE on first-token digit readout) carry from Qwen3-8B to Qwen3-14B? Free hardware only, no paid API, no mercury1 vLLM server touched.

## Bottom line
- Fits: Qwen3-14B bf16 LoRA r16 trains on ONE A100-80GB (about 34 GB per card, gradient checkpointing), 97 train prompts, 4 epochs in about 80 min per seed. It was not tested on 3-4 A4000 16GB cards of mercury2: jobs launched from skampere1 carry no Kerberos ticket, so they cannot ssh to mercury2. Run on skampere1 GPUs 0, 5, 6 instead (default taken, same free-hardware rule).
- 3 seeds trained and FROZEN on validation human rho. Test items were never copied to the cluster for this run (`pack_trainval.jsonl` only, md5 39737bb95e1f2a2cf9f3f739bc204a1b, 147 lines = 97 train + 50 val). No pass on the 30 old test items. They are scored only on the Nov 6 ratings (E64 pre-registration).
- Validation (50 prompts, 15 human-rated), at the frozen epoch: 14B human-mix mean rho_teacher 0.915, rho_human 0.906 (seeds 0.876, 0.908, 0.935). Qwen3-8B human-mix (5 seeds, E63/E64 at their frozen epochs): rho_teacher 0.920, rho_human 0.923. So on validation 14B is not better than 8B; the 15 human val items are too few to separate them (differences are within seed spread).
- Test numbers: none, by design.

## Results (validation only; no DT is not applicable here: judge-training experiment)
| seed | frozen epoch | val rho_teacher | val rho_human (n=15) | adapter sha256 |
|---|---|---|---|---|
| 0 | 3 | 0.931 | 0.876 | a116630b50ba3d3c9e3b850dd1a2fdbaedbd6fda447cefe63b48ca4eda76fb77 |
| 1 | 2 | 0.876 | 0.908 | b48ad2d0c219f2b2f9bfb847222f715f41e07c2a0292911d057abadd742df650 |
| 2 | 2 | 0.937 | 0.935 | 97bde4f1726711f0edcb4ce02f2b26180df739ea26de3cd8d2164b8ca2a4da12 |
| mean | | 0.915 | 0.906 | |
| Qwen3-8B human-mix, 5 seeds (for scale) | 3,4,4,4,3 | 0.920 | 0.923 | |
| zero-shot Qwen3-14B (epoch 0) | | 0.633 | 0.144 | |

Epoch curves per seed are in `results/runs/<run>/curves.json`. The epoch was picked on val rho_human by the trainer (`FROZEN.json`, written before anything else); epoch 4 val rho_human was lower for s0 (0.736) and s1 (0.847) than the frozen epoch, so the choice matters and the 15-item selection is noisy.

## Files
- `results/runs/sft_q3_14b_hm_s{0,1,2}/{FROZEN.json,curves.json,train_log.jsonl,res_*.json,train.log}`
- `code/run14b.sh` (launch), `code/sft_lora.py` (same as E63)
- Adapters (frozen epochs only, 246 MB each): `/dfs/scratch0/brando9/e62/runs/at2184/sft_q3_14b_hm_s*/ep<N>` on SNAP (copy); all four epochs per seed on skampere1 `/lfs/skampere1/0/brando9/at2184/runs/` (node-local).
- Job: skampere1 job-6ec365af (started 08:33, ended 09:53 on Oct 31 2026, exit 0).

## Caveats
- 15 human-rated val items choose the epoch; selection noise is large.
- Hardware differs from the E63 8B arms (one A100 per seed vs 3 GPUs model-parallel); same script and hyperparameters.
- Test performance is unknown until the Nov 6 ratings.
