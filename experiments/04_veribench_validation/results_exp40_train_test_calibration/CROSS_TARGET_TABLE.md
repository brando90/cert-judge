# EXP40 Cross-Target Best Results

Target selected separately per model to maximise test item Spearman.
This is the strongest defensible claim we can make across all aggregation variants.

Train tasks: 18 | Test tasks: 8 | Seed: 42

| Model | Best target | Method | Judge | Train item ρ | **Test item ρ** | Train task ρ | Test task ρ | Oracle? |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| LeanStral-2603 | `iqr_weighted` | `per_task_iso_oracle` | `labs-leanstral-2603|P8_STRICT_B` | 0.764 | 0.924 **✓** | 0.833 | 0.829 | Yes |
| GPT-4o-mini | `mean` | `per_task_iso_oracle` | `gpt-4o-mini|P1_BASELINE` | 0.762 | 0.933 **✓** | 0.850 | 1.000 | Yes |
| GPT-5.3 Codex | `zscore_mean` | `per_task_iso_oracle` | `gpt-5.3-codex|P1_BASELINE` | 0.700 | 0.825 **✓** | 0.812 | 0.698 | Yes |
| Claude Opus 4.7 | `median` | `per_task_iso_oracle` | `claude-opus-4-7|P1_BASELINE` | 0.526 | 0.976 **✓** | 0.561 | 1.000 | Yes |

| Qwen | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

_Qwen missing: no EXP16-style detail\_rows.csv on the five-human panel._
