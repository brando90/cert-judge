# Project: cert-judge

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/AGENTS.md>

**TLDR:** Load the shared rules and preserve the project's scientific protocols. Human-rating forms and exports use verified names first and stable IDs second.

## Human-rating identity and collection — Brando, 11-11-2026

- Every active personal human-rating Google Sheet and comma-separated values (CSV) form/export begins with `rater_name`, then `rater_id`. Prefill the actual name from the verified roster on every assigned row; keep the stable ID for joins and duplicate detection. Apply this to every participant.
- Keep Google Sheets and their CSV exports consistent in column names, order and values. Warm-up and main forms use the same schema within a study, with different assigned rows. Import/export by column name; verify identities and that scores, notes and other source fields survive unchanged.
- [trustworthy-theorem-judges experiment 09](https://github.com/brando90/trustworthy-theorem-judges/tree/main/experiments/09_prepare_packets_and_collect_human_ratings_start_28Sep2026) owns the shared VeriBench collection. Read its [identity/import workflow](https://github.com/brando90/trustworthy-theorem-judges/blob/main/experiments/09_prepare_packets_and_collect_human_ratings_start_28Sep2026/support/IDENTITY_AND_IMPORT.md) and current form amendment before preparing or importing shared ratings. Link to that collection and its named files rather than starting a competing collection workflow here.
- Track the authorized named rating artifacts in that collection; do not anonymize names, ignore the files or move them into `private/` by default. Keep original imports, source receipts and delivered archives unchanged; make schema revisions as new versions. Copies are not new observations. Preserve consent, provenance, prior exposure and sealed splits; credentials, private correspondence, consent records and sealed data remain protected.
- Names are roster metadata, not ratings. Never invent scores, rationales, assistance disclosures or human attestations to fill gaps. Collection changes do not authorize collaborator emails or change frozen evaluation protocols.

## Research workflow: no branches

This is a research project. Each experiment lives in its own numbered experiment folder (`experiments/NN_<setup_name>/`). Commit and push straight to `main`. Do not create branches or pull requests. If a leftover branch turns up, merge it into `main` (no force-push) and delete it. If two experiments pick the same number, keep the one already on `main` and renumber the new folder to the next free number, updating its internal references.

## Global Agent Rules (load first, every session)

Fetch and follow the global rules from brando90/agents-config before doing anything else:
- **Primary (always works — cloud, phone, local):** fetch `https://raw.githubusercontent.com/brando90/agents-config/main/INDEX_RULES.md` and follow all Hard Rules, Trigger Rules, and Guidelines listed there.
- **Local optimization:** if `~/agents-config/` exists locally, read `~/agents-config/INDEX_RULES.md` instead (faster, same content). Run `git -C ~/agents-config pull` first to ensure it's current.
- **Sync discipline:** after any git commit+push in this repo, also pull agents-config (`git -C ~/agents-config pull` or re-fetch the URL) so all agents stay on the latest rules. If you edit agents-config itself, commit+push there too.

This file provides shared guidance to Codex, Claude Code and Cursor when working in this repository.

## Lean specification integrity

Use the following prompt when authoring or reviewing a Lean reference, assessing a submission, or building a judge that credits Lean evidence. Include it in new authoring and judging prompts. Keep private obligations and controls out of solver inputs.

> For each scored claim, identify the intended source behavior and the exact Lean declaration that expresses it. Check the declaration's elaborated type and follow the definitions it depends on, including imports and aliases, against the trusted original. Show a reachable input for the premises. For a behavioral obligation, show how it distinguishes the intended result from a concrete wrong result or implementation. A total function may legitimately have `Pre := True`. A postcondition that unfolds to `True`, a reflexive equality unrelated to the behavior, or a premise that assumes the conclusion cannot establish that behavior.
>
> Independently replay each claimed proof against the pinned declarations. Inspect transitive dependencies with `#print axioms` and check their provenance against the pinned Lean environment. Permit only the standard `propext`, `Classical.choice` and `Quot.sound` when used. Reject a fresh or shadowed axiom, `sorryAx`, or an untrusted reduction oracle in a credited proof. A clean axiom list alone says nothing about whether the statement captures the source.
>
> Return the declaration, witness, discriminating case, replay evidence and decision. Withhold credit for a demonstrated shortcut. If evidence is missing or search times out, mark the claim unresolved. Keep intentionally false tasks and correctly checked refutations labeled separately.

## Login checks and machine access (Brando, 10-29-2026)

- **Valkyrie is already signed in as Brando on skampere1.** Check there first with `valkyrie whoami` (expect `brando@vals.ai`) and `valkyrie run list`. Do not report "no Valkyrie login" before running both.
- **If a one-time-password or config login fails**, check Sherlock, FarmShare and snap to see whether the Valkyrie login works or is signed in on one of them, then run from there.
- **The agent has no access to Brando's Mac.** Never leave work queued behind the Mac lane. Start it now on free GPUs and the other clusters, and record in the experiment folder which host runs it.
- Keys, tokens and passwords never go in repos, messages or logs.

## Email (Brando, 10-06-2026)

Send from whichever of Brando's accounts you are signed in to (mail connector, else uutils SMTP); his request is the go-ahead. CC `brando.science@gmail.com`, `brandojazz@gmail.com` and `brando@vals.ai`, skipping the sender. Internal notifications follow agents-config Trigger Rule 26. Refinements (Brando, 10-13-2026): email to Vals people (vals.ai addresses) CCs only `brando@vals.ai` and BCCs the other two; every email at least BCCs `brandojazz@gmail.com` unless it is the sender.

## Paper plan: more human data, not weaker claims (Brando, 10-13-2026)

The cert-judge paper is being made as strong as possible, and its known gap is human data: a fresh, pre-registered human rating round (shared with VeriBench's set-N round, experiment 102) that tests the judge-trust index on new items and new judges is being prepared and run. Never "rewrite the paper's claims" to fit the current evidence, retire a claim, or pick a new framing on your own because an intermediate experiment (39, 41, 42, 43, 44, 45) came out weak or null: those results feed the next human-data round and the limitations section, and the framing is Brando's call after that round. A result-consistent interim draft may be prepared on a branch, labelled as such and left unmerged. Brando, 10-13-2026: "we are not 'rewriting the paper's claims'. We are trying to make the paper as high quality as possible. I thought the issue was that we need more human data, which is what we are preparing and having people go through."

## How we choose (learn) a judge: the formulations (Brando, 11-09-2026)

**Any agent that prepares or dispatches the human-rating task packet reads this first and keeps the packet (instructions, rating scale, splits, what the ratings are used for) consistent with it.** Full notes and sources: judge paper Q&A Doc, Part 3 (<https://docs.google.com/document/d/1zB-gYk-zU1wToS_E_carGSRGtUcF1NgZ-jWF5t1SJws/edit>).

Brando's four formulations, from his handwritten pages (Θ = the judge search space; S^tr, R^tr = train tasks and ratings; S^val, R^val = validation tasks and ratings; p^H = the human rating distribution; p^AJ = the judge's):

- ① argmax over judge in Θ of Corr(p^AJ, p^H), train data helps, Corr evaluated on S^val, R^val. "This is what people are doing" (his TODO: check by deep research).
- ② argmax over judge in Θ of Corr(p^AJ, p^H), using S^tr, R^tr only (e.g. optimizing the system with an agent or prompt optimization).
- ③ argmin over judge in Θ of Loss(p^AJ, p^H) on the validation set S^val, R^val, train data helps.
- ④ argmin over judge in Θ of Loss(p^AJ, p^H) on S^tr, R^tr only. "What we do in practice": train (or tune) on the train set only, choose hyperparameters on validation or historical hyperparameters.

His conjectures (not tested): (a) ③ gives better evaluation results than ④ (it uses general machine learning knowledge instead of a hack on human correlations); (b) ③ is more principled, or at least easier to think about, since it uses the successful machine learning framework. He does not think ② is needed. His question: do both experiments, and which is best? He also wrote that "the two main formulations" are "② & ④"; whether he meant ③ and ④ or ② and ④ is being clarified. Until he answers, drop neither reading: his words, ② and ④ (develop a judge by training correlation vs by training loss; the collection note `experiments/09_prepare_packets_and_collect_human_ratings_start_28Sep2026/support/JUDGE_FORMULATIONS_11-09-2026.md` in trustworthy-theorem-judges reads it this way), and our reading, ③ and ④ (select on validation vs train only), need the same independent raw ratings and sealed splits, so keep all four formulations evaluable.

Our recommendation (an idea, not a result): run ③ and ④ in one repeated 5-fold cross-validation loop over tasks with an untouched test fold; test cross-entropy is the primary metric; ③ wins only if the paired 95% interval of the difference excludes 0 and the gain exceeds a margin fixed beforehand; ties go to ④. No such experiment has been run.

What the literature check found (about 90 papers read by abstract and key passages, none end to end; 6 re-checked by the author; 11-09-2026): the usual justification of an LLM judge is agreement with humans on a test set (accuracy, kappa, Pearson/Spearman/Kendall). I did not find a paper that states formulation ① or ② as its principle. In the 21 Chinese-company papers opened (Seed1.5-Thinking, MiniMax-M1, LongCat-Flash-Thinking, DeepSeek-GRM, Kimi k1.5 and others) I did not find one choosing a judge by maximum correlation; they report accuracy on a human-labeled test set. Baidu ERNIE 4.5 could not be opened. The ③/④ direction (a loss against the human rating distribution) appears in 2025-26 papers, each also reporting correlation or accuracy; two papers report that correlation alone selects poorly (arXiv 2510.09738; arXiv 2503.05965, "as much as 31%" worse judges). I did not find a source comparing ③ against ④ at about 25 tasks, so conjecture (a) is neither supported nor refuted.

For packets: keep the validation and test splits by task family, solver and rater; keep test ratings out of judge selection; record which ratings were available to the judge search (train, validation, test) so ③ and ④ can be run later without re-collecting; use "rating" for the data and "judge" for the model (one term per concept).

## Project Purpose

`cert-judge` studies LLM-based judges for Lean 4 theorem/specification scoring. Keep these scientific objects distinct:

- `TW_m`: the scoped trustworthiness construct;
- `TI_m`: an expensive human-grounded criterion;
- `PTI_p`, currently `PTI_v0`: a label-free behavioral proxy/screening instrument.

The older P1–P7/JTI and TIvar pipelines remain historical compatibility code. Their outputs are not PTI-v0 and must not be relabeled as such.

**VeriBench versions (Brando, 10-09-2026).** cert-judge's VeriBench items use the family's version names. VBV1 is the original VeriBench (`brando90/veribench`: 896 Python-to-Lean tasks, core 614 plus IndustrySet 282). VBV2 is the private VeriSoftBench-derived task set built in VeriBench experiments 91 and 97 (VBV2.1 is experiment 99). VBV3 is VeriBench-Infinity (`brando90/veribench-inf`, paper `paper_latex/ICLR_2027_VeriBench_Infty/`). It has 24 source tasks with correct and intentionally incorrect Python variants, three frozen agent stages and kernel-checked comparison against the gold reference. Name the version beside every VeriBench number.

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

## New runs: full int_ref evaluation, all per-task results saved (Brando, 10-29-2026)

- For every NEW run, run the full int_ref evaluation (internal plus reference), never internal only. Save every per-task factor (IC_tests, IC_proofs, FSC, RC_tests, RC_proofs; an unmeasured factor is null, never 0) and the raw outputs, so Harsh int, Smooth int, Harsh int_ref and Smooth int_ref are all recomputed from the saved files. Harsh int and Smooth int use the first three factors of the same per-task rows, so no separate internal run is needed.
- Old runs stay as they are: no recompute, and their `_ref` cells read `not computed`.

## Selecting models and agent harnesses (10-22-2026)

Before choosing a new, unpinned solver, generator or artificial-intelligence judge, read `~/agents-config/workflows/model-and-agent-selection.md` ([shared guide](https://github.com/brando90/agents-config/blob/main/workflows/model-and-agent-selection.md)).

- Select the complete model/version, harness, effort, prompt, tools and fallback policy using relevant measured quality and total task cost; maximum price or effort is not evidence of suitability. Use current primary sources and save the selection rationale and supplied screenshots in the experiment.
- A coding leaderboard can shortlist a judge, but cannot validate it. Use relevant human/reference agreement, absolute error and signed bias, repeatability and failure rates where measured; keep selection data separate from test claims.
- Reuse existing results before an authorized bounded comparison. Prefer an affordable system meeting the justified quality criterion; when testing strongest-agent capability, use a credible relevant panel, not merely cheap weak models. Count trajectories, tools, judging, retries and failures in cost.
- Report observed versus estimated scores, task coverage and missingness. Distinguish repeat standard deviation, uncertainty of the mean and subset-prediction error. Validate smaller subsets or item response theory on held-out systems before relying on them; no universal precision guarantee.
- Apply this to prospective design. Preserve explicit model choices, frozen settings/denominators, required reference acceptance, project funding routes and shared budgets. It neither resumes paused inference nor authorizes extra model calls.

## Internet policy for evaluations (Brando, 11-03-2026)

- **Default: no internet for every evaluation run**, including every judge or rater-model run and any solver or generator agent being evaluated. Block all outside network access at run time (egress blocked, as on Valkyrie); the allowlist is empty unless a result says otherwise.
- **Why:** with internet, it is hard to predict how a model behaves; it may do something odd, bad or cheat (for example fetch the gold or related Lean files or search for the answer). No internet tests the model's own reasoning, not search.
- **Task generation:** with or without internet is fine; no internet is usually safer.
- **Allowed before the run only:** package installs and the Lean/Mathlib cache. Nothing is fetched while a solver or judge runs.
- **Say which evaluation type was run:** every result, report, table and paper states "no internet" or "internet (allowed hosts: ...)" next to the judge name and prompt (and the DT / no DT tag where one is used). If a run did not record it, write "not recorded"; never assume.
- **Exceptions** are an explicit choice by Brando, with the exact allowed hosts and the reason written next to the result.

## Running Evaluations

The frozen PTI-v0 numerical specification is `docs/spec/PTI_V0.md`. Its zero-spend entry point is:

```bash
python experiments/archive/04_veribench_validation/run_pti_v0.py --help
```

That CLI has no inference client and cannot load credentials. Paid judge inference outside Valkyrie (a direct provider or model-gateway API key) requires a separate exact call/cost quote and explicit approval; Valkyrie and Vals-funded runs are subject to the temporary spending pause below. Historical JTI evaluations remain under `experiments/archive/00_overall_cert_judge_metric_with_properties/`.

### Temporary Vals-funded run pause (Brando, 10-15-2026)

Pause new inference, retries and automatic recovery through Valkyrie or Vals API keys while project spending is reviewed. This supersedes the earlier unlimited-capacity/no-automatic-caps instruction. Preserve completed cells, partial artifacts, reservations and exact resume commands; do not treat a pause as scientific completion. Resume a paid condition only after Brando identifies it as essential and supplies or approves its per-run cap; no nonzero cap has yet been specified.

Local models on Stanford Network Analysis Project (SNAP) nodes may continue under their existing scientific and resource limits. Cached-data analysis, human-rating administration and subscription-based coding are outside this spending pause. Existing non-Vals funding retains its original authorization and limits. Continue recording route and reported charges, admit only declared cells, never silently retry or re-admit verdict-bearing cells, and treat HTTP 429 as an infrastructure failure. See [the spending checkpoint](experiments/CKPT_vals_spend_pause.md) for verified status, saved settings and restart boundaries.

### One large Valkyrie experiment at a time (Brando, 10-15-2026; permanent)

Paid Valkyrie work runs one large experiment at a time across all of Brando's projects (agents-config Trigger Rule 72): the week of 10-05 was the most expensive because four large experiments, including this repository's experiment 47, ran at once. The shared `valk` gate on SNAP and the Mac reads Valkyrie's live run list and refuses (exit 75) a launch whose experiment would exceed 50 unfinished tasks while another experiment, such as VeriBench `veribench109` or cert-judge `certjudge47`, has 25 or more unfinished. On a refusal, queue behind the running experiment; never split a run to slip under the limit or bypass the wrappers. Only Brando approves running two at once (`VALK_OVERLAP_OVERRIDE='<his approval, date>'`). Before a large launch, write its expected cost in the experiment's protocol, and record the actual charges afterward. This rule stays in force after the pause above is lifted; details are in VeriBench `docs/agent_rules/experiment_funding_and_valkyrie.md` (section "One large experiment at a time").

For new Vals-hosted runs, follow `~/agents-config/workflows/valkyrie.md` for `valkyrie login`, the Daytona sandbox provider, agent secrets named by `contract.yaml`, and separate verification of the organization and model payer. Completed runs using the former local `valkyrie.yaml` configuration remain historical; their Amazon Web Services (AWS) run history does not migrate to the hosted service.

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

**One file per section (since 2026-09-22, commit 710dda9).** `main.tex` holds only the preamble and the `\input` list. Prose lives in `00_abstract`, `01_introduction`, `02_related_work`, `03_problem_setup`, `04_property_protocol`, `05_experiments`, `06_limitations`, `07_conclusion`, `08_statements` (ICLR statements), and the appendix files `990`, `994`–`998` (`.tex`); `991`–`993` were retired on 2026-09-24 and live under `paper_latex/ICLR_2027_submission/archive/` (not built). Several agents share this checkout and its index, so:

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
