#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$SCRIPT_DIR"

export MPLBACKEND="${MPLBACKEND:-Agg}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"

# Controls
RUN_EXP16="${RUN_EXP16:-0}"   # 1 => rerun expensive API-based final robust suite first
RUN_EXP13="${RUN_EXP13:-0}"   # 1 => rerun exp13 sweep first

# Paths
EXP16_OUT="${EXP16_OUT:-$SCRIPT_DIR/results_exp16_final_robust}"
EXP17_PREFIX="${EXP17_PREFIX:-$SCRIPT_DIR/results_exp17_final_robust}"
EXP13_RESULTS_DIR="${EXP13_RESULTS_DIR:-$REPO_ROOT/experiments/archive/02_neurips_reviews/results/threshold_calibration_sweep}"
OUT_DIR="${OUT_DIR:-$SCRIPT_DIR/results_final_stat_reliability_suite}"

# Human labels
OLD_RATINGS="${OLD_RATINGS:-$SCRIPT_DIR/data/ethan_human_scores_20260425.tsv}"
NEW_RATINGS="${NEW_RATINGS:-$SCRIPT_DIR/data/ethan_human_scores_ORIGINAL.tsv}"

# Inference settings
BOOTSTRAP_ITERS="${BOOTSTRAP_ITERS:-10000}"
PERM_ITERS="${PERM_ITERS:-20000}"
SEED="${SEED:-42}"

# Optional judge list for rerun mode.
JUDGES="${JUDGES:-llm:gpt-5.3-codex:P8_STRICT_B,llm:gpt-5.3-codex:P4_CHECKLIST,llm:gpt-5.3-codex:P1_BASELINE,llm_bad:gpt-5.3-codex:BAD_STRINGY,llm_bad:gpt-5.3-codex:BAD_FORMAT_BIAS,llm:gpt-4o-mini:P8_STRICT_B,llm:gpt-4o-mini:P4_CHECKLIST,editdist:e1:na,random:r1:na}"

echo "============================================================"
echo "FINAL STAT RELIABILITY SUITE"
echo "run_exp16=$RUN_EXP16 run_exp13=$RUN_EXP13"
echo "exp16_out=$EXP16_OUT"
echo "exp17_prefix=$EXP17_PREFIX"
echo "exp13_results_dir=$EXP13_RESULTS_DIR"
echo "old_ratings=$OLD_RATINGS"
echo "new_ratings=$NEW_RATINGS"
echo "bootstrap_iters=$BOOTSTRAP_ITERS perm_iters=$PERM_ITERS seed=$SEED"
echo "============================================================"

mkdir -p "$OUT_DIR"

if [[ "$RUN_EXP16" == "1" ]]; then
  echo
  echo "[1/6] Running EXP16/17 final robust suite (API-heavy)"
  JUDGES="$JUDGES" \
  BOOTSTRAP_ITERS="$BOOTSTRAP_ITERS" \
  PERM_ITERS="$PERM_ITERS" \
  SEED="$SEED" \
  EXP16_OUT="$EXP16_OUT" \
  EXP17_PREFIX="$EXP17_PREFIX" \
  bash "$SCRIPT_DIR/run_final_robust_suite.sh"
else
  echo
  echo "[1/6] Skipping EXP16/17 rerun (RUN_EXP16=0), using existing outputs"
fi

if [[ "$RUN_EXP13" == "1" ]]; then
  echo
  echo "[2/6] Running EXP13 threshold sweep (API-heavy)"
  BOOTSTRAP_ITERS="$BOOTSTRAP_ITERS" \
  bash "$REPO_ROOT/experiments/archive/02_neurips_reviews/run_exp13_threshold_sweep.sh"
else
  echo
  echo "[2/6] Skipping EXP13 rerun (RUN_EXP13=0), using existing threshold sweep outputs"
fi

echo
echo "[3/6] EXP18A: human-pass reliability (pass1 vs pass2)"
python -u "$SCRIPT_DIR/exp18_human_label_reliability.py" \
  --pass1-tsv "$OLD_RATINGS" \
  --pass2-tsv "$NEW_RATINGS" \
  --bootstrap-iters "$BOOTSTRAP_ITERS" \
  --seed "$SEED" \
  --out-dir "$OUT_DIR/exp18_human_label_reliability"

echo
echo "[4/6] EXP13B: formal threshold delta significance vs t=0.85"
python -u "$REPO_ROOT/experiments/archive/02_neurips_reviews/exp13_threshold_significance.py" \
  --detail-rows-csv "$EXP13_RESULTS_DIR/detail_rows.csv" \
  --thresholds "0.6,0.65,0.7,0.75,0.8,0.85" \
  --reference-threshold 0.85 \
  --bootstrap-iters "$BOOTSTRAP_ITERS" \
  --perm-iters "$PERM_ITERS" \
  --seed "$SEED" \
  --out-dir "$OUT_DIR/exp13_threshold_significance"

echo
echo "[5/6] EXP18B: alpha-sensitivity ablation on EXP16 outputs"
python -u "$SCRIPT_DIR/exp18_identity_alpha_ablation.py" \
  --exp16-summary "$EXP16_OUT/summary.json" \
  --exp16-detail-rows "$EXP16_OUT/detail_rows.csv" \
  --bootstrap-iters "$BOOTSTRAP_ITERS" \
  --perm-iters "$PERM_ITERS" \
  --seed "$SEED" \
  --out-dir "$OUT_DIR/exp18_identity_alpha_ablation"

echo
echo "[6/6] Writing consolidated suite summary"
export OUT_DIR EXP16_OUT
python - <<'PY'
import json
import os
from pathlib import Path

out_dir = Path(os.environ["OUT_DIR"])
exp16_out = Path(os.environ["EXP16_OUT"])
exp16 = json.loads((exp16_out / "summary.json").read_text())
exp18a = json.loads((out_dir / "exp18_human_label_reliability" / "summary.json").read_text())
exp13b = json.loads((out_dir / "exp13_threshold_significance" / "summary.json").read_text())
exp18b = json.loads((out_dir / "exp18_identity_alpha_ablation" / "summary.json").read_text())

rows13 = exp13b["rows"]
best_alt = sorted([r for r in rows13 if abs(r["threshold"] - exp13b["reference_threshold"]) > 1e-9], key=lambda r: r["delta_flip_perm_p"])[0]

summary = {
    "exp16_summary_path": str(exp16_out / "summary.json"),
    "exp18a_human_reliability_path": str(out_dir / "exp18_human_label_reliability" / "summary.json"),
    "exp13b_threshold_significance_path": str(out_dir / "exp13_threshold_significance" / "summary.json"),
    "exp18b_alpha_ablation_path": str(out_dir / "exp18_identity_alpha_ablation" / "summary.json"),
    "exp16_trend_v1_spearman": {
        k: exp16["trend_by_set"][k]["trend_v1"]["spearman_r"] for k in ["pass1", "pass2", "avg"]
    },
    "exp16_trend_v1_perm_p": {
        k: exp16["trend_by_set"][k]["trend_v1"]["spearman_perm_p"] for k in ["pass1", "pass2", "avg"]
    },
    "human_pass_reliability": exp18a["metrics"],
    "best_threshold_delta_test": best_alt,
    "alpha_ablation_trend": exp18b["trend_by_label_set"],
}
(out_dir / "summary.json").write_text(json.dumps(summary, indent=2))

lines = []
lines.append("# Final Statistical Reliability Suite")
lines.append("")
lines.append("## EXP16 (certification -> human trend, v1)")
for k in ["pass1", "pass2", "avg"]:
    lines.append(f"- {k}: Spearman={summary['exp16_trend_v1_spearman'][k]:.3f}, perm_p={summary['exp16_trend_v1_perm_p'][k]:.4g}")
lines.append("")
lines.append("## Human pass reliability (pass1 vs pass2)")
m = summary["human_pass_reliability"]
lines.append(f"- Spearman={m['spearman_r']:.3f} [{m['spearman_ci_lo']:.3f},{m['spearman_ci_hi']:.3f}]")
lines.append(f"- QWK={m['quadratic_weighted_kappa']:.3f} [{m['qwk_ci_lo']:.3f},{m['qwk_ci_hi']:.3f}]")
lines.append(f"- MAE={m['mae_0_5']:.3f}, RMSE={m['rmse_0_5']:.3f}")
lines.append("")
lines.append("## EXP13 threshold significance (vs reference t=0.85)")
b = summary["best_threshold_delta_test"]
lines.append(f"- strongest delta test threshold={b['threshold']:.2f}, delta_flip={b['delta_flip_rate_vs_ref']:.4f}, p={b['delta_flip_perm_p']:.4g}")
lines.append("")
lines.append("## EXP18 alpha ablation")
for k in ["pass1", "pass2", "avg"]:
    a = summary["alpha_ablation_trend"][k]["all_variants"]
    c = summary["alpha_ablation_trend"][k]["exclude_alpha"]
    lines.append(f"- {k}: all={a['spearman_r']:.3f} (p={a['spearman_perm_p']:.4g}) vs no_alpha={c['spearman_r']:.3f} (p={c['spearman_perm_p']:.4g})")
lines.append("")
lines.append("## Paths")
lines.append(f"- suite summary: `{out_dir / 'summary.json'}`")
lines.append(f"- exp18A: `{out_dir / 'exp18_human_label_reliability'}`")
lines.append(f"- exp13B: `{out_dir / 'exp13_threshold_significance'}`")
lines.append(f"- exp18B: `{out_dir / 'exp18_identity_alpha_ablation'}`")
(out_dir / "summary.md").write_text("\\n".join(lines))
print(f"wrote: {out_dir / 'summary.json'}")
print(f"wrote: {out_dir / 'summary.md'}")
PY

echo
echo "Done."
echo "  Suite summary JSON: $OUT_DIR/summary.json"
echo "  Suite summary MD:   $OUT_DIR/summary.md"
echo "  EXP18A output:      $OUT_DIR/exp18_human_label_reliability"
echo "  EXP13B output:      $OUT_DIR/exp13_threshold_significance"
echo "  EXP18B output:      $OUT_DIR/exp18_identity_alpha_ablation"
