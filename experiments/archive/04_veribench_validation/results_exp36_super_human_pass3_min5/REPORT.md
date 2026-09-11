# EXP36 Report: Super-Human Pass3 (Five-Rater Mean)

**TLDR:** We averaged participant1..participant5 into one label set (`super_human_pass3`) and re-ran the same pair/task judge-human analysis used for `ethan_avg`. The super-human target does **not** recover the old ~0.7 task-level correlations; best LLM task Spearman stays near **0.54**.

## Super-Human Target Construction
- Participant files averaged: 5
- Items in super-human TSV: `44`
- Items with all 5 raters: `44`
- Items with 4 raters: `0`
- Output TSV: `experiments/04_veribench_validation/data/super_human_pass3_avg_five_raters.tsv`

## Is Super-Human Similar To Ethan?
- Overlap with `ethan_avg`: `32` items
- Item-level Spearman(super_human, ethan_avg): `-0.028`
- Mean absolute score difference (0-5 scale): `1.244`

If Brando's assumption held strongly, super-human should behave like ethan_avg in judge-human correlation. It does not.

## Main Comparison (Same Analysis As Before)

| Target | Meta task Spearman(cert_v2, human align) | Best LLM task Spearman | Best judge | n tasks |
| --- | ---: | ---: | --- | ---: |
| `ethan_avg` | 0.203 | 0.640 | `claude-opus-4-7|P4_CHECKLIST` | 24 |
| `super_human_pass3` | 0.010 | 0.206 | `gpt-4o-mini|P4_CHECKLIST` | 11 |

## Top LLM Judges On Super-Human (Task Level)

| Judge | cert_v2 | Task Spearman | Pair Spearman | n tasks |
| --- | ---: | ---: | ---: | ---: |
| gpt-4o-mini|P4_CHECKLIST | 0.747 | 0.206 | 0.164 | 11 |
| claude-opus-4-7|P4_CHECKLIST | 0.883 | 0.049 | -0.037 | 11 |
| claude-opus-4-7|P8_STRICT_B | 0.930 | 0.002 | -0.031 | 11 |
| gpt-5.3-codex|P8_STRICT_B | 0.852 | -0.107 | -0.134 | 11 |
| gpt-5.3-codex|P11_JSON_FIRST | 0.880 | -0.204 | -0.015 | 11 |
| gpt-5.3-codex|P1_BASELINE | 0.865 | -0.244 | -0.234 | 11 |
| gpt-5.3-codex|P20_TC_RATER_CARD | 0.913 | -0.256 | -0.031 | 11 |
| claude-opus-4-7|P1_BASELINE | 0.884 | -0.280 | -0.138 | 11 |
| labs-leanstral-2603|P8_STRICT_B | 0.524 | -0.309 | -0.132 | 11 |
| gpt-5.3-codex|P2_FORMAL | 0.879 | -0.317 | -0.323 | 11 |

## Interpretation
- Super-human pass3 is the five-participant mean treated as one human (`n≈78` items, `n≈20-24` tasks on the cached judge panel).
- Task aggregation still helps relative to pair-level, but much less than on `ethan_avg`.
- Good judges validated on Ethan (e.g. Opus/Codex prompts) can be **negative** against the five-rater mean.
- The old ~0.7 numbers come from `ethan_avg` + task aggregation, not from averaging all annotators.
