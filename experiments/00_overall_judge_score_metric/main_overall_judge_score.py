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
    Main function to run real HSJ judge evaluation on actual data files.
    
    Args:
        **kwargs: Keyword arguments containing:
            mode (str): "online" for real LLM calls, "dryrun" for testing
            eval_mode (str): "hsj_real" to run actual evaluation
            claude_dotenv_path (str): Path to .env file with LLM credentials
            judge_prompt_temp_path (str): Path to LLM judge prompt template file
            max_score (int): Maximum score value (e.g., 30 for 0-30 scale)
            paths_p1 (list): List of directories for P1 reflexivity testing
            path_p2 (str): Path to bug ladder directory for P2
            path_p3 (str): Path to missing specs ladder directory for P3
            num_llm_judge_calls_per_file_pair (int): Repeat count for P4 variance (default: 5)
            max_workers (int, optional): Number of concurrent threads (default: 24)
    """
    from pathlib import Path
    import re
    from veribench.metrics.sim_file_eq_llm_judge import get_sim_score_file_eq_llm_result_in_json_str
    _ensure_cert_judge_on_path()
    from cert_judge.hsj_scoring import (
        compute_p1_identity,
        compute_p2_or_p3_ordering_auc,
        compute_p4_stability,
        compute_p5_tvd_mi,
        compute_jti,
    )
    from cert_judge.tvd_mi_tools import (
        tvd_mi_from_critic,
        per_item_auc_macro,
    )
    
    # Environment variables should already be loaded by the shell script
    # The shell script exports them BEFORE Python starts to ensure correct defaults
    # during module imports (especially veribench.agent.theorem_writing_llm_judge)
    claude_dotenv_path = kwargs.get("claude_dotenv_path", "")
    if claude_dotenv_path:
        logger.info(f"Note: Environment should be loaded by shell script from {claude_dotenv_path}")
        logger.info(f"Current TRACE_CUSTOMLLM_MODEL: {os.environ.get('TRACE_CUSTOMLLM_MODEL', 'NOT SET')}")
    
    # Read prompt template
    prompt_path = Path(kwargs.get("judge_prompt_temp_path", "")).expanduser().resolve()
    prompt_template = prompt_path.read_text(encoding="utf-8")
    
    max_score = int(kwargs.get("max_score", 30))
    paths_p1 = kwargs.get("paths_p1", [])
    path_p2 = kwargs.get("path_p2", "")
    path_p3 = kwargs.get("path_p3", "")
    repeats = int(kwargs.get("num_llm_judge_calls_per_file_pair", 5))
    
    def list_lean_files(dir_path: str):
        p = Path(dir_path).expanduser()
        if not p.exists() or not p.is_dir():
            return []
        return sorted([q for q in p.iterdir() if q.is_file() and q.suffix == ".lean"])
    
    def score_pair(agent_fp: Path, gold_fp: Path, s_idx: int, n_idx: int):
        res = get_sim_score_file_eq_llm_result_in_json_str(
            agent_filepath=agent_fp,
            gold_filepath=gold_fp,
            file_equiv_prompt_template=prompt_template,
            max_score=max_score,
            s_idx=s_idx,
            n_idx=n_idx,
            relative_path=agent_fp.name,
        )
        return float(res.get("normalized_score", 0.0))
    
    def build_ladder(dir_path: str):
        items = []
        for fp in list_lean_files(dir_path):
            m = re.search(r"_(\d+)_bugs\.lean$", fp.name)
            if not m:
                m = re.search(r"_(\d+)_missing\.lean$", fp.name)
            if m:
                items.append((int(m.group(1)), fp))
        items.sort(key=lambda t: t[0])
        return items
    
    # P1: Identity/Reflexivity scores
    logger.info("Computing P1: Reflexivity & Consistency")
    identity_scores = []
    for dir_path in paths_p1:
        for fp in list_lean_files(dir_path):
            try:
                identity_scores.append(score_pair(fp, fp, s_idx=0, n_idx=0))
                logger.info(f"P1: Scored {fp.name}")
            except Exception as e:
                logger.warning(f"P1 scoring failed for {fp}: {e}")
    p1 = compute_p1_identity(identity_scores) if identity_scores else 0.0
    logger.info(f"P1 = {p1:.4f} (from {len(identity_scores)} identity pairs)")
    
    # P2: Bug monotonicity
    logger.info("Computing P2: Monotonicity to Bugs")
    p2_counts, p2_scores = [], []
    if path_p2:
        ladder = build_ladder(path_p2)
        gold_fp = next((fp for k, fp in ladder if k == 0), ladder[0][1] if ladder else None)
        for k, fp in ladder:
            try:
                s = score_pair(fp, gold_fp, s_idx=0, n_idx=k)
                p2_counts.append(k)
                p2_scores.append(s)
                logger.info(f"P2: {k} bugs -> score {s:.4f}")
            except Exception as e:
                logger.warning(f"P2 scoring failed for {fp}: {e}")
    p2 = compute_p2_or_p3_ordering_auc(p2_counts, p2_scores) if p2_counts else 0.0
    logger.info(f"P2 = {p2:.4f}")
    
    # P3: Missing spec monotonicity
    logger.info("Computing P3: Monotonicity to Missing Specs")
    p3_counts, p3_scores = [], []
    if path_p3:
        ladder3 = build_ladder(path_p3)
        gold3_fp = next((fp for k, fp in ladder3 if k == 0), ladder3[0][1] if ladder3 else None)
        for k, fp in ladder3:
            try:
                s = score_pair(fp, gold3_fp, s_idx=0, n_idx=k)
                p3_counts.append(k)
                p3_scores.append(s)
                logger.info(f"P3: {k} missing -> score {s:.4f}")
            except Exception as e:
                logger.warning(f"P3 scoring failed for {fp}: {e}")
    p3 = compute_p2_or_p3_ordering_auc(p3_counts, p3_scores) if p3_counts else 0.0
    logger.info(f"P3 = {p3:.4f}")
    
    # P4: Stability/Variance
    logger.info("Computing P4: Low Variance (Stability)")
    repeat_scores_by_item = {}
    # Sample 20 files from P1 paths for repeated scoring (for full VeriBench coverage)
    id_pairs = []
    for dir_path in paths_p1:
        id_pairs.extend(list_lean_files(dir_path))
        if len(id_pairs) >= 20:
            break
    id_pairs = id_pairs[:20]
    
    for fp in id_pairs:
        key = f"p1::{fp.name}"
        vals = []
        for r in range(repeats):
            try:
                vals.append(score_pair(fp, fp, s_idx=r, n_idx=r))
            except Exception as e:
                logger.warning(f"P4 repeat {r} failed for {fp}: {e}")
        if vals:
            repeat_scores_by_item[key] = vals
            logger.info(f"P4: {fp.name} -> {len(vals)} repeats, variance={sum((v-sum(vals)/len(vals))**2 for v in vals)/len(vals):.6f}")
    
    p4 = compute_p4_stability(repeat_scores_by_item, tau=0.05) if repeat_scores_by_item else 0.0
    logger.info(f"P4 = {p4:.4f}")
    
    # P5: TVD-MI (Information-Relationship Robustness)
    logger.info("Computing P5: TVD-MI (Information-Relationship Robustness)")
    
    # Build pairwise dataset for TVD-MI
    # Same-source pairs: Use identity comparisons from P1 (file vs itself)
    # Different-source pairs: Compare different files
    y_true_same_source = []
    y_pred_critic_labels = []
    pair_scores_p5 = []
    pair_class_p5 = []
    item_ids_p5 = []
    
    # Collect same-source pairs (identity comparisons)
    all_files_p5 = []
    for dir_path in paths_p1:
        all_files_p5.extend(list_lean_files(dir_path))
    
    # Sample up to 50 files for P5 to keep computation tractable
    import random
    random.seed(42)
    sampled_files_p5 = all_files_p5[:50] if len(all_files_p5) <= 50 else random.sample(all_files_p5, 50)
    
    logger.info(f"P5: Building pairwise dataset from {len(sampled_files_p5)} files")
    
    # Same-source pairs: file vs itself
    for idx, fp in enumerate(sampled_files_p5):
        try:
            score = score_pair(fp, fp, s_idx=0, n_idx=0)
            y_true_same_source.append(True)
            pair_scores_p5.append(score)
            pair_class_p5.append(1)  # 1 = same source
            item_ids_p5.append(idx)
            
            # Convert score to categorical critic label
            # High score (>0.85) → "Significant Gain" (same source)
            # Medium score (0.5-0.85) → "Little Gain"
            # Low score (<0.5) → "No Gain" (different sources)
            if score > 0.85:
                y_pred_critic_labels.append("Significant Gain")
            elif score > 0.5:
                y_pred_critic_labels.append("Little Gain")
            else:
                y_pred_critic_labels.append("No Gain")
        except Exception as e:
            logger.warning(f"P5 same-source pair failed for {fp}: {e}")
    
    # Different-source pairs: compare different files (sample pairs to avoid O(n²))
    n_diff_pairs = min(len(sampled_files_p5), 50)  # Match number of same-source pairs
    for i in range(n_diff_pairs):
        try:
            fp1 = sampled_files_p5[i]
            fp2 = sampled_files_p5[(i + len(sampled_files_p5)//2) % len(sampled_files_p5)]
            if fp1 == fp2:
                continue
            
            score = score_pair(fp1, fp2, s_idx=0, n_idx=0)
            y_true_same_source.append(False)
            pair_scores_p5.append(score)
            pair_class_p5.append(0)  # 0 = different source
            item_ids_p5.append(i)
            
            # Convert to categorical label
            if score > 0.85:
                y_pred_critic_labels.append("Significant Gain")
            elif score > 0.5:
                y_pred_critic_labels.append("Little Gain")
            else:
                y_pred_critic_labels.append("No Gain")
        except Exception as e:
            logger.warning(f"P5 different-source pair failed: {e}")
    
    # Compute P5 components
    p5_youdens_j = 0.0
    p5_auc_macro = 0.5
    p5_delta_auc_tamper = 0.1  # Conservative default
    
    if len(y_true_same_source) > 0 and len(y_pred_critic_labels) > 0:
        try:
            # Compute Youden's J via TVD-MI
            tvd_report = tvd_mi_from_critic(y_true_same_source, y_pred_critic_labels)
            p5_youdens_j = tvd_report.youdens_j
            logger.info(f"P5: Youden's J = {p5_youdens_j:.4f} (TPR={tvd_report.tpr:.4f}, TNR={tvd_report.tnr:.4f})")
            
            # Compute item-level macro AUC
            if len(pair_scores_p5) > 0 and len(set(pair_class_p5)) > 1:
                p5_auc_macro, _ = per_item_auc_macro(item_ids_p5, pair_scores_p5, pair_class_p5)
                logger.info(f"P5: Macro AUC = {p5_auc_macro:.4f}")
            
            # Estimate tamper resistance from P4 variance
            # High variance in P4 suggests vulnerability to perturbations
            if repeat_scores_by_item:
                variances = [
                    sum((v - sum(scores)/len(scores))**2 for v in scores) / len(scores)
                    for scores in repeat_scores_by_item.values()
                    if len(scores) > 1
                ]
                if variances:
                    avg_var = sum(variances) / len(variances)
                    # Map variance to tamper drop: higher variance → higher drop
                    p5_delta_auc_tamper = min(0.5, avg_var * 10)  # Scale to [0, 0.5]
                    logger.info(f"P5: Estimated tamper AUC drop = {p5_delta_auc_tamper:.4f} (from P4 variance)")
        except Exception as e:
            logger.warning(f"P5 computation failed: {e}")
    
    # Compute final P5 score
    p5 = compute_p5_tvd_mi(p5_youdens_j, p5_auc_macro, p5_delta_auc_tamper)
    logger.info(f"P5 = {p5:.4f}")
    
    # Judge Trust Index (now with P5)
    jti = compute_jti(p1, p2, p3, p4, p5=p5)
    logger.info(f"JTI (5-property) = {jti:.4f}")
    
    return {
        "p1": p1,
        "p2": p2,
        "p3": p3,
        "p4": p4,
        "p5": p5,
        "jti": jti,
        "identity_scores": identity_scores,
        "p2_counts": p2_counts,
        "p2_scores": p2_scores,
        "p3_counts": p3_counts,
        "p3_scores": p3_scores,
        "repeat_scores": repeat_scores_by_item,
        "p5_youdens_j": p5_youdens_j,
        "p5_auc_macro": p5_auc_macro,
        "p5_delta_auc_tamper": p5_delta_auc_tamper,
    }

def _main(**kwargs):
    # Allow a local demo path without WANDB by branching before imports
    eval_mode = kwargs.get("eval_mode", "").lower()
    
    # Handle real HSJ evaluation
    if eval_mode == "hsj_real":
        logger.info('Starting REAL HSJ evaluation with actual LLM judge calls')
        from datetime import datetime
        from socket import gethostname
        import wandb
        start_time = time.time()

        today = datetime.now().strftime("%Y_m%m_d%d_t%Hh_%Mm_%Ss")
        kwargs = kwargs | {
            "today": today,
            "hostname": gethostname(),
        }
        logger.info(f'Wandb mode: {kwargs.get("mode", "dryrun")}')
        run_name = f"hsj_real_{today}"
        run = wandb.init(
            entity="brando-su",
            project="vb-thm-eq",
            mode=kwargs.get("mode", "dryrun"),
            name=run_name,
            save_code=True,
            config=kwargs,
        )
        wandb.save(__file__)
        logger.info(f"Starting real HSJ eval run: {kwargs}")
        
        # Run main evaluation
        res = main(**kwargs)
        logger.info(f'Real HSJ evaluation result: {res}')
        
        # Log to wandb
        elapsed_time = time.time() - start_time
        wandb.log({
            "p1": res["p1"],
            "p2": res["p2"],
            "p3": res["p3"],
            "p4": res["p4"],
            "p5": res["p5"],
            "jti": res["jti"],
            "p5_youdens_j": res.get("p5_youdens_j", 0.0),
            "p5_auc_macro": res.get("p5_auc_macro", 0.5),
            "p5_delta_auc_tamper": res.get("p5_delta_auc_tamper", 0.1),
            "elapsed_time_seconds": elapsed_time,
            "elapsed_time_minutes": elapsed_time / 60,
            "elapsed_time_hours": elapsed_time / 3600,
        })
        
        run.alert(title="HSJ Eval Completed", text=f"JTI={res['jti']:.4f}, P1={res['p1']:.4f}, P2={res['p2']:.4f}, P3={res['p3']:.4f}, P4={res['p4']:.4f}, P5={res['p5']:.4f}")
        logger.info(f"Run completed. URL: {run.get_url()}")
        print(f"{run.get_url()=}")
        print(f"\aTime taken: {elapsed_time:.2f} seconds, or {elapsed_time / 60:.2f} minutes, or {elapsed_time / 3600:.2f} hours.\a")
        wandb.finish()
        return res
    
    # Handle demo mode (synthetic data)
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
    parser.add_argument("--eval_mode", default="hsj_demo", help="hsj_demo for synthetic test, hsj_real for actual eval")
    parser.add_argument("--mode", default="dryrun", help="online for wandb logging, dryrun for local")
    parser.add_argument("--claude_dotenv_path", default="", help="Path to .env file with LLM credentials")
    parser.add_argument("--judge_prompt_temp_path", default="", help="Path to judge prompt template")
    parser.add_argument("--max_score", type=int, default=30, help="Maximum score value")
    parser.add_argument("--paths_p1", nargs='*', default=[], help="Directories for P1 reflexivity testing")
    parser.add_argument("--path_p2", default="", help="Bug ladder directory for P2")
    parser.add_argument("--path_p3", default="", help="Missing specs ladder directory for P3")
    parser.add_argument("--num_llm_judge_calls_per_file_pair", type=int, default=5, help="Repeats for P4 variance")
    parser.add_argument("--max_workers", type=int, default=24, help="Concurrent threads")
    args, unknown = parser.parse_known_args()
    _main(**vars(args))
    elapsed_time = time.time() - start_time
    logger.info(f"Script execution completed in {elapsed_time:.2f} seconds")
    print(f"\aTime taken: {elapsed_time:.2f} seconds, or {elapsed_time / 60:.2f} minutes, or {elapsed_time / 3600:.2f} hours.\a")
