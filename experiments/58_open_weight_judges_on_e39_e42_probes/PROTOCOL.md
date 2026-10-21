# Experiment 58 protocol: open-weight judges on experiment 39's frozen probe design

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/58_open_weight_judges_on_e39_e42_probes/PROTOCOL.md>

**TLDR:** Experiment 39 froze `C_ms_gold` (the monotone-weakening score of a judge on gold-deletion ladders) as the label-free index and tested it on hosted judges. This experiment tests the same frozen index, with the same criterion, gates and parsers, on a fresh panel of open-weight judges run locally with vLLM. Nothing in this file changes after the first judge call; any deviation is written as a dated addendum, never an edit.

**Status:** FROZEN at the commit that adds this file. No judge call (model load, generation) had been made when it was committed; the only computation before it is the prompt rebuild (`scripts/rebuild_prompts.py`, no model, `results/REBUILD_REPORT.json`).

## 1. Question and what is held fixed

Does experiment 39's frozen selection, `C_ms_gold` (`experiments/39_*/results/SELECTION.json`, sha256 `25cb2aabef5c8881792819926060c87028bedd05f7257c62289ef67658dd2a3f`), still rank judges by agreement with the VeriBench three-expert coverage ratings when the judges are new, open-weight and run locally?

Held fixed, imported read-only from experiment 39 (never copied or edited): the 249 structurally valid probes (`probe_manifest.json`, sha256 `6ca37762d012fc7cb5046c49e7b4ddd208e0ecb5325235b0615d5daa60bd4c7c`), the nine prompt configurations `D0, R4, H0, H1, H2, P1, P4, P8, LEX`, the cell layout (521 cells per configuration), the parsers (`prompts.parse` of VeriBench experiment 100 for VeriBench rubrics, `legacy.parse` for the paper's prompts), `analysis_lib` (Scores, criterion, components, PTI-v0, TI_var, association) and the 45 held-out criterion items (experiment 75 split, seed 20260903, `val` and `test` items; `results/criterion_items.json` is the copy of the fields analysis needs).

## 2. Inputs, rebuilt and verified (no SNAP)

The prompt texts of experiment 39 lived under git-ignored `private/` on SNAP. They are rebuilt from `brando90/veribench` plus the repository's own scripts (`scripts/rebuild_prompts.py`), with Lean decisions replayed from the committed manifests by an oracle validator (a candidate counts as valid iff its sha256 is a manifest-valid probe). Each rebuilt cell is compared with the committed `candidate_sha256` and `prompt_sha256` of `results/cells/*.json`. Result before any judge call: probes 249/249, experiment 39 cells 4689/4689, experiment 42 cells 5238/5238 byte-identical. A run whose prompt text does not hash to the frozen `prompt_sha256` stops (the driver checks every row before generating). Mismatches, if any appear on a rebuild elsewhere, are listed in `REBUILD_REPORT.json` and the affected cells are `unmeasured_rebuild_mismatch`, never scored.

## 3. Panel (frozen in `scripts/e58.py`, `MODELS`)

13 open-weight models x 9 prompt configurations = 117 units, all treated as fresh test units (`split = "test"`): Qwen3 4B, 8B, 14B, 32B; Qwen3.6-27B (the bridge model); Llama 3.1 8B; Llama 3.3 70B (AWQ int4); Gemma 3 4B, 12B, 27B; OLMo 3 7B and 32B Think; gpt-oss-20b. Weights are pinned to the Hugging Face revision recorded in `e58.py`. Llama and Gemma official repositories are gated (manual approval), so ungated mirrors of the same weights are used (`unsloth/*`; `casperhansen/llama-3.3-70b-instruct-awq` for the int4 70B); this is a deviation from "official weights", recorded here and in every harvest (`source: mirror`). OLMo 2 is excluded (4k context is shorter than the longest prompts). The Llama 3.3 70B quantization means that cell is "AWQ-int4 Llama 3.3 70B", not the bf16 model. The panel mixes reasoning (Qwen3, Qwen3.6, OLMo 3 Think, gpt-oss) and non-reasoning (Llama, Gemma) models in each model's default chat mode; no thinking budget is tuned. Nothing is added to or dropped from the panel after the first call except a model that cannot load, which is reported as `unmeasured_infra` for all its units (never silently removed).

## 4. Generation rules

vLLM offline, one process per model, no server, no network at run time. Prompt = the model's own chat template over [system, user] with `add_generation_prompt=True`. Sampling = the model's own `generation_config.json` defaults (temperature, top_p, top_k, min_p, repetition penalty as vLLM reads them); one sample per cell (E39's three repeats are three cells); per-cell seed `int(sha256("58|<config>|<cell>")[:8], 16)`; `max_tokens = min(prompt max_tokens, max_model_len - prompt tokens)`; if that is below 1024 the cell is `unmeasured_over_context` (never truncated). Output is parsed after stripping the reasoning (`</think>` split; gpt-oss harmony final channel), as hosted E39 judges returned only their final message. A generation that stops on length before a parseable verdict is `incomplete`; any other unparseable answer is `parse_error`; neither is retried. Deterministic cells (identity-of-gold shortcuts, E39 `deterministic`) and `unmeasured_extraction` cells are copied from the E39 cell layout, not generated. Harvests are written in experiment 39's schema (`harvest_lib.py`), so `analysis_lib.Scores` reads them unchanged.

## 5. Primary analysis (the gate)

Per unit: criterion = Spearman between the unit's median score on each criterion item (3 repeats) and `target_expert`, over the 45 `val`+`test` items, computable only if at least 90% of items are scored (`analysis_lib.criterion`). Per unit: `C_ms_gold` = `analysis_lib.components()['ms_gold']`, needing 80% of valid probes scored. Primary statistic: Spearman across units between `C_ms_gold` and the criterion (`analysis_lib.association`, 10,000 draws, seed 39, one-sided permutation p, task-bootstrap CI as in E39). **Gate (E39's, unchanged): rho >= 0.45 and permutation p < 0.05.** Also reported, same statistic with the model as the cluster: (a) a model-clustered permutation (whole models' criterion vectors are permuted across models, matched by prompt configuration, among models whose nine units are all computable; 10,000 draws, seed 58, one-sided) and (b) a model-cluster bootstrap CI (resampling models). The verdict line states the plain gate result and the clustered result separately; a PASS on plain and FAIL on clustered is reported as such, not rounded up. Units that are not computable are listed and never imputed. Descriptive, non-gated: the same association over each prompt family (D0..LEX) separately, per model-family, and with all other E39 candidate indices (secondary, test-only).

## 6. Always reported, regardless of outcome

- `PTI_v0_frozen` (strict coverage; `NOT_COMPUTABLE` units counted) and `TI_var` with experiment 39's frozen normalization (`ti_var_norm` in SELECTION.json: V_c [0.01938502014905501, 0.18715029685282752], V_s [7.703719777548943e-34, 0.025416666666666667]); same association, gate not applied.
- Experiment 42 semantic screen on the same units: the rebuilt probes (582 cells per configuration) scored by the same driver; per unit directional accuracy on vacuity, weakening, over-constraint, formatting gap and the locked PASS rule, via experiment 42's own `screen_one` (task-clustered bootstrap, seed 42). Associations of these components with the criterion are descriptive.
- Scale-within-family curves (Qwen3, Llama 3, Gemma 3, OLMo 3): criterion and `C_ms_gold` against parameter count, per prompt and averaged over the nine prompts; descriptive only, no test, no claim of monotonicity.
- Cell status counts per unit (measured, parse_error, incomplete, over-context, deterministic) so a low-coverage unit is visible.

## 7. Exploratory, not gated: TVD-MI covariates

Both variants of `py_src/cert_judge/information_properties.py`: repeat TVD (`repeat_tvd_task`, per task over the criterion-item candidates with all three repeats and at least two candidates, mean over tasks) and deletion TVD (`deletion_tvd_task`, per gold-deletion ladder with identity as level 0, mean `value` over ladders; the gold-free `information` is also kept). Reported as Spearman with the criterion across units, with no gate and no selection. **This experiment does not freeze experiment 49 or any TVD-MI design; whether to do so is W-365 and is Brando's decision.**

## 8. Bridge check (local vs hosted Qwen3.6)

`qwen36_27b` (Qwen/Qwen3.6-27B bf16, tensor parallel 2) is the weights experiment 39 called hosted (`alibaba/qwen3.6-27b`). For each of the nine prompts: cells measured in both (E39 `results/harvest/qwen36__<P>.json` vs this run) compared by cell-level Spearman of scores, exact-score agreement rate and mean absolute difference; per-unit criterion and `C_ms_gold` side by side; status counts side by side. It is a check of the harness (hosted decoding and template versus local vLLM), not a replication test, and is not gated.

## 9. Cost, compute, reproducibility

No paid API of any kind; every charge is $0.00 (`charges_usd: 0.0` in each harvest). Compute is campus GPUs: FarmShare L40S primary (`-p gpu`, 4 GPUs at once at most), Sherlock `-p normal` fallback (`slurm/SUBMIT.md`). Package, rebuilt-prompt hashes, vLLM and torch versions, host, seeds and sampling parameters are written into every `*.meta.json` and the collected tarball's sha256 list. Conclusions are drawn only from a collected, hash-listed run.

## 10. What would change the plan

Written before the run: if more than 20% of any model's cells are `incomplete` or `parse_error`, that model's units are flagged in the report, not dropped, and the primary analysis is reported with and without them. If fewer than 8 units have both numbers, no correlation is computed (E39's rule). Any other change is an addendum with date and reason.
