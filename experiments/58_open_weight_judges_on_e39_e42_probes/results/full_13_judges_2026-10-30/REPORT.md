# E58 result: 13 of 13 open-weight judges (2026-10-30)

## Gate (E39's: rho >= 0.45 and p < 0.05)

The frozen index `C_ms_gold` passes E39's gate on all 13 judges, narrowly: plain PASS, model-clustered PASS (117 units, 114 with both numbers; `scripts/analyze58.py` from main, unchanged, 10,000 draws, nothing dropped, no `unmeasured_infra`). The 8-judge partial of 2026-10-29 (`partial_8_judges_2026-10-29`, FAIL at 0.269) is superseded by this run; the verdict moved because the 5 added judges (2 of them the strongest, Qwen3.6-27B and Qwen3 32B) have a much stronger association (0.699 on their 44 units alone).

| Test | n | Spearman | p | 95% CI | Gate |
|---|---:|---:|---:|---|---|
| plain permutation | 114 units | 0.460 | 0.0001 | 0.292 to 0.603 | PASS (bar 0.45; margin 0.010) |
| model-clustered | 10 models | 0.487 | 0.0066 | 0.141 to 0.691 | PASS |

The clustered test uses only models whose 9 prompt units all have both numbers: 10 of the 13. Gemma 3 4B (H2), Llama 3.1 8B (H0) and Llama 3.3 70B AWQ (H2) each have one unit with under 90% of criterion items scored, so they drop out of the clustered test only; the plain test keeps their other units.

The pass is thin. Post-hoc leave-one-model-out (descriptive, not part of the frozen analysis): plain rho stays at or above 0.45 when dropping any of 9 models (0.460 to 0.560) but falls below the bar when dropping Gemma 3 27B (0.417), Qwen3 32B (0.417), Qwen3 14B (0.437) or Qwen3.6-27B (0.393). The clustered CI lower bound (0.141) and the plain CI lower bound (0.292) are both below 0.45, so this does not show the index clears the bar with confidence. Drop both OLMo 3 models: 0.582.

Section 10 failure sensitivity: no model has more than 20% parse-error or incomplete cells (max Llama 3.1 8B, 2.6%), so nothing is flagged and the verdict is the same with and without flagged models.

## Qwen3.6 bridge check (section 8, descriptive, not gated)

Local `qwen36_27b` (vLLM, A100 TP=2) against E39's hosted Qwen3.6, cells measured in both (449 to 511 per prompt). The protocol sets no pass bar, so "holds" is read descriptively:

- Cell level: Spearman 0.83 to 0.91 on all 9 prompts, exact-score agreement 56% to 74%, mean absolute difference 0.03 to 0.12. The harness check holds at the cell level.
- Per unit: `C_ms_gold` agrees within 0.01 on D0, H0, H1, LEX and P8, differs 0.055 on P4 and 0.136 on P1 (0.794 local, 0.658 hosted); R4 and H2 have no hosted `C_ms_gold`.
- Per unit criterion differs by up to 0.19 (P4 0.354 local, 0.544 hosted; R4 0.750/0.830; H1 0.792/0.857; D0 0.799/0.727; H2 0.876/0.817; P1 0.504/0.462; P8 0.349/0.385; H0 0.807/0.829; LEX -0.288/-0.288). So the cell-level agreement holds, the unit-level criterion does not match exactly on P4, R4 and H1.

## Collection

- Judges 1 to 8 (gemma3_4b, gemma3_12b, gpt_oss_20b, llama31_8b, olmo3_7b, qwen3_4b, qwen3_8b, qwen3_14b): FarmShare run, tarball sha256 `faf4ecb469f6420b97e2ec792c2ef5867d6481249b6e2edf81134108ceb452a3`, 144 harvests.
- Judges 9 to 13 (qwen3_32b, qwen36_27b, llama33_70b_awq, gemma3_27b, olmo3_32b): skampere1 run, tarball `e58_2gpu_results.tgz` sha256 `c44d9e2e5bb95e445a671be0f3824c377a3704e7e0ee7a955aae908a8ee93b0c` (verified after transfer), 90 of 90 harvests, 281 files with its own manifest, verified.
- Runtime deviation (hardware only): the 5 two-GPU judges ran on 2x A100-SXM4-80GB TP=2 on skampere1, not 2x L40S on FarmShare, because FarmShare TP=2 hung (vLLM shared-memory broadcast timeout). Same package, unchanged `judge_vllm.py`, pinned revisions, seeds, sampling; vLLM 0.32.0, torch 2.13.0+cu130 (`RUNTIME_2gpu.md`). The runtime-contract check matches on all 234 harvests (0 mismatches).
- Merged run: 234 of 234 harvests (13 models x e39/e42 x 9 prompts), `MISSING.json` empty, merged manifest `MANIFEST_merged_run.sha256` (729 files, sha256 `a1863fee1c18b7649dd81c71221e61e09bdca886fd607ac9eab71a54652f8e10`) built from both verified collections; analysis input check: VERIFIED.
- Status counts: all failures are parse_error or incomplete, at most 2.6% of a model's cells; the 56 deterministic and 9 unmeasured_extraction cells in D0 are the same for every model.

## Per judge (mean over the 9 prompts; criterion = Spearman with the three-expert coverage ratings on the 45 held-out items)

| Judge | criterion Spearman | C_ms_gold | failed cells fraction |
|---|---:|---:|---:|
| Qwen3.6 27B | 0.549 | 0.911 | 0.8% |
| Qwen3 32B | 0.454 | 0.842 | 0.1% |
| Qwen3 14B | 0.349 | 0.864 | 0.05% |
| Qwen3 4B | 0.293 | 0.715 | 0.06% |
| OLMo 3 7B | 0.260 | 0.460 | 0.7% |
| Llama 3.1 8B | 0.219 | 0.545 | 2.6% |
| Gemma 3 12B | 0.214 | 0.297 | 0.6% |
| OLMo 3 32B Think | 0.209 | 0.761 | 0.03% |
| gpt-oss-20b | 0.194 | 0.881 | 2.0% |
| Qwen3 8B | 0.174 | 0.770 | 0.2% |
| Gemma 3 4B | 0.130 | 0.417 | 1.4% |
| Llama 3.3 70B AWQ | 0.055 | 0.419 | 0.15% |
| Gemma 3 27B | -0.049 | 0.382 | 0.3% |

Criterion means for Gemma 3 4B and Llama 3.3 70B AWQ cover 8 prompts (one unit not computable). Per-unit rows are in `RESULTS_open_weight_judges.md` and `ANALYSIS.json`.

## Always reported

- Association of `C_ms_gold` within prompt family (descriptive, 11 to 13 units each): H2 0.864, H1 0.791, H0 0.559, R4 0.555, P1 0.473, D0 0.170, P8 0.132, P4 0.033, LEX -0.203. Within model family: Qwen3.6 0.700 (9 units), gpt-oss 0.600 (9), Qwen3 0.530 (36), Llama 3 0.547 (16), Gemma 3 0.256 (26), OLMo 3 -0.552 (18). OLMo 3 is the one family where the index and the criterion move in opposite directions.
- PTI_v0_frozen: computable on 98 of 117 units (19 NOT_COMPUTABLE); association not computed (n/a).
- TI_var (E39 frozen normalization): n 115, Spearman -0.092 [-0.260, 0.082], p 0.83, no gate applied.
- E42 semantic screen: 19 PASS, 96 FAIL, 2 NOT_COMPUTABLE of 117 units. Descriptive association of components with the criterion (115 units): weakening 0.600, overconstraint 0.553, vacuity 0.380, formatting -0.536.
- Scale within family (descriptive, no trend claim): Qwen3 criterion 0.293 (4B), 0.174 (8B), 0.349 (14B), 0.454 (32B); Qwen3 `C_ms_gold` 0.715, 0.770, 0.864, 0.842. Gemma 3 criterion 0.130 (4B), 0.214 (12B), -0.049 (27B). Llama 3 0.219 (8B), 0.055 (70B AWQ). OLMo 3 0.260 (7B), 0.209 (32B Think). Larger is not better across families; only the Qwen3 points rise.
- Exploratory TVD-MI (does not freeze E49; W-365 stays Brando's call): repeat TVD Spearman 0.007 (n 114); deletion TVD not computable (the deletion covariate needs at least two repeats per ladder level, a known gap from the 10-26 audit, `RESULTS_analysis_audit.md` item 2).

## Reading

The frozen index clears E39's gate on the full 13-judge panel, but by 0.010 on the plain test, with a confidence interval that reaches 0.29, and the result depends on a few strong Qwen models: removing Qwen3.6-27B, Qwen3 32B, Qwen3 14B or Gemma 3 27B puts it below the bar. It is a pass under the pre-registered rule, a fragile one. The index tracks the criterion well for Qwen3/Qwen3.6, gpt-oss and Llama, weakly for Gemma 3, and in the wrong direction for OLMo 3, and it is strong on H1/H2 prompts and near zero on D0, P4, P8 and LEX. Hardware differs between the two groups of judges (L40S vs A100), which the bridge check suggests matters little at the cell level.

## Reproduce

```
python experiments/58_open_weight_judges_on_e39_e42_probes/scripts/analyze58.py --run <merged runs/main with 117+117 harvests> --out <dir>
```
Run time about 19 minutes (CPU).

TLDR-end: [cert-judge: E58] C_ms_gold passes E39's gate on 13 of 13 judges, narrowly (plain rho 0.460, p 0.0001; clustered 0.487, p 0.0066); the pass flips to fail without any one of four strong judges.
