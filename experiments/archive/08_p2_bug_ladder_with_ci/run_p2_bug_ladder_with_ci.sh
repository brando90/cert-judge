#!/usr/bin/env bash
# Experiment 08: P2 bug-ladder vs LLM judge with per-x 95% CI error bars.
# Mirrors the env-loading pattern of experiments/00_overall_cert_judge_metric_with_properties.

set -euo pipefail

# ------------------- env / model -------------------
# Pick which Claude env file to load (overridable from caller)
# NOTE: real keys live under experiments/keys/ — do NOT relocate.
: "${claude_dotenv_path:="$HOME/cert-judge/experiments/keys/.env_claude_3_5_v1"}"
if [ -f "$claude_dotenv_path" ]; then
    # shellcheck disable=SC2046
    export $(grep -v "^#" "$claude_dotenv_path" | xargs)
else
    echo "WARN: claude_dotenv_path does not exist: $claude_dotenv_path" >&2
fi

# ------------------- inputs -------------------
: "${bug_ladder_path:="$HOME/cert-judge/data/file_equiv_08_19_2025/my_add_file_eq_with_bugs"}"
# NOTE: this prompt template was missing from veribench at run time
# (referenced by ~/veribench/experiments/10_file_equiv/main.sh:33 but absent
# on disk and from git history). A canonical copy lives in this experiment
# dir; see REPORT.md "Open questions for Ethan" for the patch decision.
: "${judge_prompt_temp_path:="$(cd "$(dirname "$0")" && pwd)/prompts/simplest_prompt_varying_score_range.txt"}"
: "${max_score:=30}"
: "${num_samples:=15}"          # LLM calls per bug-count file (S)
: "${max_workers:=16}"
: "${output_dir:="$(cd "$(dirname "$0")" && pwd)/out"}"
: "${wandb_project:="cert-judge-08-p2-bug-ladder-ci"}"

# Backend: "veribench_proxy" (cluster only) or "anthropic_direct" (works from any host with key)
: "${judge_backend:=anthropic_direct}"
: "${anthropic_model:=claude-sonnet-4-5}"
: "${anthropic_temperature:=0.7}"
: "${anthropic_max_tokens:=1024}"

# Auto-load Anthropic key for anthropic_direct backend if not already exported
if [ "$judge_backend" = "anthropic_direct" ] && [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -f "$HOME/keys/anthropic_bm_key_koyejolab.txt" ]; then
    export ANTHROPIC_API_KEY="$(cat "$HOME/keys/anthropic_bm_key_koyejolab.txt")"
fi

EXTRA_FLAGS=("--judge_backend" "$judge_backend" \
             "--anthropic_model" "$anthropic_model" \
             "--anthropic_temperature" "$anthropic_temperature" \
             "--anthropic_max_tokens" "$anthropic_max_tokens")
[ "${bootstrap:-0}" = "1" ] && EXTRA_FLAGS+=("--bootstrap")
[ "${wandb_off:-0}" = "1" ] && EXTRA_FLAGS+=("--wandb_off")

# ------------------- venv -------------------
command -v deactivate >/dev/null 2>&1 && deactivate || true
# Prefer cert-judge venv (arm64-correct on Apple Silicon). Fall back to veribench.
if [ -d "$HOME/uv_envs/cert-judge" ]; then
    # shellcheck source=/dev/null
    source "$HOME/uv_envs/cert-judge/bin/activate"
elif [ -d "$HOME/uv_envs/veribench" ]; then
    # shellcheck source=/dev/null
    source "$HOME/uv_envs/veribench/bin/activate"
fi

# ------------------- echo run config -------------------
echo "=================================================================="
echo "P2 bug-ladder with CI"
echo "=================================================================="
echo "Backend:             $judge_backend"
echo "Model (proxy):       ${TRACE_CUSTOMLLM_MODEL:-(unset)}"
echo "Model (anthropic):   $anthropic_model"
echo "Bug ladder:          $bug_ladder_path"
echo "Judge prompt:        $judge_prompt_temp_path"
echo "max_score:           $max_score"
echo "num_samples (S):     $num_samples"
echo "max_workers:         $max_workers"
echo "output_dir:          $output_dir"
echo "wandb_project:       $wandb_project"
echo "extra flags:         ${EXTRA_FLAGS[*]:-(none)}"
echo "=================================================================="

# ------------------- run -------------------
time python "$(dirname "$0")/run_p2_bug_ladder_with_ci.py" \
    --bug_ladder_path "$bug_ladder_path" \
    --judge_prompt_temp_path "$judge_prompt_temp_path" \
    --output_dir "$output_dir" \
    --max_score "$max_score" \
    --num_samples "$num_samples" \
    --max_workers "$max_workers" \
    --wandb_project "$wandb_project" \
    "${EXTRA_FLAGS[@]}"
