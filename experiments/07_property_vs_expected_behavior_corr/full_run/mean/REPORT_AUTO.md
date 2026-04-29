# Folder 07 Auto Report (mean)

- Input: `/Users/brandomiranda/cert-judge/experiments/07_property_vs_expected_behavior_corr/../06_cert_index_vs_human_judge_corr_and_low_var/full_run/mean/detail_rows.csv`
- Judges: 9
- Thresholds (locked): P1>=0.9 (STYLE/RENAME/REORDER), P2<=-0.7 (median per-problem rho), P4>=0.9 (median per-item alpha)

## Pass/fail summary

| Judge | P1 (S/R/Re) | P2 rho_med | P4 alpha_med | Pass |
|---|---|---|---|---|
| `claude-sonnet-4-20250514|BAD_STRINGY` | 0.950/0.927/0.947 | -0.894 | 1.000 | PASS |
| `claude-sonnet-4-20250514|P1_BASELINE` | 1.000/0.999/1.000 | -0.894 | 1.000 | PASS |
| `claude-sonnet-4-20250514|P4_CHECKLIST` | 0.992/0.993/1.000 | -0.894 | 1.000 | PASS |
| `claude-sonnet-4-20250514|P8_STRICT_B` | 0.996/0.990/0.994 | -0.894 | 1.000 | PASS |
| `editdist_e1` | 0.974/0.920/0.893 | -0.600 | 1.000 | FAIL |
| `gpt-5.3-codex|P1_BASELINE` | 1.000/1.000/1.000 | -0.866 | 1.000 | PASS |
| `gpt-5.3-codex|P4_CHECKLIST` | 0.999/1.000/1.000 | -0.866 | 1.000 | PASS |
| `gpt-5.3-codex|P8_STRICT_B` | 0.999/1.000/0.996 | -0.894 | 1.000 | PASS |
| `random_r1` | 0.414/0.451/0.479 | 0.100 | 1.000 | FAIL |

## P1 ALPHA (isolated per halting-problem argument)

- `claude-sonnet-4-20250514|BAD_STRINGY`: ALPHA mean=0.881 (n=24)
- `claude-sonnet-4-20250514|P1_BASELINE`: ALPHA mean=0.003 (n=24)
- `claude-sonnet-4-20250514|P4_CHECKLIST`: ALPHA mean=0.039 (n=24)
- `claude-sonnet-4-20250514|P8_STRICT_B`: ALPHA mean=0.700 (n=24)
- `editdist_e1`: ALPHA mean=0.953 (n=24)
- `gpt-5.3-codex|P1_BASELINE`: ALPHA mean=0.000 (n=24)
- `gpt-5.3-codex|P4_CHECKLIST`: ALPHA mean=0.000 (n=24)
- `gpt-5.3-codex|P8_STRICT_B`: ALPHA mean=0.171 (n=24)
- `random_r1`: ALPHA mean=0.476 (n=24)

## P2 details

- `claude-sonnet-4-20250514|BAD_STRINGY`: pooled rho=-0.803 CI=[-0.889,-0.683] perm_p=0.0000; weak-mono=91.7%; n_problems=24
- `claude-sonnet-4-20250514|P1_BASELINE`: pooled rho=-0.849 CI=[-0.896,-0.785] perm_p=0.0000; weak-mono=100.0%; n_problems=24
- `claude-sonnet-4-20250514|P4_CHECKLIST`: pooled rho=-0.849 CI=[-0.896,-0.784] perm_p=0.0000; weak-mono=100.0%; n_problems=24
- `claude-sonnet-4-20250514|P8_STRICT_B`: pooled rho=-0.848 CI=[-0.904,-0.760] perm_p=0.0000; weak-mono=96.9%; n_problems=24
- `editdist_e1`: pooled rho=-0.594 CI=[-0.745,-0.401] perm_p=0.0000; weak-mono=50.0%; n_problems=24
- `gpt-5.3-codex|P1_BASELINE`: pooled rho=-0.807 CI=[-0.865,-0.736] perm_p=0.0000; weak-mono=100.0%; n_problems=24
- `gpt-5.3-codex|P4_CHECKLIST`: pooled rho=-0.791 CI=[-0.853,-0.712] perm_p=0.0000; weak-mono=100.0%; n_problems=24
- `gpt-5.3-codex|P8_STRICT_B`: pooled rho=-0.767 CI=[-0.854,-0.649] perm_p=0.0000; weak-mono=95.8%; n_problems=24
- `random_r1`: pooled rho=0.003 CI=[-0.172,0.174] perm_p=0.9779; weak-mono=53.1%; n_problems=24
