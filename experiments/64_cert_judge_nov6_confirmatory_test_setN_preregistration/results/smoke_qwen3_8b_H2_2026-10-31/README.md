# E64 GPU smoke of run_setN_judge.py (AT-2239), 2026-10-31
- Command: run_setN_judge.py --model qwen3_8b --prompts H2 --limit-cells 4 (driver at 49c310c), 1 A100-80GB on skampere1 (free hardware), vllm 0.32.0, torch 2.13.0+cu130.
- Weights: Qwen/Qwen3-8B revision b968826d9c46dd6066d109eabc6255188de91218 (the E58 pin). Family file H2.jsonl.gz sha256 f07193d1... equals FAMILIES_MANIFEST.json (verified_families H2 passed before the model loaded).
- Result: 4 cells = 3 generated (2588 output tokens, 17.1 s) + 1 unmeasured_over_context (N17a, prompt 44,130 tokens, budget -3170, frozen rule). Raw: raw/setn/qwen3_8b/H2.jsonl sha256 50bc7975...; ledger.jsonl has one line for qwen3_8b|H2.
- Environment note: vLLM's FlashInfer sampler needs nvcc to JIT and failed on this host; the run set VLLM_USE_FLASHINFER_SAMPLER=0 (PyTorch sampler, same temperature 0.6 / top_p 0.95 / top_k 20 from the model's generation_config). For the full 117-unit run, set it the same way or provide nvcc.
- Other notes: E58_VERIBENCH_REPO pointed at an existing clone (veribench_e39, d7d36c319), not E58's 9a857c3dc; the driver's checks do not need it. No set-N rating read, no harvest or scoring, no paid API.
