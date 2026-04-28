"""Reuse a saved raw_score_matrix.npy + summary.json from a primary run and
re-aggregate per-x CIs using percentile bootstrap. Honors PROTOCOL: no new
LLM calls. Writes a new plot + summary into a sibling output_dir.

Usage:
  python reaggregate_with_bootstrap.py --primary_dir <dir-with-summary.json>
                                       [--output_dir <dir>]
                                       [--bootstrap_iters 2000] [--seed 42]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np

# Re-use plotting + correlation helpers from the runner
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_p2_bug_ladder_with_ci import (  # noqa: E402
    P2RunConfig, _aggregate, _correlations, _plot,
)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--primary_dir", required=True,
                   help="Dir containing raw_score_matrix.npy + summary.json from the primary t-CI run")
    p.add_argument("--output_dir", default=None,
                   help="Where to write bootstrap plot + summary; default = <primary_dir>_bootstrap")
    p.add_argument("--bootstrap_iters", type=int, default=2000)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    log = logging.getLogger("reaggregate_bootstrap")

    primary_dir = Path(args.primary_dir).expanduser().resolve()
    raw = np.load(primary_dir / "raw_score_matrix.npy")
    summary = json.loads((primary_dir / "summary.json").read_text())
    bug_counts = [d["bug_count"] for d in summary["per_file"]]

    out_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir \
              else primary_dir.parent / (primary_dir.name + "_bootstrap")
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = P2RunConfig(
        bug_ladder_path=Path(summary["config"]["bug_ladder_path"]),
        judge_prompt_temp_path=Path("/dev/null"),
        output_dir=out_dir,
        max_score=int(summary["config"]["max_score"]),
        num_samples=raw.shape[0],
        bootstrap=True,
        bootstrap_iters=args.bootstrap_iters,
        seed=args.seed,
    )

    log.info(f"Bootstrap ablation: raw shape={raw.shape}, iters={args.bootstrap_iters}")
    agg = _aggregate(raw, bug_counts, cfg)

    xs_call = np.repeat(np.array(bug_counts, dtype=float), raw.shape[0])
    ys_call = raw.T.flatten()
    corr_per_call = _correlations(xs_call, ys_call)

    xs_mean = np.array(bug_counts, dtype=float)
    ys_mean = np.array([d["mean"] for d in agg["per_file"]], dtype=float)
    corr_per_mean = _correlations(xs_mean, ys_mean)

    plot_path = _plot(agg["per_file"], corr_per_call, corr_per_mean,
                      cfg, summary["config"]["model_name"])
    log.info(f"Saved bootstrap plot: {plot_path}")

    out_summary = {
        "config": {**summary["config"],
                   "ci_method": "percentile_bootstrap",
                   "bootstrap_iters": args.bootstrap_iters,
                   "primary_dir": str(primary_dir)},
        "per_file": agg["per_file"],
        "correlations_per_call": corr_per_call,
        "correlations_per_mean": corr_per_mean,
        "plot_path": str(plot_path),
    }
    (out_dir / "summary.json").write_text(json.dumps(out_summary, indent=2))

    log.info("=" * 72)
    log.info("BOOTSTRAP PER-FILE SUMMARY (mean +/- 95% percentile CI)")
    for d in agg["per_file"]:
        log.info(f"  bugs={d['bug_count']:>2}  n={d['n_samples']:>3}  "
                 f"mean={d['mean']:.3f}  CI=[{d['ci_lo']:.3f}, {d['ci_hi']:.3f}]  sem={d['sem']:.3f}")
    log.info("=" * 72)
    log.info(f"per-call corr:  Pearson={corr_per_call['pearson_r']:.3f}  "
             f"Spearman={corr_per_call['spearman_rho']:.3f}  Kendall={corr_per_call['kendall_tau']:.3f}")
    log.info(f"per-mean corr:  Pearson={corr_per_mean['pearson_r']:.3f}  R^2={corr_per_mean['r2']:.3f}")


if __name__ == "__main__":
    main()
