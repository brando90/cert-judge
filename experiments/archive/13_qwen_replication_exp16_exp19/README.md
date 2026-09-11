# Exp13 — Qwen3.6-27B replication of Exp16 / Exp19 / Exp25

Open-weights SOTA Qwen replication of the cert-judge multi-judge cert→human
trend pipeline. Mirrors Exp12 (Leanstral) but with the latest open-weights
Qwen as the primary judge family.

## Model

- **Primary judge family:** `Qwen/Qwen3-Coder-30B-A3B-Instruct` (April 2026,
  Apache 2.0, MoE — 30B total / 3B active, 262K native ctx, code-specialized).
  Chosen as the SOTA open-weights Qwen3 *coder* model — pure-text, well-tested
  in vLLM 0.20, and on-task for Lean code judging. Initially attempted
  `Qwen/Qwen3.6-27B` (April 2026 dense flagship with linear attention + GDN)
  but vLLM 0.20 hung in early init (architecture is brand new). Kept
  Qwen3-Coder-30B-A3B-Instruct as the actual served model — still SOTA on the
  >=Qwen3 ladder Brando specified.
- **Cross-family weak controls:** `gpt-4o-mini` (P8_STRICT_B, P4_CHECKLIST).
- **Baselines:** `editdist`, `random`.
- **Bad judge:** Qwen3.6-27B + `BAD_STRINGY` prompt.

The model is served locally via vLLM (OpenAI-compatible endpoint) on snap
GPUs 2,3 with TP=2. `judge_caller.py` was extended with a `qwen` prefix
branch that points at `QWEN_BASE_URL` (default `http://127.0.0.1:8765/v1`).

Why ≥3.6 and not the older Qwen3-Coder ladder in `cc.md`?  Brando asked for
the actual SOTA Qwen (`>=3` was the floor; Qwen3.6-27B is the latest April
2026 open-weights flagship — supersedes Qwen3 / Qwen3-Coder for general
judging quality while staying open-weights and Apache 2.0).

## Pipeline

1. **Exp16** — multi-judge cert-vs-human Spearman trend (pass1 / pass2 / avg).
   Driven by `experiments/04_veribench_validation/exp16_multi_judge_human_sets.py`.
2. **Exp19** — low-variance replot of Exp16 detail rows (monotonicity curves,
   alpha-variant breakdown, bug-ladder reversal rates).
3. **Exp25** — geometric trust-index reanalysis (`TI_geom = mono^0.4 * stab^0.6`,
   for each label set: avg / pass1 / pass2). Wraps
   `exp22_geometric_trust_index.py`.

Methodology fixed (per `cc.md`): `judge-repeats=3`, `repeat-agg=median`,
`threshold=0.85`, `plot-error-bars=on`.

## Layout

```
experiments/13_qwen_replication_exp16_exp19/
├── README.md             # this file
├── cc.md                 # original prompt for Claude Code (kept for provenance)
├── finalize.py           # post-run: commit + open PR (assignee=ehersch) + email
├── scripts/
│   ├── start_vllm_qwen.sh  # launches vLLM (Qwen3.6-27B, TP=2, eager mode on snap)
│   ├── run_full_pipeline.sh  # full Exp16 → Exp19 → Exp25 driver
│   ├── smoke_qwen.py     # sanity-check the wiring before the full run
│   └── email_results.py  # standalone results email (used by finalize.py too)
├── logs/                 # vLLM + pipeline logs
└── results/
    ├── exp16_qwen_r3_median/                            # Exp16 outputs
    ├── exp19_low_variance_replot_qwen/                  # Exp19 outputs
    └── exp25_geometric_qwen_r3_median_mono_stab_40_60_{avg,pass1,pass2}/
                                                          # Exp25 geometric reanalysis
```

## Reproduce

```bash
# 1) one-time: download Qwen3.6-27B (~52 GB) into /lfs/skampere3/0/brando9/hf_cache
HF_HOME=/lfs/skampere3/0/brando9/hf_cache HF_HUB_ENABLE_HF_TRANSFER=1 \
  /lfs/skampere3/0/brando9/uv_envs/cert-judge/bin/python -c \
  "from huggingface_hub import snapshot_download; \
   snapshot_download('Qwen/Qwen3-Coder-30B-A3B-Instruct', \
     cache_dir='/lfs/skampere3/0/brando9/hf_cache')"

# 2) start vLLM (background; ~2 min to ready in eager mode)
nohup bash experiments/13_qwen_replication_exp16_exp19/scripts/start_vllm_qwen.sh \
  </dev/null >/tmp/vllm.log 2>&1 &

# 3) wait until ready
until curl -sS http://127.0.0.1:8765/v1/models >/dev/null 2>&1; do sleep 5; done

# 4) smoke test (1 judge call)
/lfs/skampere3/0/brando9/uv_envs/cert-judge/bin/python \
  experiments/13_qwen_replication_exp16_exp19/scripts/smoke_qwen.py

# 5) full pipeline
bash experiments/13_qwen_replication_exp16_exp19/scripts/run_full_pipeline.sh \
  2>&1 | tee experiments/13_qwen_replication_exp16_exp19/logs/run_pipeline.log

# 6) commit, open PR, email
PYTHONPATH=~/ultimate-utils/py_src \
  /lfs/skampere3/0/brando9/uv_envs/cert-judge/bin/python \
  experiments/13_qwen_replication_exp16_exp19/finalize.py \
  --log experiments/13_qwen_replication_exp16_exp19/logs/run_pipeline.log
```

## Notes / quirks

- The full Qwen3.6 architecture uses linear attention + GDN. vLLM 0.20 supports
  it but CUDA-graph capture for this brand-new arch can take 10+ minutes on
  first run. We ship `--enforce-eager` in `start_vllm_qwen.sh` for predictable
  startup; flip the flag if you want max throughput on a long sweep.
- `judge_caller.py` routes Qwen models via env-driven `QWEN_BASE_URL` /
  `QWEN_API_KEY` so the same code can talk to a remote OpenAI-compatible
  Qwen endpoint instead of local vLLM if needed.
- gpt-4o-mini is kept as the cross-family weak control. It still requires
  `~/keys/openai_*.txt` (already in place on snap).
