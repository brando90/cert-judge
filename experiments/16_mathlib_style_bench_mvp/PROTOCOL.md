# Mathlib Style Bench MVP Protocol
**TLDR:** Select pairs where bad and good Lean files prove the same intended fact but differ in mathlib style, then score whether a judge prefers the good file. The MVP metric is a cert-judge-style two-level monotonicity check plus margin strength and repeated-call stability.

## Evaluation Unit

Each item is one JSONL row:

```json
{"pair_id":"nat_zero_add","topic":"Nat","split":"dev","bad_path":"sample_pairs/bad/nat_zero_add_verbose.lean","good_path":"sample_pairs/good/nat_zero_add_mathlib.lean","style_issue":"avoidable induction; should use existing theorem","source":"mvp_handcrafted"}
```

Required fields:

- `pair_id`: stable ID, unique across the manifest.
- `bad_path`: Lean file with worse style.
- `good_path`: matching Lean file with preferred mathlib style.

Recommended fields:

- `topic`: mathlib area or theorem family.
- `split`: `dev`, `test`, or `holdout`.
- `style_issue`: concise taxonomy label.
- `source`: PR URL, commit, Zulip/review source, or `mvp_handcrafted`.

## Initial Metric

For each pair, collect normalized scores in `[0,1]` for both variants:

- `S_bad`: judge score for the worse file.
- `S_good`: judge score for the mathlib-style file.
- `margin = S_good - S_bad`.

Pair-level metrics:

- `style_order_score = compute_p2_or_p3_ordering_auc([0, 1], [S_good, S_bad])`.
- `preference_tie_half = 1` if `margin > 0`, `0.5` if tied, else `0`.
- `pass_at_min_margin = margin >= 0.05`.
- `margin_strength = clip(max(margin, 0) / 0.25, 0, 1)`.

Aggregate metric:

```text
MSB-MVP = 0.70 * mean(style_order_score)
        + 0.20 * mean(margin_strength)
        + 0.10 * P4_stability
```

`P4_stability` reuses `cert_judge.hsj_scoring.compute_p4_stability` over repeated scores for each `(pair_id, variant)`.
The cert-judge P4 implementation returns `1.0` when there is no repeated-score variance to estimate, so reported stability runs should collect at least two scores per `(pair_id, variant)`.

## Test-Set Selection Protocol

Start with a dev set, not a hidden benchmark. The first useful target is 50-100 pairs that are easy for Lean experts to audit.

Selection rules:

- Prefer real review-driven examples from accepted mathlib PRs, review comments, Zulip style feedback, or final cleanup commits.
- Include only pairs where both files compile against a pinned Lean/mathlib revision.
- Require the same public theorem statement or the same intended local theorem; the benchmark should isolate style, not semantic correctness.
- The bad variant should be plausible submitted code, not artificial nonsense.
- The good variant should be accepted or clearly review-preferred mathlib style.
- Keep pairs small enough for a judge to inspect without hidden context, ideally one theorem or tightly related theorem block.
- Exclude examples where the good version changes the theorem meaning, adds a missing hypothesis, or fixes a mathematical bug.

Stratification targets:

- Domain: algebra, order, topology, analysis, data/list/nat, tactic-heavy proofs.
- Style issue: existing theorem reuse, `simp`/`simpa` normalization, avoidable induction, proof compression, naming/docstrings, theorem factoring, term-vs-tactic idiom.
- Difficulty: short single-line rewrite, medium proof cleanup, longer refactor.
- Source: no more than one item per PR in the held-out split unless grouped leakage is explicitly tracked.

Split protocol:

- `dev`: open examples for prompt design and runner debugging.
- `test`: frozen after the first expert audit.
- `holdout`: hidden or access-limited pairs for final judge comparisons.

Leakage controls:

- Split by source PR/file cluster, not by individual pair.
- Record mathlib commit and PR URL before scoring.
- Keep bad/good filenames neutral in judge-facing prompts if the scoring interface exposes filenames.
- Do not include review comments or labels in the judge prompt.

## Reporting Protocol

Every run should report:

- judge ID and scoring source;
- number of pairs, skipped pairs, and split;
- `MSB-MVP`, `style_order_score`, `mean_margin_good_minus_bad`, and `P4_stability`;
- per-pair margins sorted from worst to best;
- prompt/template used to produce external scores.

The smoke heuristic is only a harness check. Reportable experiments should use human labels or a documented external judge process.
Reject score files with unknown `pair_id` or non-`bad`/`good` variants so aggregate metrics cannot be polluted by rows outside the selected test set.
