#!/usr/bin/env python3
"""Zero-model-call provenance audit: label identity + judge/rater-seen reference bytes.

Reads (all read-only):
  - cert-judge paper label TSVs (data/ethan_human_scores_*.tsv)
  - cert-judge's vendored gold copy (data/veribench_dataset/lean_src/veribench) — this is the
    DEFAULT_VERIBENCH_ROOT that exp16_multi_judge_human_sets.py resolves golds from.
  - VeriBench's own human_labels TSVs (participant files, old_prompt passes)
  - VeriBench git history (via `git log --follow`, `git show`) for byte-level timelines
  - experiment 100's inputs/provenance.json (its own judge-vs-rater provenance audit)

Writes:
  - results/label_identity.json
  - results/provenance_by_task.csv
"""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

CJ_ROOT = Path(__file__).resolve().parents[3]  # .../cert-judge_e41
EXP_DIR = Path(__file__).resolve().parents[1]
VB_ROOT = Path("/lfs/skampere1/0/brando9/veribench_e41")
DATA = CJ_ROOT / "experiments/archive/04_veribench_validation/data"
VENDORED_GOLD_ROOT = CJ_ROOT / "data/veribench_dataset/lean_src/veribench"
HUMAN_LABELS = VB_ROOT / "veribench_dataset/human_labels"
PROVENANCE_JSON = VB_ROOT / "experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/provenance.json"

PAPER_LABEL_FILES = {
    "paper_pass1_20260425": DATA / "ethan_human_scores_20260425.tsv",
    "paper_pass2_ORIGINAL": DATA / "ethan_human_scores_ORIGINAL.tsv",
    "paper_avg_two_passes": DATA / "ethan_human_scores_avg_two_passes_20260425.tsv",
}

VB_LABEL_FILES = {
    "old_prompt_p1_pass1": HUMAN_LABELS / "old_prompt/participant1_data_pass_1.tsv",
    "old_prompt_p1_pass2": HUMAN_LABELS / "old_prompt/participant1_data_pass_2.tsv",
    "p1_corrected": HUMAN_LABELS / "participant1_data_correct_prompt.tsv",
    "p2": HUMAN_LABELS / "participant2_data_pass_1.tsv",
    "p3": HUMAN_LABELS / "participant3_data_pass_1.tsv",
    "p4": HUMAN_LABELS / "participant4_data_pass_1.tsv",
    "p5": HUMAN_LABELS / "participant5_data_pass_1.tsv",
}


def read_tsv(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if not r.get("gold_file") or r.get("human_score_0_5") in (None, ""):
                continue
            rows.append(
                {
                    "gold_file": r["gold_file"].strip(),
                    "candidate_file": r["candidate_file"].strip(),
                    "score": float(r["human_score_0_5"]),
                }
            )
    return rows


def key_by_pair(rows):
    return {(r["gold_file"], r["candidate_file"]): r["score"] for r in rows}


def match_series(a_rows, b_rows):
    a = key_by_pair(a_rows)
    b = key_by_pair(b_rows)
    common = sorted(set(a) & set(b))
    identical = sum(1 for k in common if a[k] == b[k])
    return {
        "n_a": len(a),
        "n_b": len(b),
        "n_common_items": len(common),
        "n_identical_scores": identical,
        "identical_fraction_of_common": round(identical / len(common), 6) if common else None,
    }


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def build_vendored_gold_index():
    idx = {}
    for p in VENDORED_GOLD_ROOT.rglob("*.lean"):
        data = p.read_bytes()
        idx.setdefault(p.name, []).append(
            {"path": str(p.relative_to(CJ_ROOT)), "sha256": sha256_bytes(data)}
        )
    return idx


def git(args, cwd=VB_ROOT):
    return subprocess.run(
        ["git"] + args, cwd=cwd, capture_output=True, text=True, check=False
    )


GOLD_PREFIX = "veribench_dataset/lean_src/veribench/"

# The paper's/VeriBench's human_labels TSVs use a stale gold_file name for one task: no file
# named "0_unsafeMultiply_safe.lean" ever existed on veribench origin/main (verified by git log
# over full origin/main history) — only "1_unsafeMultiply_safe.lean" has, since 2025-09-20
# (commit 985a292c). The candidate filenames in the labels ("0_unsafeMultiply_safe__agentN.lean")
# confirm it is the same logical task under a name the label author used but the tree never had.
# IMPORTANT: exp16's OWN gold resolution (exp16_multi_judge_human_sets.py:_resolve_gold_path)
# does the same exact-basename lookup we do, found nothing, and recorded all 3 of this task's
# pairs in results_exp16_final_robust_r9_median/skipped_pairs.csv as reason=missing_gold. So the
# "judged bytes" below (found via this alias) were NEVER ACTUALLY USED by the frozen judge
# pipeline for this task -- it has zero rows in detail_rows.csv / judge_trust_vector and
# contributes nothing to any G0/V1-V5 computation. We still resolve the alias here to report
# what bytes a rater who used this stale name would have been looking at, for completeness.
GOLD_FILE_ALIASES = {"0_unsafeMultiply_safe.lean": "1_unsafeMultiply_safe.lean"}
SKIPPED_BY_JUDGE_PIPELINE = {"0_unsafeMultiply_safe.lean"}  # confirmed via skipped_pairs.csv


def git_full_history_for_basename(basename):
    """Return list of {rev, date, path, sha256} oldest-first for the gold file with this
    basename, restricted to `origin/main` (the mainline provenance.json itself audits) and to
    the real gold tree, to avoid playground/test/other-experiment copies and to avoid the cost
    of walking all 254 branches."""
    res = git(
        [
            "log",
            "--diff-filter=A",
            "--name-only",
            "--format=%H",
            "origin/main",
            "--",
            f"{GOLD_PREFIX}*{basename}",
        ]
    )
    paths = set()
    for line in res.stdout.splitlines():
        line = line.strip()
        if line and not all(c in "0123456789abcdef" for c in line):
            paths.add(line)
        elif line and len(line) == 40:
            continue
    timeline = []
    seen_rev_path = set()
    for p in paths:
        res = git(["log", "--follow", "--format=%H|%aI", "origin/main", "--", p])
        for line in res.stdout.splitlines():
            rev, date = line.split("|", 1)
            if (rev, p) in seen_rev_path:
                continue
            seen_rev_path.add((rev, p))
            show = subprocess.run(
                ["git", "show", f"{rev}:{p}"], cwd=VB_ROOT, capture_output=True, check=False
            )
            if show.returncode != 0:
                continue
            data = show.stdout
            timeline.append(
                {"rev": rev, "date": date, "path": p, "sha256": sha256_bytes(data)}
            )
    timeline.sort(key=lambda r: r["date"])
    return timeline


def main():
    results_dir = EXP_DIR / "results"
    results_dir.mkdir(exist_ok=True)

    # ---- Step 2: label identity ----
    paper_rows = {k: read_tsv(v) for k, v in PAPER_LABEL_FILES.items()}
    vb_rows = {k: read_tsv(v) for k, v in VB_LABEL_FILES.items()}

    label_identity = {"paper_vs_veribench": {}, "pass_name_mapping": {}}
    for pk, prows in paper_rows.items():
        best = None
        for vk, vrows in vb_rows.items():
            m = match_series(prows, vrows)
            if best is None or (m["n_identical_scores"], m["n_common_items"]) > (
                best[1]["n_identical_scores"],
                best[1]["n_common_items"],
            ):
                best = (vk, m)
        label_identity["paper_vs_veribench"][pk] = {
            "best_match_veribench_series": best[0],
            **best[1],
        }

    # Known claims from cc.md to check explicitly:
    checks = {
        "paper_pass1_vs_old_prompt_p1_pass2": match_series(
            paper_rows["paper_pass1_20260425"], vb_rows["old_prompt_p1_pass2"]
        ),
        "paper_pass2_vs_old_prompt_p1_pass1": match_series(
            paper_rows["paper_pass2_ORIGINAL"], vb_rows["old_prompt_p1_pass1"]
        ),
    }
    label_identity["pass_name_mapping"] = checks

    (results_dir / "label_identity.json").write_text(json.dumps(label_identity, indent=2) + "\n")

    # ---- Step 2b: build vendored (judge-seen) gold index ----
    vendored_idx = build_vendored_gold_index()

    # ---- Step 3/4: per-task provenance ----
    provenance = json.loads(PROVENANCE_JSON.read_text())
    # index provenance tasks by the basename of gold_path (this is the CURRENT filename)
    prov_by_current_basename = {}
    for task_id, t in provenance["tasks"].items():
        base = Path(t["gold_path"]).name
        prov_by_current_basename[base] = {"task_id": task_id, **t}

    # the 25 gold_file basenames actually used in the paper's label TSVs
    paper_gold_files = sorted({r["gold_file"] for r in paper_rows["paper_pass1_20260425"]})

    rows_out = []
    for gold_file in paper_gold_files:
        row = {"paper_gold_file": gold_file}
        resolved_file = GOLD_FILE_ALIASES.get(gold_file, gold_file)
        alias_note = f" [label uses stale name; resolved via known alias to {resolved_file}]" if resolved_file != gold_file else ""

        # (a) judge-seen: cert-judge vendored copy resolved by exact basename match
        vmatches = vendored_idx.get(resolved_file, [])
        if len(vmatches) == 1:
            row["judged_sha256"] = vmatches[0]["sha256"]
            row["judged_source"] = f"cert-judge vendored data/veribench_dataset ({vmatches[0]['path']}), frozen since 2026-04-12 (exp16/exp28 default veribench-root; no CLI override or cached request file found){alias_note}"
        elif len(vmatches) > 1:
            row["judged_sha256"] = "AMBIGUOUS:" + ",".join(sorted({m["sha256"] for m in vmatches}))
            row["judged_source"] = f"AMBIGUOUS: {len(vmatches)} files named {resolved_file} in vendored copy: {[m['path'] for m in vmatches]}"
        else:
            row["judged_sha256"] = None
            row["judged_source"] = "UNRESOLVED: no file with this basename in cert-judge vendored copy"

        # (b) full byte timeline across VeriBench history (handles renames automatically since we
        # search the real gold tree on origin/main for this basename)
        timeline = git_full_history_for_basename(resolved_file)
        row["_timeline"] = timeline  # kept for CSV helper columns below, stripped before some outputs

        # (c) current-name provenance.json cross-reference, if the CURRENT filename differs and
        # is known (best-effort; many paper names ARE already the current name)
        prov_entry = prov_by_current_basename.get(resolved_file)
        row["provenance100_task_id_same_name"] = prov_entry["task_id"] if prov_entry else None

        rows_out.append(row)

    # Rating dates (first commit date each VeriBench label-file's content was introduced)
    rating_dates = {}
    for k, path in VB_LABEL_FILES.items():
        res = git(["log", "--follow", "--diff-filter=A", "--format=%aI", "--", str(path.relative_to(VB_ROOT))])
        dates = res.stdout.strip().splitlines()
        rating_dates[k] = dates[-1] if dates else None  # oldest (first-add) date

    def as_of(timeline, date_iso):
        """Most recent timeline entry with date <= date_iso; None if no such entry (pre-dates
        all known history -> the earliest known entry is the best lower bound instead)."""
        if not timeline or date_iso is None:
            return None, "no_timeline_or_date"
        candidates = [t for t in timeline if t["date"] <= date_iso]
        if candidates:
            return candidates[-1], "as_of_or_before"
        return timeline[0], "extrapolated_to_earliest_known(predates_history)"

    final_rows = []
    for row in rows_out:
        timeline = row.pop("_timeline")
        pass1_ver, pass1_mode = as_of(timeline, rating_dates.get("old_prompt_p1_pass1"))
        pass2_ver, pass2_mode = as_of(timeline, rating_dates.get("old_prompt_p1_pass2"))
        corrected_ver, corrected_mode = as_of(timeline, rating_dates.get("p1_corrected"))

        judged = row["judged_sha256"]

        def matched(v):
            if row["paper_gold_file"] in SKIPPED_BY_JUDGE_PIPELINE:
                return "not_applicable_missing_gold_in_judge_pipeline"
            if v is None or judged is None or judged.startswith("AMBIGUOUS"):
                return "unresolvable"
            return "yes" if v["sha256"] == judged else "no"

        final_rows.append(
            {
                "gold_file": row["paper_gold_file"],
                "judged_sha256": judged,
                "judged_source": row["judged_source"],
                "n_timeline_versions": len(timeline),
                "rater_pass1_date": rating_dates.get("old_prompt_p1_pass1"),
                "rater_pass1_sha256": pass1_ver["sha256"] if pass1_ver else None,
                "rater_pass1_lookup_mode": pass1_mode,
                "matched_pass1": matched(pass1_ver),
                "rater_pass2_date": rating_dates.get("old_prompt_p1_pass2"),
                "rater_pass2_sha256": pass2_ver["sha256"] if pass2_ver else None,
                "rater_pass2_lookup_mode": pass2_mode,
                "matched_pass2": matched(pass2_ver),
                "rater_corrected_date": rating_dates.get("p1_corrected"),
                "rater_corrected_sha256": corrected_ver["sha256"] if corrected_ver else None,
                "rater_corrected_lookup_mode": corrected_mode,
                "matched_corrected": matched(corrected_ver),
                "provenance100_current_task_id": row["provenance100_task_id_same_name"],
            }
        )

    with open(results_dir / "provenance_by_task.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(final_rows[0].keys()))
        w.writeheader()
        w.writerows(final_rows)

    n_matched_pass1 = sum(1 for r in final_rows if r["matched_pass1"] == "yes")
    n_matched_pass2 = sum(1 for r in final_rows if r["matched_pass2"] == "yes")
    n_unresolved = sum(1 for r in final_rows if "unresolvable" in (r["matched_pass1"], r["matched_pass2"]))
    print(f"tasks={len(final_rows)} matched_pass1={n_matched_pass1} matched_pass2={n_matched_pass2} unresolved>=1_pass={n_unresolved}")
    for k, v in rating_dates.items():
        print(f"rating_date[{k}] = {v}")


if __name__ == "__main__":
    main()
