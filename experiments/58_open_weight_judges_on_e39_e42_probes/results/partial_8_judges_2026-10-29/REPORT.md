# E58 partial result: 8 of 13 open-weight judges (2026-10-29)

Superseded 2026-10-30 by `../full_13_judges_2026-10-30/REPORT.md` (13 of 13 judges, gate PASS).

## Gate (E39's: rho >= 0.45 and p < 0.05)

The frozen index `C_ms_gold` does not pass E39's gate on the 8 judges that finished (72 units, 70 with both numbers; `scripts/analyze58.py` from main, unchanged, 10,000 draws). This is a partial panel, not the final E58 verdict: the 5 two-GPU judges produced no output (vLLM tensor-parallel hang on FarmShare) and are retained as `unmeasured_infra`, never dropped.

| Test | n | Spearman | p | 95% CI | Gate |
|---|---:|---:|---:|---|---|
| plain permutation | 70 units | 0.269 | 0.0132 | 0.035 to 0.475 | FAIL |
| model-clustered | 6 models | 0.267 | 0.1854 | -0.194 to 0.546 | FAIL |

The clustered test uses only models whose 9 prompt units all have both numbers: 6 of the 8. Llama 3.1 8B (H0) and Gemma 3 4B (H2) each have one unit with no computable criterion (under 90% of items scored), so they drop out of the clustered test only; the plain test keeps their other units.

Section 10 failure sensitivity: no model has more than 20% parse-error or incomplete cells (max Llama 3.1 8B, 2.6%), so nothing is flagged and the verdict is the same with and without flagged models.

## Collection

- Source: FarmShare `~/e58/runs/main`, collected with `slurm/collect.sh`. Tarball `e58_results.tgz`, 74,062,812 B, sha256 `faf4ecb469f6420b97e2ec792c2ef5867d6481249b6e2edf81134108ceb452a3` (identical on FarmShare, skampere1 and the analysis host). Analysis input manifest: VERIFIED, 450 files, manifest sha256 `f23482e77e92e3b5cc0c942674a53375bb69678e8d11c65a16bb39cd368c9927`; recorded runtime settings MATCH the contract (0 mismatches).
- Present: 144 of 234 harvests (8 models x e39/e42 x 9 prompts). Missing: 90 = qwen3_32b, qwen36_27b, llama33_70b_awq, gemma3_27b, olmo3_32b (`MISSING.json`).
- Why missing: Slurm array 1862861 (tasks 3, 4, 6, 9, 11) hit the 2 h partition limit with zero output; every log, including resubmits 1862862, 1864455, 1876088 and 1893305, ends in a repeating vLLM "No available shared memory broadcast block found in 60 seconds" (tensor-parallel hang on 2 GPUs). A plain resubmit cannot work. The 5 models are being run on another route (follow-up task); until then the Qwen3.6 bridge check (section 8 of the protocol) is `missing`.
- The 4-model partial of 2026-10-26 (`partial_4_judges_2026-10-26`) is contained in this run: the Qwen3 4B/8B/14B and Llama 3.1 8B rows are identical.
- Mercury copies of gemma3_4b (tgz sha 071fd456...ef185d) and olmo3_7b (sha b8413d68...3da67) are replicates only; the FarmShare run is the frozen one-run-per-model.

## Per judge (mean over the 9 prompts; criterion = Spearman with the three-expert coverage ratings on the 45 held-out items)

| Judge | criterion Spearman | C_ms_gold | failed cells / declared |
|---|---:|---:|---:|
| Qwen3 14B | 0.349 | 0.864 | 5 / 9927 |
| Qwen3 4B | 0.293 | 0.715 | 6 / 9927 |
| OLMo 3 7B | 0.260 | 0.460 | 71 / 9927 |
| Llama 3.1 8B | 0.219 | 0.545 | 254 / 9927 |
| Gemma 3 12B | 0.214 | 0.297 | 61 / 9927 |
| gpt-oss-20b | 0.194 | 0.881 | 203 / 9927 |
| Qwen3 8B | 0.174 | 0.770 | 23 / 9927 |
| Gemma 3 4B | 0.130 | 0.417 | 135 / 9927 |

Per-prompt criterion varies far more than the per-model mean (for example Gemma 3 12B D0 0.741, H0 0.016; gpt-oss-20b H1 0.734, P4 -0.279); per-unit rows with item coverage and cell status counts are in `RESULTS_open_weight_judges.md` and `ANALYSIS.json`. gpt-oss-20b has the highest `C_ms_gold` (0.881) and a below-median criterion (0.194): a high index with a weak criterion is one reason the plain association is low.

## Always reported

- PTI_v0_frozen: computable on 57 of 117 units (60 NOT_COMPUTABLE, 45 of them the missing models); association not computed (n/a).
- TI_var (E39 frozen normalization): n 71, Spearman 0.100 [-0.111, 0.304], p 0.211, no gate applied.
- E42 semantic screen: 10 PASS, 60 FAIL, 47 NOT_COMPUTABLE (the missing models) of 117 units. Descriptive association of components with the criterion: weakening 0.560, overconstraint 0.425, vacuity 0.252, formatting -0.565 (71 units).
- Scale within family: only Qwen3 (4B, 8B, 14B), Gemma 3 (4B, 12B), OLMo 3 (7B) and Llama 3 (8B) have points; the 27B-70B points are missing. No monotonic trend in the Qwen3 points (0.293, 0.174, 0.349); descriptive only.
- Exploratory TVD-MI (does not freeze E49; W-365 stays Brando's call): repeat TVD Spearman 0.009 (n 70); deletion TVD not computable (the deletion covariate needs at least two repeats per ladder level, a known gap from the 10-26 audit, `RESULTS_analysis_audit.md` item 2).

## Reading

On 8 of 13 judges the frozen index is a weak, below-gate predictor of agreement with the three-expert ratings (0.27 against a 0.45 bar), and the clustered test is not significant. The plain p-value is below 0.05 but the plain test treats the 70 units from 8 models as independent; the clustered test does not. With the 5 larger judges missing, the final verdict can still move, so this should not be reported as the E58 result.

## What would finish it

Run the 5 two-GPU judges with the unchanged driver on skampere1 (or a tested tensor-parallel fix), collect, and rerun `analyze58.py` on all 13 models. Nothing in the protocol changes; the runtime deviation (hardware, vLLM version) goes in each harvest's meta.

## Reproduce

```
python experiments/58_open_weight_judges_on_e39_e42_probes/scripts/analyze58.py --run <extracted runs/main> --out <dir>
```

Output hashes: `ANALYSIS.json` sha256 `00ff662cf1874e291d0fd4fe872e8e634c711c59d5d3af6b71789865e9b2bf69`, `RESULTS_open_weight_judges.md` sha256 `6b447230ef4c106eed92d52306b951c43d761721037fe32ff60d23ca850ca93b`. Cost $0.00, no paid API. Analysis by cc opus 5.5 xhigh.

**TLDR-end:** [cert-judge: E58] 8 of 13 judges finished; frozen gate FAIL (plain 0.269, clustered p 0.185, bar 0.45); the 5 big judges still need another route, so this is not the final verdict.
