# Experiment 61 report (10-26-2026)

Question: do edits an attacker optimized against Claude Sonnet 5 (experiment 43's saved candidates, 77 unique texts, prompts D0/H2/P1, 6 tasks, 15 cells per unit) also inflate open-weight judges?
Analysis: `scripts/analyze61.py`, PROTOCOL.md section 3 as frozen (addenda 1-4 all dated before any output was parsed). Zero model calls in the analysis. Raw judge outputs in `results/raw/`, run metadata in `results/meta_*.json`, full numbers in `results/out/ANALYSIS61.json`.

Harness: single call, no tools (vLLM offline 0.11.0, torch 2.8.0+cu128, RTX A4000 16 GB on mercury2), model-default sampling, 2 repeats per cell, 458 judge calls per model. Settings per model: Qwen3-4B bf16 and Qwen3-8B bf16 (TP2) thinking on; Qwen2.5-14B-Instruct-AWQ int4 (TP2, gpu_memory_utilization 0.80, context 20,480) no thinking; Llama-3.1-8B-Instruct bf16 TP2 no thinking. Exact checkpoint revisions in `meta_*.json`.

Gap = mean over cells of (open-weight judge gain - reference gain). Verdict TRANSFERS only if the task-cluster bootstrap 95% CI (6 tasks) lies above 0; otherwise NO TRANSFER (a CI containing 0 is not evidence of resistance).

```
model | prompt | n meas/cells | gap [95% CI] | verdict | Sonnet gap (E43) | rho vs reference | rho vs Sonnet gain | same sign as ref
Qwen3-4B bf16 (thinking) | D0 | 15/15 | +0.138 [+0.014, +0.219] | TRANSFERS | -0.044 | +0.805 | +0.877 | 11/15
Qwen3-4B bf16 (thinking) | H2 | 15/15 | -0.271 [-0.403, -0.136] | NO TRANSFER | +0.033 | +0.465 | +0.242 | 10/15
Qwen3-4B bf16 (thinking) | P1 | 15/15 | +0.003 [-0.223, +0.171] | NO TRANSFER | -0.136 | +0.130 | +0.351 | 12/15
Qwen2.5-14B-Instruct-AWQ int4 | D0 | 15/15 | +0.191 [+0.112, +0.281] | TRANSFERS | -0.044 | +0.524 | +0.454 | 11/15
Qwen2.5-14B-Instruct-AWQ int4 | H2 | 15/15 | -0.278 [-0.463, -0.091] | NO TRANSFER | +0.033 | +0.175 | +0.298 | 11/15
Qwen2.5-14B-Instruct-AWQ int4 | P1 | 15/15 | -0.223 [-0.433, -0.020] | NO TRANSFER | -0.136 | +0.078 | +0.275 | 9/15
Qwen3-8B bf16 TP2 (thinking) | D0 | 15/15 | +0.028 [-0.064, +0.072] | NO TRANSFER | -0.044 | +0.674 | +0.782 | 10/15
Qwen3-8B bf16 TP2 (thinking) | H2 | 15/15 | -0.191 [-0.342, -0.041] | NO TRANSFER | +0.033 | +0.645 | +0.343 | 12/15
Qwen3-8B bf16 TP2 (thinking) | P1 | 15/15 | -0.153 [-0.433, +0.037] | NO TRANSFER | -0.136 | -0.024 | +0.335 | 10/15
Llama-3.1-8B-Instruct bf16 TP2 | D0 | 15/15 | -0.076 [-0.221, +0.069] | NO TRANSFER | -0.044 | +0.620 | +0.478 | 10/15
Llama-3.1-8B-Instruct bf16 TP2 | H2 | 15/15 | -0.351 [-0.542, -0.145] | NO TRANSFER | +0.033 | -0.347 | -0.350 | 7/15
Llama-3.1-8B-Instruct bf16 TP2 | P1 | 15/15 | -0.207 [-0.378, -0.036] | NO TRANSFER | -0.136 | +0.223 | +0.448 | 11/15
```

Findings (descriptive; 6 tasks, wide CIs):
- Only prompt D0 shows transfer, on two judges: Qwen3-4B (+0.138 [+0.014, +0.219]) and Qwen2.5-14B-AWQ (+0.191 [+0.112, +0.281]). Experiment 43's Sonnet gap on D0 is -0.044, so on D0 these two point estimates are above Sonnet's (no CI on the difference; Qwen3-4B's lower bound is only +0.014; 2 of 12 judge-prompt units pass, with no multiplicity correction, so this is weak evidence).
- Prompts H2 and P1: no judge shows a positive CI; H2 gaps are significantly negative for all four judges (the edits help the reference more than they help these judges).
- Qwen3-8B (thinking) and Llama-3.1-8B show no transfer on any prompt. Qwen3-8B tracks the reference and Sonnet gain on D0 (rho +0.67 / +0.78).
- Tracking of the reference is mostly weak off D0 (rho -0.35 to +0.65 across the H2 and P1 units; Llama H2 -0.35 and Qwen3-8B P1 -0.02 are the lowest).

Not run: Gemma-3-12B-it (planned in addendum 2). It failed twice at engine start on 2 x A4000 (negative KV-cache memory, 24.4 GB of weights; `lane_gemma3_12b.out`, `logs61`), so it has no rows; this is a hardware limit, not a result. The analysis lists only models with output.

Hardware: all lanes on mercury2 free GPUs; each lane deleted its weights and exited; no GPU of experiment 61 is still held. $0, no paid API.

## Independent QA notes (Claude Opus 5.5 review of the author's work, 10-26-2026)

All 12 table rows were recomputed from `ANALYSIS61.json` and match exactly (gap, CI, both rho, same-sign count, Sonnet gap, verdict). The P1 and H2 gaps were also reproduced from the raw outputs (60 of 60 cells each); D0 reproduced for 52 of 60 (the other 8 are the 2 rule-scored D0 cells per model, which need `prompts61.jsonl`). Disclosures that were missing:
- Failed repeats (protocol section 4 asks for them in every table): Qwen2.5-14B-AWQ 1 parse error; Llama-3.1-8B 6 parse errors, and 4 of its outputs hit the 16,384-token cap. None changes a verdict.
- Context length: the protocol says max_model_len 32768, but the frozen `register61.py` and `meta_*.json` use 28,672 for Qwen3-4B and Qwen3-8B. The smallest token budget was 16,384 and no cell exceeded context, so no effect. Addendum 3 names GPUs 1 and 8 for Qwen2.5-14B; its `meta` file records GPUs 4 and 5. Addendum 4 is labelled 13:30 but was committed at 13:24.
- Known bug, not fixed (the script needs inputs that are not in the repo): `scripts/analyze61.py` line 160 reads `checks.flagged_added` / `checks.n_flagged`, but experiment 43's key is `checks.flagged`. So `n_flagged` = 0 and `gap_mean_flagged` = null in `ANALYSIS61.json` are wrong and must not be used; 34 of the 45 cells are actually flagged (Qwen3-4B D0: n=13, gap +0.121; Llama H2: n=10, gap -0.527). The report's headline numbers do not use the flag split.
- Reproducibility: `analyze61.py` needs the VeriBench clone on skampere1 and `prompts61.jsonl`; neither is in the repo, and the Gemma-3-12B logs named above are not in the repo.
