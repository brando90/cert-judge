# Experiment 58: frozen-analysis audit and verified project status

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex/e58-frozen-analysis-fixes/experiments/58_open_weight_judges_on_e39_e42_probes/RESULTS_analysis_audit.md>

**TLDR:** The E58 analysis now retains missing units, distinguishes unavailable statistics from failed gates, computes the promised failure sensitivity, and rejects incompatible or unverifiable inputs. Its repaired implementation exactly reproduces the saved E60 primary association on 26 configurations as an explicitly labelled compatibility dry run; this is not new E58 evidence.

[Google companion](https://docs.google.com/document/d/1YqbZNnLQt2vmsmDEiltRjPjR6lm7cAgWU9llFZsBOeQ/edit) · [machine-readable reproduction receipt](results/audit_10-26-2026/REPRODUCTION.json) · [checkpoint](CKPT_analysis_audit.md).

## Project status as verified on 10-26-2026

The statement that the project has no results because E58 is still queued is stale. The repository's main revision `0c21bf1` already contains pull requests 78–80: E58's implementation and the completed E59/E60 studies. A status message is not an execution receipt.

| Experiment | Verified evidence | Interpretation |
|---|---|---|
| `58_open_weight_judges_on_e39_e42_probes` | Sherlock runner online; no E58/certjudge-named job found in current `squeue` or `sacct` since 10-20-2026; documented `$SCRATCH/e58` and `~/e58` absent. No original E58 harvest found in the inspected repository or these locations. | Original 117-unit E58 completion is unverified. An unrecognized job name or different location is not ruled out; coworker was asked for exact receipts. |
| `59_open_weight_proxy_index_and_frontier_fit` | `results/STATUS.md` records FINAL 10-25-2026 04:30; final report committed; SNAP harvest archives exist. | Results exist; the README's older “running/pending” rows are stale. |
| `60_open_weight_proxy_index_rigor_round` | Committed seed-0 archive contains 26 configurations; seed-1 archive contains 36 repeat configurations. SNAP lane logs end successfully on 10-25-2026 at 13:06 and 14:00 PDT. | Saved results exist. These runs use later registered settings and cannot be relabelled as original E58. |

The Sherlock check used the signed-in private runner, not an assumption that direct SSH failure means VPN is needed. SNAP access worked through the official gateway. No graphics processor or provider call was launched in this audit.

## Fixes against the existing E58 protocol

| Protocol obligation | Previous behavior | Repair |
|---|---|---|
| §3, §5–6: retain every declared model/prompt unit | Globbed only existing harvest files; an empty run produced zero units, and the semantic screen disappeared. | Both panels always contain all 117 declared units. Missing harvests remain unmeasured with no invented scores. |
| §5: report what is computable | Missing correlations were reported as FAIL. | `NOT_COMPUTABLE` is distinct from PASS/FAIL; machine-readable PASS fields are null when unavailable. Existing numerical thresholds remain unchanged. |
| §7: deletion total-variation-distance mutual-information covariate | Read `bm_gold` implementation-bug ladders. | Reads the prescribed `ms_gold` deletion ladders. No extra repeats or new calls. |
| §10: report with and without models having >20% incomplete/parse-error cells | Sensitivity analysis absent. | Flags whole models using failed cells / all declared E39 + E42 cells; reports both versions and their denominators. Missing cells remain missing, not parse errors. |
| §1, §9: frozen, collected inputs | Only selection-file hash checked; arbitrary uncollected paths accepted. | Checks both named E39 hashes, collection manifest hashes and coverage, frozen unit/cell identities, normalized finite scores and counts. Recorded runtime settings must match for ordinary analysis. |
| §5–9: visible uncertainty and coverage | Several computed fields omitted from Markdown. | Adds uncertainty intervals, all unit coverage/status rows, bridge mean absolute difference and missing prompts; full details remain in JSON. |
| Fixed-seed reproducibility | Adding missing units could reorder observed configurations. | Retains original lexical filename order; regression test protects bootstrap/permutation input order. |

`--dry-run` allows provisional or runtime-mismatched inputs, labels them prominently, and writes separate `_DRY_RUN` files. It never overwrites ordinary `ANALYSIS.json`. Reduced draw counts require this flag. A supplied manifest is always verified, even for a dry run.

The protocol, model registry, generation and parsing code, E39 numerical definitions, prompts, thresholds and seeds are unchanged. Runtime checking verifies recorded metadata; it does not independently attest loaded weights or replay generation.

## Verification and saved-data reproduction

The complete suite passes **32 tests, zero skipped**. The first five targeted checks failed against the prior implementation before their fixes. Rebuilding prompts reproduced **9,927/9,927** hashes (E39 4,689; E42 5,238), with 249 valid probes. The original committed rebuild receipt was preserved byte-for-byte.

A one-CPU, model-free SNAP dry run used the 26 E60 seed-0 harvests already committed in `60_open_weight_proxy_index_rigor_round/results/final_2026-10-25/harvest/e60_harv0.tgz`. It ran 10,000 draws with the frozen E58/E39 implementation and exited 0. The entire primary-statistic object—including unit order, point estimates, interval endpoints and permutation p-value—matches E60's saved `partA.gate.plain` exactly:

| Quantity | Reproduced value | Scope |
|---|---:|---|
| Spearman rank association | 0.6998290598290599 | 26 model/prompt configurations across 3 models; each criterion uses the same 45 validation + test items |
| 95% interval | [0.45554789800137835, 0.8205568924028875] | Bootstrap over judge configurations, 10,000 valid draws, seed 39; correlated prompts are not independent model clusters |
| One-sided permutation p-value | 0.00009999000099990002 | Positive association null test, 10,000 draws, seed 39 |
| Kendall association | 0.47692307692307695 | Same 26 configurations; no separate interval computed |
| Pearson association | 0.6624519234998569 | Same 26 configurations; no separate interval computed |
| Plain gate | PASS | Existing criterion: Spearman ≥0.45 and p<0.05 |
| Model-clustered statistic | NOT_COMPUTABLE | Only 2 complete nine-prompt models; Qwen3-32B lacks H2 in the new-unit subset; existing code requires 3 complete models |

The primary result is a ranking association, not an absolute score-agreement claim. The compatibility run retains 117 declared units, 26 with observations, and 117 unavailable semantic-screen units. It identifies **42 runtime-field mismatches** across 26 present harvests (for example, Qwen3-32B's later fp8/one-device/32,768-token settings). It therefore cannot produce an ordinary E58 result. Full source and output hashes are in the receipt.

## Unresolved protocol gaps, preserved rather than re-decided

1. **E58 §5 uncertainty wording:** the protocol says “task-bootstrap CI” for the across-judge association, while its explicitly imported frozen E39 `association` function bootstraps judge configurations. The per-judge criterion bootstraps tasks. This patch reports the implemented resampling unit and changes neither function.
2. **E58 §7 unavailable deletion covariate:** the prescribed missing-specification ladder has one score per deletion level, while the existing covariate code requires at least two repeats per retained level. After fixing its probe source, deletion covariates remain unavailable. Resolving that design would require a separately documented decision, not invented repeats.
3. **E60 §3 seed discrepancy:** `analyze60.partA` calls `analyze59.gate_verdict`, which uses seed 39; E60's prose says seed 60. Exact reproduction confirms the saved output corresponds to the current implementation. No post-result seed substitution was made.
4. **E60 §5 learner selection discrepancy:** the protocol requires choosing L2/L3 by inner validation, but `partC` selects the larger pooled held-out Spearman and labels it `best_of_L2_L3_by_loto`. The code explicitly acknowledges that inner learner selection was not tracked. Its stored FIT-ROBUST verdict is false, but that does not remove the discrepancy. Saved results and claims remain unchanged pending reconciliation with the owner.
5. **Experiment inventory:** the layout checker fails on untouched main because experiments 59 and 60 were not registered in `experiments/archive/layout.json`. This audit does not move their data or imply they are still running.

All E59/E60 human comparisons still use the existing **75 Claude 3.7 Sonnet zero-shot items across 25 tasks**, not fresh frontier-agent human ratings. Those human data remain the substantive next evidence need; this audit does not weaken or rewrite the paper's claims.

## Reproduce or continue

Run from the repository root using the existing `uv` environment and rebuilt prompts:

```bash
E58_VERIBENCH_REPO=/Users/brandomiranda/veribench /Users/brandomiranda/uv_envs/cert-judge/bin/python -m pytest -q experiments/58_open_weight_judges_on_e39_e42_probes/tests
```

For collected original E58 outputs, after `slurm/collect.sh`:

```bash
python experiments/58_open_weight_judges_on_e39_e42_probes/scripts/analyze58.py --run /path/to/collected/runs/main --out /path/to/analysis
```

For partial inputs, use the same command with `--dry-run`; to inspect an empty panel, supply an existing empty directory. Keep E59/E60 diagnostics labelled and separate. No command here launches inference.

**TLDR-end:** [cert-judge: frozen-analysis audit] E58 implementation defects are repaired and tested without new analysis choices; saved later results exist and the 26-unit primary statistic is exactly reproduced. Original E58 execution receipts and the listed protocol discrepancies remain to reconcile with the coworker.
