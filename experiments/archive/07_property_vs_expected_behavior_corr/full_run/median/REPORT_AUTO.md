# Folder 07 Auto Report (median)

- Input: `/Users/brandomiranda/cert-judge/experiments/07_property_vs_expected_behavior_corr/../06_cert_index_vs_human_judge_corr_and_low_var/full_run/median/detail_rows.csv`
- Judges: 9
- Thresholds (locked): P1>=0.9 (STYLE/RENAME/REORDER), P2<=-0.7 (median per-problem rho), P4>=0.9 (median per-item alpha)

## Pass/fail summary

| Judge | P1 (S/R/Re) | P2 rho_med | P4 alpha_med | Pass |
|---|---|---|---|---|
| `claude-sonnet-4-20250514|BAD_STRINGY` | 0.950/0.926/0.948 | -0.894 | 1.000 | PASS |
| `claude-sonnet-4-20250514|P1_BASELINE` | 1.000/1.000/1.000 | -0.894 | 1.000 | PASS |
| `claude-sonnet-4-20250514|P4_CHECKLIST` | 0.996/1.000/1.000 | -0.894 | 1.000 | PASS |
| `claude-sonnet-4-20250514|P8_STRICT_B` | 0.996/0.988/0.996 | -0.894 | 1.000 | PASS |
| `editdist_e1` | 0.974/0.920/0.893 | -0.600 | 1.000 | FAIL |
| `gpt-5.3-codex|P1_BASELINE` | 1.000/1.000/1.000 | -0.866 | 1.000 | PASS |
| `gpt-5.3-codex|P4_CHECKLIST` | 0.999/1.000/1.000 | -0.866 | 1.000 | PASS |
| `gpt-5.3-codex|P8_STRICT_B` | 0.999/1.000/0.998 | -0.894 | 1.000 | PASS |
| `random_r1` | 0.414/0.451/0.479 | 0.100 | 1.000 | FAIL |

## P1 ALPHA (isolated per halting-problem argument)

- `claude-sonnet-4-20250514|BAD_STRINGY`: ALPHA mean=0.881 (n=24)
- `claude-sonnet-4-20250514|P1_BASELINE`: ALPHA mean=0.004 (n=24)
- `claude-sonnet-4-20250514|P4_CHECKLIST`: ALPHA mean=0.046 (n=24)
- `claude-sonnet-4-20250514|P8_STRICT_B`: ALPHA mean=0.708 (n=24)
- `editdist_e1`: ALPHA mean=0.953 (n=24)
- `gpt-5.3-codex|P1_BASELINE`: ALPHA mean=0.000 (n=24)
- `gpt-5.3-codex|P4_CHECKLIST`: ALPHA mean=0.000 (n=24)
- `gpt-5.3-codex|P8_STRICT_B`: ALPHA mean=0.179 (n=24)
- `random_r1`: ALPHA mean=0.476 (n=24)

## P2 details

- `claude-sonnet-4-20250514|BAD_STRINGY`: pooled rho=-0.834 CI=[-0.905,-0.730] perm_p=0.0000; weak-mono=94.8%; n_problems=24
- `claude-sonnet-4-20250514|P1_BASELINE`: pooled rho=-0.850 CI=[-0.898,-0.785] perm_p=0.0000; weak-mono=100.0%; n_problems=24
- `claude-sonnet-4-20250514|P4_CHECKLIST`: pooled rho=-0.840 CI=[-0.891,-0.773] perm_p=0.0000; weak-mono=100.0%; n_problems=24
- `claude-sonnet-4-20250514|P8_STRICT_B`: pooled rho=-0.826 CI=[-0.891,-0.730] perm_p=0.0000; weak-mono=96.9%; n_problems=24
- `editdist_e1`: pooled rho=-0.594 CI=[-0.745,-0.401] perm_p=0.0000; weak-mono=50.0%; n_problems=24
- `gpt-5.3-codex|P1_BASELINE`: pooled rho=-0.799 CI=[-0.858,-0.726] perm_p=0.0000; weak-mono=100.0%; n_problems=24
- `gpt-5.3-codex|P4_CHECKLIST`: pooled rho=-0.791 CI=[-0.853,-0.712] perm_p=0.0000; weak-mono=100.0%; n_problems=24
- `gpt-5.3-codex|P8_STRICT_B`: pooled rho=-0.762 CI=[-0.849,-0.643] perm_p=0.0000; weak-mono=95.8%; n_problems=24
- `random_r1`: pooled rho=0.003 CI=[-0.172,0.174] perm_p=0.9779; weak-mono=53.1%; n_problems=24
