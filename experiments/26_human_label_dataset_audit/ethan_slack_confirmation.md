# Annotator confirmation — Ethan's Slack answers vs the audited facts (2026-08-14)

> Part of [`experiments/26_human_label_dataset_audit/`](README.md). The audit's central claims
> about the calibration panel were established from file forensics (content hashes, mtimes, git
> history) *before* the annotator weighed in. On 2026-08-14 Ethan answered Brando's questions on
> Slack. This document records his answers verbatim and checks each against the audit.

**Verdict: Ethan's answers confirm the audit's three load-bearing claims and contradict none of
them.** One answer conflates two distinct "3"s (the same trap the paper's earlier draft fell
into); the audit disentangles them below. Two open items remain unresolved.

## The exchange

> **Brando — 10:27 AM** Guys I do need a response please.
>
> **Ethan Hersch — 10:32 AM** Not at computer now busy week at work.
> 1. "Could be duplicated so could just say 72 if that's what the count is"
> 2. "Not sure i understand this one but pass 1/2 was myself using 2 different rubrics"
> 3. "Pass 1/2 are just my ratings and distinct from other ratings gathered"
> 4. "Those were the questions sent out to all the raters it's like a few per set"

## Answer-by-answer check

### 1. "Could be duplicated so could just say 72 if that's what the count is" — ✅ confirms the count, ⚠️ mixes up the mechanism

- **Confirms:** 72 is the analyzed count; the annotator endorses reporting it. Duplication does
  exist in his label files: the lenient-view file (`ethan_human_scores_ORIGINAL.tsv`) has 78
  rows for 75 pairs — problem `4_json_decoder` appears twice (all 3 candidates, scored 1 and
  2), which is the source of the 1.5-averaged scores in the appendix histogram and of the
  MAE/MSE convention mismatch (0.778 vs 0.771).
- **Correction the audit adds:** the duplication is **not** why 75 → 72. The 3 dropped pairs
  are the `0_unsafeMultiply_safe` rows, skipped on a stale pre-renumbering filename
  (`missing_gold`). Two different 3s: 3 *duplicate rows* in one label file (collapse to the
  same pairs, never inflated anything) vs 3 *dropped pairs* (stale key). Ethan's hedge
  ("could be duplicated") is understandable from memory but the audited mechanism is the stale
  filename. The ICLR 2027 paper states both facts separately (main.tex §data, appendix
  "75-vs-72" paragraph) — correctly.

### 2. "pass 1/2 was myself using 2 different rubrics" — ✅ direct confirmation of the audit's central claim

The audit concluded from content hashes that `pass1`/`pass2` are **one annotator, two
rubric-strictness rounds** — not two raters, and not two data splits. This was the single most
consequential reinterpretation in the audit (it reclassifies the panel's 0.249 inter-"pass"
Spearman from *inter-rater agreement* to *rubric stability*, i.e., a property of the criterion
itself). Ethan states it first-person. **Now confirmed on both evidence tracks.**

Note: the audit further established the pass *names* are inverted relative to chronology
(paper `pass1` ≡ his second, stricter round; sha-verified). Ethan's answer doesn't speak to
ordering — see open items.

### 3. "Pass 1/2 are just my ratings and distinct from other ratings gathered" — ✅ confirms the two-population separation

Exactly the audit's Campaign B vs Campaign A split: the calibration panel (his 150 old-rubric
labels) and the 5-rater pool (343 revised-rubric labels from participants 1–5) are **separate
populations that must not be mixed** (they correlate at ρ ≈ 0.13). Ethan confirms the panel
labels are his alone and disjoint as a campaign from the group collection. This underwrites the
paper's criterion-drift disclosure.

### 4. "Those were the questions sent out to all the raters it's like a few per set" — ✅ consistent (lower confidence)

Matches the pool design: one shared rating task/rubric document
(`veribench_prompts/human_judgements_prompt.md`) sent to all raters, over 5 problems per
VeriBench split ("a few per set"). We lack the exact question he was replying to, so this is
recorded as *consistent with* rather than *confirming* a specific audited fact.

## What remains open (Ethan did not address)

| open item | why it matters | who can answer |
| --- | --- | --- |
| **participant5 identity** (added after the anonymization commit; candidates Kirill / Simon / Andrew) | unblocks the by-rater train/val/test split (exp62); p5 is the pool's outlier rater | Ethan — one line |
| **which rubric text was used in which round** (audit infers strict=second round from hashes+mtimes; not contradicted, not confirmed) | only affects the historical narrative; the ICLR paper already avoids temporal names | Ethan, if records exist |

## Net effect on the paper

No number changes. The three facts the ICLR 2027 submission states about the panel (75 rated /
72 analyzed; one annotator, two rubric-strictness views; pool is a separate 343-label
population) now carry **both** forensic and first-person confirmation. The remaining editorial
guidance in [`cert_judge_judgements_human_scores.md`](cert_judge_judgements_human_scores.md) §5
is unchanged.
