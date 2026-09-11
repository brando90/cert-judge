#!/usr/bin/env python3
"""Wait for the Exp12 (Leanstral) chained run to finish, then commit results,
open a PR assigned to ehersch, and email Brando + Ethan with key figures.

Run:
    PYTHONPATH=~/ultimate-utils/py_src \
        python3 experiments/12_leanstral/finalize.py \
        --log /tmp/exp12_leanstral_<TS>.log

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
RES16 = REPO / "experiments/archive/04_veribench_validation/results_exp16_leanstral_r3_median"
RES19 = REPO / "experiments/archive/04_veribench_validation/results_exp19_low_variance_replot_leanstral"
RES25 = REPO / "experiments/archive/04_veribench_validation/results_exp22_geometric_trust_index"

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
MAX_WAIT_SEC = 4 * 60 * 60  # 4 h hard ceiling


def wait_for_done(log_path: Path) -> str:
    """Poll the log until DONE marker or fatal error appears. Returns 'ok'|'err'."""
    start = time.time()
    last_size = -1
    while time.time() - start < MAX_WAIT_SEC:
        if not log_path.exists():
            time.sleep(POLL_SEC); continue
        text = log_path.read_text(errors="replace")
        if "=== [" in text and "DONE ===" in text:
            return "ok"
        if "Traceback" in text or "Error: " in text:
            tail = "\n".join(text.splitlines()[-40:])
            if "DONE ===" not in text:
                print(f"[finalize] Detected error in log:\n{tail}", file=sys.stderr)
                return "err"
        # Stagnation check: if size unchanged for 30 min and python is gone, treat as dead.
        sz = log_path.stat().st_size
        if sz == last_size:
            if not _python_still_alive():
                print("[finalize] Python process gone and log idle. Treating as error.", file=sys.stderr)
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
    """Create branch, commit results, push. Returns branch name."""
    branch = f"exp12-leanstral-{datetime.now():%Y%m%d-%H%M}"
    # Make sure we're starting from main
    run(["git", "checkout", "main"])
    run(["git", "pull"], check=False)
    # Create branch (allow existing)
    res = run(["git", "checkout", "-b", branch], check=False)
    if res.returncode != 0:
        run(["git", "checkout", branch])

    add_paths = [
        str(RES16.relative_to(REPO)),
        str(RES19.relative_to(REPO)),
        str((RES25 / "leanstral_r3_median_mono_stab_40_60_avg").relative_to(REPO)),
        str((RES25 / "leanstral_r3_median_mono_stab_40_60_pass1").relative_to(REPO)),
        str((RES25 / "leanstral_r3_median_mono_stab_40_60_pass2").relative_to(REPO)),
        "experiments/12_leanstral/finalize.py",
    ]
    # Also include the patched judge_caller.py if it has unstaged changes
    add_paths.append("experiments/02_neurips_reviews/utils/judge_caller.py")
    add_paths.append("experiments/archive/04_veribench_validation/results_exp16_leanstral_r3_median.MODEL_USED.txt")

    for p in add_paths:
        run(["git", "add", p], check=False)

    msg = (
        "exp12: Leanstral (labs-leanstral-2603) replication of Exp16/Exp19/Exp22-GM\n\n"
        "Adds Mistral routing in judge_caller (Leanstral via api.mistral.ai/v1) and\n"
        "the full multi-judge → human trend + low-variance replot + geometric cert-index\n"
        "reanalysis (avg/pass1/pass2) outputs for the Leanstral judge family.\n\n"
        "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>\n"
    )
    res = run(["git", "commit", "-m", msg], check=False)
    if "nothing to commit" in (res.stdout + res.stderr).lower():
        print("[finalize] Nothing to commit (results may already be tracked).")
    run(["git", "push", "-u", "origin", branch])
    return branch


def open_pr(branch: str, summary_text: str) -> str:
    """gh pr create assigned to ehersch. Returns PR URL."""
    title = "[Exp12] Leanstral (labs-leanstral-2603) replication of Exp16/Exp19/Exp22-GM"
    body = (
        "## Summary\n"
        "- Runs Exp16 (multi-judge cert→human trend), Exp19 (low-variance replot), and Exp22-GM\n"
        "  (geometric cert-index, avg/pass1/pass2) with **Leanstral** (`labs-leanstral-2603`) as the\n"
        "  primary judge family. gpt-4o-mini retained as cross-family judge.\n"
        "- Adds Mistral routing in `experiments/02_neurips_reviews/utils/judge_caller.py`\n"
        "  (additive `elif` for `leanstral`/`labs-leanstral` model prefixes; no impact on existing\n"
        "  `claude-*`/`gpt-*`/`o*` paths — verified by routing test + e2e smoke).\n\n"
        f"## Headline numbers (auto)\n```\n{summary_text}\n```\n\n"
        "## Test plan\n"
        "- [ ] Verify all three steps' outputs exist (summary.json, fig_*scatter*.png, fig7_*.png)\n"
        "- [ ] Spot-check `MODEL_USED=labs-leanstral-2603` in `*.MODEL_USED.txt`\n"
        "- [ ] Compare ρ_baseline vs ρ_geometric per pass (avg / pass1 / pass2)\n"
        "- [ ] Confirm gpt-4o-mini judges still work (backward-compat smoke in PR description above)\n\n"
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
        # Maybe PR already exists; try to fetch URL.
        view = run(["gh", "pr", "view", "--json", "url", "-q", ".url"], check=False)
        if view.returncode == 0 and view.stdout.strip():
            return view.stdout.strip()
        raise RuntimeError(f"gh pr create failed:\n{res.stdout}\n{res.stderr}")
    url = res.stdout.strip()
    return url


def collect_summary() -> tuple[str, list[Path]]:
    """Return (summary_text, list_of_attachment_paths)."""
    lines: list[str] = []
    attachments: list[Path] = []
    summary_p = RES16 / "summary.json"
    if summary_p.exists():
        s = json.loads(summary_p.read_text())
        lines.append(f"Exp16 summary keys: {list(s.keys())[:10]}")
        # Best-effort numeric extract
        for k in ("rho_baseline", "rho_geometric", "trend_v1", "trend_v2", "rho_pass1", "rho_pass2", "rho_avg"):
            if k in s:
                lines.append(f"  {k}: {s[k]}")
    else:
        lines.append("(summary.json missing)")

    for label in ("avg", "pass1", "pass2"):
        gm_dir = RES25 / f"leanstral_r3_median_mono_stab_40_60_{label}"
        gm_sj = gm_dir / "summary.json"
        if gm_sj.exists():
            sj = json.loads(gm_sj.read_text())
            lines.append(f"Exp22-GM [{label}] summary keys: {list(sj.keys())[:10]}")

    # Attach key plots
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
        p = RES25 / f"leanstral_r3_median_mono_stab_40_60_{label}" / "fig7_trend_update_baseline_vs_geom.png"
        if p.exists():
            attachments.append(p)

    return ("\n".join(lines) or "(no summary collected)"), attachments


def send_completion_email(status: str, pr_url: str, branch: str, summary_text: str,
                          attachments: list[Path]) -> None:
    sys.path.insert(0, os.path.expanduser("~/ultimate-utils/py_src"))
    from uutils.emailing import send_email_smtp  # type: ignore

    host = os.uname().nodename
    subject = f"[cert-judge / Exp12 Leanstral] {status} — labs-leanstral-2603"
    body = (
        f"Hey Brando + Ethan,\n\n"
        f"TLDR: Exp12 (Leanstral replication of Exp16/Exp19/Exp22-GM) finished {status} on {host}.\n\n"
        f"PR: {pr_url}\n"
        f"Branch: {branch}\n"
        f"Repo: cert-judge\n"
        f"Model: labs-leanstral-2603 (Mistral hosted, $0 Labs tier)\n\n"
        f"Headline numbers:\n{summary_text}\n\n"
        f"Output dirs:\n"
        f"  - {RES16}\n"
        f"  - {RES19}\n"
        f"  - {RES25}/leanstral_r3_median_mono_stab_40_60_{{avg,pass1,pass2}}\n\n"
        f"Attached: scatter plots (pass1/pass2/avg), low-variance diagnostics, GM trend updates.\n\n"
        f"Patch summary (judge_caller.py):\n"
        f"  +5  constants  MISTRAL_KEY_PATH, MISTRAL_BASE_URL\n"
        f"  +9  helper     _get_mistral_key()\n"
        f"  +4  routing    elif leanstral/labs-leanstral -> Mistral OpenAI-compat endpoint\n"
        f"  Backward-compat verified: claude-*, gpt-*, o1*/o3* unchanged.\n\n"
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

    if not args.skip_wait:
        status = wait_for_done(log_path)
    else:
        status = "ok"
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
        # Always email even if PR/git failed — Brando wants to know.
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
