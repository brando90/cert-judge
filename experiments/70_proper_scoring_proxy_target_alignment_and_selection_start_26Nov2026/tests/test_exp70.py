#!/usr/bin/env python3
"""Unit tests, synthetic counterexamples, leakage guards, and privacy checks for Experiment 70."""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
EXP_DIR = THIS_DIR.parent
SCRIPTS_DIR = EXP_DIR / "scripts"
RESULTS_DIR = EXP_DIR / "results"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import proxy_metrics as PM  # noqa: E402
import metrics as M  # noqa: E402


class TestProxyMetricsAndCounterexamples(unittest.TestCase):
    def test_affine_warp_preserves_spearman_but_breaks_raw_proper_scores(self) -> None:
        """Spearman is blind to affine collapse/shift, while RPS/Brier/CE detect it."""
        ratings = [[0], [1], [2], [3], [4], [5]] * 4
        # Good well-scaled scores s in [0, 1]
        s_good = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0] * 4)
        # Harsh/compressed affine transform 0.1 * s (strictly increasing -> identical Spearman!)
        s_bad = 0.1 * s_good
        h_mean = np.array([float(np.mean(r)) for r in ratings])
        self.assertAlmostEqual(M.spearman_corr(s_good, h_mean), M.spearman_corr(s_bad, h_mean), places=12)
        q_good = np.vstack([M.binned_repeats_to_probs([v], alpha=0.5) for v in s_good])
        q_bad = np.vstack([M.binned_repeats_to_probs([v], alpha=0.5) for v in s_bad])
        ev_good = M.evaluate_forecast_panel(q_good, ratings, judge_05=5.0 * s_good)
        ev_bad = M.evaluate_forecast_panel(q_bad, ratings, judge_05=5.0 * s_bad)
        self.assertLess(ev_good["rps"], ev_bad["rps"])
        self.assertLess(ev_good["brier"], ev_bad["brier"])
        self.assertLess(ev_good["ce"], ev_bad["ce"])
        self.assertGreater(ev_good["icc_a1"], ev_bad["icc_a1"])

    def test_label_free_tie_averaging_never_leaks_target(self) -> None:
        """Shuffling targets among tied max-proxy units changes expected regret identically."""
        rows = [
            {"config": "ctrl1", "family": "ctl", "proxies": {"P": 1.0}, "targets": {"RPS": 0.20}},
            {"config": "ctrl2", "family": "ctl", "proxies": {"P": 1.0}, "targets": {"RPS": 0.18}},
            {"config": "llm1", "family": "f1", "proxies": {"P": 0.99}, "targets": {"RPS": 0.12}},
        ]
        res = PM.top1_regret_label_free(rows, "P", "RPS", lower_is_better=True)
        self.assertEqual(res["n_tied"], 2)
        self.assertAlmostEqual(res["selected_target"], 0.19, places=12)
        self.assertAlmostEqual(res["oracle_target"], 0.12, places=12)
        self.assertAlmostEqual(res["regret"], 0.07, places=12)

    def test_control_hijack_vs_e42_fullcov_brier(self) -> None:
        """A control scoring 1.0 on ident AND 1.0 on weakenings gets penalized by P_e42_fullcov_brier."""
        manifest = [
            {"probe_id": "id1", "family": "identity", "valid": True},
            {"probe_id": "fmt1", "family": "formatting", "valid": True},
            {"probe_id": "vac1", "family": "vacuity", "valid": True},
            {"probe_id": "wk1", "family": "weakening", "valid": True},
            {"probe_id": "ov1", "family": "overconstraint", "valid": True},
        ]
        # Strong LLM: 3 repeats at 1.0 on ident/fmt, 0.4 on vac/wk/ov (never 1.0 on defective probes!)
        cells_llm = [
            {"cell": "id1__r1", "status": "measured", "score": 1.0},
            {"cell": "id1__r2", "status": "measured", "score": 1.0},
            {"cell": "id1__r3", "status": "measured", "score": 1.0},
            {"cell": "fmt1__r1", "status": "measured", "score": 1.0},
            {"cell": "fmt1__r2", "status": "measured", "score": 1.0},
            {"cell": "fmt1__r3", "status": "measured", "score": 1.0},
            {"cell": "vac1__r1", "status": "measured", "score": 0.0},
            {"cell": "vac1__r2", "status": "measured", "score": 0.0},
            {"cell": "vac1__r3", "status": "measured", "score": 0.0},
            {"cell": "wk1__r1", "status": "measured", "score": 0.4},
            {"cell": "wk1__r2", "status": "measured", "score": 0.4},
            {"cell": "wk1__r3", "status": "measured", "score": 0.4},
            {"cell": "ov1__r1", "status": "measured", "score": 0.4},
            {"cell": "ov1__r2", "status": "measured", "score": 0.4},
            {"cell": "ov1__r3", "status": "measured", "score": 0.4},
        ]
        # Degenerate lexical control: gives 1.0 to weakened/overconstrained probes too
        cells_ctrl = [
            {"cell": "id1__r1", "status": "deterministic", "score": 1.0},
            {"cell": "id1__r2", "status": "deterministic", "score": 1.0},
            {"cell": "id1__r3", "status": "deterministic", "score": 1.0},
            {"cell": "fmt1__r1", "status": "deterministic", "score": 1.0},
            {"cell": "fmt1__r2", "status": "deterministic", "score": 1.0},
            {"cell": "fmt1__r3", "status": "deterministic", "score": 1.0},
            {"cell": "vac1__r1", "status": "deterministic", "score": 0.0},
            {"cell": "vac1__r2", "status": "deterministic", "score": 0.0},
            {"cell": "vac1__r3", "status": "deterministic", "score": 0.0},
            {"cell": "wk1__r1", "status": "deterministic", "score": 1.0},
            {"cell": "wk1__r2", "status": "deterministic", "score": 1.0},
            {"cell": "wk1__r3", "status": "deterministic", "score": 1.0},
            {"cell": "ov1__r1", "status": "deterministic", "score": 1.0},
            {"cell": "ov1__r2", "status": "deterministic", "score": 1.0},
            {"cell": "ov1__r3", "status": "deterministic", "score": 1.0},
        ]
        p_llm = PM.compute_e42_probe_proxies(cells_llm, manifest)
        p_ctrl = PM.compute_e42_probe_proxies(cells_ctrl, manifest)
        self.assertGreater(p_llm["P_e42_fullcov_brier"], 0.95)
        self.assertLess(p_ctrl["P_e42_fullcov_brier"], 0.78)

    def test_uwa_and_meta_binary_proper_eval(self) -> None:
        proxies = [0.9, 0.8, 0.4, 0.2]
        targets = [0.10, 0.12, 0.18, 0.22]
        self.assertAlmostEqual(PM.utility_weighted_pairwise_accuracy(proxies, targets, lower_is_better=True), 1.0, places=12)
        self.assertAlmostEqual(PM.utility_weighted_pairwise_accuracy(list(reversed(proxies)), targets, lower_is_better=True), 0.0, places=12)
        bm = PM.meta_binary_proper_eval([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1], [0.15, 0.85], [0, 1])
        self.assertLess(bm["meta_brier"], bm["base_rate_brier"])
        self.assertAlmostEqual(bm["auroc"], 1.0, places=12)

    def test_uwa_vectorized_matches_naive_reference(self) -> None:
        """Vectorized UWA matches O(n^2) scalar reference on ties, exact equal targets, and random draws."""
        rng = np.random.default_rng(123)
        proxies = np.array([0.8, 0.8, 0.5, 0.3, 0.9, 0.1, 0.5])
        targets = np.array([0.12, 0.18, 0.15, 0.15, 0.10, 0.30, 0.22])
        for lower_is_better in (True, False):
            # Reference scalar double loop
            num, den = 0.0, 0.0
            for i in range(len(proxies)):
                for j in range(i + 1, len(proxies)):
                    w = abs(float(targets[i] - targets[j]))
                    if w <= 1e-15:
                        continue
                    den += w
                    dp = float(proxies[i] - proxies[j])
                    if abs(dp) <= 1e-12:
                        num += 0.5 * w
                    elif ((targets[i] < targets[j]) if lower_is_better else (targets[i] > targets[j])) == (dp > 0.0):
                        num += w
            ref = num / den
            vec = PM.utility_weighted_pairwise_accuracy(proxies, targets, lower_is_better=lower_is_better)
            self.assertAlmostEqual(vec, ref, places=12)
        p_rand = rng.uniform(0, 1, size=25)
        t_rand = rng.uniform(0, 1, size=25)
        self.assertTrue(np.isfinite(PM.utility_weighted_pairwise_accuracy(p_rand, t_rand, lower_is_better=True)))

    def test_results_privacy_and_secrets_if_generated(self) -> None:
        """Scan all tracked Exp 70 files + LaTeX fragment for personal emails, sheet IDs, secrets, and roster names."""
        repo_root = EXP_DIR.parents[1]
        targets = (
            list(EXP_DIR.glob("*.md"))
            + list((EXP_DIR / "scripts").glob("*.py"))
            + list((EXP_DIR / "tests").glob("*.py"))
            + list((EXP_DIR / "derivation").glob("*.tex"))
            + list(RESULTS_DIR.glob("*.json"))
            + list(RESULTS_DIR.glob("*.csv"))
            + list(RESULTS_DIR.glob("*.txt"))
            + list((repo_root / "latex").rglob("*.tex"))
        )
        targets = [fp for fp in targets if fp.exists()]
        banned_patterns = [
            re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
            re.compile(r"spreadsheets/d/(?!<REDACTED)[A-Za-z0-9_-]{15,}"),
            re.compile(r"sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{20,}"),
        ]
        # Dynamically load local roster names & sheet IDs from sibling trustworthy-theorem-judges if present (never hardcode)
        ttj_man = repo_root.parent / "trustworthy-theorem-judges/experiments/09_prepare_packets_and_collect_human_ratings_start_28Sep2026/ratings/RAW_MANIFEST.json"
        if ttj_man.exists():
            man = json.loads(ttj_man.read_text())
            names = {
                str(e.get("rater_name", "")).split("(")[0].strip()
                for e in man.get("files", [])
                if e.get("rater_id") != "A1" and len(str(e.get("rater_name", "")).split("(")[0].strip()) >= 5
            }
            sids = {str(e.get("spreadsheet_id", "")).strip() for e in man.get("files", []) if len(str(e.get("spreadsheet_id", "")).strip()) >= 20}
            tokens = names | sids
            if tokens:
                banned_patterns.append(re.compile("|".join(re.escape(t) for t in sorted(tokens)), re.I))
        for fp in targets:
            txt = fp.read_text(encoding="utf-8", errors="replace")
            for pat in banned_patterns:
                self.assertIsNone(pat.search(txt), f"Banned pattern {pat.pattern} found in {fp}")


if __name__ == "__main__":
    unittest.main()
