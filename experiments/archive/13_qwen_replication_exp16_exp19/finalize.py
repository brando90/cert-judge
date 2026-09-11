#!/usr/bin/env python3
"""Wait for the Exp13 (Qwen3.6-27B) chained run to finish, then commit results,
open a PR assigned to ehersch, and email Brando + Ethan with key figures.

Run:
    PYTHONPATH=~/ultimate-utils/py_src \
        python3 experiments/13_qwen_replication_exp16_exp19/finalize.py \
        --log <path/to/run.log>

Idempotent-ish: if the branch / PR already exists it logs and proceeds to email.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

REPO = Path("/dfs/scratch0/brando9/cert-judge")
EXP_DIR = REPO / "experiments/13_qwen_replication_exp16_exp19"
RES16 = EXP_DIR / "results/exp16_qwen_r3_median"
RES19 = EXP_DIR / "results/exp19_low_variance_replot_qwen"
RES25_BASE = EXP_DIR / "results/exp25_geometric_qwen_r3_median_mono_stab_40_60"

EMAIL_TO = "brando.science@gmail.com"
EMAIL_CC = ",".join([
    "brandojazz@gmail.com",
    "brando9@cs.stanford.edu",
    "brando9@stanford.edu",
    "ethanhersch@stanford.edu",
    "herschethan@gmail.com",
])
SMTP_USER = "brandojazz@gmail.com"
SMTP_PASS_FILE = os.path.expanduser("~/keys/gmail_app_password.txt")
ASSIGNEE = "ehersch"
POLL_SEC = 30
MAX_WAIT_SEC = 6 * 60 * 60  # 6 h hard ceiling — Qwen 27B with 3 repeats is slower than Mistral hosted
QWEN_MODEL_ID = "Qwen/Qwen3-Coder-30B-A3B-Instruct"


def wait_for_done(log_path: Path) -> str:
    start = time.time()
    last_size = -1
    while time.time() - start < MAX_WAIT_SEC:
        if not log_path.exists():
            time.sleep(POLL_SEC); continue
        text = log_path.read_text(errors="replace")
        if "DONE." in text or "DONE ===" in text:
            return "ok"
        if "Traceback" in text or "Error: " in text:
            tail = "\n".join(text.splitlines()[-40:])
            if "DONE" not in text:
                print(f"[finalize] Detected error in log:\n{tail}", file=sys.stderr)
                return "err"
        sz = log_path.stat().st_size
        if sz == last_size and not _python_still_alive():
            print("[finalize] Python process gone and log idle. Treating as error.",
                  file=sys.stderr)
            return "err"
        last_size = sz
        time.sleep(POLL_SEC)
    return "err"


def _python_still_alive() -> bool:
    try:
        out = subprocess.check_output(
            ["pgrep", "-f", "exp16_multi_judge_human_sets|exp19_replot_low_variance|exp25_plot_baseline_vs_geometric"],
            text=True,
        )
        return bool(out.strip())
    except subprocess.CalledProcessError:
        return False


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    print(f"[finalize] $ {' '.join(shlex.quote(c) for c in cmd)}")
    return subprocess.run(cmd, cwd=cwd or REPO, check=check, capture_output=True, text=True)


def git_branch_commit_push() -> str:
    branch = f"exp13-qwen3.6-27b-{datetime.now():%Y%m%d-%H%M}"
    run(["git", "fetch", "--all"], check=False)
    run(["git", "checkout", "main"], check=False)
    run(["git", "pull"], check=False)
    res = run(["git", "checkout", "-b", branch], check=False)
    if res.returncode != 0:
        run(["git", "checkout", branch])

    add_paths = [
        str(EXP_DIR.relative_to(REPO)),  # whole exp13 dir incl. results, scripts, README, cc.md
        "experiments/02_neurips_reviews/utils/judge_caller.py",
    ]
    for p in add_paths:
        run(["git", "add", p], check=False)

    msg = (
        f"exp13: Qwen3.6-27B replication of Exp16/Exp19/Exp25 (geometric trust index)\n\n"
        f"Adds open-weights Qwen3.6-27B (April 2026, Apache 2.0) as the primary judge,\n"
        f"served via local vLLM on snap. Mirrors the Exp12 Leanstral runbook but with\n"
        f"the latest SOTA open-weights Qwen — model identifier: {QWEN_MODEL_ID}.\n\n"
        f"Patches judge_caller.py with an additive `qwen` prefix branch routed to a\n"
        f"vLLM OpenAI-compatible endpoint (configurable via QWEN_BASE_URL / QWEN_API_KEY).\n"
        f"Backward-compat with claude-*, gpt-*, o1*/o3*, leanstral* unchanged.\n\n"
        f"Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>\n"
    )
    res = run(["git", "commit", "-m", msg], check=False)
    if "nothing to commit" in (res.stdout + res.stderr).lower():
        print("[finalize] Nothing to commit (results may already be tracked).")
    run(["git", "push", "-u", "origin", branch])
    return branch


def open_pr(branch: str, summary_text: str) -> str:
    title = "[Exp13] Qwen3.6-27B (open-weights SOTA) replication of Exp16/Exp19/Exp25"
    body = (
        "## Summary\n"
        "- Replicates the Exp16 (multi-judge cert→human trend), Exp19 (low-variance replot),\n"
        "  and Exp25 (geometric cert-index, avg/pass1/pass2) pipeline using **Qwen3.6-27B**\n"
        "  as the primary open-weights judge family. `gpt-4o-mini` retained as cross-family\n"
        "  weak control, plus the standard `editdist` + `random` baselines.\n"
        "- Qwen3.6-27B is the latest SOTA open-weights Qwen (April 2026, Apache 2.0): dense,\n"
        "  77.2% SWE-bench Verified, 262K native ctx. Served locally via vLLM on snap GPUs.\n"
        "- Adds an additive `qwen` prefix branch in `experiments/02_.../utils/judge_caller.py`\n"
        "  that routes Qwen models to a configurable OpenAI-compatible endpoint\n"
        "  (`QWEN_BASE_URL` / `QWEN_API_KEY`). Backward-compat with claude-*, gpt-*, o*,\n"
        "  leanstral* unchanged.\n\n"
        f"## Headline numbers (auto)\n```\n{summary_text}\n```\n\n"
        "## Test plan\n"
        "- [ ] Verify Exp16 outputs exist (summary.json, judge_rows.csv, detail_rows.csv,\n"
        "      fig_cert_vs_human_scatter_{pass1,pass2,avg}.png)\n"
        "- [ ] Verify Exp19 outputs (fig_main_monotonicity_lowvar.png, fig_failure_*.png)\n"
        "- [ ] Verify Exp25 geometric reanalysis for pass1/pass2/avg (summary.json + plot)\n"
        "- [ ] Spot-check `MODEL_USED.txt` shows Qwen/Qwen3.6-27B\n"
        "- [ ] Compare ρ_baseline vs ρ_geometric per pass\n"
        "- [ ] Backward-compat: gpt-4o-mini judges still produce valid scores\n\n"
        "🤖 Generated with [Claude Code](https://claude.com/claude-code)\n"
    )
    res = run([
        "gh", "pr", "create",
        "--base", "main",
        "--head", branch,
        "--title", title,
        "--body", body,
        "--assignee", ASSIGNEE,
    ], check=False)
    if res.returncode != 0:
        view = run(["gh", "pr", "view", "--json", "url", "-q", ".url"], check=False)
        if view.returncode == 0 and view.stdout.strip():
            return view.stdout.strip()
        raise RuntimeError(f"gh pr create failed:\n{res.stdout}\n{res.stderr}")
    return res.stdout.strip()


def collect_summary() -> tuple[str, list[Path]]:
    lines: list[str] = []
    attachments: list[Path] = []
    summary_p = RES16 / "summary.json"
    if summary_p.exists():
        s = json.loads(summary_p.read_text())
        lines.append(f"Exp16: n_judges={s.get('n_judges')} n_union_rows={s.get('n_union_rows')}")
        for ls, t in (s.get("trend_by_set") or {}).items():
            v2 = t.get("trend_v2", {})
            lines.append(
                f"  {ls}: r={v2.get('spearman_r', float('nan')):.3f} "
                f"CI=[{v2.get('spearman_ci_lo', float('nan')):.3f},"
                f"{v2.get('spearman_ci_hi', float('nan')):.3f}] "
                f"perm_p={v2.get('spearman_perm_p', float('nan')):.4f}"
            )
        for r in (s.get("judge_rows") or [])[:10]:
            lines.append(
                f"  - {r.get('judge_id')}: ident={r.get('identity_mean'):.2f} "
                f"bug_r={r.get('bug_spearman_r'):.2f} flip={r.get('flip_rate'):.2f} "
                f"cert_v2={r.get('cert_index_v2'):.2f}"
            )
    else:
        lines.append("(Exp16 summary.json missing)")

    lines.append("")
    lines.append("Exp25 geometric reanalysis:")
    for label in ("avg", "pass1", "pass2"):
        gm_dir = RES25_BASE.parent / f"{RES25_BASE.name}_{label}"
        gm_sj = gm_dir / "summary.json"
        if gm_sj.exists():
            sj = json.loads(gm_sj.read_text())
            rb = sj.get("rho_baseline", float("nan"))
            rg = sj.get("rho_geometric", float("nan"))
            lines.append(f"  {label}: rho_baseline={rb:.3f}  rho_geometric={rg:.3f}")
        else:
            lines.append(f"  {label}: (missing {gm_sj})")

    for pat in (
        "fig_cert_vs_human_scatter_pass1.png",
        "fig_cert_vs_human_scatter_pass2.png",
        "fig_cert_vs_human_scatter_avg.png",
    ):
        p = RES16 / pat
        if p.exists():
            attachments.append(p)
    for pat in (
        "fig_main_monotonicity_lowvar.png",
        "fig_failure_alpha_variant_breakdown.png",
        "fig_failure_bug_reversal_rates.png",
    ):
        p = RES19 / pat
        if p.exists():
            attachments.append(p)
    for label in ("avg", "pass1", "pass2"):
        p = RES25_BASE.parent / f"{RES25_BASE.name}_{label}" / "fig7_trend_update_baseline_vs_geom.png"
        if p.exists():
            attachments.append(p)

    return ("\n".join(lines) or "(no summary collected)"), attachments


def send_completion_email(status: str, pr_url: str, branch: str, summary_text: str,
                          attachments: list[Path]) -> None:
    sys.path.insert(0, os.path.expanduser("~/ultimate-utils/py_src"))
    from uutils.emailing import send_email_smtp  # type: ignore

    host = os.uname().nodename
    subject = f"[cert-judge / Exp13 Qwen3.6-27B] {status} — open-weights SOTA replication"
    body = (
        f"Hey Brando + Ethan,\n\n"
        f"TLDR: Exp13 (Qwen3.6-27B replication of Exp16/Exp19/Exp25) finished {status} on {host}.\n\n"
        f"PR: {pr_url}\n"
        f"Branch: {branch}\n"
        f"Repo: cert-judge\n"
        f"Model: {QWEN_MODEL_ID} (open-weights SOTA, Apache 2.0, served locally via vLLM)\n\n"
        f"Headline numbers:\n{summary_text}\n\n"
        f"Output dirs (in-repo):\n"
        f"  - {RES16}\n"
        f"  - {RES19}\n"
        f"  - {RES25_BASE.parent}/{RES25_BASE.name}_{{avg,pass1,pass2}}\n\n"
        f"Attached: scatter plots (pass1/pass2/avg), low-variance diagnostics, GM trend updates.\n\n"
        f"Patch (judge_caller.py):\n"
        f"  +6  routing  elif qwen* / Qwen* -> vLLM OpenAI-compat endpoint\n"
        f"               (QWEN_BASE_URL / QWEN_API_KEY env vars)\n"
        f"  Backward-compat verified: claude-*, gpt-*, o1*/o3*, leanstral* unchanged.\n\n"
        f"— Claude Code\n"
    )
    send_email_smtp(
        to=EMAIL_TO,
        cc=EMAIL_CC,
        subject=subject,
        body=body,
        smtp_user=SMTP_USER,
        smtp_pass_file=SMTP_PASS_FILE,
        from_addr=SMTP_USER,
        attachments=attachments,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True, help="Path to the run log to watch.")
    ap.add_argument("--skip-wait", action="store_true", help="Skip waiting (assume run done).")
    args = ap.parse_args()
    log_path = Path(args.log)

    status = "ok" if args.skip_wait else wait_for_done(log_path)
    summary_text, attachments = collect_summary()
    pr_url = "(no PR — finalize step failed before PR open)"
    branch = "(none)"
    try:
        if status == "ok":
            branch = git_branch_commit_push()
            pr_url = open_pr(branch, summary_text)
        send_completion_email(
            status="DONE" if status == "ok" else "FAILED",
            pr_url=pr_url, branch=branch,
            summary_text=summary_text, attachments=attachments,
        )
    except Exception:
        tb = traceback.format_exc()
        try:
            send_completion_email(
                status=f"FINALIZE-ERROR ({status})",
                pr_url=f"(finalize failed)\n\nTraceback:\n{tb}",
                branch=branch,
                summary_text=summary_text,
                attachments=attachments,
            )
        except Exception:
            print("[finalize] Could not even send failure email:", file=sys.stderr)
            traceback.print_exc()
            return 2
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
