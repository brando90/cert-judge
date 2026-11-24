# Experiment 67: re-run of the CertJudge panel with the VeriBench-team ratings, RPS / CE / TVD first (start 11-24-2026)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/67_new_vb_team_ratings_rps_ce_tvd_rerun_of_the_certjudge_panel/README.md>

**TLDR:** Brando asked (11-24-2026) whether the incoming VeriBench-team ratings make the CertJudge results more trustworthy and whether proper scores (RPS, CE, TVD) should sit next to correlation. This folder holds the pre-registration ([PREREG.md](PREREG.md)), scripts, results and [RESULTS.md](RESULTS.md). Zero judge calls, $0 out of pocket; results in [RESULTS.md](RESULTS.md) (11-24-2026).

- Run: `~/.venvs/sci/bin/python scripts/run_old.py` then `scripts/run_new.py` (needs `inputs_local/new_ratings/<id>.tsv`, the raters' Sheets exported as TSV; not committed, aggregates only).
- Judge scores on the 100 new files do not exist yet. Plan for them (not run): 3 judge series x 3 repeats x 100 files = 900 calls; at the experiment 21 rate (about $20.2 per 675 calls at list prices) that is about $27 at list prices, $0 out of pocket on plan lanes; to be started after the next rating wave (Wed 11-25-2026 6 PM PT).
- Related: [experiment 51 (archive)](../archive/51_certjudge_rescore_rps_ce_tvd_nov2026), [experiment 41](../41_paper_panel_provenance_audit_and_vb_expert_label_rescore/REPORT.md), trustworthy-theorem-judges experiments 09 and 22.
