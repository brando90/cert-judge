#!/usr/bin/env python3
"""Zero-spend proper-scoring (RPS, CE, TVD, Brier) & agreement expansion across cert-judge panels and live VB ratings.

Outputs machine-readable JSON and CSV summaries under experiments/68_.../results/ without touching frozen archives.
Also cross-checks exact numerical reproduction of archive/51 (rescore_proper) and E63 report_test/report_e64 Spearman.
"""
from __future__ import annotations

import concurrent.futures
import csv
import difflib
import hashlib
import io
import json
import math
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from scipy import stats

SCRIPT_DIR = Path(__file__).resolve().parent
EXP_DIR = SCRIPT_DIR.parent
RESULTS_DIR = EXP_DIR / "results"
CJ_ROOT = EXP_DIR.parents[1]
VB_ROOT = CJ_ROOT.parent / "veribench"
TTJ_EXP09 = CJ_ROOT.parent / "trustworthy-theorem-judges/experiments/09_prepare_packets_and_collect_human_ratings_start_28Sep2026"

sys.path.insert(0, str(SCRIPT_DIR))
import metrics as M  # noqa: E402

ITEMS_JSONL = VB_ROOT / "experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/items.jsonl"
ITEMS_SHA256_EXPECTED = "ad9ed552fc2ffac6328e6010bf6be82215dd74f1eddd791622d433126877a96c"

VB04 = CJ_ROOT / "experiments/archive/04_veribench_validation"
VB13 = CJ_ROOT / "experiments/archive/13_qwen_replication_exp16_exp19"
HL_DIR = CJ_ROOT / "experiments/human_labels"
ARCHIVE51_JSON = CJ_ROOT / "experiments/archive/51_certjudge_rescore_rps_ce_tvd_nov2026/rescore_proper_results.json"

MIN_CRIT_COV = 0.90
BOOT_DRAWS = 10000
SEED_BOOT_DRAWS = 2000
PAPER_BOOT_DRAWS = 2000
SEED = 68


def load_items_with_human_labels() -> tuple[list[dict], dict[str, dict]]:
    """Load and SHA-256 verify VeriBench experiment 100 items.jsonl (75 items with p1..p5)."""
    raw = ITEMS_JSONL.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != ITEMS_SHA256_EXPECTED:
        raise RuntimeError(f"items.jsonl sha256 mismatch: {sha} != {ITEMS_SHA256_EXPECTED}")
    items = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    for it in items:
        it["all5_ratings"] = [int(round(float(it[p]))) for p in ("p1", "p2", "p3", "p4", "p5") if it[p] is not None]
        it["expert3_ratings"] = [int(round(float(it[p]))) for p in ("p1", "p2", "p3") if it[p] is not None]
    by_item = {it["item"]: it for it in items}
    return items, by_item


def _eval_with_ci(
    probs_mat: np.ndarray,
    rating_lists: list[list[int]],
    task_ids: list[str],
    judge_05: np.ndarray | None = None,
    draws: int = BOOT_DRAWS,
    seed: int = SEED,
    boot_kendall: bool = True,
) -> dict[str, object]:
    """Point estimates + 95% task-cluster bootstrap CIs for all proper and scalar metrics."""
    losses = M.per_item_losses(probs_mat, rating_lists)
    j05 = losses["ev_05"] if judge_05 is None else np.asarray(judge_05, dtype=float)
    h05 = losses["hum_mean_05"]

    metric_names = [
        "rps", "rps_dist_err", "ce", "tvd", "brier",
        "mae_05", "bias_05", "judge_mean_05", "human_mean_05",
        "icc_a1", "icc_c1", "spearman", "kendall", "pearson",
    ]

    def stat_vec(ii: np.ndarray, do_kendall: bool = True) -> np.ndarray:
        sub_j = j05[ii]
        sub_h = h05[ii]
        diff = sub_j - sub_h
        icc_a, icc_c = M.icc_two_way_both(sub_j, sub_h)
        return np.array([
            float(np.mean(losses["rps"][ii])),
            float(np.mean(losses["rps_dist_err"][ii])),
            float(np.mean(losses["ce"][ii])),
            float(np.mean(losses["tvd"][ii])),
            float(np.mean(losses["brier"][ii])),
            float(np.mean(np.abs(diff))),
            float(np.mean(diff)),
            float(np.mean(sub_j)),
            float(np.mean(sub_h)),
            icc_a,
            icc_c,
            M.spearman_corr(sub_j, sub_h),
            M.kendall_corr(sub_j, sub_h) if do_kendall else float("nan"),
            M.pearson_corr(sub_j, sub_h),
        ], dtype=float)

    all_idx = np.arange(len(rating_lists), dtype=int)
    pt_exact = stat_vec(all_idx, do_kendall=True)
    boot = M.task_cluster_bootstrap(task_ids, lambda ii: stat_vec(ii, do_kendall=boot_kendall), draws=draws, seed=seed)
    out: dict[str, object] = {
        "n_items": len(rating_lists),
        "n_tasks": len(set(task_ids)),
        "draws": draws,
        "finite_draws": boot["finite_draws"],
        "per_item": losses,
    }
    for idx, name in enumerate(metric_names):
        out[name] = {
            "val": float(pt_exact[idx]),
            "ci_lo": float(boot["ci_lo"][idx]),
            "ci_hi": float(boot["ci_hi"][idx]),
        }
    return out


# ===================================================================== Study A: E63 Native Distributional Judges
def run_study_a_e63(items: list[dict], by_item: dict[str, dict]) -> dict[str, object]:
    """Evaluate E63 Qwen3-8B native 6-class probability forecasts (probs) with proper scoring rules."""
    e63_runs_dir = CJ_ROOT / "experiments/63_judge_optimization_arms_prompt_sft_rl_qwen3_8b/results/runs"
    e64_frozen = json.loads((CJ_ROOT / "experiments/63_judge_optimization_arms_prompt_sft_rl_qwen3_8b/results/report_e64.json").read_text())

    run_specs = {
        "zero_shot_base": ["base_q3_8b_test.json"],
        "prompt_opt_arm1": ["arm1_q3_8b_s0/eval_test.json", "arm1_q3_8b_s1/eval_test.json"],
        "rl_grpo": ["rl_q3_8b_s0/eval_test.json", "rl_q3_8b_s1/eval_test.json", "rl_q3_8b_s2/eval_test.json"],
        "teacher_only_sft": [f"sft_q3_8b_s{i}/eval_test.json" for i in range(6)],
        "human_mix_sft": [f"sft_q3_8b_hm_s{i}/eval_test.json" for i in range(5)],
        "shuffled_control": ["sft_q3_8b_shuf_s0/eval_test.json"],
    }

    # Reference items sorted canonically from test split of items.jsonl (30 items, 10 tasks)
    test_items = sorted([it for it in items if it["split"] == "test"], key=lambda r: r["item"])
    trainval_items = [it for it in items if it["split"] in ("train", "val")]
    item_order = [it["item"] for it in test_items]
    task_ids = [it["task"] for it in test_items]

    # Assert exact match against every E63 run's crit test items & verify E64 Spearman reproduction
    arm_runs: dict[str, list[dict]] = {}
    for arm, rels in run_specs.items():
        loaded = []
        for rel in rels:
            raw = json.loads((e63_runs_dir / rel).read_text())
            res = raw["res"]
            crits = {v["item"]: v for v in res.values() if v.get("split") == "test" and v.get("human") is not None}
            if sorted(crits) != item_order:
                raise RuntimeError(f"E63 run {rel} items differ from test split ({len(crits)})")
            # Cross-check E63 human field matches target_expert to 1e-12
            for k in item_order:
                if abs(float(crits[k]["human"]) - float(by_item[k]["target_expert"])) > 1e-12:
                    raise RuntimeError(f"E63 human mismatch on {k} in {rel}")
                p = M.validate_probs(crits[k]["probs"])
                ev_from_p = M.expected_score_05(p) / 5.0
                if abs(ev_from_p - float(crits[k]["ev"])) > 1e-6:
                    raise RuntimeError(f"E63 ev vs probs mismatch on {k} in {rel}: {ev_from_p} vs {crits[k]['ev']}")
            probs_mat = np.vstack([M.validate_probs(crits[k]["probs"]) for k in item_order])
            ev05_vec = np.array([5.0 * float(crits[k]["ev"]) for k in item_order], dtype=float)
            loaded.append({"rel": rel, "probs": probs_mat, "ev05": ev05_vec})
        arm_runs[arm] = loaded

    # Exact reproduction check against report_e64.json (Spearman of mean EV vs target_expert)
    expert3_means05 = np.array([float(np.mean(it["expert3_ratings"])) for it in test_items], dtype=float)
    repro_checks = {}
    for e64_key, arm_key in (("teacher_only_SFT", "teacher_only_sft"), ("human_mix_SFT", "human_mix_sft")):
        runs = arm_runs[arm_key]
        per_seed_sp = [M.spearman_corr(r["ev05"], expert3_means05) for r in runs]
        max_seed_diff = max(abs(a - b) for a, b in zip(per_seed_sp, e64_frozen[e64_key]["per_seed"]))
        ens_ev05 = np.mean([r["ev05"] for r in runs], axis=0)
        ens_sp = M.spearman_corr(ens_ev05, expert3_means05)
        ens_diff = abs(ens_sp - float(e64_frozen[e64_key]["ens"]))
        if max_seed_diff > 1e-9 or ens_diff > 1e-9:
            raise RuntimeError(f"E64 Spearman mismatch for {arm_key}: seed_diff={max_seed_diff}, ens_diff={ens_diff}")
        repro_checks[arm_key] = {"max_seed_spearman_diff": max_seed_diff, "ens_spearman_diff": ens_diff}

    # Evaluate against both all5 (primary) and expert3 (secondary)
    targets = {
        "all5": [it["all5_ratings"] for it in test_items],
        "expert3": [it["expert3_ratings"] for it in test_items],
    }

    study_a: dict[str, object] = {"reproduction_check_vs_e64": repro_checks, "targets": {}}
    for tname, rating_lists in targets.items():
        # Constant baseline fitted ONLY on train+val (45 items)
        tv_lists = [it["all5_ratings"] if tname == "all5" else it["expert3_ratings"] for it in trainval_items]
        const_probs = M.fit_const(tv_lists, alpha=0.5)(np.zeros(len(test_items)))
        const_eval = _eval_with_ci(const_probs, rating_lists, task_ids, boot_kendall=False)

        # Human LORO ceiling on the 30 test items
        loro = M.leave_one_rater_out_ceiling(rating_lists, task_ids=task_ids, alpha=0.5, draws=BOOT_DRAWS, seed=SEED)

        arms_out: dict[str, object] = {}
        ens_losses_by_arm: dict[str, dict[str, np.ndarray]] = {}
        for arm, runs in arm_runs.items():
            # Individual seed evaluations
            seed_evals = []
            for r in runs:
                ev = _eval_with_ci(r["probs"], rating_lists, task_ids, judge_05=r["ev05"], draws=SEED_BOOT_DRAWS, boot_kendall=False)
                ev_clean = {k: v for k, v in ev.items() if k != "per_item"}
                ev_clean["run"] = r["rel"]
                seed_evals.append(ev_clean)

            # Mixture-of-probabilities ensemble (equal weight across seeds)
            ens_probs = np.mean([r["probs"] for r in runs], axis=0)
            ens_ev05 = ens_probs @ M.CATEGORIES
            ens_eval = _eval_with_ci(ens_probs, rating_lists, task_ids, judge_05=ens_ev05, boot_kendall=False)
            ens_losses_by_arm[arm] = ens_eval.pop("per_item")

            # Seed variability on proper scores
            seed_summary = {
                m: {
                    "mean": float(np.mean([s[m]["val"] for s in seed_evals])),
                    "sd": float(np.std([s[m]["val"] for s in seed_evals], ddof=1)) if len(seed_evals) > 1 else 0.0,
                }
                for m in ("rps", "ce", "tvd", "brier", "mae_05", "bias_05", "icc_a1", "spearman")
            }
            arms_out[arm] = {
                "n_seeds": len(runs),
                "ensemble": ens_eval,
                "seed_summary": seed_summary,
                "per_seed": seed_evals,
            }

        # Pre-specified paired contrasts (difference = A - B; negative is better for loss metrics RPS/CE/TVD/Brier/MAE)
        const_losses = const_eval.pop("per_item")
        ens_losses_by_arm["CONST_trainval"] = const_losses
        contrast_pairs = [
            ("human_mix_sft", "teacher_only_sft"),
            ("human_mix_sft", "rl_grpo"),
            ("human_mix_sft", "prompt_opt_arm1"),
            ("human_mix_sft", "zero_shot_base"),
            ("human_mix_sft", "CONST_trainval"),
            ("teacher_only_sft", "CONST_trainval"),
            ("rl_grpo", "CONST_trainval"),
        ]
        contrasts = []
        for arm_a, arm_b in contrast_pairs:
            la, lb = ens_losses_by_arm[arm_a], ens_losses_by_arm[arm_b]
            row = {"a": arm_a, "b": arm_b}
            loss_keys = ("rps", "ce", "tvd", "brier")
            diff_mat = np.column_stack([la[m] - lb[m] for m in loss_keys])
            boot = M.task_cluster_bootstrap(task_ids, lambda ii, dm=diff_mat: np.mean(dm[ii], axis=0), draws=BOOT_DRAWS, seed=SEED)
            for idx_m, m in enumerate(loss_keys):
                sf = M.paired_task_signflip_p(task_ids, la[m], lb[m], draws=BOOT_DRAWS, seed=SEED)
                row[m] = {
                    "diff": float(boot["point"][idx_m]),
                    "ci_lo": float(boot["ci_lo"][idx_m]),
                    "ci_hi": float(boot["ci_hi"][idx_m]),
                    "p_val": float(sf["p_val"]),
                    "p_method": sf["method"],
                }
            # Paired Spearman difference (bootstrap CI; signflip does not apply to rank correlations)
            ja, jb, hum = la["ev_05"], lb["ev_05"], la["hum_mean_05"]
            sp_boot = M.task_cluster_bootstrap(
                task_ids,
                lambda ii, a=ja, b=jb, h=hum: M.spearman_corr(a[ii], h[ii]) - M.spearman_corr(b[ii], h[ii]),
                draws=BOOT_DRAWS,
                seed=SEED,
            )
            row["spearman_diff"] = {
                "diff": float(sp_boot["point"]),
                "ci_lo": float(sp_boot["ci_lo"]),
                "ci_hi": float(sp_boot["ci_hi"]),
                "p_val": "n/a",
            }
            contrasts.append(row)

        study_a["targets"][tname] = {
            "const_trainval_baseline": const_eval,
            "human_loro_ceiling": loro,
            "arms": arms_out,
            "paired_contrasts": contrasts,
        }
    return study_a


# ===================================================================== Study B: E39 60-Unit Multi-Family Panel
def _extract_e39_scores_by_item(harvest_path: Path) -> dict[str, list[float]]:
    data = json.loads(harvest_path.read_text())
    out: dict[str, list[float]] = {}
    for c in data["cells"]:
        if c["kind"] == "crit" and c["status"] in ("measured", "deterministic") and c.get("score") is not None:
            out.setdefault(c["item"], []).append(float(c["score"]))
    return out


def _meta_table_over_units(
    rows: list[dict],
    index_keys: list[str],
    criterion_specs: list[tuple[str, float]],
    draws: int = BOOT_DRAWS,
    boot_draws: int = 2000,
    seed: int = SEED,
) -> list[dict]:
    """Compute meta-associations between behavioral indices and proper/scalar human alignment criteria."""
    out = []
    for crit_key, sign in criterion_specs:
        for idx_key in index_keys:
            elig = [r for r in rows if r["indices"].get(idx_key) is not None and r["metrics"].get(crit_key) is not None]
            if len(elig) < 8:
                continue
            xs = [float(r["indices"][idx_key]) for r in elig]
            ys = [sign * float(r["metrics"][crit_key]) for r in elig]
            fams = [str(r["family"]) for r in elig]
            meta = M.meta_association(xs, ys, families=fams, draws=draws, seed=seed, boot_draws=boot_draws)
            out.append({"criterion": crit_key, "higher_is_better_sign": sign, "index": idx_key, **meta})
    return out


def _selection_regret(rows: list[dict], index_key: str, loss_key: str) -> dict[str, object]:
    """Pick the highest-index unit and compare its held-out loss against oracle best, mean H2, and all-unit mean."""
    elig = [r for r in rows if r["indices"].get(index_key) is not None and r["metrics"].get(loss_key) is not None]
    if not elig:
        return {"n_units": 0}
    selected = max(elig, key=lambda r: (float(r["indices"][index_key]), r["config"]))
    oracle = min(elig, key=lambda r: float(r["metrics"][loss_key]))
    h2_units = [r for r in elig if r["config"].endswith("|H2")]
    h2_mean = float(np.mean([float(r["metrics"][loss_key]) for r in h2_units])) if h2_units else float("nan")
    pool_mean = float(np.mean([float(r["metrics"][loss_key]) for r in elig]))
    sel_val = float(selected["metrics"][loss_key])
    ora_val = float(oracle["metrics"][loss_key])
    return {
        "n_units": len(elig),
        "index": index_key,
        "loss": loss_key,
        "selected_config": selected["config"],
        "selected_index_val": float(selected["indices"][index_key]),
        "selected_loss": sel_val,
        "oracle_config": oracle["config"],
        "oracle_loss": ora_val,
        "regret_vs_oracle": sel_val - ora_val,
        "h2_mean_loss": h2_mean,
        "pool_mean_loss": pool_mean,
    }


def run_study_b_e39(items: list[dict]) -> dict[str, object]:
    """Evaluate all E39 60 harvest configs (56 LLMs + 4 controls) on raw and train-calibrated proper losses."""
    e39_dir = CJ_ROOT / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families/results"
    u_tv = json.loads((e39_dir / "units_train_val.json").read_text())["units"]
    u_test = json.loads((e39_dir / "units_test.json").read_text())["units"]
    all_units = u_tv + u_test

    by_cfg_path = {}
    for hp in sorted((e39_dir / "harvest").glob("*.json")):
        d = json.loads(hp.read_text())
        by_cfg_path[d["config"]] = hp

    train_items = sorted([it for it in items if it["split"] == "train"], key=lambda r: r["item"])
    heldout_items = sorted([it for it in items if it["split"] in ("val", "test")], key=lambda r: r["item"])
    test_only_items = sorted([it for it in items if it["split"] == "test"], key=lambda r: r["item"])

    # Constant baselines fit ONLY on train_items (30 items, 10 tasks)
    tr_all5 = [it["all5_ratings"] for it in train_items]
    ho_all5 = [it["all5_ratings"] for it in heldout_items]
    ho_exp3 = [it["expert3_ratings"] for it in heldout_items]
    ho_tasks = [it["task"] for it in heldout_items]
    te_all5 = [it["all5_ratings"] for it in test_only_items]
    te_tasks = [it["task"] for it in test_only_items]

    const_ho_all5 = M.evaluate_forecast_panel(M.fit_const(tr_all5)(np.zeros(len(heldout_items))), ho_all5)
    const_ho_exp3 = M.evaluate_forecast_panel(
        M.fit_const([it["expert3_ratings"] for it in train_items])(np.zeros(len(heldout_items))),
        ho_exp3,
    )
    loro_ho_all5 = M.leave_one_rater_out_ceiling(ho_all5, task_ids=ho_tasks, alpha=0.5, draws=BOOT_DRAWS, seed=SEED)
    loro_ho_exp3 = M.leave_one_rater_out_ceiling(ho_exp3, task_ids=ho_tasks, alpha=0.5, draws=BOOT_DRAWS, seed=SEED)

    unit_rows = []
    for u in all_units:
        cfg = u["config"]
        scores_map = _extract_e39_scores_by_item(by_cfg_path[cfg])

        ho_elig = [it for it in heldout_items if it["item"] in scores_map]
        tr_elig = [it for it in train_items if it["item"] in scores_map]
        ho_cov = len(ho_elig) / float(len(heldout_items))
        tr_cov = len(tr_elig) / float(len(train_items))

        metrics_dict: dict[str, float | None] = {}
        if ho_cov + 1e-9 >= MIN_CRIT_COV:
            raw_probs = np.vstack([M.binned_repeats_to_probs(scores_map[it["item"]], alpha=0.5) for it in ho_elig])
            raw_probs_a005 = np.vstack([M.binned_repeats_to_probs(scores_map[it["item"]], alpha=0.05) for it in ho_elig])
            raw_med_05 = np.array([5.0 * float(np.median(scores_map[it["item"]])) for it in ho_elig], dtype=float)
            raw_mean_05 = np.array([5.0 * float(np.mean(scores_map[it["item"]])) for it in ho_elig], dtype=float)

            ho_r_all5 = [it["all5_ratings"] for it in ho_elig]
            ho_r_exp3 = [it["expert3_ratings"] for it in ho_elig]
            ev_raw_all5 = M.evaluate_forecast_panel(raw_probs, ho_r_all5, judge_05=raw_med_05)
            ev_raw_all5_a005 = M.evaluate_forecast_panel(raw_probs_a005, ho_r_all5, judge_05=raw_med_05)
            ev_raw_exp3 = M.evaluate_forecast_panel(raw_probs, ho_r_exp3, judge_05=raw_med_05)

            for k, v in ev_raw_all5.items():
                metrics_dict[f"raw_all5_{k}"] = v
            metrics_dict["raw_all5_ce_a005"] = ev_raw_all5_a005["ce"]
            metrics_dict["raw_all5_mean_repeat_spearman"] = M.spearman_corr(raw_mean_05, np.array([np.mean(r) for r in ho_r_all5]))
            for k, v in ev_raw_exp3.items():
                metrics_dict[f"raw_exp3_{k}"] = v

            # Train-task calibrated (fit ONLY on train split, evaluated ONLY on val+test)
            if tr_cov + 1e-9 >= MIN_CRIT_COV:
                tr_s = np.array([float(np.median(scores_map[it["item"]])) for it in tr_elig], dtype=float)
                ho_s = np.array([float(np.median(scores_map[it["item"]])) for it in ho_elig], dtype=float)
                tr_r_all5 = [it["all5_ratings"] for it in tr_elig]
                tr_r_exp3 = [it["expert3_ratings"] for it in tr_elig]

                ce_fn_5 = M.fit_ce_ordinal(tr_s, tr_r_all5)
                pe_fn_5 = M.fit_pearson_gauss(tr_s, tr_r_all5)
                ev_ce_5 = M.evaluate_forecast_panel(ce_fn_5(ho_s), ho_r_all5)
                ev_pe_5 = M.evaluate_forecast_panel(pe_fn_5(ho_s), ho_r_all5)
                for k, v in ev_ce_5.items():
                    metrics_dict[f"ce_cal_all5_{k}"] = v
                for k, v in ev_pe_5.items():
                    metrics_dict[f"pe_cal_all5_{k}"] = v

                ce_fn_3 = M.fit_ce_ordinal(tr_s, tr_r_exp3)
                ev_ce_3 = M.evaluate_forecast_panel(ce_fn_3(ho_s), ho_r_exp3)
                for k, v in ev_ce_3.items():
                    metrics_dict[f"ce_cal_exp3_{k}"] = v

        unit_rows.append({
            "config": cfg,
            "family": u["family"],
            "split": u["split"],
            "kind": u["kind"],
            "harness": u["harness"],
            "train_cov": round(tr_cov, 4),
            "heldout_cov": round(ho_cov, 4),
            "indices": u["indices"],
            "e39_frozen_heldout_sp": (u["criteria"].get("heldout") or {}).get("spearman"),
            "metrics": metrics_dict,
        })

    # Verify E39 frozen expert3 Spearman matches our raw_exp3_spearman to 1e-9
    for r in unit_rows:
        f_sp = r["e39_frozen_heldout_sp"]
        c_sp = r["metrics"].get("raw_exp3_spearman")
        if f_sp is not None and c_sp is not None and abs(float(f_sp) - float(c_sp)) > 1e-9:
            raise RuntimeError(f"E39 Spearman mismatch on {r['config']}: {f_sp} vs {c_sp}")

    test_llm = [r for r in unit_rows if r["split"] == "test" and r["kind"] == "llm"]
    all_llm = [r for r in unit_rows if r["kind"] == "llm"]

    index_keys = ["C_ms_gold", "TI_var_trainnorm", "PTI_v0_frozen", "C_bm_gold"]
    criterion_specs = [
        ("raw_all5_rps", -1.0),
        ("raw_all5_ce", -1.0),
        ("raw_all5_tvd", -1.0),
        ("raw_all5_brier", -1.0),
        ("raw_all5_icc_a1", 1.0),
        ("raw_all5_spearman", 1.0),
        ("ce_cal_all5_rps", -1.0),
        ("ce_cal_all5_ce", -1.0),
        ("ce_cal_all5_tvd", -1.0),
        ("ce_cal_all5_brier", -1.0),
        ("ce_cal_all5_icc_a1", 1.0),
        ("pe_cal_all5_rps", -1.0),
        ("raw_exp3_spearman", 1.0),
        ("ce_cal_exp3_rps", -1.0),
    ]

    meta_test_llm = _meta_table_over_units(test_llm, index_keys, criterion_specs)
    meta_all_llm = _meta_table_over_units(all_llm, index_keys, criterion_specs)

    regret = []
    for subset_name, sub_rows in (("test_llm", test_llm), ("all_llm", all_llm)):
        for idx_k in ("C_ms_gold", "TI_var_trainnorm", "PTI_v0_frozen"):
            for loss_k in ("raw_all5_rps", "ce_cal_all5_rps", "ce_cal_all5_ce", "ce_cal_all5_tvd"):
                regret.append({"subset": subset_name, **_selection_regret(sub_rows, idx_k, loss_k)})

    return {
        "n_total_units": len(unit_rows),
        "n_test_llm": len(test_llm),
        "n_all_llm": len(all_llm),
        "const_train_baseline_heldout_all5": const_ho_all5,
        "const_train_baseline_heldout_exp3": const_ho_exp3,
        "human_loro_heldout_all5": loro_ho_all5,
        "human_loro_heldout_exp3": loro_ho_exp3,
        "meta_test_llm": meta_test_llm,
        "meta_all_llm": meta_all_llm,
        "selection_regret": regret,
        "units": unit_rows,
    }


# ===================================================================== Study C: Paper 8-Config Panels
def _read_legacy_labels(path: Path, rename_alias: bool = False) -> dict[tuple[str, str], float]:
    alias = {"1_unsafeMultiply_safe.lean": "0_unsafeMultiply_safe.lean"}
    out = {}
    for r in csv.DictReader(open(path), delimiter="\t"):
        g, c, s = r["gold_file"].strip(), r["candidate_file"].strip(), r["human_score_0_5"]
        if not g or not c or s in ("", None):
            continue
        if rename_alias and g in alias:
            g2 = alias[g]
            c = g2[:-5] + c[len(g[:-5]):] if c.startswith(g[:-5]) else c
            g = g2
        out[(g, c)] = float(s)
    return out


def _load_paper_detail(path: Path) -> dict[str, dict[tuple[str, str], tuple[float, list[float]]]]:
    out: dict[str, dict[tuple[str, str], tuple[float, list[float]]]] = {}
    for r in csv.DictReader(open(path)):
        if r["row_type"] != "human_eval_union":
            continue
        g, c = r["item_key"].split("::", 1)
        out.setdefault(r["judge_id"], {})[(g, c)] = (float(r["score_mean"]), json.loads(r["repeat_scores"]))
    return out


def _loto_paper(rating_lists: list[list[int]], scores_01: np.ndarray, tasks: list[str]) -> dict[str, dict[str, object]]:
    """Leave-one-task-out CONST, CE-fit, and Pearson-fit evaluated equally across artifacts."""
    n = len(rating_lists)
    tasks_arr = np.asarray(tasks)
    preds = {k: np.zeros((n, 6), dtype=float) for k in ("CONST", "CE_fit", "Pearson_fit")}
    for t in sorted(set(tasks)):
        te = np.where(tasks_arr == t)[0]
        tr = np.where(tasks_arr != t)[0]
        tr_lists = [rating_lists[i] for i in tr]
        preds["CONST"][te] = M.fit_const(tr_lists, alpha=0.5)(scores_01[te])
        preds["CE_fit"][te] = M.fit_ce_ordinal(scores_01[tr], tr_lists)(scores_01[te])
        preds["Pearson_fit"][te] = M.fit_pearson_gauss(scores_01[tr], tr_lists)(scores_01[te])

    out = {}
    per_item_by_fitter = {}
    for name, pm in preds.items():
        ev = _eval_with_ci(pm, rating_lists, tasks, draws=PAPER_BOOT_DRAWS, seed=SEED, boot_kendall=False)
        per_item_by_fitter[name] = ev.pop("per_item")
        out[name] = ev
    # Paired differences CE_fit - CONST and CE_fit - Pearson_fit on RPS
    for other in ("CONST", "Pearson_fit"):
        la, lb = per_item_by_fitter["CE_fit"], per_item_by_fitter[other]
        diff = la["rps"] - lb["rps"]
        boot = M.task_cluster_bootstrap(tasks, lambda ii, d=diff: float(np.mean(d[ii])), draws=PAPER_BOOT_DRAWS, seed=SEED)
        sf = M.paired_task_signflip_p(tasks, la["rps"], lb["rps"], draws=PAPER_BOOT_DRAWS, seed=SEED)
        out[f"diff_CE_minus_{other}_rps"] = {
            "diff": float(boot["point"]),
            "ci_lo": float(boot["ci_lo"]),
            "ci_hi": float(boot["ci_hi"]),
            "p_val": float(sf["p_val"]),
            "p_method": sf["method"],
        }
    return out


def run_study_c_paper() -> dict[str, object]:
    """Reproduce Nov 20 rescore_proper exactly, decompose raw vs LOTO-calibrated RPS/CE/TVD, and diagnose wide CIs."""
    fam_paths = {
        "Codex": (VB04 / "results_exp16_final_robust_r9_median/detail_rows.csv", VB04 / "results_exp28_varaware_codex_avg_newindex/judge_trust_vector.csv"),
        "Claude Opus": (VB04 / "results_exp16_opus47_r3_median/detail_rows.csv", VB04 / "results_exp28_varaware_opus_avg_newindex/judge_trust_vector.csv"),
        "Qwen3-Coder": (VB13 / "results/exp16_qwen_r3_median/detail_rows.csv", VB04 / "results_exp28_varaware_qwen_avg/judge_trust_vector.csv"),
    }
    eth1 = _read_legacy_labels(VB04 / "data/ethan_human_scores_20260425.tsv")
    eth2 = _read_legacy_labels(VB04 / "data/ethan_human_scores_ORIGINAL.tsv")
    vb = [
        _read_legacy_labels(HL_DIR / fn, rename_alias=True)
        for fn in (
            "participant1_data_correct_prompt.tsv",
            "participant2_data_pass_1.tsv",
            "participant3_data_pass_1.tsv",
            "participant4_data_pass_1.tsv",
            "participant5_data_pass_1.tsv",
        )
    ]

    # Step 1: Exact consistency cross-check against archive/51 rescore_proper_results.json
    archived = json.loads(ARCHIVE51_JSON.read_text())
    arch_map = {(r["family"], r["target"], r["alignment"]): r for r in archived}

    max_repro_err = 0.0
    families_out: dict[str, object] = {}
    all_24_loto_summary = []

    for fam, (dp, tp) in fam_paths.items():
        det = _load_paper_detail(dp)
        ti = {r["judge_id"]: float(r["TI_variance_aware"]) for r in csv.DictReader(open(tp))}
        judges = [j for j in ti if j in det]
        items_all = sorted(set().union(*[set(d) for d in det.values()]))

        def build_target(dicts: list[dict], min_n: int):
            out = {}
            for k in items_all:
                vals = [int(round(d[k])) for d in dicts if k in d]
                if len(vals) >= min_n:
                    out[k] = vals
            return out

        t_paper = build_target([eth1, eth2], 2)
        t_vb_all5 = build_target(vb, 5)
        t_vb_avail_arch51 = build_target(vb, 1)  # archive/51 used >=1 available rating (60 items)
        t_vb_avail = build_target(vb, 4)         # exp67 pre-registered >=4 ratings (59 items)

        # Verify exact archive/51 reproduction on raw binned RPS/CE/TVD
        ti_vec = [ti[j] for j in judges]
        for tname, T in (
            ("H_paper_2passes(n_ratings=2, one annotator)", t_paper),
            ("H_vb_5participants(all 5 rated)", t_vb_all5),
            ("H_vb_participants_available(4-5 ratings)", t_vb_avail_arch51),
        ):
            its = sorted(T)
            rlists = [T[k] for k in its]
            rps_v, ce_v, tvd_v, sp_v = [], [], [], []
            for j in judges:
                pm = np.vstack([M.binned_repeats_to_probs(det[j][k][1], alpha=0.5) for k in its])
                ev = M.evaluate_forecast_panel(pm, rlists, judge_05=np.array([5.0 * det[j][k][0] for k in its]))
                rps_v.append(-ev["rps"])
                ce_v.append(-ev["ce"])
                tvd_v.append(-ev["tvd"])
                sp_v.append(ev["spearman"])
            for align_name, arr in (
                ("-mean RPS (Laplace alpha=0.5)", rps_v),
                ("-mean CE (Laplace alpha=0.5)", ce_v),
                ("-mean TVD (Laplace alpha=0.5)", tvd_v),
                ("judge Spearman(score, mean human)", sp_v),
            ):
                ref = arch_map[(fam, tname, align_name)]
                meta = M.meta_association(ti_vec, arr, draws=1000, seed=SEED)
                err = abs(float(meta["spearman"]) - float(ref["rho_TI_vs_alignment"]))
                perr = abs(float(meta["perm_p_two_sided"]) - float(ref["perm_p"]))
                max_repro_err = max(max_repro_err, err, perr)
                if err > 1e-9 or perr > 1e-9:
                    raise RuntimeError(f"Archive 51 repro mismatch {fam} {tname} {align_name}: rho_err={err}, p_err={perr}")

        # Detailed per-judge raw + LOTO calibrated decomposition on H_vb_participants_available (>=4 ratings: 59 items, 20 tasks)
        its_vb = sorted(t_vb_avail)
        tasks_vb = [k[0] for k in its_vb]
        rlists_vb = [t_vb_avail[k] for k in its_vb]
        loro_vb = M.leave_one_rater_out_ceiling(rlists_vb, task_ids=tasks_vb, alpha=0.5, draws=PAPER_BOOT_DRAWS, seed=SEED)

        per_judge_rows = []
        for j in judges:
            raw_pm = np.vstack([M.binned_repeats_to_probs(det[j][k][1], alpha=0.5) for k in its_vb])
            s01 = np.array([det[j][k][0] for k in its_vb], dtype=float)
            raw_ev = _eval_with_ci(raw_pm, rlists_vb, tasks_vb, judge_05=5.0 * s01, draws=PAPER_BOOT_DRAWS, seed=SEED, boot_kendall=False)
            raw_ev.pop("per_item")
            loto_ev = _loto_paper(rlists_vb, s01, tasks_vb)
            row = {
                "family": fam,
                "judge_id": j,
                "TI_var": ti[j],
                "raw": raw_ev,
                "loto": loto_ev,
            }
            per_judge_rows.append(row)
            all_24_loto_summary.append({
                "family": fam,
                "judge_id": j,
                "TI_var": ti[j],
                "raw_rps": raw_ev["rps"]["val"],
                "bias_05": raw_ev["bias_05"]["val"],
                "judge_mean_05": raw_ev["judge_mean_05"]["val"],
                "human_mean_05": raw_ev["human_mean_05"]["val"],
                "icc_a1": raw_ev["icc_a1"]["val"],
                "const_rps": loto_ev["CONST"]["rps"]["val"],
                "ce_fit_rps": loto_ev["CE_fit"]["rps"]["val"],
                "pe_fit_rps": loto_ev["Pearson_fit"]["rps"]["val"],
                "ce_minus_const_ci_hi": loto_ev["diff_CE_minus_CONST_rps"]["ci_hi"],
                "ce_minus_const_p": loto_ev["diff_CE_minus_CONST_rps"]["p_val"],
                "ce_minus_pe_rps": loto_ev["diff_CE_minus_Pearson_fit_rps"]["diff"],
            })

        # TI_var meta-association on raw vs CE-calibrated RPS/CE/TVD and scalar Spearman
        ti_meta = {}
        for key, vals in (
            ("raw_neg_rps", [-r["raw"]["rps"]["val"] for r in per_judge_rows]),
            ("raw_neg_ce", [-r["raw"]["ce"]["val"] for r in per_judge_rows]),
            ("raw_neg_tvd", [-r["raw"]["tvd"]["val"] for r in per_judge_rows]),
            ("raw_spearman", [r["raw"]["spearman"]["val"] for r in per_judge_rows]),
            ("ce_cal_neg_rps", [-r["loto"]["CE_fit"]["rps"]["val"] for r in per_judge_rows]),
            ("ce_cal_neg_ce", [-r["loto"]["CE_fit"]["ce"]["val"] for r in per_judge_rows]),
            ("ce_cal_neg_tvd", [-r["loto"]["CE_fit"]["tvd"]["val"] for r in per_judge_rows]),
            ("pe_cal_neg_rps", [-r["loto"]["Pearson_fit"]["rps"]["val"] for r in per_judge_rows]),
        ):
            m = M.meta_association(ti_vec, vals, draws=BOOT_DRAWS, seed=SEED)
            # Leave-one-judge-out range
            lojo = [M.spearman_corr(ti_vec[:i] + ti_vec[i+1:], vals[:i] + vals[i+1:]) for i in range(len(ti_vec))]
            m["lojo_min"] = float(np.nanmin(lojo))
            m["lojo_max"] = float(np.nanmax(lojo))
            ti_meta[key] = m

        # Headline P8_STRICT_B CI width vs task-subset size k = 4, 8, 12, 16, 20
        headline_id = [j for j in judges if j.endswith("|P8_STRICT_B")][0]
        h_s05 = np.array([5.0 * det[headline_id][k][0] for k in its_vb], dtype=float)
        h_hum05 = np.array([float(np.mean(t_vb_avail[k])) for k in its_vb], dtype=float)
        uniq_tasks = sorted(set(tasks_vb))
        t_idx = {t: [i for i, x in enumerate(tasks_vb) if x == t] for t in uniq_tasks}
        rng = np.random.default_rng(SEED)
        k_curve = []
        for k_sub in (4, 8, 12, 16, 20):
            draws_sp = []
            for _ in range(1000):
                picks = rng.choice(uniq_tasks, size=k_sub, replace=False)
                ii = [i for t in picks for i in t_idx[t]]
                v = M.spearman_corr(h_s05[ii], h_hum05[ii])
                if math.isfinite(v):
                    draws_sp.append(v)
            p025, p50, p975 = np.percentile(draws_sp, [2.5, 50.0, 97.5])
            k_curve.append({
                "k_tasks": k_sub,
                "median": float(p50),
                "p025": float(p025),
                "p975": float(p975),
                "width": float(p975 - p025),
                "width_times_sqrt_k": float((p975 - p025) * math.sqrt(k_sub)),
            })

        families_out[fam] = {
            "loro_ceiling_vb59": loro_vb,
            "per_judge": per_judge_rows,
            "ti_var_meta_vb59": ti_meta,
            "headline_id": headline_id,
            "headline_k_curve_vb59": k_curve,
        }

    # Aggregate 24-series calibration tallies
    n_ce_beats_const_ci = sum(1 for r in all_24_loto_summary if r["ce_minus_const_ci_hi"] < 0.0)
    n_ce_beats_const_pt = sum(1 for r in all_24_loto_summary if r["ce_fit_rps"] < r["const_rps"])
    n_ce_beats_pe_pt = sum(1 for r in all_24_loto_summary if r["ce_minus_pe_rps"] < 0.0)

    return {
        "archive51_max_repro_err": max_repro_err,
        "summary_24_series": {
            "n_series": len(all_24_loto_summary),
            "ce_fit_beats_const_point": n_ce_beats_const_pt,
            "ce_fit_beats_const_ci_upper_lt_0": n_ce_beats_const_ci,
            "ce_fit_beats_pearson_fit_point": n_ce_beats_pe_pt,
            "rows": all_24_loto_summary,
        },
        "families": families_out,
    }


# ===================================================================== Study D: Live VeriBench N=100 Native Ratings
def _parse_sheet_list_from_ttj() -> list[tuple[str, str, str]]:
    readme = (TTJ_EXP09 / "README.md").read_text()
    sheets = []
    for line in readme.splitlines():
        m = re.match(r"^\|\s*`([A-Z]\d+)`\s*\|\s*([^|]+?)\s*\|.*?https://docs\.google\.com/spreadsheets/d/([A-Za-z0-9_-]+)/", line)
        if m:
            sheets.append((m.group(1), m.group(2), m.group(3)))
    m_t30 = re.search(r"`(T30)`\s*([^(*]+)\*?\*?\s*\(.*?https://docs\.google\.com/spreadsheets/d/([A-Za-z0-9_-]+)/", readme)
    if m_t30 and all(s[0] != "T30" for s in sheets):
        sheets.append(("T30", "Max Sieb", m_t30.group(3)))
    return sheets


def _fetch_sheet_csv(item: tuple[str, str, str]) -> dict[str, object]:
    rid, name, sid = item
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            if raw.lstrip().startswith("<!DOCTYPE") or "accounts.google.com" in resp.geturl():
                return {"rater_id": rid, "status": "redirect_login", "rows": [], "item_map": {}}
            rows = list(csv.DictReader(io.StringIO(raw)))
            parsed = []
            item_map = {}
            for r in rows:
                iid = (r.get("item_id") or "").strip()
                tf = (r.get("task_folder") or "").strip()
                cf = (r.get("candidate_file") or "").strip()
                if iid and cf.endswith(".lean"):
                    item_map[iid] = (tf, cf)
                s = (r.get("final_score_0_5") or "").strip()
                if s != "":
                    sf = float(s)
                    si = int(round(sf))
                    if abs(sf - si) > 1e-9 or si < 0 or si > 5:
                        raise ValueError(f"Unexpected non-integer score {s!r} in {rid}")
                    parsed.append({"item_id": iid, "task_folder": tf, "candidate_file": cf, "score": si})
            return {"rater_id": rid, "status": "ok", "n_assigned": len(rows), "rows": parsed, "item_map": item_map}
    except Exception as exc:
        return {"rater_id": rid, "status": f"err:{type(exc).__name__}:{exc}", "rows": [], "item_map": {}}


def run_study_d_live_vb() -> dict[str, object]:
    """Read live Google Sheets via public CSV export (read-only) and save aggregate-only rating + baseline analysis."""
    sheets = _parse_sheet_list_from_ttj()
    ts_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ts_pst = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%m-%d-%Y %H:%M %Z")

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(_fetch_sheet_csv, sheets))

    ok_sheets = [r for r in results if r["status"] == "ok"]
    failed_sheets = [{"rater_id": r["rater_id"], "status": r["status"]} for r in results if r["status"] != "ok"]

    # Map item_id -> task_folder / candidate_file and collect non-A1 ratings in memory (never written to disk)
    per_rater_counts = []
    by_item: dict[str, dict[str, int]] = {}
    item_meta: dict[str, tuple[str, str]] = {}
    score_hist = {str(k): 0 for k in range(6)}

    for r in ok_sheets:
        item_meta.update(r["item_map"])

    for r in ok_sheets:
        rid = r["rater_id"]
        cnt = len(r["rows"])
        if cnt > 0:
            per_rater_counts.append({"rater_id": rid, "n_scored": cnt, "n_assigned": r["n_assigned"]})
        if rid == "A1":
            continue
        for row in r["rows"]:
            iid = row["item_id"]
            if iid not in item_meta:
                item_meta[iid] = (row["task_folder"], row["candidate_file"])
            by_item.setdefault(iid, {})[rid] = row["score"]
            score_hist[str(row["score"])] += 1

    for iid in by_item:
        tf, cf = item_meta[iid]
        if not cf.endswith(".lean"):
            raise RuntimeError(f"Unresolved .lean candidate_file for item {iid}: {(tf, cf)}")

    total_non_a1 = sum(len(v) for v in by_item.values())
    ge1 = [iid for iid, d in by_item.items() if len(d) >= 1]
    ge2 = [iid for iid, d in by_item.items() if len(d) >= 2]
    ge3 = [iid for iid, d in by_item.items() if len(d) >= 3]
    folders_ge1 = sorted({item_meta[i][0] for i in ge1})
    folders_ge2 = sorted({item_meta[i][0] for i in ge2})
    folders_ge3 = sorted({item_meta[i][0] for i in ge3})

    # Pairwise human agreement across raters with >= 10 shared items
    rater_ids_active = sorted({r["rater_id"] for r in per_rater_counts if r["rater_id"] != "A1"})
    pairwise_agreement = []
    for i, r1 in enumerate(rater_ids_active):
        for r2 in rater_ids_active[i + 1:]:
            shared = sorted(iid for iid, d in by_item.items() if r1 in d and r2 in d)
            if len(shared) < 10:
                continue
            v1 = np.array([by_item[iid][r1] for iid in shared], dtype=float)
            v2 = np.array([by_item[iid][r2] for iid in shared], dtype=float)
            shared_tasks = [item_meta[iid][0] for iid in shared]
            sp_boot = M.task_cluster_bootstrap(shared_tasks, lambda ii, a=v1, b=v2: M.spearman_corr(a[ii], b[ii]), draws=BOOT_DRAWS, seed=SEED)
            pairwise_agreement.append({
                "rater_a": r1,
                "rater_b": r2,
                "n_shared_items": len(shared),
                "n_shared_tasks": len(set(shared_tasks)),
                "exact_match": float(np.mean(v1 == v2)),
                "within_1": float(np.mean(np.abs(v1 - v2) <= 1.0)),
                "qwk": M.quadratic_weighted_kappa(v1, v2),
                "mae_05": float(np.mean(np.abs(v1 - v2))),
                "bias_a_minus_b_05": float(np.mean(v1 - v2)),
                "mean_a_05": float(np.mean(v1)),
                "mean_b_05": float(np.mean(v2)),
                "icc_a1": M.icc_two_way(v1, v2, "A"),
                "icc_c1": M.icc_two_way(v1, v2, "C"),
                "spearman": {"val": float(sp_boot["point"]), "ci_lo": float(sp_boot["ci_lo"]), "ci_hi": float(sp_boot["ci_hi"])},
                "kendall": M.kendall_corr(v1, v2),
                "pearson": M.pearson_corr(v1, v2),
            })

    # LORO ceiling on the 100 items with >= 2 non-A1 ratings
    sorted_items = sorted(ge2)
    rlists_n = [[by_item[iid][r] for r in sorted(by_item[iid])] for iid in sorted_items]
    tasks_n = [item_meta[iid][0] for iid in sorted_items]
    loro_n = M.leave_one_rater_out_ceiling(rlists_n, task_ids=tasks_n, alpha=0.5, draws=BOOT_DRAWS, seed=SEED)

    # Judge-free baselines on the 100 items (edit similarity to gold, length ratio, random)
    packet_dir = TTJ_EXP09 / "rating_task_packet/main_rating_task"
    edit_sim_scores = []
    len_ratio_scores = []
    for iid in sorted_items:
        tf, cf = item_meta[iid]
        tdir = packet_dir / tf
        gold_path = tdir / "gold_lean/reference.lean"
        cand_path = tdir / "agent_lean" / Path(cf).name
        if not gold_path.exists() or not cand_path.exists():
            raise RuntimeError(f"Missing gold/candidate in {tdir}: gold={gold_path.exists()}, cand={cand_path.exists()}")
        g_txt = gold_path.read_text(encoding="utf-8", errors="replace")
        c_txt = cand_path.read_text(encoding="utf-8", errors="replace")
        edit_sim_scores.append(difflib.SequenceMatcher(None, g_txt, c_txt).ratio())
        lg, lc = max(1, len(g_txt)), len(c_txt)
        len_ratio_scores.append(min(1.0, lc / float(lg)))

    rng_rand = np.random.default_rng(SEED)
    rand_scores = rng_rand.uniform(0.0, 1.0, size=len(sorted_items))

    def eval_loto_baseline(score_vec: np.ndarray, name: str) -> dict[str, object]:
        t_arr = np.asarray(tasks_n)
        preds = {"CONST": np.zeros((len(sorted_items), 6)), "CE_fit": np.zeros((len(sorted_items), 6))}
        for t in sorted(set(tasks_n)):
            te = np.where(t_arr == t)[0]
            tr = np.where(t_arr != t)[0]
            tr_lists = [rlists_n[i] for i in tr]
            preds["CONST"][te] = M.fit_const(tr_lists, alpha=0.5)(score_vec[te])
            preds["CE_fit"][te] = M.fit_ce_ordinal(score_vec[tr], tr_lists)(score_vec[te])
        res = {"baseline": name}
        raw_ev = _eval_with_ci(
            np.vstack([M.binned_repeats_to_probs([s], alpha=0.5) for s in score_vec]),
            rlists_n,
            tasks_n,
            judge_05=5.0 * score_vec,
            draws=BOOT_DRAWS,
            seed=SEED,
            boot_kendall=False,
        )
        raw_ev.pop("per_item")
        res["raw"] = raw_ev
        for k, pm in preds.items():
            ev = _eval_with_ci(pm, rlists_n, tasks_n, draws=BOOT_DRAWS, seed=SEED, boot_kendall=False)
            ev.pop("per_item")
            res[k] = ev
        return res

    baselines_n = [
        eval_loto_baseline(np.asarray(edit_sim_scores, dtype=float), "gold_candidate_edit_similarity"),
        eval_loto_baseline(np.asarray(len_ratio_scores, dtype=float), "length_ratio_capped"),
        eval_loto_baseline(rand_scores, "seeded_random_uniform"),
    ]

    # Exact SHA-256 overlap check against E64 125-file set-N v7 packet
    p64 = json.loads((CJ_ROOT / "experiments/64_cert_judge_nov6_confirmatory_test_setN_preregistration/results/PROMPTS_MANIFEST.json").read_text())
    e64_shas = {v["candidate_sha256"] for v in p64["items"].values()}
    exp09_shas = {hashlib.sha256(p.read_bytes()).hexdigest() for p in packet_dir.rglob("agent_*.lean")}

    return {
        "fetched_utc": ts_utc,
        "fetched_pst": ts_pst,
        "sheets_total": len(sheets),
        "sheets_read_ok": len(ok_sheets),
        "sheets_failed": failed_sheets,
        "per_rater_nonzero_counts": per_rater_counts,
        "total_non_a1_ratings": total_non_a1,
        "distinct_items_ge1_non_a1": len(ge1),
        "distinct_items_ge2_non_a1": len(ge2),
        "distinct_items_ge3_non_a1": len(ge3),
        "distinct_folders_ge1": len(folders_ge1),
        "distinct_folders_ge2": len(folders_ge2),
        "distinct_folders_ge3": len(folders_ge3),
        "score_histogram_0_5": score_hist,
        "share_score_5": float(score_hist["5"] / float(total_non_a1)) if total_non_a1 else float("nan"),
        "pairwise_human_agreement": pairwise_agreement,
        "loro_ceiling": loro_n,
        "judge_free_baselines_loto": baselines_n,
        "packet_vs_e64": {
            "e64_setN_files": len(e64_shas),
            "exp09_native_files": len(exp09_shas),
            "exact_sha256_overlap": len(e64_shas & exp09_shas),
        },
    }


def cross_check_exp67(study_c: dict, study_d: dict) -> dict[str, object]:
    """Independently cross-verify Experiment 67 outputs left unchecked by its first QA pass."""
    exp67_res = CJ_ROOT / "experiments/67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/results"
    if not exp67_res.exists():
        return {"status": "exp67_not_present"}

    # 1. old_A2_calibrated_loto.csv vs Study C LOTO (heldout level CONST, CE-fit, Pearson-fit)
    a2_rows = list(csv.DictReader(open(exp67_res / "old_A2_calibrated_loto.csv")))
    a2_map = {(r["family"], r["judge"], r["comparison"]): r for r in a2_rows}
    a2_max_err = 0.0
    a2_checked = 0
    for fam, fam_data in study_c["families"].items():
        for pj in fam_data["per_judge"]:
            j = pj["judge_id"]
            for label, key in (("heldout level CONST", "CONST"), ("heldout level CE-fit", "CE_fit"), ("heldout level Pearson-fit", "Pearson_fit")):
                ref = a2_map[(fam, j, label)]
                for csv_col, m_key in (("dRPS", "rps"), ("dCE", "ce"), ("dTVD", "tvd")):
                    err = abs(float(ref[csv_col]) - float(pj["loto"][key][m_key]["val"]))
                    a2_max_err = max(a2_max_err, err)
                    a2_checked += 1

    # 2. old_A5_TI_vs_alignment.csv vs Study C TI_var raw correlations and exact permutation p
    a5_rows = list(csv.DictReader(open(exp67_res / "old_A5_TI_vs_alignment.csv")))
    a5_map = {(r["family"], r["alignment"]): r for r in a5_rows}
    a5_max_rho_err, a5_max_p_err, a5_checked = 0.0, 0.0, 0
    for fam, fam_data in study_c["families"].items():
        for al_name, m_key in (
            ("judge Spearman vs H_vb", "raw_spearman"),
            ("-mean RPS vs H_vb", "raw_neg_rps"),
            ("-mean CE vs H_vb", "raw_neg_ce"),
            ("-mean TVD vs H_vb", "raw_neg_tvd"),
        ):
            ref = a5_map[(fam, al_name)]
            ours = fam_data["ti_var_meta_vb59"][m_key]
            a5_max_rho_err = max(a5_max_rho_err, abs(float(ref["rho_TI"]) - float(ours["spearman"])))
            a5_max_p_err = max(a5_max_p_err, abs(float(ref["perm_p"]) - float(ours["perm_p_two_sided"])))
            a5_checked += 1

    # 3. new_summary.json T05/T08 agreement, QWK, share_5
    ns = json.loads((exp67_res / "new_summary.json").read_text())
    t05_t08 = [p for p in study_d["pairwise_human_agreement"] if p["rater_a"] == "T05" and p["rater_b"] == "T08"][0]
    new_diffs = {
        "t05_t08_spearman_diff": abs(float(ns["agree"]["spearman"]) - float(t05_t08["spearman"]["val"])),
        "t05_t08_qwk_diff": abs(float(ns["agree"]["qwk"]) - float(t05_t08["qwk"])),
        "t05_t08_exact_diff": abs(float(ns["agree"]["exact"]) - float(t05_t08["exact_match"])),
        "t05_t08_within1_diff": abs(float(ns["agree"]["within1"]) - float(t05_t08["within_1"])),
        "share_5_diff": abs(float(ns["agree"]["share_5"]) - round(float(study_d["share_score_5"]), 3)),
        "total_non_a1_exp67_vs_live": (sum(ns["per_rater"].values()), study_d["total_non_a1_ratings"]),
    }

    return {
        "a2_loto_scalar_checks": a2_checked,
        "a2_loto_max_err": a2_max_err,
        "a5_ti_perm_checks": a5_checked,
        "a5_max_rho_err": a5_max_rho_err,
        "a5_max_p_err": a5_max_p_err,
        "new_summary_checks": new_diffs,
    }


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def export_csv_summaries(study_a: dict, study_b: dict, study_c: dict) -> None:
    """Export clean flat CSV tables beside JSON outputs for inspection."""
    a_rows = []
    for tname, tdata in study_a["targets"].items():
        for arm, adata in tdata["arms"].items():
            ens = adata["ensemble"]
            a_rows.append({
                "target": tname,
                "arm": arm,
                "n_seeds": adata["n_seeds"],
                "rps": ens["rps"]["val"],
                "rps_ci_lo": ens["rps"]["ci_lo"],
                "rps_ci_hi": ens["rps"]["ci_hi"],
                "ce": ens["ce"]["val"],
                "tvd": ens["tvd"]["val"],
                "brier": ens["brier"]["val"],
                "mae_05": ens["mae_05"]["val"],
                "bias_05": ens["bias_05"]["val"],
                "judge_mean_05": ens["judge_mean_05"]["val"],
                "human_mean_05": ens["human_mean_05"]["val"],
                "icc_a1": ens["icc_a1"]["val"],
                "icc_c1": ens["icc_c1"]["val"],
                "spearman": ens["spearman"]["val"],
                "spearman_ci_lo": ens["spearman"]["ci_lo"],
                "spearman_ci_hi": ens["spearman"]["ci_hi"],
            })
    _write_csv(RESULTS_DIR / "study_a_e63_summary.csv", a_rows)

    b_units = []
    for u in study_b["units"]:
        m = u["metrics"]
        b_units.append({
            "config": u["config"],
            "family": u["family"],
            "split": u["split"],
            "kind": u["kind"],
            "C_ms_gold": u["indices"].get("C_ms_gold"),
            "TI_var_trainnorm": u["indices"].get("TI_var_trainnorm"),
            "PTI_v0_frozen": u["indices"].get("PTI_v0_frozen"),
            "raw_all5_rps": m.get("raw_all5_rps"),
            "raw_all5_ce": m.get("raw_all5_ce"),
            "raw_all5_tvd": m.get("raw_all5_tvd"),
            "raw_all5_bias_05": m.get("raw_all5_bias_05"),
            "raw_all5_icc_a1": m.get("raw_all5_icc_a1"),
            "raw_all5_spearman": m.get("raw_all5_spearman"),
            "ce_cal_all5_rps": m.get("ce_cal_all5_rps"),
            "ce_cal_all5_ce": m.get("ce_cal_all5_ce"),
            "ce_cal_all5_tvd": m.get("ce_cal_all5_tvd"),
            "ce_cal_all5_icc_a1": m.get("ce_cal_all5_icc_a1"),
            "pe_cal_all5_rps": m.get("pe_cal_all5_rps"),
        })
    _write_csv(RESULTS_DIR / "study_b_e39_units.csv", b_units)

    b_meta = []
    for subset, rows in (("test_llm", study_b["meta_test_llm"]), ("all_llm", study_b["meta_all_llm"])):
        for r in rows:
            ci = r.get("spearman_ci") or [None, None]
            fci = r.get("family_cluster_ci") or [None, None]
            b_meta.append({
                "subset": subset,
                "criterion": r["criterion"],
                "index": r["index"],
                "n_units": r["n_units"],
                "spearman": r.get("spearman"),
                "ci_lo": ci[0],
                "ci_hi": ci[1],
                "kendall": r.get("kendall"),
                "pearson": r.get("pearson"),
                "perm_p_two_sided": r.get("perm_p_two_sided"),
                "perm_p_one_sided_pos": r.get("perm_p_one_sided_pos"),
                "family_cluster_ci_lo": fci[0],
                "family_cluster_ci_hi": fci[1],
                "within_family_perm_p_two_sided": r.get("within_family_perm_p_two_sided"),
            })
    _write_csv(RESULTS_DIR / "study_b_e39_meta.csv", b_meta)
    _write_csv(RESULTS_DIR / "study_c_paper_loto.csv", study_c["summary_24_series"]["rows"])


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    items, by_item = load_items_with_human_labels()

    print("[1/4] Running Study A (E63 native 6-class distributional judges)...")
    study_a = run_study_a_e63(items, by_item)
    (RESULTS_DIR / "study_a_e63_proper_scores.json").write_text(json.dumps(study_a, indent=1))

    print("[2/4] Running Study B (E39 60-unit multi-family panel)...")
    study_b = run_study_b_e39(items)
    (RESULTS_DIR / "study_b_e39_proper_scores.json").write_text(json.dumps(study_b, indent=1))

    print("[3/4] Running Study C (Paper 8-config panels + archive/51 reproduction + LOTO decomposition)...")
    study_c = run_study_c_paper()
    (RESULTS_DIR / "study_c_paper_decomposition.json").write_text(json.dumps(study_c, indent=1))

    print("[4/4] Running Study D (Live VB team N=100 native ratings snapshot + LORO ceiling)...")
    study_d = run_study_d_live_vb()
    (RESULTS_DIR / "study_d_live_vb_ratings_aggregate.json").write_text(json.dumps(study_d, indent=1))

    print("[5/5] Cross-checking Experiment 67 and exporting CSV summaries...")
    exp67_check = cross_check_exp67(study_c, study_d)
    (RESULTS_DIR / "exp67_independent_crosscheck.json").write_text(json.dumps(exp67_check, indent=1))
    export_csv_summaries(study_a, study_b, study_c)

    print("DONE. Key cross-checks:")
    print("  E64 Spearman repro:", study_a["reproduction_check_vs_e64"])
    print("  Archive 51 max err:", study_c["archive51_max_repro_err"])
    print("  Exp 67 cross-check:", exp67_check)
    print("  Live VB sheets:", study_d["sheets_read_ok"], "/", study_d["sheets_total"],
          "non-A1 ratings:", study_d["total_non_a1_ratings"], "ge2 items:", study_d["distinct_items_ge2_non_a1"])


if __name__ == "__main__":
    main()
