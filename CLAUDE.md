# CLAUDE.md

## Global Agent Rules (load first, every session)

Fetch and follow the global rules from brando90/agents-config before doing anything else:
- **Primary (always works — cloud, phone, local):** fetch `https://raw.githubusercontent.com/brando90/agents-config/main/INDEX_RULES.md` and follow all Hard Rules, Trigger Rules, and Guidelines listed there.
- **Local optimization:** if `~/agents-config/` exists locally, read `~/agents-config/INDEX_RULES.md` instead (faster, same content). Run `git -C ~/agents-config pull` first to ensure it's current.
- **Sync discipline:** after any git commit+push in this repo, also pull agents-config (`git -C ~/agents-config pull` or re-fetch the URL) so all agents stay on the latest rules. If you edit agents-config itself, commit+push there too.

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

`cert-judge` studies LLM-based judges for Lean 4 theorem/specification scoring. Keep these scientific objects distinct:

- `TW_m`: the scoped trustworthiness construct;
- `TI_m`: an expensive human-grounded criterion;
- `PTI_p`, currently `PTI_v0`: a label-free behavioral proxy/screening instrument.

The older P1–P7/JTI and TIvar pipelines remain historical compatibility code. Their outputs are not PTI-v0 and must not be relabeled as such.

## Terminology for Scientific Prose

Name the operation precisely rather than using "calibration" as a catchall: distinguish validation-set association, a fitted score mapping, threshold selection, and score--outcome reliability. Preserve external titles and citations, literal paths and code identifiers, and frozen evidence; wording cleanup also applies to stored archived manuscript prose, whose corresponding PDF artifacts must be rebuilt.

### Data splits: train / validation / test only

Brando's rule (09-22-2026; `~/agents-config/writing/ml_research/ml_research_writing.md` § Data-Split Names): call data splits train, validation (val), and test. Never write "development set", "dev set", or "development panel".

- The 72-pair human panel (75 rated pairs, one gold file missing; one annotator, pass1/pass2 strictness levels) is the **validation set**. It was used to choose the index form, repeat aggregation, threshold, and prompt panel, so its correlations are optimistic.
- `TI_var` has no fitted weights, so there is **no training set**. The exp23 weight-tuned variant is trained on one label pass and evaluated on the other pass of the same pairs; that is not a test set.
- There is **no test-set result**. The five-rater pool (343 labels, 78 pairs) used a revised rubric that agrees with the validation labels at only rho ~ 0.13 on 63 shared pairs (archive `22_pooled_heldout_and_noise_ceiling`), so its null results (exp23 rho = -0.238, exp43, exp22) cannot test transfer. A real test set needs new raters under the validation set's rubric, with the properties and `TI_var` frozen first.

### "Specification" has one meaning here

"Specification" is ambiguous (natural-language intent vs. a formal object; written by an agent, a human, or a script). The paper fixes it in §3 "Task" (`sec:problem-setup`); all prose must match:

- **Intent** — the informal requirement in the natural-language problem statement or docstring. Never call it a "specification"; say "intent".
- **Formal specification** (adopted; common formal-methods usage, as preferred by the formal-methods experts consulted) — the theorem statements about the implementation plus the `Prop` predicates they use: pre/postconditions, properties, `Pre → Post` correctness, equivalence to a reference implementation. Bare "specification"/"spec" in prose means exactly this.
- **Not specification:** unit tests (`example : f 1 = 2 := by decide`, `#eval`, `#guard`), which are *tests*; proofs, which certify the theorems (golds often use `sorry`); the implementation itself. Never write "theorem/test specifications", "specification items (tests/theorems)", or "code, tests, theorems, and formal specifications" as if theorems and specs were different things.
- **Competing view (not adopted):** a unit test is a ground (closed) theorem, so tests are point specifications. It is stated only as a position in appendix `app:spec-vs-tests`; do not import it into the main text.
- **Authorship is orthogonal to the term.** Name the provenance when it matters: candidate (agent-generated), gold (the audited reference artifact `g`), probe (a scripted perturbation of a gold).
- **Frozen names vs. the definition.** The missing-specification ladder (`P_ms`, P3, `build_missing_spec_ladder`, `_is_spec_declaration` in `py_src/cert_judge/probe_validation.py`) removes theorem statements *and* tests. Keep frozen names and identifiers, but describe what it removes as "theorem statements and unit tests".
- **Bug ladders differ.** The PTI-v0 `build_bug_ladder` mutates only implementation `def`s. The historical P2 `my_add` ladder (`data/file_equiv_08_19_2025/my_add_file_eq_with_bugs/BUGS_SUMMARY.md`) mostly corrupts specification statements. State which one you mean.

## Environment Setup

Uses `uv` for environment management (not pip/conda):

```bash
# One-time setup
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv venv $HOME/uv_envs/cert-judge
source $HOME/uv_envs/cert-judge/bin/activate
cd ~/cert-judge && uv pip install -e . && uv sync --active
```

Some dependencies (`vllm`, `sglang`, `unsloth`, `flash-attn`) are Linux-only and excluded on macOS via `pyproject.toml` markers.

## Running Evaluations

The frozen PTI-v0 numerical specification is `docs/spec/PTI_V0.md`. Its zero-spend entry point is:

```bash
python experiments/archive/04_veribench_validation/run_pti_v0.py --help
```

That CLI has no inference client and cannot load credentials. Paid judge inference requires a separate exact call/cost quote and explicit approval. Historical JTI evaluations remain under `experiments/archive/00_overall_cert_judge_metric_with_properties/`.

## Architecture

### Core Package: `py_src/cert_judge/`

**`pti_v0.py`** — canonical, versioned PTI-v0 numerics: tie-aware ladder correlations, repeat instability, exact-zero log geometric means, coverage-aware properties, and three-/four-property aggregation.

**`probe_validation.py`** — conservative alpha-renaming and cumulative bug/missing-spec probe construction with fail-closed Lean elaboration.

**`hsj_scoring.py`** — legacy JTI/HSJ compatibility logic, including `compute_p1_identity()`, `compute_p2_or_p3_ordering_auc()`, `compute_p4_stability()`, `compute_jti()`, and score-mapping/fusion helpers.

**`tvd_mi_tools.py`** — TVD-MI information robustness metric:
- `tvd_mi_from_critic()` — Youden's J (TPR+TNR-1) from categorical labels
- `per_item_auc_macro()`, `tamper_suite_report()` — P5 sub-metrics

The PTI-v0 properties are exact equality (`P_eq`), bug monotonicity (`P_bm`), missing-specification monotonicity (`P_ms`), and alpha-renaming invariance (`P_eqalpha`). Structurally valid constant judge-score ladders remain included with `C=0`; structurally invalid probes are excluded independently of judge outputs; missing score coverage yields `NOT_COMPUTABLE/DEFER`.

### PTI-v0 Data Layout

- Base candidates: `data/generated_agents/`, frozen as typed `f=(item,agent,generation)` rows in `experiments/archive/04_veribench_validation/pti_v0_v4/base_pool_manifest.json`.
- Golds: resolved by the frozen precedence policy across the legacy and newest VeriBench roots.
- Frozen probe validity, requests, cache inventory, quotes, and results: `experiments/archive/04_veribench_validation/results_pti_v0_v4/`. New work must use a newly registered active experiment; never write new runs into an archive.

Historical P1–P5 fixtures retained for compatibility:

- P1 identity: directories of `.lean` files (scored against themselves)
- P2 bug ladder: `data/file_equiv_08_19_2025/my_add_file_eq_with_bugs/` — numbered files with increasing bugs
- P3 spec ladder: `data/file_equiv_08_19_2025/my_add_file_eq_with_missing_specs/` — numbered files with increasing spec deletions
- P5 pairwise: 25 same-source + 25 different-source file pairs sampled at runtime

## LaTeX Paper Sources

The active manuscript is `paper_latex/ICLR_2027_submission/`. Older ICML/NeurIPS trees are historical. Populate PTI-v0 claims only from committed machine-readable PTI-v0 outputs.

**One file per section (since 2026-09-22, commit 710dda9).** `main.tex` holds only the preamble and the `\input` list. Prose lives in `00_abstract`, `01_introduction`, `02_related_work`, `03_problem_setup`, `04_property_protocol`, `05_experiments`, `06_limitations`, `07_conclusion`, and `990`–`997_appendix_*` (`.tex`). Several agents share this checkout and its index, so:

- Edit the section file for your change, never a monolithic copy. Touch `main.tex` only to add or reorder an `\input`, and keep the `% !TEX root = main.tex` first line in every section file.
- Build in a scratch copy (`latexmk -pdf -interaction=nonstopmode main.tex`), not in the paper directory: concurrent `latexmk` runs there have truncated `main.aux`. Copy the built `main.pdf` back only for semantic changes.
- Commit with explicit pathspecs (`git commit -- <files>`), never `git add -A`, because another agent's staged files would ride along.

Prose in `.tex` files is **one sentence per line**: a newline after every full sentence and no wraps mid-sentence (rule: `~/agents-config/writing/ml_research/ml_research_writing.md` § LaTeX Source Layout). Check from the paper directory with `python3 ~/agents-config/scripts/latex_sentence_lines.py --check main.tex 0*.tex 99*.tex`.

## Experiment lifecycle (required)

Only work currently being pursued belongs directly under `experiments/`. Completed,
superseded, stopped, or parked experiments belong in `experiments/archive/`, even
when their results support the current paper. Unstarted follow-up suggestions do
not keep a completed study active. Shared label directories are data, not experiments.

`experiments/archive/layout.json` is the machine-readable active/support inventory
and retirement map. Register an active experiment there with its concrete current
task and add its row to `experiments/README.md`. When closing it, use `git mv`, record
the outcome in the archive index, update executable consumers and path depths, and
preserve frozen results byte-for-byte. Reusable code belongs in the core package.

After a pull or archive move, run:

```bash
python3 py_src/cert_judge/experiment_layout.py --check
```

If obsolete local folders remain, run the same command with `--reconcile`, then
`--check`. Reconciliation preserves ignored local files and conflicting versions;
never use `git clean -fdx`. Do not recreate retired roots when merging older branches.
