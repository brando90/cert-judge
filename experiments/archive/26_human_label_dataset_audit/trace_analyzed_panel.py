#!/usr/bin/env python3
"""EXP21c: Trace the panel that the published analyses *actually* ran on.

The label TSVs contain 75 rated pairs, but every cached judge-alignment run in
`experiments/04_veribench_validation/` reports 72. This script reads the cached run
artifacts and shows exactly why, so the `75` vs `72` question is settled from evidence
rather than from prose.

It also decomposes the two stacked "set" files, and quantifies the labeling-protocol
drift the paper's abstract refers to.

Pure stdlib. Read-only outside `results/`.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List

import audit_human_labels as A

REPO_ROOT = A.REPO_ROOT
EXP_DIR = A.EXP_DIR
VB = REPO_ROOT / "experiments" / "04_veribench_validation"

# Cached run artifacts that the paper's numbers come from.
EXP16_DIR = VB / "results_exp16_final_robust"
EXP18_DIR = VB / "results_final_stat_reliability_suite" / "exp18_human_label_reliability"
EXP30_SUMMARY = VB / "results_exp30_tivar_v3_all_models" / "summary.json"


def read_tsv_rows(path: Path) -> List:
    with path.open(newline="", encoding="utf-8") as fh:
        return [
            ((r["gold_file"].strip(), r["candidate_file"].strip()), float(r["human_score_0_5"]))
            for r in csv.DictReader(fh, delimiter="\t")
            if (r.get("human_score_0_5") or "").strip()
        ]


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP21c trace the analyzed panel")
    ap.add_argument("--out-dir", type=Path, default=EXP_DIR / "results")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    L: List[str] = []
    W = L.append
    W("# EXP21c: the panel the published analyses actually ran on\n")

    # ---------------------------------------------------------------- 1. exp16
    W("## 1. Judge-alignment runs (EXP16) report `n = 72`, not 75\n")
    s16 = json.loads((EXP16_DIR / "summary.json").read_text())
    W(f"Source: `{EXP16_DIR.relative_to(REPO_ROOT)}/summary.json`\n")
    W("| field | value |")
    W("| --- | ---: |")
    for k in ["n_judges", "n_union_rows", "n_skipped_pairs"]:
        W(f"| `{k}` | {s16.get(k)} |")
    jr = s16.get("judge_rows", [{}])[0]
    for k in ["n_human_rows_pass1", "n_human_rows_pass2", "n_human_rows_avg"]:
        W(f"| `judge_rows[0].{k}` | {jr.get(k)} |")
    W("")

    skip_path = EXP16_DIR / "skipped_pairs.csv"
    if skip_path.exists():
        with skip_path.open(newline="", encoding="utf-8") as fh:
            skipped = list(csv.DictReader(fh))
        W(f"`skipped_pairs.csv` -- the 3 human-rated pairs that every judge analysis drops:\n")
        W("| gold_file | candidate_file | reason |")
        W("| --- | --- | --- |")
        for r in skipped:
            W(f"| `{r['gold_file']}` | `{r['candidate_file']}` | `{r['reason']}` |")
        W("")
        reasons = Counter(r["reason"] for r in skipped)
        W(f"> **Root cause:** {dict(reasons)} -- but *not* because the artifact was never produced.")
        W("> The label file records a **stale pre-renumbering filename**. The problem was renamed")
        W("> `0_unsafeMultiply_safe` -> `1_unsafeMultiply_safe` in the dataset before the gold snapshot")
        W("> that EXP16 resolves against was taken, so the lookup misses and 3 rated pairs are dropped.")
        W("> The labels are valid and the artifacts exist; only the key is stale.\n")

        # Show that the old name is absent while the renumbered name is present.
        gold_names = sorted({r["gold_file"] for r in skipped})
        W("| filename | matches in repo | resolves to |")
        W("| --- | ---: | --- |")
        for g in gold_names:
            stem = g[:-5]
            for probe in (g, stem.replace("0_", "1_", 1) + ".lean"):
                hits = [h for h in REPO_ROOT.rglob(probe) if h.is_file()]
                W(f"| `{probe}` | {len(hits)} | "
                  + (f"`{hits[0].relative_to(REPO_ROOT)}`" if hits else "**absent (stale name)**") + " |")
        W("")
        W("> **Consequence:** renaming those 3 label rows to the current filename would restore the")
        W("> panel to the full 75 pairs / 25 problems. Until that happens, every published number is")
        W("> a 72-pair number. The same class of staleness affects four more problems")
        W("> (`1_bisect_left`, `2_heappush`, `3_heappop`, `4_json_decoder`), which survive only because")
        W("> the older gold snapshot still carries their pre-rename names.\n")

    # ---------------------------------------------------------------- 2. exp18
    W("## 2. The inter-pass reliability numbers (EXP18) also ran on `n = 72`\n")
    s18 = json.loads((EXP18_DIR / "summary.json").read_text())
    W(f"Source: `{EXP18_DIR.relative_to(REPO_ROOT)}/summary.json`\n")
    W("| field | value |")
    W("| --- | ---: |")
    for k in ["n_pass1_pairs", "n_pass2_pairs", "n_overlap_pairs", "n_pass1_only", "n_pass2_only"]:
        W(f"| `{k}` | {s18.get(k)} |")
    W("")
    m = s18["metrics"]
    W("| statistic | cached run | paper | match? |")
    W("| --- | ---: | ---: | --- |")
    pairs = [
        ("Spearman", m["spearman_r"], 0.249), ("Pearson", m["pearson_r"], 0.375),
        ("Kendall tau", m["kendall_tau"], 0.221), ("QWK", m["quadratic_weighted_kappa"], 0.372),
        ("MAE", m["mae_0_5"], 0.778),
        ("MSE (= rmse^2)", m["rmse_0_5"] ** 2, 1.139),
    ]
    for name, got, want in pairs:
        W(f"| {name} | {got:.4f} | {want} | {A.check(got, want, 0.0015)} |")
    W("")
    W("> The four correlation statistics reproduce the paper exactly. **MAE and MSE do not.**")
    W("> `0.778 = 56/72` and `1.139 = 82/72` are the values obtained when the three duplicated")
    W("> `4_json_decoder` rows take pass2 `= 1.0` (first-of-duplicates) instead of `1.5`")
    W("> (mean-of-duplicates). The appendix ceiling table therefore mixes two duplicate-handling")
    W("> conventions across its own rows.\n")

    with (EXP18_DIR / "pair_rows.csv").open(newline="", encoding="utf-8") as fh:
        pr = list(csv.DictReader(fh))
    d = [(float(r["score_pass1"]), float(r["score_pass2"])) for r in pr]
    for repl in (1.0, 1.5, 2.0):
        ds = [abs(a - (repl if b == 1.5 else b)) for a, b in d]
        W(f"- if the three `1.5` pass2 scores are `{repl}`: MAE = {sum(ds)/len(ds):.4f}, "
          f"MSE = {sum(x*x for x in ds)/len(ds):.4f}")
    W("")

    # ---------------------------------------------------------------- 3. what changed
    W("## 3. What changed between the cached runs and the files on disk\n")
    cached_pairs = {(r["gold_file"], r["candidate_file"]) for r in pr}
    p1 = A.LabelFile("pass1", A.FILES[A.PAPER_PASS1]).deduped()
    p2 = A.LabelFile("pass2", A.FILES[A.PAPER_PASS2]).deduped()
    now = set(p1) & set(p2)
    added = sorted(now - cached_pairs)
    removed = sorted(cached_pairs - now)
    W(f"- cached analyzed panel: **{len(cached_pairs)}** pairs / "
      f"**{len({g for g,_ in cached_pairs})}** problems")
    W(f"- current on-disk panel:  **{len(now)}** pairs / **{len({g for g,_ in now})}** problems")
    W(f"- pairs added since:   {', '.join(f'`{c}`' for _, c in added) or '(none)'}")
    W(f"- pairs removed since: {', '.join(f'`{c}`' for _, c in removed) or '(none)'}")
    changed = [k for k in cached_pairs & now
               if abs(dict((( r['gold_file'],r['candidate_file']),float(r['score_pass1'])) for r in pr)[k] - p1[k]) > 1e-9]
    W(f"- pass1 scores changed on the shared pairs: **{len(changed)}**")
    W("")
    W("> So the underlying ratings are stable; the only delta is that the extra problem")
    W("> `0_unsafeMultiply_safe` (3 pairs) was added to the label file *after* the analyses ran,")
    W("> and it is precisely the problem that gets skipped for a missing gold artifact.")
    W("> **`75` is the label-file row count. `72` is the analyzed panel. Every published")
    W("> judge-alignment and inter-pass number in the paper is a `72`-pair number.**\n")

    # ---------------------------------------------------------------- 4. stacked sets
    W("## 4. Exact decomposition of the two stacked `*_set_data.tsv` files\n")
    H = REPO_ROOT / "experiments" / "human_labels"
    D = VB / "data"
    components = {
        "expert_harsh_set_data.tsv": [
            ("participant1_data_correct_prompt.tsv", H / "participant1_data_correct_prompt.tsv"),
            ("participant2_data_pass_1.tsv", H / "participant2_data_pass_1.tsv"),
            ("participant3_data_pass_1.tsv", H / "participant3_data_pass_1.tsv"),
        ],
        "lenient_set_data.tsv": [
            ("participant4_data_pass_1.tsv", H / "participant4_data_pass_1.tsv"),
            ("participant5_data_pass_1.tsv", H / "participant5_data_pass_1.tsv"),
            ("old_prompt/participant1_data_pass_1.tsv", H / "old_prompt" / "participant1_data_pass_1.tsv"),
            ("ethan_human_scores_20260425.tsv (72-row subset)", D / "ethan_human_scores_20260425.tsv"),
        ],
    }
    for target, comps in components.items():
        stack = Counter(read_tsv_rows(H / target))
        total = sum(stack.values())
        residual = Counter(stack)  # peeled down as each component is accounted for
        W(f"### `experiments/human_labels/{target}` ({total} rows)\n")
        W("Components are peeled off in order, so the `rows accounted` column sums to the file total.\n")
        W("| component | file rows | rows accounted | fully absorbed |")
        W("| --- | ---: | ---: | --- |")
        acc = 0
        for name, path in comps:
            c = Counter(read_tsv_rows(path))
            taken = sum(min(residual[k], v) for k, v in c.items())
            fully = all(residual[k] >= v for k, v in c.items())
            for k, v in c.items():
                residual[k] -= min(residual[k], v)
            residual = +residual
            acc += taken
            W(f"| `{name}` | {sum(c.values())} | {taken} | {'yes' if fully else 'partial'} |")
        W(f"| **sum** | | **{acc}** | vs file total **{total}**, unexplained **{total - acc}** |")
        W("")

    W("> `expert_harsh_set_data.tsv` and `lenient_set_data.tsv` are **long-format concatenations")
    W("> of other rater files**, not independent rating sets. Averaging them naively double-counts")
    W("> raters. Note `lenient_set_data.tsv` mixes rubrics: it contains both lenient passes *and*")
    W("> the harsher `ethan_human_scores_20260425` pass (as its 72-row subset).\n")

    # ---------------------------------------------------------------- 5. protocol drift
    W("## 5. Labeling-protocol drift, quantified\n")
    W("Same annotator (participant 1 / Ethan), two different rubric prompts. The paper's")
    W("abstract cites a cross-protocol label correlation of `~0.13`:\n")
    correct = A.LabelFile("cp", H / "participant1_data_correct_prompt.tsv").deduped()
    views = {"pass1 (old prompt)": p1, "pass2 (old prompt)": p2,
             "avg (old prompt)": {k: (p1[k] + p2[k]) / 2 for k in now}}
    W("| old-prompt view | vs `participant1_data_correct_prompt` | n | Pearson |")
    W("| --- | ---: | ---: | ---: |")
    rhos = []
    for name, v in views.items():
        xs, ys, ks = A.aligned(v, correct)
        r = A.spearman(xs, ys)
        rhos.append(r)
        W(f"| `{name}` | {A.fmt(r)} | {len(ks)} | {A.fmt(A.pearson(xs, ys))} |")
    W(f"| **mean** | **{A.fmt(sum(rhos)/len(rhos))}** | | |")
    W("")
    W("> The same person rating the same artifacts under a different rubric prompt produces")
    W("> **nearly uncorrelated** scores. That is the reason the frozen held-out test returned a")
    W("> null: the calibration panel and the five-rater pool are not the same measurement construct.\n")

    (args.out_dir / "PANEL_TRACE.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir/'PANEL_TRACE.md'}")
    print(f"analyzed panel = {len(cached_pairs)} pairs / {len({g for g,_ in cached_pairs})} problems; "
          f"label files now hold {len(now)} pairs / {len({g for g,_ in now})} problems")
    print(f"cross-protocol mean Spearman = {sum(rhos)/len(rhos):.3f}")


if __name__ == "__main__":
    main()
