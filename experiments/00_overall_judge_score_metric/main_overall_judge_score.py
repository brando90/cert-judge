import os
from typing import Any, Dict
import time
import logging
from pathlib import Path
from statistics import mean
import sys


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Minimal logger setup for this script (avoids external deps)."""
    logger = logging.getLogger("cert_judge")
    if not logger.handlers:
        logger.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        fmt = logging.Formatter("->%(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    return logger


def _ensure_cert_judge_on_path() -> None:
    """Ensure cert-judge/py_src is on sys.path for local execution."""
    here = Path(__file__).resolve()
    repo_root = here.parents[2]  # .../cert-judge
    py_src = repo_root / "py_src"
    if str(py_src) not in sys.path:
        sys.path.insert(0, str(py_src))


# Configure logging early
logger = configure_logging()
logger = logging.getLogger(__name__)


def log_prompt_template_to_wandb(prompt_template_path, eval_mode):
    """Log the prompt template to wandb"""
    # Get prompt content
    prompt_path = Path(prompt_template_path).expanduser().resolve()
    with open(prompt_path, 'r', encoding='utf-8') as prompt_file:
        prompt_template_content: str = prompt_file.read()
    prompt_template_fragment: str = prompt_template_content[:1000] + "..." if len(prompt_template_content) > 1000 else prompt_template_content
    logger.info(f"Prompt template content: {prompt_template_fragment}")
    # Create wandb artifact
    prompt_artifact = wandb.Artifact(
        name=f"prompt_template_{eval_mode}", 
        type="prompt_template",
        description=f"LLM judge prompt template used for {eval_mode} evaluation"
    )
    # Save prompt to a temporary file and add to artifact
    # - it has to be a temporary file because wandb artifacts only support file paths, not strings or dicts
    temp_prompt_filename = f"/tmp/prompt_template_{eval_mode}.txt"
    with open(temp_prompt_filename, 'w', encoding='utf-8') as prompt_file:
        prompt_file.write(prompt_template_content)
    prompt_artifact.add_file(temp_prompt_filename)
    wandb.log_artifact(prompt_artifact)
    # log the prompt content to wandb config
    wandb.config.update({
        "prompt_template_path": str(prompt_template_path),
        "prompt_template_content": prompt_template_fragment,
        "eval_mode": eval_mode
    })
    logger.info(f"Logged prompt template to wandb with prompt path: {prompt_template_path}")

def log_model_info_to_wandb(model_name: str, api_url: str, eval_mode: str) -> None:
    """Log the model info to wandb"""
    wandb.config.update({
        "llm_model_name": model_name,
        "llm_api_url": api_url,
        "eval_mode": eval_mode
    })
    logger.info(f"Logged model info to wandb with model name: {model_name} and api url: {api_url}")

def main(**kwargs) -> Dict[str, Any]:
    """
    Main function to evaluate file equivalence between agent and gold files using LLM judge.
    
    Args:
        **kwargs: Keyword arguments containing:
            mode (str): "online" for real LLM calls, "dryrun" for testing
            eval_mode (str): "multiple_scores_multiple_data_points" for variance analysis (recommended)
            agent_path2files (str): Path to directory containing agent-generated files to evaluate
            gold_path2files (str): Path to directory containing gold standard reference files  
            file_equiv_llm_judge_eval_prompt_template_path (str): Path to LLM judge prompt template file
            max_score (int, optional): Maximum score value (default: 30), e.g. max_score=10 means 0-10 scale
            num_llm_judge_calls_per_file_pair (int, optional): How many times to evaluate each file pair for variance analysis (default: 5)
            max_workers (int, optional): Number of concurrent threads for LLM API calls (default: 64)
    """
    pass

def _main(**kwargs):
    # Allow a local demo path without WANDB by branching before imports
    eval_mode = kwargs.get("eval_mode", "").lower()
    if eval_mode == "hsj_demo":
        _ensure_cert_judge_on_path()
        try:
            from cert_judge.hsj_scoring import (
                compute_p1_identity,
                compute_p2_or_p3_ordering_auc,
                compute_p4_stability,
                compute_jti,
                fit_isotonic_calibrator,
                compute_hsj_scores,
            )
        except Exception as e:
            logger.exception("Failed to import cert_judge.hsj_scoring: %s", e)
            return {"ok": False, "error": str(e)}

        # Minimal, synthetic demo to test wiring
        p1 = compute_p1_identity([1.0, 0.99, 1.0, 0.98])
        p2 = compute_p2_or_p3_ordering_auc([0, 1, 2, 3], [0.92, 0.7, 0.5, 0.2])
        p3 = compute_p2_or_p3_ordering_auc([0, 1, 2, 3], [0.90, 0.75, 0.6, 0.4])
        p4 = compute_p4_stability({"ex": [0.9, 0.91, 0.89]}, tau=0.05)
        jti = compute_jti(p1, p2, p3, p4)
        fJ = fit_isotonic_calibrator([0.2, 0.5, 0.8], [0.0, 0.5, 1.0])
        fI = fit_isotonic_calibrator([0.1, 0.6, 0.95], [0.0, 0.6, 1.0])
        final = compute_hsj_scores([0.35, 0.55, 0.9], [0.25, 0.5, 0.99], fJ, fI, jti, lambda_gt=0.7, gamma=1.5, jti_red=0.70)
        res = {
            "p1": p1, "p2": p2, "p3": p3, "p4": p4, "jti": jti,
            "final": final,
        }

        # Optionally log to wandb
        mode = kwargs.get("mode", "dryrun")
        try:
            import wandb
            run = wandb.init(
                entity="brando-su",
                project="vb-thm-eq",
                mode=mode,
                name=f"hsj_demo_{int(time.time())}",
                config={
                    "eval_mode": eval_mode,
                    "args": kwargs,
                },
            )
            wandb.log({
                "p1": p1,
                "p2": p2,
                "p3": p3,
                "p4": p4,
                "jti": jti,
                "final_scores_mean": mean(final),
                "final_scores_min": min(final) if final else None,
                "final_scores_max": max(final) if final else None,
            })
            run.finish()
        except Exception as we:
            logger.warning("wandb logging skipped: %s", we)

        print(res)
        logger.info("HSJ demo complete: %s", res)
        return {"ok": True, **res}

    logger.info(f'Starting main execution with kwargs: {kwargs}')
    print(f'{kwargs=}')  # Keep this for immediate user feedback
    from datetime import datetime
    from socket import gethostname
    import wandb
    start_time = time.time()

    today = datetime.now().strftime("%Y_m%m_d%d_t%Hh_%Mm_%Ss")  # eg '2024_m01_d22_t13h_00m_30s'
    # os.environ['CUDA_VISIBLE_DEVICES'] = str(kwargs.get('CUDA_VISIBLE_DEVICES', '7'))
    tmux_sess_num = None
    kwargs = kwargs | {
        "today": today,
        "tmux_sess_num": tmux_sess_num,
        "hostname": gethostname(),
    }
    logger.info(f'Wandb mode: {kwargs.get("mode", "dryrun")}')
    print(f'mode={kwargs.get("mode", "dryrun")}')  # Keep this for immediate user feedback
    run_name = f"{kwargs}"
    run = wandb.init(
        entity="brando-su",
        project="vb-thm-eq",
        mode=kwargs.get("mode", "dryrun"),
        name=run_name,
        save_code=True,
        config=kwargs,
    )
    wandb.save( __file__)  # save current code now, don't wait to wandb.finish, also useful: wandb.save("*.py") # upload all .py files in current directory
    logger.info(f"Starting run with configuration: {kwargs}")
    print(f"Kwargs to run:\n{kwargs}")  # Keep this for immediate user feedback
    
    # - main
    res: dict[str, Any] = main(**kwargs)
    logger.info(f'Main result: {res}')
    
    # - Calculate and log timing metrics before finishing
    elapsed_time = time.time() - start_time
    elapsed_minutes = elapsed_time / 60
    elapsed_hours = elapsed_time / 3600
    
    # Log timing metrics to wandb
    wandb.log({
        "elapsed_time_seconds": elapsed_time,
        "elapsed_time_minutes": elapsed_minutes,
        "elapsed_time_hours": elapsed_hours,
    })
    
    # - finish main run
    run.alert(title="Run Completed", text=f"Run finished in {elapsed_time:.2f}s, run url: {run.get_url()}")
    logger.info(f"Run completed successfully. URL: {run.get_url()}")
    logger.info(f"Total execution time: {elapsed_time:.2f} seconds ({elapsed_minutes:.2f} minutes, {elapsed_hours:.2f} hours)")
    print(f"{run.get_url()=}")  # Keep this for immediate user feedback
    print(f"\aTime taken: {elapsed_time:.2f} seconds, or {elapsed_minutes:.2f} minutes, or {elapsed_hours:.2f} hours.\a")  # Keep this for immediate user feedback
    wandb.finish()


if __name__ == "__main__":
    import time
    start_time = time.time()
    # Always use argparse for predictable CLI parsing
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval_mode", default="")
    parser.add_argument("--mode", default="dryrun")
    parser.add_argument("--judge_prompt_temp_path", default="")
    parser.add_argument("--max_score", default=None)
    parser.add_argument("--paths_p1", nargs='*', default=[])
    parser.add_argument("--path_p2", default="")
    parser.add_argument("--path_p3", default="")
    parser.add_argument("--num_llm_judge_calls_per_file_pair", default=None)
    parser.add_argument("--max_workers", default=None)
    args, unknown = parser.parse_known_args()
    _main(**vars(args))
    elapsed_time = time.time() - start_time
    logger.info(f"Script execution completed in {elapsed_time:.2f} seconds")
    print(f"\aTime taken: {elapsed_time:.2f} seconds, or {elapsed_time / 60:.2f} minutes, or {elapsed_time / 3600:.2f} hours.\a")
