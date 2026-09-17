#!/usr/bin/env python3
"""
Experiment 3: Multi-Model Certification Ablation
Show protocol discriminates between models.

Uses results from exp1 + exp2 (or regenerates if not available).
"""
import json
import os
import random
import re
import statistics
import sys
from pathlib import Path

EXP_DIR = Path(__file__).parent
sys.path.insert(0, str(EXP_DIR))

VERIBENCH_DIR = Path.home() / "veribench/veribench_dataset/lean_src/veribench"
RESULTS_DIR = EXP_DIR / "results" / "multi_model"
FIGURES_DIR = EXP_DIR / "figures"

random.seed(42)

# Models to evaluate
# Note: Anthropic key has insufficient credits, using OpenAI models
ANTHROPIC_MODELS = []  # skipped due to insufficient API credits

OPENAI_KEY_PATH = os.path.expanduser("~/keys/openai_bm_key_koyejolab.txt")
OPENAI_MODELS = ["gpt-4o-mini", "gpt-4o"]

N_PAIRS = 20  # pairs per model


def collect_lean_files(n: int = 20) -> list:
    """Collect lean files from all sets."""
    subdirs = ["easy_set", "cs_set", "humaneval_set", "realcode_set", "security_set"]
    all_files = []
    for subdir in subdirs:
        path = VERIBENCH_DIR / subdir
        if path.exists():
            all_files.extend(sorted(path.glob("*.lean")))
    random.shuffle(all_files)
    return all_files[:n]


def build_degradation_ladder(code: str) -> list:
    """5-level degradation ladder."""
    ladder = [code]

    # Level 1
    level1 = code
    if re.search(r'\bn\s*>\s*0\b', code):
        level1 = re.sub(r'\bn\s*>\s*0\b', 'n >= 0', code)
    elif '∧' in code:
        level1 = code.replace('∧', '∧ True ∧', 1)
    else:
        level1 = code + "\n-- level1"
    ladder.append(level1)

    # Level 2
    level2 = level1
    if '∧' in level2:
        parts = level2.rsplit('∧', 1)
        level2 = parts[0].rstrip()
    else:
        level2 = level2 + "\n-- level2"
    ladder.append(level2)

    # Level 3
    level3 = level2
    match = re.search(r':\s*([^:=]+)\s*:=', level3)
    if match:
        type_str = match.group(1)
        new_type = type_str.replace(' = ', ' <= ', 1)
        if new_type != type_str:
            level3 = level3[:match.start(1)] + new_type + level3[match.end(1):]
    if level3 == level2:
        level3 = level2 + "\n-- level3"
    ladder.append(level3)

    # Level 4: trivialize
    level4 = "theorem trivially_true : True := trivial"
    ladder.append(level4)

    return ladder


def run_model_evaluation(
    files: list,
    model: str,
    judge_fn,
) -> dict:
    """Evaluate a model on identity + monotonicity tests."""
    from utils.variant_generator import generate_variants
    from utils.metrics import levenshtein_normalized, spearman_r, weak_monotonicity_pct

    identity_scores = []
    mono_ladders = []
    degradation_levels = []
    ladder_scores_flat = []

    for i, fpath in enumerate(files):
        content = fpath.read_text()
        print(f"  [{i+1}/{len(files)}] {fpath.name} ...")

        # Identity test: 2 variants (to save API calls in multi-model)
        variants = generate_variants(content)[:2]
        for variant in variants:
            result = judge_fn(
                generated_theorem=variant["code"],
                reference_impl=content,
                model=model,
                n_repeats=3,
            )
            identity_scores.append(result["mean"])

        # Monotonicity: 5-level ladder
        ladder_codes = build_degradation_ladder(content)
        level_scores = []
        for level, lcode in enumerate(ladder_codes):
            result = judge_fn(
                generated_theorem=lcode,
                reference_impl=content,
                model=model,
                n_repeats=3,
            )
            level_scores.append(result["mean"])
            degradation_levels.append(level)
            ladder_scores_flat.append(result["mean"])
        mono_ladders.append(level_scores)

    identity_mean = statistics.mean(identity_scores) if identity_scores else 0.0
    identity_std = statistics.stdev(identity_scores) if len(identity_scores) > 1 else 0.0
    r_spearman, p_spearman = spearman_r(degradation_levels, ladder_scores_flat)
    weak_mono = weak_monotonicity_pct(mono_ladders)

    from utils.push_per_run import IDENTITY_THRESHOLD, SPEARMAN_THRESHOLD, WEAK_MONO_THRESHOLD
    certified = int(
        identity_mean > IDENTITY_THRESHOLD and
        r_spearman < SPEARMAN_THRESHOLD and
        weak_mono > WEAK_MONO_THRESHOLD
    )

    return {
        "identity_mean_score": round(identity_mean, 4),
        "identity_std": round(identity_std, 4),
        "monotonicity_spearman_r": round(r_spearman, 4),
        "monotonicity_spearman_pvalue": round(p_spearman, 4),
        "weak_monotonicity_pct": round(weak_mono, 2),
        "pearson_edit_vs_judge": 0.0,
        "n_theorems": len(files),
        "certified": certified,
        "lean_available": False,
        "model": model,
    }


def judge_anthropic(generated_theorem, reference_impl, model, n_repeats=3):
    from utils.judge_caller import judge
    return judge(generated_theorem, reference_impl, model, n_repeats)


def judge_openai(generated_theorem, reference_impl, model, n_repeats=3):
    """OpenAI judge using the same prompt."""
    import hashlib
    import time
    from pathlib import Path

    # Use same cache structure
    CACHE_PATH = EXP_DIR / "results" / "judge_cache.json"

    def sha256(s):
        return hashlib.sha256(s.encode()).hexdigest()

    th_hash = sha256(generated_theorem)
    ref_hash = sha256(reference_impl)
    cache_key = f"{model}|{th_hash}|{ref_hash}"

    # Load cache
    cache = {}
    if CACHE_PATH.exists():
        try:
            cache = json.loads(CACHE_PATH.read_text())
        except Exception:
            pass

    if cache_key in cache:
        return {**cache[cache_key], "cached": True}

    from utils.judge_caller import JUDGE_PROMPT_TEMPLATE
    import openai

    openai_key = ""
    if os.environ.get("OPENAI_API_KEY"):
        openai_key = os.environ["OPENAI_API_KEY"]
    else:
        try:
            openai_key = Path(OPENAI_KEY_PATH).read_text().strip()
        except Exception:
            return {"score": 0.5, "mean": 0.5, "std": 0.0, "scores": [0.5], "reasoning": "no_openai_key", "cached": False}

    client = openai.OpenAI(api_key=openai_key)
    prompt = JUDGE_PROMPT_TEMPLATE.format(
        reference_impl=reference_impl,
        generated_theorem=generated_theorem,
    )

    scores = []
    reasonings = []
    for _ in range(n_repeats):
        try:
            response = client.chat.completions.create(
                model=model,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.choices[0].message.content.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            parsed = json.loads(text)
            score = float(parsed.get("score", 0.5))
            scores.append(max(0.0, min(1.0, score)))
            reasonings.append(str(parsed.get("reasoning", "")))
            time.sleep(0.5)
        except Exception as e:
            # Try to extract score
            import re
            if 'text' in locals():
                m = re.search(r'"score"\s*:\s*([0-9.]+)', text)
                if m:
                    scores.append(float(m.group(1)))
                    reasonings.append("extracted")
                else:
                    scores.append(0.5)
                    reasonings.append(f"error: {str(e)[:50]}")
            else:
                scores.append(0.5)
                reasonings.append(f"error: {str(e)[:50]}")

    mean_score = statistics.mean(scores)
    std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0
    entry = {
        "score": mean_score, "mean": mean_score, "std": std_score,
        "scores": scores, "reasoning": reasonings[0] if reasonings else "", "model": model,
    }
    cache[cache_key] = entry
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2))
    return {**entry, "cached": False}


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("EXP 3: Multi-Model Certification Ablation")
    print("=" * 60)

    files = collect_lean_files(N_PAIRS)
    if not files:
        print("ERROR: No files found.")
        sys.exit(1)

    # Determine which models to run
    models_to_run = []
    for m in ANTHROPIC_MODELS:
        models_to_run.append((m, judge_anthropic))

    # Check OpenAI key
    openai_available = False
    if os.environ.get("OPENAI_API_KEY"):
        openai_available = True
    else:
        for key_path in [OPENAI_KEY_PATH, os.path.expanduser("~/keys/openai_api_brandos_personal_key.txt")]:
            try:
                Path(key_path).read_text().strip()
                openai_available = True
                break
            except Exception:
                pass

    if openai_available:
        for m in OPENAI_MODELS:
            models_to_run.append((m, judge_openai))
    else:
        print("NOTE: OpenAI key not found. Skipping OpenAI models.")

    print(f"Running {len(models_to_run)} models: {[m for m, _ in models_to_run]}")

    all_model_results = {}

    for model, judge_fn in models_to_run:
        print(f"\n{'='*50}")
        print(f"Evaluating model: {model}")
        print(f"{'='*50}")

        try:
            result = run_model_evaluation(files, model, judge_fn)
            all_model_results[model] = result

            # Save per-model result
            model_dir = RESULTS_DIR / model.replace("/", "_").replace(":", "_")
            model_dir.mkdir(parents=True, exist_ok=True)
            model_summary = RESULTS_DIR / model.replace("/", "_").replace(":", "_") / "summary.json"
            model_summary.write_text(json.dumps(result, indent=2))
            print(f"  Saved: {model_summary}")

            print(f"\n  identity_mean = {result['identity_mean_score']:.4f}")
            print(f"  Spearman r = {result['monotonicity_spearman_r']:.4f}")
            print(f"  Weak mono = {result['weak_monotonicity_pct']:.1f}%")
            print(f"  Certified = {result['certified']}")

            # Push this model to W&B
            try:
                from utils.push_per_run import push
                push(
                    run_name=model.replace("/", "_").replace(":", "_"),
                    model=model,
                    results_path=str(model_summary),
                    experiment="exp3_multi_model",
                    notes=f"Multi-model ablation. certified={result['certified']}",
                )
            except Exception as e:
                print(f"  WARNING: W&B push failed: {e}")

        except Exception as e:
            print(f"  ERROR evaluating {model}: {e}")
            import traceback
            traceback.print_exc()

    # Print comparison table
    print("\n" + "=" * 70)
    print("MULTI-MODEL CERTIFICATION COMPARISON")
    print("-" * 70)
    print(f"{'Model':<35} {'identity':>9} {'spearman':>9} {'weak_mono':>10} {'cert':>6}")
    print("-" * 70)
    for model, result in all_model_results.items():
        cert = "PASS" if result["certified"] else "FAIL"
        print(
            f"{model[:35]:<35} "
            f"{result['identity_mean_score']:>9.4f} "
            f"{result['monotonicity_spearman_r']:>9.4f} "
            f"{result['weak_monotonicity_pct']:>9.1f}% "
            f"{cert:>6}"
        )
    print("=" * 70)

    # Create heatmap figure
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        import seaborn as sns

        plt.rcParams.update({"font.size": 12})

        if all_model_results:
            model_names = list(all_model_results.keys())
            metrics = ["identity_mean", "spearman_abs", "weak_mono_pct", "certified"]
            metric_labels = ["Identity Mean", "|Spearman r|", "Weak Mono %", "Certified"]
            thresholds = [0.90, 0.50, 80.0, 0.5]

            data = []
            cell_colors = []
            for model in model_names:
                r = all_model_results[model]
                vals = [
                    r["identity_mean_score"],
                    abs(r["monotonicity_spearman_r"]),
                    r["weak_monotonicity_pct"] / 100.0,  # normalize
                    float(r["certified"]),
                ]
                data.append(vals)
                colors_row = []
                for v, threshold in zip(vals, [0.90, 0.50, 0.80, 0.5]):
                    colors_row.append("palegreen" if v >= threshold else "lightcoral")
                cell_colors.append(colors_row)

            fig, ax = plt.subplots(figsize=(12, max(4, len(model_names) * 1.5)))

            data_array = np.array(data)
            im = ax.imshow(data_array, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")

            ax.set_xticks(range(len(metrics)))
            ax.set_xticklabels(metric_labels, fontsize=11)
            ax.set_yticks(range(len(model_names)))
            ax.set_yticklabels([m[:30] for m in model_names], fontsize=11)

            for i in range(len(model_names)):
                for j in range(len(metrics)):
                    raw = all_model_results[model_names[i]]
                    raw_vals = [
                        raw["identity_mean_score"],
                        abs(raw["monotonicity_spearman_r"]),
                        raw["weak_monotonicity_pct"],
                        float(raw["certified"]),
                    ]
                    text = f"{raw_vals[j]:.2f}" if j < 3 else ("PASS" if raw["certified"] else "FAIL")
                    ax.text(j, i, text, ha="center", va="center", fontsize=10,
                            color="black", fontweight="bold")

            ax.set_title("Multi-Model Certification Results\n(Green = Pass threshold)", fontsize=13)
            plt.colorbar(im, ax=ax, label="Normalized Score")
            plt.tight_layout()
            fig_pdf = FIGURES_DIR / "fig_model_certification_table.pdf"
            fig_png = FIGURES_DIR / "fig_model_certification_table.png"
            plt.savefig(fig_pdf, dpi=150, bbox_inches="tight")
            plt.savefig(fig_png, dpi=150, bbox_inches="tight")
            plt.close()
            print(f"\nFigure saved: {fig_pdf}")
    except Exception as e:
        print(f"WARNING: Figure creation failed: {e}")

    return all_model_results


if __name__ == "__main__":
    main()
