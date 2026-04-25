#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export MPLBACKEND="${MPLBACKEND:-Agg}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-$SCRIPT_DIR/.mplconfig}"
mkdir -p "$MPLCONFIGDIR"

# Human label inputs
OLD_RATINGS="${OLD_RATINGS:-$SCRIPT_DIR/data/ethan_human_scores_20260425.tsv}"                # pass1
NEW_RATINGS="${NEW_RATINGS:-$SCRIPT_DIR/data/ethan_human_scores_second_pass_20260425.tsv}"    # pass2
AVG_RATINGS="${AVG_RATINGS:-$SCRIPT_DIR/data/ethan_human_scores_avg_two_passes_20260425.tsv}" # regenerated below

# Main experiment settings
JUDGES="${JUDGES:-llm:gpt-5.3-codex:P8_STRICT_B,llm:gpt-5.3-codex:P4_CHECKLIST,llm:gpt-5.3-codex:P1_BASELINE,llm_bad:gpt-5.3-codex:na,llm:gpt-4o-mini:P8_STRICT_B,llm:gpt-4o-mini:P4_CHECKLIST,editdist:e1:na,random:r1:na}"
JUDGE_REPEATS="${JUDGE_REPEATS:-3}"
THRESHOLD="${THRESHOLD:-0.85}"
BOOTSTRAP_ITERS="${BOOTSTRAP_ITERS:-10000}"
PERM_ITERS="${PERM_ITERS:-20000}"
SEED="${SEED:-42}"

EXP16_OUT="${EXP16_OUT:-$SCRIPT_DIR/results_exp16_final_robust}"
EXP17_PREFIX="${EXP17_PREFIX:-$SCRIPT_DIR/results_exp17_final_robust}"

# Export so inline python (os.environ) can read these values.
export OLD_RATINGS NEW_RATINGS AVG_RATINGS
export JUDGES JUDGE_REPEATS THRESHOLD BOOTSTRAP_ITERS PERM_ITERS SEED
export EXP16_OUT EXP17_PREFIX

echo "============================================================"
echo "FINAL ROBUST SUITE"
echo "old_ratings=$OLD_RATINGS"
echo "new_ratings=$NEW_RATINGS"
echo "avg_ratings=$AVG_RATINGS"
echo "exp16_out=$EXP16_OUT"
echo "exp17_prefix=$EXP17_PREFIX"
echo "judge_repeats=$JUDGE_REPEATS threshold=$THRESHOLD seed=$SEED"
echo "bootstrap_iters=$BOOTSTRAP_ITERS perm_iters=$PERM_ITERS"
echo "judges=$JUDGES"
echo "============================================================"

echo
echo "[1/4] Rebuilding avg(old,new) label file"
python - <<'PY'
import csv
from collections import defaultdict
from pathlib import Path
import os

old_p = Path(os.environ["OLD_RATINGS"])
new_p = Path(os.environ["NEW_RATINGS"])
avg_p = Path(os.environ["AVG_RATINGS"])

def load(path: Path):
    vals = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            g = row["gold_file"].strip()
            c = row["candidate_file"].strip()
            s = row["human_score_0_5"].strip()
            if g and c and s:
                vals[(g, c)].append(float(s))
    return {k: sum(v) / len(v) for k, v in vals.items()}

old = load(old_p)
new = load(new_p)
keys = sorted(set(old) | set(new))

avg_p.parent.mkdir(parents=True, exist_ok=True)
with avg_p.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["gold_file", "candidate_file", "human_score_0_5"])
    for k in keys:
        a = old.get(k)
        b = new.get(k)
        s = (a + b) / 2.0 if a is not None and b is not None else (a if a is not None else b)
        w.writerow([k[0], k[1], f"{s:.6f}"])

print(f"old_n={len(old)} new_n={len(new)} avg_n={len(keys)}")
print(f"wrote: {avg_p}")
PY

echo
echo "[2/4] Running EXP16 (multi-judge trend across pass1/pass2/avg)"
python -u exp16_multi_judge_human_sets.py \
  --pass1-tsv "$OLD_RATINGS" \
  --pass2-tsv "$NEW_RATINGS" \
  --avg-tsv "$AVG_RATINGS" \
  --out-dir "$EXP16_OUT" \
  --judge-repeats "$JUDGE_REPEATS" \
  --threshold "$THRESHOLD" \
  --bootstrap-iters "$BOOTSTRAP_ITERS" \
  --perm-iters "$PERM_ITERS" \
  --seed "$SEED" \
  --judges "$JUDGES"

echo
echo "[3/4] Running EXP17 for pass1/pass2/avg"
for LABEL in pass1 pass2 avg; do
  OUT_DIR="${EXP17_PREFIX}_${LABEL}"
  echo "  - LABEL_SET=$LABEL -> $OUT_DIR"
  python -u exp17_property_human_analysis.py \
    --exp16-summary "$EXP16_OUT/summary.json" \
    --out-dir "$OUT_DIR" \
    --label-set "$LABEL" \
    --perm-iters "$PERM_ITERS" \
    --seed "$SEED" \
    --bad-judge-pattern "BAD_STRINGY"
done

echo
echo "[4/4] Writing consolidated summary"
python - <<'PY'
import json
from pathlib import Path
import os

exp16_out = Path(os.environ["EXP16_OUT"])
exp17_prefix = os.environ["EXP17_PREFIX"]

exp16 = json.loads((exp16_out / "summary.json").read_text())
exp17 = {}
for label in ["pass1", "pass2", "avg"]:
    p = Path(f"{exp17_prefix}_{label}") / "summary.json"
    exp17[label] = json.loads(p.read_text())

out = {
    "exp16_summary_path": str(exp16_out / "summary.json"),
    "exp17_summary_paths": {k: f"{exp17_prefix}_{k}/summary.json" for k in ["pass1", "pass2", "avg"]},
    "n_judges": exp16.get("n_judges"),
    "trend_v1_spearman": {
        k: {
            "r": exp16["trend_by_set"][k]["trend_v1"]["spearman_r"],
            "perm_p": exp16["trend_by_set"][k]["trend_v1"]["spearman_perm_p"],
        } for k in ["pass1", "pass2", "avg"]
    },
    "trend_v2_spearman": {
        k: {
            "r": exp16["trend_by_set"][k]["trend_v2"]["spearman_r"],
            "perm_p": exp16["trend_by_set"][k]["trend_v2"]["spearman_perm_p"],
        } for k in ["pass1", "pass2", "avg"]
    },
    "exp17_top_property_by_label": {},
}

for label in ["pass1", "pass2", "avg"]:
    props = exp17[label]["per_property_correlations"]
    props_sorted = sorted(props, key=lambda x: abs(float(x["spearman_r"])), reverse=True)
    out["exp17_top_property_by_label"][label] = props_sorted[0] if props_sorted else None

(exp16_out / "final_robust_suite_summary.json").write_text(json.dumps(out, indent=2))

lines = []
lines.append("# Final Robust Suite Summary")
lines.append("")
lines.append(f"- n_judges: {out['n_judges']}")
lines.append("")
lines.append("## EXP16 trend (cert -> human)")
for label in ["pass1", "pass2", "avg"]:
    v1 = out["trend_v1_spearman"][label]
    v2 = out["trend_v2_spearman"][label]
    lines.append(f"- {label}: v1 Spearman={v1['r']:.3f} (p={v1['perm_p']:.4g}), v2 Spearman={v2['r']:.3f} (p={v2['perm_p']:.4g})")
lines.append("")
lines.append("## EXP17 strongest property (by |Spearman|)")
for label in ["pass1", "pass2", "avg"]:
    t = out["exp17_top_property_by_label"][label]
    if t is None:
        lines.append(f"- {label}: n/a")
    else:
        lines.append(f"- {label}: {t['property']} r={float(t['spearman_r']):.3f} p={float(t['spearman_perm_p']):.4g}")
lines.append("")
lines.append("## Paths")
lines.append(f"- EXP16: `{exp16_out}`")
for label in ["pass1", "pass2", "avg"]:
    lines.append(f"- EXP17 {label}: `{exp17_prefix}_{label}`")

(exp16_out / "final_robust_suite_summary.md").write_text("\n".join(lines))
print(f"wrote: {exp16_out / 'final_robust_suite_summary.json'}")
print(f"wrote: {exp16_out / 'final_robust_suite_summary.md'}")
PY

echo
echo "Done."
echo "  EXP16 summary:          $EXP16_OUT/summary.json"
echo "  Final suite summary:    $EXP16_OUT/final_robust_suite_summary.json"
echo "  Final suite markdown:   $EXP16_OUT/final_robust_suite_summary.md"
echo "  EXP17 pass1 summary:    ${EXP17_PREFIX}_pass1/summary.json"
echo "  EXP17 pass2 summary:    ${EXP17_PREFIX}_pass2/summary.json"
echo "  EXP17 avg summary:      ${EXP17_PREFIX}_avg/summary.json"
