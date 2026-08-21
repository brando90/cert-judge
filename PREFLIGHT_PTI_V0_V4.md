# CertJudge PTI-v0 v4 Preflight

**TLDR:** Verdict: **BLOCKED**. The zero-spend audit found invalid bug/spec ladders, a malformed alpha transformer, a failed 72-to-75 gold-provenance claim, and unresolved pool/statistical decisions; no paid call or PTI-v0 bridge computation was made.

Date: 2026-08-20 (America/Los_Angeles)

Scope: read-only, zero-spend preflight governed by `experiments/28_new_notation_and _experiments/00-CODEX-SOL-MAX-PREFLIGHT.md` and the higher-priority rulings in `03-SPEC-OVERRIDES-R41-R49.md`.

References below to `PTI_V0_CANONICAL_SPEC.md`, `PTI_V0_TEST_VECTORS_v2.json`, `RECONCILIATION-R36-R40.md`, and `test_pti_v0_reference_final.py` refer to the inner archive nested under `experiments/28_new_notation_and _experiments/ref/files (22).zip`; the archive was inspected in a temporary directory and not modified.

## 1. Verdict

**BLOCKED.** Execution must not proceed to PTI-v0 property computation, a bridge statistic, a paid alpha run, or manuscript result replacement.

The blockers are substantive rather than cosmetic:

1. Every alpha artifact in the audited 184-row historical pool is malformed (`:=:=`); all 163 dependency-free samples fail Lean 4.22 elaboration, and bound occurrences are not renamed consistently.
2. None of the 163 dependency-free bug ladders and none of the 163 dependency-free missing-spec ladders satisfies the structural contract across all levels. The other 21 files are dependency-blocked, not validated.
3. The cached 184-row probe pool is a pool of reference Lean files scored against themselves, not the typed real-candidate pool `f=(i,a,q)` required by the PTI-v0 specification.
4. The proposed 72-to-75 repair does preserve the three candidate generations, but the historical gold is byte-identical to the current vulnerable `1_unsafeMultiply.lean`, not the intended safe `safe/1_unsafeMultiply_safe.lean`. R46 therefore forbids the rename-only repair.
5. The supplied conformance artifacts conflict after the R43 override, and the handoff does not include the reference module imported by its test file.
6. The coverage threshold, exact pool, machine-readable judge roles, several bootstrap edge policies, the SESOI data-generating process, QWK encoding, and per-property screening thresholds are not frozen.
7. Required dependencies remain open: ultimate-utils PR #44 must be resolved before cert-judge PR #38, and the current Python process is running under Rosetta in the wrong environment.

No judge score constancy was inspected to decide structural validity. No API key was loaded. No paid inference was performed. No PTI-v0-versus-`TI_m1` bridge value was computed or revealed.

## 2. HARD blockers and evidence

| ID | HARD blocker | Evidence | Required resolution |
|---|---|---|---|
| H1 | `P_eqalpha` is structurally invalid | `utils/variant_generator.py:85-124` renames only single-letter tokens in the theorem signature, reconstructs a suffix that already begins `:=` by adding another `:=` at line 118, and falls back to a comment at lines 120-122. `generate_variants` records `compiled=None` at lines 127-156. Every audited alpha output contains `:=:=`; 163/163 dependency-free transforms fail Lean 4.22. | Replace the transformer with syntax-aware capture-avoiding alpha-renaming; rename binders and every bound occurrence; reject no-ops/fallbacks; produce hashes and an elaboration manifest for the frozen pool. Rerun the no-cost gate before quoting spend. |
| H2 | Bug and missing-spec properties have no validated probe set | `exp8_veribench_sanity_properties.py:223-270` uses comment-only bug fallbacks and transformations that frequently make Lean invalid; lines 307-319 use repeated fractional removal plus arbitrary tail truncation. Across the 163 dependency-free base rows, 0 complete bug ladders and 0 complete spec ladders are structurally valid. | Design cumulative, semantically documented, Lean-valid ladders; validate every level independently of judge outputs; freeze a row-level structural manifest. |
| H3 | The base-artifact pool is not frozen and the cached 184 pool has the wrong type | `PTI_V0_CANONICAL_SPEC.md:82-108` defines `f=(i,a,q)` and separate probe sets from a frozen base-artifact pool. In contrast, `exp8_veribench_sanity_properties.py:449-528` reads a reference Lean file and scores transforms of that same file against itself; `exp9_stability.py:423-452` does the same. The manuscript says 184 “existing candidates and golds” at `main.tex:229-238`, but the cache provenance is reference-as-candidate. | Choose and freeze one typed pool before cache accounting: the 75 panel candidate pairs, the manuscript's 157 x 3 = 471 full candidate pool, or another explicit `f=(i,a,q)` manifest. Do not relabel the 184 reference-file cache as candidate evidence. |
| H4 | R46 Option B provenance check fails | Historical `results/.../0_unsafeMultiply_safe/gold.lean` has SHA-256 `cc14...facf`, exactly matching current vulnerable `security_6858/1_unsafeMultiply.lean`. Intended safe `security_6858/safe/1_unsafeMultiply_safe.lean` hashes to `7b3c...a346`. Historical resolver lines `run_veribench_validation.py:120-137` explicitly map the stale safe-looking key to the unsuffixed vulnerable Lean file, while source resolution at lines 140-158 maps to safe Python. | A data owner must choose: keep the defensible 72-row analysis; rerate the three candidates against the correct safe gold; or explicitly redefine and document them as vulnerable-gold ratings. A silent key rename is prohibited. |
| H5 | R43 conformance suite is internally inconsistent/incomplete | Top-level R43 (`03-SPEC-OVERRIDES-R41-R49.md:21-41`) requires a structurally valid constant score ladder to receive `C=0`. The nested `PTI_V0_TEST_VECTORS_v2.json:3,42-50,69-95` still specifies R36 exclusion and theta-based aggregation. The nested Python test's constant-ladder assertion at `test_pti_v0_reference_final.py:84-89` expects factor 0, but it imports an absent `pti_v0_reference_final.py` and lacks the updated aggregation/coverage oracle. | Version the spec and vectors after R43, add the missing canonical implementation, and pass one coherent vector suite at tolerance `1e-12` before real-data computation. Preserve explicit structural-invalid exclusion separately from behavioral constant `C=0`. |
| H6 | Missingness and statistical behavior are not fully frozen | R43 says “beyond a pre-frozen coverage threshold” but does not specify that threshold. The older `theta=0.20` was attached to the superseded constant-exclusion mechanism. CI type, undefined bridge-bootstrap replicate handling with only five inferred primaries, SESOI DGP details, QWK half-score encoding, and screen thresholds are also unresolved. | Record these choices in a machine-readable frozen config and decision log before computing any property or bridge result. |
| H7 | Dependency state is unresolved | ultimate-utils PR #44 and cert-judge PR #38 are both open and mergeable, with no reported checks or review decision. R42 requires review order #44 then #38. Exp27 imports `uutils` (`py_src/cert_judge/ti2prime_plot.py:35-39`). | Review/test #44, then review/test #38 against that dependency. Merge or stack explicitly; do not copy the utility or recreate Exp27. |
| H8 | Exact alpha spend cannot be quoted lawfully | R45 requires a demonstrated semantics-preserving alpha transform and a frozen cache inventory before a quote. H1 and H3 fail those prerequisites. Cache keys also omit repeat count (`judge_caller.py:513-520`), so existing entries cannot be counted as exact repeat coverage without validating stored score lengths. | Repair H1/H3 and version/enforce cache schema, then run a no-API dry-run manifest to produce exact missing calls, tokens, and model-specific pricing. Human approval must follow the quote, not precede it. |

## 3. SOFT issues

- `AGENTS.md:14-93` and `CLAUDE.md:14-93` still present P1-P7/JTI as the current project architecture. Per R49 they must later distinguish `TW_m`, `TI_m`, and `PTI_p`/`PTI_v0`, while retaining JTI/TIvar as historical compatibility code.
- `SYNC.md` is absent. This is not a blocker because the global instructions provide the relevant synchronization rule.
- Local `main` is one commit behind `origin/main`; the active branch is also one local commit ahead of its remote. Preserve that local commit and create PTI work only from updated `origin/main` after dependency resolution.
- The stale remote `origin/iclr2027-port` remains after merged PR #36. Do not recreate it.
- The dataset pins Lean 4.22 and Mathlib v4.22, but no checked-in `lake-manifest.json` or populated `.lake` dependency tree is present. Twenty-one pool files therefore remain dependency-blocked.
- The current shell runs under Rosetta (`x86_64`, translated process on ARM hardware). The active Python is `/Users/brandomiranda/uv_envs/no-gold-ref-judge/bin/python`, not the documented cert-judge environment. `uv run` currently resolves for macOS x86_64 and fails on the arm64-only `torch==2.7.0` wheel.
- The current cache is a shared JSON dictionary. It has no schema version, generation version, repeat count in its key, or atomic provenance manifest.
- The current eight-judge CLI manifest identifies `kind` but not explicit primary/control role. The likely 5/3 split is inferable but not frozen.
- The deterministic two-pass average disagrees with the checked-in average file for two unsafeMultiply rows (4.5 expected versus 5.0 checked in).
- QWK is sensitive to encoding of half scores. Historical code truncates; another audit rounds; a half-grid encoding gives a third result.
- Existing Exp27 tests do not cover all requirements in `04-EXP27-INTEGRATION-PLAN.md`: constant human/judge vectors, tied-bin rendering, within-item-only error bars, and a one-to-one join/drop audit still need explicit tests.
- The manuscript builds, but its abstract, methods, probe claims, alpha claims, panel-repair description, bridge figure, tables, and appendix remain legacy/incompatible with PTI-v0. They must be revised only after committed machine-readable PTI-v0 outputs exist.

## 4. Repository, dependency, and branch audit

### 4.1 Repository state

| Item | Observed state |
|---|---|
| Repository | `/Users/brandomiranda/cert-judge` |
| Current branch | `claude/ti2prime-validity-stability-scatter` |
| Current HEAD | `f102554c055bc6064551012d49b277c7cc1e2f9c` |
| Remote branch HEAD | `edf627426d6d0740dbd6a793e4ff985fc4e6e3fa` |
| Ahead/behind remote branch | ahead 1, behind 0 |
| Default branch | `origin/main` |
| `origin/main` | `c1021bfcd5ad9deee7dba97a8b9bac635b2962c2` |
| Local `main` | `932b4d33a8303f23a1e2c18da7e6d052b5fe1f41` (behind `origin/main` by 1) |
| Baseline dirty state | clean before this report; this report is the sole intended uncommitted change |
| Global rules revision | `/Users/brandomiranda/agents-config` at `8190074918da0c2b39e6763b1d46ba04e8215ec2`, clean after pull |

The local ahead commit is preserved. No branch, PR, label, manuscript, or source mutation occurred in this preflight.

### 4.2 Pull requests and overlap

| Dependency | State | Head/base | Checks/review | Action |
|---|---|---|---|---|
| ultimate-utils PR #44, `https://github.com/brando90/ultimate-utils/pull/44` | OPEN, MERGEABLE | `c8a6a9a70e32073d6cde2193958d570f08fd935e` -> `master` | no reported checks; no review decision | Review and test first. Local `/Users/brandomiranda/ultimate-utils` is clean at this exact head. |
| cert-judge PR #38, `https://github.com/brando90/cert-judge/pull/38` | OPEN, MERGEABLE | `edf627426d6d0740dbd6a793e4ff985fc4e6e3fa` -> `main` | no reported checks; no review decision | Review after #44 against the resolved dependency. Preserve Exp27. |
| cert-judge PR #36 | MERGED | stale remote `iclr2027-port` at `9f6fb13f3d46af432e0ca2c1698c4da53dca7be1` | historical | Do not recreate; optionally delete the stale remote branch only through a separate authorized cleanup. |

There is no `pti-v0` branch and no bridge branch. The only matching active branch is the Exp27 branch.

### 4.3 Exact dependency/branch plan

1. Preserve the current local-only `f102554` commit; do not rewrite or drop it.
2. Review/test ultimate-utils PR #44. Resolve its CI/review state and merge or pin it by explicit human decision.
3. Review/test cert-judge PR #38 against the resolved ultimate-utils SHA. Resolve its CI/review state and merge or explicitly stack it.
4. Fetch `origin`, fast-forward local `main` to `origin/main`, and verify a clean worktree.
5. Create `codex/pti-v0-final` from updated `main`. This branch owns spec, guidance refresh, implementation, tests, probe/panel manifests, frozen config, cached experiment, outer bridge data/figure, and results.
6. Create `codex/iclr2027-final` stacked on `codex/pti-v0-final`. This branch owns manuscript and paper-only assets.
7. Do not create a third bridge PR, recreate `iclr2027-port`, duplicate Exp27, push to `main`, or auto-merge.

## 5. Environment audit

| Component | Observed | Readiness |
|---|---|---|
| Host | Darwin kernel 25.6.0 on Apple Silicon; current process translated under Rosetta and reports `x86_64` | Use a native arm64 shell for execution. |
| `uv` | 0.8.3 | Available, but current architecture resolution fails. |
| Active Python | 3.11.6 at `/Users/brandomiranda/uv_envs/no-gold-ref-judge/bin/python` | Wrong project environment. Installed: NumPy 2.4.3, pandas 3.0.1, SciPy 1.17.1, scikit-learn 1.8.0. |
| `uv run` | Resolution failure for `torch==2.7.0` on macOS x86_64; project marker exposes only arm64 wheel | Recreate/sync under native arm64. |
| Global Lean | 4.18.0 | Not the dataset toolchain. |
| Pinned Lean | `/Users/brandomiranda/.elan/toolchains/leanprover--lean4---v4.22.0/bin/lean`, commit `ba2cbbf...`, arm64 | Used directly for the no-Mathlib audit. |
| Dataset toolchain | `leanprover/lean4:v4.22.0`; `lakefile.toml` requests Mathlib v4.22.0 | Correct pin, missing resolved Mathlib environment. |
| LaTeX | latexmk 4.83, pdfTeX 1.40.26 / TeX Live 2024 | Working. |

The active ICLR tree was copied to `/tmp` and built there with `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`. It produced a 23-page, letter-size PDF with no undefined-reference error. Conclusion and reproducibility material fit on page 9; the AI-use statement and references begin on page 10; appendices follow. Only minor float/underfull warnings were observed. No paper file was changed.

An accidental dependency initialization attempt created an incomplete untracked dataset `.lake` directory. The exact generated directory was stopped and moved to macOS Trash; it was never tracked and is recoverable. The repository returned to a clean baseline.

## 6. Canonical pipeline and integration points

### 6.1 Existing computations are legacy, not PTI-v0

- `py_src/cert_judge/hsj_scoring.py:65-73`: P1 is an arithmetic mean of normalized identity scores.
- `hsj_scoring.py:76-87`: P2/P3 use a pooled pairwise ordering AUC transformation.
- `hsj_scoring.py:90-112`: P4 uses pooled within-item variance with a `tau` scale.
- `hsj_scoring.py:164-205`: JTI is a weighted arithmetic mean of P1-P7.
- `experiments/04_veribench_validation/exp28_variance_aware_trust_index.py:68-133`: legacy TIvar reads only bug detail rows, drops undefined correlations, normalizes variance across the observed panel, and uses an epsilon-floored geometric expression.
- `experiments/04_veribench_validation/results_exp30_tivar_v3_all_models/`: checked legacy outputs. They must not be overwritten or renamed PTI-v0.

### 6.2 Repeat and cache schema

- `exp16_multi_judge_human_sets.py:509-525` stores `score_mean`, `score_std`, and JSON `repeat_scores` per item.
- Checked `results_exp16_final_robust/detail_rows.csv` contains 2,304 data rows: 576 human rows, 768 identity rows, and 960 bug rows. Each checked repeat list has length 3.
- `judge_caller.py:489-509` returns mean/std/raw scores.
- `judge_caller.py:513-520` hashes candidate, reference, optional prompt, namespace, and model, but not `n_repeats`.
- `judge_caller.py:522-525` returns any matching entry without verifying repeat length.
- `judge_caller.py:571-587` stores raw score lists but no cache schema/version metadata.

The repeat-count omission is correctness-critical: requesting a new repeat count can silently reuse an entry with the wrong number of calls. PTI-v0 must either add repeat count and scorer/generator versions to a new cache key or reject cached entries whose metadata and score length are not an exact match.

### 6.3 Human loader and duplicate behavior

- Default eight judges are defined at `exp16_multi_judge_human_sets.py:128-139`.
- `_load_tsv_scores` at lines 190-201 groups `(gold_file,candidate_file)` duplicates and takes their arithmetic mean.
- Gold resolution is basename-based at lines 204-219.
- Strict/pass1, lenient/pass2, and checked average are loaded independently at lines 450-453.
- The union join and silent `missing_gold`/`missing_candidate` skips are at lines 455-478.
- Human scores are joined to judge scores and evaluated at lines 616-633.
- Outputs and skipped-row records are written at lines 672-704.

### 6.4 Figures, tests, and build

- `make_fig2_tivar_cross_model.py:18-34` hardcodes three legacy panels; lines 59-82 join legacy TIvar and human rows; lines 128-138 fit an OLS guide and compute Spearman. Its output path targets the ICML tree. It is not a PTI-v0 outer-bridge generator.
- The active ICLR outer figure is inline TikZ at `main.tex:349-539`, with hardcoded legacy TIvar coordinates. It does not draw `y=x`, but it is still a legacy artifact and has no source-data contract.
- `py_src/cert_judge/ti2prime_plot.py:46-93` is a thin reusable wrapper around ultimate-utils. `show_diagonal=False` and `show_calibration_gap=False` are correct defaults.
- `experiments/27_ti_plot_like_scatter_plots/run_ti2prime_demo.py:62-93,145-194` loads the 72-row audited item join and produces the inner item-level diagnostic. It is not the outer judge-level bridge.
- `tests/test_ti2prime_plot.py` is the only checked test file. The zero-spend command `PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/test_ti2prime_plot.py -q` passed 8/8 in 3.57 seconds.
- ICLR build command: `cd paper_latex/ICLR_2027_submission && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` (preflight used a temporary copy).

### 6.5 Required PTI-v0 integration topology

Do not modify legacy JTI/TIvar semantics in place and do not leave a reference script orphaned under an experiment directory. The execution branch should use this topology:

1. Add a reusable, versioned numerical core in `py_src/cert_judge/pti_v0.py`, export its public API through `py_src/cert_judge/__init__.py`, and keep `metric_version="PTI_v0"` in every result record.
2. Add syntax-aware probe construction/validation as reusable code in `py_src/cert_judge/probe_validation.py`; it must emit structural manifests without importing the judge caller.
3. Add coherent vectors under `tests/data/PTI_V0_TEST_VECTORS_v4.json` and conformance tests under `tests/test_pti_v0.py`.
4. Add the data/cache adapter and CLI under `experiments/04_veribench_validation/run_pti_v0.py`, reusing the canonical panel/cache data but writing only to a new `results_pti_v0_v4/` directory.
5. Add the outer judge-level source-data and plot generator within the same PTI-v0 experiment tree.
6. Reuse Exp27/PR #38 for inner item-level diagnostics after dependency resolution; add its missing join/constant/tie/error-bar tests rather than duplicating plotting code.
7. Add the concise frozen spec and decision record under `docs/spec/`; explicitly mark JTI/TIvar outputs as legacy compatibility artifacts.

## 7. Structural probe manifest summary

### 7.1 Audited base pool and method

The historical Exp8 CSV resolves to 184 file rows: 150 from the older VeriBench root plus 34 non-overlapping rows from the newest append. There are only 183 unique content hashes because these two files are byte-identical:

- `security_python/safe/2_no_executable_escalation_safe.lean`
- `security_python/vulnerabilities/2_executable_escalation.lean`

Structural validity was determined from source construction, byte/content comparison, intended ordering, and Lean parsing/elaboration. Judge scores and score constancy were not used.

Of the 184 originals, 163 do not import Mathlib and all 163 elaborate with the pinned Lean 4.22 binary. The other 21 are dependency-blocked because Mathlib is not resolved locally:

- older `cs_set`: `binary_search`, `bubble_sort`, `counting_sort`, `depleted_binary_search`, `edit_distance`, `heap_sort`, `insertion_sort`, `lcs`, `merge_sort`, `quick_sort`, `selection_sort`;
- older `real_code`: `fractions_core`, `statistics_mean`, `statistics_median`, `statistics_variance`;
- newest `cs_set`: `bfs`, `dfs`, `dijkstra`;
- newest `realcode_set`: `11_statistics_median`, `14_fractions_core`, `30_statistics_covariance`.

The 21 are `DEPENDENCY_BLOCKED`, not silently valid or invalid on compilation grounds.

### 7.2 Bug ladders

Compile/elaboration results for the 163 dependency-free rows, excluding the clean L0 base:

| Bug level | Pass | Fail |
|---|---:|---:|
| L1 | 93 | 70 |
| L2 | 29 | 134 |
| L3 | 22 | 141 |
| L4 | 23 | 140 |

Only 17/163 have all modified levels elaborate, and those 17 use comment/no-op fallbacks at L1/L3 and append a trivial `example : True` at L4 instead of forming a documented cumulative semantic degradation. They are:

- `veribench/humaneval_set/humaneval_32_poly.lean`;
- newest `veribench/security_set/security_6858/vulnerabilities/{5_unsafeFormatString,6_unsafeSQLQuery,7_unsafeCommandExecution,8_crossSiteScripting,9_pathTraversal}.lean`;
- all 11 newest `veribench/security_set/security_6858/safe/{0_unsafeCopy_safe,...,10_serverSideRequestForgery_safe}.lean` files.

The other 146 dependency-free ladders have at least one Lean failure. Therefore:

| Family | VALID | STRUCTURALLY_INVALID | DEPENDENCY_BLOCKED |
|---|---:|---:|---:|
| Bug ladder | 0 | 163 | 21 |

Byte-distinct comments do not turn a no-op into a semantic probe. No cached bug score may enter PTI-v0 from this generator.

### 7.3 Missing-spec ladders

Compile/elaboration results for the 163 dependency-free rows, excluding clean L0:

| Spec level | Pass | Fail |
|---|---:|---:|
| L1 | 27 | 136 |
| L2 | 46 | 117 |
| L3 | 43 | 120 |
| L4 | 53 | 110 |

The generator removes a fraction from the already modified previous level and, when it cannot find theorem blocks, truncates an arbitrary fraction of remaining lines (`exp8...py:307-319`). In 111/184 rows at least one level uses this tail-truncation fallback; theorem count is not strictly decreasing for the same 111 rows.

Only 18/163 dependency-free rows elaborate at all modified levels: 16 security fallback cases plus `real_code/queue_threadsafe.lean` and newest `realcode_set/27_graphlib.lean`. The latter two have plausible theorem removal at L1-L3 but fall back to arbitrary near-empty truncation at L4. Consequently:

| Family | VALID | STRUCTURALLY_INVALID | DEPENDENCY_BLOCKED |
|---|---:|---:|---:|
| Missing-spec ladder | 0 | 163 | 21 |

No cached missing-spec score may enter PTI-v0 from this generator.

### 7.4 Alpha-renaming

Audit results:

- 184/184 outputs differ in bytes from their original, but 184/184 contain malformed `:=:=`.
- 87 files expose single-letter binders to the regex; in 70, those identifiers also occur in the proof body, which the transformer does not rename.
- 163/163 dependency-free transformed artifacts fail Lean 4.22 elaboration.
- Fallback comments and `compiled=None` are not evidence of semantic preservation.

Representative SHA-256 manifest:

| File | Original SHA-256 | Alpha SHA-256 | Result |
|---|---|---|---|
| `binary_search.lean` | `65f2345d0a508677bddc6f179a9e7eba7f27b07e6b87e2e1904be67269c8557c` | `ed87fba274b485570c196006d7510be5a786474fbc6ede889464c2a6fdf94aec` | malformed `:=:=`; invalid |
| `bubble_sort.lean` | `5cd1679538927bb8ee480dd514d8d52963d57221d14667b0a48552b7cc1434e7` | `f23ceb67423975245fbea9fce276772b15b0ec0d6e2bde688723f5972f15763b` | malformed `:=:=`; invalid |
| `counting_sort.lean` | `9b1ba7177dd23fe572945592b21ae34bcb90cca7fd0865c8749c4e7cf84d74a1` | `21cf15caf065aab2bab20a7f830cf673f451fab338d27e7c9246fb16749155e5` | malformed `:=:=`; invalid |
| `depleted_binary_search.lean` | `80e66fcff1bd99b23928d8d8efa0a60268da1619583d2d76c3ec63466b33ad2a` | `3d446f7b913ae1d9981edde3f16ff0ec84eb9ad369a4e44ee72e6771fc3bff34` | malformed `:=:=`; invalid |
| `edit_distance.lean` | `40bb92ebf3ce276da0b3787f01a82c5b2656bab1998c9799ea1c7c46df585e47` | `c3e57ac997e0a9ccb6c8e0bd3fb3629ab4b78188c3f16e31c971d1d7c5aee300` | malformed `:=:=`; invalid |

`P_eqalpha`: **HARD BLOCKED / NOT COMPUTABLE / NOT RUN**. If alpha remains declined or blocked after repair attempts, R45 permits only the explicitly labeled three-property proxy `PTI_{eq,bm,ms}`—but H2 currently blocks that proxy as well.

## 8. 72-to-75 panel audit

### 8.1 Label reconstruction

- Strict file `ethan_human_scores_20260425.tsv`: 75 rows, 75 unique keys.
- Lenient file `ethan_human_scores_ORIGINAL.tsv`: 78 rows, 75 unique keys. The three `4_json_decoder` candidates each appear with scores 1 and 2; the declared loader mean yields 1.5.
- Checked average file: 75 unique keys.
- Conditional old-key to new-key rename yields 75 unique pairs = 25 problems x 3 generations, with 25 rows for each agent index 0/1/2.
- A deterministic average of the duplicate-collapsed strict and lenient views matches the checked average for 73/75 rows. UnsafeMultiply agent1 and agent2 should be 4.5 from strict 4 and lenient 5, but the checked average contains 5.0.

### 8.2 Candidate preservation succeeds

The three historical candidate artifacts are byte-identical to the current renamed candidates:

| Historical candidate | Current candidate | SHA-256 |
|---|---|---|
| `agent_codex.lean` | `1_unsafeMultiply_safe__agent0.lean` | `3436f62b433971dc275197fee6a5c2cc24a11b2d0f13752dfca13738a592f539` |
| `agent_claude.lean` | `1_unsafeMultiply_safe__agent1.lean` | `9f0ad9d9e160f0b042593b49d74fc379b232831d47229cb7ef063abf6c7661c7` |
| `agent_llama.lean` | `1_unsafeMultiply_safe__agent2.lean` | `3d966d3d146d2fdea18a74712d137ebe898d7207fb7d0277660e5664e14c4ee7` |

`run_veribench_validation.py:187-188` contains the historical candidate alias, corroborating this mapping.

### 8.3 Gold preservation fails

| Artifact | SHA-256 | Interpretation |
|---|---|---|
| Historical `results/.../0_unsafeMultiply_safe/gold.lean` | `cc14eec1c55427da69df42cad1b5e291caed5396a7d0bf4cd11c844fdcc5facf` | Historical rated gold |
| Current `security_6858/1_unsafeMultiply.lean` | `cc14eec1c55427da69df42cad1b5e291caed5396a7d0bf4cd11c844fdcc5facf` | Exact match; vulnerable/unsuffixed |
| Intended current `security_6858/safe/1_unsafeMultiply_safe.lean` | `7b3c09af01aed148fc38f13ec827423bb54bf73f299b8111e2f2ad91e283a346` | Different 151-byte safe gold |

The same historical gold hash appears in both `results/veribench/...` and `results_security/veribench/...`. Old labels in `experiments/ethan_hand_labels/security_6858.csv:5-7` are all 5, and the pipeline's `_resolve_gold` explicitly selects `1_unsafeMultiply.lean` for the stale key. The apparent “rename” therefore changes the reference artifact. R46 is not satisfied.

### 8.4 Conditional statistics—not an approved repair

For audit visibility only, the following statistics were recomputed in memory under the counterfactual assumption that the three old labels could be assigned to the new safe key. They must not be published as the repaired panel without a human decision.

| Statistic | Current 72 | Conditional 75 | Change |
|---|---:|---:|---:|
| Spearman | 0.2486159061 | 0.2802151008 | +0.0315991947 |
| Pearson | 0.3747442289 | 0.3978385530 | +0.0230943241 |
| Kendall tau-b | 0.2213610111 | 0.2513644904 | +0.0300034793 |
| QWK, historical integer truncation | 0.3717812300 | 0.3895348837 | +0.0177536537 |
| QWK, round diagnostic | 0.3142050800 | 0.3360000000 | +0.0217949200 |
| QWK, half-grid diagnostic | 0.3951417004 | 0.4113029827 | +0.0161612823 |
| MAE | 0.7708333333 | 0.7666666667 | -0.0041666666 |
| MSE | 1.1215277778 | 1.1033333333 | -0.0181944445 |
| RMSE | 1.0590220856 | 1.0503967504 | -0.0086253352 |
| Signed lenient-minus-strict bias | 0.2986111111 | 0.3133333333 | +0.0147222222 |
| Exact agreement | 0.3750000000 | 0.3733333333 | -0.0016666667 |
| Agreement within 1 point | 0.8472222222 | 0.8533333333 | +0.0061111111 |

Conditional 75-view means are strict 3.600000, lenient 3.913333, and deterministic average 3.756667. The checked average file instead has mean 3.770000 because of the two 5.0-versus-4.5 discrepancies.

Using the existing item-bootstrap convention (10,000 resamples, seed 0, percentile interval), the inter-round intervals change as follows:

| Statistic | Current 72 CI | Conditional 75 CI | Valid replicates |
|---|---|---|---:|
| Spearman | [-0.0154346, 0.4886505] | [0.0247732, 0.5047378] | 10,000 |
| Pearson | [0.0759260, 0.6035372] | [0.1100012, 0.6179023] | 10,000 |
| Kendall tau-b | [-0.0156935, 0.4417162] | [0.0217084, 0.4668630] | 10,000 |
| QWK, historical truncation | [0.0726257, 0.5808785] | [0.1040527, 0.5901639] | 10,000 |

Panel outcome: **Option B BLOCKED**. Keep the 72-row analysis until a data owner decides how the three rows should be interpreted or rerated.

## 9. Cache coverage and spend gate

### 9.1 Cache inventory

The main cache `experiments/02_reviewer_response_neurips_math_ai_2026/results/judge_cache.json` contains 27,102 entries and 125,267 stored score calls, counting the length of each `scores` list.

Relevant coverage:

| Judge/scope | Cached entries | Stored calls | What it actually covers |
|---|---:|---:|---|
| GPT-5.3 Exp8 identity namespace | 732 | 2,172 | 183 unique reference contents x 4 variants, nominal r3; published CSV has 184 rows because one content is duplicated. |
| GPT-5.3 Exp8 bug namespace | 915 | 2,715 | 183 reference contents x 5 levels, nominal r3; structurally invalid generator. |
| GPT-5.3 Exp8 missing-spec namespace | 915 | 2,715 | 183 reference contents x 5 levels, nominal r3; structurally invalid generator. |
| GPT-5.3 Exp9, each prompt x each of ORIGINAL/RENAME/REORDER/STYLE/ALPHA | 183 each | 915 each | Reference-as-candidate self pairs, r5 namespace; alpha is malformed. |
| GPT-5.3 Exp16 P1/P4/P8, each | 288 each | 864 each | 72 human pairs + 24 x 4 identity variants + 24 x 5 bug levels, nominal r3. No spec ladder. |
| GPT-5.3 BAD_STRINGY | 576 untagged plus a separate 288-entry suffix namespace | 1,728 plus 1,440 | Two prompt hashes/runs; 24-problem panel scope, no spec ladder. Exact role/version needs freezing. |
| GPT-4o-mini Exp16 P8/P4, each | 288 | 864 | 24-problem human/identity/bug scope; no spec ladder. Separate r5 namespaces contain 288/1,440 each. |
| Edit-distance and random controls | local | no paid calls | Recomputable after pool freeze. |

The default panel has six LLM configurations and two local controls. The likely headline roles are five primaries (GPT-5.3 P8/P4/P1 and GPT-4o-mini P8/P4) plus three controls (BAD_STRINGY, edit distance, random), but role is not explicit in a machine-readable manifest.

None of the reference-pool bug/spec/alpha cache is admissible for PTI-v0. Real panel candidate originals are cached for the current 72 rows for each Exp16 LLM judge; the three disputed unsafeMultiply rows are absent from that join. There is no validated alpha-transformed real-candidate coverage.

### 9.2 Alpha-only quote

- Status: **NOT ESTIMATED—PROHIBITED BY FAILED R45 VALIDITY GATE**.
- Missing call count: **NOT COMPUTABLE** until the alpha transformer and typed pool are valid/frozen.
- Cost estimate: **NOT COMPUTABLE** until exact model list, pool, repeat count, valid cache cells, token counts, and applicable pricing are frozen.
- Calls authorized now: **0**.
- Preflight calls made: **0**.
- Preflight spend: **$0**.

This is intentional compliance with the master prompt: when alpha is not demonstrably semantics-preserving, mark it hard blocked and do not estimate spend.

### 9.3 Optional RENAME/REORDER/STYLE quote

- Status: **SEPARATELY NOT ESTIMATED**.
- Calls authorized now: **0**.
- Reason: these transforms are diagnostic-only under R45, the base pool is unresolved, and each transform must independently pass structural/no-op/Lean validation. They may not be bundled into an alpha approval.

After repair, the exact missing-call calculation must be:

`N_missing(T) = sum_{aj in frozen LLM judges} sum_{f in frozen pool} max(0, K_aj - N_valid_cached(aj,f,T))`

where `N_valid_cached` counts only entries with exact model, prompt hash, namespace/schema version, candidate hash, reference hash, transform/generator version, and stored repeat length. Original/base calls are subtracted only under that exact match. Alpha is quoted once; optional diagnostics are quoted as three separate rows.

## 10. Statistical freeze audit

### 10.1 Frozen by the current authority chain

| Decision | Frozen value |
|---|---|
| Metric version | `PTI_v0` on every output row |
| Base unit | `f=(i,a,q)`; generation `q` remains part of the experimental unit |
| Judge repeat | `r`, aggregated locally within each `(aj,f,T,ell)` only |
| Human pass/rater | `u` for repeated human pass under its stated protocol; do not pair it with `q` or `r` |
| Ladder level | `ell`, increasing with degradation |
| Repeat aggregate | Median |
| Ladder association | Spearman primary; Kendall tau-b robustness |
| Orientation | `C=(1-rho)/2`; negative association is desirable |
| Repeat instability | Mean over levels of `2*sd(ddof=0)`, clipped/validated per spec |
| Single repeat | `K_aj=1` removes the stability factor, so ladder factor equals `C` |
| GM | Exact-zero-first, log-domain geometric mean; no epsilon floor in the headline |
| Constant score ladder | If structurally valid, `constant_score_ladder=True`, undefined raw Spearman, and `C=0`; do not exclude it |
| Structurally invalid probe | Globally exclude with an explicit reason independent of judge outputs |
| Missing score | Coverage failure; never impute zero; threshold breach -> property `NOT_COMPUTABLE`, screen `DEFER` |
| Human criterion | Raw `TI_m1(aj)=Spearman_i(median_r judge score, human score)` in [-1,1] |
| Outer bridge | Spearman over judges primary; Kendall tau-b robustness; no `y=x`; no `|PTI-TI_m1|` level metric |
| Label views | Averaged labels primary; strict and lenient robustness views |
| Reporting roles | Primaries-only headline; pooled controls secondary |
| Bootstrap iterations/seed | 10,000, seed 0 |
| Property/PTI resampling unit | Cluster over `f=(i,a,q)`, carrying all variants/levels/repeats; paired cluster indices across properties |
| Human criterion resampling | Cluster over the paired item/generation unit while preserving actual pass provenance |
| Bridge resampling | Judges |
| Alpha headline | Alpha only; RENAME/REORDER/STYLE are separate diagnostics |
| Blocked alpha fallback | Explicitly labeled `PTI_{eq,bm,ms}`, never four-property PTI-v0; currently also blocked by invalid ladders |
| Claim language | A pre-specified behavioral screen, not proof of trustworthiness; logical falsification only under Route A or explicit Route B assumptions |

### 10.2 Unresolved and must be frozen before results

1. **Exact pool manifest:** 184 reference rows, 75 panel candidates, and 471 full candidates are different estimands. Choose one typed `f=(i,a,q)` pool and record exclusions/hashes.
2. **Judge manifest:** explicit `judge_id`, model/family, prompt hash/name, decoding configuration, `K_aj`, aggregate, primary/control role, cache namespace/version, and inclusion reason.
3. **Coverage threshold:** R43 requires a pre-frozen threshold but does not set it. Do not inherit R36's 0.20 without a new ruling because R36 attached it to the superseded constant-exclusion policy.
4. **CI algorithm:** 10,000/seed 0 is frozen; exact percentile interpolation versus basic/BCa and endpoint handling are not stated coherently across artifacts. Freeze one method and test it.
5. **Undefined bridge bootstrap policy:** with only five likely primaries, resamples can have constant vectors or insufficient unique judges. Freeze validity rules, minimum valid replicate count/fraction, and the displayed fallback.
6. **SESOI DGP:** a target around `rho0=0.5`, empirical range 0.1-0.9, 10,000 simulations, and seed 0 appear in the handoff, but the rank-correlation generator, tie structure, candidate-count/top-1 rule, family composition, missingness, and operating characteristic are not fully specified.
7. **QWK encoding:** truncation, ordinary rounding, and doubled half-grid encoding differ. Freeze one primary diagnostic or omit QWK from the headline.
8. **Panel disposition:** 72 existing rows versus rerated/redefined 75 rows.
9. **Human-pass semantics:** there is one person and two rubric-strictness views, not two independent raters. The bootstrap must preserve that structure rather than resampling `u` as independent people.
10. **Per-property screening thresholds:** none exist. Until thresholds and an evaluation design are frozen, prohibit quantitative claims about “human validations saved,” false-pass rate, false-reject rate, or a PASS-SCREEN operating point.
11. **Held-out design:** current bridge numbers are validation-set evidence. No threshold or model selection may be tuned after PTI-v0 results are seen.

## 11. Figure and manuscript audit

### 11.1 Inner versus outer figures

- Exp27 is correctly scoped as the inner item-level `TI_2'` diagnostic. Its default omits both an identity line and calibration gap, and the checked 8-test suite passes.
- The new outer figure must have one point per judge, `PTI_v0` on x in [0,1], raw `TI_m1` on y in [-1,1], role/family encoding, Spearman/Kendall, judge-bootstrap interval, `n_judges`, and valid replicate count.
- The outer figure must not contain `y=x`, level-gap MAE, or “distance to perfect level agreement” language.
- No PTI-v0 outer source CSV/JSON or generator exists yet. The inline ICLR TikZ and `make_fig2_tivar_cross_model.py` are legacy TIvar products and cannot be renamed.

### 11.2 Active manuscript

The active target is `paper_latex/ICLR_2027_submission/main.tex`; it must be revised in place on the stacked paper branch. Do not re-port from TMLR and do not edit historical paper trees.

Current incompatibilities include:

- `main.tex:87-88` and `116-121`: abstract/contributions report legacy variance-aware bridge claims and call the property vector identity/bug/spec/stability.
- `main.tex:194`: current bridge composition treats stability according to an older construction.
- `main.tex:220-250`: the methods use the legacy 184 reference tensor and TIvar formula rather than the final PTI-v0 numerical definition.
- `main.tex:284-288,653-687`: the panel prose says the dropped rows are only a stale key, which the hash audit disproves, and the checked averaged view is not a deterministic average for two rows.
- `main.tex:307-345,584`: bug/spec/alpha results are based on structurally invalid transformations and cannot support PTI-v0 claims.
- `main.tex:349-585`: bridge figure/tables and all associated values are legacy TIvar evidence, not PTI-v0.
- `main.tex:622-627`: alpha is described as semantics-preserving, but the actual transformer is malformed and signature-only.
- `main.tex:673-675`: Appendix A explicitly endorses the now-failed rename repair as an option.
- `main.tex:831`: appendix acknowledges legacy legends but does not provide the required PTI-v0 result-status/source mapping.

The manuscript is currently anonymous in its author block and builds successfully in a temporary copy. The core conclusion is on page 9, with uncounted statements/references beginning after it. That layout success does not validate the scientific content. All new numbers must come from committed machine-readable outputs, and legacy values must be marked historical or removed—not renamed.

## 12. Exact execution command list

These commands were **not run** unless explicitly identified above as a preflight test/build. Commands labeled “after implementation” define the required CLI contract; those entry points do not exist yet and must be implemented on PR A. No paid command is authorized.

### 12.1 Dependency review and branch creation

```bash
git -C /Users/brandomiranda/ultimate-utils fetch origin
git -C /Users/brandomiranda/ultimate-utils status --short --branch
git -C /Users/brandomiranda/ultimate-utils diff --check origin/master...c8a6a9a70e32073d6cde2193958d570f08fd935e
PYTHONDONTWRITEBYTECODE=1 /Users/brandomiranda/uv_envs/no-gold-ref-judge/bin/python -m pytest -p no:cacheprovider -q

cd /Users/brandomiranda/cert-judge
git fetch origin
git status --short --branch
PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/test_ti2prime_plot.py -q

# Only after human resolution of PRs #44 then #38:
git switch main
git pull --ff-only origin main
git status --short --branch
git switch -c codex/pti-v0-final
```

Before the branch switch, verify that `f102554c055bc6064551012d49b277c7cc1e2f9c` remains reachable and that this preflight report has been deliberately preserved or copied into the new branch workflow. Do not reset the current branch.

### 12.2 Native environment and dependencies

```bash
/usr/bin/arch -arm64 /bin/zsh -lc '
  cd /Users/brandomiranda/cert-judge &&
  uv venv /Users/brandomiranda/uv_envs/cert-judge &&
  source /Users/brandomiranda/uv_envs/cert-judge/bin/activate &&
  uv pip install -e . &&
  uv sync --active
'

/Users/brandomiranda/.elan/toolchains/leanprover--lean4---v4.22.0/bin/lean --version
cd /Users/brandomiranda/cert-judge/data/veribench_dataset/lean_src
lake update
lake build
```

`lake update/build` may access the network and materialize `.lake`; run it only during authorized execution, not the preflight.

### 12.3 Conformance gate (after implementation)

```bash
cd /Users/brandomiranda/cert-judge
PYTHONDONTWRITEBYTECODE=1 uv run python -m pytest -p no:cacheprovider \
  tests/test_pti_v0.py tests/test_ti2prime_plot.py -q

PYTHONDONTWRITEBYTECODE=1 uv run python -m pytest -p no:cacheprovider -q
```

The conformance test must load `tests/data/PTI_V0_TEST_VECTORS_v4.json`, enforce absolute tolerance `1e-12`, and pass before any real-data aggregation.

### 12.4 Structural manifests (after implementation, no API)

```bash
cd /Users/brandomiranda/cert-judge
uv run python experiments/04_veribench_validation/run_pti_v0.py audit-probes \
  --metric-version PTI_v0 \
  --pool-manifest experiments/04_veribench_validation/pti_v0_v4/base_pool.json \
  --lean-bin /Users/brandomiranda/.elan/toolchains/leanprover--lean4---v4.22.0/bin/lean \
  --require-elaboration \
  --reject-noops \
  --reject-comment-fallbacks \
  --no-api \
  --out experiments/04_veribench_validation/results_pti_v0_v4/probe_validity_manifest.json
```

The command must fail nonzero if any included probe lacks a documented semantic step or an elaboration result. It must never import or initialize an API client.

### 12.5 Panel audit (after human disposition, no API)

```bash
cd /Users/brandomiranda/cert-judge
uv run python experiments/04_veribench_validation/run_pti_v0.py audit-panel \
  --strict experiments/04_veribench_validation/data/ethan_human_scores_20260425.tsv \
  --lenient experiments/04_veribench_validation/data/ethan_human_scores_ORIGINAL.tsv \
  --checked-average experiments/04_veribench_validation/data/ethan_human_scores_avg_two_passes_20260425.tsv \
  --duplicate-rule mean \
  --unsafe-multiply-policy APPROVED_POLICY_PLACEHOLDER \
  --bootstrap-iters 10000 \
  --seed 0 \
  --no-api \
  --out experiments/04_veribench_validation/results_pti_v0_v4/panel_audit
```

Replace `APPROVED_POLICY_PLACEHOLDER` only with a recorded human choice; the CLI must otherwise refuse to write canonical derivatives.

### 12.6 Cache inventory and spend quote (after valid pool/transforms, no API)

```bash
cd /Users/brandomiranda/cert-judge
uv run python experiments/04_veribench_validation/run_pti_v0.py inventory-cache \
  --frozen-config experiments/04_veribench_validation/pti_v0_v4/frozen_config.json \
  --cache experiments/02_reviewer_response_neurips_math_ai_2026/results/judge_cache.json \
  --require-exact-repeat-count \
  --no-api \
  --out experiments/04_veribench_validation/results_pti_v0_v4/cache_inventory.json

uv run python experiments/04_veribench_validation/run_pti_v0.py quote-spend \
  --frozen-config experiments/04_veribench_validation/pti_v0_v4/frozen_config.json \
  --cache-inventory experiments/04_veribench_validation/results_pti_v0_v4/cache_inventory.json \
  --transforms ALPHA \
  --dry-run \
  --no-api \
  --out experiments/04_veribench_validation/results_pti_v0_v4/spend_alpha_only.json

uv run python experiments/04_veribench_validation/run_pti_v0.py quote-spend \
  --frozen-config experiments/04_veribench_validation/pti_v0_v4/frozen_config.json \
  --cache-inventory experiments/04_veribench_validation/results_pti_v0_v4/cache_inventory.json \
  --transforms RENAME REORDER STYLE \
  --dry-run \
  --no-api \
  --out experiments/04_veribench_validation/results_pti_v0_v4/spend_optional_diagnostics.json
```

The CLI must print and persist exact model-by-model calls, repeats, input/output token assumptions, unit prices with an as-of date, cached deductions, and upper-bound cost. It must not load keys in dry-run/no-API mode.

There is deliberately **no paid alpha command in this report**. It may be generated only after H1-H3/H8 are resolved and a human signs the exact alpha-only quote. Optional diagnostics require a separate approval record.

### 12.7 Zero-spend cached computation and pre-bridge freeze (after blockers)

```bash
cd /Users/brandomiranda/cert-judge
uv run python experiments/04_veribench_validation/run_pti_v0.py compute-properties \
  --frozen-config experiments/04_veribench_validation/pti_v0_v4/frozen_config.json \
  --probe-manifest experiments/04_veribench_validation/results_pti_v0_v4/probe_validity_manifest.json \
  --cache-inventory experiments/04_veribench_validation/results_pti_v0_v4/cache_inventory.json \
  --cache-only \
  --no-api \
  --bootstrap-iters 10000 \
  --seed 0 \
  --out experiments/04_veribench_validation/results_pti_v0_v4/properties

git diff --check
git status --short
```

Commit the spec, vectors, implementation, tests, structural manifest, panel disposition, judge/pool manifest, frozen statistics, alpha status, and zero-spend property outputs before any bridge computation. Do not run the next commands until that pre-bridge commit exists.

### 12.8 Bridge, figures, and manuscript (only after pre-bridge commit)

```bash
cd /Users/brandomiranda/cert-judge
uv run python experiments/04_veribench_validation/run_pti_v0.py compute-criterion \
  --frozen-config experiments/04_veribench_validation/pti_v0_v4/frozen_config.json \
  --no-api \
  --out experiments/04_veribench_validation/results_pti_v0_v4/criterion

uv run python experiments/04_veribench_validation/run_pti_v0.py compute-bridge \
  --frozen-config experiments/04_veribench_validation/pti_v0_v4/frozen_config.json \
  --properties experiments/04_veribench_validation/results_pti_v0_v4/properties \
  --criterion experiments/04_veribench_validation/results_pti_v0_v4/criterion \
  --bootstrap-iters 10000 \
  --seed 0 \
  --no-api \
  --out experiments/04_veribench_validation/results_pti_v0_v4/bridge

uv run python experiments/04_veribench_validation/run_pti_v0.py plot-outer-bridge \
  --bridge experiments/04_veribench_validation/results_pti_v0_v4/bridge \
  --no-diagonal \
  --no-level-mae \
  --out experiments/04_veribench_validation/results_pti_v0_v4/figures

git switch -c codex/iclr2027-final
cd paper_latex/ICLR_2027_submission
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
pdfinfo main.pdf | rg 'Pages|Page size'
```

Run independent code QA before PR A and independent paper QA before PR B. Stage only intended paths, scan for secrets/identifiers, and follow the global commit/push rules only in the later execution session. This preflight creates no commit and no push.

## 13. Human approvals required

1. **Dependency disposition:** approve merge/pin/stack outcome for ultimate-utils #44, then cert-judge #38.
2. **Base pool:** select the typed `f=(i,a,q)` pool and approve its exact manifest and exclusions.
3. **Panel:** choose 72 as-is, rerate three rows against the correct safe gold, or redefine/document the three labels as vulnerable-gold ratings. A rename-only 75 repair is not evidence-supported.
4. **Average labels:** approve deterministic recomputation (including the two 4.5 values) or document another rule.
5. **Judge manifest:** approve exact judge configurations, families, decoding/repeats, and primary/control roles.
6. **Coverage:** set the missing-score threshold and DEFER semantics under R43; do not silently reuse R36 theta.
7. **Bootstrap/SESOI:** approve CI algorithm, undefined-replicate rule, human-pass clustering, SESOI target, and full simulation DGP.
8. **QWK:** approve half-score encoding or remove QWK from primary reporting.
9. **Screening claims:** either freeze per-property thresholds and an operating-characteristic design or prohibit “human validations saved”/PASS-SCREEN quantitative claims.
10. **Alpha engineering gate:** approve the replacement transformer only after a complete structural/elaboration manifest.
11. **Alpha spend:** after the transformer and pool pass, approve the exact alpha-only call/cost quote. Optional RENAME/REORDER/STYLE requires a separate approval.
12. **Route and manuscript claims:** approve Route A versus explicit Route B assumptions/margins and the final scoped claim language before the paper rewrite.
13. **Git/PR actions:** authorize later commits, pushes, and draft PR creation on the two R48 branches. No merge to `main` is implicit.

## 14. Preflight acceptance checklist

- [x] Global rules pulled and recorded.
- [x] Repository/branch/PR topology audited without mutation.
- [x] Current scoring, cache, panel, legacy output, figure, test, and build paths traced.
- [x] Probe validity separated from judge behavior.
- [x] Bug/spec generators audited with pinned Lean on all dependency-free rows.
- [x] Alpha source, hashes, malformed tokens, occurrence consistency, and Lean failures audited.
- [x] 72-to-75 candidate and gold provenance reconstructed in memory/temp only.
- [x] Conditional changed panel statistics reported and clearly barred from publication.
- [x] Cache coverage inventoried; no invalid cached tensor accepted.
- [x] Alpha-only and optional diagnostics reported separately; no spend estimated after failed gate.
- [x] Frozen versus unresolved statistical decisions separated.
- [x] Exp27 inner diagnostic distinguished from the outer bridge.
- [x] ICLR manuscript built in a temporary copy and legacy incompatibilities identified.
- [x] No PTI-v0 bridge result computed or revealed.
- [x] No API key loaded, paid inference made, source/label/manuscript edited, branch changed, commit created, or push performed.
- [ ] HARD blockers resolved.

Final preflight state: **BLOCKED; stop here.**
