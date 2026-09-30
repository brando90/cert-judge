# Folder 39 — PROTOCOL (LOCKED before any expensive run)

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/39_label_free_proxy_index_train_val_test_over_judge_families/PROTOCOL.md>

**TLDR:** Locked contract for the label-free proxy-index search: 60 judge units (50 single-call model × prompt configurations, 6 Terminus2 agent-judge configurations, 4 controls) split by judge model and harness into train / val / test, one criterion (agreement with the expert coverage ratings on 45 held-out items), Lean-validated probes, Valkyrie-only judge calls under a $1,600 cap, a 22-member candidate family ranked on train and picked on val, and one sealed test with pre-registered gates.

This file freezes the protocol before any LLM-budget-spending run begins.
It is written PRIOR to seeing any results. Any deviation observed during
execution is documented in `results.md` → "Deviations and open questions for Brando" (and, once one exists, `REPORT.md` → "Open questions for <reviewer>"),
not by editing this file. Amendments, if unavoidable, are numbered and appended at the end and apply prospectively.

## Scientific question (locked)

Does a label-free property index, whose form is chosen on one set of judge models, predict judge–human agreement on judge models it was not chosen on?

Operationally: over the 18 test judge units (Claude Opus 5.5 and Qwen3.6-27B single-call configurations, plus the Terminus2 agent judges on Claude Sonnet 5 and Qwen3.6-27B), is the Spearman correlation between the selected index and the criterion at least 0.45, with a one-sided permutation p below 0.05?

- **PASS:** both conditions hold for the index selected on train → val. Also report whether the train, val and test Spearman values lie within 0.30 of each other ("the correlations match").
- **FAIL:** either condition fails. The paper's protocol section becomes a negative result with these numbers.
- **INCONCLUSIVE:** the criterion is NOT_COMPUTABLE for more than 5 of the 18 test units, or the bootstrap interval spans more than 1.2; reported as such, never resolved by changing a threshold.
- Independently of selection, `PTI_v0_frozen` and `TI_var_trainnorm` (the paper's indices) are reported on every split with the same statistics.

## Locked parameters

| Parameter | Value |
|---|---|
| Units | 56 LLM configurations (50 single-call judge model × prompt, 6 agent judge = Terminus2 harness × model × prompt) + 4 deterministic controls; `scripts/e39.py` `MODELS`, `PROMPTS`, `PROMPTS_BY_MODEL`, `CONTROLS`; receipt `results/panel.json` |
| Split (over judge models and harnesses) | train: `sol6h` (openai/gpt-6-sol-high, reasoning high), `sonnet5m` (anthropic/claude-sonnet-5-medium, compute medium), controls; val: `luna6h` (openai/gpt-6-luna-high), `gem31h` (google/gemini-3.1-pro-preview, reasoning high), `t2_luna` (Terminus2 + openai/gpt-6-luna-high; prompts H2, D0); test: `opus55x` (anthropic/claude-opus-5-5-no-fallback, compute max; prompts H2, H0, D0, P4, LEX), `qwen36` (alibaba/qwen3.6-27b), `t2_sonnet5` (Terminus2 + anthropic/claude-sonnet-5-medium; H2, D0), `t2_qwen` (Terminus2 + alibaba/qwen3.6-27b; H2, D0). Counts: train 18 LLM + 4 controls, val 20, test 18. |
| Substitutes (only if a selector is absent at admission; recorded in `results/selectors.json` before that model's first admission) | luna6h → openai/gpt-5.6-luna-high; gem31h → openai/gpt-5.6-luna-high; qwen36 → openai/gpt-5.6-luna-high, then anthropic/claude-opus-5-no-fallback; t2_luna → openai/gpt-5.6-luna-high; t2_qwen → openai/gpt-5.6-luna-high. A substitute keeps the split it replaces. |
| Agent harness | the first Terminus2 bundle of `e39.AGENT_HARNESS_CANDIDATES` (`brando_terminus_gateway`, `terminus2`, `brando_terminus_astra_smoke`) whose contract `scripts/verify_agent_harness.py` can download; its contract kwargs (`max_turns` 20 and `reasoning_effort` high where exposed), secret mapping (`-s MODEL_GATEWAY_API_KEY fellows/brandoModelGatewayApiKey` unless the contract maps it) and file hashes go to `results/agent_harness.json` before any agent-judge admission. The agent receives the frozen prompt bytes as its task (`pack.agent_task_file`) and must write the verdict JSON to the declared output path; the collect-only service returns the file. An agent judge whose smoke cell yields no parsable verdict on the chosen bundle is `NOT_RUN_ROUTE` (no other harness is substituted). |
| Prompts | D0 `D0_deployed_tc_v1`, R4 `R4_exp75_human_precondition`, H0/H1/H2 human-mirror family (experiment 100 `prompts.py`, imported); P1_BASELINE, P4_CHECKLIST, P8_STRICT_B, BAD_STRINGY (`prompts/*.txt`, verbatim from the paper's pipeline; reference = the gold's last theorem block; one neutral system line required by the transport) |
| Items | experiment 100 `inputs/items.jsonl` (75 candidates, 25 tasks, annotation-era references and Python; `inputs/MANIFEST.json` hashes) |
| Criterion items | the 45 items of experiment 75's val + test tasks (seed 20260903); target `target_expert` = mean of participants 1–3 ÷ 5; secondary: test items (30), all items (75), train items (30) |
| Criterion statistic | Spearman (tie-aware) between the median of 3 repeats and the target; computed only if ≥ 90% of the declared items have a score; task-clustered bootstrap 10,000 draws, seed 39; Kendall τ-b and Pearson beside it |
| JUDGE_REPEATS | 3 for `crit`, `ident`, `bm_gold` levels; 1 for `blank`, `ms_gold`, `ms_cand`, `alpha`, `reorder`, `sorry`, `spam` |
| Ladder depths | ms_gold ≤ 4 levels (cut points ⌈k·n/L⌉), ms_cand ≤ 3, bm_gold 4 (cert-judge `build_bug_ladder`); level 0 = the identity cell (gold ladders) or the criterion cell (candidate ladders) |
| Probe validity | every transformed artifact must elaborate with `lake env lean` (Lean 4.22 + Mathlib project, exit 0; `sorry` warnings allowed); a level that fails truncates its ladder; a candidate that does not elaborate keeps only its criterion cell; invalid probes are excluded before any call and counted in `results/probe_manifest.json` |
| Deterministic cells | the deployed judge's own rules: empty or obligation-free candidate → 0.0; obligation-free reference → 1.0; extraction error → unmeasured (missing) |
| Components (10) | ident, blank, ms_gold, ms_cand, bm_gold, alpha, reorder, sorry, spam, stab, as in `analysis_lib.components`; a component needs ≥ 80% of its valid probes scored, else None |
| Frozen indices | `PTI_v0_frozen` per `docs/spec/PTI_V0.md` (strict coverage, exact-zero geometric means, K = 1 ladders → μ = C); `TI_var_trainnorm` = paper eq. tivar with V_c, V_s min–max normalized over the train LLM units and floors at 1e-6 |
| Candidate family (22) | `analysis_lib.CANDIDATES`: the two frozen indices; GM_cov5, GM_cov6, GM_cov7, GM_all10, AM_cov7, MIN_cov7, GM_mono2, GM_inv3, GM_bm_ms_inv; and C_<component> for each of the ten components |
| Selection rule | rank candidates by Spearman with the held-out criterion over the train LLM units (ties: fewer components, then name); keep the top three; select the finalist with the highest val Spearman (same tie-break). A correlation needs ≥ 8 units. Train ranking with the four controls added is reported, not used. |
| Test gates | selected index: test Spearman ≥ 0.45 AND one-sided permutation p < 0.05 (10,000 permutations, seed 39); bootstrap over units 10,000 draws; match tolerance 0.30 |
| Sealing | `analyze.py units` writes train + val rows to `results/units_train_val.json` and test rows to `private/units_test_sealed.json`; `analyze.py test` requires `results/FINALISTS.json` committed (commit hash argument must match `git log`) and refuses if the open rows changed after selection |
| Budget | cap $2,000 on Valkyrie-reported charges; planning estimate $1,387 for 50,224 calls (dry run, unvalidated probe counts are upper bounds; agent-judge cost assumes 4 turns per cell, unmeasured); no per-model dollar caps, no sampling, no dropped models; HTTP 429 is infrastructure, not budget |
| Transport | Valkyrie only, for every model and agent call; single-call units through agent `vb103_judge` byte-identical to experiment 103's validated bundle (`verify_bundle.py` PASS required before any admission); agent-judge units through the recorded Terminus2 bundle; packs in experiment 103's task-file format (agent flavor adds the plain task wrapper) with the true rubric in the header; one served benchmark per judge key `certjudge39-<key>` (nine services, ports 8990–8998); one run per (configuration, part); exactly one call (single) or one agent episode (agent) per cell in `main`, one labelled `recovery_1` pass over cells with no verdict; no other retries; no host-side key fetching |
| Seeds | probe cut order = file order (last theorem first); admission permutation `random.Random("39|<config>")`; statistics seed 39 |

## Scale verification (no further normalization)

Judge scores are normalized to [0, 1] at parse time: H0/H1/H2/R4 integer 0–5 ÷ 5; D0 integer 0–10 ÷ 10; legacy prompts a float already in [0, 1]. `target_expert` is already the 0–5 expert mean ÷ 5. Controls are in [0, 1] by construction. Nothing downstream divides again.

## Verified data layout

- `results/panel.json` → `units[]` with `config`, `model_key`, `prompt_key`, `family`, `split`, `kind`, `selectors`, `substitutes`, `kwargs`, `rubric`, `prompt_family`, `scale`, `max_tokens`.
- `results/probe_manifest.json` → `rows[]` with `probe_id`, `kind`, `key`, `task`, `item`, `level`, `path`, `sha256`, `source_sha256`, `valid` (true / false / null = unvalidated dry run), `reason`, `note`.
- `results/cells/<config>.json` → `cells[]` with `cell` = `<kind>__<key>__L<level>__r<repeat>`, `status` (render / deterministic / unmeasured_extraction), `prompt_sha256`, `prompt_bytes`, `score` for deterministic cells.
- `results/harvest/<config>.json` → `cells[]` with `status` (measured / deterministic / parse_error / model_error / incomplete / unmeasured_infra / unmeasured_extraction), `score` (normalized), `score_raw`, `cost_usd`; `status_counts`, `charges_usd`, `run_ids`.
- experiment 100 `inputs/items.jsonl` → `item`, `task`, `split`, `candidate_path`, `ref_ann_path`, `py_ann_path`, `gold_file_name`, `candidate_file`, `target_expert`, `n_ref_theorems_ann`, `ref_placeholder_at_annotation`.

## Pre-conditions for run

- Ports 8990–8998 free (nine pack services).
- Node-local clones on skampere1: cert-judge at `/lfs/skampere1/0/brando9/cert-judge_e39`, VeriBench at `/lfs/skampere1/0/brando9/veribench_e39` (read-only use), `E39_VERIBENCH_REPO` pointing at the latter.
- `valk` at `/lfs/skampere1/0/brando9/.local/share/valkyrie-host-bootstrap/tools/valkyrie/bin/valk`, `~/.config/valkyrie/valkyrie.yaml` present (never printed), `VALKYRIE_ENV=bench`.
- `/lfs/skampere1/0/brando9/vb103_venv/bin/python` with PyYAML; cloudflared at `/lfs/skampere1/0/brando9/vb-e2-service-20260916/bin/cloudflared`.
- Lean: `~/.elan/bin/lake`, project `/lfs/skampere1/0/brando9/vb90_grading/lean_project` (Lean 4.22, Mathlib built).
- `python3 -m pytest scripts/test_e39.py` passes on the node before any admission.

## Estimated wall-clock

- Probe construction with Lean: about 1,300 elaborations (≈ 10–20 s each) at 6 jobs → 1–2 h.
- Rendering 50 configurations: ≈ 6 min. Packs: ≈ 1 min per model. Services: ≈ 2 min per model.
- Judge campaign: ≈ 50,000 calls (agent-judge cells are multi-turn episodes, ≈ 1–3 min each); at concurrency 20 per run and 6 runs in flight, Sol/Luna/Qwen runs ≈ 1–2 h each, Opus ≈ 3–5 h each → about one day end to end including the recovery pass.
- Analysis: minutes.

## Pass/fail / abort rules

- **Smoke gate (per configuration):** its spare smoke cell returns a parsable verdict through the agent before its main pack is admitted. A model whose smoke fails on the pre-registered selector and every substitute is recorded `NOT_RUN_ROUTE` and its units are missing (never replaced by another model outside the substitute list).
- **Bundle gate:** `results/agent_bundle_check.json` verdict PASS, else no single-call admission; `results/agent_harness.json` verdict PASS, else no agent-judge admission.
- **Legacy-prompt limitation (known before any call):** P1/P4/P8/LEX show the judge only the gold's last theorem block (the paper's rendering), so gold-deletion ladders are informative only at level 1 for those units; components are reported as measured, never adjusted.
- **Pack gate:** `results/packs.json` verdict PASS (every task file round-trips through the agent's parser), else no admission.
- **STOP rules during the run:** reported charges reach the cap (`private/HOLD_JUDGE_ADMISSIONS` is written and nothing new is admitted; already admitted runs finish); a delivered prompt hash differs from the frozen hash (that cell is unmeasured_infra; if more than 1% of a run, hold admissions and report).
- **Completion:** every declared cell of every admitted run has a verdict or a labelled failure; one-to-one reconciliation of pack task ids against harvested cells; missing cells stay missing in the denominators.
- **Analysis order:** `units` → `select` → commit `results/FINALISTS.json` + `results/SELECTION.json` → `test` → `report`. The test split is never inspected before that commit.

## Identity / contact crib (verified)

- GitHub: `brando90` (repository `brando90/cert-judge`, verified from the remote); the worker exports `GH_TOKEN` from `~/keys/.brando90_github_token.txt`.
- Notification email: `brando.science@gmail.com`, no CC (Trigger Rule 26).
- Valkyrie configuration: `~/.config/valkyrie/valkyrie.yaml` on the host; never copied into prompts, logs, results or git.
- Model routes: Vals-hosted gateway through Valkyrie; no personal Anthropic/OpenAI/Google keys; Allen's Gemini key is not used (it is scoped to VeriBench 91c/92c).
