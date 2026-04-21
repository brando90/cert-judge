I need you to scale our paper’s judge-sanity figures from the single Python→Lean `my_add` example to all VeriBench examples.

Context:
- Repo root: `cert-judge`
- Paper file: `paper_latex/NeurIPS_2025/mathai_neurips2025_template/neurips_2025.tex`
- Current figure filenames in paper:
  - `identity_property.png`
  - `monotonicity_bugs.png`
  - `monotonicity_missing_specs.png`
- VeriBench Lean files live under:
  - `data/veribench_dataset/lean_src/veribench/`

What I want:
1. Implement a script that computes:
   - Identity (P1) across all VeriBench files (using semantic-preserving variants).
   - Monotonicity-to-bugs (P2) across all VeriBench files (with a consistent degradation ladder).
   - Monotonicity-to-missing-specs (P3) across all VeriBench files (with a consistent ablation ladder).
2. Output aggregate CSV/JSON results and generate the three figure PNGs with the exact filenames above.
3. Save figures where the paper can directly include them (`paper_latex/NeurIPS_2025/figures`).
4. Add CLI flags for `--model`, `--n-repeats`, `--max-files`, `--seed`, and output dirs.
5. Keep paths repo-relative (no `~/...` assumptions).
6. Run a smoke test (`--max-files 3`) and report:
   - identity mean/std
   - monotonicity Spearman/Pearson and weak monotonicity %
7. Do not modify unrelated files.

Please implement directly, run checks, and then summarize:
- files changed
- exact commands run
- resulting output file paths
- key metrics from the smoke test.

---> also compute the variance of the judge (we want to make sure the variance is low) property 4

--> at the end do a PR merge it and assign it to Ethan Hersch. Make sure to e-mail brandojazz@gmail.com brando.science at gmail and ethan's email herschethan@gmail.com too with all the results eg figures pdfs images etc plots of the results

--> then if there are results go through the paper writing for this repo and inclde all those results in the writing (consistent hopefully with his already experiments that are in the paper or at least in the appendix). Tag him for this as another PR merge both to main but assign them to him.

--> Then end with a mega qa of this tasks and a final git push to main please. 

---

Note ethan also has this prompt so we need to do this too I think for the 4th property

```
You are in the cert-judge repo. Reproduce Experiment 9 (P4: Prompt Stability & Semantic Invariance) with a Claude judge model (not GPT/Codex).

Goal:
- Reproduce the full P4 run using a `claude-*` model in API mode.
- Keep judge instruction fixed; only use instruction-equivalent prompt templates.
- Report both:
  1) fixed-prompt repeatability noise (`mean_repeat_std`)
  2) cross-prompt dispersion (`mean_score_std_across_prompts`)

Important:
- Do NOT use `run_exp9_stability.sh` because it hard-checks `OPENAI_API_KEY`.
- Run `exp9_stability.py` directly with a Claude model.

Steps:
1. `cd /Users/ethanhersch/Documents/Documents/Stanford_Research/cert-judge/experiments/02_reviewer_response_neurips_math_ai_2026`
2. If available, activate env:
   `source $HOME/uv_envs/cert-judge/bin/activate`
3. Ensure Anthropic key is available:
   - either `export ANTHROPIC_API_KEY=...`
   - or file exists at `~/keys/anthropic_bm_key_koyejolab.txt`
4. Run full P4 with Claude:
   
bash
   python exp9_stability.py \
     --model claude-3-7-sonnet-latest \
     --judge-mode api \
     --n-repeats 5 \
     --max-files 0 \
     --prompt-names P1_BASELINE,P2_FORMAL,P4_CHECKLIST,P8_STRICT_B \
     --veribench-root ../../data/veribench_dataset/lean_src/veribench \
     --append-veribench-root ../../data/veribench_dataset_newest/lean_src/veribench \
     --append-max-files 34 \
     --results-dir results/stability_claude37_full_$(date +%Y%m%d_%H%M%S) \
     --figures-dir figures/stability_claude37_full_$(date +%Y%m%d_%H%M%S)
```