# Property suite — gpt-5.6-terra|P1_BASELINE (effort low, 3 repeats, median)

Panel reproduction check (8 Codex configs recomputed from exp16 r9_median detail rows vs exp30 CSV): max |Δ ti_var_v3| = 9.24e-10

| judge | ident | mono | weak | stab | varcorr_1m | varscore_1m | TI_var recomputed | published | bug ρ | const ladders |
|---|---|---|---|---|---|---|---|---|---|---|
| editdist_e1 | 0.935 | 0.797 | 0.000 | 1.000 | 1.000 | 1.000 | 0.0595 | 0.0595 | -0.594 | 0 |
| gpt-4o-mini|P4_CHECKLIST | 0.812 | 0.761 | 0.333 | 0.840 | 0.442 | 0.000 | 0.1141 | 0.1141 | -0.522 | 0 |
| gpt-4o-mini|P8_STRICT_B | 0.895 | 0.878 | 0.250 | 0.878 | 0.931 | 0.041 | 0.4709 | 0.4709 | -0.755 | 0 |
| gpt-5.3-codex|BAD_STRINGY | 0.954 | 0.851 | 0.208 | 0.983 | 0.972 | 0.998 | 0.6964 | 0.6964 | -0.702 | 0 |
| gpt-5.3-codex|P1_BASELINE | 0.750 | 0.900 | 1.000 | 1.000 | 0.974 | 0.996 | 0.9208 | 0.9208 | -0.799 | 0 |
| gpt-5.3-codex|P4_CHECKLIST | 0.750 | 0.896 | 1.000 | 0.997 | 0.974 | 1.000 | 0.9199 | 0.9199 | -0.791 | 0 |
| gpt-5.3-codex|P8_STRICT_B | 0.794 | 0.881 | 0.833 | 0.997 | 0.961 | 0.993 | 0.8919 | 0.8919 | -0.762 | 0 |
| random_r1 | 0.455 | 0.499 | 0.000 | 1.000 | 0.000 | 1.000 | 0.0083 | 0.0083 | 0.003 | 0 |
