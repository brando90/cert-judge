# Historical measured-score tests of information-inspired judge properties

**Doc link:** [experiment](https://github.com/brando90/cert-judge/tree/codex/cj-e46-tvdmi-properties/experiments/archive/46_tvdmi_inspired_properties_cached_judge_validation).
**Summary:** Three total-variation-distance mutual-information-inspired properties are defined in [PROTOCOL.md](PROTOCOL.md). A zero-inference historical-data run tests semantic discrimination, repeat information and direction-gated deletion information. Set N remains untouched.

Status: COMPLETE and archived 10-08-2026; corrected offline historical-cache analysis, awaiting landing.
Definitions are authoritative for the separate experiment 47 simulated-rater sandbox, which this experiment does not run.
Sources: measured caches from experiments 39 and 42, fixed selection pool from 44, published current human ratings from 45.
The historical test analysis uses 29/30 shared candidate files across 10 tasks; it is exploratory reuse, not prospective validation.
`deletion_tvd` is unavailable because the cached `ms_gold` ladders have one repeat per level while the frozen protocol requires two; see [ERRATA.md](ERRATA.md) for the frozen wording correction that these ladders remove theorem/lemma declarations, not unit tests.
See [the measured report](RESULTS_information_properties.md), [results.md](results.md), [CKPT_e46.md](CKPT_e46.md), and [PAPER_SUMMARY.md](PAPER_SUMMARY.md).

Start with [the interpretation and next steps](READOUT.md) for readable comparison tables and the connection to the existing set-N round.

Publication portability note (10-08-2026): the measured report was renamed byte-for-byte from `RESULTS.md` to `RESULTS_information_properties.md` because `RESULTS.md` collides with the required live ledger `results.md` on case-insensitive filesystems. The frozen analysis code and machine-readable results remain unchanged. Exact historical reproduction runs on Stanford Network Analysis Project Linux at the recorded code revision and retains the original output filename; do not reintroduce the colliding name when publishing a regenerated report.
