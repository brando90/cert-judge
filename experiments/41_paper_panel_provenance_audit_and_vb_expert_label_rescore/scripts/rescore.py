#!/usr/bin/env python3
"""Zero-model-call rescore: Gate G0 reproduction + views V1-V5 + secondary S1, S3.

All correlations are computed from frozen, already-committed files:
  - per-item judge scores: experiments/archive/04_veribench_validation/results_exp16_*/detail_rows.csv
  - label-free judge trust index: experiments/archive/04_veribench_validation/results_exp28_varaware_*/judge_trust_vector.csv
  - paper labels: experiments/archive/04_veribench_validation/data/ethan_human_scores_avg_two_passes_20260425.tsv
  - VeriBench corrected-prompt labels: veribench_e41 human_labels/{participant1_data_correct_prompt,participant2_data_pass_1,participant3_data_pass_1}.tsv
  - matched-task list: results/provenance_by_task.csv (this experiment's own step 3/4 output)

No model calls. Deterministic (fixed seed for the bootstrap only; all point estimates and the
exact permutation test are exact, not sampled).
"""
import csv
import itertools
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

EXP_DIR = Path(__file__).resolve().parents[1]
CJ_ROOT = EXP_DIR.parents[1]
VB04 = CJ_ROOT / "experiments/archive/04_veribench_validation"
VB13 = CJ_ROOT / "experiments/archive/13_qwen_replication_exp16_exp19"
VB_HUMAN_LABELS = Path("/lfs/skampere1/0/brando9/veribench_e41/veribench_dataset/human_labels")
RESULTS = EXP_DIR / "results"

SEED = 42
N_BOOT = 10000

FAMILIES = {
    "Codex": {
        "detail_rows": VB04 / "results_exp16_final_robust_r9_median/detail_rows.csv",
        "trust_vector": VB04 / "results_exp28_varaware_codex_avg_newindex/judge_trust_vector.csv",
    },
    "Claude Opus": {
        "detail_rows": VB04 / "results_exp16_opus47_r3_median/detail_rows.csv",
        "trust_vector": VB04 / "results_exp28_varaware_opus_avg_newindex/judge_trust_vector.csv",
    },
    "Qwen3-Coder": {
        "detail_rows": VB13 / "results/exp16_qwen_r3_median/detail_rows.csv",
        "trust_vector": VB04 / "results_exp28_varaware_qwen_avg/judge_trust_vector.csv",
    },
}

GOLD_FILE_ALIASES = {"1_unsafeMultiply_safe.lean": "0_unsafeMultiply_safe.lean"}


def read_tsv_scores(path):
    """Return dict[(gold_file,candidate_file)] -> float score, skipping blanks. Paper-native
    files already use the paper's naming convention, so no aliasing is applied here."""
    out = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            g = (r.get("gold_file") or "").strip()
            c = (r.get("candidate_file") or "").strip()
            s = r.get("human_score_0_5")
            if not g or not c or s in (None, ""):
                continue
            out[(g, c)] = float(s)
    return out


def alias_candidate_name(c, g_old, g_new):
    if g_new == g_old:
        return c
    old_stem = g_old[:-5]  # strip .lean
    new_stem = g_new[:-5]
    if c.startswith(new_stem):
        return old_stem + c[len(new_stem):]
    return c


def read_vb_label_file_paper_naming(path):
    """Read a VeriBench-native label TSV and rename gold/candidate to the paper's naming
    (only 1_unsafeMultiply_safe.lean -> 0_unsafeMultiply_safe.lean differs)."""
    out = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            g = (r.get("gold_file") or "").strip()
            c = (r.get("candidate_file") or "").strip()
            s = r.get("human_score_0_5")
            if not g or not c or s in (None, ""):
                continue
            g_paper = GOLD_FILE_ALIASES.get(g, g)
            c_paper = alias_candidate_name(c, g, g_paper)
            out[(g_paper, c_paper)] = float(s)
    return out


def load_matched_tasks():
    matched = set()
    all_tasks = set()
    with open(RESULTS / "provenance_by_task.csv", newline="") as f:
        for r in csv.DictReader(f):
            all_tasks.add(r["gold_file"])
            if r["matched_pass1"] == "yes":
                matched.add(r["gold_file"])
    return matched, all_tasks


def load_detail_rows(path):
    """dict[judge_id][(gold,cand)] -> score_mean, human_eval_union rows only."""
    out = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r["row_type"] != "human_eval_union":
                continue
            g, c = r["item_key"].split("::", 1)
            out.setdefault(r["judge_id"], {})[(g, c)] = float(r["score_mean"])
    return out


def load_trust_vector(path):
    ids, ti = [], []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            ids.append(r["judge_id"])
            ti.append(float(r["TI_variance_aware"]))
    return ids, np.array(ti)


def rankdata(x):
    return stats.rankdata(x, method="average")


def spearman(a, b):
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    return float(stats.spearmanr(a, b).statistic)


def kendall(a, b):
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    return float(stats.kendalltau(a, b).statistic)


def pearson(a, b):
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    return float(stats.pearsonr(a, b).statistic)


def exact_permutation_p(a, b):
    """Two-sided exact permutation p-value for Spearman(a,b) over all len(b)! orderings."""
    n = len(b)
    obs = abs(spearman(a, b))
    ra = rankdata(a)
    idx = list(range(n))
    cnt = tot = 0
    rb = rankdata(b)
    for perm in itertools.permutations(idx):
        tot += 1
        permuted = [rb[i] for i in perm]
        r = pearson(ra, permuted)
        if abs(r) >= obs - 1e-12:
            cnt += 1
    return cnt / tot


def human_agreement_per_judge(family_scores, label_map, item_filter):
    """For each judge, Spearman(judge_score, label) over items in item_filter that have both."""
    out = {}
    for judge_id, scores in family_scores.items():
        xs, ys = [], []
        for item in item_filter:
            if item in scores and item in label_map:
                xs.append(scores[item])
                ys.append(label_map[item])
        out[judge_id] = {"n": len(xs), "rho": spearman(xs, ys), "items": item_filter & set(scores) & set(label_map)}
    return out


def _np_rank(a):
    """Average-tie ranks, pure numpy (no scipy call overhead) -- used only in hot loops."""
    a = np.asarray(a, dtype=float)
    n = len(a)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(n, dtype=float)
    sorted_a = a[order]
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sorted_a[j + 1] == sorted_a[i]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def _fast_spearman(a, b):
    """Numerically equivalent to spearman() (Spearman = Pearson on average ranks) but skips
    scipy's per-call validation/hypothesis-test overhead; used only inside the hot bootstrap
    loop. Cross-checked against spearman()/scipy in test_rescore.py."""
    n = len(a)
    if n < 3:
        return float("nan")
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if np.all(a == a[0]) or np.all(b == b[0]):
        return float("nan")
    ra, rb = _np_rank(a), _np_rank(b)
    ma, mb = ra.mean(), rb.mean()
    sa = math.sqrt(((ra - ma) ** 2).sum())
    sb = math.sqrt(((rb - mb) ** 2).sum())
    if sa == 0 or sb == 0:
        return float("nan")
    return float(((ra - ma) * (rb - mb)).sum() / (sa * sb))


def task_clustered_bootstrap(family_scores, judge_ids, label_map, item_filter, ti_vector, rng):
    """Resample TASKS (gold_file) with replacement; recompute per-judge human_spearman on the
    resulting (possibly-repeated) item multiset, then the top-level Spearman(TI, human_spearman)
    for that replicate. Returns array of N_BOOT top-level rho values (NaNs dropped).

    Vectorized: precompute a (judges x items) score matrix and label vector once, then each draw
    is numpy fancy-indexing + _fast_spearman (no scipy call, no per-item dict lookups)."""
    items = sorted({it for it in item_filter if it in label_map})
    label_vec = np.array([label_map[it] for it in items])
    tasks_of_item = np.array([it[0] for it in items])
    unique_tasks = sorted(set(tasks_of_item))
    task_item_idx = {t: np.where(tasks_of_item == t)[0] for t in unique_tasks}

    score_matrix = np.full((len(judge_ids), len(items)), np.nan)
    for j, jid in enumerate(judge_ids):
        scores = family_scores[jid]
        for k, it in enumerate(items):
            if it in scores:
                score_matrix[j, k] = scores[it]

    n_tasks = len(unique_tasks)
    out = []
    for _ in range(N_BOOT):
        sampled_tasks = rng.choice(unique_tasks, size=n_tasks, replace=True)
        idx = np.concatenate([task_item_idx[t] for t in sampled_tasks])
        sub_labels = label_vec[idx]
        judge_rhos = np.full(len(judge_ids), np.nan)
        for j in range(len(judge_ids)):
            sub_scores = score_matrix[j, idx]
            mask = ~np.isnan(sub_scores)
            if mask.sum() >= 3:
                judge_rhos[j] = _fast_spearman(sub_scores[mask], sub_labels[mask])
        mask = ~np.isnan(judge_rhos)
        if mask.sum() < 3:
            continue
        r = _fast_spearman(ti_vector[mask], judge_rhos[mask])
        if not math.isnan(r):
            out.append(r)
    return np.array(out)


def main():
    matched_tasks, all_tasks = load_matched_tasks()
    print(f"matched tasks: {len(matched_tasks)} / {len(all_tasks)}")

    paper_avg = read_tsv_scores(VB04 / "data/ethan_human_scores_avg_two_passes_20260425.tsv")
    vb_p1_corr = read_vb_label_file_paper_naming(VB_HUMAN_LABELS / "participant1_data_correct_prompt.tsv")
    vb_p2 = read_vb_label_file_paper_naming(VB_HUMAN_LABELS / "participant2_data_pass_1.tsv")
    vb_p3 = read_vb_label_file_paper_naming(VB_HUMAN_LABELS / "participant3_data_pass_1.tsv")

    expert_mean = {}
    for item in set(vb_p1_corr) | set(vb_p2) | set(vb_p3):
        vals = [d[item] for d in (vb_p1_corr, vb_p2, vb_p3) if item in d]
        if vals:
            expert_mean[item] = sum(vals) / len(vals)

    all_items_any_label = set(paper_avg) | set(expert_mean)

    judge_level_rows = []
    per_judge_rows = []
    rng_master = np.random.default_rng(SEED)

    for family, paths in FAMILIES.items():
        family_scores = load_detail_rows(paths["detail_rows"])
        judge_ids, ti_vector = load_trust_vector(paths["trust_vector"])
        # restrict to judges present in both
        judge_ids = [j for j in judge_ids if j in family_scores]
        ti_vector = np.array([ti for j, ti in zip(*load_trust_vector(paths["trust_vector"])) if j in family_scores])

        any_item = set()
        for s in family_scores.values():
            any_item |= set(s.keys())

        views = {
            "V1_paper_avg_all72": (paper_avg, any_item),
            "V2_paper_avg_matched": (paper_avg, {i for i in any_item if i[0] in matched_tasks}),
            "V3_vb_expert_mean_matched": (expert_mean, {i for i in any_item if i[0] in matched_tasks}),
            "V4_vb_expert_mean_all": (expert_mean, any_item),
            "V5_vb_p1_corrected_matched": (vb_p1_corr, {i for i in any_item if i[0] in matched_tasks}),
        }

        for view_name, (label_map, item_filter) in views.items():
            agreement = human_agreement_per_judge(family_scores, label_map, item_filter)
            human_rho = np.array([agreement[j]["rho"] for j in judge_ids])
            valid = ~np.isnan(human_rho)
            for j in judge_ids:
                per_judge_rows.append(
                    {
                        "family": family,
                        "view": view_name,
                        "judge_id": j,
                        "n_items": agreement[j]["n"],
                        "human_spearman": round(agreement[j]["rho"], 6) if not math.isnan(agreement[j]["rho"]) else "",
                    }
                )
            if valid.sum() < 3:
                judge_level_rows.append(
                    {
                        "family": family,
                        "view": view_name,
                        "n_judges": int(valid.sum()),
                        "n_items_union": len(item_filter & all_items_any_label),
                        "rho_ti_spearman": "",
                        "rho_ti_kendall": "",
                        "rho_ti_pearson": "",
                        "perm_p_exact": "",
                        "boot_ci_lo": "",
                        "boot_ci_hi": "",
                        "note": "fewer than 3 judges with computable human_spearman",
                    }
                )
                continue
            ti_v = ti_vector[valid]
            hr_v = human_rho[valid]
            rho_s = spearman(ti_v, hr_v)
            rho_k = kendall(ti_v, hr_v)
            rho_p = pearson(ti_v, hr_v)
            pval = exact_permutation_p(ti_v, hr_v) if valid.sum() <= 9 else float("nan")
            boot = task_clustered_bootstrap(
                family_scores,
                [j for j, v in zip(judge_ids, valid) if v],
                label_map,
                item_filter,
                ti_v,
                np.random.default_rng(rng_master.integers(0, 2**32 - 1)),
            )
            ci_lo, ci_hi = (np.percentile(boot, [2.5, 97.5]) if len(boot) > 100 else (float("nan"), float("nan")))
            judge_level_rows.append(
                {
                    "family": family,
                    "view": view_name,
                    "n_judges": int(valid.sum()),
                    "n_items_union": len(item_filter & all_items_any_label),
                    "rho_ti_spearman": round(rho_s, 6),
                    "rho_ti_kendall": round(rho_k, 6),
                    "rho_ti_pearson": round(rho_p, 6),
                    "perm_p_exact": round(pval, 6) if not math.isnan(pval) else "",
                    "boot_ci_lo": round(float(ci_lo), 6) if not math.isnan(ci_lo) else "",
                    "boot_ci_hi": round(float(ci_hi), 6) if not math.isnan(ci_hi) else "",
                    "note": f"n_boot_valid={len(boot)}/{N_BOOT}",
                }
            )
            print(f"{family:<12} {view_name:<28} n_judges={int(valid.sum())} rho={rho_s:.3f} p={pval if not math.isnan(pval) else float('nan'):.3f} CI=[{ci_lo:.3f},{ci_hi:.3f}]")

    with open(RESULTS / "judge_level_views.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(judge_level_rows[0].keys()))
        w.writeheader()
        w.writerows(judge_level_rows)

    with open(RESULTS / "per_judge_agreement.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_judge_rows[0].keys()))
        w.writeheader()
        w.writerows(per_judge_rows)

    # ---- S1: leave-one-family-out / leave-one-configuration-out under V1 and V3 ----
    s1_rows = []
    for family, paths in FAMILIES.items():
        family_scores = load_detail_rows(paths["detail_rows"])
        judge_ids_full, ti_full = load_trust_vector(paths["trust_vector"])
        judge_ids = [j for j in judge_ids_full if j in family_scores]
        ti_vector = np.array([t for j, t in zip(judge_ids_full, ti_full) if j in family_scores])
        any_item = set()
        for s in family_scores.values():
            any_item |= set(s.keys())
        for view_name, label_map, base_filter in [
            ("V1", paper_avg, any_item),
            ("V3", expert_mean, {i for i in any_item if i[0] in matched_tasks}),
        ]:
            agreement = human_agreement_per_judge(family_scores, label_map, base_filter)
            human_rho = np.array([agreement[j]["rho"] for j in judge_ids])
            valid = ~np.isnan(human_rho)
            full_rho = spearman(ti_vector[valid], human_rho[valid]) if valid.sum() >= 3 else float("nan")
            for leave_out in judge_ids:
                keep = [j != leave_out for j in judge_ids]
                keep = np.array(keep) & valid
                r = spearman(ti_vector[keep], human_rho[keep]) if keep.sum() >= 3 else float("nan")
                s1_rows.append(
                    {
                        "family": family,
                        "view": view_name,
                        "leave_out_config": leave_out,
                        "n_remaining": int(keep.sum()),
                        "rho_full": round(full_rho, 6) if not math.isnan(full_rho) else "",
                        "rho_leave_one_out": round(r, 6) if not math.isnan(r) else "",
                    }
                )

    with open(RESULTS / "lofo_loco.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(s1_rows[0].keys()))
        w.writeheader()
        w.writerows(s1_rows)

    # ---- S3: label-agreement matrix ----
    label_sources = {
        "paper_pass1": read_tsv_scores(VB04 / "data/ethan_human_scores_20260425.tsv"),
        "paper_pass2": read_tsv_scores(VB04 / "data/ethan_human_scores_ORIGINAL.tsv"),
        "vb_p1_corrected": vb_p1_corr,
        "vb_p2": vb_p2,
        "vb_p3": vb_p3,
        "vb_expert_mean": expert_mean,
    }
    s3_rows = []
    names = list(label_sources.keys())
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            common = set(label_sources[a]) & set(label_sources[b])
            common_matched = {i for i in common if i[0] in matched_tasks}
            common_unmatched = {i for i in common if i[0] not in matched_tasks}

            def rho_over(items):
                if len(items) < 3:
                    return "", 0
                items = sorted(items)
                xs = [label_sources[a][i] for i in items]
                ys = [label_sources[b][i] for i in items]
                r = spearman(xs, ys)
                return (round(r, 6) if not math.isnan(r) else ""), len(items)

            r_all, n_all = rho_over(common)
            r_m, n_m = rho_over(common_matched)
            r_u, n_u = rho_over(common_unmatched)
            s3_rows.append(
                {
                    "series_a": a,
                    "series_b": b,
                    "n_common_all": n_all,
                    "spearman_all": r_all,
                    "n_common_matched": n_m,
                    "spearman_matched": r_m,
                    "n_common_unmatched": n_u,
                    "spearman_unmatched": r_u,
                }
            )

    with open(RESULTS / "label_agreement_matrix.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(s3_rows[0].keys()))
        w.writeheader()
        w.writerows(s3_rows)

    print("wrote judge_level_views.csv, per_judge_agreement.csv, lofo_loco.csv, label_agreement_matrix.csv")


if __name__ == "__main__":
    main()
