# Experiment 58: frozen-analysis audit and verified project status

**Doc link:** <https://github.com/brando90/cert-judge/blob/codex/e58-frozen-analysis-fixes/experiments/58_open_weight_judges_on_e39_e42_probes/RESULTS_analysis_audit.md>

**TLDR:** The E58 analysis now retains missing units, distinguishes unavailable statistics from failed gates, computes the promised failure sensitivity, and rejects incompatible or unverifiable inputs. Its repaired implementation exactly reproduces the saved E60 primary association on 26 configurations as an explicitly labelled compatibility dry run; this is not new E58 evidence.

[Google companion](https://docs.google.com/document/d/1YqbZNnLQt2vmsmDEiltRjPjR6lm7cAgWU9llFZsBOeQ/edit) · [machine-readable reproduction receipt](results/audit_10-26-2026/REPRODUCTION.json) · [actual E58 partial-smoke receipt](results/audit_10-26-2026/MERCURY1_SMOKE.json) · [full E60 reproduction](results/audit_10-26-2026/E60_FULL_REPRODUCTION.json) · [checkpoint](CKPT_analysis_audit.md).

## Project status as verified on 10-26-2026

The statement that the project has no results because E58 is still queued is stale. The repository's main revision `0c21bf1` already contains pull requests 78–80: E58's implementation and the completed E59/E60 studies. During this audit, `523ef0e` added pull request 81's mercury1 E58 smoke log, and [PR 83](https://github.com/brando90/cert-judge/pull/83) published a separate four-judge FarmShare partial result at revision `63ade61fba704d7fd50779b35ea7531f8e66a052`. The coworker has also acknowledged separate ownership of experiment `61_open_weight_judges_on_e43_gaming_candidates`; its latest reservation covers mercury2 GPUs 0–7 while this audit uses one CPU on skampere1.

| Experiment | Verified evidence | Interpretation |
|---|---|---|
| `58_open_weight_judges_on_e39_e42_probes` | Sherlock runner online; no E58/certjudge-named job found in current `squeue` or `sacct` since 10-20-2026; documented `$SCRATCH/e58` and `~/e58` absent. No original E58 harvest found in these Sherlock locations. New [mercury1 run log](results/RUN_LOG_mercury1.md) records a 12:35 PDT Gemma3-4B D0 smoke: 20 generated cells, 19 measured and 1 parse error. | PR 83 reports 72/234 FarmShare harvests covering 4 models × 9 prompts. The full 117-unit result remains unavailable. Mercury1 is a distinct smoke; its hardware/serving deviation remains visible. |
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

## Independent full E60 reproduction

The complete saved analysis of `60_open_weight_proxy_index_rigor_round`, including its separately executed `--extra` sensitivity appendix, also reproduces exactly: **2,567 matching scalar values, zero differences**, excluding only the three input-directory metadata fields. Comparisons use no numerical tolerance; dictionary key order is irrelevant and paired non-finite NaN values compare equal. This verifies implementation reproducibility, not compliance with every protocol sentence.

The original E59/E60 scripts ran unchanged on skampere1 against source-hash-verified archives with 47 old-A, 9 old-B, 26 new seed-0, and 36 seed-1 harvests. The core command used 10,000 draws and 200 splits, finishing at 12:56:11 PDT; the saved additional sensitivity finished at 13:01:27 PDT, both exit 0. Each command was capped at one CPU thread, 3 GiB virtual memory, and 1,800 seconds, with zero model calls. The stored plain new-judge gate passes; the inherited combined verdict is inconclusive because its clustered component is unavailable. The model-robustness condition passes and FIT-ROBUST is false, exactly as saved.

The first attempt supplied an extracted archive's parent rather than its nested `seed0`/`seed1` run root. E60 silently accepted this and produced no new units. That invalid attempt is retained in the execution record and is not counted as a reproduction. [PR 84](https://github.com/brando90/cert-judge/pull/84) fixes only this input boundary: every explicitly supplied directory must contain harvest JSON files; omitted optional directories remain allowed. Its eight tests pass, six fail against the previous loader, and the combined E58/E60 suite passes **40 tests with zero skips** under Python 3.12. The tests isolate E59's panel-registration side effect from E58 tests.

[Exact comparison receipt](results/audit_10-26-2026/E60_FULL_REPRODUCTION.json) · [reusable comparison command](results/audit_10-26-2026/compare_e60_reproduction.py).

## Actual E58 partial-harvest dry run

After PR 81 appeared during the audit, the mercury1 smoke harvest was copied read-only from `/lfs/mercury1/0/brando9/e58/runs/smoke/harvest/e39/gemma3_4b__D0.json`. The source and local copy both hash to `424a9d9e51e2c36f65f3f944a8f27e97dfd60bbdea5b4e11e19a9d6f56f38399`. Its 521 declared cells contain 19 measured, 1 parse error, 56 deterministic, 9 unmeasured extraction, and 436 unmeasured infrastructure cells. The recorded runtime contract matches; its vLLM 0.11.0 / torch 2.8.0+cu128 / RTX A4000 serving-stack deviation remains recorded in the source and the receipt.

The ordinary 10,000-draw settings with `--dry-run` retain 117 E39 units, only one with a present harvest, zero computable criterion/index pairs, and 117 unavailable E42 units. Both primary gates correctly report `NOT_COMPUTABLE`. The audit did not retry or generate any cells. This is the requested dry run on an actual E58 partial result, independently of the E60 compatibility check.

## Newly published four-judge FarmShare result

[PR 83](https://github.com/brando90/cert-judge/pull/83), revision `63ade61fba704d7fd50779b35ea7531f8e66a052`, reports 36 E58 configurations (Qwen3 4B/8B/14B and Llama 3.1 8B), with 72 of 234 harvest files. The named source is FarmShare `~/e58/runs/main`, with collected-archive SHA-256 `3fd6e86cb2b1b68de79c9c7dfb31e0b63dbf111ae210eddea5c4fc0767c486d7`. These are the coworker's collection receipts; they were not part of the earlier Sherlock location search or the separate mercury1 smoke.

Its committed analysis reports Spearman **0.4333333333 [0.1201011378, 0.6759870732], p-val=0.0051994801** on 35 computable configurations from 4 models (configuration bootstrap and one-sided positive-association permutation, 10,000 draws, seed 39). This partial-panel plain gate fails the frozen ≥0.45 association threshold. The model-clustered subset has 3 complete models / 27 configurations: **0.3986568987 [0.3498622590, 0.6333333333], p-val=0.3279672033** (whole-model bootstrap and block permutation, 10,000 draws, seed 58), also FAIL. Neither is the full-panel verdict. The existing semantic screen has 5 PASS, 30 FAIL, and 1 NOT_COMPUTABLE among 36 observed configurations.

A bounded one-CPU check recomputed both gate objects from all 36 published processed-unit records using the repaired E58 analysis; the plain statistic, plain PASS flag, clustered statistic and clustered PASS flag all match exactly ([receipt](results/audit_10-26-2026/E58_FARMSHARE_GATE_CHECK.json)). This does not verify raw scores or recorded serving settings.

Direct Mac SSH to FarmShare returned an authentication failure, and OnDemand showed the Stanford login page. The coworker was asked to supply the existing collected archive through SNAP. Until that archive is retrieved, runtime metadata and raw-cell identities for this four-judge result remain unverified by this audit. Source processed-analysis SHA-256: `cfe27ae1da9ed2316e8057c5b4743f0af96a0186dcd32e71f9cdbbd9eb3e67fd`.

## Unresolved protocol gaps, preserved rather than re-decided

1. **E58 §5 uncertainty wording:** the protocol says “task-bootstrap CI” for the across-judge association, while its explicitly imported frozen E39 `association` function bootstraps judge configurations. The per-judge criterion bootstraps tasks. This patch reports the implemented resampling unit and changes neither function.
2. **E58 §7 unavailable deletion covariate:** the prescribed missing-specification ladder has one score per deletion level, while the existing covariate code requires at least two repeats per retained level. After fixing its probe source, deletion covariates remain unavailable. Resolving that design would require a separately documented decision, not invented repeats.
3. **E60 §3 seed discrepancy:** `analyze60.partA` calls `analyze59.gate_verdict`, which uses seed 39; E60's prose says seed 60. Exact reproduction confirms the saved output corresponds to the current implementation. No post-result seed substitution was made.
4. **E60 §5 learner selection discrepancy:** the protocol requires choosing L2/L3 by inner validation, but `partC` selects the larger pooled held-out Spearman and labels it `best_of_L2_L3_by_loto`. The code explicitly acknowledges that inner learner selection was not tracked. Its stored FIT-ROBUST verdict is false, but that does not remove the discrepancy. Saved results and claims remain unchanged pending reconciliation with the owner.
5. **E60 interval settings:** §5 says seed 60 and 10,000 task-bootstrap draws for the reported metrics. The imported `analyze59.evaluate` uses seed 59, and caps Pearson, Kendall and intraclass-correlation intervals at 2,000 draws. The full reproduction matches this implementation; seeds and draw counts were not substituted after results.
6. **E60 pooled denominators:** the saved report combines the 87-computable-unit point estimate across 10 models with a clustered p-value computed on a different subset: 8 complete models × 9 prompts = 72 units. The full-set Spearman is 0.5833272581 [0.4137022278, 0.7128579245], p-val=0.0000999900 (configuration bootstrap and positive-association permutation, 10,000 draws, seed 39). The 72-unit clustered estimate is 0.5637018458 [0.2913710158, 0.6805522035], p-val=0.0031996800 (whole-model bootstrap and block permutation, 10,000 draws, seed 58). The report must not present these as one identically scoped statistic.
7. **Experiment inventory:** the layout checker fails on untouched main because experiments 59 and 60 were not registered in `experiments/archive/layout.json`. This audit does not move their data or imply they are still running.

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

**TLDR-end:** [cert-judge: frozen-analysis audit] E58 implementation defects are repaired and tested without new analysis choices; saved later results exist and both the 26-unit primary statistic and the complete saved E60 analysis are exactly reproduced. E58 full-panel execution and the listed protocol discrepancies remain to reconcile with the coworker; the newly published four-judge FarmShare partial result is distinguished from the separate mercury1 smoke.
