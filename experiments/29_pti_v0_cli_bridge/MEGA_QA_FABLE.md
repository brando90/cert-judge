# Final Mega-QA stage record — Claude Fable 5 (fresh context)

**TLDR:** A fresh adversarial pass independently reconstructed every Experiment 29 number from `results/scores.json` and the raw batches and reconciled every hash, commit-ordering, PR-topology, secret, and manuscript number. The evidence bundle is sound and supports only the below-SESOI/inconclusive interpretation; the applied fixes are presentation and provenance-wording corrections.

- Date: 2026-08-27 (America/Los_Angeles)
- Reviewer: Claude Fable 5, fresh session, effort `max`, with four read-only subagents (raw-batch provenance, numerics code review, paper build/visual QA, repository provenance)
- Baseline: `codex/iclr2027-final` at `ab791cf35995a9386d1fdb2d846c56dd1affeb03` over `origin/main` `b488de9fc11e87952e05e9e4ecfff38dafbe0c17`; draft PR #40
- Mode: no provider API, no LLM-provider key, no `score` rerun, no Git history change, no commit/push/merge, no external-service change

## Independently reproduced (all PASS)

- Scores: 14,184 records, 4,728 cells each with repeats {0,1,2}, all finite in [0,1]; cell set equals `score_requests.json`; `scores.json` SHA-256 `c51a2ee7…` is bound into `properties.json` and `criterion.json`.
- Raw evidence: 774 accepted `<batch>__r{0,1,2}.json` + 774 stdout + 774 stderr + 4 failure records; 0 schema violations; 0 of 10,638 LLM record bindings and 0 of 3,546 local-control values disagree with an independent re-implementation of the frozen formulas; every batch is artifact-disjoint within the 16-case / 180,000-byte caps.
- Structural binding: all 6,816 request rows bind their candidate/reference hashes to the v4 structural manifest (86/49/63/67 valid sets; levels 0..4; alpha pairs share the reference and differ in candidate); all 470 pool candidates exist on disk with matching hashes.
- Properties, ladder diagnostics, artifact-cluster bootstraps (per-judge seed `0 + judge index`), zero-factor listings, and the hard gate: reproduced with scipy/numpy to 1e-9 (point estimates), exactly for replicate counts and intervals.
- Human criterion: 72 rows match the v4 panel manifest and TSV, average = mean(strict, lenient), 75 = 25 problems × 3 generations before the keep72 policy; all 24 judge/view Spearman, Kendall tau-b, and paired-item bootstraps reproduced exactly (derived seeds included).
- Bridge: primaries `-0.3535533906` / tau-b `-0.3162277660` / `[-1.0, 0.3952847075]` / 6,647 valid; pooled `-0.2474358297` / `-0.2142857143` / `[-0.8164965809, 0.2567762955]` / 6,521 valid; both leave-one-family-out `NOT_COMPUTABLE`; four exploratory per-property analyses; three-property variant identical — all exact, for both `bridge_pti_v0.json` and `bridge_eq_bm_ms.json`.
- SESOI: all nine rows reproduced exactly with exact-rational arithmetic (a naive float Pearson gives `0.49999999999999994` at the attainable `rho = 0.5` boundary, which is the reviewer's artifact, not the pipeline's); 27.1% positive-rule power at `rho = 0.5`; 8 of 120 proxy orders are CI-positive with five primaries.
- Figures: `generate_bridge_figure.py` regenerates `outer_bridge_source_data.{csv,json}` byte-identically; all hashes in STATUS/REPORT/number map/sidecars recompute (33/33); commit ordering 395efdc (freeze, no outputs) → 6f55c44 (scores/properties/criterion, no bridge) → 540c43f (bridge/SESOI/figures) holds with no post-freeze drift.
- Paper: `latexmk` build clean (0 overfull, 0 unresolved references/citations, 0 BibTeX warnings, anonymous metadata); every Exp29 number in the PDF matches its JSON/CSV authority to printed precision, including all 40 appendix intervals; retained historical numbers match their Exp13/16/18/22/23/24/26/28 authorities.
- Tests: 71 passed + 1 skipped in the bare cert-judge environment; 79 passed with `uutils` (ultimate-utils PR #44 checkout plus `dill`, `networkx`, `lark`) on the path. `run_pti_v0_cli.py status` reports 774/774, 4,728 cells, 0 invalid, `$0`.
- Secrets/direct-API scan over the 2,470-file diff: 0 hits; provider strings occur only inside forbidden-string test assertions and the runner's scrub list.
- PR topology: #40 is draft, base `main`, `MERGEABLE`/`CLEAN`, head = local HEAD = `origin/codex/iclr2027-final`; #39 closed.

## Findings and dispositions

| # | Severity | Finding | Disposition |
|---|---|---|---|
| 1 | Major | Headline outer-bridge figure: Terra–P4 was fully occluded by Sonnet–P4 (both at PTI exactly 0, TI 0.2106 vs 0.2098); the four PTI = 0 markers were clipped by the y-axis and their vertical intervals were unattributable. | **Fixed.** `generate_bridge_figure.py` now offsets judges with identical PTI values horizontally by multiples of 0.026, draws PTI intervals at the true abscissa, marks the exact abscissa with a dotted line, stacks cluster labels with leader lines, and prints the disclosure inside the axes; the paper caption discloses the offset. Source data byte-unchanged. |
| 2 | Major | Legacy raster `figures/pull_fig.png` (submitted Figure 1) embedded the text "Certified judge", "reuse certified judge", "substantial cost savings", and the project name, contradicting the paper's no-certification/no-savings result and carrying an identifiable project name; the caption disclaimer did not remove the image text. | **Fixed** by removing the figure from the submission (no cross-reference existed; the PNG remains in the source tree for the authors). |
| 3 | Major | Required AI-use section used the ICLR 2026 heading ("The Use of Large Language Models"); the 2027 template names the required section "AI use statement" with a used / not-used / not-applicable structure. | **Heading fixed** to "AI Use Statement". Content structure left for the authors (which required-disclosure categories were *not* used cannot be asserted by a reviewer). |
| 4 | Major (wording) | `RESULTS_QA.md`/reports called Terra "requested/observed": Codex JSONL exposes no served-model field (`usage.model_provenance` in all 516 artifacts); the identity rests on the hash-bound `-m gpt-5.6-terra` argument and the CLI's 400-rejection of unsupported IDs. | **Fixed** in the paper, REPORT, STATUS, results.md, and the number map; the independent reviewer's own text in `RESULTS_QA.md` is left as written. |
| 5 | Minor (wording) | "Excluded failed attempts: 4" counted failure *records*; accepted artifacts also record 34 unretained in-run retries (`attempt` 2: 24, 3: 5), i.e. ≥ 820 CLI invocations for 774 accepted tasks. | **Fixed** in REPORT, STATUS, and the number map. The timestamped `expt_v5/results/results_summary_2026-08-26__03-40-50.md` is left as the dated snapshot. |
| 6 | Minor | `expt_v5/cc.md` listed its inputs as `../../…`, which resolves outside the experiment. | **Fixed** (`../…`). |
| 7 | Minor | `REPORT.md` labelled the protocol `PTI_v0_cli_v5` while every frozen artifact uses `PTI_v0_cli_protocol_v5`. | **Fixed** in REPORT (the W&B run configs pushed by `push_to_wandb.py` keep the short label; not changed). |
| 8 | Minor | STATUS claimed `git diff --check` passed and "79 tests" without stating the `uutils` dependency; the branch diff has whitespace hits only in immutable raw transcripts, an Exp27 prompt file, and Markdown hard breaks. | **Fixed** (precise wording). |
| 9 | Minor | natbib run-on "(… programming puzzles Chen et al., 2021)". | **Fixed** (`;`). |
| 10 | Minor | Legacy appendix wording: "Threshold Calibration" lacked the Legacy tag; the cross-model status caption said "Headline bridge claims". | **Fixed** (tagged "Legacy---Not PTI-v0"; "Legacy headline bridge claims used …"). |
| 11 | Minor | PR #38 (Exp27) is still open against `main` although every one of its commits is contained in #40, and the #40 body does not mention #38 or the ultimate-utils #44 dependency. | **Open for the authors** (external service; not changed). |
| 12 | Minor | The W&B report embeds the pre-fix outer-bridge image. | **Open** (external service; the committed source data are unchanged). |
| 13 | Minor | `refs.bib` `anonymous2025formaljudge` says "NeurIPS (to appear), 2025" while the text calls it a non-archival workshop study. | **Open** (venue truth unknown to the reviewer). |
| 14 | Minor | `ref/files (23)/` prompts instruct unzipping `certjudge-FINAL.zip`, which is git-ignored and untracked; `files (22).zip` is the tracked archive. | **Open** (adding a binary archive is the authors' call). |
| 15 | Note | Docs vs. code: property-bootstrap seed is `0 + judge index` (recorded per judge); `docs/spec/PTI_V0.md` line on "four valid primaries" is v4-era; the `>1/2 primaries NOT_COMPUTABLE` hard gate is undocumented; `_score_cell_id` omits `artifact_id`, so 1,280 byte-identical cells serve more than one typed artifact (inherited v4 design; the `content_deduplicated_sensitivity` block, `headline: False`, gives Sonnet–P8 PTI 0.805 vs 0.811 and leaves all seven exact zeros unchanged, so judge ranks and the bridge are unaffected). | Recorded; no metric change is permitted post-result. |
| 16 | Note | Test coverage: bootstraps, the computed-bridge path, and SESOI metric definitions are covered by reviewer reconstructions (this record, `RESULTS_QA.md`, `PAPER_QA.md`) rather than by the committed suite. | Recorded; no speculative rewrite. |
| 17 | Note | Claude runs end with `stop_reason: "tool_use"` (the structured-output mechanism) so "no tool use" rests on proxies (`--tools ""`, empty `permission_denials`, zero subagents/server tools); the backend binary is `claude --safe-mode`, not the `clauded` alias named in the frozen labels; the CLI-estimated Claude usage sums to about `$27.20` at API list prices while provider-API spend is `$0` under the subscription. | Recorded. |

## Fixes applied (working tree, uncommitted)

- `experiments/29_pti_v0_cli_bridge/generate_bridge_figure.py` (SHA-256 `34beeb04cf5098983ff611bfc7be3946a5fde73a1bd099bd4bca58a747f97417`), regenerated `results/figures/outer_bridge_primaries.{pdf,png}` (`dd91088665e36525649d005f81983a9ed3c94a3b5a8999ed925d82a8d7b4a745`, `2420d56d94dc2260275325fc7c38fdbc2a7280b00160adb51a0902be6605c2d6`) and `outer_bridge_pooled_secondary.{pdf,png}` (`50a498d89df8ddafb36be09afd98cfb7a4d8e4ab6f18d432dd445607edd4278b` for the PDF); `results/figures/outer_bridge_source_data.{csv,json}` byte-unchanged.
- `paper_latex/ICLR_2027_submission/main.tex` (`0532ad9285cb227a2e4cf576afb951dfb5ca15a65634c9c34f1ddab5b38d0cb1`) and `figures/outer_bridge_primaries.pdf` (byte-identical to the experiment asset); rebuilt `main.pdf` (`3d35607cb19656126318a2574c5a0cbac7068565edce549539cf4b0357e292ba`, 22 pages, conclusion on page 9).
- `REPORT.md`, `STATUS_PTI_V0_V4.md`, `MANUSCRIPT_NUMBER_MAP.md`, `results.md`, `expt_v5/cc.md`, `README.md` (this record).
- Frozen authorities untouched: `frozen_config.json`, manifests, raw batches, `scores.json`, properties, criterion, bridge, SESOI, and the figure source data.

## Scientific assessment

The evidence supports exactly what the manuscript claims: a complete, audited v5 execution of the frozen PTI-v0 protocol whose primaries-only bridge is below the 0.5 SESOI and inconclusive about zero, with four exact-zero primaries, a wide discrete judge-bootstrap interval, 27.1% positive-rule power, and disclosed execution limitations (v4 `NOT_RUN`, batching, auxiliary Haiku telemetry, requested-not-observed Terra identity). Any positive bridge, PASS-SCREEN threshold, deployment, causal, or human-savings claim would require a new, separately frozen experiment with a substantially larger judge panel and repaired zero-saturating probes; the SESOI simulation is also optimistic for a tie-heavy instrument because it draws continuous proxies without ties.

```text
VERDICT: FIXED
CRITICAL_ISSUES: 0
MAJOR_ISSUES: 4
FIXES_APPLIED: 10
STRUCTURAL: PASS
SUMMARY: Every frozen number, hash, binding, and manuscript value was independently reproduced and the below-SESOI/inconclusive interpretation stands; the applied fixes are presentation and provenance-wording corrections (occluded headline-figure point, legacy "certified/cost-savings" raster, AI-use heading, requested-not-observed Terra wording, retry accounting) with no change to any frozen scientific authority.
```

**TLDR-end:** [cj: pti-v0 mega-QA] The bundle and paper are numerically sound and honestly framed; the headline figure, a legacy raster, the AI-use heading, and several provenance sentences were corrected in place, and the remaining items (open PR #38, W&B image, bib venue, ignored reference zip, AI-use disclosure structure) are the authors' decisions.
