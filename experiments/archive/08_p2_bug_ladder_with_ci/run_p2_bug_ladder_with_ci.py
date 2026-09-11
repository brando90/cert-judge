"""
Experiment 08: P2 (bug-count vs LLM judge score) with proper per-x error bars.

Difference vs the original veribench `experiments/10_file_equiv` plot:
  - Calls the LLM judge N times per bug-count file (configurable, default 15).
  - Aggregates per bug count: mean, std, SE, 95% CI (t-based by default,
    optional percentile bootstrap with --bootstrap).
  - Plots mean +/- 95% CI as ax.errorbar instead of plain scatter.
  - Reports correlations on (a) per-call points (S*N) and (b) per-file means.
  - Saves a raw S x N score matrix to disk and (optionally) WandB.

The judge call uses veribench's get_sim_score_file_eq_llm_result_in_json_str,
matching the convention in experiments/00_overall_cert_judge_metric_with_properties.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.stats import kendalltau, pearsonr, spearmanr, t as student_t


log = logging.getLogger("p2_bug_ladder_with_ci")


# ----------------------------- helpers -----------------------------

def _ensure_cert_judge_on_path() -> None:
    here = Path(__file__).resolve()
    repo_root = here.parents[2]
    py_src = repo_root / "py_src"
    if py_src.exists():
        sys.path.insert(0, str(py_src))
    # Prepend a local fastchat shim so veribench.utils can be imported on
    # macOS without installing torch. The shim lives at _compat/ next to
    # this file. See REPORT.md "Open questions for Ethan" for the rationale.
    compat = here.parent / "_compat"
    if compat.exists():
        sys.path.insert(0, str(compat))
    # Also expose veribench's py_src if present in the standard location.
    vb_py_src = Path("~/veribench/py_src").expanduser()
    if vb_py_src.exists():
        sys.path.insert(0, str(vb_py_src))


def _setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _parse_bug_count(filename: str) -> int | None:
    m = re.search(r"_(\d+)_bugs\.lean$", filename)
    return int(m.group(1)) if m else None


def _list_bug_ladder(bug_dir: Path) -> List[Tuple[int, Path]]:
    """Return sorted [(bug_count, path), ...] for *_<k>_bugs.lean files."""
    items: List[Tuple[int, Path]] = []
    for fp in sorted(bug_dir.iterdir()):
        if fp.is_file() and fp.suffix == ".lean":
            k = _parse_bug_count(fp.name)
            if k is not None:
                items.append((k, fp))
    items.sort(key=lambda t: t[0])
    return items


# ----------------------------- core --------------------------------

@dataclass
class P2RunConfig:
    bug_ladder_path: Path
    judge_prompt_temp_path: Path
    output_dir: Path
    max_score: int = 30
    num_samples: int = 15           # judge calls per bug-count file
    max_workers: int = 16
    bootstrap: bool = False
    bootstrap_iters: int = 2000
    seed: int = 42
    wandb_project: str = "cert-judge-08-p2-bug-ladder-ci"
    wandb_off: bool = False
    judge_backend: str = "veribench_proxy"   # or "anthropic_direct"
    anthropic_model: str = "claude-sonnet-4-5"
    anthropic_temperature: float = 0.7
    anthropic_max_tokens: int = 1024


def _score_one(
    score_fn,
    agent_fp: Path,
    gold_fp: Path,
    prompt_template: str,
    max_score: int,
    s_idx: int,
    n_idx: int,
) -> float:
    res = score_fn(
        agent_filepath=agent_fp,
        gold_filepath=gold_fp,
        file_equiv_prompt_template=prompt_template,
        max_score=max_score,
        s_idx=s_idx,
        n_idx=n_idx,
        relative_path=agent_fp.name,
    )
    return float(res.get("normalized_score", 0.0))


_ANTHROPIC_CLIENT = None

def _get_anthropic_client():
    global _ANTHROPIC_CLIENT
    if _ANTHROPIC_CLIENT is None:
        import anthropic
        key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not key:
            key_path = Path("~/keys/anthropic_bm_key_koyejolab.txt").expanduser()
            if key_path.exists():
                key = key_path.read_text().strip()
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set and ~/keys/anthropic_bm_key_koyejolab.txt missing")
        _ANTHROPIC_CLIENT = anthropic.Anthropic(api_key=key)
    return _ANTHROPIC_CLIENT


def _score_one_anthropic(
    agent_fp: Path,
    gold_fp: Path,
    prompt_template: str,
    max_score: int,
    model: str,
    temperature: float,
    max_tokens: int,
) -> float:
    """Inline of veribench's `<RATIONALE>` + `<SCORE_RESULT>` parser, but
    calling the Anthropic SDK directly. Returns normalized_score in [0,1]
    or NaN on parse/HTTP failure."""
    gold_content = gold_fp.read_text(encoding="utf-8")
    agent_content = agent_fp.read_text(encoding="utf-8")
    prompt = (prompt_template
              .replace("{$GOLD_FILE}", gold_content)
              .replace("{$AGENT_FILE}", agent_content)
              .replace("{$MAX_SCORE}", str(max_score)))
    client = _get_anthropic_client()
    try:
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in msg.content if hasattr(b, "text"))
    except Exception as e:
        log.warning(f"anthropic call failed for {agent_fp.name}: {e}")
        return float("nan")
    m = re.search(r"<SCORE_RESULT>\s*(\d+)\s*</SCORE_RESULT>", text, re.IGNORECASE | re.DOTALL)
    if not m:
        log.warning(f"no <SCORE_RESULT> in response for {agent_fp.name}; first 200 chars: {text[:200]!r}")
        return float("nan")
    raw = int(m.group(1))
    raw = max(0, min(raw, max_score))
    return raw / max_score if max_score else 0.0


def _run_judge_matrix(cfg: P2RunConfig) -> Tuple[np.ndarray, List[int], List[Path], Path]:
    """Returns (raw[S, N], bug_counts[N], file_paths[N], gold_fp)."""
    _ensure_cert_judge_on_path()

    ladder = _list_bug_ladder(cfg.bug_ladder_path)
    if not ladder:
        raise RuntimeError(f"No *_<k>_bugs.lean files found under {cfg.bug_ladder_path}")
    bug_counts = [k for k, _ in ladder]
    file_paths = [fp for _, fp in ladder]

    gold_fp = next((fp for k, fp in ladder if k == 0), file_paths[0])
    log.info(f"Gold reference: {gold_fp.name}")
    log.info(f"Ladder: {len(ladder)} files, bug counts {bug_counts}")

    prompt_template = cfg.judge_prompt_temp_path.expanduser().read_text(encoding="utf-8")

    if cfg.judge_backend == "veribench_proxy":
        from veribench.metrics.sim_file_eq_llm_judge import (
            get_sim_score_file_eq_llm_result_in_json_str,
        )
        def _submit(ex, agent_fp, s_idx, n_idx):
            return ex.submit(
                _score_one,
                get_sim_score_file_eq_llm_result_in_json_str,
                agent_fp, gold_fp, prompt_template, cfg.max_score, s_idx, n_idx,
            )
        log.info("backend=veribench_proxy (uses TRACE_CUSTOMLLM_URL)")
    elif cfg.judge_backend == "anthropic_direct":
        _ = _get_anthropic_client()  # eager-init so a missing key fails before threading
        def _submit(ex, agent_fp, s_idx, n_idx):  # noqa: ARG001 (s_idx unused; sampling diversity comes from temperature)
            return ex.submit(
                _score_one_anthropic,
                agent_fp, gold_fp, prompt_template, cfg.max_score,
                cfg.anthropic_model, cfg.anthropic_temperature, cfg.anthropic_max_tokens,
            )
        log.info(f"backend=anthropic_direct model={cfg.anthropic_model} T={cfg.anthropic_temperature}")
    else:
        raise ValueError(f"Unknown judge_backend: {cfg.judge_backend!r}")

    S, N = cfg.num_samples, len(file_paths)
    raw = np.full((S, N), np.nan, dtype=float)

    log.info(f"Submitting {S * N} judge calls (S={S} samples x N={N} files), max_workers={cfg.max_workers}")
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=cfg.max_workers) as ex:
        fut_to_idx: Dict[Future, Tuple[int, int]] = {}
        for n_idx, agent_fp in enumerate(file_paths):
            for s_idx in range(S):
                fut = _submit(ex, agent_fp, s_idx, n_idx)
                fut_to_idx[fut] = (s_idx, n_idx)

        done = 0
        total = S * N
        for fut in as_completed(fut_to_idx):
            s_idx, n_idx = fut_to_idx[fut]
            try:
                raw[s_idx, n_idx] = fut.result()
            except Exception as e:
                log.warning(f"call failed s={s_idx} n={n_idx} ({file_paths[n_idx].name}): {e}")
            done += 1
            if done % max(1, total // 20) == 0:
                log.info(f"progress {done}/{total} ({100.0 * done / total:.1f}%)")

    log.info(f"Completed {S * N} judge calls in {time.time() - t0:.1f}s")
    return raw, bug_counts, file_paths, gold_fp


# ---------------------- aggregation + stats ------------------------

def _ci_t(values: np.ndarray, alpha: float = 0.05) -> Tuple[float, float, float, float]:
    """Mean and t-based two-sided (1-alpha) CI. Returns (mean, lo, hi, sem)."""
    v = values[~np.isnan(values)]
    n = len(v)
    if n == 0:
        return float("nan"), float("nan"), float("nan"), float("nan")
    mu = float(np.mean(v))
    if n == 1:
        return mu, mu, mu, 0.0
    sd = float(np.std(v, ddof=1))
    sem = sd / np.sqrt(n)
    tcrit = float(student_t.ppf(1 - alpha / 2, df=n - 1))
    return mu, mu - tcrit * sem, mu + tcrit * sem, sem


def _ci_bootstrap(values: np.ndarray, iters: int, seed: int, alpha: float = 0.05) -> Tuple[float, float, float, float]:
    v = values[~np.isnan(values)]
    n = len(v)
    if n == 0:
        return float("nan"), float("nan"), float("nan"), float("nan")
    mu = float(np.mean(v))
    if n == 1:
        return mu, mu, mu, 0.0
    rng = np.random.default_rng(seed)
    boots = rng.choice(v, size=(iters, n), replace=True).mean(axis=1)
    lo = float(np.quantile(boots, alpha / 2))
    hi = float(np.quantile(boots, 1 - alpha / 2))
    sem = float(np.std(boots, ddof=1))
    return mu, lo, hi, sem


def _aggregate(raw: np.ndarray, bug_counts: List[int], cfg: P2RunConfig) -> Dict[str, Any]:
    per_file: List[Dict[str, Any]] = []
    for n_idx, k in enumerate(bug_counts):
        col = raw[:, n_idx]
        if cfg.bootstrap:
            mu, lo, hi, sem = _ci_bootstrap(col, cfg.bootstrap_iters, cfg.seed + n_idx)
        else:
            mu, lo, hi, sem = _ci_t(col)
        per_file.append({
            "bug_count": k,
            "n_samples": int(np.sum(~np.isnan(col))),
            "mean": mu, "ci_lo": lo, "ci_hi": hi, "sem": sem,
            "raw_scores": [None if np.isnan(v) else float(v) for v in col.tolist()],
        })
    return {"per_file": per_file}


def _correlations(xs: np.ndarray, ys: np.ndarray) -> Dict[str, float]:
    mask = ~np.isnan(ys)
    x, y = xs[mask], ys[mask]
    if len(x) < 2 or np.std(x) == 0 or np.std(y) == 0:
        return {"pearson_r": float("nan"), "spearman_rho": float("nan"),
                "kendall_tau": float("nan"), "r2": float("nan")}
    pr, _ = pearsonr(x, y)
    sp, _ = spearmanr(x, y)
    kt, _ = kendalltau(x, y)
    return {"pearson_r": float(pr), "spearman_rho": float(sp),
            "kendall_tau": float(kt), "r2": float(pr ** 2)}


# ----------------------------- plot --------------------------------

def _plot(per_file: List[Dict[str, Any]], corr_per_call: Dict[str, float],
          corr_per_mean: Dict[str, float], cfg: P2RunConfig, model_name: str) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression

    xs = np.array([d["bug_count"] for d in per_file], dtype=float)
    mus = np.array([d["mean"] for d in per_file], dtype=float)
    los = np.array([d["ci_lo"] for d in per_file], dtype=float)
    his = np.array([d["ci_hi"] for d in per_file], dtype=float)
    yerr = np.vstack([mus - los, his - mus])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(xs, mus, yerr=yerr, fmt="o", capsize=4, elinewidth=1.5,
                markersize=8, color="steelblue", ecolor="black", alpha=0.85,
                markeredgecolor="black", markeredgewidth=0.8,
                label=f"mean +/- 95% CI (N={cfg.num_samples})")

    if len(xs) >= 2:
        reg = LinearRegression().fit(xs.reshape(-1, 1), mus)
        x_line = np.linspace(xs.min(), xs.max(), 100)
        ax.plot(x_line, reg.predict(x_line.reshape(-1, 1)), "r--", linewidth=2, alpha=0.85,
                label=f"OLS on means: y = {reg.coef_[0]:.3f}x + {reg.intercept_:.3f}")

    legend_lines = [
        f"Per-call (S*N points):",
        f"  Pearson r = {corr_per_call['pearson_r']:.3f}",
        f"  Spearman rho = {corr_per_call['spearman_rho']:.3f}",
        f"  Kendall tau = {corr_per_call['kendall_tau']:.3f}",
        f"Per-file (means):",
        f"  Pearson r = {corr_per_mean['pearson_r']:.3f}",
        f"  R^2 = {corr_per_mean['r2']:.3f}",
    ]
    ax.text(0.02, 0.98, "\n".join(legend_lines), transform=ax.transAxes,
            verticalalignment="top", fontsize=9,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.85))

    ax.set_xlabel("Number of Bugs", fontsize=12, fontweight="bold")
    ax.set_ylabel("LLM Judge Score (Normalized)", fontsize=12, fontweight="bold")
    ax.set_title(f"P2: Bug Count vs LLM Judge Score with 95% CI ({model_name})",
                 fontsize=13, fontweight="bold")
    ax.set_ylim(-0.05, 1.05)
    ax.set_xticks(range(int(xs.min()), int(xs.max()) + 1))
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left", fontsize=9)

    fig.tight_layout()
    out = cfg.output_dir / "p2_bug_ladder_with_ci.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


# ----------------------------- main --------------------------------

def main(cfg: P2RunConfig) -> Dict[str, Any]:
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    model_name = os.environ.get("TRACE_CUSTOMLLM_MODEL", "unknown-model")

    if cfg.judge_backend == "anthropic_direct":
        model_name = cfg.anthropic_model

    use_wandb = (not cfg.wandb_off) and bool(os.environ.get("WANDB_API_KEY"))
    wandb_run = None
    if use_wandb:
        try:
            import wandb
            wandb_run = wandb.init(
                project=cfg.wandb_project,
                config={
                    "bug_ladder_path": str(cfg.bug_ladder_path),
                    "judge_prompt_temp_path": str(cfg.judge_prompt_temp_path),
                    "max_score": cfg.max_score,
                    "num_samples": cfg.num_samples,
                    "max_workers": cfg.max_workers,
                    "bootstrap": cfg.bootstrap,
                    "bootstrap_iters": cfg.bootstrap_iters,
                    "seed": cfg.seed,
                    "model_name": model_name,
                    "judge_backend": cfg.judge_backend,
                },
            )
        except Exception as e:
            log.warning(f"wandb init failed, continuing without: {e}")
            wandb_run = None

    raw, bug_counts, file_paths, gold_fp = _run_judge_matrix(cfg)
    np.save(cfg.output_dir / "raw_score_matrix.npy", raw)

    agg = _aggregate(raw, bug_counts, cfg)

    # Per-call correlation: each (bug_count, score) pair from every LLM call.
    xs_call = np.repeat(np.array(bug_counts, dtype=float), raw.shape[0])
    ys_call = raw.T.flatten()  # shape (N*S,) matching xs_call repetition order
    corr_per_call = _correlations(xs_call, ys_call)

    xs_mean = np.array(bug_counts, dtype=float)
    ys_mean = np.array([d["mean"] for d in agg["per_file"]], dtype=float)
    corr_per_mean = _correlations(xs_mean, ys_mean)

    plot_path = _plot(agg["per_file"], corr_per_call, corr_per_mean, cfg, model_name)
    log.info(f"Saved plot: {plot_path}")

    summary = {
        "config": {
            "bug_ladder_path": str(cfg.bug_ladder_path),
            "gold_file": str(gold_fp),
            "max_score": cfg.max_score,
            "num_samples": cfg.num_samples,
            "max_workers": cfg.max_workers,
            "bootstrap": cfg.bootstrap,
            "bootstrap_iters": cfg.bootstrap_iters,
            "model_name": model_name,
        },
        "per_file": agg["per_file"],
        "correlations_per_call": corr_per_call,
        "correlations_per_mean": corr_per_mean,
        "plot_path": str(plot_path),
    }
    (cfg.output_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    log.info("=" * 72)
    log.info("PER-FILE SUMMARY (mean +/- 95% CI)")
    for d in agg["per_file"]:
        log.info(f"  bugs={d['bug_count']:>2}  n={d['n_samples']:>3}  "
                 f"mean={d['mean']:.3f}  CI=[{d['ci_lo']:.3f}, {d['ci_hi']:.3f}]  sem={d['sem']:.3f}")
    log.info("=" * 72)
    log.info(f"per-call corr:  Pearson={corr_per_call['pearson_r']:.3f}  "
             f"Spearman={corr_per_call['spearman_rho']:.3f}  Kendall={corr_per_call['kendall_tau']:.3f}")
    log.info(f"per-mean corr:  Pearson={corr_per_mean['pearson_r']:.3f}  R^2={corr_per_mean['r2']:.3f}")

    if wandb_run is not None:
        import wandb
        wandb.log({
            "p2_plot": wandb.Image(str(plot_path)),
            **{f"per_call/{k}": v for k, v in corr_per_call.items()},
            **{f"per_mean/{k}": v for k, v in corr_per_mean.items()},
        })
        for d in agg["per_file"]:
            wandb.log({
                "bug_count": d["bug_count"],
                "mean_score": d["mean"],
                "ci_lo": d["ci_lo"],
                "ci_hi": d["ci_hi"],
                "sem": d["sem"],
            })
        wandb.finish()

    return summary


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="P2 bug-ladder vs LLM judge with per-x 95% CI error bars")
    p.add_argument("--bug_ladder_path", required=True,
                   help="Directory of *_<k>_bugs.lean files (e.g. data/file_equiv_08_19_2025/my_add_file_eq_with_bugs)")
    p.add_argument("--judge_prompt_temp_path", required=True,
                   help="Path to LLM judge prompt template (e.g. veribench simplest_prompt_varying_score_range.txt)")
    p.add_argument("--output_dir", default=str(Path(__file__).resolve().parent / "out"))
    p.add_argument("--max_score", type=int, default=30)
    p.add_argument("--num_samples", type=int, default=15,
                   help="LLM judge calls per bug-count file (S). Default 15.")
    p.add_argument("--max_workers", type=int, default=16)
    p.add_argument("--bootstrap", action="store_true",
                   help="Use percentile bootstrap CI instead of t-based CI.")
    p.add_argument("--bootstrap_iters", type=int, default=2000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--wandb_project", default="cert-judge-08-p2-bug-ladder-ci")
    p.add_argument("--wandb_off", action="store_true")
    p.add_argument("--judge_backend", choices=["veribench_proxy", "anthropic_direct"],
                   default="veribench_proxy",
                   help="veribench_proxy = via TRACE_CUSTOMLLM_URL (cluster); anthropic_direct = anthropic SDK from this host.")
    p.add_argument("--anthropic_model", default="claude-sonnet-4-5")
    p.add_argument("--anthropic_temperature", type=float, default=0.7)
    p.add_argument("--anthropic_max_tokens", type=int, default=1024)
    return p


if __name__ == "__main__":
    _setup_logging()
    args = _build_parser().parse_args()
    cfg = P2RunConfig(
        bug_ladder_path=Path(args.bug_ladder_path).expanduser().resolve(),
        judge_prompt_temp_path=Path(args.judge_prompt_temp_path).expanduser().resolve(),
        output_dir=Path(args.output_dir).expanduser().resolve(),
        max_score=args.max_score,
        num_samples=args.num_samples,
        max_workers=args.max_workers,
        bootstrap=args.bootstrap,
        bootstrap_iters=args.bootstrap_iters,
        seed=args.seed,
        wandb_project=args.wandb_project,
        wandb_off=args.wandb_off,
        judge_backend=args.judge_backend,
        anthropic_model=args.anthropic_model,
        anthropic_temperature=args.anthropic_temperature,
        anthropic_max_tokens=args.anthropic_max_tokens,
    )
    main(cfg)
