#!/usr/bin/env python3
"""Email Brando + Ethan a summary of the Exp13 Qwen replication run.

Per agents-config Hard Rule 23 (uutils SMTP) and Trigger Rule 14
(experiment-completion email).
"""
import json
import os
import sys
from pathlib import Path

# Drop any leaked PYTHONPATH
for k in ("PYTHONPATH", "PYTHONHOME"):
    os.environ.pop(k, None)

UU_PATH = os.path.expanduser("~/ultimate-utils/py_src")
if UU_PATH not in sys.path:
    sys.path.insert(0, UU_PATH)

from uutils.emailing import send_email_smtp

REPO = Path(__file__).resolve().parents[3]
EXP_DIR = REPO / "experiments" / "13_qwen_replication_exp16_exp19"
EXP16_OUT = EXP_DIR / "results" / "exp16_qwen_r3_median"
EXP19_OUT = EXP_DIR / "results" / "exp19_low_variance_replot_qwen"
EXP25_BASE = EXP_DIR / "results" / "exp25_geometric_qwen_r3_median_mono_stab_40_60"


def _format_summary() -> str:
    s = EXP16_OUT / "summary.json"
    if not s.is_file():
        return f"(no summary.json yet at {s})"
    j = json.loads(s.read_text())
    lines = []
    lines.append(f"experiment={j.get('experiment')}")
    lines.append(f"n_judges={j.get('n_judges')} n_union_rows={j.get('n_union_rows')}")
    lines.append("")
    lines.append("Trend by label set (cert v2 vs human Spearman):")
    for ls, t in (j.get("trend_by_set") or {}).items():
        v2 = t.get("trend_v2", {})
        lines.append(
            f"  {ls}: r={v2.get('spearman_r', float('nan')):.3f} "
            f"CI=[{v2.get('spearman_ci_lo', float('nan')):.3f},{v2.get('spearman_ci_hi', float('nan')):.3f}] "
            f"perm_p={v2.get('spearman_perm_p', float('nan')):.4f}"
        )
    lines.append("")
    lines.append("Per-judge head:")
    for r in (j.get("judge_rows") or [])[:8]:
        lines.append(
            f"  - {r.get('judge_id')}: ident={r.get('identity_mean'):.2f} "
            f"bug_r={r.get('bug_spearman_r'):.2f} "
            f"flip={r.get('flip_rate'):.2f} cert_v2={r.get('cert_index_v2'):.2f}"
        )
    return "\n".join(lines)


def _format_geom_summary() -> str:
    lines = []
    for ls in ("avg", "pass1", "pass2"):
        sj = EXP25_BASE.parent / f"{EXP25_BASE.name}_{ls}" / "summary.json"
        if not sj.is_file():
            lines.append(f"  {ls}: (missing {sj})")
            continue
        j = json.loads(sj.read_text())
        rb = j.get("rho_baseline", float("nan"))
        rg = j.get("rho_geometric", float("nan"))
        lines.append(f"  {ls}: rho_baseline={rb:.3f} rho_geometric={rg:.3f}")
    return "\n".join(lines)


def main() -> int:
    subject = "[cert-judge] Exp13 Qwen3.6-27B replication of Exp16/Exp19/Exp25 — DONE"
    body_lines = [
        "TLDR: Full Qwen3.6-27B (open-weights, served via vLLM on snap)",
        "replication of the Exp16 → Exp19 → Exp25 pipeline.",
        "",
        "Pipeline:",
        "  1) Exp16 (multi-judge cert-vs-human trend)",
        "  2) Exp19 (low-variance replot)",
        "  3) Exp25 (geometric trust-index reanalysis: avg/pass1/pass2)",
        "",
        f"Repo dir: {EXP_DIR}",
        f"Exp16 out: {EXP16_OUT}",
        f"Exp19 out: {EXP19_OUT}",
        f"Exp25 base: {EXP25_BASE}_<label>",
        "",
        "===== Exp16 summary =====",
        _format_summary(),
        "",
        "===== Exp25 geometric =====",
        _format_geom_summary(),
        "",
        "Artifacts (in-repo):",
        f"  {EXP16_OUT}/summary.json",
        f"  {EXP16_OUT}/judge_rows.csv",
        f"  {EXP16_OUT}/detail_rows.csv",
        f"  {EXP16_OUT}/fig_cert_vs_human_scatter_{{pass1,pass2,avg}}.png",
        f"  {EXP19_OUT}/fig_main_monotonicity_lowvar.png",
        f"  {EXP19_OUT}/fig_failure_alpha_variant_breakdown.png",
        f"  {EXP19_OUT}/fig_failure_bug_reversal_rates.png",
        f"  {EXP25_BASE}_<label>/summary.json",
        "",
        "— Claude Code (snap)",
    ]
    body = "\n".join(body_lines)

    to = "brando.science@gmail.com"
    cc = "brando9@stanford.edu, brando9@cs.stanford.edu, herschethan@gmail.com"

    send_email_smtp(
        to=to,
        cc=cc,
        subject=subject,
        body=body,
        smtp_user="brandojazz@gmail.com",
        smtp_pass_file="~/keys/gmail_app_password.txt",
        from_addr="brandojazz@gmail.com",
    )
    print(f"emailed: to={to} cc={cc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
