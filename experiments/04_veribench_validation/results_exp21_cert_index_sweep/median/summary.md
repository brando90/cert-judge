# EXP21 Cert-Index Sweep

- source: `experiments/04_veribench_validation/results_exp16_final_robust_r9_median/summary.json`
- label set: `avg`
- baseline v1: rho=0.762, CI=[0.103, 1.000], width=0.897

## Best objective (rho - 0.25*CI_width)
- id=1579 arith comps=ident|mono|stab w=0.200|0.500|0.300 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=2839 arith comps=anti|ident|mono|stab w=0.000|0.200|0.500|0.300 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=9299 arith comps=ident|mono|stab|weak w=0.200|0.400|0.400|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=9307 arith comps=ident|mono|stab|weak w=0.200|0.500|0.300|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=11555 arith comps=anti|ident|mono|stab|subtle w=0.000|0.200|0.400|0.400|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=11563 arith comps=anti|ident|mono|stab|subtle w=0.000|0.200|0.500|0.300|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=13555 arith comps=anti|ident|mono|stab|weak w=0.000|0.200|0.500|0.300|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=22503 arith comps=ident|mono|stab|subtle|weak w=0.200|0.400|0.400|0.000|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=22523 arith comps=ident|mono|stab|subtle|weak w=0.200|0.500|0.300|0.000|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=24495 arith comps=anti|ident|mono|stab|subtle|weak w=0.000|0.200|0.400|0.400|0.000|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608

## Candidates with rho >= min_rho (sorted by CI width)
- id=1579 arith comps=ident|mono|stab w=0.200|0.500|0.300 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=2839 arith comps=anti|ident|mono|stab w=0.000|0.200|0.500|0.300 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=9299 arith comps=ident|mono|stab|weak w=0.200|0.400|0.400|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=9307 arith comps=ident|mono|stab|weak w=0.200|0.500|0.300|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=11555 arith comps=anti|ident|mono|stab|subtle w=0.000|0.200|0.400|0.400|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=11563 arith comps=anti|ident|mono|stab|subtle w=0.000|0.200|0.500|0.300|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=13555 arith comps=anti|ident|mono|stab|weak w=0.000|0.200|0.500|0.300|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=22503 arith comps=ident|mono|stab|subtle|weak w=0.200|0.400|0.400|0.000|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=22523 arith comps=ident|mono|stab|subtle|weak w=0.200|0.500|0.300|0.000|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608
- id=24495 arith comps=anti|ident|mono|stab|subtle|weak w=0.000|0.200|0.400|0.400|0.000|0.000 | rho=0.881 CI=[0.392,1.000] width=0.608