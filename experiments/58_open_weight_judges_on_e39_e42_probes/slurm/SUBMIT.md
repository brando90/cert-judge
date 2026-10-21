# SUBMIT: experiment 58 on FarmShare (Sherlock fallback at the end)

**TLDR:** upload one tarball, run `prepare.sh`, `sbatch smoke.sbatch`, then `bash submit_all.sh`; the 13 judge jobs run at most 4 GPUs at a time and write one results tarball with `collect.sh`. Everything lives under `~/e58`; no paid API; mail goes to both addresses on END and FAIL.

Package: `e58_pkg.tgz` (sha256 in `e58_pkg.tgz.sha256`, printed in the task result). GPU time: about 90 GPU-hours for all 13 models (`GPU_HOURS.md`, assumed throughput until the smoke prints real tokens/s); about 16 GPU-hours for the 1-GPU subset.

## FarmShare (primary)

All in the OnDemand JupyterLab **Terminal** (a node with internet), Stanford account `brando9`.

0. **Shared venv.** `~/venvs/fs_hf` (vLLM 0.32.0, transformers 5.19.0, torch 2.13.0+cu130) must exist; `ls ~/venvs/fs_hf/bin/python` should print a path. If not, build it as `~/at615/build_fs_hf.sbatch` did (`/usr/bin/python3.12 -m venv`, then `pip install -r requirements.lock.txt`).
1. **Upload and unpack.**
   ```
   mkdir -p ~/e58/code && cd ~/e58
   # upload e58_pkg.tgz to ~/e58 (Jupyter file browser's upload arrow, or OnDemand Files > Upload)
   echo "<sha256 from the task result>  e58_pkg.tgz" | sha256sum -c -
   tar xzf e58_pkg.tgz -C ~/e58/code
   ```
2. **Prepare** (about 30-60 minutes, mostly downloading ~410 GB of weights into `~/e58/models`; check `du -sh ~` against your quota first, or start with a subset: `bash .../prepare.sh qwen3_4b,qwen3_8b,llama31_8b,gemma3_4b,gemma3_12b,olmo3_7b,gpt_oss_20b`).
   ```
   bash ~/e58/code/experiments/58_open_weight_judges_on_e39_e42_probes/slurm/prepare.sh
   ```
   It downloads each model at its pinned revision, verifies sizes, writes `slurm/tasks.tsv`, verifies the 9,927 prompt rows against the frozen hashes, tokenizes every prompt per model (`results/TOKEN_BUDGET.json`: over-context cells per model) and runs the CPU tests. It ends with `PREPARE OK`.
3. **Smoke** (one L40S, about 10 minutes, 20 cells with Qwen3-4B).
   ```
   cd ~/e58 && sbatch ~/e58/code/experiments/58_open_weight_judges_on_e39_e42_probes/slurm/smoke.sbatch
   squeue -u $USER ; tail -30 ~/e58/logs/e58_smoke_*.log
   ```
   Expect `SMOKE OK`, harvest status counts with mostly `measured`, and a tokens/s line. Mail arrives from nobody@stanford.edu. A `parse_error` share above a few cells, or a vLLM crash, means stop and send the log back.
4. **Submit everything.** Check the queue room first (`squeue -r -h -u $USER -q gpu | wc -l`; the script refuses if fewer than 13 slots of 32 are free).
   ```
   bash ~/e58/code/experiments/58_open_weight_judges_on_e39_e42_probes/slurm/submit_all.sh
   ```
   One array for the seven 1-GPU models (`%4`) and one for the six 2-GPU models (`%2`); QOS gpu allows 4 GPUs at once, so the two arrays share them. A subset: `ONLY="0 1 2" bash submit_all.sh` (indices of `slurm/tasks.tsv`: 0 qwen3_4b, 1 qwen3_8b, 2 qwen3_14b, 3 qwen3_32b, 4 qwen36_27b, 5 llama31_8b, 6 llama33_70b_awq, 7 gemma3_4b, 8 gemma3_12b, 9 gemma3_27b, 10 olmo3_7b, 11 olmo3_32b, 12 gpt_oss_20b). Job ids are saved in `~/e58/job_ids.txt`. The JupyterLab session may end after the submit.
5. **A job timed out or failed** (2 days max; each is resumable): resubmit the same index, which skips finished cells: `sbatch --gres=gpu:<1|2> --array=<idx> .../slurm/run_model.sbatch`.
6. **Collect** (when `sacct -X -u $USER --format=JobID,JobName,State,Elapsed` shows all COMPLETED; safe to run earlier too).
   ```
   bash ~/e58/code/experiments/58_open_weight_judges_on_e39_e42_probes/slurm/collect.sh
   ```
   It writes `~/e58/e58_results.tgz` and prints its sha256 (also `e58_results.tgz.sha256`) and how many of the 234 harvests exist. Download: `https://ondemand.farmshare.stanford.edu/pun/sys/dashboard/files/fs//home/users/brando9/e58/e58_results.tgz?download=1`, then compare the sha256.
7. **Analyze** (CPU, anywhere with the repo): `python experiments/58_.../scripts/analyze58.py --run <extracted runs/main>` writes `results/ANALYSIS.json` and `results/RESULTS_open_weight_judges.md`.

## Sherlock (fallback, same package)

Use when FarmShare's queue is full. GPU partition `gpu` with L40S or H100 (the `-p normal` partition is CPU only); the vLLM 0.30.0 Apptainer image from the earlier rl4cv work must exist at `$SCRATCH/rl4cv_sherlock/containers/vllm-openai_v0.30.0.sif`.

1. Upload `e58_pkg.tgz` to `$SCRATCH/e58`, verify the sha256, `mkdir -p $SCRATCH/e58/code && tar xzf e58_pkg.tgz -C $SCRATCH/e58/code`.
2. `srun -p dev -c 4 --mem=16G -t 02:00:00 bash $SCRATCH/e58/code/experiments/58_open_weight_judges_on_e39_e42_probes/slurm/sherlock/prepare.sh` (internet; the dev node has no GPU, weights land in `$SCRATCH/e58/models`; repeat with a model list if 2 hours is not enough, it resumes).
3. Smoke: `cd $SCRATCH/e58 && sbatch -G 1 --array=0 $CODE/slurm/sherlock/run_model.sbatch smoke` (source `slurm/sherlock/env.sh` first for `$CODE`), look for `SMOKE OK` in `logs/`.
4. `bash $CODE/slurm/sherlock/submit_all.sh`, then `bash $CODE/slurm/sherlock/collect.sh`; results at `$SCRATCH/e58/e58_results.tgz` (fetch with Files `?download=1`).

## What a good outcome looks like

Smoke: `SMOKE OK`, 20 cells, at most a few `parse_error`/`incomplete`, tokens/s in the thousands for a 4B model. Full: `collect.sh` reports 234 of 234 harvests (117 units x E39 and E42; any `MISSING.json` entry is a model that did not finish), mostly `measured` cells, `unmeasured_over_context` only where `TOKEN_BUDGET.json` predicted it.
