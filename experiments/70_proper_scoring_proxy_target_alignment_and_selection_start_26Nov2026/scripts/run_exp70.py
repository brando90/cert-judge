#!/usr/bin/env python3
"""Experiment 70: Live VeriBench ratings verification and proper-scoring proxy-vs-target alignment & selection.

Studies:
  1. Live read-only check of 33 VeriBench team Google Sheets vs trustworthy-theorem-judges Exp 09 (460466d)
     plus anonymized LORO human ceilings and score distributions on R_v1 (75 items) and native_main (100 items).
  2. E39 + E42 (60 configs: 56 LLMs + 4 controls) proper-scoring proxy-vs-target alignment, selection regret,
     Beat-CONST Meta-Brier, and Meta-Corr vs Meta-Proper-RPS zero-leakage head-to-head.
  3. Independent open-weight replication on E60 raw tarballs (26 seed-0 + 36 seed-1 units) and E58 (117 units).
  4. Bridge to live native_main (N=100, 250 ratings) judges/baselines and E63 native 6-class distributional arms.

$0 API / Valkyrie spend. Zero raw rater rows, names, or personal emails are written to disk.
"""
from __future__ import annotations

import concurrent.futures
import csv
import difflib
import hashlib
import io
import json
import math
import os
import sys
import tarfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy import optimize  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
EXP_DIR = SCRIPT_DIR.parent
RESULTS_DIR = EXP_DIR / "results"
FIGURES_DIR = EXP_DIR / "figures"
CJ_ROOT = EXP_DIR.parents[1]
VB_ROOT = CJ_ROOT.parent / "veribench"
TTJ_ROOT = CJ_ROOT.parent / "trustworthy-theorem-judges"
TTJ_EXP09 = TTJ_ROOT / "experiments/09_prepare_packets_and_collect_human_ratings_start_28Sep2026"
TTJ_EXP27 = TTJ_ROOT / "experiments/27_build_a_judge_that_beats_the_constant_forecast_on_held_out_tasks_old_new_ratings_start_24Nov2026"

EXP68_DIR = CJ_ROOT / "experiments/68_proper_scoring_expansion_e39_e63_and_vb_ratings_start_24Nov2026"
E39_DIR = CJ_ROOT / "experiments/39_label_free_proxy_index_train_val_test_over_judge_families"
E42_DIR = CJ_ROOT / "experiments/42_semantic_weakening_overconstraint_vacuity_probes_on_e39_judges"
E58_DIR = CJ_ROOT / "experiments/58_open_weight_judges_on_e39_e42_probes"
E60_DIR = CJ_ROOT / "experiments/60_open_weight_proxy_index_rigor_round"
E62_DIR = CJ_ROOT / "experiments/62_label_free_judge_selection_regret_stage_a"
E63_DIR = CJ_ROOT / "experiments/63_judge_optimization_arms_prompt_sft_rl_qwen3_8b"
E67_DIR = CJ_ROOT / "experiments/67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel"

sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(EXP68_DIR / "scripts"))
sys.path.insert(0, str(E39_DIR / "scripts"))

import metrics as M  # noqa: E402
import proxy_metrics as PM  # noqa: E402
import analysis_lib as E39_LIB  # noqa: E402

ITEMS_JSONL = VB_ROOT / "experiments/100_karpathy_recipe_tc_judge_search_human_train_val_test/inputs/items.jsonl"
ITEMS_SHA256_EXPECTED = "ad9ed552fc2ffac6328e6010bf6be82215dd74f1eddd791622d433126877a96c"

SEED = 69
MIN_CRIT_COV = 0.90
BOOT_DRAWS = 2000


def _write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=1), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def load_rv1_items() -> tuple[list[dict], dict[str, dict]]:
    raw = ITEMS_JSONL.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != ITEMS_SHA256_EXPECTED:
        raise RuntimeError(f"items.jsonl sha256 mismatch: {sha} != {ITEMS_SHA256_EXPECTED}")
    items = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    for it in items:
        it["all5_ratings"] = [int(round(float(it[p]))) for p in ("p1", "p2", "p3", "p4", "p5") if it[p] is not None]
        it["expert3_ratings"] = [int(round(float(it[p]))) for p in ("p1", "p2", "p3") if it[p] is not None]
    return items, {it["item"]: it for it in items}


def _eval_scores_map_on_rv1(
    scores_map: dict[str, list[float]],
    train_items: list[dict],
    heldout_items: list[dict],
) -> dict[str, float | None]:
    """Evaluate a judge's crit scores_map on R_v1 (45 held-out items, calibrated strictly on 30 train items)."""
    ho_elig = [it for it in heldout_items if it["item"] in scores_map]
    tr_elig = [it for it in train_items if it["item"] in scores_map]
    ho_cov = len(ho_elig) / float(len(heldout_items))
    tr_cov = len(tr_elig) / float(len(train_items))
    out: dict[str, float | None] = {"train_cov": round(tr_cov, 4), "heldout_cov": round(ho_cov, 4)}
    if ho_cov + 1e-9 < MIN_CRIT_COV:
        return out

    raw_probs = np.vstack([M.binned_repeats_to_probs(scores_map[it["item"]], alpha=0.5) for it in ho_elig])
    raw_med_05 = np.array([5.0 * float(np.median(scores_map[it["item"]])) for it in ho_elig], dtype=float)
    ho_r_all5 = [it["all5_ratings"] for it in ho_elig]
    ho_r_exp3 = [it["expert3_ratings"] for it in ho_elig]
    ev_raw_5 = M.evaluate_forecast_panel(raw_probs, ho_r_all5, judge_05=raw_med_05)
    ev_raw_3 = M.evaluate_forecast_panel(raw_probs, ho_r_exp3, judge_05=raw_med_05)
    for k, v in ev_raw_5.items():
        out[f"raw_all5_{k}"] = float(v)
    for k, v in ev_raw_3.items():
        out[f"raw_exp3_{k}"] = float(v)

    if tr_cov + 1e-9 >= MIN_CRIT_COV:
        tr_s = np.array([float(np.median(scores_map[it["item"]])) for it in tr_elig], dtype=float)
        ho_s = np.array([float(np.median(scores_map[it["item"]])) for it in ho_elig], dtype=float)
        tr_r_all5 = [it["all5_ratings"] for it in tr_elig]
        tr_r_exp3 = [it["expert3_ratings"] for it in tr_elig]
        ce_5 = M.fit_ce_ordinal(tr_s, tr_r_all5)(ho_s)
        pe_5 = M.fit_pearson_gauss(tr_s, tr_r_all5)(ho_s)
        ce_3 = M.fit_ce_ordinal(tr_s, tr_r_exp3)(ho_s)
        for k, v in M.evaluate_forecast_panel(ce_5, ho_r_all5).items():
            out[f"ce_cal_all5_{k}"] = float(v)
        for k, v in M.evaluate_forecast_panel(pe_5, ho_r_all5).items():
            out[f"pe_cal_all5_{k}"] = float(v)
        for k, v in M.evaluate_forecast_panel(ce_3, ho_r_exp3).items():
            out[f"ce_cal_exp3_{k}"] = float(v)
    return out


# ===================================================================== Study 1: Live Human Ratings Verification
def run_study_1_human_cohorts(rv1_items: list[dict]) -> tuple[dict[str, object], dict[str, dict]]:
    """Verify live public Google Sheets vs local TTJ Exp 09 CSVs and compute aggregate-only cohort stats."""
    man = json.loads((TTJ_EXP09 / "ratings/RAW_MANIFEST.json").read_text())
    main_entries = [e for e in man["files"] if "__native_main_" in e.get("filename", "")]

    ts_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ts_pst = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%m-%d-%Y %H:%M %Z")

    def check_live(entry: dict) -> dict[str, object]:
        rid = entry["rater_id"]
        sid = entry["spreadsheet_id"]
        url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8-sig")
            if raw.lstrip().startswith("<!DOCTYPE"):
                return {"rater_id": rid, "status": "redirect_login", "live_numeric": -1, "manifest_numeric": entry.get("numeric_ratings", 0)}
            rows = list(csv.reader(io.StringIO(raw, newline="")))
            sidx = rows[0].index("final_score_0_5")
            scored = sum(1 for r in rows[1:] if len(r) > sidx and r[sidx].strip() in {"0", "1", "2", "3", "4", "5"})
            return {"rater_id": rid, "status": "ok", "live_numeric": scored, "manifest_numeric": entry.get("numeric_ratings", 0)}
        except Exception as exc:
            return {"rater_id": rid, "status": f"err:{type(exc).__name__}", "live_numeric": -1, "manifest_numeric": entry.get("numeric_ratings", 0)}

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        live_checks = list(ex.map(check_live, main_entries))

    # Optionally check additional non-manifest sheet ID from env/local sibling config without committing IDs/names
    t30_status = "skipped_no_local_id"
    t30_sid = os.environ.get("VERIBENCH_EXTRA_SHEET_ID", "").strip()
    if not t30_sid:
        t30_manifest = TTJ_EXP09 / "ratings/extra_sheet_ids.json"
        if t30_manifest.exists():
            t30_sid = str(json.loads(t30_manifest.read_text()).get("T30", "")).strip()
    if t30_sid:
        try:
            req = urllib.request.Request(f"https://docs.google.com/spreadsheets/d/{t30_sid}/export?format=csv", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                t30_status = f"http_200_len_{len(resp.read())}"
        except Exception as exc:
            t30_status = str(exc)

    # Read local synced Exp 09 CSVs in memory (anonymized aggregates ONLY written out)
    by_item: dict[str, dict[str, int]] = {}
    item_meta: dict[str, tuple[str, str]] = {}
    per_rater_counts: list[dict[str, object]] = []
    hist = {str(k): 0 for k in range(6)}

    for entry in sorted(main_entries, key=lambda e: e["rater_id"]):
        rid = entry["rater_id"]
        csv_path = TTJ_EXP09 / entry["path"]
        raw_bytes = csv_path.read_bytes()
        sha = hashlib.sha256(raw_bytes).hexdigest()
        rows = list(csv.DictReader(io.StringIO(raw_bytes.decode("utf-8"))))
        scored = 0
        for r in rows:
            iid = r["item_id"].strip()
            tf = r["task_folder"].strip()
            cf = r["candidate_file"].strip()
            if cf.endswith(".lean") and iid not in item_meta:
                item_meta[iid] = (tf, cf)
            s = (r.get("final_score_0_5") or "").strip()
            if s in {"0", "1", "2", "3", "4", "5"}:
                scored += 1
                if rid != "A1":
                    val = int(s)
                    by_item.setdefault(iid, {})[rid] = val
                    hist[str(val)] += 1
        if scored > 0 or rid == "A1":
            per_rater_counts.append({
                "rater_id": rid,
                "scored_rows": scored,
                "assigned_rows": len(rows),
                "csv_sha256_prefix": sha[:16],
            })

    # Resolve T06 candidate_file edit via item_meta from complete sheets
    sorted_items = sorted(by_item)
    rlists = [[by_item[iid][r] for r in sorted(by_item[iid])] for iid in sorted_items]
    tasks = [item_meta[iid][0] for iid in sorted_items]

    # Pairwise agreement (anonymized IDs only)
    active_ids = sorted({r["rater_id"] for r in per_rater_counts if r["rater_id"] != "A1" and r["scored_rows"] >= 10})
    pairwise = []
    for i, r1 in enumerate(active_ids):
        for r2 in active_ids[i + 1 :]:
            shared = sorted(iid for iid, d in by_item.items() if r1 in d and r2 in d)
            if len(shared) < 10:
                continue
            v1 = np.array([by_item[iid][r1] for iid in shared], dtype=float)
            v2 = np.array([by_item[iid][r2] for iid in shared], dtype=float)
            stasks = [item_meta[iid][0] for iid in shared]
            sp_b = M.task_cluster_bootstrap(stasks, lambda ii, a=v1, b=v2: M.spearman_corr(a[ii], b[ii]), draws=BOOT_DRAWS, seed=SEED)
            pairwise.append({
                "rater_a": r1,
                "rater_b": r2,
                "n_items": len(shared),
                "n_tasks": len(set(stasks)),
                "exact_match": float(np.mean(v1 == v2)),
                "within_1": float(np.mean(np.abs(v1 - v2) <= 1.0)),
                "qwk": M.quadratic_weighted_kappa(v1, v2),
                "mae_05": float(np.mean(np.abs(v1 - v2))),
                "bias_a_minus_b": float(np.mean(v1 - v2)),
                "icc_a1": M.icc_two_way(v1, v2, "A"),
                "spearman": float(sp_b["point"]),
                "spearman_ci": [float(sp_b["ci_lo"]), float(sp_b["ci_hi"])],
                "pearson": M.pearson_corr(v1, v2),
            })

    loro_native = M.leave_one_rater_out_ceiling(rlists, task_ids=tasks, alpha=0.5, draws=BOOT_DRAWS, seed=SEED)

    # LOTO constant baseline on native_main
    t_arr = np.asarray(tasks)
    const_preds = np.zeros((len(sorted_items), 6), dtype=float)
    for t in sorted(set(tasks)):
        te = np.where(t_arr == t)[0]
        tr = np.where(t_arr != t)[0]
        const_preds[te] = M.fit_const([rlists[i] for i in tr], alpha=0.5)(np.zeros(len(te)))
    const_losses = M.per_item_losses(const_preds, rlists)
    const_boot = M.task_cluster_bootstrap(
        tasks,
        lambda ii: np.array([
            float(np.mean(const_losses["rps"][ii])),
            float(np.mean(const_losses["ce"][ii])),
            float(np.mean(const_losses["tvd"][ii])),
            float(np.mean(const_losses["brier"][ii])),
            float(np.mean(const_losses["hum_mean_05"][ii])),
        ]),
        draws=BOOT_DRAWS,
        seed=SEED,
    )

    # R_v1 cohort summary (75 items / 25 tasks)
    rv1_hist = {str(k): 0 for k in range(6)}
    for it in rv1_items:
        for v in it["all5_ratings"]:
            rv1_hist[str(v)] += 1
    rv1_loro = M.leave_one_rater_out_ceiling(
        [it["all5_ratings"] for it in rv1_items],
        task_ids=[it["task"] for it in rv1_items],
        alpha=0.5,
        draws=BOOT_DRAWS,
        seed=SEED,
    )

    summary = {
        "checked_utc": ts_utc,
        "checked_pst": ts_pst,
        "ttj_manifest_recorded_utc": man.get("recorded_utc"),
        "sheets_checked_public_csv": len([c for c in live_checks if c["status"] == "ok"]),
        "sheets_total_in_manifest": len(main_entries),
        "live_vs_manifest_changed": [c for c in live_checks if c["status"] != "ok" or c["live_numeric"] != c["manifest_numeric"]],
        "t30_status": t30_status,
        "native_main": {
            "n_items": len(sorted_items),
            "n_tasks": len(set(tasks)),
            "total_non_a1_ratings": sum(len(v) for v in by_item.values()),
            "ge2_ratings_items": sum(1 for v in by_item.values() if len(v) >= 2),
            "ge3_ratings_items": sum(1 for v in by_item.values() if len(v) >= 3),
            "per_rater_counts": per_rater_counts,
            "score_histogram_0_5": hist,
            "share_score_5": float(hist["5"] / max(1, sum(hist.values()))),
            "pairwise_agreement": pairwise,
            "loro_ceiling": loro_native,
            "const_loto": {
                "rps": {"val": float(const_boot["point"][0]), "ci": [float(const_boot["ci_lo"][0]), float(const_boot["ci_hi"][0])]},
                "ce": {"val": float(const_boot["point"][1]), "ci": [float(const_boot["ci_lo"][1]), float(const_boot["ci_hi"][1])]},
                "tvd": {"val": float(const_boot["point"][2]), "ci": [float(const_boot["ci_lo"][2]), float(const_boot["ci_hi"][2])]},
                "brier": {"val": float(const_boot["point"][3]), "ci": [float(const_boot["ci_lo"][3]), float(const_boot["ci_hi"][3])]},
                "human_mean_05": {"val": float(const_boot["point"][4]), "ci": [float(const_boot["ci_lo"][4]), float(const_boot["ci_hi"][4])]},
            },
        },
        "rv1_cohort": {
            "n_items": len(rv1_items),
            "n_tasks": len({it["task"] for it in rv1_items}),
            "total_ratings_all5": sum(len(it["all5_ratings"]) for it in rv1_items),
            "score_histogram_0_5": rv1_hist,
            "share_score_5": float(rv1_hist["5"] / max(1, sum(rv1_hist.values()))),
            "loro_ceiling_all5": rv1_loro,
        },
    }
    in_memory_native = {
        "sorted_items": sorted_items,
        "item_meta": item_meta,
        "by_item": by_item,
        "rlists": rlists,
        "tasks": tasks,
        "const_loto_rps": float(const_boot["point"][0]),
    }
    return summary, in_memory_native


# ===================================================================== Study 2: E39 + E42 Proxy-vs-Target & Selection
def _fit_trainval_meta_combiner(
    trainval_rows: list[dict],
    feature_keys: list[str],
    target_key: str,
    lower_is_better: bool = True,
) -> tuple[dict[str, float], callable]:
    """Fit a non-negative ridge linear meta-combiner strictly on train+val judge units."""
    elig = [
        r for r in trainval_rows
        if all(r["proxies"].get(k) is not None for k in feature_keys) and r["targets"].get(target_key) is not None
    ]
    X_raw = np.array([[float(r["proxies"][k]) for k in feature_keys] for r in elig], dtype=float)
    y = np.array([float(r["targets"][target_key]) for r in elig], dtype=float)
    if lower_is_better:
        y = -y  # higher score = better judge
    mu = X_raw.mean(axis=0)
    sd = X_raw.std(axis=0)
    sd = np.where(sd > 1e-9, sd, 1.0)
    Xz = (X_raw - mu) / sd
    yc = y - y.mean()

    def loss(w: np.ndarray) -> float:
        pred = Xz @ w
        return float(np.mean((pred - yc) ** 2) + 0.05 * np.sum(w * w))

    bounds = [(0.0, None) for _ in feature_keys]
    opt = optimize.minimize(loss, np.full(len(feature_keys), 1.0 / len(feature_keys)), bounds=bounds, method="L-BFGS-B")
    w = opt.x
    if float(np.sum(w)) > 0.0:
        w = w / float(np.sum(w))
    weights = {k: float(w[i]) for i, k in enumerate(feature_keys)}

    def predict(row: dict) -> float | None:
        if any(row["proxies"].get(k) is None for k in feature_keys):
            return None
        x = np.array([float(row["proxies"][k]) for k in feature_keys], dtype=float)
        return float(np.dot((x - mu) / sd, w))

    return weights, predict


def run_study_2_e39_e42(rv1_items: list[dict]) -> dict[str, object]:
    """Full proper-scoring proxy-vs-target alignment, regret, and Meta-Corr vs Meta-Proper-RPS head-to-head."""
    e39_res = E39_DIR / "results"
    e42_res = E42_DIR / "results"
    m39 = json.loads((e39_res / "probe_manifest.json").read_text())["rows"]
    m42 = json.loads((e42_res / "semantic_probe_manifest.json").read_text())["rows"]
    strict_probe_ids: set[str] = set()
    audit_dir = E42_DIR / "probe_edits/audit"
    if audit_dir.exists():
        for ap in sorted(audit_dir.glob("*.json")):
            ad = json.loads(ap.read_text())
            for pid, info in (ad.get("labels") or {}).items():
                if info.get("label") == "strict":
                    strict_probe_ids.add(str(pid))
    screen42 = json.loads((e42_res / "semantic_screen.json").read_text())["units"]
    screen42_map = {u["config"]: u for u in screen42} if isinstance(screen42, list) else screen42

    u_tv = json.loads((e39_res / "units_train_val.json").read_text())["units"]
    u_te = json.loads((e39_res / "units_test.json").read_text())["units"]
    all_units = u_tv + u_te

    h39_map = {}
    for p in sorted((e39_res / "harvest").glob("*.json")):
        d = json.loads(p.read_text())
        h39_map[d["config"]] = d
    h42_map = {}
    for p in sorted((e42_res / "harvest").glob("*.json")):
        d = json.loads(p.read_text())
        h42_map[d["config"]] = d

    train_items = sorted([it for it in rv1_items if it["split"] == "train"], key=lambda r: r["item"])
    heldout_items = sorted([it for it in rv1_items if it["split"] in ("val", "test")], key=lambda r: r["item"])

    const_train_all5 = M.evaluate_forecast_panel(
        M.fit_const([it["all5_ratings"] for it in train_items])(np.zeros(len(heldout_items))),
        [it["all5_ratings"] for it in heldout_items],
    )
    const_rps_all5 = float(const_train_all5["rps"])

    # Cross-check parity against Exp 68 study_b_e39_proper_scores.json
    e68_b = json.loads((EXP68_DIR / "results/study_b_e39_proper_scores.json").read_text())
    e68_unit_map = {u["config"]: u for u in e68_b["units"]}
    max_e68_diff = 0.0

    unit_rows: list[dict] = []
    for u in all_units:
        cfg = u["config"]
        d39 = h39_map[cfg]
        d42 = h42_map[cfg]
        scores_map: dict[str, list[float]] = {}
        for c in d39["cells"]:
            if c["kind"] == "crit" and c["status"] in ("measured", "deterministic") and c.get("score") is not None:
                scores_map.setdefault(c["item"], []).append(float(c["score"]))

        targets = _eval_scores_map_on_rv1(scores_map, train_items, heldout_items)
        # Verify exact parity with Exp 68
        ref_m = e68_unit_map[cfg]["metrics"]
        for mk in ("raw_all5_rps", "raw_all5_ce", "ce_cal_all5_rps", "ce_cal_all5_ce", "raw_all5_icc_a1", "raw_exp3_spearman"):
            if mk in targets and mk in ref_m and targets[mk] is not None and ref_m[mk] is not None:
                max_e68_diff = max(max_e68_diff, abs(float(targets[mk]) - float(ref_m[mk])))

        p39 = PM.compute_e39_probe_proxies(d39["cells"], m39)
        p42 = PM.compute_e42_probe_proxies(d42["cells"], m42, strict_probe_ids=strict_probe_ids or None)
        s42_u = screen42_map[cfg]
        s42_m = s42_u["metrics"]

        c_ms_gold = u["indices"].get("C_ms_gold")
        p_e42_fb = p42["P_e42_fullcov_brier"]
        p_e42_sb = p42["P_e42_strict_brier"]
        p_e39_fb = p39["P_e39_fullcov_brier"]
        p_dsti = 0.5 * (float(p_e39_fb) + float(p_e42_fb)) if (p_e39_fb is not None and p_e42_fb is not None) else None
        p_dsti_gated = (float(p_e42_fb) * max(0.0, float(c_ms_gold))) if (p_e42_fb is not None and c_ms_gold is not None) else None

        proxies = {
            "TI_var_trainnorm": u["indices"].get("TI_var_trainnorm"),
            "PTI_v0_frozen": u["indices"].get("PTI_v0_frozen"),
            "C_ms_gold": c_ms_gold,
            "C_bm_gold": u["indices"].get("C_bm_gold"),
            "C_ident": u["indices"].get("C_ident"),
            "S_e42": s42_u.get("semantic_component_S"),
            "P_e42_disc": s42_m.get("discrimination"),
            "P_e39_fullcov_brier": p_e39_fb,
            "P_e39_fullcov_ce": p39["P_e39_fullcov_ce"],
            "P_e39_probe_rps": p39["P_e39_probe_rps"],
            "P_e39_curve_rps": p39["P_e39_curve_rps"],
            "P_e39_ms_margin": p39["P_e39_ms_margin"],
            "P_e42_fullcov_brier": p_e42_fb,
            "P_e42_strict_brier": p_e42_sb,
            "P_e42_fullcov_ce": p42["P_e42_fullcov_ce"],
            "P_e42_score_brier": p42["P_e42_score_brier"],
            "P_e42_probe_rps": p42["P_e42_probe_rps"],
            "P_dsti_proper": p_dsti,
            "P_dsti_gated": p_dsti_gated,
            "e42_brier_weak": p42["e42_brier_weak"],
            "e42_brier_overc": p42["e42_brier_overc"],
            "e42_brier_fmt": p42["e42_brier_fmt"],
        }
        prompt_name = cfg.split("|", 1)[1] if "|" in cfg else ""
        is_rubric = u["kind"] == "llm" and prompt_name in ("D0", "H0", "H1", "H2", "R4")
        unit_rows.append({
            "config": cfg,
            "family": u["family"],
            "split": u["split"],
            "kind": u["kind"],
            "harness": u["harness"],
            "is_rubric": is_rubric,
            "proxies": proxies,
            "targets": targets,
        })

    if max_e68_diff > 1e-10:
        raise RuntimeError(f"Parity failure against Exp 68 study_b: max_diff={max_e68_diff}")

    # Fit train+val non-negative meta-combiner on LLM units only (zero test leakage)
    tv_llm = [r for r in unit_rows if r["split"] in ("train", "val") and r["kind"] == "llm"]
    comb_feats = ["P_e39_fullcov_brier", "P_e42_fullcov_brier", "C_ms_gold", "P_e39_ms_margin"]
    comb_w_cal, comb_fn_cal = _fit_trainval_meta_combiner(tv_llm, comb_feats, "ce_cal_all5_rps", lower_is_better=True)
    comb_w_raw, comb_fn_raw = _fit_trainval_meta_combiner(tv_llm, comb_feats, "raw_all5_rps", lower_is_better=True)
    for r in unit_rows:
        r["proxies"]["P_meta_comb_cecal"] = comb_fn_cal(r)
        r["proxies"]["P_meta_comb_raw"] = comb_fn_raw(r)

    proxy_list = [
        "TI_var_trainnorm",
        "PTI_v0_frozen",
        "C_ms_gold",
        "C_bm_gold",
        "C_ident",
        "S_e42",
        "P_e42_disc",
        "P_e39_fullcov_brier",
        "P_e39_probe_rps",
        "P_e39_curve_rps",
        "P_e39_ms_margin",
        "P_e42_fullcov_brier",
        "P_e42_strict_brier",
        "P_e42_fullcov_ce",
        "P_e42_score_brier",
        "P_e42_probe_rps",
        "P_dsti_proper",
        "P_dsti_gated",
        "P_meta_comb_cecal",
        "P_meta_comb_raw",
    ]

    subsets = {
        "test_llm": [r for r in unit_rows if r["split"] == "test" and r["kind"] == "llm"],
        "test_llm_plus_ctrl": [r for r in unit_rows if r["split"] == "test" or r["kind"] != "llm"],
        "all_llm": [r for r in unit_rows if r["kind"] == "llm"],
        "all_plus_ctrl": unit_rows,
        "rubric_only_all": [r for r in unit_rows if r["is_rubric"]],
        "rubric_only_test": [r for r in unit_rows if r["is_rubric"] and r["split"] == "test"],
        # n=16 non-PTI_v0 common support (controls/PTI_v0 excluded so remaining proxies share identical pool & oracle)
        "common_support_test_llm": [
            r for r in unit_rows
            if r["split"] == "test" and r["kind"] == "llm" and r["proxies"].get("C_ms_gold") is not None
        ],
    }

    target_specs = [
        ("ce_cal_all5_rps", const_rps_all5, True),
        ("raw_all5_rps", const_rps_all5, True),
        ("ce_cal_all5_ce", float(const_train_all5["ce"]), True),
        ("ce_cal_all5_tvd", float(const_train_all5["tvd"]), True),
        ("raw_all5_brier", float(const_train_all5["brier"]), True),
        ("raw_all5_icc_a1", 0.0, False),
        ("raw_all5_spearman", 0.0, False),
    ]

    meta_results: dict[str, dict[str, list[dict]]] = {}
    for sname, srows in subsets.items():
        meta_results[sname] = {}
        for tkey, c_thr, lib in target_specs:
            # For Meta-Brier/Meta-RMSE in test_llm / test_llm_plus_ctrl, pass full train+val + test rows
            # while keeping Top-1 / Subpool / UWA / Spearman strictly on srows
            rows_for_eval = srows
            evals = []
            for pk in proxy_list:
                ev = PM.evaluate_proxy_against_target(
                    rows_for_eval, pk, tkey, const_threshold=c_thr, lower_is_better=lib, draws=BOOT_DRAWS, seed=SEED
                )
                # Fit held-out Beat-CONST Meta-Brier & Meta-RMSE strictly on train+val LLMs only (zero test/control leakage)
                if sname in ("test_llm", "test_llm_plus_ctrl", "common_support_test_llm") and ev.get("computable"):
                    tv_src = [r for r in unit_rows if r["split"] in ("train", "val") and r["kind"] == "llm"]
                    tr_elig = [r for r in tv_src if r["proxies"].get(pk) is not None and r["targets"].get(tkey) is not None]
                    te_elig = [r for r in srows if r["proxies"].get(pk) is not None and r["targets"].get(tkey) is not None]
                    if len(tr_elig) >= 5 and len(te_elig) >= 3:
                        tr_x = [float(r["proxies"][pk]) for r in tr_elig]
                        te_x = [float(r["proxies"][pk]) for r in te_elig]
                        tr_y = [float(r["targets"][tkey]) for r in tr_elig]
                        te_y = [float(r["targets"][tkey]) for r in te_elig]
                        tr_b = [1 if (v < c_thr if lib else v > c_thr) else 0 for v in tr_y]
                        te_b = [1 if (v < c_thr if lib else v > c_thr) else 0 for v in te_y]
                        ev["beat_const_meta_pred"] = PM.meta_binary_proper_eval(tr_x, tr_b, te_x, te_b)
                        cb = (0.0, 1.0) if "rps" in tkey or "tvd" in tkey else ((-1.0, 1.0) if not lib else (0.0, 10.0))
                        ev["risk_meta_pred"] = PM.meta_continuous_risk_eval(tr_x, tr_y, te_x, te_y, clip_bounds=cb)
                evals.append(ev)
            meta_results[sname][tkey] = evals

    # Locked Meta-Selection Head-to-Head (Arm A: Meta-Corr vs Arm B: Meta-Proper-RPS)
    # Candidate pool excludes meta-combiners (single frozen proxies only)
    single_candidates = [p for p in proxy_list if not p.startswith("P_meta_comb")]
    tv_llm_pool = [r for r in unit_rows if r["split"] in ("train", "val") and r["kind"] == "llm"]
    tv_all_pool = [r for r in unit_rows if r["split"] in ("train", "val")]
    tv_pools = {
        "llm_selected_zero_overlap": (tv_llm_pool, False),
        "trainval_with_ctrl_selected": (tv_all_pool, True),
    }
    head_to_head = {}
    for pool_name, (tv_sub, has_ctrl_overlap) in tv_pools.items():
        # Arm A: pick proxy maximizing Spearman(P, raw_exp3_spearman) on train+val
        arm_a_scores = []
        for pk in single_candidates:
            ev_sp = PM.evaluate_proxy_against_target(tv_sub, pk, "raw_exp3_spearman", lower_is_better=False, draws=1000, seed=SEED)
            if ev_sp.get("computable") and ev_sp["rank_meta"].get("spearman") is not None and math.isfinite(ev_sp["rank_meta"]["spearman"]):
                arm_a_scores.append((float(ev_sp["rank_meta"]["spearman"]), pk))
        arm_a_scores.sort(reverse=True)
        pick_a = arm_a_scores[0][1]

        # Arm B: pick proxy minimizing expected subpool_10 regret on ce_cal_all5_rps on train+val
        arm_b_scores = []
        for pk in single_candidates:
            ev_rps = PM.evaluate_proxy_against_target(tv_sub, pk, "ce_cal_all5_rps", const_threshold=const_rps_all5, lower_is_better=True, draws=1000, seed=SEED)
            if ev_rps.get("computable") and ev_rps["subpool_10"].get("computed"):
                arm_b_scores.append((float(ev_rps["subpool_10"]["mean_regret"]), pk))
        arm_b_scores.sort()
        pick_b = arm_b_scores[0][1]

        # Arm B_raw: pick proxy minimizing expected subpool_10 regret on raw_all5_rps on train+val
        arm_b_raw_scores = []
        for pk in single_candidates:
            ev_raw = PM.evaluate_proxy_against_target(tv_sub, pk, "raw_all5_rps", const_threshold=const_rps_all5, lower_is_better=True, draws=1000, seed=SEED)
            if ev_raw.get("computable") and ev_raw["subpool_10"].get("computed"):
                arm_b_raw_scores.append((float(ev_raw["subpool_10"]["mean_regret"]), pk))
        arm_b_raw_scores.sort()
        pick_b_raw = arm_b_raw_scores[0][1]

        te_llm = subsets["test_llm"]
        te_plus = subsets["test_llm_plus_ctrl"]
        head_to_head[pool_name] = {
            "controls_overlap_trainval_and_stress_pool": has_ctrl_overlap,
            "arm_a_meta_corr_pick": pick_a,
            "arm_a_trainval_top3": arm_a_scores[:3],
            "arm_b_meta_proper_cecal_pick": pick_b,
            "arm_b_trainval_top3": arm_b_scores[:3],
            "arm_b_meta_proper_raw_pick": pick_b_raw,
            "arm_b_raw_trainval_top3": arm_b_raw_scores[:3],
            "test_llm_arm_a_on_cecal_rps": PM.evaluate_proxy_against_target(te_llm, pick_a, "ce_cal_all5_rps", const_threshold=const_rps_all5, lower_is_better=True, draws=BOOT_DRAWS, seed=SEED),
            "test_llm_arm_b_on_cecal_rps": PM.evaluate_proxy_against_target(te_llm, pick_b, "ce_cal_all5_rps", const_threshold=const_rps_all5, lower_is_better=True, draws=BOOT_DRAWS, seed=SEED),
            "test_llm_plus_ctrl_arm_a_on_cecal_rps": PM.evaluate_proxy_against_target(te_plus, pick_a, "ce_cal_all5_rps", const_threshold=const_rps_all5, lower_is_better=True, draws=BOOT_DRAWS, seed=SEED),
            "test_llm_plus_ctrl_arm_b_on_cecal_rps": PM.evaluate_proxy_against_target(te_plus, pick_b, "ce_cal_all5_rps", const_threshold=const_rps_all5, lower_is_better=True, draws=BOOT_DRAWS, seed=SEED),
            "test_llm_arm_a_on_raw_rps": PM.evaluate_proxy_against_target(te_llm, pick_a, "raw_all5_rps", const_threshold=const_rps_all5, lower_is_better=True, draws=BOOT_DRAWS, seed=SEED),
            "test_llm_arm_b_raw_on_raw_rps": PM.evaluate_proxy_against_target(te_llm, pick_b_raw, "raw_all5_rps", const_threshold=const_rps_all5, lower_is_better=True, draws=BOOT_DRAWS, seed=SEED),
        }

    return {
        "parity_max_diff_vs_exp68": max_e68_diff,
        "const_train_baseline_heldout_all5": const_train_all5,
        "meta_combiner_weights": {"ce_cal": comb_w_cal, "raw": comb_w_raw},
        "unit_rows": unit_rows,
        "meta_results": meta_results,
        "head_to_head": head_to_head,
    }


# ===================================================================== Study 3: E60 Open-Weight Replication & E58 Cross-Check
def run_study_3_e60_e58(rv1_items: list[dict]) -> dict[str, object]:
    """Stream E60 tarballs in memory to compute full proper scores & E39 behavioral proxies, plus cross-check E58."""
    e39_res = E39_DIR / "results"
    m39_dict = json.loads((e39_res / "probe_manifest.json").read_text())
    m39_rows = m39_dict["rows"]
    probes_e39 = E39_LIB.valid_probes(m39_dict)
    ti_norm = json.loads((e39_res / "units_train_val.json").read_text())["meta"]["ti_var_norm"]

    train_items = sorted([it for it in rv1_items if it["split"] == "train"], key=lambda r: r["item"])
    heldout_items = sorted([it for it in rv1_items if it["split"] in ("val", "test")], key=lambda r: r["item"])
    const_rps_all5 = float(
        M.evaluate_forecast_panel(
            M.fit_const([it["all5_ratings"] for it in train_items])(np.zeros(len(heldout_items))),
            [it["all5_ratings"] for it in heldout_items],
        )["rps"]
    )

    # E62 cached reference for verification
    u90_map = {u["config"]: u for u in json.loads((E62_DIR / "results/units_90.json").read_text())}

    def load_tarball_units(tgz_path: Path, tag: str) -> list[dict]:
        rows = []
        with tarfile.open(tgz_path, "r:gz") as tf:
            for member in sorted(tf.getmembers(), key=lambda m: m.name):
                if not member.isfile() or not member.name.endswith(".json"):
                    continue
                d = json.loads(tf.extractfile(member).read().decode("utf-8"))
                cfg = d["config"]
                sc = E39_LIB.Scores(d)
                comps = E39_LIB.components(sc, probes_e39)
                pti = E39_LIB.pti_v0_frozen(sc, probes_e39)
                tir = E39_LIB.ti_var_raw(sc, probes_e39)
                frozen = {
                    "PTI_v0_frozen": pti["value"],
                    "TI_var_trainnorm": None if tir is None else E39_LIB.ti_var(tir, ti_norm),
                }
                c_ms = E39_LIB.candidate_value("C_ms_gold", comps, frozen)
                c_bm = E39_LIB.candidate_value("C_bm_gold", comps, frozen)
                p39 = PM.compute_e39_probe_proxies(d["cells"], m39_rows)

                crit_map: dict[str, list[float]] = {}
                for c in d["cells"]:
                    if c["kind"] == "crit" and c["status"] in ("measured", "deterministic") and c.get("score") is not None:
                        crit_map.setdefault(c["item"], []).append(float(c["score"]))
                targets = _eval_scores_map_on_rv1(crit_map, train_items, heldout_items)

                rows.append({
                    "config": cfg,
                    "family": d["family"],
                    "split": "e60_" + tag,
                    "kind": d["kind"],
                    "proxies": {
                        "C_ms_gold": c_ms,
                        "C_bm_gold": c_bm,
                        "C_ident": E39_LIB.candidate_value("C_ident", comps, frozen),
                        "TI_var_trainnorm": frozen["TI_var_trainnorm"],
                        "PTI_v0_frozen": frozen["PTI_v0_frozen"],
                        **p39,
                    },
                    "targets": targets,
                })
        return rows

    harv_dir = E60_DIR / "results/final_2026-10-25/harvest"
    seed0_rows = load_tarball_units(harv_dir / "e60_harv0.tgz", "seed0")
    seed1_rows = load_tarball_units(harv_dir / "e60_harv1.tgz", "seed1")

    # Verify seed0 parity against E62 units_90.json
    max_e62_cms_diff = 0.0
    max_e62_crit_diff = 0.0
    for r in seed0_rows:
        ref = u90_map.get(r["config"])
        if ref:
            if r["proxies"].get("C_ms_gold") is not None and ref.get("C_ms_gold") is not None:
                max_e62_cms_diff = max(max_e62_cms_diff, abs(float(r["proxies"]["C_ms_gold"]) - float(ref["C_ms_gold"])))
            if r["targets"].get("raw_exp3_spearman") is not None and ref.get("criterion") is not None:
                max_e62_crit_diff = max(max_e62_crit_diff, abs(float(r["targets"]["raw_exp3_spearman"]) - float(ref["criterion"])))

    e39_proxies = [
        "TI_var_trainnorm", "PTI_v0_frozen", "C_ms_gold", "C_bm_gold", "C_ident",
        "P_e39_fullcov_brier", "P_e39_fullcov_ce", "P_e39_probe_rps", "P_e39_curve_rps", "P_e39_ms_margin",
    ]
    e60_meta = {}
    for cohort_name, crows in (("e60_seed0_26", seed0_rows), ("e60_seed1_36", seed1_rows)):
        e60_meta[cohort_name] = {}
        for tkey, lib in (("ce_cal_all5_rps", True), ("raw_all5_rps", True), ("raw_all5_icc_a1", False), ("raw_exp3_spearman", False)):
            e60_meta[cohort_name][tkey] = [
                PM.evaluate_proxy_against_target(crows, pk, tkey, const_threshold=const_rps_all5 if "rps" in tkey else 0.0, lower_is_better=lib, draws=BOOT_DRAWS, seed=SEED)
                for pk in e39_proxies
            ]

    # Seed-0 vs Seed-1 proxy stability (comparing E60 ANALYSIS partD seed0 vs seed1 for C_ms_gold, and reporting seed1 proper scores)
    a60_partd = json.loads((E60_DIR / "results/final_2026-10-25/ANALYSIS.json").read_text())["partD"]
    cms_diffs = [
        abs(float(v["C_ms_gold_seed0"]) - float(v["C_ms_gold_seed1"]))
        for v in a60_partd.values()
        if v.get("C_ms_gold_seed0") is not None and v.get("C_ms_gold_seed1") is not None
    ]

    # E58 117-unit open-weight cross-check (E39 + E42 behavioral scores vs Spearman criterion)
    a58 = json.loads((E58_DIR / "results/full_13_judges_2026-10-30/ANALYSIS.json").read_text())
    e58_e42_map = {u["config"]: u for u in a58["e42"]["units"]}
    e58_rows = []
    for u in a58["units"]:
        cfg = u["config"]
        ho = (u["criteria"].get("heldout") or {})
        sp = ho.get("spearman")
        e42_u = e58_e42_map.get(cfg, {})
        e42_m = e42_u.get("metrics", {})
        e58_rows.append({
            "config": cfg,
            "family": u["model_key"],
            "proxies": {
                "C_ms_gold": u["indices"].get("C_ms_gold"),
                "TI_var_trainnorm": u["indices"].get("TI_var_trainnorm"),
                "PTI_v0_frozen": u["indices"].get("PTI_v0_frozen"),
                "S_e42": e42_u.get("semantic_component_S"),
                "P_e42_disc": e42_m.get("discrimination"),
                "e42_weakening": (e42_m.get("weakening") or {}).get("value"),
            },
            "targets": {"raw_exp3_spearman": sp},
        })
    e58_meta = [
        PM.evaluate_proxy_against_target(e58_rows, pk, "raw_exp3_spearman", lower_is_better=False, draws=BOOT_DRAWS, seed=SEED)
        for pk in ("C_ms_gold", "TI_var_trainnorm", "PTI_v0_frozen", "S_e42", "P_e42_disc", "e42_weakening")
    ]

    return {
        "e62_parity_check": {"max_c_ms_gold_diff": max_e62_cms_diff, "max_criterion_spearman_diff": max_e62_crit_diff},
        "e60_seed0_units": seed0_rows,
        "e60_seed1_units": seed1_rows,
        "e60_meta": e60_meta,
        "e60_seed0_vs_seed1_c_ms_gold_diffs": {"n": len(cms_diffs), "mean_abs_diff": float(np.mean(cms_diffs)), "max_abs_diff": float(np.max(cms_diffs))},
        "e58_117_meta_vs_spearman": e58_meta,
    }


# ===================================================================== Study 4: native_main (N=100) Bridge & E63 Check
def run_study_4_native_bridge(native_mem: dict, study2_rows: list[dict], rv1_items: list[dict]) -> dict[str, object]:
    """Evaluate cached H2/H3 judges and judge-free baselines on 11-26-2026 native_main (100 items), link to E39/E42 proxies, and verify E63."""
    sorted_items = native_mem["sorted_items"]
    item_meta = native_mem["item_meta"]
    rlists = native_mem["rlists"]
    tasks = native_mem["tasks"]
    t_arr = np.asarray(tasks)

    # Map native item_id -> Exp 27 judge scores
    h2_scores: dict[str, dict[str, list[float]]] = {}
    for r in csv.DictReader(open(TTJ_EXP27 / "data_11-24-2026/judge_scores_h2_11-24-2026.csv")):
        if r["set"] == "new":
            h2_scores.setdefault(r["judge"], {}).setdefault(r["item"], []).append(float(r["score_0to5"]) / 5.0)

    # Load H3 features (both trainval and test) across all 100 new items
    h3_probs: dict[str, np.ndarray] = {}
    h3_scores_01: dict[str, float] = {}
    for rel in ("results/h3_features_trainval_11-24-2026.csv", "results/h3_features_test_11-24-2026.csv"):
        for r in csv.DictReader(open(TTJ_EXP27 / rel)):
            if r["item"].startswith("native-heavy"):
                p = M.validate_probs([float(r[f"p{k}"]) for k in range(6)])
                h3_probs[r["item"]] = p
                h3_scores_01[r["item"]] = float(r["h3_score"]) / 5.0

    # Compute judge-free baselines on the 100 native items
    packet_dir = TTJ_EXP09 / "rating_task_packet/main_rating_task"
    edit_sim, len_rat = [], []
    for iid in sorted_items:
        tf, cf = item_meta[iid]
        g_txt = (packet_dir / tf / "gold_lean/reference.lean").read_text(encoding="utf-8", errors="replace")
        c_txt = (packet_dir / tf / "agent_lean" / Path(cf).name).read_text(encoding="utf-8", errors="replace")
        edit_sim.append(difflib.SequenceMatcher(None, g_txt, c_txt).ratio())
        len_rat.append(min(1.0, len(c_txt) / float(max(1, len(g_txt)))))
    rand_u = np.random.default_rng(SEED).uniform(0.0, 1.0, size=len(sorted_items))

    def eval_loto_panel(name: str, raw_probs: np.ndarray, scalar_01: np.ndarray, proxy_ref_cfg: str | None = None) -> dict[str, object]:
        raw_ev = M.evaluate_forecast_panel(raw_probs, rlists, judge_05=5.0 * scalar_01)
        # LOTO CE-fit calibration
        ce_preds = np.zeros((len(sorted_items), 6), dtype=float)
        const_preds = np.zeros((len(sorted_items), 6), dtype=float)
        for t in sorted(set(tasks)):
            te = np.where(t_arr == t)[0]
            tr = np.where(t_arr != t)[0]
            tr_lists = [rlists[i] for i in tr]
            const_preds[te] = M.fit_const(tr_lists, alpha=0.5)(scalar_01[te])
            ce_preds[te] = M.fit_ce_ordinal(scalar_01[tr], tr_lists)(scalar_01[te])

        raw_losses = M.per_item_losses(raw_probs, rlists)
        ce_losses = M.per_item_losses(ce_preds, rlists)
        const_losses = M.per_item_losses(const_preds, rlists)
        boot_raw = M.task_cluster_bootstrap(tasks, lambda ii: np.mean(raw_losses["rps"][ii]), draws=BOOT_DRAWS, seed=SEED)
        boot_ce = M.task_cluster_bootstrap(tasks, lambda ii: np.mean(ce_losses["rps"][ii]), draws=BOOT_DRAWS, seed=SEED)
        boot_diff = M.task_cluster_bootstrap(tasks, lambda ii: float(np.mean(ce_losses["rps"][ii] - const_losses["rps"][ii])), draws=BOOT_DRAWS, seed=SEED)
        sf_diff = M.paired_task_signflip_p(tasks, ce_losses["rps"], const_losses["rps"], draws=BOOT_DRAWS, seed=SEED)
        ce_ev = M.evaluate_forecast_panel(ce_preds, rlists)

        proxy_info = None
        if proxy_ref_cfg is not None:
            match = [r for r in study2_rows if r["config"] == proxy_ref_cfg]
            if match:
                proxy_info = {
                    "ref_config": proxy_ref_cfg,
                    "C_ms_gold": match[0]["proxies"].get("C_ms_gold"),
                    "P_e42_fullcov_brier": match[0]["proxies"].get("P_e42_fullcov_brier"),
                    "P_dsti_proper": match[0]["proxies"].get("P_dsti_proper"),
                    "TI_var_trainnorm": match[0]["proxies"].get("TI_var_trainnorm"),
                }

        return {
            "judge": name,
            "n_items": len(sorted_items),
            "n_tasks": len(set(tasks)),
            "raw": {**raw_ev, "rps_ci": [float(boot_raw["ci_lo"]), float(boot_raw["ci_hi"])]},
            "loto_ce_fit": {
                **ce_ev,
                "rps_ci": [float(boot_ce["ci_lo"]), float(boot_ce["ci_hi"])],
                "dRPS_vs_const": float(boot_diff["point"]),
                "dRPS_vs_const_ci": [float(boot_diff["ci_lo"]), float(boot_diff["ci_hi"])],
                "dRPS_vs_const_p": float(sf_diff["p_val"]),
            },
            "e39_e42_proxy_bridge": proxy_info,
        }

    native_evals = []
    # H2_astra & H2_opus
    for jkey, ref_cfg in (("H2_astra", "sol6h|H2"), ("H2_opus", "opus55x|H2")):
        smap = h2_scores[jkey]
        rp = np.vstack([M.binned_repeats_to_probs(smap[iid], alpha=0.5) for iid in sorted_items])
        sc01 = np.array([float(np.median(smap[iid])) for iid in sorted_items], dtype=float)
        native_evals.append(eval_loto_panel(jkey, rp, sc01, proxy_ref_cfg=ref_cfg))

    # H3_astra native 6-class probs + raw scalar
    h3_rp = np.vstack([h3_probs[iid] for iid in sorted_items])
    h3_s01 = np.array([h3_scores_01[iid] for iid in sorted_items], dtype=float)
    native_evals.append(eval_loto_panel("H3_astra_native_probs", h3_rp, h3_s01, proxy_ref_cfg="sol6h|H2"))

    # Judge-free baselines
    for bname, vec, ref_cfg in (
        ("edit_similarity", np.asarray(edit_sim, dtype=float), "ctl|editdist"),
        ("length_ratio_capped", np.asarray(len_rat, dtype=float), "ctl|count_ratio"),
        ("seeded_random_uniform", rand_u, "ctl|random"),
    ):
        rp = np.vstack([M.binned_repeats_to_probs([v], alpha=0.5) for v in vec])
        native_evals.append(eval_loto_panel(bname, rp, vec, proxy_ref_cfg=ref_cfg))

    # Read Exp 67 interim P8_STRICT_B rows (11-24-2026 247-rating snapshot on the same 100 items) + bridge to E39/E42 proxies
    exp67_b1 = list(csv.DictReader(open(E67_DIR / "results/interim_11-24-2026/judged_B1_per_set_and_pooled.csv")))
    exp67_new_rows = [dict(r) for r in exp67_b1 if r["set"].startswith("new")]
    p8_bridge_map = {
        "Codex": ("sol6h|P8", True, "exact_prompt_close_model (sol6h|P8 vs gpt-5.3-codex|P8_STRICT_B)"),
        "Claude Opus": ("opus55x|P4", False, "same_family_prompt_P4_proxy (no opus55x|P8 in E39/E42)"),
        "Qwen3-Coder": ("qwen36|P8", True, "exact_prompt_close_model (qwen36|P8 vs Qwen3-Coder-30B-A3B|P8_STRICT_B)"),
    }
    for r in exp67_new_rows:
        info = p8_bridge_map.get(r["family"])
        if info:
            rcfg, exact_p, note = info
            m = [x for x in study2_rows if x["config"] == rcfg]
            if m:
                r["proxy_ref_config"] = rcfg
                r["proxy_ref_exact_prompt"] = exact_p
                r["proxy_ref_note"] = note
                r["C_ms_gold"] = m[0]["proxies"].get("C_ms_gold")
                r["P_e42_fullcov_brier"] = m[0]["proxies"].get("P_e42_fullcov_brier")
                r["P_dsti_proper"] = m[0]["proxies"].get("P_dsti_proper")

    # E63 parity check against Exp 68 study_a_e63_proper_scores.json
    e68_a = json.loads((EXP68_DIR / "results/study_a_e63_proper_scores.json").read_text())
    e63_test = sorted([it for it in rv1_items if it["split"] == "test"], key=lambda x: x["item"])
    e63_runs_dir = E63_DIR / "results/runs"
    e63_arms = {
        "zero_shot_base": ["base_q3_8b_test.json"],
        "prompt_opt_arm1": ["arm1_q3_8b_s0/eval_test.json", "arm1_q3_8b_s1/eval_test.json"],
        "rl_grpo": ["rl_q3_8b_s0/eval_test.json", "rl_q3_8b_s1/eval_test.json", "rl_q3_8b_s2/eval_test.json"],
        "teacher_only_sft": [f"sft_q3_8b_s{i}/eval_test.json" for i in range(6)],
        "human_mix_sft": [f"sft_q3_8b_hm_s{i}/eval_test.json" for i in range(5)],
        "shuffled_control": ["sft_q3_8b_shuf_s0/eval_test.json"],
    }
    e63_max_diff = 0.0
    e63_summary = []
    for arm, rels in e63_arms.items():
        probs_list = []
        for rel in rels:
            raw = json.loads((e63_runs_dir / rel).read_text())["res"]
            crits = {v["item"]: v for v in raw.values() if v.get("split") == "test" and v.get("human") is not None}
            probs_list.append(np.vstack([M.validate_probs(crits[it["item"]]["probs"]) for it in e63_test]))
        ens_p = np.mean(probs_list, axis=0)
        ev5 = M.evaluate_forecast_panel(ens_p, [it["all5_ratings"] for it in e63_test])
        ref5 = e68_a["targets"]["all5"]["arms"][arm]["ensemble"]
        for k in ("rps", "ce", "tvd", "brier", "icc_a1", "spearman"):
            e63_max_diff = max(e63_max_diff, abs(float(ev5[k]) - float(ref5[k]["val"])))
        e63_summary.append({"arm": arm, "n_seeds": len(rels), **{k: float(ev5[k]) for k in ("rps", "ce", "tvd", "brier", "bias_05", "icc_a1", "spearman")}})

    if e63_max_diff > 1e-10:
        raise RuntimeError(f"E63 parity check failed: max_diff={e63_max_diff}")

    return {
        "native_main_cached_evals": native_evals,
        "exp67_interim_p8_rows": exp67_new_rows,
        "e63_parity_max_diff_vs_exp68": e63_max_diff,
        "e63_all5_summary": e63_summary,
    }


# ===================================================================== Figures
def make_figures(study1: dict, study2: dict, study3: dict, study4: dict) -> list[str]:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    rows = study2["unit_rows"]
    const_rps = float(study2["const_train_baseline_heldout_all5"]["rps"])

    # Figure 1: Proxy vs Target (C_ms_gold vs P_dsti_proper vs TI_var against ce_cal_all5_rps)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
    panels = [
        ("TI_var_trainnorm", "Legacy TI_var (train-norm)"),
        ("C_ms_gold", "E39 Selected C_ms_gold"),
        ("P_dsti_proper", "Proper Behavioral P_dsti_proper"),
    ]
    for ax, (pk, title) in zip(axes, panels):
        for grp, color, marker, label in (
            ([r for r in rows if r["kind"] == "llm" and r["split"] != "test"], "#4C72B0", "o", "Train/Val LLM"),
            ([r for r in rows if r["kind"] == "llm" and r["split"] == "test"], "#2CA02C", "s", "Test LLM (n=18)"),
            ([r for r in rows if r["kind"] != "llm"], "#D62728", "^", "Deterministic Ctrl (n=4)"),
        ):
            xs = [r["proxies"][pk] for r in grp if r["proxies"].get(pk) is not None and r["targets"].get("ce_cal_all5_rps") is not None]
            ys = [r["targets"]["ce_cal_all5_rps"] for r in grp if r["proxies"].get(pk) is not None and r["targets"].get("ce_cal_all5_rps") is not None]
            ax.scatter(xs, ys, c=color, marker=marker, s=55, alpha=0.88, label=label, edgecolors="white", linewidths=0.5)
            if grp and grp[0]["kind"] != "llm":
                for r in grp:
                    xv, yv = r["proxies"].get(pk), r["targets"].get("ce_cal_all5_rps")
                    if xv is not None and yv is not None:
                        lbl = r["config"].replace("ctl|", "")
                        if pk == "C_ms_gold" and xv > 0.95:
                            ax.annotate(lbl, (xv, yv), xytext=(-6, 3), textcoords="offset points", ha="right", fontsize=7.5, color="#900")
                        else:
                            ax.annotate(lbl, (xv, yv), xytext=(4, 4), textcoords="offset points", fontsize=7.5, color="#900")
        ax.axhline(const_rps, color="#555555", linestyle="--", linewidth=1.2, label=f"CONST_train ({const_rps:.3f})")
        ax.set_title(title, fontsize=10.5, fontweight="bold")
        ax.set_xlabel(pk, fontsize=9.5)
        ax.grid(True, alpha=0.35)
    axes[0].set_ylabel("Held-Out CE-Calibrated RPS (lower = better)", fontsize=9.5)
    axes[2].legend(loc="lower left", fontsize=7.5, framealpha=0.92)
    fig.suptitle("Experiment 70 (E39+E42, n=60): Label-Free Proxies vs Held-Out Proper-Scoring Judge Risk", fontsize=11.5, fontweight="bold")
    fig.tight_layout()
    f1 = FIGURES_DIR / "fig1_proxy_vs_proper_target_e39_e42.png"
    fig.savefig(f1, dpi=180)
    plt.close(fig)

    # Figure 2: Meta-metrics (Top-1 Regret & UWA_RPS on Test LLM vs Test LLM + Ctrl, plus E60)
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.8))
    show_proxies = ["TI_var_trainnorm", "PTI_v0_frozen", "C_ms_gold", "P_e39_fullcov_brier", "P_e42_fullcov_brier", "P_dsti_proper"]
    short_names = ["TI_var", "PTI_v0", "C_ms_gold", "P_e39_Brier", "P_e42_Brier", "P_dsti_proper"]
    x = np.arange(len(show_proxies))
    w = 0.36

    def _get_vals(subset_key: str, metric: str) -> list[float]:
        ev_map = {e["proxy"]: e for e in study2["meta_results"][subset_key]["ce_cal_all5_rps"]}
        vals = []
        for pk in show_proxies:
            e = ev_map.get(pk, {})
            if not e.get("computable"):
                vals.append(float("nan"))
            elif metric == "top1_regret":
                vals.append(float(e["top1"]["regret"]))
            elif metric == "uwa":
                vals.append(float(e["uwa"]))
        return vals

    r_llm = _get_vals("test_llm", "top1_regret")
    r_ctrl = _get_vals("test_llm_plus_ctrl", "top1_regret")
    axes[0].bar(x - w / 2, r_llm, width=w, label="Test LLM (n<=18; n varies)", color="#4C72B0")
    axes[0].bar(x + w / 2, r_ctrl, width=w, label="Test LLM + 4 Controls (n<=22)", color="#D62728", alpha=0.85)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(short_names, rotation=20, ha="right", fontsize=8.5)
    axes[0].set_ylabel("Top-1 CE-Calibrated RPS Regret (lower = better)", fontsize=9.5)
    axes[0].set_title("A. Top-1 Selection Regret (Controls Hijack Rank Proxies)", fontsize=10, fontweight="bold")
    axes[0].grid(True, alpha=0.35, axis="y")
    axes[0].legend(fontsize=8)

    u_llm = _get_vals("test_llm", "uwa")
    u_ctrl = _get_vals("test_llm_plus_ctrl", "uwa")
    axes[1].bar(x - w / 2, u_llm, width=w, label="Test LLM (n<=18; n varies)", color="#2CA02C")
    axes[1].bar(x + w / 2, u_ctrl, width=w, label="Test LLM + 4 Controls (n<=22)", color="#FF7F0E", alpha=0.85)
    axes[1].axhline(0.5, color="#555555", linestyle="--", linewidth=1.1, label="Random ordering (0.50)")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(short_names, rotation=20, ha="right", fontsize=8.5)
    axes[1].set_ylabel("Utility-Weighted Pairwise Accuracy (UWA_RPS)", fontsize=9.5)
    axes[1].set_title("B. Utility-Weighted Pairwise Decision Accuracy (higher = better)", fontsize=10, fontweight="bold")
    axes[1].set_ylim(0.0, 1.05)
    axes[1].grid(True, alpha=0.35, axis="y")
    axes[1].legend(fontsize=8)

    fig.suptitle("Experiment 70: Decision-Theoretic Proxy Evaluation on Held-Out Test Judges", fontsize=11.5, fontweight="bold")
    fig.tight_layout()
    f2 = FIGURES_DIR / "fig2_meta_metrics_comparison_and_regret.png"
    fig.savefig(f2, dpi=180)
    plt.close(fig)

    # Figure 3: native_main N=100 (250 ratings) Bridge — Judges/Baselines RPS vs Proxy Scores
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    evals = study4["native_main_cached_evals"]
    names = [e["judge"] for e in evals] + [f"Exp67_{r['family']}|P8" for r in study4["exp67_interim_p8_rows"]]
    raw_rps = [e["raw"]["rps"] for e in evals] + [float(r["RPS"]) for r in study4["exp67_interim_p8_rows"]]
    cal_rps = [e["loto_ce_fit"]["rps"] for e in evals] + [float("nan")] * len(study4["exp67_interim_p8_rows"])
    const_loto_rps = float(study1["native_main"]["const_loto"]["rps"]["val"])
    loro_emp_rps = float(study1["native_main"]["loro_ceiling"]["empirical"]["rps"])
    x3 = np.arange(len(names))
    w3 = 0.36
    ax.bar(x3 - w3 / 2, raw_rps, width=w3, label="Raw binned/native RPS", color="#8C564B")
    cal_mask = [not math.isnan(v) for v in cal_rps]
    ax.bar(
        x3[cal_mask] + w3 / 2,
        [v for v, m in zip(cal_rps, cal_mask) if m],
        width=w3,
        label="LOTO CE-fit RPS (cached H2/H3/base)",
        color="#1F77B4",
    )
    ax.axhline(const_loto_rps, color="#D62728", linestyle="--", linewidth=1.3, label=f"CONST_loto RPS ({const_loto_rps:.4f})")
    ax.axhline(loro_emp_rps, color="#2CA02C", linestyle=":", linewidth=1.5, label=f"Empirical Human LORO Ceiling ({loro_emp_rps:.4f})")
    ax.set_xticks(x3)
    ax.set_xticklabels(names, rotation=22, ha="right", fontsize=8.5)
    ax.set_ylabel("RPS on 100 native_main files (lower = better)", fontsize=9.5)
    ax.set_title("Experiment 70: Live VeriBench native_main (N=100, 250 ratings) Judge & Baseline Proper Scores", fontsize=11, fontweight="bold")
    ax.grid(True, alpha=0.35, axis="y")
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    f3 = FIGURES_DIR / "fig3_native_main_100files_bridge.png"
    fig.savefig(f3, dpi=180)
    plt.close(fig)

    return [f1.name, f2.name, f3.name]


def export_csv_tables(study2: dict, study3: dict, study4: dict) -> None:
    # 1. Study 2 unit table
    u_rows = []
    for r in study2["unit_rows"]:
        u_rows.append({
            "config": r["config"],
            "family": r["family"],
            "split": r["split"],
            "kind": r["kind"],
            "harness": r["harness"],
            "is_rubric": r["is_rubric"],
            **{k: r["proxies"].get(k) for k in (
                "TI_var_trainnorm", "PTI_v0_frozen", "C_ms_gold", "S_e42", "P_e42_disc",
                "P_e39_fullcov_brier", "P_e39_probe_rps", "P_e42_fullcov_brier", "P_e42_strict_brier",
                "P_e42_fullcov_ce", "P_dsti_proper", "P_dsti_gated", "P_meta_comb_cecal",
            )},
            **{k: r["targets"].get(k) for k in (
                "raw_all5_rps", "raw_all5_ce", "raw_all5_tvd", "raw_all5_brier", "raw_all5_icc_a1", "raw_all5_spearman",
                "ce_cal_all5_rps", "ce_cal_all5_ce", "ce_cal_all5_tvd", "ce_cal_all5_brier", "ce_cal_all5_icc_a1",
                "pe_cal_all5_rps", "raw_exp3_spearman", "ce_cal_exp3_rps",
            )},
        })
    _write_csv(RESULTS_DIR / "study2_e39_e42_units.csv", u_rows)

    # 2. Study 2 meta-evaluation table
    m_rows = []
    for sname, tdict in study2["meta_results"].items():
        for tkey, evals in tdict.items():
            for ev in evals:
                if not ev.get("computable"):
                    continue
                rm = ev.get("rank_meta") or {}
                bc = ev.get("beat_const_meta_pred") or {}
                rk = ev.get("risk_meta_pred") or {}
                sp_ci = rm.get("spearman_ci") or [None, None]
                uwa_ci = ev.get("uwa_ci") or [None, None]
                m_rows.append({
                    "subset": sname,
                    "target": tkey,
                    "proxy": ev["proxy"],
                    "n_units": ev["n_units"],
                    "top1_regret": ev["top1"]["regret"],
                    "top1_n_tied": ev["top1"]["n_tied"],
                    "top1_selected": ";".join(ev["top1"]["selected_configs"]),
                    "sub5_mean_regret": ev["subpool_5"].get("mean_regret"),
                    "sub10_mean_regret": ev["subpool_10"].get("mean_regret"),
                    "sub10_beat_const_rate": ev["subpool_10"].get("beat_const_rate"),
                    "lofo_mean_regret": ev["lofo"].get("lofo_mean_regret"),
                    "within_fam_regret": ev["lofo"].get("within_family_mean_regret"),
                    "uwa": ev["uwa"],
                    "uwa_ci_lo": uwa_ci[0],
                    "uwa_ci_hi": uwa_ci[1],
                    "beat_const_meta_brier": bc.get("meta_brier"),
                    "beat_const_base_brier": bc.get("base_rate_brier"),
                    "beat_const_meta_ce": bc.get("meta_ce"),
                    "beat_const_auroc": bc.get("auroc"),
                    "beat_const_calibrated_auroc": bc.get("calibrated_auroc"),
                    "risk_meta_rmse": rk.get("meta_rmse"),
                    "risk_const_rmse": rk.get("const_rmse"),
                    "risk_meta_icc_a1": rk.get("meta_icc_a1"),
                    "spearman": rm.get("spearman"),
                    "spearman_ci_lo": sp_ci[0],
                    "spearman_ci_hi": sp_ci[1],
                    "kendall": rm.get("kendall"),
                    "pearson": rm.get("pearson"),
                    "perm_p_two_sided": rm.get("perm_p_two_sided"),
                    "within_family_perm_p": rm.get("within_family_perm_p_two_sided"),
                })
    _write_csv(RESULTS_DIR / "study2_meta_comparison.csv", m_rows)

    # 3. Study 3 E60 meta table
    e60_rows = []
    for cohort, tdict in study3["e60_meta"].items():
        for tkey, evals in tdict.items():
            for ev in evals:
                if not ev.get("computable"):
                    continue
                rm = ev.get("rank_meta") or {}
                sp_ci = rm.get("spearman_ci") or [None, None]
                e60_rows.append({
                    "cohort": cohort,
                    "target": tkey,
                    "proxy": ev["proxy"],
                    "n_units": ev["n_units"],
                    "top1_regret": ev["top1"]["regret"],
                    "sub10_mean_regret": ev["subpool_10"].get("mean_regret"),
                    "lofo_mean_regret": ev["lofo"].get("lofo_mean_regret"),
                    "uwa": ev["uwa"],
                    "spearman": rm.get("spearman"),
                    "spearman_ci_lo": sp_ci[0],
                    "spearman_ci_hi": sp_ci[1],
                    "perm_p_two_sided": rm.get("perm_p_two_sided"),
                })
    _write_csv(RESULTS_DIR / "study3_e60_meta.csv", e60_rows)

    # 4. Study 4 native_main bridge
    n_rows = []
    for e in study4["native_main_cached_evals"]:
        pb = e.get("e39_e42_proxy_bridge") or {}
        n_rows.append({
            "judge": e["judge"],
            "raw_rps": e["raw"]["rps"],
            "raw_ce": e["raw"]["ce"],
            "raw_tvd": e["raw"]["tvd"],
            "raw_bias_05": e["raw"]["bias_05"],
            "raw_icc_a1": e["raw"]["icc_a1"],
            "raw_spearman": e["raw"]["spearman"],
            "loto_ce_rps": e["loto_ce_fit"]["rps"],
            "loto_ce_ce": e["loto_ce_fit"]["ce"],
            "loto_ce_tvd": e["loto_ce_fit"]["tvd"],
            "loto_dRPS_vs_const": e["loto_ce_fit"]["dRPS_vs_const"],
            "loto_dRPS_p": e["loto_ce_fit"]["dRPS_vs_const_p"],
            "proxy_ref_config": pb.get("ref_config"),
            "C_ms_gold": pb.get("C_ms_gold"),
            "P_e42_fullcov_brier": pb.get("P_e42_fullcov_brier"),
            "P_dsti_proper": pb.get("P_dsti_proper"),
        })
    _write_csv(RESULTS_DIR / "study4_native_main_bridge.csv", n_rows)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    rv1_items, _ = load_rv1_items()

    print("[1/4] Study 1: Live VeriBench Google Sheets check & cohort ceilings...")
    study1, native_mem = run_study_1_human_cohorts(rv1_items)
    _write_json(RESULTS_DIR / "study1_human_cohorts.json", study1)

    print("[2/4] Study 2: E39+E42 proper-scoring proxy-vs-target alignment & Meta-Corr vs Meta-Proper...")
    study2 = run_study_2_e39_e42(rv1_items)
    _write_json(RESULTS_DIR / "study2_e39_e42_proxy_target.json", study2)

    print("[3/4] Study 3: E60 open-weight replication (streaming tarballs) & E58 cross-check...")
    study3 = run_study_3_e60_e58(rv1_items)
    _write_json(RESULTS_DIR / "study3_e60_e58_replication.json", study3)

    print("[4/4] Study 4: native_main (N=100, 250 ratings) bridge & E63 parity check...")
    study4 = run_study_4_native_bridge(native_mem, study2["unit_rows"], rv1_items)
    _write_json(RESULTS_DIR / "study4_native_main_bridge.json", study4)

    export_csv_tables(study2, study3, study4)
    figs = make_figures(study1, study2, study3, study4)
    print("DONE. Generated figures:", figs)
    print("  Study 1 live non-A1 ratings:", study1["native_main"]["total_non_a1_ratings"], "changed:", len(study1["live_vs_manifest_changed"]))
    print("  Study 2 Exp68 max parity diff:", study2["parity_max_diff_vs_exp68"])
    print("  Study 3 E62 max parity diff:", study3["e62_parity_check"])
    print("  Study 4 E63 max parity diff:", study4["e63_parity_max_diff_vs_exp68"])


if __name__ == "__main__":
    main()
