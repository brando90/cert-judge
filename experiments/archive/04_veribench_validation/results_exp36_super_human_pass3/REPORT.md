# EXP36 Report: Super-Human Pass3 (Five-Rater Mean)

**TLDR:** We averaged participant1..participant5 into one label set (`super_human_pass3`) and re-ran the same pair/task judge-human analysis used for `ethan_avg`. The super-human target does **not** recover the old ~0.7 task-level correlations; best LLM task Spearman stays near **0.54**.

## Super-Human Target Construction
- Participant files averaged: 5
- Items in super-human TSV: `78`
- Items with all 5 raters: `44`
- Items with 4 raters: `27`
- Output TSV: `experiments/04_veribench_validation/data/super_human_pass3_avg_five_raters.tsv`

## Is Super-Human Similar To Ethan?
- Overlap with `ethan_avg`: `63` items
- Item-level Spearman(super_human, ethan_avg): `0.131`
- Mean absolute score difference (0-5 scale): `1.230`

If Brando's assumption held strongly, super-human should behave like ethan_avg in judge-human correlation. It does not.

## Main Comparison (Same Analysis As Before)

| Target | Meta task Spearman(cert_v2, human align) | Best LLM task Spearman | Best judge | n tasks |
| --- | ---: | ---: | --- | ---: |
| `ethan_avg` | 0.203 | 0.640 | `claude-opus-4-7|P4_CHECKLIST` | 24 |
| `super_human_pass3` | 0.034 | 0.541 | `labs-leanstral-2603|P1_BASELINE` | 20 |

## Top LLM Judges On Super-Human (Task Level)

| Judge | cert_v2 | Task Spearman | Pair Spearman | n tasks |
| --- | ---: | ---: | ---: | ---: |
| labs-leanstral-2603|P1_BASELINE | 0.724 | 0.541 | 0.422 | 20 |
| gpt-4o-mini|P1_BASELINE | 0.745 | 0.353 | 0.263 | 20 |
| claude-opus-4-7|P1_BASELINE | 0.884 | 0.327 | 0.189 | 20 |
| gpt-5.3-codex|P20_TC_RATER_CARD | 0.913 | -0.012 | -0.045 | 20 |
| gpt-4o-mini|P4_CHECKLIST | 0.747 | -0.040 | -0.010 | 20 |
| labs-leanstral-2603|P8_STRICT_B | 0.524 | -0.042 | -0.008 | 20 |
| gpt-5.3-codex|P7_STRICT_A | 0.869 | -0.127 | -0.114 | 20 |
| gpt-5.3-codex|P14_HUMAN_ALIGN_V2 | 0.876 | -0.139 | -0.080 | 20 |
| gpt-5.3-codex|P13_HUMAN_ALIGN_STRICT | 0.874 | -0.252 | -0.173 | 20 |
| claude-opus-4-7|P4_CHECKLIST | 0.883 | -0.296 | -0.252 | 20 |

## Interpretation
- Super-human pass3 is the five-participant mean treated as one human (`n≈78` items, `n≈20-24` tasks on the cached judge panel).
- Task aggregation still helps relative to pair-level, but much less than on `ethan_avg`.
- Good judges validated on Ethan (e.g. Opus/Codex prompts) can be **negative** against the five-rater mean.
- The old ~0.7 numbers come from `ethan_avg` + task aggregation, not from averaging all annotators.
