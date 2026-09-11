# EXP42 Multi-Seed Robustness (split_isotonic, zscore_mean)

10 random train/test splits (70/30). Best judge per model selected per seed.

| Model | Mean test ρ | Std | Min | Max |
| --- | ---: | ---: | ---: | ---: |
| LeanStral | 0.457 | ±0.218 | 0.026 | 0.822 |
| GPT-4o-mini | 0.439 | ±0.173 | 0.180 | 0.664 |
| GPT-5.3 Codex | 0.119 | ±0.275 | -0.281 | 0.615 |
| Claude Opus 4.7 | 0.291 | ±0.273 | -0.272 | 0.591 |
| Qwen | N/A | N/A | N/A | N/A |

**✓** = Mean test ρ ≥ 0.70.

Seeds used: [42, 1, 2, 3, 7, 13, 17, 31, 99, 123]
