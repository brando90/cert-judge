# Experiment 69C — Formulation ③ vs ④ & Proper-Score vs Pearson Selection (2026-11-27)

Evaluated on the pre-registered sealed task split (`10` train / `5` val / `10` test tasks; `const` test RPS = `0.05201`).

| Judge | `rps_3` (test RPS) | `rps_4` (test RPS) | `rps3 − rps4` [95% CI] | `rps3 − pearson3` [95% CI] | `rps4 − pearson4` [95% CI] |
|---|---:|---:|---:|---:|---:|
| `api_gpt_4_1` | `const` (0.0520) | `ce_map` (**0.0495**) | +0.00255 **[+0.00030, +0.00560]** | −0.0873 **[−0.1852, −0.0202]** (wins) | −0.0122 **[−0.0195, −0.0033]** (wins) |
| `api_gpt_4_1_mini` | `const` (0.0520) | `ce_map` (0.0498) | +0.00226 [−0.00149, +0.00553] | −0.1197 **[−0.1729, −0.0601]** (wins) | 0.0000 (tie) |
| `api_gpt_5_4` | `const` (0.0520) | `ce_map` (0.0518) | +0.00025 [−0.00609, +0.00644] | −0.3637 **[−0.4638, −0.2496]** (wins) | −0.0129 **[−0.0196, −0.0044]** (wins) |
| `api_gpt_5_4_mini` | `const` (0.0520) | `ce_map` (0.0495) | +0.00253 [−0.00053, +0.00576] | −0.3161 **[−0.4213, −0.2144]** (wins) | 0.0000 (tie) |
| `snap_qwen3_8b` | `const` (0.0520) | `ce_map` (0.0498) | +0.00225 [−0.00367, +0.00798] | −0.2605 **[−0.3273, −0.1859]** (wins) | 0.0000 (tie) |

**Key takeaways:**
1. **Proper-score selection beats Pearson selection on 5/5 models in Formulation ③** (`rps3 − pearson3` 95% CIs exclude 0 on every single judge, saving 0.087–0.364 RPS).
2. **CE-map beats Pearson-map on both flagship models in Formulation ④** (`api_gpt_4_1`: −0.0122 [−0.0195, −0.0033]; `api_gpt_5_4`: −0.0129 [−0.0196, −0.0044]).
3. **`api_gpt_4_1` + CE-map (Formulation ④) statistically significantly beats the constant forecast on the sealed 10-task test split** (`0.0495` vs. `0.0520`, diff `−0.00255 [−0.00560, −0.00030]`), and Formulation ④ beats or ties Formulation ③ on all 5 judges.

See `results/eval_69c_all_measured.json`.
