#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge-rows", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.judge_rows)
    df = df[df["judge_id"].astype(str).str.startswith("gpt-5.3-codex|")].copy()
    if df.empty:
        raise SystemExit("No codex rows found in judge_rows.csv")

    cols = [
        "judge_id",
        "human_spearman_r_pass1",
        "human_spearman_p_pass1",
        "human_spearman_r_pass2",
        "human_spearman_p_pass2",
        "human_spearman_r_avg",
        "human_spearman_p_avg",
    ]
    avail = [c for c in cols if c in df.columns]
    view = df[avail].copy()

    best_pass1 = view.sort_values("human_spearman_r_pass1", ascending=False).iloc[0]
    best_pass2 = view.sort_values("human_spearman_r_pass2", ascending=False).iloc[0]
    best_avg = view.sort_values("human_spearman_r_avg", ascending=False).iloc[0]

    ranking = view.sort_values("human_spearman_r_avg", ascending=False)

    lines = []
    lines.append("# Codex Prompt Tuning Summary\n")
    lines.append("## Best Prompts by Target\n")
    lines.append(f"- Best `pass1`: `{best_pass1['judge_id']}` with Spearman `{best_pass1['human_spearman_r_pass1']:.6f}` (p={best_pass1['human_spearman_p_pass1']:.6g})")
    lines.append(f"- Best `pass2`: `{best_pass2['judge_id']}` with Spearman `{best_pass2['human_spearman_r_pass2']:.6f}` (p={best_pass2['human_spearman_p_pass2']:.6g})")
    lines.append(f"- Best `avg`: `{best_avg['judge_id']}` with Spearman `{best_avg['human_spearman_r_avg']:.6f}` (p={best_avg['human_spearman_p_avg']:.6g})\n")

    lines.append("## Ranking by Avg Spearman\n")
    lines.append("| judge_id | pass1 rho | pass2 rho | avg rho |")
    lines.append("|---|---:|---:|---:|")
    for _, r in ranking.iterrows():
        lines.append(
            f"| {r['judge_id']} | {r['human_spearman_r_pass1']:.6f} | {r['human_spearman_r_pass2']:.6f} | {r['human_spearman_r_avg']:.6f} |"
        )

    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
