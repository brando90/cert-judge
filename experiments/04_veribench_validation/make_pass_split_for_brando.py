#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple


Key = Tuple[str, str]


def read_tsv(path: Path) -> Dict[Key, float]:
    out: Dict[Key, float] = {}
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            key = (row["gold_file"], row["candidate_file"])
            out[key] = float(row["human_score_0_5"])
    return out


def write_tsv(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        fieldnames = ["gold_file", "candidate_file", "human_score_0_5"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def rows_from_keys(keys: List[Key], values: Dict[Key, float]) -> List[dict]:
    rows = []
    for gold, cand in sorted(keys):
        rows.append(
            {
                "gold_file": gold,
                "candidate_file": cand,
                "human_score_0_5": f"{values[(gold, cand)]:.6f}",
            }
        )
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--pass1",
        default="experiments/04_veribench_validation/data/ethan_human_scores_20260425.tsv",
    )
    ap.add_argument(
        "--pass2",
        default="experiments/04_veribench_validation/data/ethan_human_scores_ORIGINAL.tsv",
    )
    ap.add_argument(
        "--outdir",
        default="experiments/04_veribench_validation/results_exp23_pass_split_for_brando",
    )
    ap.add_argument("--val-rows", type=int, default=15)
    ap.add_argument("--test-rows", type=int, default=15)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    pass1 = read_tsv(Path(args.pass1))
    pass2 = read_tsv(Path(args.pass2))

    overlap_keys = sorted(set(pass1).intersection(set(pass2)))
    by_gold: Dict[str, List[Key]] = {}
    for k in overlap_keys:
        by_gold.setdefault(k[0], []).append(k)

    # Keep only full 3-candidate groups to preserve within-problem comparability.
    full_groups = {g: ks for g, ks in by_gold.items() if len(ks) == 3}
    gold_files = sorted(full_groups.keys())

    rows_per_group = 3
    need_groups_val = args.val_rows // rows_per_group
    need_groups_test = args.test_rows // rows_per_group

    if args.val_rows % rows_per_group != 0 or args.test_rows % rows_per_group != 0:
        raise ValueError("val_rows and test_rows must be multiples of 3 (one full problem group).")

    if len(gold_files) < need_groups_val + need_groups_test:
        raise ValueError(
            f"Not enough full groups: have {len(gold_files)}, need {need_groups_val + need_groups_test}."
        )

    rng = random.Random(args.seed)
    shuffled = gold_files[:]
    rng.shuffle(shuffled)

    val_gold = sorted(shuffled[:need_groups_val])
    test_gold = sorted(shuffled[need_groups_val : need_groups_val + need_groups_test])
    holdout_gold = sorted(shuffled[need_groups_val + need_groups_test :])

    def flatten(groups: List[str]) -> List[Key]:
        keys: List[Key] = []
        for g in groups:
            keys.extend(full_groups[g])
        return keys

    val_keys = flatten(val_gold)
    test_keys = flatten(test_gold)
    holdout_keys = flatten(holdout_gold)

    avg = {k: (pass1[k] + pass2[k]) / 2.0 for k in overlap_keys}

    outdir = Path(args.outdir)
    split_dir = outdir / "splits"
    split_dir.mkdir(parents=True, exist_ok=True)

    # Write pair lists for reproducibility.
    for name, keys in (("val", val_keys), ("test", test_keys), ("holdout", holdout_keys)):
        with (split_dir / f"{name}_pairs.tsv").open("w", newline="") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow(["gold_file", "candidate_file"])
            for g, c in sorted(keys):
                w.writerow([g, c])

    # Write score files per split for pass1/pass2/avg.
    for split_name, keys in (("val", val_keys), ("test", test_keys), ("holdout", holdout_keys)):
        write_tsv(split_dir / f"{split_name}_pass1.tsv", rows_from_keys(keys, pass1))
        write_tsv(split_dir / f"{split_name}_pass2.tsv", rows_from_keys(keys, pass2))
        write_tsv(split_dir / f"{split_name}_avg.tsv", rows_from_keys(keys, avg))

    summary = {
        "seed": args.seed,
        "input": {"pass1": args.pass1, "pass2": args.pass2},
        "counts": {
            "pass1_rows": len(pass1),
            "pass2_rows": len(pass2),
            "overlap_rows": len(overlap_keys),
            "full_groups": len(full_groups),
            "rows_per_group": rows_per_group,
            "val_rows": len(val_keys),
            "test_rows": len(test_keys),
            "holdout_rows": len(holdout_keys),
        },
        "splits": {
            "val_gold_files": val_gold,
            "test_gold_files": test_gold,
            "holdout_gold_files": holdout_gold,
        },
        "notes": [
            "Splits are by problem (gold_file), not by individual pair rows.",
            "Each selected problem contributes all 3 candidate rows.",
            "This yields 15/15 rows for val/test and keeps comparisons internally consistent.",
        ],
    }

    outdir.mkdir(parents=True, exist_ok=True)
    with (outdir / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
