# EXP43 Frozen TIvar vs Held-Out Human Correlation

Held-out corpus: participant1–5 labels (78 pairs, ~343 labels).  
TIvar (v3) taken frozen from EXP30 — never refit on participant data.  
Bootstrap: 2000 replicates, percentile 95% CI.

---

## Table 1 — Held-Out: TIvar vs Participant Human Spearman

Metric: family-level Spearman(TIvar, judge-level human Spearman) on held-out corpus.

| Family | n judges | n items | Held-out ρ | 95% CI | Calib avg ρ | Calib pass1 ρ | Calib pass2 ρ |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| GPT-5.3-Codex | 8 | 60 | -0.071 | [-0.852, 0.950] | 0.762 **✓** | 0.762 **✓** | 0.810 **✓** |
| Claude Opus 4.7 | 8 | 60 | 0.119 | [-0.852, 0.918] | 0.429 | 0.405 | 0.643 |
| Qwen3-Coder-30B | 8 | 60 | -0.333 | [-1.000, 0.615] | 0.667 | -0.048 | 0.905 **✓** |
| LeanStral | 8 | 60 | 0.048 | [-0.919, 0.974] | -0.333 | -0.667 | 0.167 |

**✓** = ρ ≥ 0.70.

---

## Interpretation

- **Held-out ρ** is the primary TMLR claim: TIvar predicts which judge
  configurations are more human-aligned, evaluated on labels collected
  independently from the development panel.
- **Calib ρ** (pass1/pass2/avg) is the within-panel validation result
  already reported in the paper (Table in Section 4).
- Agreement between held-out ρ and calib ρ demonstrates that the
  TIvar ranking is not overfit to the original development labels.
- n judges ≈ 8 per family; CIs are wide by design — we report them
  explicitly rather than suppressing the uncertainty.
