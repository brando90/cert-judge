E58 two-GPU judges rerun on skampere1 (Stanford CS), 2026-10-29. Same package (e58_pkg_at1209.tgz sha256 889c8af991634499907e0f97f8f89eceee0341490fa7a6b75805e20f9cefb574), unchanged scripts/judge_vllm.py, pinned revisions, seeds and sampling.
Deviation from the FarmShare plan: hardware only. 2x NVIDIA A100-SXM4-80GB (TP=2) instead of 2x L40S; no Slurm. Stack identical to the FarmShare one: vLLM 0.32.0, torch 2.13.0+cu130, transformers 5.19.0 (venv at962/venv). Each raw *.meta.json engine block records vllm, torch, gpu, host, tensor_parallel_size.
Weights: re-downloaded at the pinned HF revision (qwen36_27b copied from an existing snapshot at the same revision), each checked by fetch_models.snapshot_ok.
Cause: FarmShare TP=2 jobs hung (vLLM shm broadcast timeout) and timed out.
