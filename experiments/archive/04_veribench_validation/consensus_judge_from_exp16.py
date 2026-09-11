#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compute weighted consensus judge from EXP16 detail rows.")
    p.add_argument("--detail-rows", type=Path, required=True)
    p.add_argument("--pass1-tsv", type=Path, required=True)
    p.add_argument("--pass2-tsv", type=Path, required=True)
    p.add_argument("--avg-tsv", type=Path, required=True)
    p.add_argument("--judges", type=str, required=True, help="Comma-separated judge ids.")
    p.add_argument(
        "--weights",
        type=str,
        required=True,
        help="Comma-separated weights aligned with --judges (example: 0.25,0.25,0.2,0.2,0.1).",
    )
    p.add_argument("--repeat-agg", choices=["mean", "median"], default="median")
    p.add_argument("--winsor-pct", type=float, default=0.1, help="Winsorization fraction per tail (0.1 => 10%%).")
    p.add_argument("--out-dir", type=Path, required=True)
    return p.parse_args()


def _rankdata(xs: list[float]) -> list[float]:
    idx = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[idx[j + 1]] == xs[idx[i]]:
            j += 1
        rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[idx[k]] = rank
        i = j + 1
    return ranks


def _pearson(x: list[float], y: list[float]) -> float:
    mx, my = mean(x), mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    denx = sum((a - mx) ** 2 for a in x)
    deny = sum((b - my) ** 2 for b in y)
    den = (denx * deny) ** 0.5
    if den == 0.0:
        return float("nan")
    return num / den


def _spearman(x: list[float], y: list[float]) -> float:
    return _pearson(_rankdata(x), _rankdata(y))


def _agg(vals: list[float], mode: str) -> float:
    if mode == "mean":
        return sum(vals) / len(vals)
    s = sorted(vals)
    n = len(s)
    m = n // 2
    if n % 2 == 1:
        return s[m]
    return (s[m - 1] + s[m]) / 2.0


def _winsorize(scores: list[float], pct: float) -> list[float]:
    if not scores:
        return scores
    s = sorted(scores)
    n = len(s)
    k = int(pct * n)
    lo = s[k]
    hi = s[n - 1 - k]
    return [min(hi, max(lo, v)) for v in scores]


def _load_human_tsv(path: Path) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            g = Path(row["gold_file"]).name
            c = Path(row["candidate_file"]).name
            out[(g, c)] = float(row["human_score_0_5"]) / 5.0
    return out


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    judges = [x.strip() for x in args.judges.split(",") if x.strip()]
    weights = [float(x.strip()) for x in args.weights.split(",") if x.strip()]
    if len(judges) != len(weights):
        raise ValueError("Length mismatch: --judges and --weights")
    s = sum(weights)
    if s <= 0:
        raise ValueError("Weights must sum to > 0")
    weights = [w / s for w in weights]

    human_sets = {
        "pass1": _load_human_tsv(args.pass1_tsv),
        "pass2": _load_human_tsv(args.pass2_tsv),
        "avg": _load_human_tsv(args.avg_tsv),
    }
    # item -> judge -> score
    item_scores: dict[tuple[str, str], dict[str, float]] = {}
    with args.detail_rows.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row["row_type"] != "human_eval_union":
                continue
            jid = row["judge_id"]
            if jid not in judges:
                continue
            try:
                g_raw, c_raw = row["item_key"].split("::", 1)
            except ValueError:
                continue
            key = (Path(g_raw).name, Path(c_raw).name)
            reps = json.loads(row["repeat_scores"])
            score = _agg([float(x) for x in reps], args.repeat_agg)
            item_scores.setdefault(key, {})[jid] = score

    rows_out: list[dict[str, float | str]] = []
    pred_by_item: dict[tuple[str, str], float] = {}
    for key, by_judge in item_scores.items():
        if any(j not in by_judge for j in judges):
            continue
        vals = [by_judge[j] for j in judges]
        vals_w = _winsorize(vals, args.winsor_pct)
        pred = sum(w * v for w, v in zip(weights, vals_w))
        pred_by_item[key] = pred
        d = {"gold_file": key[0], "candidate_file": key[1], "consensus_score": pred}
        for j, v in zip(judges, vals):
            d[f"raw::{j}"] = v
        rows_out.append(d)

    corrs = {}
    for split, hs in human_sets.items():
        keys = [k for k in pred_by_item.keys() if k in hs]
        x = [pred_by_item[k] for k in keys]
        y = [hs[k] for k in keys]
        if not keys:
            corrs[split] = {"spearman": float("nan"), "n": 0}
        else:
            corrs[split] = {"spearman": _spearman(x, y), "n": len(keys)}

    out_csv = args.out_dir / "consensus_rows.csv"
    if rows_out:
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
            w.writeheader()
            w.writerows(rows_out)

    summary = {
        "judges": judges,
        "weights": weights,
        "repeat_agg": args.repeat_agg,
        "winsor_pct": args.winsor_pct,
        "correlations": corrs,
        "n_consensus_rows": len(rows_out),
        "outputs": {"consensus_rows_csv": str(out_csv)},
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
