# Note: 

# let's score our current llm judge
export mode=online

# path to veribench test dataset/benchmark
export gold_path2files="$HOME/veribench/veribench_dataset/lean_src/veribench"
# llm judge args (in the python code it will be a llm judge object/class, implement it if not there)
# path to claude .env file
export claude_dotenv_path="$HOME/cert-judge/experiments/.env_claude_3_7"
# export claude_dotenv_path2="$HOME/cert-judge/experiments/.env_claude_3_5_v1"
# export claude_dotenv_path3="$HOME/cert-judge/experiments/.env_claude_3_5_v2"
# Load environment variables from .env file BEFORE running Python
# Uncomment exactly one of the following lines:
export $(grep -v "^#" "$claude_dotenv_path" | xargs)
# export $(grep -v "^#" "$HOME/cert-judge/experiments/.env_claude_3_5_v1" | xargs)
# export $(grep -v "^#" "$HOME/cert-judge/experiments/.env_claude_3_5_v2" | xargs)
# export $(grep -v "^#" "$HOME/cert-judge/experiments/.env_sri_claude_3_7" | xargs)
# export $(grep -v "^#" "$HOME/cert-judge/experiments/.env_koyejo_lab_key_claude_3_7" | xargs)
export judge_prompt_temp_path="$HOME/veribench/veribench_prompts/eval_prompts/file_equiv_prompts/simplest_prompt_varying_score_range.txt"
export eval_mode="hsj_real"
export max_score=30 

# for property p1 reflexivity p2 monotonicity wrt bugs p3 monotonicity wrt missing specs p4 low variance/stability
# for p1 it should be able to tell two files are the same even if they have a bug (but are the same file)
# P1: Use FULL VeriBench dataset for identity/reflexivity testing (140 files)
export paths_p1=(
    "/lfs/skampere1/0/brando9/veribench/veribench_dataset/lean_src/veribench/cs_set"
    "/lfs/skampere1/0/brando9/veribench/veribench_dataset/lean_src/veribench/easy_set"
    "/lfs/skampere1/0/brando9/veribench/veribench_dataset/lean_src/veribench/humaneval_set"
    "/lfs/skampere1/0/brando9/veribench/veribench_dataset/lean_src/veribench/real_code"
    "/lfs/skampere1/0/brando9/veribench/veribench_dataset/lean_src/veribench/security_6858"
    "/lfs/skampere1/0/brando9/veribench/veribench_dataset/lean_src/veribench/security_python"
)
# P2 and P3: Use curated bug/missing-spec ladders (these are specifically constructed test sets)
export path_p2="$HOME/cert-judge/data/file_equiv_08_19_2025/my_add_file_eq_with_bugs"
export path_p3="/lfs/skampere1/0/brando9/cert-judge/data/file_equiv_08_19_2025/my_add_file_eq_with_missing_specs"

# P4 (Low Variance/Stability): Number of repeated calls per file to measure consistency
# Higher values give more robust variance estimates (e.g., 10-20 for production)
export num_llm_judge_calls_per_file_pair=${num_llm_judge_calls_per_file_pair:-10}


# run the script to score the judge
command -v deactivate >/dev/null 2>&1 && deactivate || true
source "$HOME/uv_envs/veribench/bin/activate"
export max_workers=${max_workers:-24}
time python ~/cert-judge/experiments/00_overall_judge_score_metric/main_overall_judge_score.py \
    --mode "$mode" \
    --eval_mode "$eval_mode" \
    --claude_dotenv_path "$claude_dotenv_path" \
    --judge_prompt_temp_path "$judge_prompt_temp_path" \
    --max_score "$max_score" \
    --paths_p1 "${paths_p1[@]}" \
    --path_p2 "$path_p2" \
    --path_p3 "$path_p3" \
    --num_llm_judge_calls_per_file_pair "$num_llm_judge_calls_per_file_pair" \
    --max_workers "$max_workers"
